"""
Main configuration settings.
"""

# =============================================================================
# FREQUENCY CONFIGURATION
# =============================================================================

DATA_FREQUENCY = 'M'  # Input data frequency
ANALYSIS_FREQUENCY = 'M'  # Analysis frequency
DECISION_FREQUENCY = 'M'  # Decision frequency

# =============================================================================
# DATA PROCESSING PARAMETERS
# =============================================================================

DATE_FORMAT = '%Y-%m-%d'
MIN_HISTORY_DAYS = 365
MAX_MISSING_PCT = 0.10
FORWARD_FILL_LIMIT_DAYS = 7
DATA_VALIDATION_STRICT = True

# =============================================================================
# RESAMPLING CONFIGURATION
# =============================================================================

RESAMPLE_METHOD = 'mean'

# =============================================================================
# VOLUME FLEXIBILITY CONFIGURATION
# =============================================================================

VOLUME_FLEXIBILITY_CONFIG = {
    'enabled': True,
    'base_volume_mmbtu': 3_800_000,  # PURCHASE contract base
    'tolerance_pct': 0.10,
    'min_volume_mmbtu': 3_420_000,  # 90% of purchase
    'max_volume_mmbtu': 4_180_000,  # 110% of purchase
    'optimization_method': 'margin_based',
    'margin_thresholds': {
        'high_margin_min': 5.0,
        'low_margin_max': 2.0
    }
}

# =============================================================================
# SALES CONTRACT CONFIGURATION (SEPARATE FROM PURCHASE!)
# =============================================================================

SALES_CONTRACT = {
    'enabled': True,
    'base_volume_mmbtu': 3_700_000,  # SALES contract base (100k less than purchase)
    'tolerance_pct': 0.10,
    'min_volume_mmbtu': 3_330_000,  # 90% of sales
    'max_volume_mmbtu': 4_070_000,  # 110% of sales
    'stranded_volume_treatment': 'opportunity_cost',  # Paid for but can't sell
}

# =============================================================================
# DEMAND PRICING ADJUSTMENT CONFIGURATION
# =============================================================================

DEMAND_PRICING_MODEL = {
    'enabled': True,  # Use price adjustment instead of probability
    'model_type': 'price_adjustment',  # vs 'probability' (old approach)
    'smooth': True,  # Use polynomial smoothing (vs step function)
    'rationale': 'Sales are forward contracts (M-1 nomination). Demand % affects negotiating position and achievable pricing, not binary sale probability.',
    
    # Price adjustments by demand level ($/MMBtu)
    'adjustments': {
        'very_low': {'threshold': 0.20, 'adjustment': -2.00},   # <20% demand: Strong discount
        'low': {'threshold': 0.40, 'adjustment': -1.00},        # 20-40%: Moderate discount
        'moderate': {'threshold': 0.60, 'adjustment': -0.25},   # 40-60%: Slight discount
        'high': {'threshold': 0.80, 'adjustment': 0.00},        # 60-80%: Market pricing
        'very_high': {'threshold': 1.00, 'adjustment': +1.00},  # >80%: Scarcity premium
    }
}

# =============================================================================
# HEDGING CONFIGURATION
# =============================================================================

HEDGING_CONFIG = {
    'enabled': True,
    'henry_hub_hedge': {
        'enabled': True,
        'contract_size_mmbtu': 10_000,
        'hedge_ratio': 1.0,
        'timing': 'M-2'
    }
}

# =============================================================================
# MONTE CARLO CONFIGURATION
# =============================================================================

MONTE_CARLO_CONFIG = {
    'enabled': True,
    'n_simulations': 10_000,
    'confidence_levels': [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
}

# =============================================================================
# MONTE CARLO CARGO CONFIG
# =============================================================================

MONTE_CARLO_CARGO_CONFIG = MONTE_CARLO_CONFIG

# =============================================================================
# ARIMA CONFIGURATION
# =============================================================================

ARIMA_CONFIG = {
    'max_p': 3,
    'max_d': 2,
    'max_q': 3,
    'seasonal': False,
    'trend': None,
    'method': 'lbfgs',
    'maxiter': 50
}

# =============================================================================
# GARCH CONFIGURATION
# =============================================================================

GARCH_CONFIG = {
    'vol': 'GARCH',
    'p': 1,
    'q': 1,
    'dist': 'normal',
    'rescale': True,
    'default_p': 1,
    'default_q': 1
}

# =============================================================================
# FORECASTING CONFIGURATION
# =============================================================================

CARGO_FORECASTING_METHOD = {
    'henry_hub': {'method': 'arima_garch', 'reason': 'High quality data, good for ARIMA+GARCH'},
    'jkm': {'method': 'arima_garch', 'reason': 'High quality data, good for ARIMA+GARCH'},
    'brent': {'method': 'arima_garch', 'reason': 'High quality data, good for ARIMA+GARCH'},
    'freight': {'method': 'arima_garch', 'reason': 'Using ARIMA+GARCH for volatility forecasting'}
}
CARGO_ARIMA_GARCH_CONFIG = {
    'enabled': True,
    'min_months_required': 24,
    'arima': ARIMA_CONFIG,
    'garch': GARCH_CONFIG
}

# =============================================================================
# SCENARIO CONFIGURATION
# =============================================================================

CARGO_SCENARIOS = {
    'bull_market': {'hh_multiplier': 1.2, 'jkm_multiplier': 1.3, 'brent_multiplier': 1.1},
    'bear_market': {'hh_multiplier': 0.8, 'jkm_multiplier': 0.7, 'brent_multiplier': 0.9},
    'volatile': {'hh_multiplier': 1.0, 'jkm_multiplier': 1.0, 'brent_multiplier': 1.0}
}

# =============================================================================
# FORECAST CONFIGURATION
# =============================================================================

FORECAST_CONFIG = {
    'forecast_horizon_months': 6,
    'confidence_level': 0.95,
    'bootstrap_samples': 1000
}

# =============================================================================
# BACKTEST CONFIGURATION
# =============================================================================

BACKTEST_CONFIG = {
    'enabled': True,
    'test_periods': 12,
    'refit_frequency': 1
}

# =============================================================================
# SEASONALITY CONFIGURATION
# =============================================================================

SEASONALITY_CONFIG = {
    'enabled': True,
    'test_method': 'canova_hansen',
    'significance_level': 0.05
}

# =============================================================================
# OUTLIER CONFIGURATION
# =============================================================================

OUTLIER_CONFIG = {
    'enabled': True,
    'method': 'iqr',
    'threshold': 3.0,
    'action': 'flag'
}

# =============================================================================
# FORECASTING CONFIGURATION (ALIAS)
# =============================================================================

FORECASTING_CONFIG = FORECAST_CONFIG

# =============================================================================
# MANUAL ARIMA OVERRIDES
# =============================================================================

MANUAL_ARIMA_OVERRIDES = {
    'henry_hub': None,
    'jkm': None,
    'brent': None,
    'freight': None
}

# =============================================================================
# MANUAL GARCH OVERRIDES
# =============================================================================

MANUAL_GARCH_OVERRIDES = {
    'henry_hub': None,
    'jkm': None,
    'brent': None,
    'freight': None
}

# =============================================================================
# FORECAST HORIZON
# =============================================================================

FORECAST_HORIZON_DAYS = 180  # 6 months
