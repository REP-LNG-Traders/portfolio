"""
Configuration file for LNG Trading Optimization System.

This file contains all constants, parameters, and mappings that may need
to be adjusted when the actual competition data is released.

Author: [Your Name]
Date: 2025-10-15
"""

import os
from pathlib import Path

# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS_MODELS = PROJECT_ROOT / "outputs" / "models"
OUTPUTS_RESULTS = PROJECT_ROOT / "outputs" / "results"
OUTPUTS_FIGURES = PROJECT_ROOT / "outputs" / "figures"
OUTPUTS_SUBMISSION = PROJECT_ROOT / "outputs" / "submission"
OUTPUTS_DIAGNOSTICS = PROJECT_ROOT / "outputs" / "diagnostics"

# =============================================================================
# DATA FILE NAMES (Edit these when real data arrives)
# =============================================================================

DATA_FILES = {
    'production': 'production_cost.xlsx',
    'freight': 'freight_cost.xlsx',
    'prices': 'lng_prices_asia.xlsx'
}

# =============================================================================
# DATA COLUMN MAPPINGS (Edit if real data has different column names)
# =============================================================================

COLUMN_MAPPING = {
    'prices': {
        'date': 'Date',          # Could be 'Date', 'DATE', 'date', 'Period', etc.
        'market': 'Market',       # Could be 'Market', 'Country', 'Region', etc.
        'price': 'Price'         # Could be 'Price', 'Spot_Price', 'LNG_Price', etc.
    },
    'production': {
        'date': 'Date',
        'cost': 'Cost_per_MMBtu'
    },
    'freight': {
        'route': 'Route',
        'market': 'Market',
        'cost': 'Cost_per_MMBtu'
    }
}

# =============================================================================
# MARKET STANDARDIZATION (Edit if real data has different market names)
# =============================================================================

MARKET_MAPPING = {
    # Standard names (left) <- Possible variations (right)
    'Singapore': ['Singapore', 'SG', 'SGP', 'Singapore Hub'],
    'China': ['China', 'CN', 'CHN', 'Shanghai', 'China (Shanghai)'],
    'Japan': ['Japan', 'JP', 'JPN', 'Tokyo', 'Japan (Tokyo)']
}

# Standard market order for consistency
MARKETS = ['Singapore', 'China', 'Japan']

# =============================================================================
# DATA PROCESSING PARAMETERS
# =============================================================================

# =============================================================================
# FREQUENCY CONFIGURATION
# =============================================================================
# This system supports flexible time frequencies for different stages:
# 1. DATA_FREQUENCY: The frequency of input data you receive
# 2. ANALYSIS_FREQUENCY: The frequency at which models (ARIMA/GARCH) operate
# 3. DECISION_FREQUENCY: The frequency at which optimization/decisions are made
#
# Example configuration:
#   - Input: Daily prices (730 days)
#   - Analysis: Fit ARIMA on daily data, forecast 730 days ahead
#   - Decisions: Aggregate to monthly, optimize 12 monthly cargo allocations
# =============================================================================

# Input data frequency
DATA_FREQUENCY = 'M'  # Expected frequency: 'D' (daily), 'W' (weekly), 'M' (monthly)

# Analysis frequency (for ARIMA/GARCH modeling)
ANALYSIS_FREQUENCY = 'M'  # Frequency for time series models: 'D', 'W', or 'M'
                          # Changed to 'M' = monthly for more stable volatility estimates

# Decision frequency (for optimization and cargo allocation)
DECISION_FREQUENCY = 'M'  # Frequency for decisions: 'D', 'W', or 'M'
                          # Default 'M' = monthly cargo allocations

# Date format for parsing
DATE_FORMAT = '%Y-%m-%d'  # Adjust if needed: '%d/%m/%Y', '%m-%d-%Y', etc.

# Resampling configuration (when frequencies differ)
RESAMPLE_METHOD = 'mean'  # How to aggregate when downsampling: 'mean', 'median', 'last', 'first'

# =============================================================================
# TIME-BASED PARAMETERS (in days for flexibility)
# =============================================================================

# Minimum historical data required
MIN_HISTORY_DAYS = 730  # ~2 years (24 months for monthly data)
                        # For monthly data: 24 months
                        # For daily data: 730 days

# Forward fill limit for missing values
FORWARD_FILL_LIMIT_DAYS = 30  # Maximum days to forward fill missing values
                               # 30 days = 1 month (reasonable for monthly data)
                               # Adjust based on DATA_FREQUENCY:
                               #   Daily: 7 days (1 week)
                               #   Weekly: 14-28 days (2-4 weeks)
                               #   Monthly: 30-60 days (1-2 months)

