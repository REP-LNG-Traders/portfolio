# Critical Gaps Analysis - User's Excellent Catch

**Date:** October 17, 2025  
**Status:** Investigating two CRITICAL gaps

---

## 🚨 GAP 1: CANCELLATION OPTION ANALYSIS

### User's Question
> "Are you actually evaluating cancellation vs. lifting for each cargo?"

### Investigation Results

**✅ GOOD NEWS: Cancellation IS Being Evaluated!**

```python
# models/optimization.py line 703-705
def evaluate_all_options_for_month():
    # Option 1: Cancel (no volume optimization needed)
    cancel_result = self.calculator.calculate_cancel_option(month)
    options.append(cancel_result)
    
    # Options 2-N: Each destination + buyer combination
    for destination in BUYERS.keys():
        for buyer in BUYERS[destination].keys():
            # Calculate P&L for lifting
            ...
```

**Cancellation Economics:**
- Tolling fee: $2.50/MMBtu × 3.8M MMBtu = **$9.5M loss**
- This is evaluated as an option for EVERY month
- Optimization picks max(all options) including cancellation

**January 2026 Example:**
```
Options evaluated:
1. Cancel: -$9.5M
2. Singapore/Iron_Man: +$3.21M  ← SELECTED
3. Singapore/Thor: +$2.8M
4. Japan/Hawk_Eye: +$2.5M
...

Decision: LIFT (since $3.21M > -$9.5M)
```

### Wait - Tolling Fee Discrepancy!

**User said:** $1.50/MMBtu → $5.7M cancellation cost  
**Model has:** $2.50/MMBtu → $9.5M cancellation cost

**Which is correct?**

Need to check case materials. If tolling fee is actually $1.50:
- Line 79 in `config/constants.py` should be: `'tolling_fee': 1.50`
- This would make cancellation more attractive (-$5.7M vs -$9.5M)
- But still wouldn't change January decision ($3.21M > -$5.7M)

### Conclusion on GAP 1

✅ **Cancellation analysis IS implemented**
✅ **Evaluated for every month**
✅ **Properly compared against lifting options**
⚠️ **Need to verify tolling fee** ($1.50 vs $2.50)

**For presentation:**
> "We evaluated cancellation economics for all 6 base cargoes. With a tolling fee of $2.50/MMBtu ($9.5M per cargo), analysis shows expected contribution margins range from $3.2M (January) to $24.3M (May), all significantly exceeding the cancellation cost threshold. Therefore, optimal strategy lifts all base cargoes."

---

## 🚨 GAP 2: SALES VOLUME CONSTRAINT VIOLATION

### User's Critical Observation

**Purchase Contract:** 3.8M MMBtu ±10% = 3.42M to 4.18M  
**Sales Contract:** 3.7M MMBtu ±10% = 3.33M to 4.07M ← **DIFFERENT!**

**Current Model Behavior:**
```
Purchase: 4.18M MMBtu (110% of 3.8M)
Voyage boil-off (48 days @ 0.05%/day): -100k MMBtu (2.4%)
Delivered at port: 4.08M MMBtu

PROBLEM: 4.08M > 4.07M (max sales volume)!
```

**Questions to Answer:**
1. Does model cap sales at 4.07M?
2. What happens to 10k MMBtu excess?
   - Vented as boil-off?
   - Sold in spot market?
   - Stored?
   - Penalty?

### Investigation: Current Implementation

```python
# config/settings.py
VOLUME_FLEXIBILITY_CONFIG = {
    'base_volume_mmbtu': 3_800_000,  # Purchase contract base
    'min_volume_mmbtu': 3_420_000,   # 90% of purchase
    'max_volume_mmbtu': 4_180_000,   # 110% of purchase
}
```

**FINDING:** Model only has ONE volume constraint (purchase), not TWO!

### Root Cause Analysis

**Assumption Made:** Purchase volume = Sales volume  
**Reality:** TWO SEPARATE CONTRACTS with different bases!

```
Purchase Contract: 3.8M ±10%
Sales Contract:    3.7M ±10%

This 100k MMBtu difference (2.6%) is likely to account for:
1. Boil-off during voyage
2. Heel gas remaining in tanks
3. Other operational losses
```

### Impact Calculation

**Scenario: Singapore Cargo at 110% Purchase**

```
Step 1: Purchase
  Contract allows: 3.8M × 110% = 4.18M MMBtu

Step 2: Voyage (48 days)
  Boil-off: 4.18M × 0.0005 × 48 = 100,320 MMBtu (2.4%)
  Delivered: 4.18M - 100k = 4.08M MMBtu

Step 3: Sales Contract Check
  Max allowed: 3.7M × 110% = 4.07M MMBtu
  Excess: 4.08M - 4.07M = 10,000 MMBtu ❌ VIOLATION

Step 4: What happens to excess?
  Option A: Sell in spot market (additional revenue?)
  Option B: Vent as boil-off (loss)
  Option C: Contract penalty (cost)
  Option D: Can't physically deliver (violation)
```

### Possible Interpretations

