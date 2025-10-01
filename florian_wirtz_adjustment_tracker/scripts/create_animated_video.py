"""
Florian Wirtz Performance Animation
Creates mobile-optimized animated video for social media platforms
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import numpy as np
import os

class WirtzAnimationCreator:
    def __init__(self, data_path, output_dir):
        self.data_path = data_path
        self.output_dir = output_dir
        self.df = None
        self.fig = None
        self.ax = None

        # Square format settings
        self.mobile_width = 1080
        self.mobile_height = 1080

        # Animation timing (in seconds) - shortened version
        self.intro_duration = 0  # Skip introduction
        self.baseline_duration = 9  # Reduced from 10 seconds
        self.match_duration = 1  # 1 second per match
        self.finale_duration = 3

    def load_and_prepare_data(self):
        """Load and organize the performance data"""
        self.df = pd.read_csv(self.data_path)

        # Separate baseline and match data
        self.baseline_data = self.df[self.df['opponent'].isin(['2023-2024', '2024-2025'])].copy()
        self.match_data = self.df[~self.df['opponent'].isin(['2023-2024', '2024-2025'])].copy()

        # Sort baseline data chronologically
        self.baseline_data = self.baseline_data.sort_values('opponent')

        print(f"Baseline data: {len(self.baseline_data)} seasons")
        print("Baseline data:")
        print(self.baseline_data)
        print(f"Match data: {len(self.match_data)} matches")
        print("Match data:")
        print(self.match_data)

    def setup_mobile_plot(self):
        """Setup the plot with square dimensions and styling"""
        plt.style.use('dark_background')

        # Calculate dimensions for square layout
        figsize_width = 10.8  # Scale down from 1080px
        figsize_height = 10.8  # Scale down from 1080px (square format)

        self.fig, self.ax = plt.subplots(figsize=(figsize_width, figsize_height))
        self.fig.patch.set_facecolor('#0E1117')
        self.ax.set_facecolor('#0E1117')

        # Adjust layout
        plt.subplots_adjust(top=0.95, bottom=0.1)

        # Set axis limits with y-axis being 130% of x-axis range
        all_data = pd.concat([self.baseline_data, self.match_data])
        x_min, x_max = all_data['CII'].min() * 0.9, all_data['CII'].max() * 1.1
        x_range = x_max - x_min

        # Calculate y-axis range to be 130% of x-axis range
        y_center = (all_data['GTI'].min() + all_data['GTI'].max()) / 2
        y_range = x_range * 1.3
        y_min = y_center - y_range / 2
        y_max = y_center + y_range / 2

        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)

        print(f"Plot setup - X limits: ({x_min:.3f}, {x_max:.3f}), Y limits: ({y_min:.3f}, {y_max:.3f})")
        print(f"X range: {x_range:.3f}, Y range: {y_range:.3f} (130% of X)")

        # Mobile-optimized styling
        self.ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#404040')
        self.ax.set_axisbelow(True)

        # Clean axis styling
        self.ax.spines['bottom'].set_color('#404040')
        self.ax.spines['left'].set_color('#404040')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.tick_params(colors='#CCCCCC', which='both', labelsize=16)

        # Large, mobile-friendly labels
        self.ax.set_xlabel('Creative Impact Index (CII)',
                          fontsize=20, fontweight='bold', color='#FFFFFF', labelpad=20)
        self.ax.set_ylabel('Goal Threat Index (GTI)',
                          fontsize=20, fontweight='bold', color='#FFFFFF', labelpad=20)

    def create_text_overlay(self, text, y_position=0.05, fontsize=24):
        """Create text overlay below the x-axis"""
        return self.fig.text(0.5, y_position, text,
                           fontsize=fontsize, fontweight='bold',
                           color='#FFFFFF', ha='center', va='center',
                           bbox=dict(boxstyle='round,pad=0.8',
                                   facecolor='#1a1a1a', alpha=0.8))

    def animate_frame(self, frame):
        """Animation function for each frame"""
        self.ax.clear()

        # Re-setup basic plot styling (without full setup)
        self.ax.set_facecolor('#0E1117')

        # Set axis limits with y-axis being 130% of x-axis range
        all_data = pd.concat([self.baseline_data, self.match_data])
        x_min, x_max = all_data['CII'].min() * 0.9, all_data['CII'].max() * 1.1
        x_range = x_max - x_min

        # Calculate y-axis range to be 130% of x-axis range
        y_center = (all_data['GTI'].min() + all_data['GTI'].max()) / 2
        y_range = x_range * 1.3
        y_min = y_center - y_range / 2
        y_max = y_center + y_range / 2

        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)

        # Style the axes
        self.ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#404040')
        self.ax.set_axisbelow(True)
        self.ax.spines['bottom'].set_color('#404040')
        self.ax.spines['left'].set_color('#404040')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.tick_params(colors='#CCCCCC', which='both', labelsize=16)

        # Labels
        self.ax.set_xlabel('Creative Impact Index (CII)',
                          fontsize=20, fontweight='bold', color='#FFFFFF', labelpad=20)
        self.ax.set_ylabel('Goal Threat Index (GTI)',
                          fontsize=20, fontweight='bold', color='#FFFFFF', labelpad=20)

        # Remove existing text overlays
        for text in self.fig.texts:
            text.remove()

        total_frames = (self.intro_duration + self.baseline_duration +
                       len(self.match_data) * self.match_duration + self.finale_duration) * 30

        current_time = frame / 30  # Convert frame to seconds (30 fps)

        # Debug print
        if frame % 60 == 0:  # Print every 2 seconds
            print(f"Frame {frame}, Time: {current_time:.1f}s")

        # Since intro_duration = 0, start directly with baseline section
        # Section 1: Baseline Data (0-9 seconds)
        if current_time <= self.baseline_duration:
            section_time = current_time
            progress = section_time / self.baseline_duration

            if frame % 60 == 0:
                print(f"  Section 1: Baseline, progress={progress:.2f}")

            # Show baseline points with bounce effect
            if progress > 0.1:  # Start earlier since we have less time
                colors = ['#00FF7F', '#32CD32']  # Bright greens for Leverkusen

                for i, (_, row) in enumerate(self.baseline_data.iterrows()):
                    if progress > 0.1 + i * 0.2:  # Faster appearance
                        # Bounce effect
                        bounce_scale = 1 + 0.3 * np.sin((progress - 0.1 - i * 0.2) * 25)
                        size = 200 * bounce_scale if progress < 0.4 + i * 0.2 else 200

                        self.ax.scatter(row['CII'], row['GTI'],
                                      c=colors[i], s=size, alpha=0.9,
                                      edgecolors='white', linewidth=2, zorder=3)

                        # Add labels
                        self.ax.annotate(row['opponent'],
                                       (row['CII'], row['GTI']),
                                       xytext=(10, 10), textcoords='offset points',
                                       fontsize=16, fontweight='bold', color='white',
                                       bbox=dict(boxstyle='round,pad=0.3',
                                               facecolor='black', alpha=0.7))

                        if frame % 60 == 0:
                            print(f"    Showing baseline point {i}: {row['opponent']} at ({row['CII']:.2f}, {row['GTI']:.2f})")

                # Connect baseline points
                if progress > 0.6:  # Earlier connection
                    baseline_x = self.baseline_data['CII'].values
                    baseline_y = self.baseline_data['GTI'].values
                    self.ax.plot(baseline_x, baseline_y, 'g--', linewidth=2, alpha=0.7)

        # Section 2: Liverpool Performance (9+ seconds)
        else:
            # Show baseline points (always visible)
            colors = ['#00FF7F', '#32CD32']
            for i, (_, row) in enumerate(self.baseline_data.iterrows()):
                self.ax.scatter(row['CII'], row['GTI'],
                              c=colors[i], s=200, alpha=0.9,
                              edgecolors='white', linewidth=2, zorder=3)
                self.ax.annotate(row['opponent'],
                               (row['CII'], row['GTI']),
                               xytext=(10, 10), textcoords='offset points',
                               fontsize=16, fontweight='bold', color='white',
                               bbox=dict(boxstyle='round,pad=0.3',
                                       facecolor='black', alpha=0.7))

            # Connect baseline points
            baseline_x = self.baseline_data['CII'].values
            baseline_y = self.baseline_data['GTI'].values
            self.ax.plot(baseline_x, baseline_y, 'g--', linewidth=2, alpha=0.7)

            # Liverpool matches
            match_start_time = self.baseline_duration  # Starts at 9 seconds
            match_time = current_time - match_start_time
            matches_to_show = int(match_time / self.match_duration)

            if matches_to_show > 0:
                # Show Liverpool matches progressively
                liverpool_colors = plt.cm.Reds(np.linspace(0.5, 1, len(self.match_data)))

                match_x = []
                match_y = []

                for i in range(min(matches_to_show, len(self.match_data))):
                    row = self.match_data.iloc[i]

                    # Special effect for the current match being added
                    if i == matches_to_show - 1:
                        pulse_time = (match_time % self.match_duration) / self.match_duration
                        pulse_scale = 1 + 0.5 * np.sin(pulse_time * 10)
                        size = 250 * pulse_scale
                    else:
                        size = 200

                    self.ax.scatter(row['CII'], row['GTI'],
                                  c=[liverpool_colors[i]], s=size, alpha=0.9,
                                  edgecolors='white', linewidth=2, zorder=3)

                    self.ax.annotate(row['opponent'],
                                   (row['CII'], row['GTI']),
                                   xytext=(10, 10), textcoords='offset points',
                                   fontsize=16, fontweight='bold', color='white',
                                   bbox=dict(boxstyle='round,pad=0.3',
                                           facecolor='darkred', alpha=0.7))

                    match_x.append(row['CII'])
                    match_y.append(row['GTI'])

                # Connect Liverpool matches with trajectory line
                if len(match_x) > 1:
                    self.ax.plot(match_x, match_y, 'r-', linewidth=3, alpha=0.8)

            # Section 4: Finale (highlight final match)
            finale_start = (match_start_time + len(self.match_data) * self.match_duration)
            if current_time > finale_start:
                finale_time = current_time - finale_start
                if finale_time <= self.finale_duration:
                    # Pulse the final point
                    final_match = self.match_data.iloc[-1]
                    pulse = 1 + 0.3 * np.sin(finale_time * 8)

                    # Add glow effect
                    self.ax.scatter(final_match['CII'], final_match['GTI'],
                                  c='red', s=400 * pulse, alpha=0.3, zorder=1)
                    self.ax.scatter(final_match['CII'], final_match['GTI'],
                                  c='red', s=250 * pulse, alpha=0.9,
                                  edgecolors='white', linewidth=3, zorder=4)

    def create_animation(self):
        """Create the full animation"""
        self.load_and_prepare_data()

        # Setup the plot first
        self.setup_mobile_plot()

        # Calculate total duration and frames
        total_duration = (self.intro_duration + self.baseline_duration +
                         len(self.match_data) * self.match_duration + self.finale_duration)
        total_frames = int(total_duration * 30)  # 30 fps

        print(f"Creating animation with {total_frames} frames ({total_duration} seconds)")

        # Create animation
        anim = animation.FuncAnimation(self.fig, self.animate_frame,
                                     frames=total_frames, interval=33, repeat=False)

        # Save as high-quality video
        output_path = os.path.join(self.output_dir, 'wirtz_performance_animation.mp4')

        # Use high-quality settings for social media
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=30, metadata=dict(artist='Football Analytics'), bitrate=8000)

        anim.save(output_path, writer=writer, dpi=100)

        print(f"Animation saved to: {output_path}")
        plt.close()

        return output_path

def main():
    """Main execution function"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'wirtz_performance_data.csv')
    output_dir = os.path.join(script_dir, '..', 'video')

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create the animation
    creator = WirtzAnimationCreator(data_path, output_dir)
    video_path = creator.create_animation()

    print(f"\nVideo created successfully!")
    print(f"Output: {video_path}")
    print(f"Format: 1:1 (square format)")
    print(f"Ready for Instagram posts and other square video platforms")

if __name__ == "__main__":
    main()