# Data quality
MAX_MISSING_PCT = 0.10   # Maximum 10% missing values allowed
DATA_VALIDATION_STRICT = False  # If True, raise errors; if False, log warnings and continue

# =============================================================================
# Helper function to convert days to periods based on frequency
# =============================================================================
def days_to_periods(days: int, frequency: str) -> int:
    """
    Convert days to number of periods based on frequency.
    
    Args:
        days: Number of days
        frequency: 'D', 'W', or 'M'
        
    Returns:
        Number of periods
    """
    if frequency == 'D':
        return days
    elif frequency == 'W':
        return days // 7
    elif frequency == 'M':
        return days // 30  # Approximate
    else:
        raise ValueError(f"Unknown frequency: {frequency}")

def periods_to_days(periods: int, frequency: str) -> int:
    """
    Convert periods to days based on frequency.
    
    Args:
        periods: Number of periods
        frequency: 'D', 'W', or 'M'
        
    Returns:
        Approximate number of days
    """
    if frequency == 'D':
        return periods
    elif frequency == 'W':
        return periods * 7
    elif frequency == 'M':
        return periods * 30  # Approximate
    else:
        raise ValueError(f"Unknown frequency: {frequency}")

# =============================================================================
# LNG TRADING PARAMETERS
# =============================================================================

# Physical cargo specifications
TOTAL_CARGOES = 12              # Total number of cargoes to allocate
CARGO_SIZE_M3 = 150000          # Cargo size in cubic meters
MMBTU_PER_M3 = 22.83            # Conversion factor: MMBtu per m³

# Calculate total volume
CARGO_SIZE_MMBTU = CARGO_SIZE_M3 * MMBTU_PER_M3  # ~3.4M MMBtu per cargo

# =============================================================================
# COST ASSUMPTIONS (Edit when real costs are provided)
# =============================================================================

# Terminal costs by market ($/MMBtu)
TERMINAL_COSTS = {
    'Singapore': 0.80,
    'China': 1.00,
    'Japan': 0.80
}

# Production cost ($/MMBtu) - will be overwritten by actual data
DEFAULT_PRODUCTION_COST = 4.50

# =============================================================================
# FORECASTING PARAMETERS
# =============================================================================

# Forecast horizon (in days for flexibility)
FORECAST_HORIZON_DAYS = 730  # Generate 730-day forecasts (~2 years)
                              # Will forecast at ANALYSIS_FREQUENCY
                              # Then aggregate to DECISION_FREQUENCY for optimization
                              # 
                              # Examples:
                              #   730 days @ daily = 730 daily forecasts
                              #   730 days @ weekly = ~104 weekly forecasts  
                              #   730 days @ monthly = ~24 monthly forecasts

# ARIMA configuration
ARIMA_CONFIG = {
    'criterion': 'bic',              # Model selection criterion: 'aic' or 'bic'
    'max_p': 3,                      # Maximum AR order to test
    'max_q': 3,                      # Maximum MA order to test
    'max_d': 2,                      # Maximum differencing order (cap)
    'show_top_n': 3,                 # Show top N models in comparison
    'seasonal': False,               # Set to True if seasonal patterns detected
    'seasonal_periods': 12,          # Months in a seasonal cycle
    'ljung_box_lags': 10,           # Lags for Ljung-Box test
    'auto_extend_search': True,      # Auto-extend search if diagnostics fail
    'alpha': 0.05,                   # Significance level for statistical tests
    
    # NEW: BIC Tolerance Rule (Prefer parsimony)
    'bic_tolerance': 2.0,            # If ΔBIC < 2, prefer simpler model (lower p+q)
    'prefer_parsimony': True,        # When models within tolerance, prefer simpler
    
    # NEW: ACF/PACF Interpretation Helper
    'use_acf_pacf_helper': True,     # Auto-interpret ACF/PACF patterns and suggest orders
    
    # NEW: Fallback Method (if ARIMA fails to converge)
    'fallback_method': 'holt',       # 'holt' (exponential smoothing), 'naive', 'ma'
    'fallback_ci_multiplier': 2.0,   # Wider confidence intervals for fallback (2 std instead of 1.96)
}

# Manual ARIMA overrides (use if automated selection fails)
# Format: 'Market': {'p': X, 'd': Y, 'q': Z}
MANUAL_ARIMA_OVERRIDES = {
    # Example: 'Singapore': {'p': 1, 'd': 1, 'q': 1}
}

