"""
Instagram API integration for Reels uploads using instagrapi.
"""

import asyncio
import os
import tempfile
from datetime import datetime
from typing import Dict, Optional

from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword, ChallengeRequired, FeedbackRequired,
    LoginRequired, PleaseWaitFewMinutes, RateLimitError,
    TwoFactorRequired, UnknownError
)
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential


class InstagramUploader:
    """Handles Instagram Reels uploads using instagrapi."""

    def __init__(self, config_manager):
        self.config = config_manager
        self.client = Client()
        self.authenticated = False

    async def authenticate(self) -> bool:
        """
        Authenticate with Instagram using username/password.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            username = self.config.get('instagram.username')
            password = self.config.get('instagram.password')
            session_path = self.config.get('instagram.session_path', 'data/instagram_session.json')

            if not username or not password:
                raise ValueError("Instagram username and password are required")

            # Try to load existing session
            if os.path.exists(session_path):
                try:
                    self.client.load_settings(session_path)
                    self.client.login(username, password)
                    logger.info("Instagram session loaded successfully")
                    self.authenticated = True
                    return True
                except Exception as e:
                    logger.warning(f"Failed to load Instagram session: {e}")

            # Fresh login
            logger.info("Performing fresh Instagram login...")
            self.client.login(username, password)

            # Save session
            self.client.dump_settings(session_path)
            logger.info(f"Instagram session saved to {session_path}")

            self.authenticated = True
            return True

        except TwoFactorRequired:
            logger.error("Instagram requires 2FA. Please handle this manually.")
            return False
        except ChallengeRequired:
            logger.error("Instagram challenge required. Please verify your account.")
            return False
        except BadPassword:
            logger.error("Invalid Instagram username or password")
            return False
        except PleaseWaitFewMinutes:
            logger.error("Instagram rate limit. Please wait before retrying.")
            return False
        except Exception as e:
            logger.error(f"Instagram authentication failed: {e}")
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def upload(
        self,
        video_path: str,
        caption: str,
        schedule_time: Optional[datetime] = None,
        cover_frame_time: float = 1.0,
        share_to_story: bool = False,
        share_to_facebook: bool = False,
        **kwargs
    ) -> Dict:
        """
        Upload video to Instagram as a Reel.

        Args:
            video_path: Path to video file
            caption: Video caption with hashtags
            schedule_time: Scheduled publish time (Note: Instagram doesn't support scheduling via API)
            cover_frame_time: Time in seconds for cover frame extraction
            share_to_story: Whether to share Reel to Story
            share_to_facebook: Whether to cross-post to Facebook
            **kwargs: Additional parameters

        Returns:
            Dict containing media ID and other metadata
        """
        if not self.authenticated:
            if not await self.authenticate():
                raise Exception("Instagram authentication failed")

        try:
            # Note: Instagram API doesn't support scheduling, so we'll ignore schedule_time
            if schedule_time:
                logger.warning("Instagram doesn't support scheduled posts via API. Publishing immediately.")

            logger.info(f"Starting Instagram Reel upload: {caption[:50]}...")

            # Generate cover image if needed
            cover_path = None
            if cover_frame_time > 0:
                cover_path = await self._extract_cover_frame(video_path, cover_frame_time)

            # Upload as Reel
            media = self.client.clip_upload(
                path=video_path,
                caption=self._format_caption(caption),
                thumbnail=cover_path
            )

            logger.info(f"Instagram Reel upload successful. Media ID: {media.pk}")

            # Optional: Share to Story
            if share_to_story:
                try:
                    self.client.story_share(media.pk)
                    logger.info("Reel shared to Story successfully")
                except Exception as e:
                    logger.warning(f"Failed to share to Story: {e}")

            # Clean up cover image
            if cover_path and os.path.exists(cover_path):
                os.unlink(cover_path)

            return {
                'pk': media.pk,
                'id': media.id,
                'code': media.code,
                'video_url': f"https://instagram.com/reel/{media.code}",
                'taken_at': media.taken_at,
                'media_type': media.media_type,
                'caption_text': media.caption_text
            }

        except RateLimitError as e:
            logger.error(f"Instagram rate limit exceeded: {e}")
            raise Exception("Instagram rate limit exceeded. Please try again later.")

        except FeedbackRequired as e:
            logger.error(f"Instagram feedback required: {e}")
            raise Exception("Instagram requires feedback. Please check your account.")

        except LoginRequired as e:
            logger.error(f"Instagram login required: {e}")
            self.authenticated = False
            raise Exception("Instagram login expired. Please re-authenticate.")

        except Exception as e:
            logger.error(f"Instagram upload error: {e}")
            raise Exception(f"Instagram upload failed: {str(e)}")

    async def _extract_cover_frame(self, video_path: str, frame_time: float) -> str:
        """Extract cover frame from video at specified time."""
        try:
            import cv2

            # Create temporary file for cover image
            temp_cover = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_cover.close()

            # Extract frame using OpenCV
            cap = cv2.VideoCapture(video_path)

            # Set position to extract frame
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(frame_time * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

            ret, frame = cap.read()
            if ret:
                cv2.imwrite(temp_cover.name, frame)
                logger.debug(f"Cover frame extracted to {temp_cover.name}")
            else:
                logger.warning("Failed to extract cover frame")
                return None

            cap.release()
            return temp_cover.name

        except ImportError:
            logger.warning("OpenCV not available. Using default cover.")
            return None
        except Exception as e:
            logger.warning(f"Cover frame extraction failed: {e}")
            return None

    def _format_caption(self, caption: str) -> str:
        """Format caption for Instagram with proper hashtags and limits."""
        # Instagram caption limit is 2200 characters
        if len(caption) > 2200:
            # Truncate but preserve hashtags at the end
            lines = caption.split('\n')
            hashtag_lines = [line for line in lines if line.strip().startswith('#')]
            content_lines = [line for line in lines if not line.strip().startswith('#')]

            content = '\n'.join(content_lines)
            hashtags = '\n'.join(hashtag_lines)

            # Calculate space for hashtags
            hashtag_space = len(hashtags) + 2 if hashtags else 0
            max_content_length = 2200 - hashtag_space

            if len(content) > max_content_length:
                content = content[:max_content_length-3] + "..."

            caption = f"{content}\n\n{hashtags}" if hashtags else content

        # Ensure #Reels hashtag is included
        if '#Reels' not in caption and '#reels' not in caption:
            caption += "\n\n#Reels"

        return caption

    async def get_media_info(self, media_pk: str) -> Dict:
        """Get information about uploaded media."""
        try:
            media = self.client.media_info(media_pk)
            return {
                'pk': media.pk,
                'id': media.id,
                'code': media.code,
                'url': f"https://instagram.com/reel/{media.code}",
                'view_count': media.view_count,
                'like_count': media.like_count,
                'comment_count': media.comment_count,
                'caption': media.caption_text
            }
        except Exception as e:
            logger.error(f"Error getting media info: {e}")
            raise

    async def delete_media(self, media_pk: str) -> bool:
        """Delete media from Instagram."""
        try:
            self.client.media_delete(media_pk)
            logger.info(f"Media {media_pk} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting media: {e}")
            return False

    async def get_account_info(self) -> Dict:
        """Get current account information."""
        try:
            user_info = self.client.account_info()
            return {
                'username': user_info.username,
                'full_name': user_info.full_name,
                'follower_count': user_info.follower_count,
                'following_count': user_info.following_count,
                'media_count': user_info.media_count,
                'is_verified': user_info.is_verified,
                'is_private': user_info.is_private
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            raise

    def logout(self):
        """Logout from Instagram."""
        try:
            self.client.logout()
            self.authenticated = False
            logger.info("Instagram logout successful")
        except Exception as e:
            logger.warning(f"Instagram logout warning: {e}")

    async def test_connection(self) -> bool:
        """Test Instagram connection and authentication."""
        try:
            if not self.authenticated:
                if not await self.authenticate():
                    return False

            # Try to get account info as a test
            account_info = await self.get_account_info()
            logger.info(f"Instagram connection test successful for @{account_info['username']}")
            return True

        except Exception as e:
            logger.error(f"Instagram connection test failed: {e}")
            return False