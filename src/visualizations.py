"""
Pentagon Protocol - Thesis Visualizations
Generates publication-ready charts for Chapter 5: Results and Analysis
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from typing import Dict, List, Any
import os

# Set publication-quality defaults
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.titlesize': 18,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.3
})

# Color scheme
COLORS = {
    'pentagon': '#2E86AB',      # Blue
    'baseline': '#E94F37',      # Red
    'pentagon_light': '#7EC8E3',
    'baseline_light': '#F4A492',
    'success': '#28A745',
    'warning': '#FFC107',
    'danger': '#DC3545',
    'neutral': '#6C757D'
}


def load_evaluation_data(filepath: str) -> Dict[str, Any]:
    """Load evaluation report JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================
# Figure 1: Composite Score Comparison by Prompt
# ============================================

def plot_composite_scores_by_prompt(data: Dict[str, Any], output_dir: str):
    """
    Bar chart comparing Pentagon vs Baseline composite scores for each prompt.
    """
    evaluations = data.get('prompt_evaluations', [])
    
    prompt_ids = [e['prompt_id'] for e in evaluations]
    pentagon_scores = [e['summary']['pentagon']['composite_score'] for e in evaluations]
    baseline_scores = [e['summary']['baseline']['composite_score'] for e in evaluations]
    complexities = [e['complexity'] for e in evaluations]
    
    x = np.arange(len(prompt_ids))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    bars1 = ax.bar(x - width/2, pentagon_scores, width, label='Pentagon Protocol', 
                   color=COLORS['pentagon'], edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, baseline_scores, width, label='Baseline (Single Agent)', 
                   color=COLORS['baseline'], edgecolor='black', linewidth=0.5)
    
    # Add value labels on bars
    for bar, score in zip(bars1, pentagon_scores):
        ax.annotate(f'{score:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, rotation=45)
    
    for bar, score in zip(bars2, baseline_scores):
        ax.annotate(f'{score:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, rotation=45)
    
    # Color-code x-axis labels by complexity
    complexity_colors = {'easy': '#28A745', 'medium': '#FFC107', 'complex': '#DC3545'}
    for i, (label, comp) in enumerate(zip(ax.get_xticklabels(), complexities)):
        ax.get_xticklabels()[i].set_color(complexity_colors.get(comp, 'black'))
    
    ax.set_xlabel('Prompt ID')
    ax.set_ylabel('Composite Score')
    ax.set_title('Figure 5.1: Composite Score Comparison by Prompt')
    ax.set_xticks(x)
    ax.set_xticklabels(prompt_ids)
    ax.legend(loc='lower right')
    ax.set_ylim(0.7, 1.05)
    
    # Add complexity legend
    easy_patch = mpatches.Patch(color='#28A745', label='Easy')
    medium_patch = mpatches.Patch(color='#FFC107', label='Medium')
    complex_patch = mpatches.Patch(color='#DC3545', label='Complex')
    
    legend1 = ax.legend(loc='lower right')
    legend2 = ax.legend(handles=[easy_patch, medium_patch, complex_patch], 
                        loc='lower left', title='Complexity')
    ax.add_artist(legend1)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig_5_1_composite_scores.png'))
    plt.savefig(os.path.join(output_dir, 'fig_5_1_composite_scores.pdf'))
    plt.close()
    print("✓ Generated: Figure 5.1 - Composite Score Comparison")


# ============================================
# Figure 2: Expected Features Implementation Rate
# ============================================

def plot_features_implementation(data: Dict[str, Any], output_dir: str):
    """
    Bar chart comparing feature implementation rates.
    """
    evaluations = data.get('prompt_evaluations', [])
    
    prompt_ids = [e['prompt_id'] for e in evaluations]
    pentagon_features = [e['expected_features']['pentagon']['percentage'] for e in evaluations]
    baseline_features = [e['expected_features']['baseline']['percentage'] for e in evaluations]
    total_features = [e['expected_features']['total_expected_features'] for e in evaluations]
    
    x = np.arange(len(prompt_ids))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    bars1 = ax.bar(x - width/2, pentagon_features, width, label='Pentagon Protocol', 
                   color=COLORS['pentagon'], edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, baseline_features, width, label='Baseline (Single Agent)', 
                   color=COLORS['baseline'], edgecolor='black', linewidth=0.5)
    
    # Add feature counts as annotations
    for i, (bar, total) in enumerate(zip(bars1, total_features)):
        ax.annotate(f'n={total}',
                    xy=(bar.get_x() + bar.get_width() / 2, 102),
                    ha='center', va='bottom', fontsize=8, color='gray')
    
    # Highlight prompts where Pentagon wins
    for i, (p, b) in enumerate(zip(pentagon_features, baseline_features)):
        if p > b:
            ax.annotate(f'+{p-b:.1f}%',
                        xy=(x[i], max(p, b) + 3),
                        ha='center', va='bottom', fontsize=10, 
                        color=COLORS['pentagon'], fontweight='bold')
    
    ax.set_xlabel('Prompt ID')
    ax.set_ylabel('Feature Implementation Rate (%)')
    ax.set_title('Figure 5.2: Expected Features Implementation Rate')
    ax.set_xticks(x)
    ax.set_xticklabels(prompt_ids)
    ax.legend(loc='lower right')
    ax.set_ylim(70, 115)
    ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5, label='100% baseline')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig_5_2_features_implementation.png'))
    plt.savefig(os.path.join(output_dir, 'fig_5_2_features_implementation.pdf'))
    plt.close()
    print("✓ Generated: Figure 5.2 - Features Implementation Rate")


# ============================================
# Figure 3: Radar Chart - Multi-dimensional Comparison
# ============================================

def plot_radar_comparison(data: Dict[str, Any], output_dir: str):
    """
    Radar chart showing multi-dimensional comparison.
    """
    aggregate = data.get('aggregate', {})
    pentagon = aggregate.get('pentagon', {})
    baseline = aggregate.get('baseline', {})
    
    # Dimensions to compare
    dimensions = ['Features', 'Pipeline', 'Executability', 'Code Quality', 'Composite']
    
    pentagon_values = [
        pentagon.get('features', {}).get('mean', 0),
        pentagon.get('pipeline', {}).get('mean', 0),
        pentagon.get('executability', {}).get('mean', 0),
        pentagon.get('quality', {}).get('mean', 0),
        pentagon.get('composite', {}).get('mean', 0)
    ]
    
    baseline_values = [
        baseline.get('features', {}).get('mean', 0),
        baseline.get('pipeline', {}).get('mean', 0),
        baseline.get('executability', {}).get('mean', 0),
        baseline.get('quality', {}).get('mean', 0),
        baseline.get('composite', {}).get('mean', 0)
    ]
    
    # Number of dimensions
    num_dims = len(dimensions)
    angles = np.linspace(0, 2 * np.pi, num_dims, endpoint=False).tolist()
    
    # Close the plot
    pentagon_values += pentagon_values[:1]
    baseline_values += baseline_values[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    ax.plot(angles, pentagon_values, 'o-', linewidth=2, label='Pentagon Protocol', 
            color=COLORS['pentagon'])
    ax.fill(angles, pentagon_values, alpha=0.25, color=COLORS['pentagon'])
    
    ax.plot(angles, baseline_values, 'o-', linewidth=2, label='Baseline (Single Agent)', 
            color=COLORS['baseline'])
    ax.fill(angles, baseline_values, alpha=0.25, color=COLORS['baseline'])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions)
    ax.set_ylim(0, 1.1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'])
    
    ax.set_title('Figure 5.3: Multi-dimensional Performance Comparison', y=1.08)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig_5_3_radar_comparison.png'))
    plt.savefig(os.path.join(output_dir, 'fig_5_3_radar_comparison.pdf'))
    plt.close()
    print("✓ Generated: Figure 5.3 - Radar Comparison")


# ============================================
# Figure 4: Performance by Complexity Level
# ============================================

def plot_performance_by_complexity(data: Dict[str, Any], output_dir: str):
    """
    Grouped bar chart showing performance by complexity level.
    """
    by_complexity = data.get('aggregate', {}).get('by_complexity', {})
    
    complexities = ['easy', 'medium', 'complex']
    pentagon_features = [by_complexity.get(c, {}).get('pentagon_features_mean', 0) * 100 for c in complexities]
    baseline_features = [by_complexity.get(c, {}).get('baseline_features_mean', 0) * 100 for c in complexities]
    pentagon_composite = [by_complexity.get(c, {}).get('pentagon_composite_mean', 0) for c in complexities]
    baseline_composite = [by_complexity.get(c, {}).get('baseline_composite_mean', 0) for c in complexities]
    counts = [by_complexity.get(c, {}).get('count', 0) for c in complexities]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    x = np.arange(len(complexities))
    width = 0.35
    
    # Features subplot
    ax1 = axes[0]
    bars1 = ax1.bar(x - width/2, pentagon_features, width, label='Pentagon', color=COLORS['pentagon'])
    bars2 = ax1.bar(x + width/2, baseline_features, width, label='Baseline', color=COLORS['baseline'])
    
    ax1.set_xlabel('Complexity Level')
    ax1.set_ylabel('Feature Implementation Rate (%)')
    ax1.set_title('(a) Expected Features by Complexity')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'{c.capitalize()}\n(n={counts[i]})' for i, c in enumerate(complexities)])
    ax1.legend()
    ax1.set_ylim(80, 105)
    
    # Add value labels
    for bar in bars1:
        ax1.annotate(f'{bar.get_height():.1f}%',
                     xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=10)
    for bar in bars2:
        ax1.annotate(f'{bar.get_height():.1f}%',
                     xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=10)
    
    # Composite subplot
    ax2 = axes[1]
    bars3 = ax2.bar(x - width/2, pentagon_composite, width, label='Pentagon', color=COLORS['pentagon'])
    bars4 = ax2.bar(x + width/2, baseline_composite, width, label='Baseline', color=COLORS['baseline'])
    
    ax2.set_xlabel('Complexity Level')
    ax2.set_ylabel('Composite Score')
    ax2.set_title('(b) Composite Score by Complexity')
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'{c.capitalize()}\n(n={counts[i]})' for i, c in enumerate(complexities)])
    ax2.legend()
    ax2.set_ylim(0.75, 1.0)
    
    # Add value labels
    for bar in bars3:
        ax2.annotate(f'{bar.get_height():.3f}',
                     xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=10)
    for bar in bars4:
        ax2.annotate(f'{bar.get_height():.3f}',
                     xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=10)
    
    fig.suptitle('Figure 5.4: Performance by Complexity Level', fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig_5_4_performance_by_complexity.png'))
    plt.savefig(os.path.join(output_dir, 'fig_5_4_performance_by_complexity.pdf'))
    plt.close()
    print("✓ Generated: Figure 5.4 - Performance by Complexity")


# ============================================
# Figure 5: Code Quality Breakdown
# ============================================

def plot_code_quality_breakdown(data: Dict[str, Any], output_dir: str):
    """
    Bar chart showing code quality dimensions.
    """
    evaluations = data.get('prompt_evaluations', [])
    
    # Extract quality dimensions
    pentagon_structure = []
    pentagon_readability = []
    pentagon_api = []
    pentagon_error = []
    baseline_structure = []
    baseline_readability = []
    baseline_api = []
    baseline_error = []
    
    for e in evaluations:
        pq = e.get('code_quality_llm', {}).get('pentagon', {})
        bq = e.get('code_quality_llm', {}).get('baseline', {})
        
        pentagon_structure.append(pq.get('code_structure', 5))
        pentagon_readability.append(pq.get('readability', 5))
        pentagon_api.append(pq.get('api_design', 5))
        pentagon_error.append(pq.get('error_handling', 5))
        
        baseline_structure.append(bq.get('code_structure', 5))
        baseline_readability.append(bq.get('readability', 5))
        baseline_api.append(bq.get('api_design', 5))
        baseline_error.append(bq.get('error_handling', 5))
    
    # Calculate means
    dimensions = ['Code\nStructure', 'Readability', 'API\nDesign', 'Error\nHandling']
    pentagon_means = [
        np.mean(pentagon_structure),
        np.mean(pentagon_readability),
        np.mean(pentagon_api),
        np.mean(pentagon_error)
    ]
    baseline_means = [
        np.mean(baseline_structure),
        np.mean(baseline_readability),
        np.mean(baseline_api),
        np.mean(baseline_error)
    ]
    
    x = np.arange(len(dimensions))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars1 = ax.bar(x - width/2, pentagon_means, width, label='Pentagon Protocol', 
                   color=COLORS['pentagon'], edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, baseline_means, width, label='Baseline (Single Agent)', 
                   color=COLORS['baseline'], edgecolor='black', linewidth=0.5)
    
    # Add improvement percentages
    for i, (p, b) in enumerate(zip(pentagon_means, baseline_means)):
        if b > 0:
            improvement = ((p - b) / b) * 100
            ax.annotate(f'+{improvement:.0f}%',
                        xy=(x[i], max(p, b) + 0.3),
                        ha='center', va='bottom', fontsize=11,
                        color=COLORS['pentagon'], fontweight='bold')
    
    # Add value labels
    for bar in bars1:
        ax.annotate(f'{bar.get_height():.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)
    for bar in bars2:
        ax.annotate(f'{bar.get_height():.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)
    
    ax.set_xlabel('Quality Dimension')
    ax.set_ylabel('Score (1-10)')
    ax.set_title('Figure 5.5: Code Quality Breakdown by Dimension')
    ax.set_xticks(x)
    ax.set_xticklabels(dimensions)
    ax.legend(loc='upper right')
    ax.set_ylim(0, 11)
    ax.axhline(y=5, color='gray', linestyle='--', alpha=0.5, label='Neutral (5.0)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig_5_5_code_quality_breakdown.png'))
    plt.savefig(os.path.join(output_dir, 'fig_5_5_code_quality_breakdown.pdf'))
    plt.close()
    print("✓ Generated: Figure 5.5 - Code Quality Breakdown")


# ============================================
# Figure 6: Execution Time vs Quality Trade-off
# ============================================

def plot_time_quality_tradeoff(data: Dict[str, Any], output_dir: str):
    """
    Scatter plot showing execution time vs quality trade-off.
    """
    evaluations = data.get('prompt_evaluations', [])
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for e in evaluations:
        prompt_id = e['prompt_id']
        complexity = e['complexity']
        
        # Pentagon point
        p_time = e['efficiency']['pentagon']['execution_time_seconds']
        p_quality = e['summary']['pentagon']['composite_score']
        
        # Baseline point
        b_time = e['efficiency']['baseline']['execution_time_seconds']
        b_quality = e['summary']['baseline']['composite_score']
        
        # Plot Pentagon
        marker_size = {'easy': 100, 'medium': 150, 'complex': 200}.get(complexity, 100)
        ax.scatter(p_time, p_quality, s=marker_size, c=COLORS['pentagon'], 
                   alpha=0.7, edgecolors='black', linewidth=1)
        ax.annotate(prompt_id, (p_time, p_quality), textcoords="offset points",
                    xytext=(5, 5), fontsize=8, color=COLORS['pentagon'])
        
        # Plot Baseline
        ax.scatter(b_time, b_quality, s=marker_size, c=COLORS['baseline'], 
                   alpha=0.7, edgecolors='black', linewidth=1, marker='s')
        ax.annotate(prompt_id, (b_time, b_quality), textcoords="offset points",
                    xytext=(5, -10), fontsize=8, color=COLORS['baseline'])
        
        # Draw connecting line
        ax.plot([b_time, p_time], [b_quality, p_quality], 
                'k--', alpha=0.2, linewidth=1)
    
    # Legend
    pentagon_patch = plt.scatter([], [], c=COLORS['pentagon'], s=100, label='Pentagon Protocol')
    baseline_patch = plt.scatter([], [], c=COLORS['baseline'], s=100, marker='s', label='Baseline')
    
    ax.set_xlabel('Execution Time (seconds)')
    ax.set_ylabel('Composite Score')
    ax.set_title('Figure 5.6: Execution Time vs Quality Trade-off')
    ax.legend(handles=[pentagon_patch, baseline_patch], loc='lower right')
    
    # Add quadrant labels
    ax.axhline(y=0.9, color='gray', linestyle=':', alpha=0.5)
    ax.axvline(x=200, color='gray', linestyle=':', alpha=0.5)
    ax.text(50, 0.97, 'Fast & High Quality', fontsize=10, style='italic', alpha=0.7)
    ax.text(400, 0.97, 'Slow & High Quality', fontsize=10, style='italic', alpha=0.7)
    ax.text(50, 0.82, 'Fast & Lower Quality', fontsize=10, style='italic', alpha=0.7)
    ax.text(400, 0.82, 'Slow & Lower Quality', fontsize=10, style='italic', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig_5_6_time_quality_tradeoff.png'))
    plt.savefig(os.path.join(output_dir, 'fig_5_6_time_quality_tradeoff.pdf'))
    plt.close()
    print("✓ Generated: Figure 5.6 - Time vs Quality Trade-off")


# ============================================
# Figure 7: Box Plot - Score Distribution
# ============================================
def plot_score_distributions(data: Dict[str, Any], output_dir: str):
    """
    Box plots showing score distributions.
    """
    evaluations = data.get('prompt_evaluations', [])
    
    pentagon_composites = [e['summary']['pentagon']['composite_score'] for e in evaluations]
    baseline_composites = [e['summary']['baseline']['composite_score'] for e in evaluations]
    pentagon_features = [e['summary']['pentagon']['features_score'] for e in evaluations]
    baseline_features = [e['summary']['baseline']['features_score'] for e in evaluations]
    pentagon_quality = [e['summary']['pentagon']['quality_score'] for e in evaluations]
    baseline_quality = [e['summary']['baseline']['quality_score'] for e in evaluations]
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    
    # Composite Score
    ax1 = axes[0]
    bp1 = ax1.boxplot([pentagon_composites, baseline_composites], 
                       tick_labels=['Pentagon', 'Baseline'],  # Changed from 'labels'
                       patch_artist=True)
    bp1['boxes'][0].set_facecolor(COLORS['pentagon_light'])
    bp1['boxes'][1].set_facecolor(COLORS['baseline_light'])
    ax1.set_ylabel('Score')
    ax1.set_title('(a) Composite Score Distribution')
    ax1.set_ylim(0.75, 1.0)
    
    # Features Score
    ax2 = axes[1]
    bp2 = ax2.boxplot([pentagon_features, baseline_features], 
                       tick_labels=['Pentagon', 'Baseline'],  # Changed from 'labels'
                       patch_artist=True)
    bp2['boxes'][0].set_facecolor(COLORS['pentagon_light'])
    bp2['boxes'][1].set_facecolor(COLORS['baseline_light'])
    ax2.set_ylabel('Score')
    ax2.set_title('(b) Features Score Distribution')
    ax2.set_ylim(0.7, 1.05)
    
    # Quality Score
    ax3 = axes[2]
    bp3 = ax3.boxplot([pentagon_quality, baseline_quality], 
                       tick_labels=['Pentagon', 'Baseline'],  # Changed from 'labels'
                       patch_artist=True)
    bp3['boxes'][0].set_facecolor(COLORS['pentagon_light'])
    bp3['boxes'][1].set_facecolor(COLORS['baseline_light'])
    ax3.set_ylabel('Score')
    ax3.set_title('(c) Code Quality Score Distribution')
    ax3.set_ylim(0.3, 1.0)
    
    fig.suptitle('Figure 5.7: Score Distribution Comparison', fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig_5_7_score_distributions.png'))
    plt.savefig(os.path.join(output_dir, 'fig_5_7_score_distributions.pdf'))
    plt.close()
    print("✓ Generated: Figure 5.7 - Score Distributions")
    

# ============================================
# Figure 8: Win Rate Summary
# ============================================

def plot_win_rate_summary(data: Dict[str, Any], output_dir: str):
    """
    Pie chart and bar chart showing win rates.
    """
    comparison = data.get('aggregate', {}).get('comparison', {})
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Pie chart - Composite Win Rate
    ax1 = axes[0]
    pentagon_wins = comparison.get('pentagon_wins', 0)
    baseline_wins = comparison.get('baseline_wins', 0)
    
    sizes = [pentagon_wins, baseline_wins]
    labels = [f'Pentagon\n({pentagon_wins} wins)', f'Baseline\n({baseline_wins} wins)']
    colors = [COLORS['pentagon'], COLORS['baseline']]
    explode = (0.05, 0)
    
    wedges, texts, autotexts = ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
                                        autopct='%1.0f%%', shadow=True, startangle=90,
                                        textprops={'fontsize': 12})
    autotexts[0].set_fontsize(14)
    autotexts[0].set_fontweight('bold')
    ax1.set_title('(a) Composite Score Win Rate')
    
    # Bar chart - Dimension Win Rates
    ax2 = axes[1]
    
    # Calculate win rates per dimension
    evaluations = data.get('prompt_evaluations', [])
    dimensions = ['Features', 'Pipeline', 'Executability', 'Quality']
    pentagon_wins_by_dim = []
    
    for dim in ['features', 'pipeline', 'executability', 'quality']:
        wins = 0
        for e in evaluations:
            p_score = e['summary']['pentagon'].get(f'{dim}_score', 0)
            b_score = e['summary']['baseline'].get(f'{dim}_score', 0)
            if p_score > b_score:
                wins += 1
        pentagon_wins_by_dim.append(wins / len(evaluations) * 100)
    
    x = np.arange(len(dimensions))
    bars = ax2.bar(x, pentagon_wins_by_dim, color=COLORS['pentagon'], edgecolor='black')
    
    ax2.set_xlabel('Dimension')
    ax2.set_ylabel('Pentagon Win Rate (%)')
    ax2.set_title('(b) Pentagon Win Rate by Dimension')
    ax2.set_xticks(x)
    ax2.set_xticklabels(dimensions)
    ax2.set_ylim(0, 110)
    ax2.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50% baseline')
    
    for bar in bars:
        ax2.annotate(f'{bar.get_height():.0f}%',
                     xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    fig.suptitle('Figure 5.8: Win Rate Summary', fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig_5_8_win_rate_summary.png'))
    plt.savefig(os.path.join(output_dir, 'fig_5_8_win_rate_summary.pdf'))
    plt.close()
    print("✓ Generated: Figure 5.8 - Win Rate Summary")


# ============================================
# Figure 9: Feature Detail Heatmap
# ============================================

def plot_feature_heatmap(data: Dict[str, Any], output_dir: str):
    """
    Heatmap showing feature implementation status per prompt.
    """
    evaluations = data.get('prompt_evaluations', [])
    
    # Build matrix
    prompt_ids = [e['prompt_id'] for e in evaluations]
    
    # Pentagon feature percentages
    pentagon_pcts = [e['expected_features']['pentagon']['percentage'] / 100 for e in evaluations]
    baseline_pcts = [e['expected_features']['baseline']['percentage'] / 100 for e in evaluations]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create heatmap data
    data_matrix = np.array([pentagon_pcts, baseline_pcts])
    
    im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=0.7, vmax=1.0)
    
    ax.set_xticks(np.arange(len(prompt_ids)))
    ax.set_yticks(np.arange(2))
    ax.set_xticklabels(prompt_ids)
    ax.set_yticklabels(['Pentagon', 'Baseline'])
    
    # Add text annotations
    for i in range(2):
        for j in range(len(prompt_ids)):
            value = data_matrix[i, j]
            text_color = 'white' if value < 0.85 else 'black'
            ax.text(j, i, f'{value*100:.0f}%', ha='center', va='center', 
                    color=text_color, fontsize=11, fontweight='bold')
    
    ax.set_title('Figure 5.9: Feature Implementation Rate Heatmap')
    
    # Colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Implementation Rate', rotation=-90, va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig_5_9_feature_heatmap.png'))
    plt.savefig(os.path.join(output_dir, 'fig_5_9_feature_heatmap.pdf'))
    plt.close()
    print("✓ Generated: Figure 5.9 - Feature Heatmap")


# ============================================
# Figure 10: Summary Statistics Table (as image)
# ============================================

def plot_summary_table(data: Dict[str, Any], output_dir: str):
    """
    Generate summary statistics table as an image.
    """
    aggregate = data.get('aggregate', {})
    pentagon = aggregate.get('pentagon', {})
    baseline = aggregate.get('baseline', {})
    comparison = aggregate.get('comparison', {})
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    # Table data
    table_data = [
        ['Metric', 'Pentagon', 'Baseline', 'Advantage', 'Winner'],
        ['', '', '', '', ''],
        ['Features (Mean)', f"{pentagon['features']['mean']*100:.1f}%", 
         f"{baseline['features']['mean']*100:.1f}%", 
         f"+{(pentagon['features']['mean']-baseline['features']['mean'])*100:.1f}%", 'Pentagon'],
        ['Features (Std)', f"{pentagon['features']['std']*100:.1f}%", 
         f"{baseline['features']['std']*100:.1f}%", '-', '-'],
        ['', '', '', '', ''],
        ['Pipeline Success', f"{pentagon['pipeline']['mean']*100:.0f}%", 
         f"{baseline['pipeline']['mean']*100:.0f}%", '0%', 'Tie'],
        ['Executability', f"{pentagon['executability']['mean']*100:.0f}%", 
         f"{baseline['executability']['mean']*100:.0f}%", '0%', 'Tie'],
        ['', '', '', '', ''],
        ['Code Quality', f"{pentagon['quality']['mean']*100:.1f}%", 
         f"{baseline['quality']['mean']*100:.1f}%", 
         f"+{(pentagon['quality']['mean']-baseline['quality']['mean'])*100:.1f}%", 'Pentagon'],
        ['QA Pass Rate', f"{pentagon['qa']['mean']*100:.0f}%", 'N/A', 'N/A', 'Pentagon'],
        ['', '', '', '', ''],
        ['Composite (Mean)', f"{pentagon['composite']['mean']:.3f}", 
         f"{baseline['composite']['mean']:.3f}", 
         f"+{comparison['average_composite_advantage']:.3f}", 'Pentagon'],
        ['Composite (Std)', f"{pentagon['composite']['std']:.3f}", 
         f"{baseline['composite']['std']:.3f}", '-', '-'],
        ['', '', '', '', ''],
        ['Win Rate', f"{comparison['pentagon_win_rate']*100:.0f}%", 
         f"{(1-comparison['pentagon_win_rate'])*100:.0f}%", '-', 'Pentagon'],
    ]
    
    table = ax.table(cellText=table_data, loc='center', cellLoc='center',
                     colWidths=[0.25, 0.15, 0.15, 0.15, 0.15])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)
    
    # Style header
    for i in range(5):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(color='white', fontweight='bold')
    
    # Highlight Pentagon wins
    for row in range(2, len(table_data)):
        if len(table_data[row]) > 4 and table_data[row][4] == 'Pentagon':
            table[(row, 4)].set_facecolor(COLORS['pentagon_light'])
    
    ax.set_title('Figure 5.10: Summary Statistics', fontsize=16, y=0.95)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fig_5_10_summary_table.png'))
    plt.savefig(os.path.join(output_dir, 'fig_5_10_summary_table.pdf'))
    plt.close()
    print("✓ Generated: Figure 5.10 - Summary Table")


# ============================================
# Main Execution
# ============================================

def generate_all_visualizations(evaluation_json_path: str, output_dir: str = 'thesis_figures'):
    """
    Generate all thesis visualizations from evaluation data.
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load data
    print(f"Loading evaluation data from: {evaluation_json_path}")
    data = load_evaluation_data(evaluation_json_path)
    print(f"Loaded data for {data.get('total_prompts', 0)} prompts")
    
    print(f"\nGenerating visualizations in: {output_dir}/")
    print("=" * 50)
    
    # Generate all figures
    plot_composite_scores_by_prompt(data, output_dir)
    plot_features_implementation(data, output_dir)
    plot_radar_comparison(data, output_dir)
    plot_performance_by_complexity(data, output_dir)
    plot_code_quality_breakdown(data, output_dir)
    plot_time_quality_tradeoff(data, output_dir)
    plot_score_distributions(data, output_dir)
    plot_win_rate_summary(data, output_dir)
    plot_feature_heatmap(data, output_dir)
    plot_summary_table(data, output_dir)
    
    print("=" * 50)
    print(f"✓ All visualizations generated successfully!")
    print(f"  Output directory: {output_dir}/")
    print(f"  Files generated: 10 figures (PNG + PDF)")
    
    return output_dir

# rename_figures.py
import os
import shutil

# Mapping: original filename -> thesis figure number
FIGURE_MAPPING = {
    'fig_5_9_feature_heatmap': 'fig_5_1_feature_heatmap',
    'fig_5_2_features_implementation': 'fig_5_2_features_implementation',
    'fig_5_1_composite_scores': 'fig_5_3_composite_scores',
    'fig_5_3_radar_comparison': 'fig_5_4_radar_comparison',
    'fig_5_5_code_quality_breakdown': 'fig_5_5_code_quality_breakdown',
    'fig_5_4_performance_by_complexity': 'fig_5_6_performance_by_complexity',
    'fig_5_7_score_distributions': 'fig_5_7_score_distributions',
    'fig_5_6_time_quality_tradeoff': 'fig_5_8_time_quality_tradeoff',
    'fig_5_8_win_rate_summary': 'fig_5_9_win_rate_summary',
    'fig_5_10_summary_table': 'fig_5_10_summary_table',
}

def rename_figures(input_dir='thesis_figures', output_dir='thesis_figures_final'):
    os.makedirs(output_dir, exist_ok=True)
    
    for old_name, new_name in FIGURE_MAPPING.items():
        for ext in ['.png', '.pdf']:
            old_path = os.path.join(input_dir, old_name + ext)
            new_path = os.path.join(output_dir, new_name + ext)
            
            if os.path.exists(old_path):
                shutil.copy(old_path, new_path)
                print(f"✓ {old_name}{ext} -> {new_name}{ext}")
            else:
                print(f"✗ {old_name}{ext} not found")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    else:
        json_path = "evaluation_output/evaluation_report.json"
    
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = "thesis_figures"
    
    generate_all_visualizations(json_path, output_dir)
    rename_figures()
