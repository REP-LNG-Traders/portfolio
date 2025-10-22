"""
Embedded Option Analysis - Real Options Framework

This module implements practical embedded option analysis for the LNG contract's
optional cargoes (up to 5 additional cargoes within Jan-Jun 2026 period, with >3 month nomination).

CONTRACT TERMS:
- Base contract: 6 cargoes (Jan-Jun 2026)
- Optional: Up to 5 ADDITIONAL cargoes within same period if nominated >3 months in advance
- This analysis evaluates Feb-Jun options (5 months) with M-3 decision points

REAL OPTIONS FRAMEWORK:
- Uses Black-Scholes framework adapted for commodity options
- Incorporates GARCH volatility forecasts for realistic pricing
- Implements hierarchical exercise decision framework
- Provides scenario analysis for risk assessment

KEY FEATURES:
1. Intrinsic Value Calculation (Expected P&L at M-3)
2. Time Value Calculation (Black-Scholes with GARCH volatility)
3. Risk-Adjusted Decision Framework (4-level hierarchy)
4. Scenario Analysis (Bull/Base/Bear cases)
5. Integration with main optimization strategy
6. Enforces maximum 5 options limit per contract

Author: LNG Trading Optimization Team
Date: October 2025
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
from scipy.stats import norm
import matplotlib.pyplot as plt
import seaborn as sns

from config.constants import (
    CARGO_CONTRACT, BUYERS, SALES_FORMULAS, DEMAND_PROFILE,
    VOYAGE_DAYS, OPERATIONAL
)
from config.settings import HEDGING_CONFIG

# Set up logging
logger = logging.getLogger(__name__)

class EmbeddedOptionAnalyzer:
    """
    Analyzes embedded options in LNG contract using real options framework.
    
    Contract allows up to 5 additional cargoes within the Jan-Jun 2026 period
    if nominated >3 months in advance (M-3 decision point).
    This class values these options and provides exercise recommendations.
    """
    
    def __init__(self, forecasts: Dict[str, pd.Series], garch_volatilities: Dict[str, float]):
        """
        Initialize option analyzer with forecasts and volatility data.
        
        Args:
            forecasts: Price forecasts from ARIMA+GARCH models
            garch_volatilities: Volatility forecasts from GARCH models
        """
        self.forecasts = forecasts
        self.garch_volatilities = garch_volatilities
        self.risk_free_rate = 0.05  # 5% annual risk-free rate
        self.exercise_threshold = 0.75  # $0.75/MMBtu minimum option value
        self.demand_threshold = 0.50  # 50% minimum demand probability
        
        # CORRECTED: Optional cargo months (all Jan-Jun 2026)
        # Contract structure:
        # - 6 base cargoes (one per month Jan-Jun) - these are FIXED
        # - Up to 5 ADDITIONAL optional cargoes with >3 month notice
        # - Optional cargoes can be in ANY month (multiple per month allowed)
        self.optional_months = [
            '2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06'
        ]
        
        # M-3 decision points (3 months before delivery for optional cargoes)
        # Must decide by M-3 to exercise option
        self.decision_points = {
            '2026-01': '2025-10',  # Oct 2025: Decide on Jan optional cargo
            '2026-02': '2025-11',  # Nov 2025: Decide on Feb optional cargo
            '2026-03': '2025-12',  # Dec 2025: Decide on Mar optional cargo
            '2026-04': '2026-01',  # Jan 2026: Decide on Apr optional cargo
            '2026-05': '2026-02',  # Feb 2026: Decide on May optional cargo
            '2026-06': '2026-03'   # Mar 2026: Decide on Jun optional cargo
        }
        
        self.max_options = 5  # Maximum 5 optional cargoes per contract
        
        # For comprehensive analysis, we evaluate multiple option scenarios per month
        # (e.g., different destination/buyer combinations, different volumes)
        self.options_per_month = 3  # Evaluate top 3 option scenarios per month
    
    def calculate_intrinsic_value(self, delivery_month: str, decision_date: str) -> Dict:
        """
        Calculate intrinsic value of option at M-3 decision point.
        
        Intrinsic Value = MAX(Expected Sale Price - Strike Price - Costs, 0)
        
        Args:
            delivery_month: Month of potential cargo delivery
            decision_date: M-3 decision date
            
        Returns:
            Dict with intrinsic value components
        """
        # Get forecasts for decision date and delivery month
        # For decision dates before our forecast period (Nov-Dec 2025), use earliest available forecast
        hh_strike = self.forecasts['henry_hub'].get(decision_date, self.forecasts['henry_hub'].iloc[0])
        jkm_price = self.forecasts['jkm'].get(delivery_month, self.forecasts['jkm'].iloc[0])
        brent_price = self.forecasts['brent'].get(decision_date, self.forecasts['brent'].iloc[0])
        freight_rate = self.forecasts['freight'].get(delivery_month, self.forecasts['freight'].iloc[0])
        
        # Calculate strike price (HH + tolling fee)
        strike_price = hh_strike + CARGO_CONTRACT['tolling_fee']
        
        # Find best destination/buyer combination
        best_option = None
        best_intrinsic_value = 0
        
        for destination in BUYERS.keys():
            for buyer in BUYERS[destination].keys():
                # Calculate expected sale price
                buyer_info = BUYERS[destination][buyer]
                sales_formula = SALES_FORMULAS[destination]
                
                if sales_formula['type'] == 'brent_based':
                    base_price = brent_price * 0.13  # Brent to LNG conversion
                    premium = buyer_info['premium']
                    terminal_tariff = 0.75  # Default for Singapore
                    sale_price = base_price + premium + terminal_tariff
                else:  # jkm_based
                    sale_price = jkm_price + buyer_info['premium'] + sales_formula['berthing_cost']
                
                # Calculate costs
                voyage_days = VOYAGE_DAYS[f'USGC_to_{destination}']
                freight_cost = freight_rate * voyage_days / CARGO_CONTRACT['volume_mmbtu']
                boil_off_cost = OPERATIONAL['boil_off_rate_per_day'] * voyage_days
                
                total_costs = freight_cost + boil_off_cost
                
                # Intrinsic value
                intrinsic_value = max(sale_price - strike_price - total_costs, 0)
                
                if intrinsic_value > best_intrinsic_value:
                    best_intrinsic_value = intrinsic_value
                    best_option = {
                        'destination': destination,
                        'buyer': buyer,
                        'sale_price': sale_price,
                        'strike_price': strike_price,
                        'costs': total_costs,
                        'intrinsic_value': intrinsic_value
                    }
        
        return best_option
    
    def calculate_time_value(self, delivery_month: str, decision_date: str, 
                           intrinsic_value: float) -> Dict:
        """
        Calculate time value using Black-Scholes framework.
        
        Args:
            delivery_month: Month of potential cargo delivery
            decision_date: M-3 decision date
            intrinsic_value: Intrinsic value from calculate_intrinsic_value
            
        Returns:
            Dict with time value components
        """
        # Time to delivery (3 months = 0.25 years)
        time_to_delivery = 0.25
        
        # Get volatility from GARCH forecasts
        hh_vol = self.garch_volatilities.get('henry_hub', 0.3)  # Default 30%
        jkm_vol = self.garch_volatilities.get('jkm', 0.4)       # Default 40%
        
        # Use average volatility (simplified approach)
        volatility = (hh_vol + jkm_vol) / 2
        
        # Get current prices for Black-Scholes
        hh_price = self.forecasts['henry_hub'].get(decision_date, 0)
        jkm_price = self.forecasts['jkm'].get(delivery_month, 0)
        
        # Use JKM as underlying (simplified - in practice would be more complex)
        S = jkm_price  # Current price
        K = hh_price + CARGO_CONTRACT['tolling_fee']  # Strike price
        r = self.risk_free_rate
        T = time_to_delivery
        sigma = volatility
        
        # Black-Scholes calculation
        if S > 0 and K > 0 and T > 0 and sigma > 0:
            d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
            d2 = d1 - sigma*np.sqrt(T)
            
            # Option value
            option_value = S * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
            time_value = max(option_value - intrinsic_value, 0)
        else:
            # Fallback to simple time value
            time_value = intrinsic_value * 0.1  # 10% of intrinsic value
        
        return {
            'time_value': time_value,
            'volatility': volatility,
            'time_to_delivery': time_to_delivery,
            'd1': d1 if 'd1' in locals() else 0,
            'd2': d2 if 'd2' in locals() else 0
        }
    
    def calculate_demand_probability(self, delivery_month: str, destination: str) -> float:
        """
        Calculate demand probability based on case pack data.
        
        Args:
            delivery_month: Month of potential cargo delivery
            destination: Target destination
            
        Returns:
            Demand probability (0-1)
        """
        # Get demand from DEMAND_PROFILE
        demand_pct = DEMAND_PROFILE.get(destination, {}).get('monthly_demand', {}).get(delivery_month, 1.0)
        
        # Convert to probability (demand > 50% = high probability)
        if demand_pct >= 0.7:
            return 0.9  # High demand
        elif demand_pct >= 0.5:
            return 0.7  # Medium demand
        elif demand_pct >= 0.3:
            return 0.5  # Low demand
        else:
            return 0.3  # Very low demand
    
    def calculate_working_capital_cost(self, delivery_month: str) -> float:
        """
        Calculate working capital cost for option.
        
        Args:
            delivery_month: Month of potential cargo delivery
            
        Returns:
            Working capital cost per MMBtu
        """
        # Opportunity cost of capital tied up for 3 months
        working_capital_rate = 0.05  # 5% annual
        time_factor = 0.25  # 3 months
        
        # Base cost on Henry Hub price
        hh_price = self.forecasts['henry_hub'].get(delivery_month, 4.0)
        working_capital_cost = hh_price * working_capital_rate * time_factor
        
        return working_capital_cost
    
    def evaluate_all_option_scenarios_for_month(self, delivery_month: str) -> List[Dict]:
        """
        Evaluate ALL possible option scenarios (destination/buyer combinations) for a given month.
        
        This allows us to find the best N options across all months, with potentially
        multiple options in the same profitable month.
        
        Args:
            delivery_month: Month of potential cargo delivery
            
        Returns:
            List of all option evaluations for this month, sorted by risk-adjusted value
        """
        decision_date = self.decision_points[delivery_month]
        options = []
        
        # Evaluate every destination/buyer combination
        for destination in BUYERS.keys():
            for buyer in BUYERS[destination].keys():
                option = self.evaluate_option_for_destination_buyer(
                    delivery_month, decision_date, destination, buyer
                )
                if option is not None:
                    options.append(option)
        
        # Sort by risk-adjusted value (descending)
        options.sort(key=lambda x: x['risk_adjusted_value'], reverse=True)
        
        return options
    
    def evaluate_option_for_destination_buyer(
        self, delivery_month: str, decision_date: str, destination: str, buyer: str
    ) -> Dict:
        """
        Evaluate option for a specific destination/buyer combination.
        
        Args:
            delivery_month: Month of potential cargo delivery
            decision_date: M-3 decision date
            destination: Target destination
            buyer: Target buyer
            
        Returns:
            Complete option evaluation or None if not profitable
        """
        # Get forecasts
        hh_strike = self.forecasts['henry_hub'].get(decision_date, self.forecasts['henry_hub'].iloc[0])
        jkm_price = self.forecasts['jkm'].get(delivery_month, self.forecasts['jkm'].iloc[0])
        brent_price = self.forecasts['brent'].get(decision_date, self.forecasts['brent'].iloc[0])
        freight_rate = self.forecasts['freight'].get(delivery_month, self.forecasts['freight'].iloc[0])
        
        # Calculate strike price
        strike_price = hh_strike + CARGO_CONTRACT['tolling_fee']
        
        # Calculate expected sale price
        buyer_info = BUYERS[destination][buyer]
        sales_formula = SALES_FORMULAS[destination]
        
        if sales_formula['type'] == 'brent_based':
            base_price = brent_price * 0.13  # Brent to LNG conversion
            premium = buyer_info['premium']
            terminal_tariff = 0.75  # Default for Singapore
            sale_price = base_price + premium + terminal_tariff
        else:  # jkm_based
            sale_price = jkm_price + buyer_info['premium'] + sales_formula['berthing_cost']
        
        # Calculate costs
        voyage_days = VOYAGE_DAYS[f'USGC_to_{destination}']
        freight_cost = freight_rate * voyage_days / CARGO_CONTRACT['volume_mmbtu']
        boiloff_loss = OPERATIONAL['boil_off_rate_per_day'] * voyage_days * sale_price  # Boil-off cost
        
        # Intrinsic value
        intrinsic_value = max(sale_price - strike_price - freight_cost - boiloff_loss, 0)
        
        # If not profitable, skip
        if intrinsic_value <= 0:
            return None
        
        # Time value
        time_result = self.calculate_time_value(delivery_month, decision_date, intrinsic_value)
        
        # Demand probability
        demand_prob = self.calculate_demand_probability(delivery_month, destination)
        
        # Working capital cost
        working_capital_cost = self.calculate_working_capital_cost(delivery_month)
        
        # Total option value
        total_option_value = intrinsic_value + time_result['time_value']
        risk_adjusted_value = total_option_value * demand_prob - working_capital_cost
        
        # Exercise decision
        exercise_recommendation = self.make_exercise_decision(
            total_option_value, demand_prob, risk_adjusted_value
        )
        
        # Expected incremental P&L
        cargo_volume = CARGO_CONTRACT['volume_mmbtu']
        expected_incremental_pnl = risk_adjusted_value * cargo_volume / 1e6
        
        return {
            'delivery_month': delivery_month,
            'decision_date': decision_date,
            'destination': destination,
            'buyer': buyer,
            'forecasted_hh_strike': hh_strike,
            'expected_sale_price': sale_price,
            'intrinsic_value_per_mmbtu': intrinsic_value,
            'time_value_per_mmbtu': time_result['time_value'],
            'total_option_value_per_mmbtu': total_option_value,
            'demand_probability_pct': demand_prob * 100,
            'risk_adjusted_value': risk_adjusted_value,
            'exercise_recommendation': exercise_recommendation,
            'expected_incremental_pnl_millions': expected_incremental_pnl,
            'reasoning': self.generate_reasoning(total_option_value, demand_prob, risk_adjusted_value, exercise_recommendation),
            'volatility': time_result['volatility'],
            'working_capital_cost': working_capital_cost
        }
    
    def evaluate_option(self, delivery_month: str) -> Dict:
        """
        Evaluate the BEST single embedded option for a month (legacy method).
        
        Args:
            delivery_month: Month of potential cargo delivery
            
        Returns:
            Best option evaluation for this month
        """
        decision_date = self.decision_points[delivery_month]
        
        # Step 1: Calculate intrinsic value
        intrinsic_result = self.calculate_intrinsic_value(delivery_month, decision_date)
        
        if intrinsic_result is None:
            return {
                'delivery_month': delivery_month,
                'decision_date': decision_date,
                'exercise_recommendation': 'NO',
                'reasoning': 'No profitable destination/buyer combination found',
                'total_option_value': 0,
                'intrinsic_value': 0,
                'time_value': 0,
                'demand_probability': 0,
                'risk_adjusted_value': 0,
                'expected_incremental_pnl': 0
            }
        
        # Step 2: Calculate time value
        time_result = self.calculate_time_value(
            delivery_month, decision_date, intrinsic_result['intrinsic_value']
        )
        
        # Step 3: Calculate demand probability
        demand_prob = self.calculate_demand_probability(
            delivery_month, intrinsic_result['destination']
        )
        
        # Step 4: Calculate working capital cost
        working_capital_cost = self.calculate_working_capital_cost(delivery_month)
        
        # Step 5: Calculate total option value
        total_option_value = intrinsic_result['intrinsic_value'] + time_result['time_value']
        risk_adjusted_value = total_option_value * demand_prob - working_capital_cost
        
        # Step 6: Exercise decision (4-level hierarchy)
        exercise_recommendation = self.make_exercise_decision(
            total_option_value, demand_prob, risk_adjusted_value
        )
        
        # Step 7: Calculate expected incremental P&L
        cargo_volume = CARGO_CONTRACT['volume_mmbtu']
        expected_incremental_pnl = risk_adjusted_value * cargo_volume / 1e6  # Convert to millions
        
        return {
            'delivery_month': delivery_month,
            'decision_date': decision_date,
            'destination': intrinsic_result['destination'],
            'buyer': intrinsic_result['buyer'],
            'forecasted_hh_strike': intrinsic_result['strike_price'],
            'expected_sale_price': intrinsic_result['sale_price'],
            'intrinsic_value_per_mmbtu': intrinsic_result['intrinsic_value'],
            'time_value_per_mmbtu': time_result['time_value'],
            'total_option_value_per_mmbtu': total_option_value,
            'demand_probability_pct': demand_prob * 100,
            'risk_adjusted_value': risk_adjusted_value,
            'exercise_recommendation': exercise_recommendation,
            'expected_incremental_pnl_millions': expected_incremental_pnl,
            'reasoning': self.generate_reasoning(
                total_option_value, demand_prob, risk_adjusted_value, exercise_recommendation
            ),
            'volatility': time_result['volatility'],
            'working_capital_cost': working_capital_cost
        }
    
    def make_exercise_decision(self, option_value: float, demand_prob: float, 
                              risk_adjusted_value: float) -> str:
        """
        Make exercise decision using 4-level hierarchy.
        
        LEVEL 1: Financial Hurdle (>$0.75/MMBtu)
        LEVEL 2: Demand Check (>50% demand probability)
        LEVEL 3: Portfolio Constraint (max 5 cargoes)
        LEVEL 4: Risk Management (VaR check)
        
        Args:
            option_value: Total option value per MMBtu
            demand_prob: Demand probability (0-1)
            risk_adjusted_value: Risk-adjusted option value
            
        Returns:
            'YES' or 'NO'
        """
        # LEVEL 1: Financial Hurdle
        if option_value < self.exercise_threshold:
            return 'NO'
        
        # LEVEL 2: Demand Check
        if demand_prob < self.demand_threshold:
            return 'NO'
        
        # LEVEL 3: Portfolio Constraint (handled in main analysis)
        # LEVEL 4: Risk Management (simplified - positive risk-adjusted value)
        if risk_adjusted_value <= 0:
            return 'NO'
        
        return 'YES'
    
    def generate_reasoning(self, option_value: float, demand_prob: float, 
                         risk_adjusted_value: float, recommendation: str) -> str:
        """
        Generate one-sentence reasoning for exercise decision.
        
        Args:
            option_value: Total option value per MMBtu
            demand_prob: Demand probability (0-1)
            risk_adjusted_value: Risk-adjusted option value
            recommendation: Exercise recommendation
            
        Returns:
            One-sentence reasoning
        """
        if recommendation == 'NO':
            if option_value < self.exercise_threshold:
                return f"Option value ${option_value:.2f}/MMBtu below ${self.exercise_threshold} threshold"
            elif demand_prob < self.demand_threshold:
                return f"Demand probability {demand_prob:.0%} below {self.demand_threshold:.0%} threshold"
            else:
                return f"Risk-adjusted value ${risk_adjusted_value:.2f}/MMBtu insufficient"
        else:
            return f"Strong option value ${option_value:.2f}/MMBtu with {demand_prob:.0%} demand probability"
    
    def analyze_all_options(self) -> pd.DataFrame:
        """
        Analyze all embedded options with comprehensive evaluation.
        
        Strategy:
        1. Evaluate ALL destination/buyer combinations for ALL months
        2. Rank ALL options by risk-adjusted value
        3. Select TOP 5 options overall (can be multiple in same month)
        4. Enforces maximum of 5 optional cargoes per contract terms
        
        Returns:
            DataFrame with all option evaluations
        """
        logger.info(f"Analyzing embedded options for {self.optional_months[0]} to {self.optional_months[-1]}...")
        logger.info(f"  Evaluating ALL destination/buyer combinations across all months...")
        
        # Step 1: Generate ALL possible options across all months
        all_options = []
        for month in self.optional_months:
            logger.info(f"  Evaluating all scenarios for {month}...")
            month_options = self.evaluate_all_option_scenarios_for_month(month)
            all_options.extend(month_options)
        
        if not all_options:
            logger.warning("  No profitable options found")
            return pd.DataFrame()
        
        # Step 2: Sort ALL options by risk-adjusted value
        all_options.sort(key=lambda x: x['risk_adjusted_value'], reverse=True)
        
        logger.info(f"  Total profitable options evaluated: {len(all_options)}")
        logger.info(f"  Top option: {all_options[0]['delivery_month']} to {all_options[0]['destination']} "
                   f"({all_options[0]['buyer']}) = ${all_options[0]['expected_incremental_pnl_millions']:.1f}M")
        
        # Step 3: Select TOP 5 options overall
        selected_options = []
        for i, option in enumerate(all_options):
            if len(selected_options) >= self.max_options:
                # Update recommendation to NO for remaining options
                option['exercise_recommendation'] = 'NO'
                option['reasoning'] = f"Ranked #{i+1}, below top {self.max_options} options by value"
            else:
                # Keep original recommendation (should be YES for profitable options)
                if option['risk_adjusted_value'] > 0:
                    option['exercise_recommendation'] = 'YES'
                    selected_options.append(option)
        
        # Create DataFrame
        df = pd.DataFrame(all_options)
        
        # Calculate summary statistics
        total_options_evaluated = len(df)
        options_to_exercise = len(selected_options)
        total_uplift = sum([opt['expected_incremental_pnl_millions'] for opt in selected_options])
        
        # Log exercise distribution by month
        exercise_by_month = {}
        for opt in selected_options:
            month = opt['delivery_month']
            exercise_by_month[month] = exercise_by_month.get(month, 0) + 1
        
        logger.info(f"\n  ✓ Selected {options_to_exercise}/{total_options_evaluated} options (max {self.max_options})")
        logger.info(f"  Distribution by month:")
        for month in self.optional_months:
            count = exercise_by_month.get(month, 0)
            if count > 0:
                logger.info(f"    {month}: {count} option(s)")
        
        # Add summary row
        summary_row = {
            'delivery_month': 'SUMMARY',
            'decision_date': '',
            'destination': '',
            'buyer': '',
            'forecasted_hh_strike': 0,
            'expected_sale_price': 0,
            'intrinsic_value_per_mmbtu': 0,
            'time_value_per_mmbtu': 0,
            'total_option_value_per_mmbtu': 0,
            'demand_probability_pct': 0,
            'risk_adjusted_value': 0,
            'exercise_recommendation': f'{options_to_exercise} of {total_options_evaluated}',
            'expected_incremental_pnl_millions': total_uplift,
            'reasoning': f'Total uplift: ${total_uplift:.1f}M from {options_to_exercise} options (max {self.max_options}, evaluated {total_options_evaluated} scenarios)',
            'volatility': 0,
            'working_capital_cost': 0
        }
        
        df = pd.concat([df, pd.DataFrame([summary_row])], ignore_index=True)
        
        logger.info(f"\n  Option analysis complete: {options_to_exercise} options recommended (max {self.max_options})")
        logger.info(f"  Total expected uplift: ${total_uplift:.1f}M")
        
        return df
    
    def scenario_analysis(self) -> pd.DataFrame:
        """
        Perform scenario analysis (Bull/Base/Bear cases).
        
        Returns:
            DataFrame with scenario results
        """
        logger.info("Performing scenario analysis...")
        
        scenarios = {
            'Bull Case': {'jkm_multiplier': 1.2, 'hh_multiplier': 1.0, 'description': 'JKM +20%, HH flat'},
            'Base Case': {'jkm_multiplier': 1.0, 'hh_multiplier': 1.0, 'description': 'Current forecasts'},
            'Bear Case': {'jkm_multiplier': 0.8, 'hh_multiplier': 1.1, 'description': 'JKM -20%, HH +10%'}
        }
        
        scenario_results = []
        
        for scenario_name, params in scenarios.items():
            # Adjust forecasts for scenario
            original_forecasts = self.forecasts.copy()
            
            # Apply scenario multipliers
            for month in self.optional_months:
                if month in self.forecasts['jkm']:
                    self.forecasts['jkm'][month] *= params['jkm_multiplier']
                if month in self.forecasts['henry_hub']:
                    self.forecasts['henry_hub'][month] *= params['hh_multiplier']
            
            # Analyze options under scenario
            options_df = self.analyze_all_options()
            options_to_exercise = len(options_df[options_df['exercise_recommendation'] == 'YES'])
            total_uplift = options_df[options_df['exercise_recommendation'] == 'YES']['expected_incremental_pnl_millions'].sum()
            
            scenario_results.append({
                'scenario': scenario_name,
                'description': params['description'],
                'options_to_exercise': options_to_exercise,
                'total_uplift_millions': total_uplift,
                'confidence': 'High' if options_to_exercise >= 3 else 'Medium' if options_to_exercise >= 1 else 'Low'
            })
            
            # Restore original forecasts
            self.forecasts = original_forecasts
        
        return pd.DataFrame(scenario_results)
    
    def create_visualization(self, options_df: pd.DataFrame, output_path: str):
        """
        Create bar chart visualization of option values.
        
        Args:
            options_df: DataFrame with option analysis results
            output_path: Path to save visualization
        """
        # Filter out summary row
        plot_df = options_df[options_df['delivery_month'] != 'SUMMARY'].copy()
        
        # Create figure with better styling
        sns.set_style("whitegrid")
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Prepare data
        months = [m.split('-')[1] for m in plot_df['delivery_month']]  # Extract month names
        intrinsic_values = plot_df['intrinsic_value_per_mmbtu']
        time_values = plot_df['time_value_per_mmbtu']
        
        # Create bars with professional colors
        x = np.arange(len(months))
        width = 0.4
        
        bars1 = ax.bar(x - width/2, intrinsic_values, width, label='Intrinsic Value', 
                       color='#2E86AB', alpha=0.85, edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, time_values, width, label='Time Value', 
                       color='#F18F01', alpha=0.85, edgecolor='black', linewidth=1.5)
        
        # Add exercise threshold line
        threshold = self.exercise_threshold
        ax.axhline(y=threshold, color='#E63946', linestyle='--', linewidth=2.5, 
                   label=f'Exercise Threshold (${threshold}/MMBtu)', alpha=0.8)
        
        # Highlight recommended options with different color
        for i, (idx, row) in enumerate(plot_df.iterrows()):
            if row['exercise_recommendation'] == 'YES':
                bars1[i].set_color('#06A77D')
                bars1[i].set_alpha(0.9)
                bars2[i].set_color('#06A77D')
                bars2[i].set_alpha(0.7)
        
        # Customize plot
        ax.set_xlabel('Delivery Month', fontsize=12, fontweight='bold')
        ax.set_ylabel('Option Value ($/MMBtu)', fontsize=12, fontweight='bold')
        ax.set_title('Embedded Option Analysis - Jan-Jun 2026', fontsize=14, fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(months, fontsize=11)
        ax.legend(loc='upper left', frameon=True, shadow=True, fontsize=10)
        ax.grid(True, alpha=0.3, linewidth=0.5)
        
        # Clean up spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1.5)
        ax.spines['bottom'].set_linewidth(1.5)
        
        # Add value labels on bars
        for i, (intrinsic, time) in enumerate(zip(intrinsic_values, time_values)):
            total = intrinsic + time
            ax.text(i, total + 0.08, f'${total:.2f}', ha='center', va='bottom', 
                   fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Visualization saved to {output_path}")
    
    def save_results(self, options_df: pd.DataFrame, scenarios_df: pd.DataFrame, 
                    output_dir: str = 'outputs/results'):
        """
        Save all results to CSV files.
        
        Args:
            options_df: Options analysis DataFrame
            scenarios_df: Scenarios analysis DataFrame
            output_dir: Output directory
        """
        from pathlib import Path
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save options analysis
        options_file = output_path / f'embedded_option_analysis_{timestamp}.csv'
        options_df.to_csv(options_file, index=False)
        logger.info(f"Options analysis saved to {options_file}")
        
        # Save scenario analysis
        scenarios_file = output_path / f'option_scenarios_{timestamp}.csv'
        scenarios_df.to_csv(scenarios_file, index=False)
        logger.info(f"Scenario analysis saved to {scenarios_file}")
        
        # Create visualization
        viz_file = output_path / f'option_value_by_month_{timestamp}.png'
        self.create_visualization(options_df, str(viz_file))
        
        return {
            'options_file': str(options_file),
            'scenarios_file': str(scenarios_file),
            'visualization_file': str(viz_file)
        }


def run_embedded_option_analysis(forecasts: Dict[str, pd.Series], 
                                garch_volatilities: Dict[str, float]) -> Dict:
    """
    Run complete embedded option analysis.
    
    Args:
        forecasts: Price forecasts from ARIMA+GARCH models
        garch_volatilities: Volatility forecasts from GARCH models
        
    Returns:
        Dict with analysis results and file paths
    """
    logger.info("Starting embedded option analysis...")
    
    # Initialize analyzer
    analyzer = EmbeddedOptionAnalyzer(forecasts, garch_volatilities)
    
    # Analyze all options
    options_df = analyzer.analyze_all_options()
    
    # Perform scenario analysis
    scenarios_df = analyzer.scenario_analysis()
    
    # Save results
    file_paths = analyzer.save_results(options_df, scenarios_df)
    
    # Extract summary statistics
    summary_options = options_df[options_df['exercise_recommendation'] == 'YES']
    total_options = len(options_df[options_df['delivery_month'] != 'SUMMARY'])
    options_to_exercise = len(summary_options)
    total_uplift = summary_options['expected_incremental_pnl_millions'].sum()
    
    results = {
        'total_options_available': total_options,
        'options_to_exercise': options_to_exercise,
        'total_expected_uplift_millions': total_uplift,
        'confidence': 'High' if options_to_exercise >= 3 else 'Medium' if options_to_exercise >= 1 else 'Low',
        'file_paths': file_paths,
        'options_df': options_df,
        'scenarios_df': scenarios_df
    }
    
    logger.info(f"Embedded option analysis complete:")
    logger.info(f"  - {options_to_exercise}/{total_options} options recommended")
    logger.info(f"  - Total expected uplift: ${total_uplift:.1f}M")
    logger.info(f"  - Confidence: {results['confidence']}")
    
    return results


if __name__ == "__main__":
    # Test the module
    print("Embedded Option Analysis Module")
    print("This module provides real options valuation for LNG contract embedded options.")
    print("Use run_embedded_option_analysis() function to perform complete analysis.")
