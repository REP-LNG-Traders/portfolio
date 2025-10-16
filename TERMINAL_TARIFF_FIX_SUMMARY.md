# Singapore Terminal Tariff Fix - Summary

## Issue Identified

The Singapore terminal tariff was incorrectly implemented as a **fixed $/MMBtu cost**, when it should actually be a **daily fee in Singapore Dollars (SGD)** that varies with:
1. Discharge time at terminal
2. USD/SGD exchange rate
3. Cargo volume

## Source Document

From **Singapore Related Data.xlsx** (sourced from SLNG - Singapore LNG):

```
SLNG Terminal Tariff
Terminal Tariff: Cost per day in SGD [Defined as 0000-2400]
- FY2024: 150,000 SGD/day
- FY2025: 200,000 SGD/day
```

## Changes Made

### 1. Updated `config/constants.py`

#### Before:
```python
TERMINAL_COSTS = {
    'Singapore': 0.50,  # $0.50/MMBtu - WRONG!
    'Japan': 0.75,
    'China': 0.60
}

BUYERS = {
    'Singapore': ['Iron_Man', 'Thor'],  # Just a list
    ...
}

SALES_FORMULAS = {
    'Singapore': 'brent_based',  # Just a string
    ...
}
```

#### After:
```python
# New: Singapore terminal tariff configuration
SINGAPORE_TERMINAL_TARIFF = {
    'min_sgd_per_day': 150_000,  # SGD/day (FY2024)
    'max_sgd_per_day': 200_000,  # SGD/day (FY2025)
    'default_sgd_per_day': 200_000,  # Use FY2025 rate
    'discharge_time_days': 1.0
}

# New: Dynamic calculation function
def calculate_singapore_terminal_tariff_per_mmbtu(
    cargo_volume_mmbtu: float,
    usdsgd_fx_rate: float = 1.35,
    discharge_days: float = None
) -> float:
    """Calculate terminal tariff in USD/MMBtu"""
    tariff_sgd_per_day = SINGAPORE_TERMINAL_TARIFF['default_sgd_per_day']
    total_tariff_sgd = tariff_sgd_per_day * discharge_days
    total_tariff_usd = total_tariff_sgd / usdsgd_fx_rate
    return total_tariff_usd / cargo_volume_mmbtu

# Updated: BUYERS now contains full buyer info
BUYERS = {
    'Singapore': {
        'Iron_Man': {
            'premium': 4.00,
            'credit_rating': 'AA',
            'type': 'bunker'
        },
        'Thor': {
            'premium': 3.50,
            'credit_rating': 'AA',
            'type': 'utility'
        }
    },
    # ... similar for Japan and China
}

# Updated: SALES_FORMULAS includes calculation function
SALES_FORMULAS = {
    'Singapore': {
        'type': 'brent_based',
        'terminal_tariff': None,  # Calculated dynamically
        'calculate_terminal_tariff': calculate_singapore_terminal_tariff_per_mmbtu
    },
    # ... similar for Japan and China
}
```

### 2. Updated `models/optimization.py`

#### `calculate_sale_revenue()` method:
- Added `usdsgd_fx_rate` parameter (default: 1.35)
- Changed terminal tariff calculation from fixed value to dynamic function call
- Updated docstring

#### `calculate_cargo_pnl()` method:
- Added `usdsgd_fx_rate` parameter (default: 1.35)
- Passes FX rate to `calculate_sale_revenue()`
- Updated docstring

## Impact on Calculations

### Example Calculation (Standard Cargo):
- Cargo volume: 3,800,000 MMBtu
- Discharge time: 1 day
- Terminal tariff: 200,000 SGD/day
- USD/SGD FX rate: 1.35

**Calculation:**
```
Terminal Tariff ($/MMBtu) = (200,000 SGD × 1 day) ÷ 1.35 ÷ 3,800,000 MMBtu
                          = 148,148 USD ÷ 3,800,000 MMBtu
                          = $0.039/MMBtu
```

**Previously used:** $0.50/MMBtu or $0.80/MMBtu (WRONG!)

**Correctly calculated:** $0.039/MMBtu

## Important Notes

1. **FX Rate Matters**: The actual cost varies with USD/SGD exchange rate
   - If SGD strengthens (FX rate decreases): Cost goes up
   - If SGD weakens (FX rate increases): Cost goes down

2. **Volume Flexibility**: With ±10% volume tolerance:
   - Larger cargo (110% = 4.18M MMBtu): Lower $/MMBtu cost
   - Smaller cargo (90% = 3.42M MMBtu): Higher $/MMBtu cost

3. **Discharge Time**: Currently assumes 1 day. If discharge takes longer, cost increases proportionally.

4. **FX Data Available**: The system already loads USD/SGD FX data from the competition pack, so this can be integrated into the optimization.

## Next Steps

To fully utilize this fix, consider:

1. **Load FX data in optimization pipeline** to use actual FX rates by month
2. **Verify discharge time assumption** (currently 1 day)
3. **Check Japan/China port costs** - they may also need similar treatment
4. **Update documentation** to reflect this dynamic calculation

## Files Modified

- `config/constants.py` - Added dynamic terminal tariff calculation
- `models/optimization.py` - Updated to use dynamic calculation with FX rate
- Deleted temporary investigation scripts

## Testing Recommendation

Run the optimization with these changes and compare:
- Old results (with $0.50 or $0.80/MMBtu fixed)
- New results (with $0.039/MMBtu dynamic)

The Singapore route should now be **significantly more attractive** financially!

