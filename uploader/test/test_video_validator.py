"""
Unit tests for video validator.
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import pytest

from scripts.video_validator import VideoValidator, ValidationResult


class TestVideoValidator(unittest.TestCase):
    """Test cases for VideoValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = VideoValidator()

    def test_init(self):
        """Test validator initialization."""
        self.assertIsInstance(self.validator, VideoValidator)
        self.assertIsInstance(self.validator.ffprobe_available, bool)

    def test_check_ffprobe_available(self):
        """Test ffprobe availability check."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            validator = VideoValidator()
            self.assertTrue(validator._check_ffprobe())

    def test_check_ffprobe_not_available(self):
        """Test ffprobe not available."""
        with patch('subprocess.run', side_effect=FileNotFoundError):
            validator = VideoValidator()
            self.assertFalse(validator._check_ffprobe())

    @pytest.mark.asyncio
    async def test_validate_video_file_not_found(self):
        """Test validation with non-existent file."""
        result = await self.validator.validate_video('/nonexistent/path.mp4')

        self.assertFalse(result.is_valid)
        self.assertIn("Video file not found", result.error_message)

    @pytest.mark.asyncio
    async def test_validate_video_unsupported_format(self):
        """Test validation with unsupported format."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b'test content')
            temp_file.flush()

            try:
                result = await self.validator.validate_video(temp_file.name)
                self.assertFalse(result.is_valid)
                self.assertIn("Unsupported format", result.error_message)
            finally:
                os.unlink(temp_file.name)

    @pytest.mark.asyncio
    async def test_validate_video_empty_file(self):
        """Test validation with empty file."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.flush()

            try:
                result = await self.validator.validate_video(temp_file.name)
                self.assertFalse(result.is_valid)
                self.assertIn("Video file is empty", result.error_message)
            finally:
                os.unlink(temp_file.name)

    @pytest.mark.asyncio
    async def test_validate_video_file_too_large(self):
        """Test validation with file too large."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            # Write more than max file size
            large_data = b'0' * (self.validator.MAX_FILE_SIZE + 1000)
            temp_file.write(large_data)
            temp_file.flush()

            try:
                result = await self.validator.validate_video(temp_file.name)
                self.assertFalse(result.is_valid)
                self.assertIn("File too large", result.error_message)
            finally:
                os.unlink(temp_file.name)

    def test_parse_fps_fractional(self):
        """Test FPS parsing from fractional string."""
        fps = self.validator._parse_fps("30/1")
        self.assertEqual(fps, 30.0)

        fps = self.validator._parse_fps("25/1")
        self.assertEqual(fps, 25.0)

        fps = self.validator._parse_fps("invalid")
        self.assertEqual(fps, 0.0)

    def test_validate_metadata_duration_too_short(self):
        """Test metadata validation with short duration."""
        metadata = {
            'duration': 0.5,  # Too short
            'width': 1080,
            'height': 1920,
            'aspect_ratio': 1080/1920
        }

        errors = self.validator._validate_metadata(metadata)
        self.assertTrue(any("too short" in error for error in errors))

    def test_validate_metadata_duration_too_long(self):
        """Test metadata validation with long duration."""
        metadata = {
            'duration': 100,  # Too long
            'width': 1080,
            'height': 1920,
            'aspect_ratio': 1080/1920
        }

        errors = self.validator._validate_metadata(metadata)
        self.assertTrue(any("too long" in error for error in errors))

    def test_validate_metadata_resolution_too_low(self):
        """Test metadata validation with low resolution."""
        metadata = {
            'duration': 30,
            'width': 640,  # Too low
            'height': 480,  # Too low
            'aspect_ratio': 640/480
        }

        errors = self.validator._validate_metadata(metadata)
        self.assertTrue(any("too low" in error for error in errors))

    def test_validate_metadata_landscape_video(self):
        """Test metadata validation with landscape video."""
        metadata = {
            'duration': 30,
            'width': 1920,  # Landscape
            'height': 1080,
            'aspect_ratio': 1920/1080
        }

        errors = self.validator._validate_metadata(metadata)
        self.assertTrue(any("landscape" in error for error in errors))

    def test_is_youtube_shorts_compatible(self):
        """Test YouTube Shorts compatibility check."""
        valid_result = ValidationResult(
            is_valid=True,
            duration=45,
            aspect_ratio=9/16
        )
        self.assertTrue(self.validator._is_youtube_shorts_compatible(valid_result))

        invalid_result = ValidationResult(
            is_valid=True,
            duration=70,  # Too long
            aspect_ratio=9/16
        )
        self.assertFalse(self.validator._is_youtube_shorts_compatible(invalid_result))

    def test_is_instagram_reels_compatible(self):
        """Test Instagram Reels compatibility check."""
        valid_result = ValidationResult(
            is_valid=True,
            duration=60,
            aspect_ratio=9/16
        )
        self.assertTrue(self.validator._is_instagram_reels_compatible(valid_result))

        invalid_result = ValidationResult(
            is_valid=True,
            duration=100,  # Too long
            aspect_ratio=9/16
        )
        self.assertFalse(self.validator._is_instagram_reels_compatible(invalid_result))

    @pytest.mark.asyncio
    async def test_get_basic_metadata_no_opencv(self):
        """Test basic metadata extraction without OpenCV."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(b'fake video data')
            temp_file.flush()

            try:
                with patch('scripts.video_validator.cv2', None):
                    metadata = await self.validator._get_basic_metadata(temp_file.name)

                    self.assertEqual(metadata['duration'], 0)
                    self.assertEqual(metadata['width'], 0)
                    self.assertEqual(metadata['height'], 0)
                    self.assertGreater(metadata['file_size'], 0)
            finally:
                os.unlink(temp_file.name)


if __name__ == '__main__':
    unittest.main()