# GARCH configuration
GARCH_CONFIG = {
    'default_p': 1,                  # Default GARCH p order (like ARIMA default)
    'default_q': 1,                  # Default GARCH q order
    'max_p': 2,                      # Maximum p order for grid search
    'max_q': 2,                      # Maximum q order for grid search
    'vol_annualization': 12,         # Months in year for annualization (12 for monthly data)
                                     # For daily: 252 (trading) or 365 (calendar)
                                     # For monthly: 12
    'rescale': True,                 # Rescale data for numerical stability
    'mean': 'Zero',                  # Mean model: 'Zero', 'Constant', 'AR'
    'auto_extend_search': True,      # Auto-extend if diagnostics fail
    
    # NEW: Distribution Selection
    'distribution': 'auto',          # 'normal', 't' (Student's t), 'auto' (based on JB test)
    'df_constraint': None,           # Degrees of freedom for t-dist (None = estimate)
    
    # NEW: ARCH-LM Test Integration
    'skip_if_no_arch': True,         # Skip GARCH if ARCH-LM shows no effects (save computation)
    'arch_lm_lags': 10,              # Number of lags for ARCH-LM test
    'arch_lm_alpha': 0.05,           # Significance level for ARCH-LM test
}

# Manual GARCH overrides (like ARIMA)
# Format: 'Market': {'p': X, 'q': Y}
MANUAL_GARCH_OVERRIDES = {
    # Example: 'Singapore': {'p': 2, 'q': 1}
}

# Backtesting configuration (in days)
BACKTEST_CONFIG = {
    'enabled': True,                 # Run backtesting (mandatory for validation)
    'train_size_days': 365,          # Initial training window (~1 year)
    'test_size_days': 180,           # Test set size (~6 months)
    'step_days': 90,                 # Walk-forward step size (~3 months, faster)
    'forecast_horizon': 30,          # Forecast X days ahead for validation
}

# Seasonality Detection Configuration
SEASONALITY_CONFIG = {
    'check_enabled': True,           # Run seasonality checks before modeling
    'variance_threshold': 0.15,      # Flag if seasonal component > 15% of total variance
    'methods': ['decomposition', 'acf', 'statistical'],  # Tests to run
    'seasonal_lags': [7, 30, 365],   # Check these lags (weekly, monthly, yearly)
    'seasonal_periods': None,        # Auto-detect or specify (e.g., 30 for monthly pattern in daily data)
}

# Outlier Detection Configuration
OUTLIER_CONFIG = {
    'detection_enabled': True,       # Run outlier detection before ARIMA
    'method': 'rolling_zscore',      # 'rolling_zscore', 'iqr', 'isolation'
    'threshold': 3.0,                # Z-score threshold (3.0 = 99.7%)
    'window': 30,                    # Rolling window for calculating statistics
    'action': 'flag',                # 'flag' (report only), 'winsorize', 'interpolate'
    'max_outlier_pct': 0.05,         # Warn if > 5% outliers detected
}

# Forecast Configuration
FORECAST_CONFIG = {
    'horizon_days': 730,             # 730 days = ~2 years
    'confidence_levels': [0.95],     # Can add multiple: [0.68, 0.95, 0.99]
    'include_bounds': True,          # Generate confidence intervals
    'volatility_method': 'mean_reverting',  # 'mean_reverting' or 'constant'
    'ci_distribution': 'auto',       # 'normal', 't' (Student's t), or 'auto'
    'df': 30,                        # Degrees of freedom if using t-distribution
}

# Overall Forecasting Control (Master Switches)
FORECASTING_CONFIG = {
    'check_seasonality': True,       # Run seasonality detection
    'detect_outliers': True,         # Run outlier detection
    'run_arch_lm_test': True,        # Run ARCH-LM test before GARCH
    'auto_distribution': True,       # Auto-select normal vs Student's t
    'use_acf_pacf_helper': True,     # Use ACF/PACF interpretation helper
    'document_formulas': True,       # Include formulas in Excel diagnostics
}

# =============================================================================
# PORTFOLIO OPTIMIZATION PARAMETERS
# =============================================================================

# Risk-free rate (annual)
RISK_FREE_RATE = 0.04  # 4% annual risk-free rate

