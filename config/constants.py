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

# Singapore Terminal Tariff (from Singapore Related Data)
# Source: SLNG Terminal Tariff - Cost per day in SGD [Defined as 0000-2400]
# FY2024: 150,000 SGD/day, FY2025: 200,000 SGD/day
#
# IMPORTANT: This is NOT a fixed $/MMBtu rate - it's a daily fee that must be:
# 1. Multiplied by discharge time (days)
# 2. Converted from SGD to USD using FX rate
# 3. Divided by cargo volume to get $/MMBtu
#
# Example calculation for standard cargo (3.8M MMBtu, 1.35 FX, 1 day):
#   200,000 SGD/day × 1 day ÷ 1.35 (USD/SGD) ÷ 3,800,000 MMBtu = $0.039/MMBtu
#
SINGAPORE_TERMINAL_TARIFF = {
    'min_sgd_per_day': 150_000,  # SGD/day (FY2024)
    'max_sgd_per_day': 200_000,  # SGD/day (FY2025)
    'default_sgd_per_day': 200_000,  # Use FY2025 rate for 2026 forecast
    'discharge_time_days': 1.0  # Assume 1 day discharge time
}

# Port/Berthing costs for Japan and China (these may also need verification)
TERMINAL_COSTS = {
    'Japan': 0.75,      # $0.75/MMBtu - NEEDS VERIFICATION
    'China': 0.60       # $0.60/MMBtu - NEEDS VERIFICATION
}

# =============================================================================
# PORT FEES (Based on ~174,000 m³ LNG Carrier Analysis)
# =============================================================================
# Vessel Specifications:
# - Volume: ~174,000 m³
# - Gross Tonnage (GT): ~100,000 GT
# - Net Tonnage (NT): ~60,000 NT
# - Deadweight: ~80,000 DWT

# Helper function for time-dependent China port fees
def get_china_us_ship_fee_per_nt(cargo_month: str) -> float:
    """
    Get China US ship special port fee per net tonne based on cargo month.
    
    Timeline (China Ministry of Transport):
    - Oct 14, 2025 - Apr 16, 2026: RMB 400/NT ($56.13/NT)
    - Apr 17, 2026 - Apr 16, 2027: RMB 640/NT ($89.81/NT)
    - Apr 17, 2027 onwards: RMB 880/NT ($123.52/NT)
    
    Args:
        cargo_month: Month string in format 'YYYY-MM'
        
    Returns:
        Fee in USD per net tonne
    """
    from datetime import datetime
    
    try:
        month_date = datetime.strptime(cargo_month, '%Y-%m')
    except:
        # If parsing fails, assume period 1 (conservative)
        return 56.13
    
    # Period boundaries
    period1_end = datetime(2026, 4, 16)  # RMB 400/NT
    period2_end = datetime(2027, 4, 16)  # RMB 640/NT
    
    if month_date <= period1_end:
        return 56.13  # $56.13/NT (RMB 400)
    elif month_date <= period2_end:
        return 89.81  # $89.81/NT (RMB 640)
    else:
        return 123.52  # $123.52/NT (RMB 880)

def calculate_china_us_ship_fee(cargo_month: str, vessel_net_tonnage: float = 60000) -> float:
    """
    Calculate total China US ship special port fee.
    
    Args:
        cargo_month: Month string in format 'YYYY-MM'
        vessel_net_tonnage: Vessel net tonnage (default: 60,000 NT for 174k m³ carrier)
        
    Returns:
        Total fee in USD
    """
    fee_per_nt = get_china_us_ship_fee_per_nt(cargo_month)
    return fee_per_nt * vessel_net_tonnage

