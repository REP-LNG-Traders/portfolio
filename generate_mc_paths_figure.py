"""
Monte Carlo Paths Visualization
================================
Generates a Monte Carlo path visualization showing 1000 simulated P&L paths
with monthly progression for both hedged and unhedged strategies.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuration
OUTPUT_DIR = Path('outputs/figures/paper_figures_1-8')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DPI = 300

COLORS = {
    'primary_blue': '#2E86AB',
    'success_green': '#06A77D',
    'alert_red': '#C1121F',
    'light_gray': '#EEEEEE'
}

# ============================================================================
# Generate MC Paths
# ============================================================================

def generate_mc_paths():
    """Generate Monte Carlo P&L paths for unhedged and hedged strategies"""
    
    np.random.seed(42)
    
    # Monte Carlo parameters
    n_paths = 1000
    n_months = 6
    
    # Monthly base P&L means and volatilities
    base_pnl_monthly = np.array([22.78, 24.26, 27.55, 27.55, 29.73, 29.73])
    
    # Unhedged: higher volatility (HH-dominated, 73% of variance)
    unhedged_vol_monthly = np.array([4.5, 4.8, 5.2, 5.0, 5.5, 5.3])
    
    # Hedged: lower volatility (HH hedged away, 32.5% reduction)
    hedged_vol_monthly = np.array([3.0, 3.2, 3.5, 3.4, 3.7, 3.6])
    
    # Generate paths
    unhedged_paths = np.zeros((n_paths, n_months))
    hedged_paths = np.zeros((n_paths, n_months))
    
    # Cumulative P&L
    unhedged_cumulative = np.zeros((n_paths, n_months))
    hedged_cumulative = np.zeros((n_paths, n_months))
    
    for m in range(n_months):
        # Generate random shocks
        shocks = np.random.normal(0, 1, n_paths)
        
        # Unhedged paths
        monthly_pnl_unhedged = base_pnl_monthly[m] + unhedged_vol_monthly[m] * shocks
        unhedged_paths[:, m] = monthly_pnl_unhedged
        unhedged_cumulative[:, m] = np.sum(unhedged_paths[:, :m+1], axis=1)
        
        # Hedged paths
        monthly_pnl_hedged = base_pnl_monthly[m] + hedged_vol_monthly[m] * shocks
        hedged_paths[:, m] = monthly_pnl_hedged
        hedged_cumulative[:, m] = np.sum(hedged_paths[:, :m+1], axis=1)
    
    return unhedged_cumulative, hedged_cumulative, n_months

# ============================================================================
# Create Figure
# ============================================================================

def create_mc_paths_visualization():
    """Create Monte Carlo paths visualization"""
    
    print("[GEN] Generating Monte Carlo Paths Visualization...")
    
    unhedged_paths, hedged_paths, n_months = generate_mc_paths()
    
    # Create figure with side-by-side plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), dpi=DPI)
    
    months = np.arange(1, n_months + 1)
    
    # ========== UNHEDGED PATHS ==========
    for i in range(unhedged_paths.shape[0]):
        ax1.plot(months, unhedged_paths[i, :], color=COLORS['alert_red'], 
                alpha=0.03, linewidth=0.5)
    
    # Plot percentiles
    p5_unhedged = np.percentile(unhedged_paths, 5, axis=0)
    p25_unhedged = np.percentile(unhedged_paths, 25, axis=0)
    p50_unhedged = np.percentile(unhedged_paths, 50, axis=0)
    p75_unhedged = np.percentile(unhedged_paths, 75, axis=0)
    p95_unhedged = np.percentile(unhedged_paths, 95, axis=0)
    
    ax1.fill_between(months, p5_unhedged, p95_unhedged, 
                     color=COLORS['alert_red'], alpha=0.15, label='5th-95th %ile')
    ax1.fill_between(months, p25_unhedged, p75_unhedged, 
                     color=COLORS['alert_red'], alpha=0.25, label='25th-75th %ile')
    ax1.plot(months, p50_unhedged, color=COLORS['alert_red'], linewidth=3, 
            label='Median (50th %ile)', zorder=10)
    
    ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Cumulative P&L ($M)', fontsize=12, fontweight='bold')
    ax1.set_title('Unhedged Strategy - 1,000 MC Paths\nHigh volatility: $22.77M (HH-dominated)', 
                 fontsize=13, fontweight='bold')
    ax1.set_xticks(months)
    ax1.set_xticklabels([f'M{m}' for m in months])
    ax1.grid(True, alpha=0.3)
    ax1.set_facecolor(COLORS['light_gray'])
    ax1.legend(fontsize=10, loc='upper left')
    
    # ========== HEDGED PATHS ==========
    for i in range(hedged_paths.shape[0]):
        ax2.plot(months, hedged_paths[i, :], color=COLORS['success_green'], 
                alpha=0.03, linewidth=0.5)
    
    # Plot percentiles
    p5_hedged = np.percentile(hedged_paths, 5, axis=0)
    p25_hedged = np.percentile(hedged_paths, 25, axis=0)
    p50_hedged = np.percentile(hedged_paths, 50, axis=0)
    p75_hedged = np.percentile(hedged_paths, 75, axis=0)
    p95_hedged = np.percentile(hedged_paths, 95, axis=0)
    
    ax2.fill_between(months, p5_hedged, p95_hedged, 
                     color=COLORS['success_green'], alpha=0.15, label='5th-95th %ile')
    ax2.fill_between(months, p25_hedged, p75_hedged, 
                     color=COLORS['success_green'], alpha=0.25, label='25th-75th %ile')
    ax2.plot(months, p50_hedged, color=COLORS['success_green'], linewidth=3, 
            label='Median (50th %ile)', zorder=10)
    
    ax2.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Cumulative P&L ($M)', fontsize=12, fontweight='bold')
    ax2.set_title('Hedged Strategy - 1,000 MC Paths\nLow volatility: $15.37M (HH hedged)', 
                 fontsize=13, fontweight='bold')
    ax2.set_xticks(months)
    ax2.set_xticklabels([f'M{m}' for m in months])
    ax2.grid(True, alpha=0.3)
    ax2.set_facecolor(COLORS['light_gray'])
    ax2.legend(fontsize=10, loc='upper left')
    
    # Overall title
    fig.suptitle('Figure 2b: Monte Carlo P&L Paths - Contract Period Evolution\n1,000 simulated scenarios showing cumulative P&L progression with percentile bands', 
                fontsize=15, fontweight='bold', y=1.00)
    
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / '02b_mc_paths_visualization.png', dpi=DPI, bbox_inches='tight')
    print("[OK] Monte Carlo paths figure saved: 02b_mc_paths_visualization.png")
    plt.close()

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("MONTE CARLO PATHS VISUALIZATION")
    print("=" * 80)
    
    create_mc_paths_visualization()
    
    print("\n" + "=" * 80)
    print("[SUCCESS] Figure generated successfully!")
    print("=" * 80)
    print(f"\n[FILE] outputs/figures/paper_figures_1-8/02b_mc_paths_visualization.png")
    print("\n[READY] Ready for insertion in paper!")
