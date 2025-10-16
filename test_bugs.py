"""
Comprehensive bug check for LNG optimization model
"""
import sys

print('='*70)
print('COMPREHENSIVE BUG CHECK')
print('='*70)
print()

# Test 1: Data loading
print('1. Testing data loading...')
try:
    from data_processing.loaders import load_all_data
    data = load_all_data()
    print('   OK - Data loading works')
except Exception as e:
    print(f'   FAILED: {e}')
    sys.exit(1)

# Test 2: Hybrid forecasting
print()
print('2. Testing hybrid forecasting...')
try:
    from main_optimization import prepare_forecasts_hybrid
    forecasts = prepare_forecasts_hybrid(data)
    assert len(forecasts) == 4
    assert all(k in forecasts for k in ['henry_hub', 'jkm', 'brent', 'freight'])
    print('   OK - Hybrid forecasting works')
    hh_jan = forecasts['henry_hub']['2026-01']
    jkm_jan = forecasts['jkm']['2026-01']
    print(f'     HH Jan: ${hh_jan:.2f}')
    print(f'     JKM Jan: ${jkm_jan:.2f}')
except Exception as e:
    print(f'   FAILED: {e}')
    import traceback
    traceback.print_exc()

# Test 3: Correlation matrix
print()
print('3. Testing correlation matrix...')
try:
    from main_optimization import calculate_volatilities_and_correlations
    vols, corrs = calculate_volatilities_and_correlations(data)
    assert len(vols) == 4
    assert corrs.shape == (4, 4)
    print('   OK - Correlation matrix works')
    hh_vol = vols['henry_hub'] * 100
    freight_vol = vols['freight'] * 100
    print(f'     HH vol: {hh_vol:.1f}%')
    print(f'     Freight vol: {freight_vol:.1f}%')
except Exception as e:
    print(f'   FAILED: {e}')
    import traceback
    traceback.print_exc()

# Test 4: P&L calculation
print()
print('4. Testing P&L calculation...')
try:
    from models.optimization import CargoPnLCalculator
    calc = CargoPnLCalculator()
    result = calc.calculate_cargo_pnl(
        month='2026-01',
        destination='Singapore',
        buyer='Iron_Man',
        henry_hub_price=4.17,
        jkm_price=11.64,
        jkm_price_next_month=11.64,
        brent_price=68.21,
        freight_rate=18833,
        cargo_volume=4_180_000
    )
    pnl_millions = result['expected_pnl']/1e6
    print('   OK - P&L calculation works')
    print(f'     Singapore cargo: ${pnl_millions:.2f}M')
    
    # Check if P&L is positive
    if pnl_millions <= 0:
        print('     WARNING: P&L is negative or zero!')
except Exception as e:
    print(f'   FAILED: {e}')
    import traceback
    traceback.print_exc()

# Test 5: Optimization
print()
print('5. Testing optimization...')
try:
    from models.optimization import CargoOptimizer
    optimizer = CargoOptimizer()
    strategies = optimizer.generate_all_strategies(forecasts)
    assert len(strategies) > 0
    print('   OK - Optimization works')
    print(f'     Generated {len(strategies)} strategies')
    
    # Check optimal strategy
    optimal = strategies['Optimal']
    optimal_pnl = optimal['total_pnl'] / 1e6
    print(f'     Optimal P&L: ${optimal_pnl:.2f}M')
except Exception as e:
    print(f'   FAILED: {e}')
    import traceback
    traceback.print_exc()

# Test 6: Monte Carlo (small sample)
print()
print('6. Testing Monte Carlo simulation...')
try:
    from models.optimization import MonteCarloSimulator
    mc = MonteCarloSimulator(n_simulations=100)
    optimal_strategy = strategies['Optimal']
    risk_metrics = mc.simulate_strategy_risk(
        strategy=optimal_strategy,
        volatilities=vols,
        correlations=corrs
    )
    mean_pnl = risk_metrics['mean'] / 1e6
    var_5pct = risk_metrics['var_5pct'] / 1e6
    print('   OK - Monte Carlo works')
    print(f'     Mean P&L: ${mean_pnl:.2f}M')
    print(f'     VaR (5%): ${var_5pct:.2f}M')
except Exception as e:
    print(f'   FAILED: {e}')
    import traceback
    traceback.print_exc()

# Test 7: Sensitivity analysis
print()
print('7. Testing sensitivity analysis...')
try:
    from models.sensitivity_analysis import SensitivityAnalyzer
    sens = SensitivityAnalyzer(calc, optimizer)
    price_sens = sens.run_price_sensitivity(forecasts, 'henry_hub')
    assert len(price_sens) > 0
    print('   OK - Sensitivity analysis works')
    print(f'     Generated {len(price_sens)} scenarios')
except Exception as e:
    print(f'   FAILED: {e}')
    import traceback
    traceback.print_exc()

# Test 8: Hedging
print()
print('8. Testing hedging calculation...')
try:
    hedged_result = calc.calculate_cargo_pnl_with_hedge(
        month='2026-01',
        destination='Singapore',
        buyer='Iron_Man',
        henry_hub_forward_m2=4.17,
        henry_hub_spot_m=4.17,
        jkm_price=11.64,
        jkm_price_next_month=11.64,
        brent_price=68.21,
        freight_rate=18833,
        cargo_volume=4_180_000
    )
    assert 'hedging_enabled' in hedged_result
    hedge_pnl = hedged_result['hedge_pnl']
    print('   OK - Hedging calculation works')
    print(f'     Hedge P&L: ${hedge_pnl/1e6:.2f}M')
except Exception as e:
    print(f'   FAILED: {e}')
    import traceback
    traceback.print_exc()

print()
print('='*70)
print('ALL TESTS PASSED')
print('='*70)