# Position constraints
ALLOW_SHORT_SELLING = False  # Set to True to allow negative positions
MIN_POSITION = -0.3 if ALLOW_SHORT_SELLING else 0.0  # Minimum weight per market
MAX_POSITION = 0.6                                    # Maximum weight per market

# Optimization settings
OPTIMIZATION_CONFIG = {
    'method': 'SLSQP',              # Optimization method
    'max_iterations': 1000,          # Maximum iterations
    'tolerance': 1e-10,              # Convergence tolerance
    'efficient_frontier_points': 50  # Points on efficient frontier
}

# =============================================================================
# RISK ANALYSIS PARAMETERS
# =============================================================================

# Monte Carlo simulation
N_SIMULATIONS = 10000            # Number of simulation paths
CONFIDENCE_LEVEL = 0.95          # Confidence level for VaR/CVaR
MC_SIMULATION_HORIZON_DAYS = 730 # Days to simulate (~2 years)
                                  # Simulates at ANALYSIS_FREQUENCY
                                  # Aggregates to DECISION_FREQUENCY for portfolio returns
MC_RANDOM_SEED = 42              # Set for reproducibility (None for random)

# Risk metrics
RISK_METRICS = {
    'var_confidence': 0.95,      # 95% VaR
    'cvar_confidence': 0.95,     # 95% CVaR
    'target_return': 0.10,       # 10% target return threshold
    'loss_threshold': 0.0,       # Loss threshold for probability calculation
}

# =============================================================================
# SCENARIO ANALYSIS (Edit scenarios when problem statement is released)
# =============================================================================

SCENARIOS = {
    'Base_Case': {
        'description': 'Current market conditions',
        'price_adj': [1.0, 1.0, 1.0],      # [Singapore, China, Japan] multipliers
        'freight_adj': [1.0, 1.0, 1.0],    # [Singapore, China, Japan] multipliers
        'probability': 0.50                 # Probability of scenario
    },
    # Add more scenarios when details are released:
    # 'China_Demand_Surge': {
    #     'description': 'Strong Chinese demand growth',
    #     'price_adj': [1.05, 1.20, 1.10],
    #     'freight_adj': [1.0, 1.10, 1.0],
    #     'probability': 0.20
    # },
}

# =============================================================================
# HEDGING PARAMETERS (Optional - currently disabled)
# =============================================================================

HEDGING_CONFIG = {
    'enabled': False,                # Enable hedging analysis
    'hedge_ratio_min': 0.75,        # Minimum hedge ratio
    'hedge_ratio_max': 0.90,        # Maximum hedge ratio
    'futures_contract_size': 10000,  # MMBtu per contract
}

# =============================================================================
# VISUALIZATION PARAMETERS
# =============================================================================

PLOT_CONFIG = {
    'style': 'whitegrid',           # Seaborn style
    'dpi': 300,                     # Resolution for saved figures
    'figsize_default': (10, 6),     # Default figure size
    'figsize_wide': (14, 6),        # Wide figure size
    'figsize_square': (8, 8),       # Square figure size
    'font_size_title': 14,          # Title font size
    'font_size_label': 12,          # Axis label font size
    'font_size_legend': 11,         # Legend font size
    'font_size_tick': 10,           # Tick label font size
    'grid_alpha': 0.3,              # Grid transparency
    'color_palette': 'Set2',        # Default color palette
}

