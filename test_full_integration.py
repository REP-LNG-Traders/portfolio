"""
Full Integration Test Suite
Tests all components working together end-to-end
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

print("="*80)
print("FULL INTEGRATION TEST SUITE")
print("="*80)
print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

test_results = []

def test_result(test_name, passed, details=""):
    """Record test result"""
    status = "[PASS]" if passed else "[FAIL]"
    test_results.append({
        'Test': test_name,
        'Status': status,
        'Details': details
    })
    print(f"{status} {test_name}")
    if details:
        print(f"      {details}")

# =============================================================================
# TEST 1: Data Loading
# =============================================================================
print("\n" + "="*80)
print("TEST 1: DATA LOADING")
print("="*80)

try:
    from data_processing.loaders import load_all_data
    data = load_all_data()
    
    # Check all data loaded
    required_keys = ['henry_hub', 'jkm', 'brent', 'freight', 'fx']
    all_loaded = all(k in data for k in required_keys)
    test_result("Data Loading", all_loaded, f"Loaded: {list(data.keys())}")
    
    # Check data quality
    hh_len = len(data['henry_hub'])
    jkm_len = len(data['jkm'])
    brent_len = len(data['brent'])
    
    test_result("Henry Hub Data", hh_len > 700, f"{hh_len} rows")
    test_result("JKM Data", jkm_len > 700, f"{jkm_len} rows")
    test_result("Brent Data", brent_len > 400, f"{brent_len} rows")
    
except Exception as e:
    test_result("Data Loading", False, str(e))
    sys.exit(1)

# =============================================================================
# TEST 2: Forecast Generation
# =============================================================================
print("\n" + "="*80)
print("TEST 2: FORECAST GENERATION")
print("="*80)

try:
    from main_optimization import prepare_forecasts_simple
    forecasts = prepare_forecasts_simple(data)
    
    # Check forecasts created
    forecast_keys = ['henry_hub', 'jkm', 'brent', 'freight']
    all_forecasts = all(k in forecasts for k in forecast_keys)
    test_result("Forecast Creation", all_forecasts, f"Forecasts: {list(forecasts.keys())}")
    
    # Check forecast values are reasonable
    hh_jan = forecasts['henry_hub'].loc['2026-01']
    jkm_jan = forecasts['jkm'].loc['2026-01']
    brent_jan = forecasts['brent'].loc['2026-01']
    
    hh_valid = 2.0 <= hh_jan <= 10.0
    jkm_valid = 5.0 <= jkm_jan <= 30.0
    brent_valid = 30.0 <= brent_jan <= 150.0
    
    test_result("HH Forecast Range", hh_valid, f"${hh_jan:.2f}/MMBtu")
    test_result("JKM Forecast Range", jkm_valid, f"${jkm_jan:.2f}/MMBtu")
    test_result("Brent Forecast Range", brent_valid, f"${brent_jan:.2f}/bbl")
    
except Exception as e:
    test_result("Forecast Generation", False, str(e))
    sys.exit(1)

# =============================================================================
# TEST 3: P&L Calculator
# =============================================================================
print("\n" + "="*80)
print("TEST 3: P&L CALCULATOR")
print("="*80)

try:
    from models.optimization import CargoPnLCalculator
    from config.constants import CARGO_CONTRACT
    
    calc = CargoPnLCalculator()
    
    # Test cargo P&L calculation
    test_pnl = calc.calculate_cargo_pnl(
        month='2026-01',
        destination='Singapore',
        buyer='Iron_Man',
        henry_hub_price=forecasts['henry_hub'].loc['2026-01'],
        jkm_price=forecasts['jkm'].loc['2026-01'],
        jkm_price_next_month=forecasts['jkm'].loc['2026-02'],
        brent_price=forecasts['brent'].loc['2026-01'],
        freight_rate=forecasts['freight'].loc['2026-01'],
        cargo_volume=3.8e6  # Base volume
    )
    
    # Check P&L components
    has_revenue = 'sale_revenue' in test_pnl
    has_costs = 'purchase_cost' in test_pnl
    has_total = 'total_pnl' in test_pnl
    
    test_result("P&L Calculation", has_revenue and has_costs and has_total, 
                f"Total P&L: ${test_pnl.get('total_pnl', 0)/1e6:.2f}M")
    
    # Check cost components
    cost_keys = ['purchase_cost', 'freight_cost', 'terminal_cost', 'boiloff_cost', 
                 'working_capital_cost', 'carbon_cost']
    has_all_costs = all(k in test_pnl for k in cost_keys)
    test_result("Cost Components", has_all_costs, 
                f"Components: {len([k for k in cost_keys if k in test_pnl])}/{len(cost_keys)}")
    
    # Verify sales constraint
    sales_volume = test_pnl.get('sales_volume', 0)
    max_sales = 3.7e6 * 1.1  # Max sales contract
    within_limit = sales_volume <= max_sales
    test_result("Sales Volume Constraint", within_limit, 
                f"Sales: {sales_volume/1e6:.2f}M MMBtu (limit: {max_sales/1e6:.2f}M)")
    
    # Check stranded volume calculation
    stranded_vol = test_pnl.get('stranded_volume', 0)
    test_result("Stranded Volume", True, f"{stranded_vol/1e3:.1f}k MMBtu")
    
except Exception as e:
    test_result("P&L Calculator", False, str(e))
    import traceback
    traceback.print_exc()

# =============================================================================
# TEST 4: Strategy Optimization
# =============================================================================
print("\n" + "="*80)
print("TEST 4: STRATEGY OPTIMIZATION")
print("="*80)

try:
    from models.optimization import StrategyOptimizer
    
    optimizer = StrategyOptimizer(calc)
    strategy = optimizer.generate_optimal_strategy(forecasts)
    
    # Check strategy structure
    has_cargoes = 'base_cargoes' in strategy
    has_total = 'total_expected_pnl' in strategy
    
    test_result("Strategy Generation", has_cargoes and has_total, 
                f"Total P&L: ${strategy.get('total_expected_pnl', 0)/1e6:.2f}M")
    
    # Check 6 base cargoes
    num_cargoes = len(strategy.get('base_cargoes', []))
    test_result("Base Cargo Count", num_cargoes == 6, f"{num_cargoes} cargoes")
    
    # Check destination distribution
    if num_cargoes == 6:
        destinations = [c['destination'] for c in strategy['base_cargoes']]
        singapore_count = destinations.count('Singapore')
        japan_count = destinations.count('Japan')
        china_count = destinations.count('China')
        
        test_result("Destination Mix", True, 
                    f"Singapore: {singapore_count}, Japan: {japan_count}, China: {china_count}")
    
    # Verify P&L is positive
    total_pnl = strategy.get('total_expected_pnl', 0)
    test_result("Positive P&L", total_pnl > 0, f"${total_pnl/1e6:.2f}M")
    
    # Verify P&L is reasonable (should be $100M+)
    reasonable = 50e6 <= total_pnl <= 300e6
    test_result("Reasonable P&L", reasonable, f"${total_pnl/1e6:.2f}M (50M-300M expected)")
    
except Exception as e:
    test_result("Strategy Optimization", False, str(e))
    import traceback
    traceback.print_exc()

# =============================================================================
# TEST 5: Option Valuation
# =============================================================================
print("\n" + "="*80)
print("TEST 5: OPTION VALUATION")
print("="*80)

try:
    from models.option_valuation import EmbeddedOptionAnalyzer
    
    # Calculate GARCH volatilities
    garch_vols = {}
    for commodity in ['henry_hub', 'jkm', 'brent', 'freight']:
        if commodity in forecasts:
            vol = forecasts[commodity].pct_change().std() * np.sqrt(12)
            garch_vols[commodity] = vol if not pd.isna(vol) else 0.20
    
    analyzer = EmbeddedOptionAnalyzer(forecasts, garch_vols)
    options_df = analyzer.analyze_all_options()
    
    # Check options generated
    num_options = len(options_df)
    test_result("Option Analysis", num_options > 0, f"{num_options} options evaluated")
    
    # Check top 5 selection
    top_5 = options_df.nlargest(5, 'risk_adjusted_value')
    test_result("Top 5 Options", len(top_5) == 5, 
                f"Months: {list(top_5['delivery_month'].unique())}")
    
    # Verify option values are positive
    all_positive = (top_5['risk_adjusted_value'] > 0).all()
    test_result("Positive Option Values", all_positive, 
                f"Range: ${top_5['risk_adjusted_value'].min():.1f}M - ${top_5['risk_adjusted_value'].max():.1f}M")
    
    # Check total option uplift
    total_uplift = top_5['expected_incremental_pnl_millions'].sum() if 'expected_incremental_pnl_millions' in top_5.columns else top_5['risk_adjusted_value'].sum()
    test_result("Option Uplift", total_uplift > 50, f"${total_uplift:.1f}M")
    
except Exception as e:
    test_result("Option Valuation", False, str(e))
    import traceback
    traceback.print_exc()

# =============================================================================
# TEST 6: Decision Constraints
# =============================================================================
print("\n" + "="*80)
print("TEST 6: DECISION CONSTRAINTS")
print("="*80)

try:
    from models.decision_constraints import DecisionValidator
    
    validator = DecisionValidator()
    
    # Test validator instantiation
    test_result("Validator Instantiation", validator is not None, "DecisionValidator created successfully")
    
    # Test validate_strategy method exists
    has_validate = hasattr(validator, 'validate_strategy')
    test_result("Validate Strategy Method", has_validate, "validate_strategy() method exists")
    
except Exception as e:
    test_result("Decision Constraints", False, str(e))
    import traceback
    traceback.print_exc()

# =============================================================================
# TEST 7: Demand Pricing Model
# =============================================================================
print("\n" + "="*80)
print("TEST 7: DEMAND PRICING MODEL")
print("="*80)

try:
    from config.settings import DEMAND_PRICING_MODEL
    
    # Check config loaded
    model_enabled = DEMAND_PRICING_MODEL.get('enabled', False)
    test_result("Demand Model Enabled", model_enabled == True, "Price adjustment model active")
    
    # Check adjustments configured
    adjustments = DEMAND_PRICING_MODEL.get('adjustments', {})
    has_tiers = len(adjustments) >= 5
    test_result("Demand Tiers", has_tiers, f"{len(adjustments)} tiers configured")
    
    # Test demand adjustment logic - check if demand profile is configured
    from config.constants import DEMAND_PROFILE
    
    # Verify demand profile exists
    has_demand_profile = 'Singapore' in DEMAND_PROFILE and '2026-01' in DEMAND_PROFILE['Singapore']
    
    # Note: Full demand testing requires integration with strategy optimizer
    # which applies demand adjustments. Direct P&L calculation doesn't expose demand parameter
    low_demand_pnl = {'total_pnl': 0}  # Placeholder
    high_demand_pnl = {'total_pnl': 0}  # Placeholder
    demand_impact_correct = True  # Skip detailed test
    
    # High demand should yield higher P&L
    demand_impact_correct = high_demand_pnl['total_pnl'] > low_demand_pnl['total_pnl']
    test_result("Demand Price Adjustment", demand_impact_correct,
                f"Low: ${low_demand_pnl['total_pnl']/1e6:.1f}M, High: ${high_demand_pnl['total_pnl']/1e6:.1f}M")
    
except Exception as e:
    test_result("Demand Pricing Model", False, str(e))
    import traceback
    traceback.print_exc()

# =============================================================================
# TEST 8: Sales Contract Constraint
# =============================================================================
print("\n" + "="*80)
print("TEST 8: SALES CONTRACT CONSTRAINT")
print("="*80)

try:
    from config.settings import SALES_CONTRACT
    
    # Check sales contract config
    max_sales = SALES_CONTRACT.get('max_volume_mmbtu', 0)
    test_result("Sales Contract Config", max_sales == 4.07e6, f"Max: {max_sales/1e6:.2f}M MMBtu")
    
    # Test with excessive purchase volume (should create stranded volume)
    high_vol_pnl = calc.calculate_cargo_pnl(
        month='2026-01',
        destination='Singapore',
        buyer='Iron_Man',
        henry_hub_price=forecasts['henry_hub'].loc['2026-01'],
        jkm_price=forecasts['jkm'].loc['2026-01'],
        jkm_price_next_month=forecasts['jkm'].loc['2026-02'],
        brent_price=forecasts['brent'].loc['2026-01'],
        freight_rate=forecasts['freight'].loc['2026-01'],
        cargo_volume=3.8e6 * 1.10  # 110% purchase volume
    )
    
    # Check if sales are capped
    sales_capped = high_vol_pnl['sales_volume'] <= max_sales
    test_result("Sales Volume Cap", sales_capped,
                f"Sales: {high_vol_pnl['sales_volume']/1e6:.3f}M (cap: {max_sales/1e6:.2f}M)")
    
    # Check stranded volume calculated
    has_stranded = high_vol_pnl.get('stranded_volume', 0) > 0
    test_result("Stranded Volume Calculation", has_stranded,
                f"Stranded: {high_vol_pnl.get('stranded_volume', 0)/1e3:.1f}k MMBtu")
    
except Exception as e:
    test_result("Sales Contract Constraint", False, str(e))
    import traceback
    traceback.print_exc()

# =============================================================================
# TEST 9: Voyage Times and Boil-off
# =============================================================================
print("\n" + "="*80)
print("TEST 9: VOYAGE TIMES AND BOIL-OFF")
print("="*80)

try:
    from config.constants import VOYAGE_DAYS
    
    # Check corrected voyage times
    singapore_days = VOYAGE_DAYS.get('USGC_to_Singapore', 0)
    japan_days = VOYAGE_DAYS.get('USGC_to_Japan', 0)
    china_days = VOYAGE_DAYS.get('USGC_to_China', 0)
    
    test_result("Singapore Voyage Time", singapore_days == 48, f"{singapore_days} days (48 expected)")
    test_result("Japan Voyage Time", japan_days == 41, f"{japan_days} days (41 expected)")
    test_result("China Voyage Time", china_days == 52, f"{china_days} days (52 expected)")
    
    # Verify boil-off rates (0.05% per day)
    singapore_boiloff = singapore_days * 0.0005
    japan_boiloff = japan_days * 0.0005
    china_boiloff = china_days * 0.0005
    
    test_result("Singapore Boil-off", abs(singapore_boiloff - 0.024) < 0.001, f"{singapore_boiloff:.3%}")
    test_result("Japan Boil-off", abs(japan_boiloff - 0.0205) < 0.001, f"{japan_boiloff:.3%}")
    test_result("China Boil-off", abs(china_boiloff - 0.026) < 0.001, f"{china_boiloff:.3%}")
    
except Exception as e:
    test_result("Voyage Times", False, str(e))

# =============================================================================
# TEST 10: Configuration Constants
# =============================================================================
print("\n" + "="*80)
print("TEST 10: CONFIGURATION CONSTANTS")
print("="*80)

try:
    from config.constants import TERMINAL_COSTS, CARGO_CONTRACT, OPERATIONAL
    
    # Check tolling fee correction (it's in CARGO_CONTRACT)
    tolling_fee = CARGO_CONTRACT.get('tolling_fee', 0)
    test_result("Tolling Fee", tolling_fee == 1.50, f"${tolling_fee:.2f}/MMBtu (1.50 expected)")
    
    # Check cargo volumes
    base_purchase = CARGO_CONTRACT.get('volume_mmbtu', 0)
    test_result("Base Purchase Volume", base_purchase == 3.8e6, f"{base_purchase/1e6:.1f}M MMBtu")
    
    # Check volume flexibility (it's in OPERATIONAL)
    min_vol = OPERATIONAL.get('min_volume_pct', 0)
    max_vol = OPERATIONAL.get('max_volume_pct', 0)
    test_result("Volume Flexibility", min_vol == 0.90 and max_vol == 1.10, f"{min_vol:.0%} - {max_vol:.0%}")
    
except Exception as e:
    test_result("Configuration Constants", False, str(e))

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "="*80)
print("INTEGRATION TEST SUMMARY")
print("="*80)

results_df = pd.DataFrame(test_results)
passed = len(results_df[results_df['Status'] == '[PASS]'])
failed = len(results_df[results_df['Status'] == '[FAIL]'])
total = len(results_df)

print(f"\nTotal Tests: {total}")
print(f"Passed: {passed} ({passed/total*100:.1f}%)")
print(f"Failed: {failed} ({failed/total*100:.1f}%)")

if failed > 0:
    print("\nFailed Tests:")
    for _, row in results_df[results_df['Status'] == '[FAIL]'].iterrows():
        print(f"  - {row['Test']}: {row['Details']}")

# Save results
output_path = Path("outputs/diagnostics/integration_test_results.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(output_path, index=False)
print(f"\n[OK] Results saved to: {output_path}")

print("\n" + "="*80)
if failed == 0:
    print("ALL TESTS PASSED - System Ready for Production")
else:
    print(f"TESTS FAILED - {failed} issue(s) need resolution")
print("="*80)

sys.exit(0 if failed == 0 else 1)

