"""
Business constants and parameters.
"""

# =============================================================================
# DATA FILE NAMES
# =============================================================================

DATA_FILES = {
    'production': 'production_cost.xlsx',
    'freight': 'freight_cost.xlsx',
    'prices': 'lng_prices_asia.xlsx'
}

# =============================================================================
# DATA COLUMN MAPPINGS
# =============================================================================

COLUMN_MAPPING = {
    'prices': {
        'date': 'Date',
        'market': 'Market',
        'price': 'Price'
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
# MARKET STANDARDIZATION
# =============================================================================

MARKET_MAPPING = {
    'Singapore': ['Singapore', 'SG', 'SGP', 'Singapore Hub'],
    'China': ['China', 'CN', 'CHN', 'Shanghai', 'China (Shanghai)'],
    'Japan': ['Japan', 'JP', 'JPN', 'Tokyo', 'Japan (Tokyo)']
}

MARKETS = ['Singapore', 'China', 'Japan']

# =============================================================================
# CARGO CONTRACT SPECIFICATIONS
# =============================================================================

CARGO_CONTRACT = {
    'volume_mmbtu': 3_800_000,  # Base cargo size
    'delivery_period': ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06'],
    'nomination_deadline': 'M-2',  # Must nominate by M-2
    'loading_window': 'M',  # Load in month M
    'delivery_window': 'M+1'  # Deliver in month M+1
}

# =============================================================================
# OPERATIONAL PARAMETERS
# =============================================================================

OPERATIONAL = {
    'boil_off_rate_per_day': 0.0005,  # 0.05% per day
    'storage_cost_per_mmbtu_per_month': 0.05,  # $0.05/MMBtu/month
    'voyage_days': {
        'USGC_to_Singapore': 25,
        'USGC_to_Japan': 20,
        'USGC_to_China': 22
    }
}

# =============================================================================
# TERMINAL COSTS
# =============================================================================

TERMINAL_COSTS = {
    'Singapore': 0.50,  # $0.50/MMBtu
    'Japan': 0.75,      # $0.75/MMBtu
    'China': 0.60       # $0.60/MMBtu
}

# =============================================================================
# VALIDATION THRESHOLDS
# =============================================================================

VALIDATION_THRESHOLDS = {
    'min_price': 0.0,
    'max_price': 1000.0,
    'min_cost': 0.0,
    'max_cost': 100.0
}

# =============================================================================
# MARKET STANDARDIZATION FUNCTIONS
# =============================================================================

def get_market_standard_name(market_name: str) -> str:
    """Convert market name to standard format."""
    for standard, variations in MARKET_MAPPING.items():
        if market_name in variations:
            return standard
    raise ValueError(f"Unknown market: {market_name}")

def days_to_periods(days: int, frequency: str) -> int:
    """Convert days to periods based on frequency."""
    if frequency == 'D':
        return days
    elif frequency == 'W':
        return days // 7
    elif frequency == 'M':
        return days // 30
    else:
        return days

def periods_to_days(periods: int, frequency: str) -> int:
    """Convert periods to days based on frequency."""
    if frequency == 'D':
        return periods
    elif frequency == 'W':
        return periods * 7
    elif frequency == 'M':
        return periods * 30
    else:
        return periods

# =============================================================================
# VOYAGE DAYS
# =============================================================================

VOYAGE_DAYS = {
    'USGC_to_Singapore': 25,
    'USGC_to_Japan': 20,
    'USGC_to_China': 22
}

# =============================================================================
# FREIGHT SCALING FACTORS
# =============================================================================

FREIGHT_SCALING_FACTORS = {
    'Singapore': 1.0,
    'Japan': 1.0,
    'China': 1.0
}

# =============================================================================
# SALES FORMULAS
# =============================================================================

SALES_FORMULAS = {
    'Singapore': 'brent_based',
    'Japan': 'jkm_based',
    'China': 'jkm_based'
}

# =============================================================================
# BUYERS
# =============================================================================

BUYERS = {
    'Singapore': ['Iron_Man', 'Thor'],
    'Japan': ['Hawk_Eye', 'QuickSilver'],
    'China': ['QuickSilver', 'Hawk_Eye']
}

# =============================================================================
# BUYER CREDIT RATINGS
# =============================================================================

BUYER_CREDIT_RATINGS = {
    'Iron_Man': 'AA',      # Highest credit quality
    'Thor': 'AA',          # Highest credit quality
    'Hawk_Eye': 'A',       # Strong credit quality
    'QuickSilver': 'BBB'   # Good credit quality
}

# =============================================================================
# BUYER DEMAND PROBABILITIES (from case pack page 17)
# =============================================================================

BUYER_DEMAND_PROBABILITIES = {
    'Iron_Man': 0.75,      # 75% probability of taking delivery
    'Thor': 0.70,          # 70% probability
    'Hawk_Eye': 0.65,      # 65% probability
    'QuickSilver': 0.60    # 60% probability
}

# =============================================================================
# PAYMENT TERMS
# =============================================================================

PAYMENT_TERMS = {
    'Singapore': 'immediate',  # T+0
    'Japan': 'immediate',      # T+0
    'China': '30_days'         # T+30
}

# =============================================================================
# BUYER SELECTION SCORING WEIGHTS
# =============================================================================

BUYER_SELECTION_WEIGHTS = {
    'margin': 0.50,        # 50% - Expected margin is most important
    'credit': 0.25,        # 25% - Credit risk is significant
    'demand': 0.15,        # 15% - Demand confidence matters
    'payment': 0.10        # 10% - Payment terms have modest impact
}

# Credit rating scores (0-100 scale)
CREDIT_SCORES = {
    'AA': 100,   # 0% penalty
    'A': 95,     # 5% penalty
    'BBB': 85,   # 15% penalty
    'BB': 70,    # 30% penalty
    'B': 50,     # 50% penalty
    'CCC': 30    # 70% penalty
}

# Risk-free rate for NPV calculations
RISK_FREE_RATE = 0.05  # 5% annual rate

# =============================================================================
# CREDIT DEFAULT PROBABILITY
# =============================================================================

CREDIT_DEFAULT_PROBABILITY = {
    'Iron_Man': 0.001,  # AA rating
    'Thor': 0.001,      # AA rating
    'Hawk_Eye': 0.005,  # A rating
    'QuickSilver': 0.02  # BBB rating
}

# =============================================================================
# CREDIT RECOVERY RATE
# =============================================================================

CREDIT_RECOVERY_RATE = {
    'Iron_Man': 0.40,  # 40% recovery
    'Thor': 0.40,      # 40% recovery
    'Hawk_Eye': 0.35,  # 35% recovery
    'QuickSilver': 0.30  # 30% recovery
}

# =============================================================================
# DEMAND PROFILE
# =============================================================================

DEMAND_PROFILE = {
    'Singapore': {'base_demand': 1.0, 'seasonal_factor': 1.0},
    'Japan': {'base_demand': 1.0, 'seasonal_factor': 1.2},
    'China': {'base_demand': 1.0, 'seasonal_factor': 1.1}
}

# =============================================================================
# INSURANCE COSTS
# =============================================================================

INSURANCE_COSTS = {
    'Singapore': 0.10,  # $0.10/MMBtu
    'Japan': 0.12,      # $0.12/MMBtu
    'China': 0.11       # $0.11/MMBtu
}

# =============================================================================
# BROKERAGE COSTS
# =============================================================================

BROKERAGE_COSTS = {
    'Singapore': 0.05,  # $0.05/MMBtu
    'Japan': 0.05,      # $0.05/MMBtu
    'China': 0.05       # $0.05/MMBtu
}

# =============================================================================
# WORKING CAPITAL
# =============================================================================

WORKING_CAPITAL = {
    'Singapore': 0.02,  # $0.02/MMBtu
    'Japan': 0.02,      # $0.02/MMBtu
    'China': 0.02       # $0.02/MMBtu
}

# =============================================================================
# CARBON COSTS
# =============================================================================

CARBON_COSTS = {
    'Singapore': 0.03,  # $0.03/MMBtu
    'Japan': 0.03,      # $0.03/MMBtu
    'China': 0.03       # $0.03/MMBtu
}

# =============================================================================
# DEMURRAGE COSTS
# =============================================================================

DEMURRAGE_COSTS = {
    'Singapore': 0.01,  # $0.01/MMBtu
    'Japan': 0.01,      # $0.01/MMBtu
    'China': 0.01       # $0.01/MMBtu
}

# =============================================================================
# LC COSTS
# =============================================================================

LC_COSTS = {
    'Singapore': 0.02,  # $0.02/MMBtu
    'Japan': 0.02,      # $0.02/MMBtu
    'China': 0.02       # $0.02/MMBtu
}
