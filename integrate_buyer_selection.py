"""
Integrate Buyer Selection Framework with Real Optimization Data

This script runs the actual optimization to get real P&L data,
then applies the buyer selection scoring framework.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging

from data_processing.loaders import load_all_data
from models.optimization import CargoPnLCalculator, StrategyOptimizer
from models.buyer_selection import (
    BuyerSelectionFramework,
    create_buyer_selection_matrix,
    create_selection_summary_table
)
from config.constants import CARGO_CONTRACT
from typing import Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_buyer_options_from_optimization(
    optimizer: StrategyOptimizer,
    forecasts: Dict[str, pd.Series]
) -> Dict[str, Dict]:
    """
    Extract buyer options from the actual optimization.
    
    Returns:
        Dict of {month: {(destination, buyer): {margin, pnl, ...}}}
    """
    buyer_options_by_month = {}
    
    for month in CARGO_CONTRACT['delivery_period']:
        logger.info(f"Extracting options for {month}...")
        
        # Get all options for this month from the optimizer
        options_df = optimizer.evaluate_all_options_for_month(month, forecasts)
        
        # Filter out cancel option and extract buyer options
        buyer_options_df = options_df[options_df['destination'] != 'Cancel'].copy()
        
        # Extract margin per MMBtu
        buyer_options_df['margin_per_mmbtu'] = (
            buyer_options_df['expected_pnl'] / buyer_options_df['cargo_volume']
        )
        
        # Build dictionary for this month
        month_options = {}
        for _, row in buyer_options_df.iterrows():
            key = (row['destination'], row['buyer'])
            month_options[key] = {
                'margin': row['margin_per_mmbtu'],
                'pnl': row['expected_pnl'],
                'cargo_volume': row['cargo_volume'],
                'sale_revenue': row.get('sale_revenue', 0),
                'purchase_cost': row.get('purchase_cost', 0),
                'freight_cost': row.get('freight_cost', 0),
                'terminal_cost': row.get('terminal_cost', 0)
            }
        
        buyer_options_by_month[month] = month_options
        logger.info(f"  Found {len(month_options)} buyer options for {month}")
    
    return buyer_options_by_month


def main():
    """Run integrated buyer selection analysis with real data."""
    logger.info("=" * 80)
    logger.info("INTEGRATED BUYER SELECTION ANALYSIS (REAL DATA)")
    logger.info("=" * 80)
    
    # Create output directory
    output_dir = Path("outputs/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Step 1: Load real data
    logger.info("\nStep 1: Loading real market data...")
    data = load_all_data()
    logger.info("  ✓ Data loaded successfully")
    
    # Step 2: Generate forecasts (simplified - using simple method for speed)
    logger.info("\nStep 2: Generating price forecasts...")
    # Use simple forecasts for speed (can switch to ARIMA+GARCH if needed)
    from main_optimization import prepare_forecasts_simple
    forecasts = prepare_forecasts_simple(data)
    logger.info("  ✓ Forecasts generated")
    logger.info(f"    HH: ${forecasts['henry_hub'].iloc[0]:.2f}/MMBtu")
    logger.info(f"    JKM: ${forecasts['jkm'].iloc[0]:.2f}/MMBtu")
    logger.info(f"    Brent: ${forecasts['brent'].iloc[0]:.2f}/bbl")
    logger.info(f"    Freight: ${forecasts['freight'].iloc[0]:.0f}/day")
    
    # Step 3: Run optimization to get all buyer options
    logger.info("\nStep 3: Running optimization to evaluate all buyer options...")
    calculator = CargoPnLCalculator()
    optimizer = StrategyOptimizer(calculator)
    
    buyer_options_by_month = extract_buyer_options_from_optimization(
        optimizer, forecasts
    )
    
    # Step 4: Apply buyer selection framework
    logger.info("\nStep 4: Applying buyer selection scoring framework...")
    framework = BuyerSelectionFramework()
    
    monthly_rankings = {}
    for month, options in buyer_options_by_month.items():
        if len(options) == 0:
            logger.warning(f"  No options found for {month}, skipping...")
            continue
            
        ranked_df = framework.rank_buyers_for_month(month, options)
        monthly_rankings[month] = ranked_df
        
        # Show top 3
        logger.info(f"\n{month} - Top 3 Selections:")
        for i, row in ranked_df.head(3).iterrows():
            logger.info(
                f"  {int(row['rank'])}. {row['buyer']} ({row['credit_rating']}) at {row['destination']}: "
                f"Score={row['composite_score']:.1f}, "
                f"Margin=${row['expected_margin']:.2f}/MMBtu, "
                f"P&L=${row['expected_pnl_millions']:.2f}M"
            )
    
    # Step 5: Create outputs
    logger.info("\nStep 5: Generating output files...")
    
    # Matrix CSV
    matrix_path = output_dir / f"buyer_selection_matrix_REAL_{timestamp}.csv"
    matrix_df = create_buyer_selection_matrix(monthly_rankings, str(matrix_path))
    logger.info(f"  ✓ Matrix saved: {matrix_path.name}")
    
    # Rationale TXT
    rationale_path = output_dir / f"selection_rationale_REAL_{timestamp}.txt"
    with open(rationale_path, 'w', encoding='utf-8') as f:
        f.write("BUYER SELECTION DECISION RATIONALES (REAL DATA)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Framework Weights: {framework.weights}\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for month in sorted(monthly_rankings.keys()):
            ranked_df = monthly_rankings[month]
            selected = ranked_df[ranked_df['rank'] == 1].iloc[0]
            
            rationale = framework.generate_selection_rationale(
                month=month,
                selected_buyer=selected['buyer'],
                selected_destination=selected['destination'],
                ranked_df=ranked_df
            )
            
            f.write(rationale)
            f.write("\n" + "-" * 80 + "\n\n")
    
    logger.info(f"  ✓ Rationales saved: {rationale_path.name}")
    
    # Sensitivity analysis
    logger.info("\nStep 6: Running sensitivity analysis...")
    sensitivity_results = []
    for month, options in buyer_options_by_month.items():
        if len(options) == 0:
            continue
        sensitivity = framework.run_sensitivity_analysis(month, options)
        sensitivity_results.append(sensitivity)
        status = "ROBUST" if sensitivity['is_robust'] else "MARGINAL"
        logger.info(f"  {month}: {status}")
    
    sensitivity_path = output_dir / f"sensitivity_check_REAL_{timestamp}.csv"
    sensitivity_rows = []
    for result in sensitivity_results:
        for selection in result['selections']:
            sensitivity_rows.append({
                'month': result['month'],
                'credit_weight': selection['weights']['credit'],
                'demand_weight': selection['weights']['demand'],
                'selected_buyer': selection['selected_buyer'],
                'selected_destination': selection['selected_destination'],
                'composite_score': selection['composite_score']
            })
    
    sensitivity_df = pd.DataFrame(sensitivity_rows)
    sensitivity_df.to_csv(sensitivity_path, index=False)
    logger.info(f"  ✓ Sensitivity saved: {sensitivity_path.name}")
    
    # Summary table
    summary_df = create_selection_summary_table(monthly_rankings)
    summary_path = output_dir / f"buyer_selection_summary_REAL_{timestamp}.csv"
    summary_df.to_csv(summary_path, index=False)
    
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY TABLE (PowerPoint-Ready):")
    logger.info("=" * 80)
    print("\n" + summary_df.to_string(index=False))
    logger.info(f"\n  ✓ Summary saved: {summary_path.name}")
    
    # Step 7: Aggregate statistics
    logger.info("\n" + "=" * 80)
    logger.info("AGGREGATE STATISTICS:")
    logger.info("=" * 80)
    
    total_pnl = sum(
        df[df['rank'] == 1]['expected_pnl_millions'].iloc[0]
        for df in monthly_rankings.values()
    )
    logger.info(f"  Total Expected P&L: ${total_pnl:.2f}M")
    
    robust_months = sum(1 for r in sensitivity_results if r['is_robust'])
    logger.info(f"  Robust Selections: {robust_months}/{len(sensitivity_results)} months")
    
    # Destination distribution
    selected_destinations = [
        df[df['rank'] == 1]['destination'].iloc[0]
        for df in monthly_rankings.values()
    ]
    dest_counts = pd.Series(selected_destinations).value_counts()
    logger.info(f"\n  Selected Destinations:")
    for dest, count in dest_counts.items():
        logger.info(f"    {dest}: {count} months")
    
    # Buyer distribution
    selected_buyers = [
        df[df['rank'] == 1]['buyer'].iloc[0]
        for df in monthly_rankings.values()
    ]
    buyer_counts = pd.Series(selected_buyers).value_counts()
    logger.info(f"\n  Selected Buyers:")
    for buyer, count in buyer_counts.items():
        rating = framework.credit_ratings.get(buyer, 'Unknown')
        logger.info(f"    {buyer} ({rating}): {count} months")
    
    logger.info("\n" + "=" * 80)
    logger.info("ANALYSIS COMPLETE - USING REAL DATA")
    logger.info("=" * 80)
    
    return {
        'monthly_rankings': monthly_rankings,
        'sensitivity_results': sensitivity_results,
        'summary_df': summary_df,
        'total_pnl': total_pnl
    }


if __name__ == "__main__":
    results = main()

