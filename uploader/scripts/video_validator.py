"""
Video validation and processing utilities.
"""

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from loguru import logger


@dataclass
class ValidationResult:
    """Result of video validation."""
    is_valid: bool
    error_message: Optional[str] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[float] = None
    file_size: Optional[int] = None
    format: Optional[str] = None
    bitrate: Optional[int] = None
    fps: Optional[float] = None


class VideoValidator:
    """Validates video files for platform requirements."""

    # Platform limits
    YOUTUBE_SHORTS_MAX_DURATION = 60  # seconds
    INSTAGRAM_REELS_MAX_DURATION = 90  # seconds
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    MIN_RESOLUTION = (720, 1280)  # min width x height for vertical videos
    MAX_RESOLUTION = (1080, 1920)  # max width x height for vertical videos
    PREFERRED_ASPECT_RATIO = 9/16  # vertical aspect ratio
    SUPPORTED_FORMATS = ['.mp4', '.mov', '.avi']
    MIN_DURATION = 1.0  # minimum 1 second

    def __init__(self):
        self.ffprobe_available = self._check_ffprobe()

    def _check_ffprobe(self) -> bool:
        """Check if ffprobe is available for video analysis."""
        try:
            import subprocess
            result = subprocess.run(['ffprobe', '-version'],
                                 capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("ffprobe not found. Limited video validation available.")
            return False

    async def validate_video(self, video_path: str) -> ValidationResult:
        """
        Validate video file for platform requirements.

        Args:
            video_path: Path to video file

        Returns:
            ValidationResult object with validation status and metadata
        """
        try:
            # Check file existence
            if not os.path.exists(video_path):
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Video file not found: {video_path}"
                )

            # Check file extension
            file_ext = Path(video_path).suffix.lower()
            if file_ext not in self.SUPPORTED_FORMATS:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Unsupported format: {file_ext}. Supported: {self.SUPPORTED_FORMATS}"
                )

            # Check file size
            file_size = os.path.getsize(video_path)
            if file_size > self.MAX_FILE_SIZE:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"File too large: {file_size/1024/1024:.1f}MB. Max: {self.MAX_FILE_SIZE/1024/1024}MB"
                )

            if file_size == 0:
                return ValidationResult(
                    is_valid=False,
                    error_message="Video file is empty"
                )

            # Get video metadata using ffprobe if available
            if self.ffprobe_available:
                metadata = await self._get_video_metadata_ffprobe(video_path)
            else:
                # Fallback to basic validation
                metadata = await self._get_basic_metadata(video_path)

            # Validate metadata
            validation_errors = self._validate_metadata(metadata)
            if validation_errors:
                return ValidationResult(
                    is_valid=False,
                    error_message="; ".join(validation_errors),
                    **metadata
                )

            logger.info(f"Video validation successful: {video_path}")
            return ValidationResult(
                is_valid=True,
                **metadata
            )

        except Exception as e:
            logger.error(f"Video validation error: {e}")
            return ValidationResult(
                is_valid=False,
                error_message=f"Validation error: {str(e)}"
            )

    async def _get_video_metadata_ffprobe(self, video_path: str) -> dict:
        """Get detailed video metadata using ffprobe."""
        try:
            import subprocess
            import json

            # Run ffprobe to get video info
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise Exception(f"ffprobe failed: {stderr.decode()}")

            data = json.loads(stdout.decode())

            # Find video stream
            video_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break

            if not video_stream:
                raise Exception("No video stream found")

            # Extract metadata
            duration = float(data.get('format', {}).get('duration', 0))
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            fps = self._parse_fps(video_stream.get('r_frame_rate', '0/1'))
            bitrate = int(data.get('format', {}).get('bit_rate', 0))
            file_size = int(data.get('format', {}).get('size', 0))

            aspect_ratio = width / height if height > 0 else 0

            return {
                'duration': duration,
                'width': width,
                'height': height,
                'aspect_ratio': aspect_ratio,
                'file_size': file_size,
                'format': video_stream.get('codec_name', 'unknown'),
                'bitrate': bitrate,
                'fps': fps
            }

        except Exception as e:
            logger.error(f"ffprobe metadata extraction failed: {e}")
            raise

    async def _get_basic_metadata(self, video_path: str) -> dict:
        """Get basic video metadata without ffprobe."""
        file_size = os.path.getsize(video_path)

        # Try to use OpenCV for basic info
        try:
            import cv2
            cap = cv2.VideoCapture(video_path)

            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = frame_count / fps if fps > 0 else 0

                cap.release()

                return {
                    'duration': duration,
                    'width': width,
                    'height': height,
                    'aspect_ratio': width / height if height > 0 else 0,
                    'file_size': file_size,
                    'format': 'unknown',
                    'bitrate': 0,
                    'fps': fps
                }

        except ImportError:
            logger.warning("OpenCV not available for video analysis")
        except Exception as e:
            logger.warning(f"OpenCV video analysis failed: {e}")

        # Minimal fallback
        return {
            'duration': 0,
            'width': 0,
            'height': 0,
            'aspect_ratio': 0,
            'file_size': file_size,
            'format': 'unknown',
            'bitrate': 0,
            'fps': 0
        }

    def _parse_fps(self, fps_string: str) -> float:
        """Parse fps from fractional string like '30/1'."""
        try:
            if '/' in fps_string:
                num, den = fps_string.split('/')
                return float(num) / float(den)
            return float(fps_string)
        except (ValueError, ZeroDivisionError):
            return 0.0

    def _validate_metadata(self, metadata: dict) -> list:
        """Validate video metadata against platform requirements."""
        errors = []

        duration = metadata.get('duration', 0)
        width = metadata.get('width', 0)
        height = metadata.get('height', 0)
        aspect_ratio = metadata.get('aspect_ratio', 0)

        # Duration validation
        if duration < self.MIN_DURATION:
            errors.append(f"Video too short: {duration:.1f}s (min: {self.MIN_DURATION}s)")

        if duration > self.INSTAGRAM_REELS_MAX_DURATION:
            errors.append(f"Video too long: {duration:.1f}s (max: {self.INSTAGRAM_REELS_MAX_DURATION}s for Reels, {self.YOUTUBE_SHORTS_MAX_DURATION}s for Shorts)")

        # Resolution validation
        if width > 0 and height > 0:
            if width < self.MIN_RESOLUTION[0] or height < self.MIN_RESOLUTION[1]:
                errors.append(f"Resolution too low: {width}x{height} (min: {self.MIN_RESOLUTION[0]}x{self.MIN_RESOLUTION[1]})")

            if width > self.MAX_RESOLUTION[0] or height > self.MAX_RESOLUTION[1]:
                errors.append(f"Resolution too high: {width}x{height} (max: {self.MAX_RESOLUTION[0]}x{self.MAX_RESOLUTION[1]})")

            # Aspect ratio validation (prefer vertical)
            if aspect_ratio > 0:
                if aspect_ratio > 1.0:  # Landscape
                    errors.append(f"Video is landscape ({aspect_ratio:.2f}). Vertical videos (9:16) work best for Shorts/Reels")
                elif abs(aspect_ratio - self.PREFERRED_ASPECT_RATIO) > 0.1:
                    errors.append(f"Aspect ratio {aspect_ratio:.2f} may not be optimal. Preferred: {self.PREFERRED_ASPECT_RATIO:.2f} (9:16)")

        return errors

    async def get_video_info(self, video_path: str) -> dict:
        """Get comprehensive video information."""
        validation_result = await self.validate_video(video_path)

        return {
            'path': video_path,
            'filename': os.path.basename(video_path),
            'is_valid': validation_result.is_valid,
            'error_message': validation_result.error_message,
            'duration': validation_result.duration,
            'resolution': f"{validation_result.width}x{validation_result.height}" if validation_result.width and validation_result.height else "unknown",
            'aspect_ratio': validation_result.aspect_ratio,
            'file_size_mb': validation_result.file_size / 1024 / 1024 if validation_result.file_size else 0,
            'format': validation_result.format,
            'bitrate_kbps': validation_result.bitrate / 1000 if validation_result.bitrate else 0,
            'fps': validation_result.fps,
            'youtube_shorts_compatible': self._is_youtube_shorts_compatible(validation_result),
            'instagram_reels_compatible': self._is_instagram_reels_compatible(validation_result)
        }

    def _is_youtube_shorts_compatible(self, result: ValidationResult) -> bool:
        """Check if video is compatible with YouTube Shorts."""
        if not result.is_valid:
            return False

        return (
            result.duration and result.duration <= self.YOUTUBE_SHORTS_MAX_DURATION and
            result.aspect_ratio and result.aspect_ratio <= 1.0  # Vertical or square
        )

    def _is_instagram_reels_compatible(self, result: ValidationResult) -> bool:
        """Check if video is compatible with Instagram Reels."""
        if not result.is_valid:
            return False

        return (
            result.duration and result.duration <= self.INSTAGRAM_REELS_MAX_DURATION and
            result.aspect_ratio and result.aspect_ratio <= 1.0  # Vertical or square
        )

    async def optimize_for_platforms(self, video_path: str, output_path: str) -> bool:
        """
        Optimize video for platform requirements (requires ffmpeg).

        Args:
            video_path: Input video path
            output_path: Output video path

        Returns:
            bool: True if optimization successful
        """
        try:
            import subprocess

            # Check if ffmpeg is available
            try:
                subprocess.run(['ffmpeg', '-version'],
                             capture_output=True, timeout=5)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                logger.error("ffmpeg not found. Cannot optimize video.")
                return False

            # Optimization command for vertical video
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                '-y',  # Overwrite output file
                output_path
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logger.info(f"Video optimized successfully: {output_path}")
                return True
            else:
                logger.error(f"Video optimization failed: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"Video optimization error: {e}")
            return False