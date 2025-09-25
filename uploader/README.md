# YouTube Shorts & Instagram Reels Uploader

A production-ready Python script for programmatically uploading videos to both YouTube Shorts and Instagram Reels with comprehensive error handling, validation, and monitoring.

## Features

- **Dual Platform Upload**: Simultaneously upload to YouTube Shorts and Instagram Reels
- **API-Based Authentication**: Uses official APIs with OAuth2 (YouTube) and session management (Instagram)
- **Video Validation**: Comprehensive validation for format, duration, resolution, and platform requirements
- **Async Operations**: Concurrent uploads with proper error handling and retry logic
- **Structured Logging**: JSON-formatted logs with progress tracking and detailed error reporting
- **Configuration Management**: Flexible config via files, environment variables, and CLI arguments
- **Production Ready**: Implements retry logic, rate limiting, chunked uploads, and graceful error handling

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up YouTube API credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the YouTube Data API v3
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials JSON file to `data/youtube_credentials.json`

3. **Configure Instagram credentials:**
   ```bash
   # Set environment variables
   export INSTAGRAM_USERNAME="your_username"
   export INSTAGRAM_PASSWORD="your_password"

   # Or create a .env file
   echo "INSTAGRAM_USERNAME=your_username" >> .env
   echo "INSTAGRAM_PASSWORD=your_password" >> .env
   ```

4. **Create data directory:**
   ```bash
   mkdir -p data
   ```

## Usage

### Command Line Interface

```bash
python scripts/upload_video.py \
  --video-source path/to/video.mp4 \
  --title "Your Video Title" \
  --description "Your video description with #hashtags" \
  --tags "tag1,tag2,tag3" \
  --privacy public \
  --instagram-caption "Instagram caption #hashtags" \
  --platforms "youtube,instagram"
```

### Full Example

```bash
python scripts/upload_video.py \
  --video-source /path/to/my_short_video.mp4 \
  --title "Amazing Short Video!" \
  --description "Check out this amazing content! #Shorts #Amazing #Content" \
  --tags "shorts,amazing,content,viral" \
  --privacy public \
  --instagram-caption "Amazing content! 🔥 #Reels #Amazing #Content #Viral" \
  --schedule-time "2024-12-01T10:00:00Z" \
  --platforms "youtube,instagram"
```

### Python API Usage

```python
import asyncio
from scripts.upload_video import VideoUploader

async def upload_example():
    uploader = VideoUploader()

    results = await uploader.upload_video(
        video_source="path/to/video.mp4",
        title="Test Video",
        description="Test description #Shorts",
        tags=["test", "shorts", "video"],
        privacy="public",
        instagram_caption="Test on Instagram! #Reels",
        platforms=["youtube", "instagram"]
    )

    for result in results:
        if result.success:
            print(f"✓ {result.platform}: {result.video_url}")
        else:
            print(f"✗ {result.platform}: {result.error_message}")

# Run the upload
asyncio.run(upload_example())
```

## Configuration

### Environment Variables

```bash
# YouTube API
YOUTUBE_CREDENTIALS_PATH=data/youtube_credentials.json
YOUTUBE_TOKEN_PATH=data/youtube_token.json
YOUTUBE_CATEGORY_ID=22
YOUTUBE_DEFAULT_PRIVACY=public

# Instagram
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
INSTAGRAM_SESSION_PATH=data/instagram_session.json

# Video Settings
MAX_FILE_SIZE=524288000  # 500MB
MAX_DURATION_YOUTUBE=60
MAX_DURATION_INSTAGRAM=90

# Upload Settings
UPLOAD_TIMEOUT=300
MAX_RETRIES=3

# Logging
LOG_LEVEL=INFO
LOG_FILE=uploads.log
```

### Configuration File

Create `data/config.json`:

