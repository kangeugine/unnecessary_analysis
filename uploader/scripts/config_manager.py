"""
Configuration management for video uploader.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from loguru import logger
from dotenv import load_dotenv


class ConfigManager:
    """Manages configuration from environment variables, config files, and defaults."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_data = {}
        self.config_path = config_path

        # Load configuration in order of precedence
        self._load_defaults()
        self._load_config_file()
        self._load_environment()

    def _load_defaults(self):
        """Load default configuration values."""
        self.config_data = {
            'youtube': {
                'credentials_path': 'data/youtube_credentials.json',
                'token_path': 'data/youtube_token.json',
                'category_id': '22',  # People & Blogs
                'default_privacy': 'public',
                'default_tags': ['Shorts', 'Video', 'Content'],
                'chunk_size': 4 * 1024 * 1024,  # 4MB
                'max_retries': 3
            },
            'instagram': {
                'session_path': 'data/instagram_session.json',
                'max_retries': 3,
                'delay_between_uploads': 30,  # seconds
                'default_hashtags': ['#Reels', '#Instagram', '#Video']
            },
            'video': {
                'max_file_size': 500 * 1024 * 1024,  # 500MB
                'supported_formats': ['.mp4', '.mov', '.avi'],
                'max_duration_youtube': 60,  # seconds
                'max_duration_instagram': 90,  # seconds
                'min_duration': 1.0,
                'preferred_aspect_ratio': 9/16,
                'min_resolution': [720, 1280],
                'max_resolution': [1080, 1920]
            },
            'upload': {
                'concurrent_uploads': True,
                'retry_delays': [1, 2, 4, 8],  # exponential backoff
                'timeout': 300,  # 5 minutes
                'chunk_upload_timeout': 60
            },
            'logging': {
                'level': 'INFO',
                'file_path': 'uploads.log',
                'max_file_size': '10 MB',
                'backup_count': 5,
                'format': '{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}'
            }
        }

    def _load_config_file(self):
        """Load configuration from file."""
        if not self.config_path:
            # Try default config file locations
            possible_paths = [
                'data/config.json',
                'data/config.yaml',
                'data/config.yml',
                'config.json',
                'config.yaml',
                'config.yml'
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    self.config_path = path
                    break

        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    if self.config_path.endswith(('.yaml', '.yml')):
                        file_config = yaml.safe_load(f)
                    else:
                        file_config = json.load(f)

                # Merge with existing config
                self._deep_merge(self.config_data, file_config)
                logger.info(f"Configuration loaded from {self.config_path}")

            except Exception as e:
                logger.warning(f"Failed to load config file {self.config_path}: {e}")

    def _load_environment(self):
        """Load configuration from environment variables."""
        load_dotenv()

        # Map environment variables to config keys
        env_mappings = {
            # YouTube
            'YOUTUBE_CREDENTIALS_PATH': 'youtube.credentials_path',
            'YOUTUBE_TOKEN_PATH': 'youtube.token_path',
            'YOUTUBE_CATEGORY_ID': 'youtube.category_id',
            'YOUTUBE_DEFAULT_PRIVACY': 'youtube.default_privacy',

            # Instagram
            'INSTAGRAM_USERNAME': 'instagram.username',
            'INSTAGRAM_PASSWORD': 'instagram.password',
            'INSTAGRAM_SESSION_PATH': 'instagram.session_path',

            # Video
            'MAX_FILE_SIZE': 'video.max_file_size',
            'MAX_DURATION_YOUTUBE': 'video.max_duration_youtube',
            'MAX_DURATION_INSTAGRAM': 'video.max_duration_instagram',

            # Upload
            'UPLOAD_TIMEOUT': 'upload.timeout',
            'MAX_RETRIES': 'youtube.max_retries',

            # Logging
            'LOG_LEVEL': 'logging.level',
            'LOG_FILE': 'logging.file_path'
        }

        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert value to appropriate type
                converted_value = self._convert_env_value(value)
                self._set_nested_value(self.config_data, config_key, converted_value)

    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _deep_merge(self, base: Dict, update: Dict):
        """Deep merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _set_nested_value(self, data: Dict, key_path: str, value: Any):
        """Set value in nested dictionary using dot notation."""
        keys = key_path.split('.')
        current = data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key_path: Dot-separated path to config value (e.g., 'youtube.credentials_path')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        current = self.config_data

        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation."""
        self._set_nested_value(self.config_data, key_path, value)

    def get_section(self, section: str) -> Dict:
        """Get entire configuration section."""
        return self.config_data.get(section, {})

    def save_config(self, output_path: Optional[str] = None):
        """Save current configuration to file."""
        if not output_path:
            output_path = self.config_path or 'data/config.json'

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            with open(output_path, 'w') as f:
                if output_path.endswith(('.yaml', '.yml')):
                    yaml.dump(self.config_data, f, indent=2, default_flow_style=False)
                else:
                    json.dump(self.config_data, f, indent=2)

            logger.info(f"Configuration saved to {output_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def validate_config(self) -> Dict[str, list]:
        """
        Validate configuration and return any issues.

        Returns:
            Dictionary with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []

        # Check required YouTube settings
        if not os.path.exists(self.get('youtube.credentials_path', '')):
            errors.append("YouTube credentials file not found. Download from Google Cloud Console.")

        # Check Instagram credentials
        if not self.get('instagram.username'):
            warnings.append("Instagram username not configured")
        if not self.get('instagram.password'):
            warnings.append("Instagram password not configured")

        # Validate video settings
        max_file_size = self.get('video.max_file_size', 0)
        if max_file_size <= 0:
            errors.append("Invalid max file size configuration")

        # Validate paths
        data_dir = Path('data')
        if not data_dir.exists():
            warnings.append("Data directory does not exist. It will be created automatically.")

        return {
            'errors': errors,
            'warnings': warnings
        }

    def create_sample_config(self, output_path: str = 'data/config_sample.json'):
        """Create a sample configuration file with all options."""
        sample_config = {
            "youtube": {
                "credentials_path": "data/youtube_credentials.json",
                "token_path": "data/youtube_token.json",
                "category_id": "22",
                "default_privacy": "public",
                "default_tags": ["Shorts", "YourBrand", "Content"],
                "chunk_size": 4194304,
                "max_retries": 3
            },
            "instagram": {
                "username": "your_instagram_username",
                "password": "your_instagram_password",
                "session_path": "data/instagram_session.json",
                "max_retries": 3,
                "delay_between_uploads": 30,
                "default_hashtags": ["#Reels", "#YourBrand", "#Content"]
            },
            "video": {
                "max_file_size": 524288000,
                "supported_formats": [".mp4", ".mov", ".avi"],
                "max_duration_youtube": 60,
                "max_duration_instagram": 90,
                "min_duration": 1.0,
                "preferred_aspect_ratio": 0.5625,
                "min_resolution": [720, 1280],
                "max_resolution": [1080, 1920]
            },
            "upload": {
                "concurrent_uploads": True,
                "retry_delays": [1, 2, 4, 8],
                "timeout": 300,
                "chunk_upload_timeout": 60
            },
            "logging": {
                "level": "INFO",
                "file_path": "uploads.log",
                "max_file_size": "10 MB",
                "backup_count": 5
            }
        }

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            with open(output_path, 'w') as f:
                json.dump(sample_config, f, indent=2)
            logger.info(f"Sample configuration created at {output_path}")
        except Exception as e:
            logger.error(f"Failed to create sample config: {e}")
            raise

    def get_credentials_info(self) -> Dict:
        """Get information about configured credentials."""
        info = {
            'youtube': {
                'credentials_file_exists': os.path.exists(self.get('youtube.credentials_path', '')),
                'token_file_exists': os.path.exists(self.get('youtube.token_path', '')),
                'credentials_path': self.get('youtube.credentials_path', ''),
                'token_path': self.get('youtube.token_path', '')
            },
            'instagram': {
                'username_configured': bool(self.get('instagram.username')),
                'password_configured': bool(self.get('instagram.password')),
                'session_file_exists': os.path.exists(self.get('instagram.session_path', '')),
                'session_path': self.get('instagram.session_path', '')
            }
        }

        return info

    def __str__(self) -> str:
        """String representation of configuration."""
        # Return config without sensitive information
        safe_config = json.loads(json.dumps(self.config_data))

        # Mask sensitive data
        if 'instagram' in safe_config and 'password' in safe_config['instagram']:
            safe_config['instagram']['password'] = '***masked***'

        return json.dumps(safe_config, indent=2)