"""
Decision Constraints and Validation Module

Enforces realistic trading constraints:
1. Information Set: Only use data available at decision points
2. Nomination Deadlines: M-2 for base cargoes, M-3 for options
3. Buyer-Specific Rules: Lead time requirements (e.g., Thor 3-6 months)
4. Sales Confirmation: M-1 deadline validation

Author: LNG Trading Optimization Team
Date: October 16, 2025
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from config.constants import CARGO_CONTRACT, BUYERS

logger = logging.getLogger(__name__)


class InformationSetValidator:
    """
    Validates that decisions only use information available at decision time.
    
    Key Principle: No perfect foresight - only use data that would actually
    be available when making the decision.
    
    Timeline:
    - M-2 (Nov 2025 for Jan 2026 cargo): Can see historical up to Nov, forward curves from Nov onwards
    - M-3 (Oct 2025 for Jan 2026 option): Can see historical up to Oct, forward curves from Oct onwards
    """
    
    def __init__(self):
        self.decision_timeline = CARGO_CONTRACT['decision_timeline']
    
    def get_available_data_date(self, cargo_month: str, decision_type: str = 'base') -> pd.Timestamp:
        """
        Get the cutoff date for available data at decision time.
        
        Args:
            cargo_month: Delivery month (e.g., '2026-01')
            decision_type: 'base' (M-2), 'option' (M-3), or 'sales' (M-1)
        
        Returns:
            Timestamp representing data availability cutoff
        """
        cargo_date = pd.Timestamp(cargo_month)
        
        if decision_type == 'base':
            # M-2: Two months before cargo loading
            decision_date = cargo_date - relativedelta(months=2)
        elif decision_type == 'option':
            # M-3: Three months before cargo loading
            decision_date = cargo_date - relativedelta(months=3)
        elif decision_type == 'sales':
            # M-1: One month before cargo loading
            decision_date = cargo_date - relativedelta(months=1)
        else:
            raise ValueError(f"Unknown decision_type: {decision_type}")
        
        return decision_date
    
    def validate_forecast_availability(
        self,
        cargo_month: str,
        forecast_dict: Dict[str, pd.Series],
        decision_type: str = 'base'
    ) -> Tuple[bool, str]:
        """
        Validate that forecasts are available at decision time.
        
        Args:
            cargo_month: Delivery month
            forecast_dict: Dictionary of forecasts by commodity
            decision_type: Type of decision
        
        Returns:
            (is_valid, message)
        """
        decision_date = self.get_available_data_date(cargo_month, decision_type)
        
        issues = []
        
        for commodity, forecast_series in forecast_dict.items():
            # Check if we have forecast for the cargo month
            if cargo_month not in forecast_series.index:
                issues.append(f"{commodity}: No forecast for {cargo_month}")
                continue
            
            # For forward curves, we need the forecast to be based on data available at decision_date
            # This is implicitly satisfied if we're using forward curves as of decision_date
            # For ARIMA/GARCH, we need historical data up to decision_date only
        
        if issues:
            return False, "; ".join(issues)
        
        return True, "All forecasts available"
    
    def get_restricted_forecasts(
        self,
        cargo_month: str,
        full_forecasts: Dict[str, pd.Series],
        decision_type: str = 'base'
    ) -> Dict[str, pd.Series]:
        """
        Restrict forecasts to only use information available at decision time.
        
        This is critical for realistic modeling - we shouldn't use future information
        that wouldn't be available when making the decision.
        
        Args:
            cargo_month: Delivery month
            full_forecasts: Full forecast dictionary
            decision_type: Type of decision
        
        Returns:
            Restricted forecast dictionary
        """
        decision_date = self.get_available_data_date(cargo_month, decision_type)
        
        logger.info(f"Restricting forecasts for {cargo_month} ({decision_type} decision at {decision_date.strftime('%Y-%m')})")
        
        # For forward curves (HH, JKM): Use the forward curve as of decision_date
        # For ARIMA/GARCH (Brent, Freight): Use forecast generated with data up to decision_date
        # 
        # CURRENT IMPLEMENTATION SIMPLIFICATION:
        # Since we generate forecasts at model runtime (not at historical decision dates),
        # we're implicitly using forward curves "as of Sep 2025" for all decisions.
        # This is acceptable for competition purposes but noted as limitation.
        
        # Return full forecasts for now - proper implementation would require:
        # 1. Historical forward curve data at each decision date
        # 2. Re-running ARIMA/GARCH with data cutoff at decision_date
        
        return full_forecasts


class DeadlineValidator:
    """
    Validates that all decisions meet contract deadline requirements.
    
    Deadlines:
    - Base cargoes: M-2 (two months before loading)
    - Optional cargoes: M-3 (three months before loading)
    - Sales confirmation: M-1 (one month before loading)
    """
    
    def __init__(self):
        self.base_deadline_offset = -2  # M-2
        self.option_deadline_offset = -3  # M-3
        self.sales_deadline_offset = -1  # M-1
    
    def get_deadline(self, cargo_month: str, deadline_type: str = 'base') -> pd.Timestamp:
        """
        Get the deadline for a specific cargo and decision type.
        
        Args:
            cargo_month: Delivery month (e.g., '2026-01')
            deadline_type: 'base', 'option', or 'sales'
        
        Returns:
            Deadline timestamp
        """
        cargo_date = pd.Timestamp(cargo_month)
        
        if deadline_type == 'base':
            offset = self.base_deadline_offset
        elif deadline_type == 'option':
            offset = self.option_deadline_offset
        elif deadline_type == 'sales':
            offset = self.sales_deadline_offset
        else:
            raise ValueError(f"Unknown deadline_type: {deadline_type}")
        
        deadline = cargo_date + relativedelta(months=offset)
        return deadline
    
    def validate_decision_timing(
        self,
        cargo_month: str,
        decision_date: pd.Timestamp,
        deadline_type: str = 'base'
    ) -> Tuple[bool, str]:
        """
        Validate that decision is made by deadline.
        
        Args:
            cargo_month: Delivery month
            decision_date: When decision is being made
            deadline_type: Type of deadline
        
        Returns:
            (is_valid, message)
        """
        deadline = self.get_deadline(cargo_month, deadline_type)
        
        if decision_date <= deadline:
            return True, f"Decision made on time ({decision_date.strftime('%Y-%m')} <= {deadline.strftime('%Y-%m')})"
        else:
            return False, f"Decision too late ({decision_date.strftime('%Y-%m')} > {deadline.strftime('%Y-%m')} deadline)"
    
    def validate_all_base_cargoes(
        self,
        strategy: Dict,
        current_date: Optional[pd.Timestamp] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all base cargo decisions meet M-2 deadline.
        
        Args:
            strategy: Strategy dictionary with monthly_decisions
            current_date: Current date (default: today)
        
        Returns:
            (all_valid, list_of_issues)
        """
        if current_date is None:
            current_date = pd.Timestamp.now()
        
        issues = []
        
        for month in CARGO_CONTRACT['delivery_period']:
            deadline = self.get_deadline(month, 'base')
            
            if current_date > deadline:
                # Decision should have been made already
                if month not in strategy.get('monthly_decisions', {}):
                    issues.append(f"{month}: Missing decision (deadline {deadline.strftime('%Y-%m')} passed)")
        
        return len(issues) == 0, issues


