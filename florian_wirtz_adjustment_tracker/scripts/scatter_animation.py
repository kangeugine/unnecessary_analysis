import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import LineCollection
import random

def generate_random_data(n_points=50):
    """Generate random x, y data with timestamps"""
    # Generate random timestamps (sorted)
    timestamps = sorted([random.uniform(0, 10) for _ in range(n_points)])

    # Generate random x, y coordinates
    x_data = [random.uniform(-10, 10) for _ in range(n_points)]
    y_data = [random.uniform(-10, 10) for _ in range(n_points)]

    return timestamps, x_data, y_data

def create_scatter_animation():
    """Create scatter plot animation with smooth pointer movement"""
    # Generate data
    timestamps, x_data, y_data = generate_random_data()

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(-12, 12)
    ax.set_ylim(-12, 12)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Animated Scatter Plot with Smooth Pointer Movement')
    ax.grid(True, alpha=0.3)

    # Initialize plots
    scatter = ax.scatter([], [], c=[], s=50, cmap='viridis', alpha=0.7)
    line, = ax.plot([], [], 'b-', alpha=0.5, linewidth=2)
    pointer, = ax.plot([], [], 'ro', markersize=12, markeredgecolor='white', markeredgewidth=2)

    # Store data for animation
    x_points = []
    y_points = []
    colors = []

    # Animation parameters
    frames_per_segment = 3  # Number of frames to move between points (reduced from 20 for 8x speed)
    total_segments = len(timestamps) - 1 if len(timestamps) > 1 else 0

    def interpolate_position(start_pos, end_pos, t):
        """Interpolate between two positions"""
        return start_pos + t * (end_pos - start_pos)

    def animate(frame):
        """Animation function called for each frame"""
        if total_segments == 0:
            return scatter, line, pointer

        total_frames = total_segments * frames_per_segment

        if frame < total_frames:
            # Calculate which segment we're in and progress within that segment
            segment_index = frame // frames_per_segment
            segment_progress = (frame % frames_per_segment) / frames_per_segment

            # Ensure we don't go beyond available data
            segment_index = min(segment_index, len(timestamps) - 2)

            # Add points up to current segment
            target_points = segment_index + 1
            while len(x_points) < target_points:
                idx = len(x_points)
                x_points.append(x_data[idx])
                y_points.append(y_data[idx])
                colors.append(timestamps[idx])

            # Update scatter plot with visited points
            if x_points:
                scatter.set_offsets(np.column_stack([x_points, y_points]))
                scatter.set_array(np.array(colors))

                # Update line connecting visited points
                line.set_data(x_points, y_points)

            # Calculate current pointer position with smooth interpolation
            start_x = x_data[segment_index]
            start_y = y_data[segment_index]
            end_x = x_data[segment_index + 1]
            end_y = y_data[segment_index + 1]

            current_x = interpolate_position(start_x, end_x, segment_progress)
            current_y = interpolate_position(start_y, end_y, segment_progress)

            # Update pointer position
            pointer.set_data([current_x], [current_y])

            # Update title with current position and progress
            current_time = interpolate_position(timestamps[segment_index],
                                             timestamps[segment_index + 1],
                                             segment_progress)
            ax.set_title(f'Smooth Pointer Animation - Time: {current_time:.2f} - Segment: {segment_index + 1}/{total_segments}')

        elif frame < total_frames + 30:  # Pause at end
            # Show final state with all points
            if len(x_points) < len(timestamps):
                x_points.extend(x_data[len(x_points):])
                y_points.extend(y_data[len(y_points):])
                colors.extend(timestamps[len(colors):])

                scatter.set_offsets(np.column_stack([x_points, y_points]))
                scatter.set_array(np.array(colors))
                line.set_data(x_points, y_points)

            # Keep pointer at final position
            if x_data:
                pointer.set_data([x_data[-1]], [y_data[-1]])
            ax.set_title(f'Animation Complete - Final Time: {timestamps[-1]:.2f}')

        return scatter, line, pointer

    # Create animation with more frames for smooth motion
    total_frames = total_segments * frames_per_segment + 30  # +30 for pause at end
    anim = animation.FuncAnimation(
        fig, animate, frames=total_frames,
        interval=50, blit=False, repeat=True  # Faster interval for smoother motion
    )

    return fig, anim

def save_animation_video(anim, filename='scatter_animation.mp4'):
    """Save animation as video file"""
    print(f"Saving animation to {filename}...")

    # Set up writer
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=5, metadata=dict(artist='Python'), bitrate=1800)

    # Save animation
    anim.save(filename, writer=writer)
    print(f"Animation saved as {filename}")

if __name__ == "__main__":
    print("Creating scatter plot animation...")

    # Create animation
    fig, anim = create_scatter_animation()

    # Save as video
    save_animation_video(anim)

    # Show animation (optional - comment out if running headless)
    plt.show()