```json
{
  "youtube": {
    "credentials_path": "data/youtube_credentials.json",
    "token_path": "data/youtube_token.json",
    "category_id": "22",
    "default_privacy": "public",
    "default_tags": ["Shorts", "YourBrand"],
    "max_retries": 3
  },
  "instagram": {
    "username": "your_username",
    "password": "your_password",
    "session_path": "data/instagram_session.json",
    "max_retries": 3,
    "default_hashtags": ["#Reels", "#YourBrand"]
  },
  "video": {
    "max_file_size": 524288000,
    "max_duration_youtube": 60,
    "max_duration_instagram": 90,
    "preferred_aspect_ratio": 0.5625
  }
}
```

## Video Requirements

### YouTube Shorts
- **Duration**: ≤ 60 seconds
- **Aspect Ratio**: Vertical (9:16) or Square (1:1)
- **Resolution**: 720x1280 to 1080x1920
- **Format**: MP4, MOV, AVI
- **File Size**: ≤ 500MB

### Instagram Reels
- **Duration**: ≤ 90 seconds
- **Aspect Ratio**: Vertical (9:16) or Square (1:1)
- **Resolution**: 720x1280 to 1080x1920
- **Format**: MP4, MOV, AVI
- **File Size**: ≤ 500MB

## Error Handling

The uploader includes comprehensive error handling:

- **Network Issues**: Automatic retry with exponential backoff
- **API Rate Limits**: Respectful backoff and retry strategies
- **Authentication**: Automatic token refresh and re-authentication
- **Video Validation**: Pre-upload validation with detailed error messages
- **Partial Failures**: Graceful handling when one platform fails
- **Resource Cleanup**: Automatic cleanup of temporary files

## Logging

Structured logging with multiple levels:

```bash
# View logs in real-time
tail -f uploads.log

# JSON formatted output for programmatic processing
python scripts/upload_video.py --video-source video.mp4 --title "Test" --description "Test" 2>&1 | jq .
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
python -m pytest test/ -v

# Run specific test file
python -m pytest test/test_video_validator.py -v

# Run with coverage
python -m pytest test/ --cov=scripts --cov-report=html
```

## Security Considerations

- **Credential Storage**: Uses secure credential storage with environment variables
- **Token Management**: Automatic OAuth2 token refresh and secure storage
- **Input Validation**: All inputs are validated and sanitized
- **No Hardcoded Secrets**: All sensitive data loaded from secure sources
- **Session Management**: Secure Instagram session handling with automatic cleanup

## Troubleshooting

### Common Issues

1. **YouTube Authentication Error**
   ```bash
   # Re-download credentials from Google Cloud Console
   # Ensure OAuth2 consent screen is configured
   # Check that YouTube Data API v3 is enabled
   ```

2. **Instagram Login Failed**
   ```bash
   # Check username/password
   # Handle 2FA if enabled (manual setup required)
   # Clear session file if corrupted: rm data/instagram_session.json
   ```

3. **Video Validation Failed**
   ```bash
   # Check video format, duration, and resolution
   # Install ffprobe for detailed validation: brew install ffmpeg
   ```

4. **Upload Timeout**
   ```bash
   # Increase timeout in config
   # Check network connection
   # Reduce video file size
   ```

### Debug Mode

Enable verbose logging:

```bash
export LOG_LEVEL=DEBUG
python scripts/upload_video.py --video-source video.mp4 --title "Test" --description "Test"
```

## Platform-Specific Features

### YouTube Shorts
- Automatic #Shorts hashtag addition
- Custom thumbnail support
- Monetization settings
- Scheduled publishing
- Category assignment

### Instagram Reels
- Cover frame extraction
- Story sharing option
- Music/audio handling
- Cross-posting to Facebook

## Performance Optimization

- **Concurrent Uploads**: Uploads to both platforms simultaneously
- **Chunked Uploads**: Large files uploaded in chunks with resume capability
- **Memory Efficient**: Handles video data in memory without unnecessary copying
- **Connection Pooling**: Reuses HTTP connections for better performance

## License

This project is provided as-is for educational and personal use. Please ensure you comply with YouTube and Instagram's Terms of Service and API usage policies.

## Support

For issues and feature requests, please check the troubleshooting section above or review the code documentation.