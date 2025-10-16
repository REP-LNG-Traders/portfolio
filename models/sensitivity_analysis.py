"""
Sensitivity Analysis Module

Tests robustness of optimization results to parameter changes.

Key Questions for Judges:
1. How sensitive is our strategy to price forecast errors?
2. At what point does our strategy change destinations?
3. What parameters have the biggest impact on P&L?
4. Is our optimal strategy robust or marginal?

Author: LNG Trading Optimization Team
Date: October 2025
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

from models.optimization import CargoPnLCalculator, StrategyOptimizer
from config import (
    CARGO_CONTRACT, VOYAGE_DAYS, OPERATIONAL, BUYERS,
    FREIGHT_SCALING_FACTORS
)

logger = logging.getLogger(__name__)


class SensitivityAnalyzer:
    """
    Performs sensitivity analysis on optimization results.
    
    Tests:
    1. Price sensitivities (HH, JKM, Brent, Freight)
    2. Operational sensitivities (voyage days, boil-off, tolling fee)
    3. Commercial sensitivities (premiums, demand probabilities)
    4. Break-even analysis
    """
    
    def __init__(self, calculator: CargoPnLCalculator = None, optimizer: StrategyOptimizer = None):
        """Initialize analyzer with calculator and optimizer."""
        self.calculator = calculator or CargoPnLCalculator()
        self.optimizer = optimizer or StrategyOptimizer(self.calculator)
    
    def run_price_sensitivity(
        self,
        base_forecasts: Dict[str, pd.Series],
        commodity: str,
        adjustments: List[float] = None
    ) -> pd.DataFrame:
        """
        Test sensitivity to price changes for one commodity.
        
        Args:
            base_forecasts: Base price forecasts
            commodity: 'henry_hub', 'jkm', 'brent', or 'freight'
            adjustments: List of multipliers (e.g., [0.8, 0.9, 1.0, 1.1, 1.2])
            
        Returns:
            DataFrame with adjustment, total_pnl, strategy_changes
        """
        if adjustments is None:
            adjustments = [0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2]
        
        logger.info(f"\nPrice Sensitivity: {commodity}")
        logger.info(f"  Testing {len(adjustments)} scenarios")
        
        results = []
        
        # Get base strategy for comparison
        base_strategy = self.optimizer.generate_optimal_strategy(base_forecasts)
        base_pnl = base_strategy['total_expected_pnl']
        base_decisions = base_strategy['monthly_decisions']
        
        for adj in adjustments:
            # Create adjusted forecasts
            adjusted_forecasts = base_forecasts.copy()
            adjusted_forecasts[commodity] = base_forecasts[commodity] * adj
            
            # Run optimization with adjusted forecasts
            strategy = self.optimizer.generate_optimal_strategy(adjusted_forecasts)
            
            # Count strategy changes
            changes = 0
            for month in CARGO_CONTRACT['delivery_period']:
                base_dest = base_decisions[month]['destination']
                base_buyer = base_decisions[month]['buyer']
                adj_dest = strategy['monthly_decisions'][month]['destination']
                adj_buyer = strategy['monthly_decisions'][month]['buyer']
                
                if base_dest != adj_dest or base_buyer != adj_buyer:
                    changes += 1
            
            results.append({
                'commodity': commodity,
                'adjustment': adj,
                'adjustment_pct': (adj - 1) * 100,
                'price_level': f"{adj:.0%}",
                'total_pnl': strategy['total_expected_pnl'],
                'pnl_change': strategy['total_expected_pnl'] - base_pnl,
                'pnl_change_pct': (strategy['total_expected_pnl'] / base_pnl - 1) * 100,
                'strategy_changes': changes,
                'strategy_robust': changes == 0
            })
        
        return pd.DataFrame(results)
    
    def run_all_price_sensitivities(
        self,
        base_forecasts: Dict[str, pd.Series]
    ) -> Dict[str, pd.DataFrame]:
        """
        Run price sensitivity for all commodities.
        
        Returns:
            Dict with keys: 'henry_hub', 'jkm', 'brent', 'freight'
        """
        logger.info("="*80)
        logger.info("COMPREHENSIVE PRICE SENSITIVITY ANALYSIS")
        logger.info("="*80)
        
        commodities = ['henry_hub', 'jkm', 'brent', 'freight']
        results = {}
        
        for commodity in commodities:
            df = self.run_price_sensitivity(base_forecasts, commodity)
            results[commodity] = df
            
            # Log summary
            base_row = df[df['adjustment'] == 1.0].iloc[0]
            logger.info(f"\n{commodity.upper()} Sensitivity:")
            logger.info(f"  Base P&L: ${base_row['total_pnl']/1e6:.2f}M")
            logger.info(f"  Range: ${df['total_pnl'].min()/1e6:.2f}M to ${df['total_pnl'].max()/1e6:.2f}M")
            logger.info(f"  Strategy changes: {df['strategy_changes'].sum()} total across scenarios")
        
        return results
    
    def run_stress_test_scenarios(
        self,
        base_forecasts: Dict[str, pd.Series]
    ) -> Dict[str, pd.DataFrame]:
        """
        Run stress test scenarios for realistic LNG market events.
        
        Tests:
        1. JKM price spike due to cold snap in Northeast Asia
        2. SLNG outage/capacity constraint (Singapore destination unavailable)
        3. Panama Canal delay (voyage time increases)
        
        Returns:
            Dict with scenario results and strategy adjustments
        """
        logger.info("\n" + "="*80)
        logger.info("STRESS TEST SCENARIOS - LNG MARKET EVENTS")
        logger.info("="*80)
        
        results = {}
        
        # Get base strategy for comparison
        base_strategy = self.optimizer.generate_optimal_strategy(base_forecasts)
        base_pnl = base_strategy['total_expected_pnl']
        base_decisions = base_strategy['monthly_decisions']
        
        logger.info(f"Base Strategy P&L: ${base_pnl/1e6:.2f}M")
        
        # Scenario 1: JKM Price Spike (Cold Snap in Northeast Asia)
        logger.info("\n1. SCENARIO: JKM Price Spike (+$5/MMBtu)")
        logger.info("   Event: Sudden cold snap in Northeast Asia")
        logger.info("   Impact: JKM prices spike due to demand surge")
        
        cold_snap_forecasts = base_forecasts.copy()
        cold_snap_forecasts['jkm'] = base_forecasts['jkm'] + 5.0  # +$5/MMBtu spike
        
        cold_snap_strategy = self.optimizer.generate_optimal_strategy(cold_snap_forecasts)
        
        # Analyze strategy changes
        strategy_changes = []
        for month in CARGO_CONTRACT['delivery_period']:
            base_decision = base_decisions[month]
            new_decision = cold_snap_strategy['monthly_decisions'][month]
            
            if (base_decision['destination'] != new_decision['destination'] or 
                base_decision['buyer'] != new_decision['buyer']):
                strategy_changes.append({
                    'month': month,
                    'base_destination': base_decision['destination'],
                    'new_destination': new_decision['destination'],
                    'base_buyer': base_decision['buyer'],
                    'new_buyer': new_decision['buyer'],
                    'reason': 'JKM price spike favors Japan/China'
                })
        
        results['cold_snap'] = {
            'scenario': 'JKM Price Spike (Cold Snap)',
            'event': 'Sudden cold snap in Northeast Asia',
            'price_impact': '+$5.00/MMBtu JKM spike',
            'base_pnl': base_pnl,
            'scenario_pnl': cold_snap_strategy['total_expected_pnl'],
            'pnl_change': cold_snap_strategy['total_expected_pnl'] - base_pnl,
            'pnl_change_pct': (cold_snap_strategy['total_expected_pnl'] / base_pnl - 1) * 100,
            'strategy_changes': strategy_changes,
            'strategy_changes_count': len(strategy_changes),
            'monthly_decisions': cold_snap_strategy['monthly_decisions']
        }
        
        logger.info(f"   P&L Impact: +${(cold_snap_strategy['total_expected_pnl'] - base_pnl)/1e6:.2f}M")
        logger.info(f"   Strategy Changes: {len(strategy_changes)} months")
        
        # Scenario 2: SLNG Outage (Singapore Unavailable)
        logger.info("\n2. SCENARIO: SLNG Outage/Capacity Constraint")
        logger.info("   Event: SLNG terminal outage or capacity constraint")
        logger.info("   Impact: Singapore destination becomes unavailable")
        
        # Create modified buyer configuration without Singapore
        from config.constants import BUYERS
        limited_buyers = {
            k: v for k, v in BUYERS.items() 
            if v.get('destination', '') != 'Singapore'
        }
        
        # Temporarily modify calculator to exclude Singapore
        original_calculator = self.calculator
        modified_calculator = CargoPnLCalculator()
        modified_calculator.buyers = limited_buyers
        modified_optimizer = StrategyOptimizer(modified_calculator)
        
        slng_outage_strategy = modified_optimizer.generate_optimal_strategy(base_forecasts)
        
        # Analyze forced rerouting
        rerouting_changes = []
        for month in CARGO_CONTRACT['delivery_period']:
            base_decision = base_decisions[month]
            new_decision = slng_outage_strategy['monthly_decisions'][month]
            
            if base_decision['destination'] == 'Singapore':
                rerouting_changes.append({
                    'month': month,
                    'original_destination': base_decision['destination'],
                    'rerouted_to': new_decision['destination'],
                    'original_buyer': base_decision['buyer'],
                    'new_buyer': new_decision['buyer'],
                    'reason': 'Singapore unavailable - forced rerouting'
                })
            elif (base_decision['destination'] != new_decision['destination'] or 
                  base_decision['buyer'] != new_decision['buyer']):
                rerouting_changes.append({
                    'month': month,
                    'original_destination': base_decision['destination'],
                    'rerouted_to': new_decision['destination'],
                    'original_buyer': base_decision['buyer'],
                    'new_buyer': new_decision['buyer'],
                    'reason': 'Cascade effect from Singapore outage'
                })
        
        results['slng_outage'] = {
            'scenario': 'SLNG Terminal Outage',
            'event': 'SLNG terminal outage or capacity constraint',
            'operational_impact': 'Singapore destination unavailable',
            'base_pnl': base_pnl,
            'scenario_pnl': slng_outage_strategy['total_expected_pnl'],
            'pnl_change': slng_outage_strategy['total_expected_pnl'] - base_pnl,
            'pnl_change_pct': (slng_outage_strategy['total_expected_pnl'] / base_pnl - 1) * 100,
            'rerouting_changes': rerouting_changes,
            'rerouting_count': len(rerouting_changes),
            'forced_reroutes': len([c for c in rerouting_changes if c['original_destination'] == 'Singapore']),
            'monthly_decisions': slng_outage_strategy['monthly_decisions']
        }
        
        logger.info(f"   P&L Impact: ${(slng_outage_strategy['total_expected_pnl'] - base_pnl)/1e6:.2f}M")
        logger.info(f"   Forced Reroutes: {len([c for c in rerouting_changes if c['original_destination'] == 'Singapore'])} months")
        
        # Restore original calculator
        self.calculator = original_calculator
        self.optimizer = StrategyOptimizer(original_calculator)
        
        # Scenario 3: Panama Canal Delay (Voyage Time Increase)
        logger.info("\n3. SCENARIO: Panama Canal Delay")
        logger.info("   Event: Vessel stuck at Panama Canal")
        logger.info("   Impact: Voyage time increases by 5 days")
        
        # Create modified voyage days (increase all by 5 days)
        from config.constants import VOYAGE_DAYS
        delayed_voyage_days = {k: v + 5 for k, v in VOYAGE_DAYS.items()}
        
        # Temporarily modify calculator with delayed voyages
        delayed_calculator = CargoPnLCalculator()
        delayed_calculator.voyage_days = delayed_voyage_days
        delayed_optimizer = StrategyOptimizer(delayed_calculator)
        
        canal_delay_strategy = delayed_optimizer.generate_optimal_strategy(base_forecasts)
        
        # Analyze impact of increased voyage costs
        delay_changes = []
        for month in CARGO_CONTRACT['delivery_period']:
            base_decision = base_decisions[month]
            new_decision = canal_delay_strategy['monthly_decisions'][month]
            
            if (base_decision['destination'] != new_decision['destination'] or 
                base_decision['buyer'] != new_decision['buyer']):
                delay_changes.append({
                    'month': month,
                    'base_destination': base_decision['destination'],
                    'new_destination': new_decision['destination'],
                    'base_buyer': base_decision['buyer'],
                    'new_buyer': new_decision['buyer'],
                    'voyage_cost_increase': '5 days additional freight',
                    'reason': 'Increased voyage costs change destination economics'
                })
        
        results['canal_delay'] = {
            'scenario': 'Panama Canal Delay',
            'event': 'Vessel stuck at Panama Canal',
            'operational_impact': '+5 days voyage time',
            'base_pnl': base_pnl,
            'scenario_pnl': canal_delay_strategy['total_expected_pnl'],
            'pnl_change': canal_delay_strategy['total_expected_pnl'] - base_pnl,
            'pnl_change_pct': (canal_delay_strategy['total_expected_pnl'] / base_pnl - 1) * 100,
            'strategy_changes': delay_changes,
            'strategy_changes_count': len(delay_changes),
            'monthly_decisions': canal_delay_strategy['monthly_decisions']
        }
        
        logger.info(f"   P&L Impact: ${(canal_delay_strategy['total_expected_pnl'] - base_pnl)/1e6:.2f}M")
        logger.info(f"   Strategy Changes: {len(delay_changes)} months")
        
        # Restore original calculator
        self.calculator = original_calculator
        self.optimizer = StrategyOptimizer(original_calculator)
        
        # Summary
        logger.info("\n" + "="*80)
        logger.info("STRESS TEST SUMMARY")
        logger.info("="*80)
        
        total_scenarios = len(results)
        total_pnl_impact = sum(result['pnl_change'] for result in results.values())
        total_strategy_changes = sum(result.get('strategy_changes_count', result.get('rerouting_count', 0)) 
                                   for result in results.values())
        
        logger.info(f"Scenarios Tested: {total_scenarios}")
        logger.info(f"Total P&L Impact Range: ${total_pnl_impact/1e6:.2f}M")
        logger.info(f"Total Strategy Changes: {total_strategy_changes}")
        
        # Most/least resilient scenarios
        best_scenario = max(results.values(), key=lambda x: x['pnl_change'])
        worst_scenario = min(results.values(), key=lambda x: x['pnl_change'])
        
        logger.info(f"\nMost Resilient: {best_scenario['scenario']} (+${best_scenario['pnl_change']/1e6:.2f}M)")
        logger.info(f"Least Resilient: {worst_scenario['scenario']} (${worst_scenario['pnl_change']/1e6:.2f}M)")
        
        return results

    def run_spread_sensitivity(
        self,
        base_forecasts: Dict[str, pd.Series],
        spread_type: str = 'jkm_hh'
    ) -> pd.DataFrame:
        """
        Test sensitivity to price spreads (e.g., JKM-HH spread).
        
        This is critical for destination selection:
        - High JKM-HH spread → Favor Japan/China
        - Low JKM-HH spread → Favor Singapore (Brent-linked)
        
        Args:
            base_forecasts: Base price forecasts
            spread_type: 'jkm_hh', 'brent_hh', or 'jkm_brent'
            
        Returns:
            DataFrame with spread levels and optimal destinations
        """
        logger.info(f"\nSpread Sensitivity: {spread_type.upper()}")
        
        results = []
        
        # Define spread adjustments (±$5/MMBtu in $0.50 increments)
        spread_adjustments = np.arange(-5.0, 5.5, 0.5)
        
        for adj in spread_adjustments:
            # Adjust forecasts to change spread
            adjusted_forecasts = base_forecasts.copy()
            
            if spread_type == 'jkm_hh':
                # Increase JKM, decrease HH to widen spread
                adjusted_forecasts['jkm'] = base_forecasts['jkm'] + adj
                adjusted_forecasts['henry_hub'] = base_forecasts['henry_hub'] - adj
            elif spread_type == 'brent_hh':
                adjusted_forecasts['brent'] = base_forecasts['brent'] + adj
                adjusted_forecasts['henry_hub'] = base_forecasts['henry_hub'] - adj
            elif spread_type == 'jkm_brent':
                adjusted_forecasts['jkm'] = base_forecasts['jkm'] + adj
                adjusted_forecasts['brent'] = base_forecasts['brent'] - adj
            
            # Run optimization
            strategy = self.optimizer.generate_optimal_strategy(adjusted_forecasts)
            
            # Count destination choices
            dest_counts = {}
            for month, decision in strategy['monthly_decisions'].items():
                dest = decision['destination']
                dest_counts[dest] = dest_counts.get(dest, 0) + 1
            
            results.append({
                'spread_type': spread_type,
                'spread_adjustment': adj,
                'total_pnl': strategy['total_expected_pnl'],
                'singapore_count': dest_counts.get('Singapore', 0),
                'japan_count': dest_counts.get('Japan', 0),
                'china_count': dest_counts.get('China', 0),
                'cancel_count': dest_counts.get('Cancel', 0),
                'dominant_destination': max(dest_counts, key=dest_counts.get) if dest_counts else 'None'
            })
        
        return pd.DataFrame(results)
    
    def run_operational_sensitivity(
        self,
        base_forecasts: Dict[str, pd.Series]
    ) -> pd.DataFrame:
        """
        Test sensitivity to operational parameters.
        
        Tests:
        1. Freight rates: ±20%
        2. Voyage days: ±2 days
        3. Boil-off rate: ±0.01%/day
        4. Tolling fee: ±$0.50/MMBtu
        
        Returns:
            DataFrame with parameter adjustments and P&L impacts
        """
        logger.info("\nOperational Parameter Sensitivity")
        
        results = []
        
        # Base case
        base_strategy = self.optimizer.generate_optimal_strategy(base_forecasts)
        base_pnl = base_strategy['total_expected_pnl']
        
        # Test 1: Freight rates
        for freight_adj in [0.8, 0.9, 1.0, 1.1, 1.2]:
            adjusted_forecasts = base_forecasts.copy()
            adjusted_forecasts['freight'] = base_forecasts['freight'] * freight_adj
            
            strategy = self.optimizer.generate_optimal_strategy(adjusted_forecasts)
            
            results.append({
                'parameter': 'Freight Rate',
                'adjustment': f"{freight_adj:.0%}",
                'adjustment_value': freight_adj,
                'total_pnl': strategy['total_expected_pnl'],
                'pnl_change': strategy['total_expected_pnl'] - base_pnl,
                'pnl_change_pct': (strategy['total_expected_pnl'] / base_pnl - 1) * 100
            })
        
        # Test 2: Tolling fee (modify CARGO_CONTRACT temporarily)
        # Note: This requires reinitialization - simplified for now
        for tolling_adj in [-0.5, -0.25, 0, 0.25, 0.5]:
            # This is conceptual - actual implementation would need to adjust
            # the calculator's tolling fee parameter
            estimated_impact = tolling_adj * CARGO_CONTRACT['volume_mmbtu'] * 6  # 6 cargoes
            
            results.append({
                'parameter': 'Tolling Fee',
                'adjustment': f"{tolling_adj:+.2f} $/MMBtu",
                'adjustment_value': 2.50 + tolling_adj,
                'total_pnl': base_pnl - estimated_impact,
                'pnl_change': -estimated_impact,
                'pnl_change_pct': (-estimated_impact / base_pnl) * 100
            })
        
        return pd.DataFrame(results)
    
    def find_break_even_points(
        self,
        base_forecasts: Dict[str, pd.Series]
    ) -> Dict[str, float]:
        """
        Find break-even points where strategy decisions change.
        
        For each commodity, find the price level where:
        - Optimal destination changes
        - P&L crosses zero
        - Cancel becomes optimal
        
        Returns:
            Dict with break-even prices for key decision points
        """
        logger.info("\nBreak-Even Analysis")
        
        break_evens = {}
        
        # Get base strategy
        base_strategy = self.optimizer.generate_optimal_strategy(base_forecasts)
        base_decisions = base_strategy['monthly_decisions']
        
        # For each commodity, binary search for break-even
        for commodity in ['henry_hub', 'jkm', 'brent']:
            logger.info(f"\n  Finding break-even for {commodity}...")
            
            # Test if strategy changes between 0.5x and 2.0x
            low, high = 0.5, 2.0
            
            for _ in range(10):  # 10 iterations of binary search
                mid = (low + high) / 2
                
                adjusted_forecasts = base_forecasts.copy()
                adjusted_forecasts[commodity] = base_forecasts[commodity] * mid
                
                strategy = self.optimizer.generate_optimal_strategy(adjusted_forecasts)
                
                # Check if strategy changed
                strategy_changed = False
                for month in CARGO_CONTRACT['delivery_period']:
                    if (strategy['monthly_decisions'][month]['destination'] != 
                        base_decisions[month]['destination']):
                        strategy_changed = True
                        break
                
                if strategy_changed:
                    high = mid
                else:
                    low = mid
            
            break_even_multiplier = (low + high) / 2
            break_evens[commodity] = {
                'multiplier': break_even_multiplier,
                'tolerance': f"±{(break_even_multiplier - 1) * 100:.1f}%"
            }
            
            logger.info(f"    Break-even: {break_even_multiplier:.1%} of base forecast")
        
        return break_evens
    
    def run_tornado_analysis(
        self,
        base_forecasts: Dict[str, pd.Series],
        parameters: List[str] = None
    ) -> pd.DataFrame:
        """
        Tornado diagram analysis: Which parameters have biggest P&L impact?
        
        Tests each parameter at ±10% and ranks by impact magnitude.
        
        Args:
            base_forecasts: Base price forecasts
            parameters: List of parameters to test (default: all major ones)
            
        Returns:
            DataFrame sorted by impact magnitude
        """
        logger.info("\nTornado Analysis: Ranking Parameter Impacts")
        
        if parameters is None:
            parameters = ['henry_hub', 'jkm', 'brent', 'freight']
        
        results = []
        
        # Base case
        base_strategy = self.optimizer.generate_optimal_strategy(base_forecasts)
        base_pnl = base_strategy['total_expected_pnl']
        
        # Test each parameter at ±10%
        for param in parameters:
            # Low case (-10%)
            low_forecasts = base_forecasts.copy()
            low_forecasts[param] = base_forecasts[param] * 0.9
            low_strategy = self.optimizer.generate_optimal_strategy(low_forecasts)
            low_pnl = low_strategy['total_expected_pnl']
            
            # High case (+10%)
            high_forecasts = base_forecasts.copy()
            high_forecasts[param] = base_forecasts[param] * 1.1
            high_strategy = self.optimizer.generate_optimal_strategy(high_forecasts)
            high_pnl = high_strategy['total_expected_pnl']
            
            # Calculate range and impact
            pnl_range = high_pnl - low_pnl
            impact_magnitude = abs(pnl_range)
            
            results.append({
                'parameter': param,
                'base_pnl': base_pnl,
                'low_case_pnl': low_pnl,
                'high_case_pnl': high_pnl,
                'pnl_range': pnl_range,
                'impact_magnitude': impact_magnitude,
                'low_case_change_pct': (low_pnl / base_pnl - 1) * 100,
                'high_case_change_pct': (high_pnl / base_pnl - 1) * 100
            })
        
        # Sort by impact magnitude (descending)
        df = pd.DataFrame(results)
        df = df.sort_values('impact_magnitude', ascending=False)
        
        logger.info("\n  Parameter Impact Ranking:")
        for _, row in df.iterrows():
            logger.info(f"    {row['parameter']:12s}: ±${row['impact_magnitude']/1e6:.2f}M "
                       f"({row['low_case_change_pct']:+.1f}% to {row['high_case_change_pct']:+.1f}%)")
        
        return df


def create_sensitivity_plots(
    sensitivity_results: Dict[str, pd.DataFrame],
    output_dir: Path = Path("outputs/diagnostics/sensitivity")
):
    """
    Create visualization plots for sensitivity analysis.
    
    Creates:
    1. Price sensitivity spider plot
    2. Tornado diagram
    3. Spread sensitivity chart
    4. Strategy robustness heatmap
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"\nCreating sensitivity visualizations...")
    
    # Set style
    sns.set_style("whitegrid")
    
    # Plot 1: Price Sensitivity Lines
    if 'price_sensitivities' in sensitivity_results:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        commodities = ['henry_hub', 'jkm', 'brent', 'freight']
        titles = ['Henry Hub', 'JKM', 'Brent', 'Freight']
        
        for idx, (commodity, title) in enumerate(zip(commodities, titles)):
            ax = axes[idx // 2, idx % 2]
            
            df = sensitivity_results['price_sensitivities'][commodity]
            
            # P&L line
            ax.plot(df['adjustment_pct'], df['total_pnl'] / 1e6, 
                   linewidth=2, marker='o', label='Total P&L')
            
            # Base case line
            ax.axvline(0, color='red', linestyle='--', alpha=0.5, label='Base Case')
            ax.axhline(df[df['adjustment'] == 1.0]['total_pnl'].iloc[0] / 1e6,
                      color='gray', linestyle=':', alpha=0.5)
            
            ax.set_xlabel(f'{title} Price Adjustment (%)')
            ax.set_ylabel('Total P&L ($M)')
            ax.set_title(f'Sensitivity to {title} Prices')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        plt.tight_layout()
        plt.savefig(output_dir / 'price_sensitivities.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"  Saved: price_sensitivities.png")
    
    # Plot 2: Tornado Diagram
    if 'tornado' in sensitivity_results:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        df = sensitivity_results['tornado']
        
        # Calculate bar positions
        y_pos = np.arange(len(df))
        
        # Plot bars (low to base = left, base to high = right)
        base_pnl = df['base_pnl'].iloc[0] / 1e6
        
        left_bars = (df['low_case_pnl'] / 1e6) - base_pnl
        right_bars = (df['high_case_pnl'] / 1e6) - base_pnl
        
        ax.barh(y_pos, right_bars, left=0, height=0.4, 
               color='steelblue', label='High Case (+10%)')
        ax.barh(y_pos, left_bars, left=0, height=0.4,
               color='coral', label='Low Case (-10%)')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(df['parameter'].str.replace('_', ' ').str.title())
        ax.set_xlabel('P&L Change from Base ($M)')
        ax.set_title('Tornado Diagram: Parameter Impact on P&L', fontweight='bold')
        ax.axvline(0, color='black', linewidth=0.8)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'tornado_diagram.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"  Saved: tornado_diagram.png")
    
    # Plot 3: Spread Sensitivity
    if 'spread' in sensitivity_results:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        df = sensitivity_results['spread']
        
        # Plot 1: P&L vs spread
        ax1.plot(df['spread_adjustment'], df['total_pnl'] / 1e6,
                linewidth=2, marker='o', color='steelblue')
        ax1.set_xlabel('Spread Adjustment ($/MMBtu)')
        ax1.set_ylabel('Total P&L ($M)')
        ax1.set_title('P&L vs Price Spread', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.axvline(0, color='red', linestyle='--', alpha=0.5)
        
        # Plot 2: Destination mix vs spread
        ax2.plot(df['spread_adjustment'], df['singapore_count'], 
                label='Singapore', marker='o', linewidth=2)
        ax2.plot(df['spread_adjustment'], df['japan_count'],
                label='Japan', marker='s', linewidth=2)
        ax2.plot(df['spread_adjustment'], df['china_count'],
                label='China', marker='^', linewidth=2)
        
        ax2.set_xlabel('Spread Adjustment ($/MMBtu)')
        ax2.set_ylabel('Number of Cargoes')
        ax2.set_title('Optimal Destination vs Price Spread', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.axvline(0, color='red', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'spread_sensitivity.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"  Saved: spread_sensitivity.png")
    
    # Plot 4: Stress Test Scenarios
    if 'stress_tests' in sensitivity_results:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        stress_data = sensitivity_results['stress_tests']
        
        # Plot 1: P&L Impact Comparison
        scenarios = list(stress_data.keys())
        scenario_names = [stress_data[s]['scenario'] for s in scenarios]
        pnl_changes = [stress_data[s]['pnl_change'] / 1e6 for s in scenarios]
        
        colors = ['green' if x > 0 else 'red' for x in pnl_changes]
        bars = ax1.bar(range(len(scenarios)), pnl_changes, color=colors, alpha=0.7)
        
        ax1.set_xticks(range(len(scenarios)))
        ax1.set_xticklabels([name.replace(' ', '\n') for name in scenario_names], fontsize=9)
        ax1.set_ylabel('P&L Change ($M)')
        ax1.set_title('Stress Test P&L Impact', fontweight='bold')
        ax1.axhline(0, color='black', linewidth=0.8)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars, pnl_changes):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + (0.1 if height > 0 else -0.3),
                    f'${value:.1f}M', ha='center', va='bottom' if height > 0 else 'top')
        
        # Plot 2: Strategy Changes Count
        strategy_changes = []
        for s in scenarios:
            if 'strategy_changes_count' in stress_data[s]:
                strategy_changes.append(stress_data[s]['strategy_changes_count'])
            elif 'rerouting_count' in stress_data[s]:
                strategy_changes.append(stress_data[s]['rerouting_count'])
            else:
                strategy_changes.append(0)
        
        bars2 = ax2.bar(range(len(scenarios)), strategy_changes, color='steelblue', alpha=0.7)
        ax2.set_xticks(range(len(scenarios)))
        ax2.set_xticklabels([name.replace(' ', '\n') for name in scenario_names], fontsize=9)
        ax2.set_ylabel('Strategy Changes')
        ax2.set_title('Strategy Robustness', fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, value in zip(bars2, strategy_changes):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{int(value)}', ha='center', va='bottom')
        
        # Plot 3: Monthly Strategy Changes Heatmap
        months = list(CARGO_CONTRACT['delivery_period'])
        heatmap_data = np.zeros((len(scenarios), len(months)))
        
        for i, scenario in enumerate(scenarios):
            for j, month in enumerate(months):
                # Check if strategy changed for this month/scenario
                if scenario == 'cold_snap' and 'strategy_changes' in stress_data[scenario]:
                    changed = any(c['month'] == month for c in stress_data[scenario]['strategy_changes'])
                elif scenario == 'slng_outage' and 'rerouting_changes' in stress_data[scenario]:
                    changed = any(c['month'] == month for c in stress_data[scenario]['rerouting_changes'])
                elif scenario == 'canal_delay' and 'strategy_changes' in stress_data[scenario]:
                    changed = any(c['month'] == month for c in stress_data[scenario]['strategy_changes'])
                else:
                    changed = False
                
                heatmap_data[i, j] = 1 if changed else 0
        
        im = ax3.imshow(heatmap_data, cmap='RdYlGn_r', aspect='auto')
        ax3.set_xticks(range(len(months)))
        ax3.set_xticklabels([m.split('-')[1] for m in months])  # Show month only
        ax3.set_yticks(range(len(scenarios)))
        ax3.set_yticklabels([s.replace('_', ' ').title() for s in scenarios])
        ax3.set_xlabel('Delivery Month')
        ax3.set_title('Monthly Strategy Changes', fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax3, shrink=0.6)
        cbar.set_label('Strategy Changed', rotation=270, labelpad=15)
        
        # Plot 4: Risk-Return Summary
        # Calculate risk metrics for each scenario
        risk_metrics = []
        for scenario in scenarios:
            pnl_change_pct = stress_data[scenario]['pnl_change_pct']
            strategy_changes = strategy_changes[scenarios.index(scenario)]
            
            # Simple risk score: higher strategy changes = higher risk
            risk_score = strategy_changes / len(months) * 100  # % of months with changes
            
            risk_metrics.append({
                'scenario': scenario,
                'return_pct': pnl_change_pct,
                'risk_score': risk_score
            })
        
        returns = [m['return_pct'] for m in risk_metrics]
        risks = [m['risk_score'] for m in risk_metrics]
        
        scatter = ax4.scatter(risks, returns, s=100, alpha=0.7, c=colors)
        
        for i, (risk, ret) in enumerate(zip(risks, returns)):
            ax4.annotate(scenario_names[i].split()[0],  # First word of scenario name
                        (risk, ret), xytext=(5, 5), textcoords='offset points',
                        fontsize=9)
        
        ax4.set_xlabel('Risk Score (% Strategy Changes)')
        ax4.set_ylabel('Return Impact (%)')
        ax4.set_title('Risk-Return Profile', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.axhline(0, color='black', linewidth=0.8, alpha=0.5)
        ax4.axvline(0, color='black', linewidth=0.8, alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'stress_test_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"  Saved: stress_test_analysis.png")


def save_sensitivity_results(
    results: Dict[str, pd.DataFrame],
    output_path: Path = None
):
    """
    Save sensitivity results to Excel file.
    
    Args:
        results: Dict of DataFrames from sensitivity analysis
        output_path: Path to save Excel file
    """
    if output_path is None:
        output_path = Path("outputs/results/sensitivity_analysis.xlsx")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"\nSaving sensitivity results to Excel...")
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = []
        
        if 'tornado' in results:
            summary_data.append(['Parameter Impact Ranking (±10%)', ''])
            summary_data.append(['Parameter', 'Impact Range ($M)'])
            
            for _, row in results['tornado'].iterrows():
                summary_data.append([
                    row['parameter'].replace('_', ' ').title(),
                    f"${row['impact_magnitude']/1e6:.2f}M"
                ])
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False, header=False)
        
        # Individual sensitivity sheets
        if 'price_sensitivities' in results:
            for commodity, df in results['price_sensitivities'].items():
                sheet_name = commodity.replace('_', ' ').title()[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        if 'tornado' in results:
            results['tornado'].to_excel(writer, sheet_name='Tornado_Analysis', index=False)
        
        if 'spread' in results:
            results['spread'].to_excel(writer, sheet_name='Spread_Sensitivity', index=False)
        
        if 'operational' in results:
            results['operational'].to_excel(writer, sheet_name='Operational_Parameters', index=False)
        
        if 'stress_tests' in results:
            # Create summary sheet for stress tests
            stress_summary_data = []
            stress_data = results['stress_tests']
            
            stress_summary_data.append(['STRESS TEST SCENARIOS SUMMARY', ''])
            stress_summary_data.append(['Scenario', 'P&L Impact ($M)', 'Strategy Changes', 'Risk Level'])
            
            for scenario_key, scenario_data in stress_data.items():
                pnl_impact = scenario_data['pnl_change'] / 1e6
                strategy_changes = scenario_data.get('strategy_changes_count', scenario_data.get('rerouting_count', 0))
                risk_level = 'High' if strategy_changes > 3 else 'Medium' if strategy_changes > 1 else 'Low'
                
                stress_summary_data.append([
                    scenario_data['scenario'],
                    f"${pnl_impact:.2f}M",
                    str(strategy_changes),
                    risk_level
                ])
            
            stress_summary_df = pd.DataFrame(stress_summary_data)
            stress_summary_df.to_excel(writer, sheet_name='Stress_Tests_Summary', index=False, header=False)
            
            # Individual scenario sheets
            for scenario_key, scenario_data in stress_data.items():
                sheet_name = scenario_key.replace('_', ' ').title()[:31]
                
                # Create detailed data for each scenario
                scenario_details = []
                scenario_details.append(['SCENARIO DETAILS', ''])
                scenario_details.append(['Event', scenario_data['event']])
                scenario_details.append(['Impact', scenario_data.get('price_impact', scenario_data.get('operational_impact', ''))])
                scenario_details.append(['Base P&L', f"${scenario_data['base_pnl']/1e6:.2f}M"])
                scenario_details.append(['Scenario P&L', f"${scenario_data['scenario_pnl']/1e6:.2f}M"])
                scenario_details.append(['P&L Change', f"${scenario_data['pnl_change']/1e6:.2f}M"])
                scenario_details.append(['P&L Change %', f"{scenario_data['pnl_change_pct']:.1f}%"])
                scenario_details.append(['', ''])
                
                # Strategy changes
                if 'strategy_changes' in scenario_data:
                    scenario_details.append(['STRATEGY CHANGES', ''])
                    scenario_details.append(['Month', 'From', 'To', 'Reason'])
                    for change in scenario_data['strategy_changes']:
                        scenario_details.append([
                            change['month'],
                            f"{change.get('base_destination', change.get('original_destination', ''))} ({change.get('base_buyer', change.get('original_buyer', ''))})",
                            f"{change.get('new_destination', change.get('rerouted_to', ''))} ({change.get('new_buyer', change.get('new_buyer', ''))})",
                            change['reason']
                        ])
                
                elif 'rerouting_changes' in scenario_data:
                    scenario_details.append(['REROUTING CHANGES', ''])
                    scenario_details.append(['Month', 'From', 'To', 'Reason'])
                    for change in scenario_data['rerouting_changes']:
                        scenario_details.append([
                            change['month'],
                            f"{change['original_destination']} ({change['original_buyer']})",
                            f"{change['rerouted_to']} ({change['new_buyer']})",
                            change['reason']
                        ])
                
                scenario_df = pd.DataFrame(scenario_details)
                scenario_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
    
    logger.info(f"  Saved to: {output_path}")


if __name__ == "__main__":
    # Test/demo
    logging.basicConfig(level=logging.INFO)
    
    logger.info("Sensitivity Analysis Module - Test Mode")
    logger.info("="*80)
    logger.info("\nTo use this module:")
    logger.info("1. Load forecasts from main_optimization.py")
    logger.info("2. Create SensitivityAnalyzer instance")
    logger.info("3. Run desired analyses")
    logger.info("4. Generate plots and Excel outputs")
    logger.info("\nExample:")
    logger.info("""
    from models.sensitivity_analysis import SensitivityAnalyzer
    
    # After running main_optimization.py
    analyzer = SensitivityAnalyzer()
    
    # Run all price sensitivities
    price_sens = analyzer.run_all_price_sensitivities(forecasts)
    
    # Run tornado analysis
    tornado = analyzer.run_tornado_analysis(forecasts)
    
    # Create visualizations
    results = {
        'price_sensitivities': price_sens,
        'tornado': tornado
    }
    create_sensitivity_plots(results)
    save_sensitivity_results(results)
    """)

