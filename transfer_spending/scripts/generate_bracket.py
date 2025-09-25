import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Top 8 teams from the transfer spending plot
teams = [
    "1. Paris Saint-Germain 23/24 (€454m)",
    "2. Liverpool FC 25/26 (€309m)",
    "3. FC Barcelona 19/20 (€304m)",
    "4. Juventus FC 18/19 (€265m)",
    "5. Chelsea FC 17/18 (€260m)",
    "6. Manchester City 23/24 (€260m)",
    "7. Real Madrid 18/19 (€165m)",
    "8. Atlético de Madrid 14/15 (€144m)"
]

# Traditional bracket matchups: 1v8, 2v7, 3v6, 4v5
matchups = [
    (teams[0], teams[7]),  # 1 vs 8
    (teams[3], teams[4]),  # 4 vs 5
    (teams[1], teams[6]),  # 2 vs 7
    (teams[2], teams[5])   # 3 vs 6
]

fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis('off')

# Title
ax.text(6, 7.5, 'Transfer Spending Tournament Bracket', 
        fontsize=18, fontweight='bold', ha='center')
ax.text(6, 7.1, 'Top 8 Teams by Transfer Expenditure (Traditional Seeding)', 
        fontsize=12, ha='center', style='italic')

# Quarter-finals positions
y_positions = [5.5, 4.5, 2.5, 1.5]

# Team colors from the original plot (Ligue 1 = purple, Premier League = blue, LaLiga = red, Serie A = green)
team_colors = {
    "Paris Saint-Germain": "#9966CC",  # Purple (Ligue 1)
    "Liverpool FC": "#4169E1",         # Blue (Premier League)
    "FC Barcelona": "#DC143C",         # Red (LaLiga)
    "Juventus FC": "#32CD32",          # Green (Serie A)
    "Chelsea FC": "#4169E1",           # Blue (Premier League)
    "Manchester City": "#4169E1",      # Blue (Premier League)
    "Real Madrid": "#DC143C",          # Red (LaLiga)
    "Atlético de Madrid": "#DC143C"    # Red (LaLiga)
}

# Draw quarter-final matchups
for i, ((team1, team2), y_pos) in enumerate(zip(matchups, y_positions)):
    # Extract team names for color lookup
    team1_name = team1.split(' 23/24')[0].split(' 25/26')[0].split(' 19/20')[0].split(' 18/19')[0].split(' 17/18')[0].split(' 14/15')[0].replace('1. ', '').replace('2. ', '').replace('3. ', '').replace('4. ', '').replace('5. ', '').replace('6. ', '').replace('7. ', '').replace('8. ', '')
    team2_name = team2.split(' 23/24')[0].split(' 25/26')[0].split(' 19/20')[0].split(' 18/19')[0].split(' 17/18')[0].split(' 14/15')[0].replace('1. ', '').replace('2. ', '').replace('3. ', '').replace('4. ', '').replace('5. ', '').replace('6. ', '').replace('7. ', '').replace('8. ', '')
    
    # Team 1
    rect1 = patches.Rectangle((0.5, y_pos), 3, 0.3, 
                             linewidth=1, edgecolor='black', facecolor=team_colors[team1_name])
    ax.add_patch(rect1)
    ax.text(2, y_pos + 0.15, team1.split('(')[0].strip(), 
            fontsize=9, ha='center', va='center', fontweight='bold', color='white')
    
    # Team 2
    rect2 = patches.Rectangle((0.5, y_pos - 0.4), 3, 0.3, 
                             linewidth=1, edgecolor='black', facecolor=team_colors[team2_name])
    ax.add_patch(rect2)
    ax.text(2, y_pos - 0.25, team2.split('(')[0].strip(), 
            fontsize=9, ha='center', va='center', fontweight='bold', color='white')
    
    # Connecting line
    ax.plot([3.5, 4.5], [y_pos - 0.05, y_pos - 0.05], 'k-', linewidth=2)

# Semi-final positions
sf_y_positions = [5, 2]
for i, y_pos in enumerate(sf_y_positions):
    rect = patches.Rectangle((5, y_pos - 0.15), 2.5, 0.3, 
                            linewidth=1, edgecolor='black', facecolor='lightyellow')
    ax.add_patch(rect)
    ax.text(6.25, y_pos, f'Semi-Final {i+1}', 
            fontsize=10, ha='center', va='center', fontweight='bold')
    
    # Connect quarter-finals to semi-finals
    if i == 0:
        ax.plot([4.5, 5], [5.45, 5], 'k-', linewidth=2)
        ax.plot([4.5, 5], [4.45, 5], 'k-', linewidth=2)
    else:
        ax.plot([4.5, 5], [2.45, 2], 'k-', linewidth=2)
        ax.plot([4.5, 5], [1.45, 2], 'k-', linewidth=2)
    
    # Connect to final
    ax.plot([7.5, 9], [y_pos, 3.5], 'k-', linewidth=2)

# Final
final_rect = patches.Rectangle((9, 3.35), 2.5, 0.3, 
                              linewidth=2, edgecolor='black', facecolor='gold')
ax.add_patch(final_rect)
ax.text(10.25, 3.5, 'FINAL', 
        fontsize=12, ha='center', va='center', fontweight='bold')

# Round labels
ax.text(2, 6.5, 'Quarter-Finals', fontsize=14, fontweight='bold', ha='center')
ax.text(6.25, 6.5, 'Semi-Finals', fontsize=14, fontweight='bold', ha='center')
ax.text(10.25, 6.5, 'Final', fontsize=14, fontweight='bold', ha='center')

# Matchup details
ax.text(0.5, 0.8, 'Matchups based on transfer spending rank:', fontsize=10, fontweight='bold')
ax.text(0.5, 0.5, '• 1 vs 8: PSG vs Atlético Madrid', fontsize=9)
ax.text(0.5, 0.2, '• 2 vs 7: Liverpool vs Real Madrid', fontsize=9)
ax.text(6, 0.5, '• 3 vs 6: Barcelona vs Manchester City', fontsize=9)
ax.text(6, 0.2, '• 4 vs 5: Juventus vs Chelsea', fontsize=9)

# Add color legend
legend_y = -0.2
ax.text(0.5, legend_y, 'League Colors:', fontsize=10, fontweight='bold')
ax.add_patch(patches.Rectangle((2.5, legend_y - 0.05), 0.2, 0.1, facecolor='#9966CC', edgecolor='black'))
ax.text(2.8, legend_y, 'Ligue 1', fontsize=9, va='center')
ax.add_patch(patches.Rectangle((4, legend_y - 0.05), 0.2, 0.1, facecolor='#4169E1', edgecolor='black'))
ax.text(4.3, legend_y, 'Premier League', fontsize=9, va='center')
ax.add_patch(patches.Rectangle((6, legend_y - 0.05), 0.2, 0.1, facecolor='#DC143C', edgecolor='black'))
ax.text(6.3, legend_y, 'LaLiga', fontsize=9, va='center')
ax.add_patch(patches.Rectangle((7.5, legend_y - 0.05), 0.2, 0.1, facecolor='#32CD32', edgecolor='black'))
ax.text(7.8, legend_y, 'Serie A', fontsize=9, va='center')

plt.tight_layout()
plt.savefig('/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/plots/transfer_spending_bracket.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.show()
print("Bracket saved to transfer_spending/plots/transfer_spending_bracket.png")