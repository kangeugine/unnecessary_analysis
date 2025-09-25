"""
Pillar 1: Creative Influence & On-Ball Value

This is Wirtz's bread and butter. Is he still the creative hub of his new team?

Shot-Creating Actions (SCA) per 90: This is any offensive action (a pass, a dribble, drawing a foul) that leads to a shot. It's a brilliant measure of overall creative involvement. If his SCA is high, he's still making things happen, even if they don't result in an assist.

Expected Assists (xA) per 90: This measures the quality of the chances he creates. A pass with a 0.4 xA is one that a typical player would score from 40% of the time. This separates his passing quality from the finishing ability of his teammates. Is he still creating high-quality chances?

Passes into the Final Third & Passes into the Penalty Area per 90: These are measures of penetration. They show if he is successfully breaking down the opposition's defensive lines and moving the ball into dangerous areas.

Progressive Passes per 90: A pass that moves the ball significantly closer to the opponent's goal. This shows his intent to play forward and be aggressive, a key trait for a Liverpool midfielder.

xGChain (Expected Goal Chain) & xGBuildup: These are advanced metrics. xGChain measures the total xG of every possession he is involved in. xGBuildup is similar but excludes the key pass and the shot itself. A high xGBuildup shows he is vital in the early stages of attacking moves, even if he's not playing the final ball. This is perfect for tracking his developing chemistry within the team's possession structure.

Pillar 2: Individual Goal Threat

Even if he's not scoring, we need to know if he's still a threat himself.

Non-Penalty Expected Goals (npxG) per 90: This is the single best metric for goal-scoring process. It measures the quality of the shots he is taking. A high npxG with low actual goals suggests bad luck or poor finishing, but the key is that he's still getting into high-quality scoring positions.

Touches in the Attacking Penalty Area per 90: A simple but powerful metric. Is he making the runs to get into the box? This is a prerequisite for being a goal threat. A week-over-week increase here is a strong positive signal.

Successful Take-Ons / Dribbles Completed: Wirtz is known for his ability to glide past players. Is he still attempting and completing these dribbles? This shows his confidence and willingness to take risks in the final third.
"""

from functools import reduce
from typing import List, Tuple, Dict
import os

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import seaborn as sns


def read_data() -> Tuple[List[pd.DataFrame], List[pd.DataFrame]]:
    """Read scout report and match logs data from fbref URLs."""
    scout_report_url = "https://fbref.com/en/players/e7fcf289/dom_lg/Florian-Wirtz-Domestic-League-Stats#all_stats_gca"
    tables = pd.read_html(scout_report_url)

    match_logs_url = [
        "https://fbref.com/en/players/e7fcf289/matchlogs/2025-2026/Florian-Wirtz-Match-Logs",
        "https://fbref.com/en/players/e7fcf289/matchlogs/2025-2026/passing/Florian-Wirtz-Match-Logs",
        "https://fbref.com/en/players/e7fcf289/matchlogs/2025-2026/possession/Florian-Wirtz-Match-Logs",
    ]

    match_logs = []
    for url in match_logs_url:
        match_logs.extend(pd.read_html(url))

    return tables, match_logs


def get_column_mappings() -> Dict:
    """Define column mappings for data extraction."""
    return {
        'season_col': ('Unnamed: 0_level_0', 'Season'),
        'per90_col': ('Unnamed: 6_level_0', '90s'),
        'seasons': ["2023-2024", "2024-2025", "2025-2026"],
        # Pillar 1: Creative Influence & On-Ball Value
        'SCA': ('SCA', 'SCA'),  # Shot-Creating Actions (SCA) per 90
        'xA': ('Expected', 'xA'),  # Expected Assists (xA) per 90
        'passFin3': ('Unnamed: 26_level_0', '1/3'),  # Passes into the Final Third per 90
        'PPA': ('Unnamed: 27_level_0', 'PPA'),  # Passes into the Penalty Area per 90
        'PrgP': ('Unnamed: 29_level_0', 'PrgP'),  # Progressive Passes per 90
        # Pillar 2: Individual Goal Threat
        'npxG': ('Expected', 'npxG'),  # Non-Penalty Expected Goals (npxG) per 90
        'touchesAttPen': ('Touches', 'Att Pen'),  # Touches in the Attacking Penalty Area per 90
        'takeOnsAtt': ('Take-Ons', 'Att'),  # Take-Ons Attempt
        'takeOnsSucc': ('Take-Ons', 'Succ'),  # Successful Take-Ons
    }


