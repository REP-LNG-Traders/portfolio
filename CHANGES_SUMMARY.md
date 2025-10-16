# Summary: Singapore Terminal Tariff Fix

## What Was Wrong ❌

The terminal tariff was hardcoded as:
- **Config**: `$0.50/MMBtu`
- **Documentation**: `$0.80/MMBtu` 

Both were **completely wrong**!

## What It Should Be ✅

From the official **Singapore Related Data.xlsx** (SLNG terminal):

```
Terminal Tariff: 200,000 SGD per day
```

This is **NOT a per-MMBtu rate**. It must be:
1. Converted from SGD to USD using FX rate
2. Divided by cargo volume

**Correct calculation** for standard cargo:
```
200,000 SGD/day ÷ 1.35 (FX) ÷ 3,800,000 MMBtu = $0.039/MMBtu
```

## Files Changed

1. **`config/constants.py`**
   - Added `SINGAPORE_TERMINAL_TARIFF` config dict
   - Added `calculate_singapore_terminal_tariff_per_mmbtu()` function
   - Updated `BUYERS` to include full buyer details (premium, credit rating)
   - Updated `SALES_FORMULAS` to include calculation functions

2. **`models/optimization.py`**
   - Added `usdsgd_fx_rate` parameter to `calculate_sale_revenue()`
   - Added `usdsgd_fx_rate` parameter to `calculate_cargo_pnl()`
   - Changed terminal tariff from fixed lookup to dynamic calculation

## Impact 💰

**Per cargo:**
- Old (wrong): $0.50/MMBtu × 3.8M MMBtu = $1,900,000 cost
- New (correct): $0.039/MMBtu × 3.8M MMBtu = $148,148 cost
- **Savings: ~$1.75M per cargo!**

**Over 6 months (6 cargoes):**
- **Total additional profit: ~$10.5M**

**This makes Singapore routes MUCH more attractive!**

## Testing ✅

Run `python test_terminal_tariff.py` to verify:
- Standard cargo: $0.039/MMBtu
- Large cargo (110%): $0.035/MMBtu  
- Small cargo (90%): $0.043/MMBtu
- Different FX rates: Varies appropriately

All tests passing ✅

## Backward Compatibility ✅

All existing code continues to work because:
- Default FX rate = 1.35 (reasonable assumption)
- Parameter is optional in function signatures
- No breaking changes to existing calls

## What You Found 🎯

You correctly identified that the source document shows:
- **150,000 to 200,000 SGD per day** (not per MMBtu)
- This is a daily terminal fee
- Must be calculated dynamically

**Great catch!** This is exactly the kind of detail that wins competitions.

## To Use in Optimization

The code is ready to use. Optionally:
1. Load actual FX data month-by-month (already available in `data['fx']`)
2. Pass `usdsgd_fx_rate=forecasts['fx'][month]` in optimization calls
3. Or just use default 1.35 - impact is minimal (~$5K variation vs $1.75M savings)

---

**Status**: ✅ Complete and tested
**Priority**: ⭐⭐⭐ High impact fix ($10.5M over 6 cargoes)
**Risk**: Low - backward compatible, well tested

