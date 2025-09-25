"""
Unit tests for main upload functionality.
"""

import asyncio
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scripts.upload_video import VideoUploader, UploadResult
from scripts.config_manager import ConfigManager
from scripts.video_validator import ValidationResult


class TestVideoUploader(unittest.TestCase):
    """Test cases for VideoUploader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = ConfigManager()
        self.uploader = VideoUploader()

    @patch('scripts.upload_video.YouTubeUploader')
    @patch('scripts.upload_video.InstagramUploader')
    @patch('scripts.upload_video.VideoValidator')
    def test_init(self, mock_validator, mock_instagram, mock_youtube):
        """Test uploader initialization."""
        uploader = VideoUploader()

        self.assertIsNotNone(uploader.config)
        mock_validator.assert_called_once()
        mock_youtube.assert_called_once()
        mock_instagram.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_video_validation_failure(self):
        """Test upload with video validation failure."""
        with patch.object(self.uploader.validator, 'validate_video') as mock_validate:
            mock_validate.return_value = ValidationResult(
                is_valid=False,
                error_message="Test validation error"
            )

            results = await self.uploader.upload_video(
                video_source=b'fake video data',
                title="Test Video",
                description="Test Description",
                platforms=["youtube", "instagram"]
            )

            # Should return failed results for both platforms
            self.assertEqual(len(results), 2)
            for result in results:
                self.assertFalse(result.success)
                self.assertIn("validation failed", result.error_message)

    @pytest.mark.asyncio
    async def test_upload_video_successful(self):
        """Test successful video upload to both platforms."""
        # Mock validation
        with patch.object(self.uploader.validator, 'validate_video') as mock_validate:
            mock_validate.return_value = ValidationResult(is_valid=True)

            # Mock YouTube upload
            with patch.object(self.uploader, '_upload_to_youtube') as mock_youtube:
                mock_youtube.return_value = UploadResult(
                    platform="youtube",
                    success=True,
                    video_id="test_youtube_id",
                    video_url="https://youtube.com/watch?v=test_youtube_id"
                )

                # Mock Instagram upload
                with patch.object(self.uploader, '_upload_to_instagram') as mock_instagram:
                    mock_instagram.return_value = UploadResult(
                        platform="instagram",
                        success=True,
                        video_id="test_instagram_id",
                        video_url="https://instagram.com/reel/test_code"
                    )

                    results = await self.uploader.upload_video(
                        video_source=b'fake video data',
                        title="Test Video",
                        description="Test Description",
                        platforms=["youtube", "instagram"]
                    )

                    # Should have successful results for both platforms
                    self.assertEqual(len(results), 2)

                    youtube_result = next(r for r in results if r.platform == "youtube")
                    instagram_result = next(r for r in results if r.platform == "instagram")

                    self.assertTrue(youtube_result.success)
                    self.assertEqual(youtube_result.video_id, "test_youtube_id")

                    self.assertTrue(instagram_result.success)
                    self.assertEqual(instagram_result.video_id, "test_instagram_id")

    @pytest.mark.asyncio
    async def test_upload_video_partial_failure(self):
        """Test upload with one platform failing."""
        with patch.object(self.uploader.validator, 'validate_video') as mock_validate:
            mock_validate.return_value = ValidationResult(is_valid=True)

            # Mock YouTube success
            with patch.object(self.uploader, '_upload_to_youtube') as mock_youtube:
                mock_youtube.return_value = UploadResult(
                    platform="youtube",
                    success=True,
                    video_id="test_youtube_id"
                )

                # Mock Instagram failure
                with patch.object(self.uploader, '_upload_to_instagram') as mock_instagram:
                    mock_instagram.side_effect = Exception("Instagram upload failed")

                    results = await self.uploader.upload_video(
                        video_source=b'fake video data',
                        title="Test Video",
                        description="Test Description",
                        platforms=["youtube", "instagram"]
                    )

                    # Should have one success and one failure
                    successful = [r for r in results if r.success]
                    failed = [r for r in results if not r.success]

                    self.assertEqual(len(successful), 1)
                    self.assertEqual(len(failed), 1)
                    self.assertEqual(successful[0].platform, "youtube")
                    self.assertEqual(failed[0].platform, "instagram")

    @pytest.mark.asyncio
    async def test_upload_video_with_file_path(self):
        """Test upload with file path instead of bytes."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(b'fake video data')
            temp_file.flush()

            try:
                with patch.object(self.uploader.validator, 'validate_video') as mock_validate:
                    mock_validate.return_value = ValidationResult(is_valid=True)

                    with patch.object(self.uploader, '_upload_to_youtube') as mock_youtube:
                        mock_youtube.return_value = UploadResult(
                            platform="youtube",
                            success=True,
                            video_id="test_id"
                        )

                        results = await self.uploader.upload_video(
                            video_source=temp_file.name,
                            title="Test Video",
                            description="Test Description",
                            platforms=["youtube"]
                        )

                        self.assertEqual(len(results), 1)
                        self.assertTrue(results[0].success)

            finally:
                import os
                os.unlink(temp_file.name)

    @pytest.mark.asyncio
    async def test_upload_to_youtube_success(self):
        """Test successful YouTube upload."""
        mock_response = {
            'id': 'test_video_id',
            'status': {'privacyStatus': 'public'},
            'snippet': {'title': 'Test Video'}
        }

        with patch.object(self.uploader.youtube_uploader, 'upload') as mock_upload:
            mock_upload.return_value = mock_response

            result = await self.uploader._upload_to_youtube(
                video_path='/fake/path.mp4',
                title='Test Video',
                description='Test Description',
                tags=['test'],
                privacy='public',
                schedule_time=None
            )

            self.assertTrue(result.success)
            self.assertEqual(result.platform, 'youtube')
            self.assertEqual(result.video_id, 'test_video_id')
            self.assertIn('youtube.com/watch', result.video_url)

    @pytest.mark.asyncio
    async def test_upload_to_youtube_failure(self):
        """Test failed YouTube upload."""
        with patch.object(self.uploader.youtube_uploader, 'upload') as mock_upload:
            mock_upload.side_effect = Exception("YouTube API error")

            result = await self.uploader._upload_to_youtube(
                video_path='/fake/path.mp4',
                title='Test Video',
                description='Test Description',
                tags=['test'],
                privacy='public',
                schedule_time=None
            )

            self.assertFalse(result.success)
            self.assertEqual(result.platform, 'youtube')
            self.assertIn("YouTube API error", result.error_message)

    @pytest.mark.asyncio
    async def test_upload_to_instagram_success(self):
        """Test successful Instagram upload."""
        mock_response = {
            'pk': 'test_media_id',
            'video_url': 'https://instagram.com/reel/test_code'
        }

        with patch.object(self.uploader.instagram_uploader, 'upload') as mock_upload:
            mock_upload.return_value = mock_response

            result = await self.uploader._upload_to_instagram(
                video_path='/fake/path.mp4',
                caption='Test Caption',
                schedule_time=None
            )

            self.assertTrue(result.success)
            self.assertEqual(result.platform, 'instagram')
            self.assertEqual(result.video_id, 'test_media_id')

    @pytest.mark.asyncio
    async def test_upload_to_instagram_failure(self):
        """Test failed Instagram upload."""
        with patch.object(self.uploader.instagram_uploader, 'upload') as mock_upload:
            mock_upload.side_effect = Exception("Instagram API error")

            result = await self.uploader._upload_to_instagram(
                video_path='/fake/path.mp4',
                caption='Test Caption',
                schedule_time=None
            )

            self.assertFalse(result.success)
            self.assertEqual(result.platform, 'instagram')
            self.assertIn("Instagram API error", result.error_message)

    def test_upload_result_dataclass(self):
        """Test UploadResult dataclass."""
        result = UploadResult(
            platform="youtube",
            success=True,
            video_id="test_id",
            video_url="https://youtube.com/watch?v=test_id",
            upload_duration=45.5
        )

        self.assertEqual(result.platform, "youtube")
        self.assertTrue(result.success)
        self.assertEqual(result.video_id, "test_id")
        self.assertEqual(result.video_url, "https://youtube.com/watch?v=test_id")
        self.assertEqual(result.upload_duration, 45.5)
        self.assertIsNone(result.error_message)

        # Test failed result
        failed_result = UploadResult(
            platform="instagram",
            success=False,
            error_message="Upload failed"
        )

        self.assertEqual(failed_result.platform, "instagram")
        self.assertFalse(failed_result.success)
        self.assertEqual(failed_result.error_message, "Upload failed")
        self.assertIsNone(failed_result.video_id)
        self.assertIsNone(failed_result.video_url)
        self.assertEqual(failed_result.upload_duration, 0.0)


if __name__ == '__main__':
    unittest.main()