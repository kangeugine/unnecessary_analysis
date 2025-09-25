"""
Unit tests for configuration manager.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from scripts.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test_config.json')

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.config_path):
            os.unlink(self.config_path)
        os.rmdir(self.temp_dir)

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        config = ConfigManager()

        # Check that defaults are loaded
        self.assertEqual(config.get('youtube.category_id'), '22')
        self.assertEqual(config.get('youtube.default_privacy'), 'public')
        self.assertEqual(config.get('video.max_duration_youtube'), 60)
        self.assertEqual(config.get('video.max_duration_instagram'), 90)

    def test_init_with_config_file(self):
        """Test initialization with config file."""
        test_config = {
            'youtube': {
                'category_id': '25',
                'default_privacy': 'unlisted'
            },
            'custom_setting': 'test_value'
        }

        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)

        config = ConfigManager(self.config_path)

        # Check that file config overrides defaults
        self.assertEqual(config.get('youtube.category_id'), '25')
        self.assertEqual(config.get('youtube.default_privacy'), 'unlisted')
        self.assertEqual(config.get('custom_setting'), 'test_value')

        # Check that defaults are still present for non-overridden values
        self.assertEqual(config.get('video.max_duration_youtube'), 60)

    def test_get_with_dot_notation(self):
        """Test getting values with dot notation."""
        config = ConfigManager()

        # Test nested access
        self.assertEqual(config.get('youtube.category_id'), '22')
        self.assertEqual(config.get('video.max_file_size'), 500 * 1024 * 1024)

        # Test with default value
        self.assertEqual(config.get('nonexistent.key', 'default'), 'default')
        self.assertIsNone(config.get('nonexistent.key'))

    def test_set_with_dot_notation(self):
        """Test setting values with dot notation."""
        config = ConfigManager()

        config.set('youtube.category_id', '30')
        self.assertEqual(config.get('youtube.category_id'), '30')

        config.set('new_section.new_key', 'new_value')
        self.assertEqual(config.get('new_section.new_key'), 'new_value')

    def test_get_section(self):
        """Test getting entire configuration section."""
        config = ConfigManager()

        youtube_section = config.get_section('youtube')
        self.assertIsInstance(youtube_section, dict)
        self.assertIn('category_id', youtube_section)
        self.assertIn('default_privacy', youtube_section)

        # Test non-existent section
        empty_section = config.get_section('nonexistent')
        self.assertEqual(empty_section, {})

    @patch.dict(os.environ, {
        'YOUTUBE_CATEGORY_ID': '35',
        'INSTAGRAM_USERNAME': 'test_user',
        'MAX_FILE_SIZE': '1000000000',
        'LOG_LEVEL': 'DEBUG'
    })
    def test_load_environment_variables(self):
        """Test loading configuration from environment variables."""
        config = ConfigManager()

        # Check that environment variables override defaults
        self.assertEqual(config.get('youtube.category_id'), '35')
        self.assertEqual(config.get('instagram.username'), 'test_user')
        self.assertEqual(config.get('video.max_file_size'), 1000000000)
        self.assertEqual(config.get('logging.level'), 'DEBUG')

    def test_convert_env_value(self):
        """Test environment value conversion."""
        config = ConfigManager()

        # Test boolean conversion
        self.assertTrue(config._convert_env_value('true'))
        self.assertFalse(config._convert_env_value('false'))
        self.assertTrue(config._convert_env_value('True'))
        self.assertFalse(config._convert_env_value('False'))

        # Test integer conversion
        self.assertEqual(config._convert_env_value('123'), 123)
        self.assertEqual(config._convert_env_value('-456'), -456)

        # Test float conversion
        self.assertEqual(config._convert_env_value('123.45'), 123.45)
        self.assertEqual(config._convert_env_value('-67.89'), -67.89)

        # Test string (no conversion)
        self.assertEqual(config._convert_env_value('test_string'), 'test_string')

    def test_save_config(self):
        """Test saving configuration to file."""
        config = ConfigManager()
        config.set('test_key', 'test_value')

        output_path = os.path.join(self.temp_dir, 'saved_config.json')
        config.save_config(output_path)

        # Verify file was created and contains correct data
        self.assertTrue(os.path.exists(output_path))

        with open(output_path, 'r') as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data['test_key'], 'test_value')

    def test_validate_config(self):
        """Test configuration validation."""
        config = ConfigManager()

        validation_result = config.validate_config()

        # Should have errors and warnings lists
        self.assertIn('errors', validation_result)
        self.assertIn('warnings', validation_result)
        self.assertIsInstance(validation_result['errors'], list)
        self.assertIsInstance(validation_result['warnings'], list)

        # Should have error about missing YouTube credentials
        errors = validation_result['errors']
        self.assertTrue(any('YouTube credentials' in error for error in errors))

    def test_get_credentials_info(self):
        """Test getting credentials information."""
        config = ConfigManager()

        creds_info = config.get_credentials_info()

        # Check structure
        self.assertIn('youtube', creds_info)
        self.assertIn('instagram', creds_info)

        # Check YouTube info
        youtube_info = creds_info['youtube']
        self.assertIn('credentials_file_exists', youtube_info)
        self.assertIn('token_file_exists', youtube_info)
        self.assertIn('credentials_path', youtube_info)
        self.assertIn('token_path', youtube_info)

        # Check Instagram info
        instagram_info = creds_info['instagram']
        self.assertIn('username_configured', instagram_info)
        self.assertIn('password_configured', instagram_info)
        self.assertIn('session_file_exists', instagram_info)
        self.assertIn('session_path', instagram_info)

    def test_create_sample_config(self):
        """Test creating sample configuration file."""
        config = ConfigManager()
        sample_path = os.path.join(self.temp_dir, 'sample_config.json')

        config.create_sample_config(sample_path)

        # Verify file was created
        self.assertTrue(os.path.exists(sample_path))

        # Verify structure
        with open(sample_path, 'r') as f:
            sample_data = json.load(f)

        expected_sections = ['youtube', 'instagram', 'video', 'upload', 'logging']
        for section in expected_sections:
            self.assertIn(section, sample_data)

    def test_deep_merge(self):
        """Test deep merge functionality."""
        config = ConfigManager()

        base = {
            'section1': {'key1': 'value1', 'key2': 'value2'},
            'section2': {'key3': 'value3'}
        }

        update = {
            'section1': {'key2': 'new_value2', 'key4': 'value4'},
            'section3': {'key5': 'value5'}
        }

        config._deep_merge(base, update)

        # Check merged result
        self.assertEqual(base['section1']['key1'], 'value1')  # Unchanged
        self.assertEqual(base['section1']['key2'], 'new_value2')  # Updated
        self.assertEqual(base['section1']['key4'], 'value4')  # Added
        self.assertEqual(base['section2']['key3'], 'value3')  # Unchanged
        self.assertEqual(base['section3']['key5'], 'value5')  # Added

    def test_str_representation(self):
        """Test string representation masks sensitive data."""
        config = ConfigManager()
        config.set('instagram.password', 'secret_password')

        config_str = str(config)
        config_data = json.loads(config_str)

        # Password should be masked
        self.assertEqual(config_data['instagram']['password'], '***masked***')


if __name__ == '__main__':
    unittest.main()