**Interpretation 1: Volume Tolerance is for SALES, not PURCHASE**
```python
# Purchase is FIXED at 3.8M
# Sales can vary ±10% of 3.7M = 3.33M to 4.07M

# After 2.4% boil-off:
# 3.8M → 3.71M delivered

# This fits within 3.7M ±10% range! ✓
```

**Interpretation 2: Optimization should respect BOTH constraints**
```python
# Constraint 1: Purchase ≤ 4.18M
# Constraint 2: Delivered ≤ 4.07M

# For 48-day voyage with 2.4% loss:
# Max purchase = 4.07M / (1 - 0.024) = 4.17M

# So effectively:
# Max purchase for Singapore = 4.17M (not 4.18M)
# Max purchase for Japan (2.05% loss) = 4.15M
# Max purchase for China (2.6% loss) = 4.18M ✓
```

**Interpretation 3: Two Separate Dimensions**
```python
# Volume tolerance applies to BOTH independently:
# Purchase: 3.8M ±10%
# Sales: 3.7M ±10%

# Optimization window:
# Can buy: 3.42M to 4.18M
# Can sell: 3.33M to 4.07M

# Must ensure: Delivered volume ∈ [3.33M, 4.07M]
```

### Recommended Fix

**MOST LIKELY INTERPRETATION:** Sales contract is 3.7M ±10%

```python
# config/settings.py - ADD SALES CONSTRAINT
SALES_CONTRACT = {
    'base_volume_mmbtu': 3_700_000,  # Sales contract base (NOT 3.8M!)
    'min_volume_mmbtu': 3_330_000,   # 90% of sales
    'max_volume_mmbtu': 4_070_000,   # 110% of sales
}

# models/optimization.py - MODIFY volume optimization
def optimize_cargo_volume(month, destination, buyer, forecasts):
    """Optimize volume subject to BOTH purchase AND sales constraints"""
    
    # Purchase constraints
    purchase_min = VOLUME_FLEXIBILITY_CONFIG['min_volume_mmbtu']  # 3.42M
    purchase_max = VOLUME_FLEXIBILITY_CONFIG['max_volume_mmbtu']  # 4.18M
    
    # Sales constraints (after boil-off)
    voyage_days = VOYAGE_DAYS[f'USGC_to_{destination}']
    boiloff_rate = OPERATIONAL['boil_off_rate_per_day']
    boiloff_pct = boiloff_rate * voyage_days
    
    sales_min = SALES_CONTRACT['min_volume_mmbtu']  # 3.33M
    sales_max = SALES_CONTRACT['max_volume_mmbtu']  # 4.07M
    
    # Delivered volume = Purchase × (1 - boil-off%)
    # Therefore: Purchase ≤ Sales_max / (1 - boil-off%)
    
    effective_purchase_max = sales_max / (1 - boiloff_pct)
    
    # Binding constraint
    actual_max = min(purchase_max, effective_purchase_max)
    
    # Optimize within [purchase_min, actual_max]
    ...
```

### Impact on Results

**With Sales Constraint (Singapore 48-day voyage):**
```
Boil-off: 2.4%
Sales max: 4.07M MMBtu
Purchase max: 4.07M / 0.976 = 4.17M MMBtu

Current: 4.18M MMBtu ❌
Corrected: 4.17M MMBtu ✓

Impact: -10k MMBtu = -0.24% revenue = ~$24k loss per cargo
Total impact: ~$144k across 6 cargoes
```

**NOT material** (0.15% of total P&L) but **technically correct**.

---

## Summary of Findings

| Gap | Status | Material Impact | Fix Needed |
|-----|--------|-----------------|------------|
| **GAP 1: Cancellation** | ✅ IMPLEMENTED | None | Verify tolling fee ($1.50 vs $2.50) |
| **GAP 2: Sales Volume** | ❌ NOT IMPLEMENTED | ~$144k | Add sales contract constraint |

---

## Immediate Actions

### 1. Verify Tolling Fee (High Priority)
- Check case materials for exact tolling fee
- If $1.50: Update line 79 in `config/constants.py`
- Re-run to confirm no months become cancellation-optimal

### 2. Implement Sales Volume Constraint (Medium Priority)
- Add `SALES_CONTRACT` config
- Modify `optimize_cargo_volume()` to respect both constraints
- Re-run optimization to get corrected P&L

### 3. Update Documentation (Low Priority)
- Document that cancellation IS evaluated
- Explain sales volume constraint logic
- Add to presentation: "We evaluated cancellation for all cargoes"

---

## Questions for User

1. **Tolling Fee:** Can you confirm from case materials - is it $1.50 or $2.50/MMBtu?

2. **Sales Volume:** Can you confirm sales contract base:
   - Is it 3.7M MMBtu (different from purchase)?
   - Or is it also 3.8M MMBtu (same as purchase)?

3. **Excess Volume:** If delivered > sales max, what happens?
   - Spot market sale?
   - Vented?
   - Penalty?
   - Contract violation?

---

**Excellent catches! These are the kind of details that separate good models from great ones.**


