"""
YouTube API integration for video uploads with OAuth2 authentication.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

import google.auth.transport.requests
import google.oauth2.credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential


class YouTubeUploader:
    """Handles YouTube video uploads with OAuth2 authentication."""

    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'

    def __init__(self, config_manager):
        self.config = config_manager
        self.youtube = None
        self.credentials = None

    async def authenticate(self) -> bool:
        """
        Authenticate with YouTube API using OAuth2.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            creds_path = self.config.get('youtube.credentials_path', 'data/youtube_credentials.json')
            token_path = self.config.get('youtube.token_path', 'data/youtube_token.json')

            creds = None

            # Load existing token
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)

            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing YouTube credentials...")
                    creds.refresh(Request())
                else:
                    logger.info("Starting YouTube OAuth2 flow...")
                    if not os.path.exists(creds_path):
                        raise FileNotFoundError(
                            f"YouTube credentials file not found at {creds_path}. "
                            "Please download from Google Cloud Console."
                        )

                    flow = InstalledAppFlow.from_client_secrets_file(creds_path, self.SCOPES)
                    creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                logger.info(f"YouTube credentials saved to {token_path}")

            self.credentials = creds
            self.youtube = build(self.API_SERVICE_NAME, self.API_VERSION, credentials=creds)
            logger.info("YouTube authentication successful")
            return True

        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def upload(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        privacy: str = "public",
        category_id: str = "22",  # People & Blogs
        schedule_time: Optional[datetime] = None,
        thumbnail_path: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Upload video to YouTube as a Short.

        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            privacy: Privacy setting (public, unlisted, private)
            category_id: YouTube category ID
            schedule_time: Scheduled publish time
            thumbnail_path: Path to custom thumbnail
            **kwargs: Additional parameters

        Returns:
            Dict containing video ID and other metadata
        """
        if not self.youtube:
            if not await self.authenticate():
                raise Exception("YouTube authentication failed")

        try:
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': self._format_description(description, tags),
                    'tags': tags[:500] if tags else [],  # YouTube tag limit
                    'categoryId': category_id,
                    'defaultLanguage': 'en',
                    'defaultAudioLanguage': 'en'
                },
                'status': {
                    'privacyStatus': privacy,
                    'selfDeclaredMadeForKids': False,
                    'embeddable': True,
                    'publicStatsViewable': True
                }
            }

            # Add scheduled publish time
            if schedule_time:
                body['status']['publishAt'] = schedule_time.isoformat()
                body['status']['privacyStatus'] = 'private'  # Must be private for scheduled videos

            # Prepare media upload
            media = MediaFileUpload(
                video_path,
                chunksize=1024*1024*4,  # 4MB chunks
                resumable=True,
                mimetype='video/mp4'
            )

            logger.info(f"Starting YouTube upload: {title}")

            # Execute upload
            insert_request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            response = await self._execute_upload_with_progress(insert_request)

            video_id = response['id']
            logger.info(f"YouTube upload successful. Video ID: {video_id}")

            # Upload custom thumbnail if provided
            if thumbnail_path and os.path.exists(thumbnail_path):
                await self._upload_thumbnail(video_id, thumbnail_path)

            # Ensure video is recognized as a Short
            await self._optimize_for_shorts(video_id)

            return {
                'id': video_id,
                'url': f'https://youtube.com/watch?v={video_id}',
                'shorts_url': f'https://youtube.com/shorts/{video_id}',
                'status': response.get('status', {}),
                'snippet': response.get('snippet', {})
            }

        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            error_message = error_details.get('error', {}).get('message', str(e))
            logger.error(f"YouTube API error: {error_message}")
            raise Exception(f"YouTube upload failed: {error_message}")

        except Exception as e:
            logger.error(f"YouTube upload error: {e}")
            raise

    async def _execute_upload_with_progress(self, insert_request) -> Dict:
        """Execute upload with progress tracking."""
        response = None
        error = None
        retry_count = 0
        max_retries = 3

        while response is None:
            try:
                status, response = insert_request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"YouTube upload progress: {progress}%")

            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    if retry_count < max_retries:
                        retry_count += 1
                        logger.warning(f"Retryable error occurred. Retry {retry_count}/{max_retries}")
                        await asyncio.sleep(2 ** retry_count)
                        continue
                raise
            except Exception as e:
                logger.error(f"Upload error: {e}")
                raise

        return response

    async def _upload_thumbnail(self, video_id: str, thumbnail_path: str):
        """Upload custom thumbnail for video."""
        try:
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            logger.info(f"Thumbnail uploaded for video {video_id}")
        except Exception as e:
            logger.warning(f"Thumbnail upload failed: {e}")

    async def _optimize_for_shorts(self, video_id: str):
        """Optimize video settings for YouTube Shorts."""
        try:
            # Add #Shorts hashtag to description if not present
            video_response = self.youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()

            if video_response['items']:
                snippet = video_response['items'][0]['snippet']
                description = snippet.get('description', '')

                if '#Shorts' not in description and '#shorts' not in description:
                    # Update description to include #Shorts
                    updated_description = f"{description}\n\n#Shorts"

                    self.youtube.videos().update(
                        part='snippet',
                        body={
                            'id': video_id,
                            'snippet': {
                                **snippet,
                                'description': updated_description
                            }
                        }
                    ).execute()

                    logger.info("Added #Shorts hashtag to video description")

        except Exception as e:
            logger.warning(f"Shorts optimization failed: {e}")

    def _format_description(self, description: str, tags: Optional[List[str]] = None) -> str:
        """Format video description with tags and Shorts optimization."""
        formatted_desc = description

        # Add tags as hashtags
        if tags:
            hashtags = [f"#{tag.replace(' ', '').replace('#', '')}" for tag in tags[:10]]
            formatted_desc += f"\n\n{' '.join(hashtags)}"

        # Ensure #Shorts is included
        if '#Shorts' not in formatted_desc and '#shorts' not in formatted_desc:
            formatted_desc += "\n\n#Shorts"

        # YouTube description limit is 5000 characters
        return formatted_desc[:5000]

    async def get_video_status(self, video_id: str) -> Dict:
        """Get current status of uploaded video."""
        try:
            response = self.youtube.videos().list(
                part='status,processingDetails,snippet',
                id=video_id
            ).execute()

            if response['items']:
                return response['items'][0]
            else:
                raise Exception(f"Video {video_id} not found")

        except Exception as e:
            logger.error(f"Error getting video status: {e}")
            raise

    async def delete_video(self, video_id: str) -> bool:
        """Delete video from YouTube."""
        try:
            self.youtube.videos().delete(id=video_id).execute()
            logger.info(f"Video {video_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting video: {e}")
            return False