# Market colors for consistent visualization
MARKET_COLORS = {
    'Singapore': '#66c2a5',
    'China': '#fc8d62',
    'Japan': '#8da0cb'
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOG_CONFIG = {
    'level': 'INFO',                # Logging level: DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'file': 'outputs/execution.log',
    'console': True,                # Also log to console
}

# =============================================================================
# EXCEL EXPORT CONFIGURATION
# =============================================================================

EXCEL_CONFIG = {
    'master_workbook': 'MASTER_WORKBOOK.xlsx',
    'float_format': '%.4f',
    'currency_format': '$#,##0.00',
    'percent_format': '0.00%',
    'include_index': True,
}

# Excel sheet names
EXCEL_SHEETS = {
    'summary': 'Summary',
    'price_forecasts': 'Price_Forecasts',
    'volatility': 'Volatility',
    'correlation': 'Correlation',
    'covariance': 'Covariance',
    'returns': 'Returns',
    'optimal_portfolio': 'Optimal_Portfolio',
    'physical_allocation': 'Physical_Allocation',
    'monte_carlo': 'Monte_Carlo',
    'scenarios': 'Scenarios',
    'backtest': 'Backtest',
    'arima_diagnostics': 'ARIMA_Diagnostics',
    'garch_diagnostics': 'GARCH_Diagnostics',
}

# =============================================================================
# PERFORMANCE SETTINGS
# =============================================================================

PERFORMANCE_CONFIG = {
    'use_multiprocessing': False,    # Enable parallel processing (if needed)
    'n_jobs': -1,                    # Number of parallel jobs (-1 = all cores)
    'show_progress_bars': True,      # Show tqdm progress bars
    'cache_results': True,           # Cache intermediate results
}

# =============================================================================
# VALIDATION THRESHOLDS
# =============================================================================

VALIDATION_THRESHOLDS = {
    'min_price': 0.0,                # Minimum valid price ($/MMBtu)
    'max_price': 50.0,               # Maximum valid price ($/MMBtu)
    'min_cost': 0.0,                 # Minimum valid cost ($/MMBtu)
    'max_cost': 30.0,                # Maximum valid cost ($/MMBtu)
    'weights_sum_tolerance': 1e-6,   # Tolerance for weights summing to 1
    'covariance_eigenvalue_min': -1e-10,  # Minimum eigenvalue for PSD check
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_market_standard_name(market_name: str) -> str:
    """
    Standardize market names from various input formats.
    
    Args:
        market_name: Input market name (possibly non-standard)
        
    Returns:
        Standardized market name
        
    Raises:
        ValueError: If market name cannot be mapped
    """
    market_name = str(market_name).strip()
    
    for standard, variations in MARKET_MAPPING.items():
        if market_name in variations:
            return standard
    
    raise ValueError(f"Unknown market name: '{market_name}'. "
                     f"Expected one of: {MARKET_MAPPING}")


def validate_config():
    """
    Validate configuration parameters for consistency.
    
    Raises:
        ValueError: If configuration is invalid
    """
    # Validate paths exist
    for path in [DATA_RAW, DATA_PROCESSED, OUTPUTS_MODELS, OUTPUTS_RESULTS, 
                 OUTPUTS_FIGURES, OUTPUTS_SUBMISSION, OUTPUTS_DIAGNOSTICS]:
        path.mkdir(parents=True, exist_ok=True)
    
    # Validate frequencies
    valid_frequencies = ['D', 'W', 'M']
    if DATA_FREQUENCY not in valid_frequencies:
        raise ValueError(f"DATA_FREQUENCY must be one of {valid_frequencies}, got {DATA_FREQUENCY}")
    if ANALYSIS_FREQUENCY not in valid_frequencies:
        raise ValueError(f"ANALYSIS_FREQUENCY must be one of {valid_frequencies}, got {ANALYSIS_FREQUENCY}")
    if DECISION_FREQUENCY not in valid_frequencies:
        raise ValueError(f"DECISION_FREQUENCY must be one of {valid_frequencies}, got {DECISION_FREQUENCY}")
    
    # Validate time parameters
    if MIN_HISTORY_DAYS < 1:
        raise ValueError(f"MIN_HISTORY_DAYS must be >= 1, got {MIN_HISTORY_DAYS}")
    if FORWARD_FILL_LIMIT_DAYS < 0:
        raise ValueError(f"FORWARD_FILL_LIMIT_DAYS cannot be negative, got {FORWARD_FILL_LIMIT_DAYS}")
    if FORECAST_HORIZON_DAYS < 1:
        raise ValueError(f"FORECAST_HORIZON_DAYS must be >= 1, got {FORECAST_HORIZON_DAYS}")
    
    # Validate position constraints
    if MIN_POSITION > MAX_POSITION:
        raise ValueError(f"MIN_POSITION ({MIN_POSITION}) cannot exceed MAX_POSITION ({MAX_POSITION})")
    
    if not ALLOW_SHORT_SELLING and MIN_POSITION < 0:
        raise ValueError("MIN_POSITION cannot be negative when ALLOW_SHORT_SELLING is False")
    
    # Validate simulation parameters
    if N_SIMULATIONS < 1000:
        raise ValueError(f"N_SIMULATIONS should be >= 1000 for stable results, got {N_SIMULATIONS}")
    
    # Validate ARIMA config
    if ARIMA_CONFIG['criterion'] not in ['aic', 'bic']:
        raise ValueError(f"ARIMA criterion must be 'aic' or 'bic', got {ARIMA_CONFIG['criterion']}")
    
    print("[OK] Configuration validated successfully")


# =============================================================================
# LNG CARGO TRADING CONFIGURATION
# =============================================================================

# Contract Terms (from case pack page 15)
CARGO_CONTRACT = {
    'volume_mmbtu': 3_800_000,
    'volume_tolerance': 0.10,  # ±10%
    'purchase_formula': 'henry_hub_wma_M + 2.50',  # M = loading month
    'tolling_fee': 1.50,  # $/MMBtu if cancelled
    'delivery_period': ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06']
}

# Voyage Times (from case pack page 20)
VOYAGE_DAYS = {
    'USGC_to_Singapore': 48,  # 2025 average
    'USGC_to_Japan': 41,
    'USGC_to_China': 52
}

# Freight Rate Scaling Factors (route-specific adjustments to BLNG 1)
# Used as proxy for distance differences between routes
FREIGHT_SCALING_FACTORS = {
    'USGC_to_Singapore': 0.9,   # Shorter route - scale down
    'USGC_to_Japan': 1.0,        # Baseline BLNG 1
    'USGC_to_China': 1.05        # Longer route - scale up
}

# ============================================================================
# COMPREHENSIVE SHIPPING COST COMPONENTS
# ============================================================================
# Sources and assumptions documented for each component

# 1. Insurance Costs
# Source: bplan.ai - LNG carrier insurance premiums range $250k-$1M per year
# Source: financialmodelexcel.com - Annual premiums for large LNG carriers
INSURANCE_COSTS = {
    'annual_premium': 650000,  # USD per year (mid-range estimate)
    'per_voyage': 54167,       # USD per voyage (annual / 12 months)
    'per_mmbtu': 0.016,        # USD per MMBtu (per_voyage / 3.4M MMBtu)
    'components': {
        'hull_and_machinery': 0.40,  # 40% of total premium
        'protection_indemnity': 0.35,  # 35% of total premium
        'war_risk': 0.15,              # 15% of total premium
        'cargo_insurance': 0.10        # 10% of total premium
    },
    'source': 'https://bplan.ai/blogs/running-expenses/lng-liquefied-natural-gas-shipping-and-transportation-running-expenses'
}

# 2. Brokerage Costs
# Source: Industry standard for shipping brokerage is 1.25% of freight value
# This is the commission paid to ship brokers for arranging the charter
BROKERAGE_COSTS = {
    'rate': 0.0125,  # 1.25% of freight cost
    'description': 'Ship brokerage commission for charter arrangement',
    'source': 'Industry standard for maritime brokerage services',
    'note': 'Applied as percentage of base freight cost'
}

# 3. Working Capital Costs
# Source: Commodity trading working capital typically financed at SOFR + spread
# Current rates around 5-7% annually for short-term trade finance
WORKING_CAPITAL = {
    'annual_rate': 0.06,  # 6% per annum
    'description': 'Cost of capital tied up in voyage duration',
    'calculation': 'cargo_value × rate × (voyage_days / 365)',
    'source': 'Industry standard commodity trade finance rates 2024-2025',
    'note': 'Applied to total cargo purchase cost during voyage period'
}

# 4. Carbon Costs (Port/Region Specific)
# Source: EU ETS, IMO regulations, regional carbon pricing
# Source: mdpi.com - EU Fit for 55, waytronsc.com - IMO 2020 sulfur cap
CARBON_COSTS = {
    'EU_ETS_rate': 85.0,  # EUR per ton CO2 (2024-2025 estimate)
    'emissions_per_day': 50,  # Tons CO2 per day (typical LNG carrier)
    'by_destination': {
        'Singapore': {
            'rate_per_day': 1500,  # USD per day (lower due to limited regulation)
            'total_voyage_cost': lambda days: 1500 * days,
            'description': 'Limited carbon regulations in Singapore',
            'source': 'Regional carbon pricing estimates 2024'
        },
        'Japan': {
            'rate_per_day': 2500,  # USD per day (moderate regulation)
            'total_voyage_cost': lambda days: 2500 * days,
            'description': 'Japan carbon pricing mechanism',
            'source': 'Japan carbon tax and emissions regulations'
        },
        'China': {
            'rate_per_day': 2000,  # USD per day (growing regulation)
            'total_voyage_cost': lambda days: 2000 * days,
            'description': 'China ETS and environmental regulations',
            'source': 'China national carbon trading scheme'
        }
    },
    'note': 'Carbon costs vary by route due to different regulatory frameworks',
    'sources': [
        'https://www.mdpi.com/2077-1312/10/7/946',
        'https://www.waytronsc.com/sys-nd/678.html'
    ]
}

# 5. Demurrage Costs
# Source: waytronsc.com, timera-energy.com - Can exceed $100k per day for LNG carriers
DEMURRAGE_COSTS = {
    'rate_per_day': 125000,  # USD per day
    'laytime_loading': 36,   # Hours allowed for loading (1.5 days)
    'laytime_discharge': 36, # Hours allowed for discharge (1.5 days)
    'probability_delay': 0.15,  # 15% probability of delay
    'expected_delay_hours': 12,  # Expected delay if it occurs (hours)
    'expected_cost': 125000 * (12/24) * 0.15,  # Expected value of demurrage
    'description': 'Charges for delays beyond agreed laytime',
    'source': 'https://www.waytronsc.com/sys-nd/678.html',
    'note': 'Applied probabilistically in risk calculations'
}

# 6. Letter of Credit (LC) Costs
# Source: Standard international trade finance fees
# Typical range 0.1-0.5% of transaction value
LC_COSTS = {
    'rate': 0.003,  # 0.3% of transaction value (mid-range)
    'minimum_fee': 5000,  # USD minimum fee
    'tenor_days': 90,  # Typical LC tenor for LNG trades
    'description': 'Bank fees for LC issuance and confirmation',
    'components': {
        'issuance_fee': 0.0015,  # 0.15% - issuing bank
        'confirmation_fee': 0.0010,  # 0.10% - confirming bank
        'negotiation_fee': 0.0005   # 0.05% - negotiating bank
    },
    'source': 'Standard international trade finance rates 2024',
    'note': 'Applied to total sale value of cargo'
}

# Summary of Additional Shipping Costs
SHIPPING_COST_SUMMARY = {
    'components': [
        'base_freight',      # Baltic LNG rate × voyage days × scaling factor
        'insurance',         # Per voyage insurance premium
        'brokerage',         # 1.25% of freight cost
        'working_capital',   # Interest on capital during voyage
        'carbon',           # Region-specific carbon costs
        'demurrage_risk',   # Expected value of demurrage
        'lc_cost'           # Letter of credit fees
    ],
    'total_formula': 'SUM(all components)',
    'allocation': 'All costs allocated per MMBtu of cargo'
}

# Operational Assumptions
OPERATIONAL = {
    'boil_off_rate_per_day': 0.0015,  # 0.15% per day (industry standard)
    'storage_cost_per_mmbtu_per_month': 0.05,  # ASSUMPTION - ask mentors if possible
    'slng_storage_capacity': 12_000_000,  # MMBtu (from case pack page 22)
    'discharge_time_days': 1.0,  # ASSUMPTION
    'freight_interpretation': 'ASSUMPTION: Baltic data treated as $/MMBtu equivalent. '
                              'If actually $/day, needs conversion using vessel capacity.'
}

# Sales Contract Formulas (from case pack page 16)
SALES_FORMULAS = {
    'Singapore': {
        'base': 'brent_M * 0.13',  # M = loading month
        'terminal_tariff': 0.80,  # From Singapore Related Data
        'payment_terms': 'upon_delivery'
    },
    'Japan': {
        'base': 'jkm_M+1',  # M+1 = month after loading (IMPORTANT: need July forecast for June cargo)
        'berthing_cost': 0.10,
        'payment_terms': 'upon_receipt_of_documents'
    },
    'China': {
        'base': 'jkm_M+1',  # M+1 = month after loading
        'berthing_cost': 0.10,
        'payment_terms': '30_days_after_delivery'
    }
}

# Buyers and Their Characteristics (from case pack page 18)
# Note: All premiums are ADDED to base price (ranges reflect negotiation strength)
BUYERS = {
    'Singapore': {
        'Thor': {
            'type': 'Power Utility',
            'credit_rating': 'AA',
            'premium': 3.5,  # LOW end of $3-7.5 range (strong AA negotiator)
            'note': 'Contracts 3-6 months ahead, strong bargaining power'
        },
        'Iron_Man': {
            'type': 'Bunker Supplier',
            'credit_rating': 'A',
            'premium': 4.0,  # Based on "JKM + $3-5" bunker pricing
            'note': 'Bunker prices at JKM + $3-5'
        },
        'Vision': {
            'type': 'Trader',
            'credit_rating': 'BB',
            'premium': 5.5,  # MID range
            'note': 'Negotiates $1-2 discount (from high end)'
        },
        'Loki': {
            'type': 'Trader',
            'credit_rating': 'CCC',
            'premium': 6.5,  # HIGH end (weak negotiator + high credit risk)
            'note': 'Negotiates $1-2 discount, HIGH credit risk'
        }
    },
    'Japan': {
        'Hawk_Eye': {
            'type': 'Trader',
            'credit_rating': 'AA',
            'premium': 0.6,  # LOW end of $0.5-1.2
            'note': 'Strong AA negotiator'
        },
        'Ultron': {
            'type': 'Trader',
            'credit_rating': 'B',
            'premium': 1.2,  # HIGH end (pays market price)
            'note': 'Pays market prices'
        }
    },
    'China': {
        'QuickSilver': {
            'type': 'Trader',
            'credit_rating': 'A',
            'premium': 2.2,  # LOW end of $2-3.5
            'note': 'Strong A-rated negotiator'
        },
        'Hulk': {
            'type': 'Trader',
            'credit_rating': 'BB',
            'premium': 3.0,  # MID range
            'note': 'Negotiates $1-2 discount'
        }
    }
}

# Credit Risk (industry standard default probabilities)
CREDIT_DEFAULT_PROBABILITY = {
    'AA': 0.005,   # 0.5% annual default probability
    'A': 0.01,     # 1%
    'BBB': 0.03,   # 3%
    'BB': 0.08,    # 8%
    'B': 0.15,     # 15%
    'CCC': 0.30,   # 30%
    'D': 1.0       # Already defaulted
}
CREDIT_RECOVERY_RATE = 0.40  # Typically recover 40% through legal process

# Demand Profile (from case pack page 17)
# Values represent probability of successful sale at stated price
DEMAND_PROFILE = {
    'Singapore': {
        '2026-01': 0.10, '2026-02': 0.25, '2026-03': 0.50,
        '2026-04': 0.50, '2026-05': 0.65, '2026-06': 0.65
    },
    'China': {
        '2026-01': 0.10, '2026-02': 0.25, '2026-03': 0.25,
        '2026-04': 0.50, '2026-05': 0.60, '2026-06': 0.60
    },
    'Japan': {
        '2026-01': 0.05, '2026-02': 0.25, '2026-03': 0.25,
        '2026-04': 0.70, '2026-05': 0.70, '2026-06': 0.70
    }
}

# Monte Carlo Configuration (Cargo Optimization)
MONTE_CARLO_CARGO_CONFIG = {
    'n_simulations': 10000,
    'random_seed': 42,
    'confidence_levels': [0.90, 0.95, 0.99]
}

# Scenario Analysis
CARGO_SCENARIOS = {
    'Base': {
        'description': 'Base case using our forecasts',
        'adjustments': {}
    },
    'Bull_Asia': {
        'description': 'Strong Asian demand - JKM up 20%, HH unchanged',
        'adjustments': {'jkm_multiplier': 1.20}
    },
    'Bear_US': {
        'description': 'High US gas prices - HH up 15%, JKM unchanged',
        'adjustments': {'henry_hub_multiplier': 1.15}
    },
    'Logistics_Stress': {
        'description': 'Panama Canal closure - freight up, voyage time +7 days',
        'adjustments': {
            'freight_addon': 2.0,  # $/MMBtu additional
            'voyage_days_addon': 7
        }
    }
}


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Validate configuration when run directly
    validate_config()
    print("\nConfiguration Summary:")
    print(f"  Markets: {MARKETS}")
    print(f"  Frequencies:")
    print(f"    Data Input: {DATA_FREQUENCY} (daily/weekly/monthly)")
    print(f"    Analysis (ARIMA): {ANALYSIS_FREQUENCY}")
    print(f"    Decisions (Optimization): {DECISION_FREQUENCY}")
    print(f"  Time Parameters:")
    print(f"    Min History: {MIN_HISTORY_DAYS} days (~{MIN_HISTORY_DAYS/30:.1f} months)")
    print(f"    Forward Fill Limit: {FORWARD_FILL_LIMIT_DAYS} days")
    print(f"    Forecast Horizon: {FORECAST_HORIZON_DAYS} days (~{FORECAST_HORIZON_DAYS/30:.1f} months)")
    print(f"  Trading:")
    print(f"    Total Cargoes: {TOTAL_CARGOES}")
    print(f"    Position Constraints: [{MIN_POSITION:.1%}, {MAX_POSITION:.1%}]")
    print(f"  Risk:")
    print(f"    Monte Carlo Simulations: {N_SIMULATIONS:,}")
    print(f"    Risk-Free Rate: {RISK_FREE_RATE:.1%}")