def get_match_log_mappings() -> Dict:
    """Define column mappings for match log data."""
    return {
        'match_cols': [
            ('Unnamed: 0_level_0', 'Date'),
            ('Unnamed: 2_level_0', 'Comp'),
            ('Unnamed: 7_level_0', 'Opponent'),
            ('Unnamed: 10_level_0', 'Min'),
        ],
        'match_cols_name': ["date", "comp", "opponent", "min"],
        'metrics_summary': [
            ('Expected', 'npxG'),
            ('SCA', 'SCA'),
            ('Take-Ons', 'Att'),
            ('Take-Ons', 'Succ'),
        ],
        'metrics_summary_name': ["npxG", "SCA", "takeOnsAtt", "takeOnsSucc"],
        'metrics_passing': [
            ('Unnamed: 27_level_0', 'xA'),
            ('Unnamed: 29_level_0', '1/3'),
            ('Unnamed: 30_level_0', 'PPA'),
            ('Unnamed: 32_level_0', 'PrgP'),
        ],
        'metrics_passing_name': ["xA", "passFin3", "PPA", "PrgP"],
        'metrics_possession': [
            ('Touches', 'Att Pen'),
        ],
        'metrics_possession_name': ["touchesAttPen"]
    }


def find_table_by_columns(tables: List[pd.DataFrame], required_columns: List[tuple]) -> pd.DataFrame:
    """Find the table that contains all required columns."""
    for table in tables:
        try:
            # Check if all required columns exist in this table
            if all(col in table.columns for col in required_columns):
                return table
        except (AttributeError, TypeError):
            # Skip tables that don't have proper column structure
            continue

    # If no table found, raise an error with helpful message
    col_names = [str(col) for col in required_columns]
    raise ValueError(f"No table found containing all required columns: {col_names}")


def transform_season_data(tables: List[pd.DataFrame]) -> List[pd.DataFrame]:
    """Transform raw season tables into structured metrics dataframes."""
    cols = get_column_mappings()
    season_col = cols['season_col']
    per90_col = cols['per90_col']
    seasons = cols['seasons']

    # Goal and shot creation metrics
    gca_cols = [season_col, per90_col, cols['SCA']]
    gca = find_table_by_columns(tables, gca_cols)
    ix = gca[season_col].isin(seasons)
    gca_metric = gca[ix][gca_cols].reset_index(drop=True)
    gca_metric.columns = ["season", "m90s", "SCA"]

    # Passing metrics
    passing_cols = [season_col, per90_col, cols['xA'], cols['passFin3'], cols['PPA'], cols['PrgP']]
    passing = find_table_by_columns(tables, passing_cols)
    ix = passing[season_col].isin(seasons)
    passing_metric = passing[ix][passing_cols].reset_index(drop=True)
    passing_metric.columns = ["season", "m90s", "xA", "passFin3", "PPA", "PrgP"]

    # Shooting metrics
    shooting_cols = [season_col, per90_col, cols['npxG']]
    shooting = find_table_by_columns(tables, shooting_cols)
    ix = shooting[season_col].isin(seasons)
    shooting_metric = shooting[ix][shooting_cols]
    shooting_metric.columns = ["season", "m90s", "npxG"]

    # Possession metrics
    possession_cols = [season_col, per90_col, cols['touchesAttPen'], cols['takeOnsAtt'], cols['takeOnsSucc']]
    possession = find_table_by_columns(tables, possession_cols)
    ix = possession[season_col].isin(seasons)
    possession_metric = possession[ix][possession_cols].reset_index(drop=True)
    possession_metric.columns = ["season", "m90s", "touchesAttPen", "takeOnsAtt", "takeOnsSucc"]

    return [gca_metric, passing_metric, shooting_metric, possession_metric]


def clean_match_log_metrics(data: pd.DataFrame, metrics: List[tuple], metrics_cols_name: List[str], match_cols: List[tuple], match_cols_name: List[str]) -> pd.DataFrame:
    """Clean and structure match log metrics data."""
    _data = data[match_cols + metrics]
    _data = _data[_data.notna().all(axis=1)]
    _data.columns = match_cols_name + metrics_cols_name
    return _data


