"""
Video uploader package for YouTube Shorts and Instagram Reels.
"""

__version__ = "1.0.0"
__author__ = "Video Uploader"
__description__ = "Production-ready Python package for uploading videos to YouTube Shorts and Instagram Reels"

from .upload_video import VideoUploader, UploadResult
from .youtube_uploader import YouTubeUploader
from .instagram_uploader import InstagramUploader
from .video_validator import VideoValidator, ValidationResult
from .config_manager import ConfigManager

__all__ = [
    'VideoUploader',
    'UploadResult',
    'YouTubeUploader',
    'InstagramUploader',
    'VideoValidator',
    'ValidationResult',
    'ConfigManager'
]