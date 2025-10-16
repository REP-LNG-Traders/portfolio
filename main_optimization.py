"""
Main execution script for LNG cargo optimization.

This script:
1. Loads competition data
2. Generates price forecasts
3. Optimizes cargo routing
4. Exports results
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('optimization.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import modules
from src.data_loader import load_all_data
from src.cargo_optimization import (
    CargoPnLCalculator, StrategyOptimizer,
    MonteCarloRiskAnalyzer, ScenarioAnalyzer
)
from config import CARGO_CONTRACT


def prepare_forecasts_simple(data: dict) -> Dict[str, pd.Series]:
    """
    Prepare price forecasts for Jan-Jul 2026.
    
    Approach:
    - HH & JKM: Use forward curves
    - Brent: Use latest historical value (simple assumption)
    - Freight: Use average of recent historical values
    
    Returns:
        Dict with keys ['henry_hub', 'jkm', 'brent', 'freight']
        Each value is pd.Series indexed by month string ('2026-01', etc.)
    """
    logger.info("="*80)
    logger.info("PREPARING PRICE FORECASTS")
    logger.info("="*80)
    
    # Months we need forecasts for (Jan-Jul for M+1 pricing)
    months = pd.date_range('2026-01', '2026-07', freq='MS')
    
    forecasts = {}
    
    # Henry Hub: Use forward curve
    logger.info("\n1. Henry Hub: Using forward curve...")
    hh_fwd = data['henry_hub']['HH_Forward'].dropna()
    
    hh_forecast_dict = {}
    for month in months:
        # Get closest forward contract
        closest_val = hh_fwd.asof(month)
        if pd.isna(closest_val):
            # Use last available
            closest_val = hh_fwd.iloc[-1]
        hh_forecast_dict[month.strftime('%Y-%m')] = closest_val
    
    forecasts['henry_hub'] = pd.Series(hh_forecast_dict, name='henry_hub')
    
    logger.info(f"   HH Forecast range: ${forecasts['henry_hub'].min():.2f} - ${forecasts['henry_hub'].max():.2f}/MMBtu")
    logger.info(f"   Jan 2026: ${forecasts['henry_hub']['2026-01']:.2f}/MMBtu")
    
    # JKM: Use forward curve
    logger.info("\n2. JKM: Using forward curve...")
    jkm_fwd = data['jkm']['JKM_Forward'].dropna()
    
    jkm_forecast_dict = {}
    for month in months:
        closest_val = jkm_fwd.asof(month)
        if pd.isna(closest_val):
            closest_val = jkm_fwd.iloc[-1]
        jkm_forecast_dict[month.strftime('%Y-%m')] = closest_val
    
    forecasts['jkm'] = pd.Series(jkm_forecast_dict, name='jkm')
    
    logger.info(f"   JKM Forecast range: ${forecasts['jkm'].min():.2f} - ${forecasts['jkm'].max():.2f}/MMBtu")
    logger.info(f"   Jan 2026: ${forecasts['jkm']['2026-01']:.2f}/MMBtu")
    
    # Brent: Use latest historical value
    logger.info("\n3. Brent: Using latest historical value...")
    brent_latest = data['brent']['Brent'].iloc[-1]
    
    brent_forecast_dict = {month.strftime('%Y-%m'): brent_latest for month in months}
    forecasts['brent'] = pd.Series(brent_forecast_dict, name='brent')
    
    logger.info(f"   Brent Forecast: ${forecasts['brent']['2026-01']:.2f}/bbl (constant)")
    
    # Freight: Use average of recent historical
    logger.info("\n4. Freight: Using recent historical average...")
    freight_recent = data['freight']['Freight'].iloc[-30:].mean()  # Last 30 days
    
    freight_forecast_dict = {month.strftime('%Y-%m'): freight_recent for month in months}
    forecasts['freight'] = pd.Series(freight_forecast_dict, name='freight')
    
    logger.info(f"   Freight Forecast: ${forecasts['freight']['2026-01']:.0f}/day (constant)")
    
    logger.info("\n" + "="*80)
    logger.info("FORECAST PREPARATION COMPLETE")
    logger.info("="*80)
    
    return forecasts


def prepare_forecasts_arima_garch(data: dict) -> Dict[str, pd.Series]:
    """
    Prepare price forecasts using ARIMA+GARCH for Brent and Freight,
    forward curves for Henry Hub and JKM.
    
    Forecasting Strategy (explained in config.py):
    - Henry Hub & JKM: Use market forward curves (superior to modeling)
    - Brent & Freight: Use ARIMA+GARCH (no forward curves available)
    
    Returns:
        Dict with keys ['henry_hub', 'jkm', 'brent', 'freight']
        Each value is pd.Series indexed by month string ('2026-01', etc.)
    """
    from src.forecasting import (
        test_stationarity, 
        fit_arima_model, fit_garch_model, generate_simple_forecast
    )
    from config import (
        CARGO_FORECASTING_METHOD, CARGO_ARIMA_GARCH_CONFIG,
        ARIMA_CONFIG, GARCH_CONFIG
    )
    
    logger.info("="*80)
    logger.info("PREPARING PRICE FORECASTS (ARIMA+GARCH INTEGRATION)")
    logger.info("="*80)
    
    # Target months: Jan-Jul 2026 (need Jul for JKM M+1 pricing)
    months = pd.date_range('2026-01', '2026-07', freq='MS')
    forecasts = {}
    garch_volatilities = {}  # Store GARCH volatilities for Monte Carlo
    
    # Process each commodity
    for commodity in ['henry_hub', 'jkm', 'brent', 'freight']:
        logger.info(f"\n{'='*80}")
        logger.info(f"COMMODITY: {commodity.upper().replace('_', ' ')}")
        logger.info(f"{'='*80}")
        
        method_config = CARGO_FORECASTING_METHOD[commodity]
        method = method_config['method']
        reason = method_config['reason']
        
        logger.info(f"Method: {method.upper()}")
        logger.info(f"Reason: {reason}")
        
        if method == 'forward_curve':
            # ================================================================
            # USE FORWARD CURVE (Henry Hub & JKM)
            # ================================================================
            logger.info(f"\nUsing forward curve for {commodity}...")
            
            if commodity == 'henry_hub':
                fwd_data = data['henry_hub']['HH_Forward'].dropna()
            elif commodity == 'jkm':
                fwd_data = data['jkm']['JKM_Forward'].dropna()
            
            forecast_dict = {}
            for month in months:
                closest_val = fwd_data.asof(month)
                if pd.isna(closest_val):
                    closest_val = fwd_data.iloc[-1]
                forecast_dict[month.strftime('%Y-%m')] = closest_val
            
            forecasts[commodity] = pd.Series(forecast_dict, name=commodity)
            
            logger.info(f"  Forecast range: ${forecasts[commodity].min():.2f} - ${forecasts[commodity].max():.2f}")
            logger.info(f"  Jan 2026: ${forecasts[commodity]['2026-01']:.2f}")
            
        elif method == 'arima_garch':
            # ================================================================
            # USE ARIMA+GARCH (Brent & Freight)
            # ================================================================
            logger.info(f"\nUsing ARIMA+GARCH for {commodity}...")
            
            # Get historical data
            if commodity == 'brent':
                hist_data = data['brent']['Brent'].dropna()
                unit = '$/bbl'
            elif commodity == 'freight':
                hist_data = data['freight']['Freight'].dropna()
                unit = '$/day'
            
            # Resample to monthly (use last value of each month)
            monthly_data = hist_data.resample('MS').last().dropna()
            
            logger.info(f"  Historical data: {len(hist_data)} daily observations")
            logger.info(f"  Monthly data: {len(monthly_data)} months ({len(monthly_data)/12:.1f} years)")
            logger.info(f"  Date range: {monthly_data.index[0].date()} to {monthly_data.index[-1].date()}")
            
            # Check data sufficiency
            min_months = CARGO_ARIMA_GARCH_CONFIG['min_months_required']
            if len(monthly_data) < min_months:
                if CARGO_ARIMA_GARCH_CONFIG['warn_if_below_minimum']:
                    logger.warning(f"  ⚠️  WARNING: Only {len(monthly_data)} months available (ideal: {min_months}+)")
                    logger.warning(f"      Proceeding anyway - acceptable for competition purposes")
            
            try:
                # ============================================================
                # STEP 1: FIT ARIMA MODEL
                # ============================================================
                logger.info(f"\n  Step 1: Fitting ARIMA model...")
                
                # Test stationarity (returns dict with 'd_recommended')
                stationarity_result = test_stationarity(monthly_data, name=commodity)
                d_order = stationarity_result['d_recommended']
                
                logger.info(f"    Using differencing order d={d_order}")
                
                # Fit ARIMA with grid search
                arima_model, arima_info = fit_arima_model(
                    monthly_data,
                    market_name=commodity,
                    d=d_order,
                    max_p=ARIMA_CONFIG['max_p'],
                    max_q=ARIMA_CONFIG['max_q']
                )
                
                if arima_model is None or not arima_info.get('success', False):
                    raise ValueError(f"ARIMA fitting failed: {arima_info.get('error', 'Unknown error')}")
                
                arima_order = arima_info['order']
                logger.info(f"    ✓ ARIMA{arima_order} fitted successfully")
                logger.info(f"      AIC: {arima_info['aic']:.2f}, BIC: {arima_info['bic']:.2f}")
                
                # ============================================================
                # STEP 2: FIT GARCH MODEL ON RESIDUALS
                # ============================================================
                logger.info(f"\n  Step 2: Fitting GARCH model...")
                
                residuals = arima_model.resid
                
                # Fit GARCH
                garch_model, garch_vol, garch_info = fit_garch_model(
                    residuals,
                    market_name=commodity,
                    p=GARCH_CONFIG['default_p'],
                    q=GARCH_CONFIG['default_q']
                )
                
                if garch_model is not None and garch_info.get('success', False):
                    garch_order = (garch_info['p'], garch_info['q'])
                    logger.info(f"    ✓ GARCH{garch_order} fitted successfully")
                    logger.info(f"      Annual volatility: {garch_vol:.2%}")
                    
                    # Store GARCH volatility for Monte Carlo
                    garch_volatilities[commodity] = garch_vol
                else:
                    logger.warning(f"    ⚠️  GARCH fitting failed: {garch_info.get('error', 'Unknown error')}")
                    logger.warning(f"       Will use ARIMA-only forecasts")
                    garch_model = None
                
                # ============================================================
                # STEP 3: GENERATE FORECASTS
                # ============================================================
                logger.info(f"\n  Step 3: Generating {CARGO_ARIMA_GARCH_CONFIG['forecast_months']}-month forecast...")
                
                # ARIMA forecast
                horizon_months = CARGO_ARIMA_GARCH_CONFIG['forecast_months']
                arima_forecast_df = generate_simple_forecast(
                    arima_model, 
                    horizon=horizon_months,
                    confidence_level=0.95
                )
                
                # Create forecast series for target months
                forecast_dict = {}
                for i, month in enumerate(months):
                    month_str = month.strftime('%Y-%m')
                    forecast_dict[month_str] = arima_forecast_df['forecast'].iloc[i]
                
                forecasts[commodity] = pd.Series(forecast_dict, name=commodity)
                
                logger.info(f"    ✓ Forecast complete")
                logger.info(f"      Range: {forecasts[commodity].min():.2f} - {forecasts[commodity].max():.2f} {unit}")
                logger.info(f"      Jan 2026: {forecasts[commodity]['2026-01']:.2f} {unit}")
                logger.info(f"      Jul 2026: {forecasts[commodity]['2026-07']:.2f} {unit}")
                
                # ============================================================
                # STEP 4: SAVE DIAGNOSTICS (if configured)
                # ============================================================
                if CARGO_ARIMA_GARCH_CONFIG['save_diagnostics']:
                    logger.info(f"\n  Step 4: Saving diagnostics...")
                    
                    # Create diagnostics directory
                    diag_dir = Path("outputs/diagnostics/arima_garch")
                    diag_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Save forecast plot
                    plt.figure(figsize=(12, 6))
                    
                    # Historical
                    plt.plot(monthly_data.index, monthly_data.values, 
                            label='Historical', color='blue', linewidth=1.5)
                    
                    # Forecast
                    forecast_dates = pd.date_range(monthly_data.index[-1] + pd.DateOffset(months=1),
                                                   periods=horizon_months, freq='MS')
                    plt.plot(forecast_dates, arima_forecast_df['forecast'].values,
                            label='ARIMA+GARCH Forecast', color='red', linewidth=2)
                    
                    # Confidence intervals
                    plt.fill_between(forecast_dates, 
                                    arima_forecast_df['lower'].values,
                                    arima_forecast_df['upper'].values,
                                    alpha=0.3, color='red', label='95% CI')
                    
                    plt.axvline(monthly_data.index[-1], color='black', 
                               linestyle='--', alpha=0.5, label='Forecast Start')
                    plt.xlabel('Date')
                    plt.ylabel(f'Price ({unit})')
                    plt.title(f'{commodity.upper().replace("_", " ")} - ARIMA+GARCH Forecast')
                    plt.legend()
                    plt.grid(alpha=0.3)
                    plt.tight_layout()
                    
                    plot_file = diag_dir / f"{commodity}_forecast.png"
                    plt.savefig(plot_file, dpi=150)
                    plt.close()
                    
                    logger.info(f"      Saved plot: {plot_file}")
                
            except Exception as e:
                logger.error(f"  ✗ ARIMA+GARCH failed for {commodity}: {e}")
                logger.info(f"    Falling back to simple method...")
                
                # Fallback to latest value (simple approach)
                latest_value = monthly_data.iloc[-1]
                forecast_dict = {month.strftime('%Y-%m'): latest_value for month in months}
                forecasts[commodity] = pd.Series(forecast_dict, name=commodity)
                
                logger.info(f"      Fallback: Using latest value = {latest_value:.2f} {unit}")
    
    logger.info("\n" + "="*80)
    logger.info("FORECAST PREPARATION COMPLETE")
    logger.info("="*80)
    
    logger.info("\nForecast Summary:")
    for commodity in ['henry_hub', 'jkm', 'brent', 'freight']:
        method = CARGO_FORECASTING_METHOD[commodity]['method']
        jan_val = forecasts[commodity]['2026-01']
        jul_val = forecasts[commodity]['2026-07']
        logger.info(f"  {commodity:12s} ({method:15s}): Jan=${jan_val:7.2f}  Jul=${jul_val:7.2f}")
    
    return forecasts


def calculate_volatilities_and_correlations(data: dict) -> tuple:
    """
    Calculate historical volatilities and correlations for Monte Carlo.
    
    Returns:
        (volatilities_dict, correlation_matrix)
    """
    logger.info("\nCalculating volatilities and correlations...")
    
    volatilities = {}
    
    # Henry Hub
    hh_returns = data['henry_hub']['HH_Historical'].pct_change().dropna()
    volatilities['henry_hub'] = hh_returns.std() * np.sqrt(252)  # Annualized (daily data)
    
    # JKM
    jkm_returns = data['jkm']['JKM_Historical'].pct_change().dropna()
    volatilities['jkm'] = jkm_returns.std() * np.sqrt(252)
    
    # Brent
    brent_returns = data['brent']['Brent'].pct_change().dropna()
    volatilities['brent'] = brent_returns.std() * np.sqrt(252)
    
    # Freight
    freight_returns = data['freight']['Freight'].pct_change().dropna()
    volatilities['freight'] = freight_returns.std() * np.sqrt(252)
    
    # Calculate correlation matrix
    returns_df = pd.DataFrame({
        'henry_hub': data['henry_hub']['HH_Historical'].pct_change(),
        'jkm': data['jkm']['JKM_Historical'].pct_change(),
        'brent': data['brent']['Brent'].pct_change(),
        'freight': data['freight']['Freight'].pct_change()
    }).dropna()
    
    correlations = returns_df.corr()
    
    logger.info("  Volatilities (annualized):")
    for commodity, vol in volatilities.items():
        logger.info(f"    {commodity:12s}: {vol:.1%}")
    
    return volatilities, correlations


def save_results(
    strategies: Dict,
    monte_carlo_results: Dict = None,
    scenario_results: Dict = None,
    output_dir: Path = Path("outputs/results")
):
    """Save optimization results to Excel files."""
    logger.info("\n" + "="*80)
    logger.info("SAVING RESULTS")
    logger.info("="*80)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Strategies comparison
    logger.info("\n1. Strategies Comparison...")
    strategies_data = []
    for name, strategy in strategies.items():
        strategies_data.append({
            'Strategy': name,
            'Description': strategy['description'],
            'Total_Expected_PnL_USD': strategy['total_expected_pnl'],
            'Total_Expected_PnL_Millions': strategy['total_expected_pnl'] / 1e6
        })
    
    strategies_df = pd.DataFrame(strategies_data)
    strategies_df = strategies_df.sort_values('Total_Expected_PnL_USD', ascending=False)
    
    excel_file = output_dir / f"strategies_comparison_{timestamp}.xlsx"
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Sheet 1: Summary
        strategies_df.to_excel(writer, sheet_name='Strategy_Comparison', index=False)
        
        # Sheet 2-4: Monthly breakdown for each strategy
        for name, strategy in strategies.items():
            sheet_name = name[:31]  # Excel sheet name limit
            monthly_df = strategy['monthly_results_df']
            
            # Select key columns
            cols_to_save = [
                'month', 'destination', 'buyer', 'buyer_credit_rating',
                'henry_hub_price', 'jkm_price', 'brent_price',
                'purchase_cost', 'sale_revenue_gross', 'freight_cost',
                'gross_pnl', 'expected_pnl', 'probability_of_sale'
            ]
            cols_available = [c for c in cols_to_save if c in monthly_df.columns]
            
            monthly_df[cols_available].to_excel(writer, sheet_name=sheet_name, index=False)
    
    logger.info(f"   Saved to: {excel_file}")
    
    # 2. Optimal strategy decision table (for presentation)
    logger.info("\n2. Optimal Strategy Decision Table...")
    optimal = strategies['Optimal']
    decision_table = []
    
    for month in CARGO_CONTRACT['delivery_period']:
        decision = optimal['monthly_decisions'][month]
        decision_table.append({
            'Month': month,
            'Destination': decision['destination'],
            'Buyer': decision['buyer'],
            'Expected_PnL_USD': decision['expected_pnl'],
            'Expected_PnL_Millions': decision['expected_pnl'] / 1e6
        })
    
    decision_df = pd.DataFrame(decision_table)
    decision_file = output_dir / f"optimal_strategy_{timestamp}.csv"
    decision_df.to_csv(decision_file, index=False)
    
    logger.info(f"   Saved to: {decision_file}")
    
    # 3. Monte Carlo risk metrics (if provided)
    if monte_carlo_results:
        logger.info("\n3. Monte Carlo Risk Metrics...")
        mc_data = []
        for strategy_name, result in monte_carlo_results.items():
            metrics = result['risk_metrics']
            mc_data.append({
                'Strategy': strategy_name,
                'Mean_PnL_M': metrics['mean'] / 1e6,
                'Std_Dev_M': metrics['std'] / 1e6,
                'VaR_5pct_M': metrics['var_5pct'] / 1e6,
                'CVaR_5pct_M': metrics['cvar_5pct'] / 1e6,
                'Prob_Profit': metrics['prob_profit'],
                'P10_M': metrics['p10'] / 1e6,
                'P25_M': metrics['p25'] / 1e6,
                'P50_M': metrics['p50'] / 1e6,
                'P75_M': metrics['p75'] / 1e6,
                'P90_M': metrics['p90'] / 1e6,
                'Sharpe_Ratio': metrics['sharpe_ratio']
            })
        
        mc_df = pd.DataFrame(mc_data)
        mc_file = output_dir / f"monte_carlo_risk_metrics_{timestamp}.xlsx"
        mc_df.to_excel(mc_file, index=False)
        logger.info(f"   Saved to: {mc_file}")
    
    # 4. Scenario analysis (if provided)
    if scenario_results:
        logger.info("\n4. Scenario Analysis...")
        scenario_data = []
        for scenario_name, strategies_dict in scenario_results.items():
            for strategy_name, result in strategies_dict.items():
                scenario_data.append({
                    'Scenario': scenario_name,
                    'Strategy': strategy_name,
                    'Total_PnL_USD': result['total_pnl'],
                    'Total_PnL_Millions': result['total_pnl'] / 1e6
                })
        
        scenario_df = pd.DataFrame(scenario_data)
        
        # Pivot for easier comparison
        scenario_pivot = scenario_df.pivot(
            index='Strategy',
            columns='Scenario',
            values='Total_PnL_Millions'
        )
        
        scenario_file = output_dir / f"scenario_analysis_{timestamp}.xlsx"
        
        with pd.ExcelWriter(scenario_file, engine='openpyxl') as writer:
            scenario_df.to_excel(writer, sheet_name='All_Scenarios', index=False)
            scenario_pivot.to_excel(writer, sheet_name='Scenario_Comparison')
        
        logger.info(f"   Saved to: {scenario_file}")
    
    logger.info("\n" + "="*80)
    logger.info("RESULTS SAVED SUCCESSFULLY")
    logger.info("="*80)
    
    output_files = {'excel': excel_file, 'csv': decision_file}
    if monte_carlo_results:
        output_files['monte_carlo'] = mc_file
    if scenario_results:
        output_files['scenarios'] = scenario_file
    
    return output_files


def print_summary(strategies: Dict):
    """Print executive summary."""
    logger.info("\n" + "="*80)
    logger.info("EXECUTION SUMMARY")
    logger.info("="*80)
    
    logger.info("\nSTRATEGIES GENERATED:")
    for name, strategy in strategies.items():
        pnl_millions = strategy['total_expected_pnl'] / 1e6
        logger.info(f"  {name:20s}: ${pnl_millions:8.2f}M")
    
    logger.info("\nOPTIMAL STRATEGY MONTHLY BREAKDOWN:")
    optimal = strategies['Optimal']
    for month in CARGO_CONTRACT['delivery_period']:
        decision = optimal['monthly_decisions'][month]
        pnl_millions = decision['expected_pnl'] / 1e6
        logger.info(f"  {month}: {decision['destination']:10s} ({decision['buyer']:15s}) -> ${pnl_millions:8.2f}M")
    
    logger.info("\n" + "="*80)
    logger.info("OPTIMIZATION COMPLETE!")
    logger.info("="*80)


def main(run_monte_carlo: bool = True, run_scenarios: bool = True, use_arima_garch: bool = True):
    """
    Main execution function.
    
    Args:
        run_monte_carlo: Whether to run Monte Carlo simulation (default True)
        run_scenarios: Whether to run scenario analysis (default True)
        use_arima_garch: Whether to use ARIMA+GARCH for Brent/Freight (default True)
    """
    from config import CARGO_ARIMA_GARCH_CONFIG
    
    try:
        # Step 1: Load data
        logger.info("\n" + "="*80)
        logger.info("STEP 1: LOADING DATA")
        logger.info("="*80)
        data = load_all_data()
        
        # Step 2: Prepare forecasts
        logger.info("\n" + "="*80)
        logger.info("STEP 2: PREPARING FORECASTS")
        logger.info("="*80)
        
        # Choose forecasting method based on configuration
        if use_arima_garch and CARGO_ARIMA_GARCH_CONFIG['enabled']:
            logger.info("Using ARIMA+GARCH for Brent and Freight forecasting...")
            forecasts = prepare_forecasts_arima_garch(data)
        else:
            logger.info("Using simple forecasting (forward curves + naive methods)...")
            forecasts = prepare_forecasts_simple(data)
        
        # Step 2b: Calculate volatilities and correlations (for Monte Carlo)
        volatilities, correlations = {}, pd.DataFrame()  # Initialize for scope
        if run_monte_carlo:
            volatilities, correlations = calculate_volatilities_and_correlations(data)
        
        # Step 3: Run optimization
        logger.info("\n" + "="*80)
        logger.info("STEP 3: RUNNING OPTIMIZATION")
        logger.info("="*80)
        
        calculator = CargoPnLCalculator()
        optimizer = StrategyOptimizer(calculator)
        
        strategies = optimizer.generate_all_strategies(forecasts)
        
        # Step 4: Monte Carlo Risk Analysis (optional)
        monte_carlo_results = None
        if run_monte_carlo:
            logger.info("\n" + "="*80)
            logger.info("STEP 4: MONTE CARLO RISK ANALYSIS")
            logger.info("="*80)
            
            mc_analyzer = MonteCarloRiskAnalyzer(calculator)
            monte_carlo_results = mc_analyzer.run_monte_carlo(
                strategies, forecasts, volatilities, correlations
            )
        
        # Step 5: Scenario Analysis (optional)
        scenario_results = None
        if run_scenarios:
            logger.info("\n" + "="*80)
            logger.info("STEP 5: SCENARIO ANALYSIS")
            logger.info("="*80)
            
            scenario_analyzer = ScenarioAnalyzer(calculator)
            scenario_results = scenario_analyzer.run_scenario_analysis(
                strategies, forecasts
            )
        
        # Step 6: Save results
        logger.info("\n" + "="*80)
        logger.info("STEP 6: SAVING RESULTS")
        logger.info("="*80)
        output_files = save_results(strategies, monte_carlo_results, scenario_results)
        
        # Step 7: Print summary
        print_summary(strategies)
        
        logger.info("\nOUTPUT FILES:")
        for file_type, file_path in output_files.items():
            logger.info(f"  {file_type:15s}: {file_path}")
        logger.info("\n" + "="*80)
        logger.info("ALL DONE!")
        logger.info("="*80)
        
        return {
            'strategies': strategies,
            'monte_carlo_results': monte_carlo_results,
            'scenario_results': scenario_results,
            'output_files': output_files
        }
        
    except Exception as e:
        logger.error(f"\nERROR: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    results = main()

