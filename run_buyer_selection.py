"""
Run Buyer Selection Framework Analysis

Standalone script to analyze buyer selections using multi-factor scoring.
Generates:
1. Buyer selection matrix CSV
2. Decision rationale text file
3. Sensitivity analysis CSV
4. Summary table for presentation
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging

from models.buyer_selection import (
    BuyerSelectionFramework,
    create_buyer_selection_matrix,
    create_selection_summary_table
)
from config.constants import BUYERS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_sample_buyer_options():
    """
    Generate sample buyer options for demonstration.
    In production, this would come from the optimization module.
    """
    months = ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07']
    
    # Sample data - replace with actual optimization results
    buyer_options_by_month = {}
    
    for month in months:
        options = {}
        
        # Generate realistic margins for each destination/buyer combination
        for destination, buyers in BUYERS.items():
            for buyer in buyers:
                # Base margin varies by destination
                base_margin = {
                    'Singapore': 3.5,
                    'Japan': 4.2,
                    'China': 3.8
                }.get(destination, 3.5)
                
                # Add buyer-specific variation
                buyer_adj = {
                    'Iron_Man': 0.2,
                    'Thor': 0.1,
                    'Hawk_Eye': 0.15,
                    'QuickSilver': -0.1  # Lower margin but BBB credit
                }.get(buyer, 0)
                
                # Add monthly variation
                month_idx = months.index(month)
                month_adj = np.sin(month_idx * 0.5) * 0.3
                
                margin = base_margin + buyer_adj + month_adj
                
                # Calculate P&L (simplified - based on 3.5 million MMBtu cargo)
                cargo_size = 3.5e6  # MMBtu
                pnl = margin * cargo_size
                
                options[(destination, buyer)] = {
                    'margin': margin,
                    'pnl': pnl
                }
        
        buyer_options_by_month[month] = options
    
    return buyer_options_by_month


def main():
    """Run buyer selection analysis."""
    logger.info("=" * 80)
    logger.info("BUYER SELECTION FRAMEWORK ANALYSIS")
    logger.info("=" * 80)
    
    # Create output directory
    output_dir = Path("outputs/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Step 1: Initialize framework
    logger.info("\nStep 1: Initializing buyer selection framework...")
    framework = BuyerSelectionFramework()
    logger.info(f"Weights: {framework.weights}")
    
    # Step 2: Generate buyer options (in production, get from optimization)
    logger.info("\nStep 2: Loading buyer options...")
    buyer_options_by_month = generate_sample_buyer_options()
    logger.info(f"Analyzing {len(buyer_options_by_month)} months")
    
    # Step 3: Rank buyers for each month
    logger.info("\nStep 3: Ranking buyers for each month...")
    monthly_rankings = {}
    for month, options in buyer_options_by_month.items():
        ranked_df = framework.rank_buyers_for_month(month, options)
        monthly_rankings[month] = ranked_df
        
        # Show top 3
        logger.info(f"\n{month} - Top 3 Options:")
        for i, row in ranked_df.head(3).iterrows():
            logger.info(f"  {row['rank']}. {row['buyer']} at {row['destination']}: "
                       f"Score={row['composite_score']:.1f}, "
                       f"Margin=${row['expected_margin']:.2f}/MMBtu, "
                       f"P&L=${row['expected_pnl_millions']:.1f}M")
    
    # Step 4: Create buyer selection matrix CSV
    logger.info("\nStep 4: Creating buyer selection matrix...")
    matrix_path = output_dir / f"buyer_selection_matrix_{timestamp}.csv"
    matrix_df = create_buyer_selection_matrix(monthly_rankings, str(matrix_path))
    logger.info(f"Matrix saved: {matrix_path}")
    
    # Step 5: Generate decision rationales
    logger.info("\nStep 5: Generating decision rationales...")
    rationale_path = output_dir / f"selection_rationale_{timestamp}.txt"
    with open(rationale_path, 'w', encoding='utf-8') as f:
        f.write("BUYER SELECTION DECISION RATIONALES\n")
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
    
    logger.info(f"Rationales saved: {rationale_path}")
    
    # Step 6: Run sensitivity analysis
    logger.info("\nStep 6: Running sensitivity analysis...")
    sensitivity_results = []
    for month, options in buyer_options_by_month.items():
        sensitivity = framework.run_sensitivity_analysis(month, options)
        sensitivity_results.append(sensitivity)
        logger.info(f"  {month}: {sensitivity['robustness_note']}")
    
    # Save sensitivity details
    sensitivity_path = output_dir / f"sensitivity_check_{timestamp}.csv"
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
    logger.info(f"Sensitivity analysis saved: {sensitivity_path}")
    
    # Step 7: Create summary table for presentation
    logger.info("\nStep 7: Creating summary table for presentation...")
    summary_df = create_selection_summary_table(monthly_rankings)
    summary_path = output_dir / f"buyer_selection_summary_{timestamp}.csv"
    summary_df.to_csv(summary_path, index=False)
    
    logger.info("\nSummary Table (PowerPoint-ready):")
    logger.info("\n" + summary_df.to_string(index=False))
    logger.info(f"\nSummary saved: {summary_path}")
    
    # Step 8: Calculate aggregate statistics
    logger.info("\nStep 8: Aggregate Statistics:")
    total_pnl = sum(
        df[df['rank'] == 1]['expected_pnl_millions'].iloc[0]
        for df in monthly_rankings.values()
    )
    logger.info(f"  Total Expected P&L: ${total_pnl:.1f}M")
    
    robust_months = sum(1 for r in sensitivity_results if r['is_robust'])
    logger.info(f"  Robust Selections: {robust_months}/{len(sensitivity_results)} months")
    
    # Credit rating distribution
    selected_ratings = [
        df[df['rank'] == 1]['credit_rating'].iloc[0]
        for df in monthly_rankings.values()
    ]
    rating_counts = pd.Series(selected_ratings).value_counts()
    logger.info(f"  Selected Buyer Credit Ratings:")
    for rating, count in rating_counts.items():
        logger.info(f"    {rating}: {count} months")
    
    logger.info("\n" + "=" * 80)
    logger.info("ANALYSIS COMPLETE")
    logger.info("=" * 80)
    logger.info(f"\nOutputs saved to: {output_dir}/")
    logger.info(f"  1. Buyer selection matrix: buyer_selection_matrix_{timestamp}.csv")
    logger.info(f"  2. Decision rationales: selection_rationale_{timestamp}.txt")
    logger.info(f"  3. Sensitivity analysis: sensitivity_check_{timestamp}.csv")
    logger.info(f"  4. Summary table: buyer_selection_summary_{timestamp}.csv")
    
    return {
        'monthly_rankings': monthly_rankings,
        'sensitivity_results': sensitivity_results,
        'summary_df': summary_df,
        'total_pnl': total_pnl
    }


if __name__ == "__main__":
    results = main()