def transform_match_log_data(match_logs: List[pd.DataFrame]) -> List[pd.DataFrame]:
    """Transform raw match log data into structured metrics dataframes."""
    mappings = get_match_log_mappings()

    match_log_summary = clean_match_log_metrics(
        match_logs[0], mappings['metrics_summary'], mappings['metrics_summary_name'],
        mappings['match_cols'], mappings['match_cols_name']
    )
    match_log_passing = clean_match_log_metrics(
        match_logs[1], mappings['metrics_passing'], mappings['metrics_passing_name'],
        mappings['match_cols'], mappings['match_cols_name']
    )
    match_log_possession = clean_match_log_metrics(
        match_logs[2], mappings['metrics_possession'], mappings['metrics_possession_name'],
        mappings['match_cols'], mappings['match_cols_name']
    )

    return [match_log_summary, match_log_passing, match_log_possession]


def join_data(dataframes: List[pd.DataFrame]) -> pd.DataFrame:
    """Join multiple dataframes on common columns."""
    if 'season' in dataframes[0].columns:
        return reduce(lambda left, right: pd.merge(left, right, on=['season', 'm90s'], how='inner'), dataframes)
    else:
        mappings = get_match_log_mappings()
        match_cols_name = mappings['match_cols_name']
        return reduce(lambda left, right: pd.merge(left, right, on=match_cols_name, how='inner'), dataframes)


def apply_cii_metric(data: pd.DataFrame) -> pd.Series:
    """Calculate Creative Impact Index (CII) metric."""
    cii_metrics = ["SCA", "xA", "PPA", "PrgP"]
    return data[cii_metrics].sum(axis=1) / len(cii_metrics)


def apply_gti_metric(data: pd.DataFrame) -> pd.Series:
    """Calculate Goal Threat Index (GTI) metric."""
    gti_metrics = ['npxG', 'touchesAttPen', 'takeOnsAtt', 'takeOnsSucc']
    return data[gti_metrics].sum(axis=1) / len(gti_metrics)


def normalize_to_per90(data: pd.DataFrame, is_match_log: bool = False) -> pd.DataFrame:
    """Normalize metrics to per 90 minutes."""
    if is_match_log:
        mappings = get_match_log_mappings()
        match_cols_name = mappings['match_cols_name']
        cols_to_divide = data.columns.drop(match_cols_name)
        data_per90 = data.copy()
        data_per90[cols_to_divide] = data_per90[cols_to_divide].apply(pd.to_numeric, errors='coerce')
        data_per90[cols_to_divide] = data_per90[cols_to_divide].div(data_per90['min'] / 90, axis=0)
    else:
        cols_to_divide = data.columns.drop(['season'])
        data_per90 = data.copy()
        data_per90[cols_to_divide] = data_per90[cols_to_divide].apply(pd.to_numeric, errors='coerce')
        data_per90[cols_to_divide] = data_per90[cols_to_divide].div(data_per90['m90s'], axis=0)

    return data_per90


def organize_and_clean_data(season_data: pd.DataFrame, match_log_data: pd.DataFrame) -> pd.DataFrame:
    """Organize and clean all data, normalize metrics, and prepare final dataset for plotting."""
    mappings = get_match_log_mappings()
    match_cols_name = mappings['match_cols_name']

    # Normalize season data to per 90
    season_data_per90 = normalize_to_per90(season_data, is_match_log=False)
    cols_to_divide = season_data_per90.columns.drop(['season'])
    season_data_norm = season_data_per90[cols_to_divide] / season_data_per90[cols_to_divide].iloc[0]
    season_data_norm["CII"] = apply_cii_metric(season_data_norm)
    season_data_norm["GTI"] = apply_gti_metric(season_data_norm)

    # Normalize match log data to per 90
    match_log_per90 = normalize_to_per90(match_log_data, is_match_log=True)

    # Normalize match log data against baseline
    match_log_norm = match_log_per90.copy()
    baseline_metric = season_data_per90.iloc[0]
    cols_to_divide_ml = match_log_per90.columns.drop(match_cols_name)

    for col in cols_to_divide_ml:
        match_log_norm[col] = match_log_norm[col] / baseline_metric[col]

    match_log_norm["CII"] = apply_cii_metric(match_log_norm)
    match_log_norm["GTI"] = apply_gti_metric(match_log_norm)

    # Combine season and match data
    season_summary = season_data_norm[["CII", "GTI"]].head(2)
    season_summary['opponent'] = ['2023-2024', '2024-2025']

    df = pd.concat([match_log_norm[['opponent', 'CII', 'GTI']], season_summary], ignore_index=True)

    return df