PORT_FEES = {
    'vessel_specs': {
        'volume_m3': 174000,      # Cubic meters
        'gross_tonnage': 100000,   # GT
        'net_tonnage': 60000,      # NT
        'deadweight': 80000        # DWT
    },
    
    'Singapore': {
        'port_dues': {
            'description': 'Based on GT and stay duration',
            'base_calculation': 'GT/100 × rate_per_100GT',
            'stay_1_day': 2000,    # $ per call (100k GT × 2.00)
            'stay_2_days': 6000,   # $ per call (100k GT × 6.00) - typical LNG discharge
            'stay_3_days': 9000,   # $ per call (100k GT × 9.00)
            'typical': 6000        # Use 2-day rate as default
        },
        'maritime_welfare_fee': 175,    # $ per call (vessels >40k GT)
        'pilotage': {
            'description': 'Inbound + outbound operations',
            'per_operation': 16500,  # $ per operation (¥5,000-20,000 range)
            'total': 33000           # $ per call (in + out)
        },
        'mooring_wharfage': 7500,       # $ per call
        'entry_fee': {
            'normal_rate': 285000,  # $ per call (¥2.70/GT × 100k GT) if not waived
            'waived_until': '2026-03-31',
            'current': 0            # WAIVED for LNG vessels until March 31, 2026
        },
        'total_per_call': 46675,        # Port dues + welfare + pilotage + mooring (entry fee waived)
        'per_mmbtu': 0.012              # Total / 3.8M MMBtu
    },
    
    'Japan': {
        'port_dues': 13500,            # $ per call (estimate for 100k GT)
        'pilotage': 25000,             # $ per call (in + out)
        'tug_assistance': 20000,       # $ per call
        'other_fees': 7500,            # $ per call (mooring, customs, etc.)
        'total_per_call': 66000,
        'per_mmbtu': 0.017             # Total / 3.8M MMBtu
    },
    
    'China': {
        'us_ship_classification': True,  # IMPORTANT: US Gulf Coast origin = US ship
        'net_tonnage': 60000,           # Used for special fee calculation
        
        'us_ship_special_fee': {
            'description': 'Special Port Fee for US ships at Chinese ports',
            'source': 'China Ministry of Transport',
            'calculation_function': calculate_china_us_ship_fee,
            
            'rate_schedule': {
                'period_1': {
                    'dates': 'Oct 14, 2025 - Apr 16, 2026',
                    'rate_per_nt_usd': 56.13,   # RMB 400/NT
                    'rate_per_nt_rmb': 400,
                    'total_for_60k_nt': 3367800  # $56.13 × 60,000 NT
                },
                'period_2': {
                    'dates': 'Apr 17, 2026 - Apr 16, 2027',
                    'rate_per_nt_usd': 89.81,   # RMB 640/NT
                    'rate_per_nt_rmb': 640,
                    'total_for_60k_nt': 5388600  # $89.81 × 60,000 NT
                },
                'period_3': {
                    'dates': 'Apr 17, 2027 onwards',
                    'rate_per_nt_usd': 123.52,  # RMB 880/NT
                    'rate_per_nt_rmb': 880,
                    'total_for_60k_nt': 7411200  # $123.52 × 60,000 NT
                }
            },
            
            # For our cargo months (Jan-Jun 2026):
            'jan_2026': 3367800,  # Period 1 rate
            'feb_2026': 3367800,  # Period 1 rate
            'mar_2026': 3367800,  # Period 1 rate
            'apr_2026': 3367800,  # Period 1 rate (before Apr 17)
            'may_2026': 5388600,  # Period 2 rate (after Apr 17)
            'jun_2026': 5388600   # Period 2 rate
        },
        
        'standard_port_fees': {
            'berthing_handling': 840,    # $ per call (RMB 6,000 ≈ $840)
            'pilotage_towage': 5600,     # $ per call (RMB 40,000 ≈ $5,600)
            'customs_inspection': 1400,   # $ per call (RMB 10,000 ≈ $1,400)
            'total': 7840
        },
        
        'total_per_call_with_us_fee': {
            'jan_apr_2026': 3375640,     # US special fee (period 1) + standard fees
            'may_jun_2026': 5396440      # US special fee (period 2) + standard fees
        },
        
        'per_mmbtu': {
            'jan_apr_2026': 0.888,       # $3,375,640 / 3.8M MMBtu
            'may_jun_2026': 1.420        # $5,396,440 / 3.8M MMBtu
        },
        
        'note': '⚠️ US ship classification adds $3.4-5.4M per call - likely makes China uneconomical!'
    }
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

def calculate_singapore_terminal_tariff_per_mmbtu(
    cargo_volume_mmbtu: float,
    usdsgd_fx_rate: float = 1.35,  # Default FX rate if not provided
    discharge_days: float = None
) -> float:
    """
    Calculate Singapore terminal tariff per MMBtu.
    
    From Singapore Related Data:
    - Terminal Tariff: 150,000 to 200,000 SGD/day (FY2024-2025)
    - Using 200,000 SGD/day for 2026 forecast
    
    Args:
        cargo_volume_mmbtu: Cargo size in MMBtu
        usdsgd_fx_rate: USD/SGD exchange rate
        discharge_days: Discharge time in days (default: 1.0)
    
    Returns:
        Terminal tariff in USD per MMBtu
    """
    if discharge_days is None:
        discharge_days = SINGAPORE_TERMINAL_TARIFF['discharge_time_days']
    
    tariff_sgd_per_day = SINGAPORE_TERMINAL_TARIFF['default_sgd_per_day']
    total_tariff_sgd = tariff_sgd_per_day * discharge_days
    total_tariff_usd = total_tariff_sgd / usdsgd_fx_rate
    tariff_per_mmbtu = total_tariff_usd / cargo_volume_mmbtu
    
    return tariff_per_mmbtu


SALES_FORMULAS = {
    'Singapore': {
        'type': 'brent_based',
        'terminal_tariff': None,  # Will be calculated dynamically
        'calculate_terminal_tariff': calculate_singapore_terminal_tariff_per_mmbtu
    },
    'Japan': {
        'type': 'jkm_based',
        'berthing_cost': 0.10  # $0.10/MMBtu from case pack page 16
    },
    'China': {
        'type': 'jkm_based',
        'berthing_cost': 0.10  # $0.10/MMBtu from case pack page 16
    }
}

# =============================================================================
# BUYERS
# =============================================================================

# Buyer information with premiums and credit ratings
# Premiums from case pack and documentation
BUYERS = {
    'Singapore': {
        'Iron_Man': {
            'premium': 4.00,  # $/MMBtu
            'credit_rating': 'AA',
            'type': 'bunker'
        },
        'Thor': {
            'premium': 3.50,  # $/MMBtu (LOW end due to AA negotiating power)
            'credit_rating': 'AA',
            'type': 'utility'
        }
    },
    'Japan': {
        'Hawk_Eye': {
            'premium': 0.60,  # $/MMBtu (LOW end due to strong negotiator)
            'credit_rating': 'A',
            'type': 'utility'
        },
        'QuickSilver': {
            'premium': 2.20,  # $/MMBtu
            'credit_rating': 'BBB',
            'type': 'trader'
        }
    },
    'China': {
        'QuickSilver': {
            'premium': 2.20,  # $/MMBtu
            'credit_rating': 'BBB',
            'type': 'trader'
        },
        'Hawk_Eye': {
            'premium': 0.60,  # $/MMBtu
            'credit_rating': 'A',
            'type': 'utility'
        }
    }
}

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
