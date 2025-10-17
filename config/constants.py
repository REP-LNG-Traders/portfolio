"""
Business constants and parameters.

KEY ASSUMPTIONS:
===============

1. CURRENCY ASSUMPTION (FX RISK):
   - All prices, costs, and revenues are assumed to be in USD
   - Singapore sales: Assumed USD-denominated (not SGD conversion)
   - Rationale: Common industry practice; simplifies analysis
   - FX data loaded but not used (out of scope for this analysis)
   - Note: In practice, Singapore LNG trades in USD despite location
   
2. PRICE ASSUMPTIONS:
   - Henry Hub: Uses NYMEX NG forward curve (most liquid, reliable)
   - JKM: Uses forward curve where available, ARIMA+GARCH for extensions
   - Brent: Historical data, ARIMA+GARCH for forecasting
   - Freight: Baltic LNG data with monthly aggregation to handle volatility
   
3. OPERATIONAL ASSUMPTIONS:
   - Boil-off: 0.05%/day (industry standard for modern LNG carriers)
   - Voyage days: USGC to Singapore (25d), Japan (20d), China (22d)
   - Volume flexibility: ±10% per contract terms (case pack page 15)
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
    'volume_mmbtu': 3_800_000,  # Base cargo size (PURCHASE contract)
    'delivery_period': ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06'],
    'nomination_deadline': 'M-2',  # Must nominate by M-2
    'loading_window': 'M',  # Load in month M
    'delivery_window': 'M+1',  # Deliver in month M+1
    'tolling_fee': 1.50,  # $1.50/MMBtu tolling fee (from contract terms - CORRECTED)
    'decision_timeline': {
        '2026-01': '2025-11',  # November 2025: Decide on January 2026 cargo
        '2026-02': '2025-12',  # December 2025: Decide on February 2026 cargo
        '2026-03': '2026-01',  # January 2026: Decide on March 2026 cargo
        '2026-04': '2026-02',  # February 2026: Decide on April 2026 cargo
        '2026-05': '2026-03',  # March 2026: Decide on May 2026 cargo
        '2026-06': '2026-04'   # April 2026: Decide on June 2026 cargo
    }
}

# =============================================================================
# OPERATIONAL PARAMETERS
# =============================================================================

OPERATIONAL = {
    'boil_off_rate_per_day': 0.0005,  # 0.05% per day
    'storage_cost_per_mmbtu_per_month': 0.05,  # $0.05/MMBtu/month
    'voyage_days': {
        'USGC_to_Singapore': 48,  # 47.92 days from case materials (2025 data)
        'USGC_to_Japan': 41,      # 41.45 days from case materials (2025 data)
        'USGC_to_China': 52       # 51.79 days from case materials (2025 data)
    }
}

# =============================================================================
# CHINA SPECIAL PORT FEE - US-LINKED VESSELS
# =============================================================================
# Reference: Shanghai Yangshan Port Fees for US ships
# Special Port Fee for vessels under US ownership or operation
# Capped at 5 port calls/year; applies to US-linked vessels only
#
# SOURCE: Competition case materials - Shanghai Yangshan Port Fee schedule
#
# RATES:
# - From Oct 14, 2025 to Apr 16, 2026: RMB 400 per net tonne (≈ US$56)
# - From Apr 17, 2026 onwards: RMB 640 per net tonne (≈ US$90)
#
# VESSEL ASSUMPTIONS:
# - Typical LNG carrier capacity: 174,000 m³
# - Net tonnage: ~70,000 net tonnes (standard for this vessel size)
#
# COST IMPACT:
# - Jan-Mar 2026: 70,000 NT × $56 = $3,920,000 per port call
# - Apr-Jun 2026: 70,000 NT × $90 = $6,300,000 per port call
# - Per MMBtu (4.2M cargo): $0.93/MMBtu (Jan-Mar), $1.50/MMBtu (Apr-Jun)

SPECIAL_PORT_FEE = {
    'enabled': True,
    'jurisdiction': 'China',  # Only applies to China (Shanghai Yangshan Port)
    'vessel_net_tonnage': 70000,  # Net tonnes for typical 174,000 m³ LNG carrier
    'fee_schedule': {
        # RMB per net tonne, with USD conversion
        'period_1': {
            'start_date': '2025-10-14',
            'end_date': '2026-04-16',
            'rmb_per_net_tonne': 400,
            'usd_per_net_tonne': 56,  # RMB 400 ≈ US$56 per case materials
            'exchange_rate': 7.14  # RMB/USD (400/56)
        },
        'period_2': {
            'start_date': '2026-04-17',
            'end_date': '2026-12-31',
            'rmb_per_net_tonne': 640,
            'usd_per_net_tonne': 90,  # RMB 640 ≈ US$90 per case materials
            'exchange_rate': 7.11  # RMB/USD (640/90)
        }
    },
    'total_fee_period_1': 3920000,  # $56 × 70,000 NT = $3.92M
    'total_fee_period_2': 6300000,  # $90 × 70,000 NT = $6.30M
    'note': 'Special Port Fee for US-linked vessels; standard fees lower for non-US vessels'
}

# =============================================================================
# BIOLNG MANDATE (Singapore) - NEW REGULATION
# =============================================================================

BIOLNG_MANDATE = {
    'enabled': True,
    'jurisdiction': 'Singapore',  # Only applies to Singapore
    'mandate_percentage': 0.05,  # 5% BioLNG required
    'our_biolng_content': 0.00,  # We have 0% BioLNG (no change to cargo)
    'penalty_sgd_per_mt': 30,  # 30 SGD per metric tonne on shortfall
    'sgd_to_usd': 0.74,  # Approximate exchange rate: 1 SGD = 0.74 USD (1.35 SGD/USD)
    'lng_mmbtu_to_mt': 1/48,  # 1 metric tonne LNG ≈ 48 MMBtu (industry standard)
    'note': 'Penalty applies to entire 5% shortfall since we have 0% BioLNG content'
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
    'USGC_to_Singapore': 48,  # 47.92 days from case materials (2025 data)
    'USGC_to_Japan': 41,      # 41.45 days from case materials (2025 data)
    'USGC_to_China': 52       # 51.79 days from case materials (2025 data)
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
    'Singapore': {
        'type': 'brent_based',
        'terminal_tariff': None,  # Will be calculated dynamically
        'berthing_cost': 0.0,     # Not applicable for Singapore
        'payment_terms': 'immediate',  # T+0
        'calculate_terminal_tariff': 'calculate_singapore_terminal_tariff_per_mmbtu'  # Dynamic calculation
    },
    'Japan': {
        'type': 'jkm_based',
        'terminal_tariff': 0.0,       # Not applicable for Japan
        'berthing_cost': 0.10,        # $0.10/MMBtu from case pack page 16
        'payment_terms': 'immediate'  # T+0
    },
    'China': {
        'type': 'jkm_based',
        'terminal_tariff': 0.0,       # Not applicable for China
        'berthing_cost': 0.10,        # $0.10/MMBtu from case pack page 16
        'payment_terms': '30_days_after_delivery'  # T+30
    }
}

# =============================================================================
# BUYERS
# =============================================================================

# FILTERED TO A-RATED AND ABOVE ONLY (AA, A)
BUYERS = {
    'Singapore': {
        'Iron_Man': {
            'premium': 4.00,  # $/MMBtu (A-rated, moderate negotiating power)
            'credit_rating': 'A',
            'type': 'bunker'
        },
        'Thor': {
            'premium': 3.50,  # $/MMBtu (AA-rated, strong negotiator - gets discount)
            'credit_rating': 'AA',
            'type': 'utility'
        }
    },
    'Japan': {
        'Hawk_Eye': {
            'premium': 0.60,  # $/MMBtu (AA-rated, strong negotiator - gets discount)
            'credit_rating': 'AA',
            'type': 'utility'
        }
    },
    'China': {
        'QuickSilver': {
            'premium': 2.20,  # $/MMBtu (A-rated, moderate negotiator)
            'credit_rating': 'A',
            'type': 'trader'
        }
    }
}

# =============================================================================
# BUYER CREDIT RATINGS (by destination and buyer)
# =============================================================================

# FILTERED TO A-RATED AND ABOVE ONLY
BUYER_CREDIT_RATINGS = {
    'Iron_Man': 'A',       # CORRECTED: Case page 18 shows A-rated
    'Thor': 'AA',          # Highest credit quality (CORRECT)
    'Hawk_Eye': 'AA',      # CORRECTED: Case page 18 shows AA-rated
    'QuickSilver': 'A'     # CORRECTED: Case page 18 shows A-rated
}

# =============================================================================
# BUYER DEMAND PROBABILITIES (from case pack page 17)
# =============================================================================

# FILTERED TO A-RATED AND ABOVE ONLY
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

# FILTERED TO A-RATED AND ABOVE ONLY
CREDIT_DEFAULT_PROBABILITY = {
    # By buyer name
    'Iron_Man': 0.005,  # CORRECTED: A rating (was 0.001 for AA)
    'Thor': 0.001,      # AA rating (CORRECT)
    'Hawk_Eye': 0.001,  # CORRECTED: AA rating (was 0.005 for A)
    'QuickSilver': 0.005,  # CORRECTED: A rating (was 0.02 for BBB)
    # By rating (for lookup by rating)
    'AA': 0.001,
    'A': 0.005,
    'BBB': 0.02,
    'BB': 0.05,
    'B': 0.10,
    'CCC': 0.20
}

# =============================================================================
# CREDIT RECOVERY RATE
# =============================================================================

# FILTERED TO A-RATED AND ABOVE ONLY
CREDIT_RECOVERY_RATE = {
    # By buyer name
    'Iron_Man': 0.35,  # CORRECTED: A rating (was 0.40 for AA)
    'Thor': 0.40,      # 40% recovery (CORRECT for AA)
    'Hawk_Eye': 0.40,  # CORRECTED: AA rating (was 0.35 for A)
    'QuickSilver': 0.35,  # CORRECTED: A rating (was 0.30 for BBB)
    # By rating (for lookup by rating)
    'AA': 0.40,
    'A': 0.35,
    'BBB': 0.30,
    'BB': 0.25,
    'B': 0.20,
    'CCC': 0.10
}

# =============================================================================
# DEMAND PROFILE
# =============================================================================

DEMAND_PROFILE = {
    'Singapore': {
        'base_demand': 1.0, 
        'seasonal_factor': 1.0,
        'monthly_demand': {
            '2026-01': 0.10,  # 10% demand in Jan
            '2026-02': 0.25,  # 25% demand in Feb
            '2026-03': 0.50,  # 50% demand in Mar
            '2026-04': 0.50,  # 50% demand in Apr
            '2026-05': 0.65,  # 65% demand in May (midpoint of 50-80%)
            '2026-06': 0.65,  # 65% demand in Jun (midpoint of 50-80%)
            '2026-07': 0.80,  # 80% demand in Jul
            '2026-08': 0.90,  # 90% demand in Aug onwards
            '2026-09': 0.90,  # 90% demand in Sep onwards
            '2026-10': 0.90,  # 90% demand in Oct onwards
            '2026-11': 0.90,  # 90% demand in Nov onwards
            '2026-12': 0.90   # 90% demand in Dec onwards
        }
    },
    'Japan': {
        'base_demand': 1.0, 
        'seasonal_factor': 1.2,
        'monthly_demand': {
            '2026-01': 0.05,  # 5% demand in Jan
            '2026-02': 0.25,  # 25% demand in Feb
            '2026-03': 0.25,  # 25% demand in Mar
            '2026-04': 0.70,  # 70% demand in Apr
            '2026-05': 0.70,  # 70% demand in May
            '2026-06': 0.70,  # 70% demand in Jun
            '2026-07': 0.70,  # 70% demand in Jul
            '2026-08': 0.80,  # 80% demand in Aug onwards (midpoint of 70-90%)
            '2026-09': 0.80,  # 80% demand in Sep onwards
            '2026-10': 0.80,  # 80% demand in Oct onwards
            '2026-11': 0.80,  # 80% demand in Nov onwards
            '2026-12': 0.80   # 80% demand in Dec onwards
        }
    },
    'China': {
        'base_demand': 1.0, 
        'seasonal_factor': 1.1,
        'monthly_demand': {
            '2026-01': 0.10,  # 10% demand in Jan
            '2026-02': 0.25,  # 25% demand in Feb
            '2026-03': 0.25,  # 25% demand in Mar
            '2026-04': 0.50,  # 50% demand in Apr
            '2026-05': 0.60,  # 60% demand in May (midpoint of 50-70%)
            '2026-06': 0.60,  # 60% demand in Jun (midpoint of 50-70%)
            '2026-07': 0.60,  # 60% demand in Jul (midpoint of 50-70%)
            '2026-08': 0.70,  # 70% demand in Aug onwards
            '2026-09': 0.70,  # 70% demand in Sep onwards
            '2026-10': 0.70,  # 70% demand in Oct onwards
            '2026-11': 0.70,  # 70% demand in Nov onwards
            '2026-12': 0.70   # 70% demand in Dec onwards
        }
    }
}

# =============================================================================
# INSURANCE COSTS
# =============================================================================

INSURANCE_COSTS = {
    'per_voyage': 150000,  # $150k per voyage
    'Singapore': 0.10,     # $0.10/MMBtu (alternative calculation)
    'Japan': 0.12,         # $0.12/MMBtu
    'China': 0.11          # $0.11/MMBtu
}

# =============================================================================
# BROKERAGE COSTS
# =============================================================================

BROKERAGE_COSTS = {
    'rate': 0.015,      # 1.5% of base freight cost
    'Singapore': 0.05,  # $0.05/MMBtu (alternative)
    'Japan': 0.05,      # $0.05/MMBtu
    'China': 0.05       # $0.05/MMBtu
}

# =============================================================================
# WORKING CAPITAL
# =============================================================================

WORKING_CAPITAL = {
    'annual_rate': 0.05,  # 5% annual rate for working capital cost
    'Singapore': 0.02,    # $0.02/MMBtu (alternative)
    'Japan': 0.02,        # $0.02/MMBtu
    'China': 0.02         # $0.02/MMBtu
}

# =============================================================================
# CARBON COSTS (2026 Regional Carbon Pricing)
# =============================================================================
# Based on 473 tons CO₂/day from LNG carrier operations
# (150 tons fuel/day × 3.15 emission factor)
#
# Regional carbon prices reflect 2026 government policies:
# - Singapore: S$50/ton transition rate → $37 USD/ton
# - Japan: Voluntary carbon market → $20 USD/ton
# - China: National ETS rate → $12 USD/ton (if expanded to maritime)

CARBON_COSTS = {
    'by_destination': {
        'Singapore': {
            'rate_per_day': 17500,  # $17.5k/day ($37/ton × 473 tons CO₂/day)
            'carbon_price_per_ton': 37,
            'source': 'Singapore 2026-2030 carbon tax roadmap (S$50/ton)'
        },
        'Japan': {
            'rate_per_day': 9500,   # $9.5k/day ($20/ton × 473 tons CO₂/day)
            'carbon_price_per_ton': 20,
            'source': 'Japan voluntary carbon market baseline'
        },
        'China': {
            'rate_per_day': 5700,   # $5.7k/day ($12/ton × 473 tons CO₂/day)
            'carbon_price_per_ton': 12,
            'source': 'China ETS rate (if expanded to maritime)'
        }
    },
    'assumptions': {
        'daily_co2_emissions_tons': 473,
        'fuel_consumption_tons_per_day': 150,
        'emission_factor_co2_per_fuel_ton': 3.15
    },
    'note': 'Updated Oct 2025 based on 2026 regional carbon policy research'
}

# =============================================================================
# DEMURRAGE COSTS
# =============================================================================

DEMURRAGE_COSTS = {
    'expected_cost': 50000,  # $50k expected demurrage per voyage
    'Singapore': 0.01,       # $0.01/MMBtu (alternative)
    'Japan': 0.01,           # $0.01/MMBtu
    'China': 0.01            # $0.01/MMBtu
}

# =============================================================================
# LC COSTS
# =============================================================================

LC_COSTS = {
    'rate': 0.001,        # 0.1% of sale value
    'minimum_fee': 25000, # $25k minimum LC fee
    'Singapore': 0.02,    # $0.02/MMBtu (alternative)
    'Japan': 0.02,        # $0.02/MMBtu
    'China': 0.02         # $0.02/MMBtu
}