def plot_performance_data(df: pd.DataFrame) -> None:
    """Create a visualization of Wirtz's performance data."""
    # Set the style for a modern look
    plt.style.use('dark_background')
    sns.set_palette("husl")

    # Create the figure with a square size
    fig, ax = plt.subplots(figsize=(12, 12))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    # Create a beautiful color gradient for the points
    colors = plt.cm.plasma(np.linspace(0, 1, len(df)))

    # Create the scatter plot with enhanced styling
    scatter = ax.scatter(df['CII'], df['GTI'],
                        c=colors,
                        s=120,
                        alpha=0.8,
                        edgecolors='white',
                        linewidth=1.5,
                        zorder=3)

    # Add a subtle glow effect around points
    ax.scatter(df['CII'], df['GTI'],
              c=colors,
              s=200,
              alpha=0.2,
              edgecolors='none',
              zorder=2)

    # Annotate points with better styling
    for i, row in df.iterrows():
        ax.annotate(row['opponent'],
                    (row['CII'], row['GTI']),
                    xytext=(9, 9),
                    textcoords='offset points',
                    fontsize=18,
                    fontweight='medium',
                    color='white',
                    alpha=0.9,
                    bbox=dict(boxstyle='round,pad=0.3',
                             facecolor='black',
                             alpha=0.7,
                             edgecolor='none'),
                    zorder=4)

    # Enhanced grid
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.5, color='#404040')
    ax.set_axisbelow(True)

    # Modern axis styling
    ax.spines['bottom'].set_color('#404040')
    ax.spines['left'].set_color('#404040')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#CCCCCC', which='both')

    # Beautiful labels with MORE SPACING
    ax.set_xlabel('Creative Impact Index (CII)',
                  fontsize=24,
                  fontweight='bold',
                  color='#FFFFFF',
                  labelpad=25)
    ax.set_ylabel('Goal Threat Index (GTI)',
                  fontsize=24,
                  fontweight='bold',
                  color='#FFFFFF',
                  labelpad=25)

    # Eye-catching title with subtitle and MORE SPACING
    fig.suptitle('How far is Wirtz from his Leverkusen level?',
                 fontsize=30,
                 fontweight='bold',
                 color='#FFFFFF',
                 y=0.97)
    ax.text(0.5, 1.05,
            'Performance by Opponent',
            transform=ax.transAxes,
            fontsize=16,
            alpha=0.8,
            color='#CCCCCC',
            ha='center')

    # Add a subtle border around the plot area
    border = Rectangle((ax.get_xlim()[0], ax.get_ylim()[0]),
                      ax.get_xlim()[1] - ax.get_xlim()[0],
                      ax.get_ylim()[1] - ax.get_ylim()[0],
                      linewidth=2,
                      edgecolor='#404040',
                      facecolor='none',
                      alpha=0.5)
    ax.add_patch(border)

    # Add data source attribution (r/dataisbeautiful style)
    fig.text(0.02, 0.02, 'Data Source | fbref',
             fontsize=12,
             alpha=0.6,
             color='#888888')

    # Adjust layout with MORE SPACING
    plt.tight_layout()
    plt.subplots_adjust(top=0.88,
                       bottom=0.12,
                       left=0.12,
                       right=0.95)

    plt.show()


def main():
    """Main execution function that orchestrates the entire analysis."""
    # Read data
    tables, match_logs = read_data()

    # Transform data
    season_dataframes = transform_season_data(tables)
    match_log_dataframes = transform_match_log_data(match_logs)

    # Join data
    season_data = join_data(season_dataframes)
    match_log_data = join_data(match_log_dataframes)

    # Organize and clean data
    final_data = organize_and_clean_data(season_data, match_log_data)

    # Save final data to CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, 'wirtz_performance_data.csv')
    final_data.to_csv(output_path, index=False)
    print(f"Final data saved to: {output_path}")
    print(f"Data shape: {final_data.shape}")
    print(f"Columns: {list(final_data.columns)}")

    # Plot the results
    plot_performance_data(final_data)


if __name__ == "__main__":
    main()