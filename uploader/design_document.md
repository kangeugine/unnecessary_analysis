# Prompt for YouTube Shorts & Instagram Reels Python Uploader

## Context & Requirements
Create a production-ready Python 3.12 script that programmatically uploads videos to both YouTube (as Shorts) and Instagram (as Reels). The script must handle videos generated in memory or temporary locations, not direct file paths.

## Technical Specifications

### Core Functionality
- **Video Source**: Handle MP4 files from programmatic generation (memory/temp locations, not static file paths)
- **Dual Platform Upload**: Simultaneously upload to YouTube Shorts and Instagram Reels
- **API-Based Authentication**: Use official APIs with tokens/keys (no browser automation)
- **Full Metadata Control**: Accept all video metadata as script arguments

### Authentication Requirements
- **YouTube**: Use YouTube Data API v3 with OAuth2 or Service Account credentials
- **Instagram**: Use Instagram Graph API or reliable third-party library (instagrapi recommended)
- **Credential Management**: Secure handling of API keys, tokens, and refresh mechanisms

### Metadata Parameters (Command Line Arguments)
```bash
python upload_video.py \
  --video-source [memory_object|temp_file_path] \
  --title "Video Title" \
  --description "Video description with hashtags" \
  --tags "tag1,tag2,tag3" \
  --privacy [public|unlisted|private] \
  --instagram-caption "Instagram caption #hashtags" \
  --schedule-time "2024-12-01T10:00:00Z" \  # Optional
  --platforms "youtube,instagram"  # Or individual platform
```

### Production-Grade Requirements

#### Error Handling & Resilience
- **Retry Logic**: Exponential backoff for API rate limits and temporary failures
- **Comprehensive Error Handling**: Network issues, authentication failures, file format problems
- **Graceful Degradation**: Continue with one platform if the other fails
- **Validation**: Pre-upload video format, duration, and size validation

#### Logging & Monitoring
- **Structured Logging**: JSON format with timestamps, levels, and context
- **Progress Tracking**: Upload progress indicators and status updates
- **Error Reporting**: Detailed error messages with suggested fixes
- **Success Confirmation**: Return upload URLs, video IDs, and status confirmation

#### Performance Optimization
- **Async Operations**: Concurrent uploads to both platforms when possible
- **Memory Management**: Efficient handling of video data in memory
- **Chunked Uploads**: Support for large file uploads with resume capability
- **Cleanup**: Automatic cleanup of temporary files and resources

### Video Processing Considerations
- **Format Validation**: Ensure MP4 compatibility for both platforms
- **Duration Limits**: Respect YouTube Shorts (60s) and Instagram Reels (90s) limits
- **Aspect Ratio**: Handle vertical (9:16) video optimization
- **Quality Settings**: Maintain optimal video quality during processing

### Platform-Specific Features

#### YouTube Shorts
- **Shorts Optimization**: Ensure video is recognized as a Short (vertical, <60s)
- **Thumbnail Management**: Custom thumbnail upload capability
- **Category Assignment**: Proper video categorization
- **Monetization Settings**: Handle monetization preferences

#### Instagram Reels
- **Cover Image**: Extract or specify custom cover frame
- **Music/Audio**: Handle audio tracks and music attribution
- **Story Sharing**: Option to share Reel to Story automatically
- **Cross-posting**: Option to share to Facebook simultaneously

### Security & Best Practices
- **Credential Security**: Store API keys securely (environment variables, keyring)
- **Rate Limit Compliance**: Respect API quotas and implement backoff strategies
- **Data Privacy**: Handle video content securely, avoid unnecessary storage
- **Input Sanitization**: Validate and sanitize all user inputs

### Dependencies & Environment
```python
# Required packages
google-api-python-client==2.110.0
google-auth==2.23.4
google-auth-oauthlib==1.1.0
instagrapi==2.0.0
tenacity==8.2.3
loguru==0.7.2
requests==2.31.0
python-dotenv==1.0.0
```

### Expected Output Structure
```python
class UploadResult:
    platform: str
    success: bool
    video_id: Optional[str]
    video_url: Optional[str]
    error_message: Optional[str]
    upload_duration: float
    
def upload_video(
    video_source: Union[bytes, str, Path],
    title: str,
    description: str,
    **metadata_kwargs
) -> List[UploadResult]:
    # Implementation here
    pass
```

### Configuration Management
- **Environment Variables**: API keys, default settings
- **Config File Support**: JSON/YAML configuration for default metadata
- **CLI Override**: Command line arguments override config file settings

## Success Criteria
1. **Reliability**: 99%+ success rate under normal conditions
2. **Performance**: Handle videos up to 500MB efficiently
3. **Usability**: Clear documentation and error messages
4. **Maintainability**: Clean, well-documented code structure
5. **Security**: No credential leaks or security vulnerabilities

Create a complete, production-ready solution that handles all edge cases and provides excellent developer experience.