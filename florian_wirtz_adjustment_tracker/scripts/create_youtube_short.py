#!/usr/bin/env python3
"""
Create a YouTube Short (9:16 ratio) with title, video, and subtitles using MoviePy.
Modularized script with separate functions for each component.
"""

from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
import os
import json

TITLE_FONT_SIZE = 60
SUBTITLE_FONT_SIZE = 40

def load_source_video(video_path):
    """Load and return the source video clip."""
    return VideoFileClip(video_path)


def load_video_metadata(metadata_path):
    """Load video metadata from JSON file."""
    with open(metadata_path, 'r') as f:
        return json.load(f)


def create_background(width, height, duration, color=(0, 0, 0)):
    """Create a solid color background clip."""
    return ColorClip(size=(width, height), color=color, duration=duration)


def calculate_video_dimensions(source_video, final_width, final_height):
    """Calculate the optimal dimensions and position for the source video."""
    source_width, source_height = source_video.size
    source_aspect_ratio = source_width / source_height

    # Reserve space for title (5% spacing + text) and subtitles (5% spacing + text)
    # Allocate roughly 15% for title area and 15% for subtitle area
    available_height = final_height * 0.7  # 70% of total height for video
    available_width = final_width * 0.9    # 90% of width with some padding

    # Scale video to fit available space
    if source_aspect_ratio > (available_width / available_height):
        # Video is wider, fit to width
        video_width = int(available_width)
        video_height = int(available_width / source_aspect_ratio)
    else:
        # Video is taller, fit to height
        video_height = int(available_height)
        video_width = int(available_height * source_aspect_ratio)

    # Calculate position (center of middle section)
    # Start at 15% down (title area) and center within the available space
    video_y_position = (final_height * 0.15) + (available_height - video_height) // 2
    video_x_position = (final_width - video_width) // 2

    return video_width, video_height, video_x_position, video_y_position


def resize_and_position_video(source_video, width, height, x_pos, y_pos):
    """Resize the source video and position it."""
    resized_video = source_video.resized((width, height))
    return resized_video.with_position((x_pos, y_pos))


def create_title_text(text, duration, final_height, video_y_pos):
    """Create the title text clip positioned 5% above the video."""
    title_text = TextClip(text=text, font_size=TITLE_FONT_SIZE, color='white')

    # Get the actual text dimensions to properly position it
    text_width, text_height = title_text.size

    # Position 5% above the video, accounting for the full text height
    spacing = final_height * 0.05
    title_y_pos = video_y_pos - spacing - text_height

    return title_text.with_position(('center', title_y_pos)).with_duration(duration)


def create_subtitle_clips(subtitles, total_duration, final_width, final_height, video_y_pos, video_height):
    """Create multiple subtitle text clips timed throughout the video."""
    subtitle_clips = []

    if not subtitles:
        return subtitle_clips

    # Calculate timing for each subtitle
    subtitle_duration = total_duration / len(subtitles)

    for i, subtitle_text in enumerate(subtitles):
        start_time = i * subtitle_duration

        subtitle_clip = TextClip(
            text=subtitle_text,
            font_size=SUBTITLE_FONT_SIZE,
            color='white'
        )

        # Get actual text dimensions for proper positioning
        text_width, text_height = subtitle_clip.size

        # Position 5% below the video, ensuring full text height is visible
        spacing = final_height * 0.05
        subtitle_y_pos = video_y_pos + video_height + spacing - text_height

        positioned_subtitle = subtitle_clip.with_position(('center', subtitle_y_pos)).with_duration(subtitle_duration).with_start(start_time)
        subtitle_clips.append(positioned_subtitle)

    return subtitle_clips


def compose_final_video(background, positioned_video, title_text, subtitle_clips):
    """Compose all elements into the final video."""
    # Set layer attribute to ensure text appears on top
    background.layer = 0  # Bottom layer
    positioned_video.layer = 1  # Middle layer
    title_text.layer = 2  # Higher layer for title

    # Set subtitle clips to highest layer
    for clip in subtitle_clips:
        clip.layer = 3

    all_clips = [background, positioned_video, title_text] + subtitle_clips
    return CompositeVideoClip(all_clips)


def export_video(final_video, output_path):
    """Export the final video to file."""
    final_video.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )


def cleanup_resources(*clips):
    """Close all video clips to free up resources."""
    for clip in clips:
        if clip:
            clip.close()


def create_youtube_short():
    """Main function to orchestrate the creation of the YouTube Short."""
    # Configuration
    input_video_path = "video/wirtz_performance_animation.mp4"
    metadata_path = "data/video_metadata.json"
    output_video_path = "video/wirtz_performance_youtube_short.mp4"
    final_width = 1080
    final_height = 1920

    # Load video metadata
    metadata = load_video_metadata(metadata_path)

    # Load source video
    source_video = load_source_video(input_video_path)

    # Create background
    background = create_background(final_width, final_height, source_video.duration)

    # Calculate video dimensions and position
    video_width, video_height, video_x_pos, video_y_pos = calculate_video_dimensions(
        source_video, final_width, final_height
    )

    # Resize and position the video
    positioned_video = resize_and_position_video(
        source_video, video_width, video_height, video_x_pos, video_y_pos
    )

    # Create text elements using metadata
    title_text = create_title_text(metadata["title"], source_video.duration, final_height, video_y_pos)
    subtitle_clips = create_subtitle_clips(
        metadata["subtitle"],
        source_video.duration,
        final_width,
        final_height,
        video_y_pos,
        video_height
    )

    # Compose final video
    final_video = compose_final_video(background, positioned_video, title_text, subtitle_clips)

    # Export the video
    export_video(final_video, output_video_path)

    # Clean up resources
    cleanup_resources(source_video, final_video)

    print(f"YouTube Short created successfully: {output_video_path}")
    print(f"Dimensions: {final_width}x{final_height} (9:16 ratio)")
    print(f"Title: {metadata['title']}")
    print(f"Subtitles: {len(metadata['subtitle'])} segments")


if __name__ == "__main__":
    # Change to the florian_wirtz_adjustment_tracker directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    os.chdir(parent_dir)

    create_youtube_short()