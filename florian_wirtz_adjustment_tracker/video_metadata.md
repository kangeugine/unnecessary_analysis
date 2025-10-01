## YouTube Short Metadata Generator

### Task Description

This task creates a JSON file with metadata for a YouTube short based on football performance data analysis.

### Input Files Required

1. **Data file**: `data/wirtz_performance_data.csv` - Contains performance metrics (CII, GTI) for different opponents and seasons
2. **Analysis script**: `scripts/match_stats.py` - Contains the logic for calculating Creative Influence Index (CII) and Goal Threat Index (GTI)

### Output

Creates `data/video_metadata.json` with the following structure:

```json
{
  "title": "YouTube short title with engaging question/hook",
  "description": "Detailed description explaining the analysis and metrics used",
  "hashtag": "Relevant hashtags for football, data analysis, and player performance",
  "subtitle": ["Array of subtitle text that guides viewers through the data story"]
}
```

### Task Instructions

Based on the performance data and analysis script, create a JSON file that includes:

- **title**: Engaging YouTube short title asking about the player's performance
- **description**: Explanation of the data visualization and what metrics are being tracked
- **hashtag**: Relevant hashtags for football analytics, player analysis, and social media
- **subtitle**: Sequential subtitles that tell the data story, explaining metrics and highlighting key performance points

### Repeat Command

To repeat this task, simply ask:
"Based on the data in @florian_wirtz_adjustment_tracker/data/wirtz_performance_data.csv and @florian_wirtz_adjustment_tracker/scripts/match_stats.py create a json file under @florian_wirtz_adjustment_tracker/data with the following values: title, description, hashtag, subtitle"