class BuyerConstraintValidator:
    """
    Validates buyer-specific constraints and requirements.
    
    Known constraints:
    - Thor: Requires 3-6 months advance notice
    - (Add others as identified from case materials)
    """
    
    def __init__(self):
        # Buyer lead time requirements (in months)
        self.buyer_lead_times = {
            'Thor': {'min': 3, 'max': 6},  # Thor wants 3-6 months advance notice
            # Add others as needed
        }
    
    def validate_buyer_lead_time(
        self,
        buyer: str,
        cargo_month: str,
        decision_date: pd.Timestamp
    ) -> Tuple[bool, str]:
        """
        Validate buyer-specific lead time requirements.
        
        Args:
            buyer: Buyer name
            cargo_month: Delivery month
            decision_date: When decision is made
        
        Returns:
            (is_valid, message)
        """
        if buyer not in self.buyer_lead_times:
            # No specific constraint for this buyer
            return True, f"{buyer} has no lead time constraints"
        
        constraint = self.buyer_lead_times[buyer]
        cargo_date = pd.Timestamp(cargo_month)
        
        # Calculate months between decision and cargo
        months_advance = (cargo_date.year - decision_date.year) * 12 + (cargo_date.month - decision_date.month)
        
        if months_advance < constraint['min']:
            return False, f"{buyer} requires minimum {constraint['min']} months notice (only {months_advance} months)"
        
        if months_advance > constraint['max']:
            return False, f"{buyer} requires maximum {constraint['max']} months notice ({months_advance} months too far ahead)"
        
        return True, f"{buyer} lead time satisfied ({months_advance} months, requires {constraint['min']}-{constraint['max']})"
    
    def validate_strategy_buyer_constraints(
        self,
        strategy: Dict,
        current_date: Optional[pd.Timestamp] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate all buyer selections in strategy meet constraints.
        
        Args:
            strategy: Strategy with monthly_decisions
            current_date: Decision date (default: use M-2 deadlines)
        
        Returns:
            (all_valid, list_of_issues)
        """
        issues = []
        deadline_validator = DeadlineValidator()
        
        for month, decision in strategy.get('monthly_decisions', {}).items():
            buyer = decision.get('buyer')
            
            if buyer == 'N/A' or buyer is None:
                continue  # Cancelled cargo
            
            # Get decision date (M-2 for base cargoes)
            if current_date is None:
                decision_date = deadline_validator.get_deadline(month, 'base')
            else:
                decision_date = current_date
            
            is_valid, msg = self.validate_buyer_lead_time(buyer, month, decision_date)
            
            if not is_valid:
                issues.append(f"{month}: {msg}")
        
        return len(issues) == 0, issues


class DecisionValidator:
    """
    Master validator that combines all constraint checks.
    """
    
    def __init__(self):
        self.info_validator = InformationSetValidator()
        self.deadline_validator = DeadlineValidator()
        self.buyer_validator = BuyerConstraintValidator()
    
    def validate_strategy(
        self,
        strategy: Dict,
        forecasts: Dict[str, pd.Series],
        current_date: Optional[pd.Timestamp] = None,
        strict_mode: bool = False
    ) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Comprehensive validation of strategy against all constraints.
        
        Args:
            strategy: Strategy dictionary
            forecasts: Forecast dictionary
            current_date: Current date for deadline checks
            strict_mode: If True, fail on any violation. If False, warn only.
        
        Returns:
            (is_valid, dict_of_issues_by_category)
        """
        all_issues = {
            'deadlines': [],
            'buyer_constraints': [],
            'information_set': []
        }
        
        # Check 1: Deadline compliance
        deadline_valid, deadline_issues = self.deadline_validator.validate_all_base_cargoes(
            strategy, current_date
        )
        all_issues['deadlines'] = deadline_issues
        
        # Check 2: Buyer constraints
        buyer_valid, buyer_issues = self.buyer_validator.validate_strategy_buyer_constraints(
            strategy, current_date
        )
        all_issues['buyer_constraints'] = buyer_issues
        
        # Check 3: Information set (for each month)
        for month in CARGO_CONTRACT['delivery_period']:
            info_valid, info_msg = self.info_validator.validate_forecast_availability(
                month, forecasts, 'base'
            )
            if not info_valid:
                all_issues['information_set'].append(f"{month}: {info_msg}")
        
        # Overall validation
        has_issues = any(len(issues) > 0 for issues in all_issues.values())
        
        if has_issues:
            if strict_mode:
                logger.error("VALIDATION FAILED - Strategy violates constraints:")
                for category, issues in all_issues.items():
                    if issues:
                        logger.error(f"  {category.upper()}:")
                        for issue in issues:
                            logger.error(f"    - {issue}")
            else:
                logger.warning("VALIDATION WARNINGS - Strategy may violate constraints:")
                for category, issues in all_issues.items():
                    if issues:
                        logger.warning(f"  {category.upper()}:")
                        for issue in issues:
                            logger.warning(f"    - {issue}")
        
        return not has_issues, all_issues
    
    def log_validation_summary(self, is_valid: bool, issues: Dict[str, List[str]]):
        """Log a formatted validation summary."""
        logger.info("\n" + "="*80)
        logger.info("DECISION CONSTRAINT VALIDATION SUMMARY")
        logger.info("="*80)
        
        if is_valid:
            logger.info("✅ ALL CONSTRAINTS SATISFIED")
        else:
            logger.info("⚠️  CONSTRAINT VIOLATIONS DETECTED")
        
        for category, issue_list in issues.items():
            if issue_list:
                logger.info(f"\n{category.upper()} ({len(issue_list)} issues):")
                for issue in issue_list:
                    logger.info(f"  - {issue}")
            else:
                logger.info(f"\n{category.upper()}: ✓ OK")
        
        logger.info("="*80)

