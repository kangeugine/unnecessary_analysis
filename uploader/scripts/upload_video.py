#!/usr/bin/env python3
"""
YouTube Shorts & Instagram Reels Uploader
Production-ready Python script for programmatic video uploads to both platforms.
"""

import asyncio
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union
import click
from loguru import logger
from dotenv import load_dotenv

from .youtube_uploader import YouTubeUploader
from .instagram_uploader import InstagramUploader
from .video_validator import VideoValidator
from .config_manager import ConfigManager


@dataclass
class UploadResult:
    """Result of a video upload attempt."""
    platform: str
    success: bool
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    upload_duration: float = 0.0


class VideoUploader:
    """Main video uploader orchestrating uploads to multiple platforms."""

    def __init__(self, config_path: Optional[str] = None):
        self.config = ConfigManager(config_path)
        self.validator = VideoValidator()
        self.youtube_uploader = YouTubeUploader(self.config)
        self.instagram_uploader = InstagramUploader(self.config)

        # Configure logging
        logger.remove()
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        logger.add(
            "uploads.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB"
        )

    async def upload_video(
        self,
        video_source: Union[bytes, str, Path],
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        privacy: str = "public",
        instagram_caption: Optional[str] = None,
        schedule_time: Optional[datetime] = None,
        platforms: List[str] = None,
        **kwargs
    ) -> List[UploadResult]:
        """
        Upload video to specified platforms.

        Args:
            video_source: Video data as bytes, file path, or Path object
            title: Video title
            description: Video description
            tags: List of tags/keywords
            privacy: Privacy setting (public, unlisted, private)
            instagram_caption: Instagram-specific caption
            schedule_time: Scheduled publish time
            platforms: List of platforms to upload to
            **kwargs: Additional platform-specific parameters

        Returns:
            List of UploadResult objects for each platform
        """
        if platforms is None:
            platforms = ["youtube", "instagram"]

        logger.info(f"Starting upload to platforms: {platforms}")

        # Handle video source
        temp_file_path = None
        try:
            if isinstance(video_source, bytes):
                # Create temporary file for bytes data
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                temp_file.write(video_source)
                temp_file.close()
                temp_file_path = temp_file.name
                video_path = temp_file_path
            else:
                video_path = str(video_source)

            # Validate video
            validation_result = await self.validator.validate_video(video_path)
            if not validation_result.is_valid:
                error_msg = f"Video validation failed: {validation_result.error_message}"
                logger.error(error_msg)
                return [UploadResult(
                    platform=platform,
                    success=False,
                    error_message=error_msg
                ) for platform in platforms]

            # Prepare upload tasks
            upload_tasks = []

            if "youtube" in platforms:
                upload_tasks.append(
                    self._upload_to_youtube(
                        video_path, title, description, tags, privacy, schedule_time, **kwargs
                    )
                )

            if "instagram" in platforms:
                caption = instagram_caption or f"{title}\n\n{description}"
                upload_tasks.append(
                    self._upload_to_instagram(
                        video_path, caption, schedule_time, **kwargs
                    )
                )

            # Execute uploads concurrently
            results = await asyncio.gather(*upload_tasks, return_exceptions=True)

            # Process results
            upload_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    platform = platforms[i]
                    upload_results.append(UploadResult(
                        platform=platform,
                        success=False,
                        error_message=str(result)
                    ))
                else:
                    upload_results.append(result)

            # Log summary
            successful = [r for r in upload_results if r.success]
            failed = [r for r in upload_results if not r.success]

            logger.info(f"Upload completed. Successful: {len(successful)}, Failed: {len(failed)}")

            if successful:
                for result in successful:
                    logger.info(f"✓ {result.platform}: {result.video_url} (ID: {result.video_id})")

            if failed:
                for result in failed:
                    logger.error(f"✗ {result.platform}: {result.error_message}")

            return upload_results

        finally:
            # Cleanup temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")

    async def _upload_to_youtube(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]],
        privacy: str,
        schedule_time: Optional[datetime],
        **kwargs
    ) -> UploadResult:
        """Upload video to YouTube."""
        start_time = datetime.now()
        try:
            logger.info("Starting YouTube upload...")
            result = await self.youtube_uploader.upload(
                video_path=video_path,
                title=title,
                description=description,
                tags=tags,
                privacy=privacy,
                schedule_time=schedule_time,
                **kwargs
            )
            duration = (datetime.now() - start_time).total_seconds()

            return UploadResult(
                platform="youtube",
                success=True,
                video_id=result.get("id"),
                video_url=f"https://youtube.com/watch?v={result.get('id')}",
                upload_duration=duration
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"YouTube upload failed: {e}")
            return UploadResult(
                platform="youtube",
                success=False,
                error_message=str(e),
                upload_duration=duration
            )

    async def _upload_to_instagram(
        self,
        video_path: str,
        caption: str,
        schedule_time: Optional[datetime],
        **kwargs
    ) -> UploadResult:
        """Upload video to Instagram."""
        start_time = datetime.now()
        try:
            logger.info("Starting Instagram upload...")
            result = await self.instagram_uploader.upload(
                video_path=video_path,
                caption=caption,
                schedule_time=schedule_time,
                **kwargs
            )
            duration = (datetime.now() - start_time).total_seconds()

            return UploadResult(
                platform="instagram",
                success=True,
                video_id=result.get("pk"),
                video_url=result.get("video_url"),
                upload_duration=duration
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Instagram upload failed: {e}")
            return UploadResult(
                platform="instagram",
                success=False,
                error_message=str(e),
                upload_duration=duration
            )


@click.command()
@click.option('--video-source', required=True, help='Path to video file or temp location')
@click.option('--title', required=True, help='Video title')
@click.option('--description', required=True, help='Video description')
@click.option('--tags', help='Comma-separated tags')
@click.option('--privacy', default='public', type=click.Choice(['public', 'unlisted', 'private']), help='Privacy setting')
@click.option('--instagram-caption', help='Instagram-specific caption')
@click.option('--schedule-time', help='Schedule time (ISO format: 2024-12-01T10:00:00Z)')
@click.option('--platforms', default='youtube,instagram', help='Comma-separated platforms')
@click.option('--config', help='Path to configuration file')
def main(video_source, title, description, tags, privacy, instagram_caption, schedule_time, platforms, config):
    """Upload video to YouTube Shorts and Instagram Reels."""

    # Load environment variables
    load_dotenv()

    # Parse arguments
    tag_list = [tag.strip() for tag in tags.split(',')] if tags else None
    platform_list = [p.strip() for p in platforms.split(',')]
    schedule_dt = datetime.fromisoformat(schedule_time.replace('Z', '+00:00')) if schedule_time else None

    # Initialize uploader
    uploader = VideoUploader(config)

    # Run upload
    try:
        results = asyncio.run(uploader.upload_video(
            video_source=video_source,
            title=title,
            description=description,
            tags=tag_list,
            privacy=privacy,
            instagram_caption=instagram_caption,
            schedule_time=schedule_dt,
            platforms=platform_list
        ))

        # Output results as JSON
        results_dict = [
            {
                "platform": r.platform,
                "success": r.success,
                "video_id": r.video_id,
                "video_url": r.video_url,
                "error_message": r.error_message,
                "upload_duration": r.upload_duration
            }
            for r in results
        ]

        print(json.dumps(results_dict, indent=2))

        # Exit with error if any uploads failed
        if any(not r.success for r in results):
            sys.exit(1)

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        print(json.dumps([{
            "platform": "all",
            "success": False,
            "error_message": str(e)
        }], indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()