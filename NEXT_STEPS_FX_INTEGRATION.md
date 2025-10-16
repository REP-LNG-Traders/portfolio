# Next Steps: FX Rate Integration

## Current Status ✅

The terminal tariff calculation has been successfully updated to be **dynamic** rather than fixed:

- **Function created**: `calculate_singapore_terminal_tariff_per_mmbtu()`
- **Default FX rate**: 1.35 (USD/SGD)
- **Result**: ~$0.039/MMBtu (vs old incorrect $0.50/MMBtu)
- **Impact**: ~$1.8M more profit per cargo, ~$10.5M over 6 cargoes!

## Current Behavior

All existing code continues to work using the **default FX rate of 1.35**:
```python
result = calculator.calculate_cargo_pnl(
    month='2026-01',
    destination='Singapore',
    buyer='Thor',
    henry_hub_price=3.0,
    jkm_price=15.0,
    jkm_price_next_month=15.5,
    brent_price=75.0,
    freight_rate=18000
    # usdsgd_fx_rate defaults to 1.35
)
```

## Optional Enhancement: Use Actual FX Data

The system already loads USD/SGD FX data in `load_all_data()`:
```python
data = load_all_data()
# data['fx'] contains USD/SGD exchange rates
```

To use actual FX rates by month, modify `main_optimization.py`:

### Option 1: Extract FX rates in forecast preparation

```python
def prepare_forecasts_simple(data: dict) -> Dict[str, pd.Series]:
    """Prepare price forecasts for Jan-Jul 2026."""
    # ... existing code ...
    
    # Add FX forecast
    logger.info("\n5. FX Rate: Using latest historical value...")
    fx_latest = data['fx']['USDSGD'].iloc[-1]
    fx_forecast_dict = {month.strftime('%Y-%m'): fx_latest for month in months}
    forecasts['fx'] = pd.Series(fx_forecast_dict, name='fx')
    
    return forecasts
```

### Option 2: Pass FX rate in strategy generation

In `StrategyOptimizer.generate_optimal_strategy()`:
```python
result = self.calculator.calculate_cargo_pnl(
    month=month,
    destination=destination,
    buyer=buyer,
    henry_hub_price=forecasts['henry_hub'][month],
    jkm_price=forecasts['jkm'][month],
    jkm_price_next_month=forecasts['jkm'].get(next_month_str, ...),
    brent_price=forecasts['brent'][month],
    freight_rate=forecasts['freight'][month],
    cargo_volume=optimal_volume,
    usdsgd_fx_rate=forecasts['fx'][month]  # ← ADD THIS
)
```

## When to Worry About FX

The default FX rate (1.35) is reasonable for the calculation. Only implement actual FX integration if:

1. **FX volatility is high** during the forecast period
2. **Precision matters** for close optimization decisions
3. **You have time** and want to be thorough

## Impact Analysis

| Scenario | FX Rate | Terminal Tariff | Impact vs Default |
|----------|---------|----------------|-------------------|
| Default (current) | 1.35 | $0.0390/MMBtu | Baseline |
| SGD weakens | 1.40 | $0.0376/MMBtu | +$0.0014/MMBtu (~$5K savings) |
| SGD strengthens | 1.30 | $0.0405/MMBtu | -$0.0015/MMBtu (~$6K cost) |

Per cargo impact: ~$5-6K variation
Over 6 cargoes: ~$30-36K variation

**Conclusion**: FX variation has **minimal impact** compared to the ~$1.8M we just saved by fixing the calculation method!

## Recommendation

✅ **Current implementation is good enough for competition**
- The fix from $0.50 → $0.039 is the big win
- FX variation is noise compared to that
- Default 1.35 is reasonable

🎯 **Focus on other priorities:**
1. Verify discharge time assumption (1 day)
2. Check Japan/China port costs  
3. Run full optimization and compare strategies
4. Validate with mentors/organizers

💡 **If you have extra time:**
- Integrate actual FX data (straightforward as shown above)
- Test sensitivity to FX scenarios
- Document FX assumptions in final report

