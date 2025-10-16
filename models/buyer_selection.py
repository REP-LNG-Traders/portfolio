"""
Buyer Selection Framework - Multi-Factor Scoring System

Implements a transparent, weighted scoring approach to buyer selection based on:
1. Expected Margin (50%)
2. Credit Risk (25%)
3. Demand Confidence (15%)
4. Payment Terms (10%)

This framework provides principled decision-making with clear rationale for judges.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import logging

from config.constants import (
    BUYERS, BUYER_CREDIT_RATINGS, BUYER_DEMAND_PROBABILITIES,
    PAYMENT_TERMS, BUYER_SELECTION_WEIGHTS, CREDIT_SCORES, RISK_FREE_RATE
)

logger = logging.getLogger(__name__)


class BuyerSelectionFramework:
    """
    Multi-factor buyer selection scoring system.
    
    Provides transparent, explainable buyer recommendations based on
    weighted combination of margin, credit, demand, and payment factors.
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize buyer selection framework.
        
        Args:
            weights: Custom weights for factors (default uses config)
        """
        self.weights = weights or BUYER_SELECTION_WEIGHTS
        self.credit_ratings = BUYER_CREDIT_RATINGS
        self.demand_probs = BUYER_DEMAND_PROBABILITIES
        self.payment_terms = PAYMENT_TERMS
        self.credit_scores = CREDIT_SCORES
        
        # Validate weights sum to 1.0
        weight_sum = sum(self.weights.values())
        if not np.isclose(weight_sum, 1.0):
            logger.warning(f"Weights sum to {weight_sum:.3f}, not 1.0. Normalizing...")
            total = sum(self.weights.values())
            self.weights = {k: v/total for k, v in self.weights.items()}
    
    def calculate_margin_score(self, margin: float, all_margins: List[float]) -> float:
        """
        Calculate normalized margin score (0-100).
        
        Args:
            margin: Margin for this buyer ($/MMBtu)
            all_margins: All margins this month for normalization
        
        Returns:
            Score from 0-100
        """
        if len(all_margins) < 2:
            return 100.0  # Only one option
        
        min_margin = min(all_margins)
        max_margin = max(all_margins)
        
        if np.isclose(max_margin, min_margin):
            return 100.0  # All margins equal
        
        # Normalize to 0-100
        score = (margin - min_margin) / (max_margin - min_margin) * 100
        return max(0.0, min(100.0, score))
    
    def calculate_credit_score(self, buyer: str) -> float:
        """
        Calculate credit risk score (0-100).
        
        Args:
            buyer: Buyer name
        
        Returns:
            Score from 0-100 based on credit rating
        """
        rating = self.credit_ratings.get(buyer, 'BBB')  # Default to BBB
        return self.credit_scores.get(rating, 85)  # Default to 85
    
    def calculate_demand_score(self, buyer: str) -> float:
        """
        Calculate demand confidence score (0-100).
        
        Args:
            buyer: Buyer name
        
        Returns:
            Score from 0-100 based on demand probability
        """
        prob = self.demand_probs.get(buyer, 0.25)  # Conservative default
        return prob * 100  # Convert to percentage
    
    def calculate_payment_score(self, destination: str) -> float:
        """
        Calculate payment terms score (0-100).
        
        Args:
            destination: Destination market
        
        Returns:
            Score from 0-100 based on payment terms
        """
        terms = self.payment_terms.get(destination, 'immediate')
        
        if terms == 'immediate':
            return 100.0
        elif terms == '30_days':
            # Apply NPV discount for 30-day terms
            # Discount = 1 - (30/365 * risk_free_rate)
            discount = 1 - (30/365 * RISK_FREE_RATE)
            return discount * 100
        else:
            return 100.0  # Default to immediate
    
    def calculate_composite_score(
        self,
        margin: float,
        all_margins: List[float],
        buyer: str,
        destination: str
    ) -> Dict[str, float]:
        """
        Calculate composite buyer selection score.
        
        Args:
            margin: Expected margin ($/MMBtu)
            all_margins: All margins this month for normalization
            buyer: Buyer name
            destination: Destination market
        
        Returns:
            Dictionary with all scores and composite
        """
        # Calculate individual factor scores
        margin_score = self.calculate_margin_score(margin, all_margins)
        credit_score = self.calculate_credit_score(buyer)
        demand_score = self.calculate_demand_score(buyer)
        payment_score = self.calculate_payment_score(destination)
        
        # Calculate weighted composite score
        composite = (
            margin_score * self.weights['margin'] +
            credit_score * self.weights['credit'] +
            demand_score * self.weights['demand'] +
            payment_score * self.weights['payment']
        )
        
        return {
            'margin_score': margin_score,
            'credit_score': credit_score,
            'demand_score': demand_score,
            'payment_score': payment_score,
            'composite_score': composite,
            'margin': margin,
            'credit_rating': self.credit_ratings.get(buyer, 'BBB'),
            'demand_probability': self.demand_probs.get(buyer, 0.25),
            'payment_terms': self.payment_terms.get(destination, 'immediate')
        }
    
    def rank_buyers_for_month(
        self,
        month: str,
        buyer_options: Dict[str, Dict]
    ) -> pd.DataFrame:
        """
        Rank all buyer options for a given month.
        
        Args:
            month: Month string (e.g., '2026-01')
            buyer_options: Dict of {(destination, buyer): {margin, pnl, ...}}
        
        Returns:
            DataFrame with ranked buyers and scores
        """
        # Extract all margins for normalization
        all_margins = [opt['margin'] for opt in buyer_options.values()]
        
        results = []
        for (destination, buyer), opt_data in buyer_options.items():
            scores = self.calculate_composite_score(
                margin=opt_data['margin'],
                all_margins=all_margins,
                buyer=buyer,
                destination=destination
            )
            
            result = {
                'month': month,
                'destination': destination,
                'buyer': buyer,
                'expected_margin': opt_data['margin'],
                'expected_pnl_millions': opt_data.get('pnl', 0) / 1e6,
                **scores
            }
            results.append(result)
        
        # Create DataFrame and rank
        df = pd.DataFrame(results)
        df = df.sort_values('composite_score', ascending=False)
        df['rank'] = range(1, len(df) + 1)
        
        return df
    
    def generate_selection_rationale(
        self,
        month: str,
        selected_buyer: str,
        selected_destination: str,
        ranked_df: pd.DataFrame
    ) -> str:
        """
        Generate human-readable selection rationale.
        
        Args:
            month: Month string
            selected_buyer: Selected buyer name
            selected_destination: Selected destination
            ranked_df: DataFrame with ranked buyers
        
        Returns:
            Formatted rationale string
        """
        # Get selected buyer row
        selected = ranked_df[
            (ranked_df['buyer'] == selected_buyer) &
            (ranked_df['destination'] == selected_destination)
        ].iloc[0]
        
        # Get runner-up (rank 2)
        runner_up = ranked_df[ranked_df['rank'] == 2].iloc[0] if len(ranked_df) > 1 else None
        
        # Identify top 2 score contributors
        contributions = {
            'Margin': selected['margin_score'] * self.weights['margin'],
            'Credit': selected['credit_score'] * self.weights['credit'],
            'Demand': selected['demand_score'] * self.weights['demand'],
            'Payment': selected['payment_score'] * self.weights['payment']
        }
        top_factors = sorted(contributions.items(), key=lambda x: x[1], reverse=True)[:2]
        
        # Build rationale
        rationale = f"Month {month}: Selected {selected_buyer} ({selected['credit_rating']}) at {selected_destination}\n"
        rationale += f"- Composite Score: {selected['composite_score']:.1f}/100 (Rank #{int(selected['rank'])} of {len(ranked_df)} options)\n"
        rationale += f"- Key Drivers: {top_factors[0][0]} ({top_factors[0][1]:.1f} pts), {top_factors[1][0]} ({top_factors[1][1]:.1f} pts)\n"
        rationale += f"- Expected Margin: ${selected['expected_margin']:.2f}/MMBtu → Total P&L: ${selected['expected_pnl_millions']:.1f}M\n"
        
        # Trade-off analysis
        if selected['rank'] > 1:
            best = ranked_df[ranked_df['rank'] == 1].iloc[0]
            margin_diff = best['expected_margin'] - selected['expected_margin']
            rationale += f"- Trade-off: Accepted ${margin_diff:.2f}/MMBtu lower margin for "
            if best['credit_rating'] != selected['credit_rating']:
                rationale += f"{selected['credit_rating']} vs {best['credit_rating']} credit rating\n"
            else:
                rationale += "better risk-adjusted return\n"
        
        # Runner-up comparison
        if runner_up is not None:
            pnl_diff = selected['expected_pnl_millions'] - runner_up['expected_pnl_millions']
            rationale += f"\nRunner-up: {runner_up['buyer']} (Score: {runner_up['composite_score']:.1f}/100) "
            rationale += f"offered ${abs(pnl_diff):.1f}M {'less' if pnl_diff > 0 else 'more'} P&L\n"
        
        return rationale
    
    def run_sensitivity_analysis(
        self,
        month: str,
        buyer_options: Dict[str, Dict],
        weight_variations: List[Dict[str, float]] = None
    ) -> Dict[str, any]:
        """
        Test robustness of selection under weight variations.
        
        Args:
            month: Month string
            buyer_options: Buyer options dict
            weight_variations: List of weight dicts to test
        
        Returns:
            Dictionary with sensitivity results
        """
        if weight_variations is None:
            # Default: vary credit and demand weights
            weight_variations = [
                {'margin': 0.50, 'credit': 0.20, 'demand': 0.20, 'payment': 0.10},
                {'margin': 0.50, 'credit': 0.25, 'demand': 0.15, 'payment': 0.10},  # Base
                {'margin': 0.50, 'credit': 0.30, 'demand': 0.10, 'payment': 0.10},
                {'margin': 0.50, 'credit': 0.25, 'demand': 0.12, 'payment': 0.13},
                {'margin': 0.50, 'credit': 0.25, 'demand': 0.18, 'payment': 0.07},
            ]
        
        selections = []
        for weights in weight_variations:
            # Create temporary framework with these weights
            temp_framework = BuyerSelectionFramework(weights=weights)
            ranked = temp_framework.rank_buyers_for_month(month, buyer_options)
            top_choice = ranked.iloc[0]
            selections.append({
                'weights': weights,
                'selected_buyer': top_choice['buyer'],
                'selected_destination': top_choice['destination'],
                'composite_score': top_choice['composite_score']
            })
        
        # Check if selection is robust (same across all variations)
        unique_selections = set([(s['selected_buyer'], s['selected_destination']) 
                                 for s in selections])
        
        is_robust = len(unique_selections) == 1
        
        return {
            'month': month,
            'is_robust': is_robust,
            'variations_tested': len(weight_variations),
            'unique_selections': len(unique_selections),
            'selections': selections,
            'robustness_note': (
                f"{month} selection is ROBUST across weight variations"
                if is_robust else
                f"{month} selection is MARGINAL - sensitive to weight changes"
            )
        }


def create_buyer_selection_matrix(
    monthly_rankings: Dict[str, pd.DataFrame],
    output_path: str
) -> pd.DataFrame:
    """
    Create comprehensive buyer selection matrix CSV.
    
    Args:
        monthly_rankings: Dict of {month: ranked_df}
        output_path: Path to save CSV
    
    Returns:
        Combined DataFrame
    """
    all_months = []
    for month, df in monthly_rankings.items():
        df_copy = df.copy()
        df_copy['selected'] = df_copy['rank'] == 1
        all_months.append(df_copy)
    
    combined = pd.concat(all_months, ignore_index=True)
    
    # Reorder columns for clarity
    column_order = [
        'month', 'buyer', 'destination', 'rank',
        'expected_margin', 'credit_rating', 'demand_probability',
        'margin_score', 'credit_score', 'demand_score', 'payment_score',
        'composite_score', 'expected_pnl_millions', 'selected'
    ]
    combined = combined[column_order]
    
    # Save to CSV
    combined.to_csv(output_path, index=False)
    logger.info(f"Buyer selection matrix saved to: {output_path}")
    
    return combined


def create_selection_summary_table(
    monthly_rankings: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """
    Create PowerPoint-ready summary table.
    
    Args:
        monthly_rankings: Dict of {month: ranked_df}
    
    Returns:
        Summary DataFrame
    """
    summary_rows = []
    
    for month in sorted(monthly_rankings.keys()):
        df = monthly_rankings[month]
        selected = df[df['rank'] == 1].iloc[0]
        
        # Generate one-phrase "why"
        if selected['margin_score'] > 90:
            why = "Best margin"
        elif selected['credit_score'] == 100:
            why = "AA credit quality"
        elif selected['demand_score'] > 70:
            why = "High demand confidence"
        else:
            why = "Optimal risk-return balance"
        
        summary_rows.append({
            'Month': month,
            'Selected': selected['buyer'],
            'Destination': selected['destination'],
            'Score': f"{selected['composite_score']:.1f}",
            'Why (1 phrase)': why,
            'P&L ($M)': f"${selected['expected_pnl_millions']:.1f}M"
        })
    
    summary_df = pd.DataFrame(summary_rows)
    return summary_df

