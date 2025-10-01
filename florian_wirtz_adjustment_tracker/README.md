# Florian Wirtz Adjustment Tracker

This project analyzes Florian Wirtz's performance adaptation from Bayer Leverkusen to Liverpool using advanced football statistics.

## Project Structure

```
florian_wirtz_adjustment_tracker/
├── data/           # Data files (CSV, JSON, Excel)
│   └── stats.xlsx  # Raw statistics data
├── images/         # Raw images
├── plots/          # Generated graphs and charts
│   ├── plot_week3.png
│   └── plot_week4.png
├── scripts/        # Python scripts
│   ├── match_stats.py       # Main data processing and static visualization
│   ├── animated_analysis.py # Animated video generation
│   └── scatter_animation.py # Legacy animation script
├── tests/          # Unit tests
├── video/          # Generated video outputs
│   └── scatter_animation.mp4
└── README.md       # This file
```

## Key Files

### Scripts
- **`match_stats.py`**: Main script for data processing and static plot generation
  - Modular functions for reading, transforming, joining, and cleaning data
  - Generates static scatter plot visualization

- **`animated_analysis.py`**: Creates animated video explanation
  - Uses matplotlib FuncAnimation
  - Explains Creative Impact Index (CII) and Goal Threat Index (GTI)
  - Shows match-by-match progression with baseline comparison

### Performance Metrics

**Creative Impact Index (CII)**: Measures creative involvement
- Shot-Creating Actions per 90
- Expected Assists per 90
- Progressive Passes per 90
- Passes into Penalty Area per 90

**Goal Threat Index (GTI)**: Measures goal-scoring threat
- Non-Penalty Expected Goals per 90
- Touches in Attacking Penalty Area per 90
- Successful Take-Ons per 90
- Take-On Attempts per 90

## Usage

### Generate Static Plot
```bash
cd scripts/
python match_stats.py
```

### Generate Animated Video
```bash
cd scripts/
python animated_analysis.py
```

## Requirements

```bash
uv pip install pandas matplotlib seaborn numpy pillow
```

For video generation:
```bash
uv pip install moviepy
```

## Data Source

All performance data is sourced from [FBref](https://fbref.com) - Florian Wirtz player statistics.

