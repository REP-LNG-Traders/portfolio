# CRITICAL MODELING ISSUE: Demand Percentage Treatment

**Date:** October 17, 2025  
**Status:** 🚨 **FUNDAMENTAL QUESTION REQUIRES DECISION**  
**Priority:** HIGH - Affects all P&L calculations

---

## 🚨 User's Critical Observation

### **The Problem:**

**Current Model Behavior (January):**
```
Gross margin: $24.24M
Probability of sale: 13% (10% demand × 1.3 AA multiplier)
Expected P&L: $24.24M × 13% = $3.15M

PROBLEM: If there's only 13% chance of selling, why lift the cargo at all?
87% chance of being stuck with unsold LNG = disaster!
```

**User is absolutely right** - You wouldn't lift a cargo with 13% sale probability in reality!

---

## Two Competing Interpretations

### **INTERPRETATION 1: Pre-Contracted Sales** (Most Likely!) ✅

**Evidence from case materials:**
1. Sales contracts show **specific buyers** (Iron_Man, Thor, etc.)
2. **DES (Delivered Ex-Ship)** contract structure with pricing formulas
3. **M-1 nomination** requirement suggests advance commitments
4. **Credit ratings matter** → ongoing buyer relationships
5. **Thor requires 3-6 month advance notice** → contracts, not spot

**What "demand %" means under this interpretation:**
```
Demand % = Market tightness / Buyer appetite

10% demand (January):
  → Only 1-2 buyers seeking additional volume
  → Competitive market (many sellers, few buyers)
  → You must DISCOUNT price to win the deal
  
100% demand (Peak season):
  → All buyers seeking volume
  → Tight market (few sellers, many buyers)
  → You can charge PREMIUM pricing
```

**Modeling approach:**
```python
# Demand affects PRICE, not probability
if demand_pct < 0.20:  # Tight market (low demand)
    price_adjustment = -$1.50/MMBtu  # Competitive discount
elif demand_pct > 0.80:  # Loose market (high demand)
    price_adjustment = +$1.00/MMBtu  # Scarcity premium
else:
    price_adjustment = $0  # Base pricing

margin = gross_margin + (sales_volume × price_adjustment)

# Sale is CERTAIN (contracted)
# Only apply credit risk (default probability)
expected_pnl = margin - expected_credit_loss
```

**January result under this approach:**
```
Gross margin: $24.24M
Price discount (10% demand): -$1.50/MMBtu × 4.07M = -$6.1M
Credit risk: -$12k
Net P&L: $18.1M ✓ (much more realistic!)
```

---

### **INTERPRETATION 2: Spot Market Sales** (Current Model)

**What "demand %" means under this interpretation:**
```
Demand % = Probability of finding ANY buyer in spot market

10% demand = 90% chance you find NO buyer
```

**Modeling approach (CURRENT):**
```python
prob_sale = demand_pct × buyer_quality_multiplier
expected_pnl = gross_pnl × prob_sale + storage_cost × (1 - prob_sale)
```

**Why this is problematic:**
- ❌ Wouldn't lift cargo with 13% sale probability
- ❌ 87% chance of disaster (unsold cargo on ship)
- ❌ Storage cost doesn't capture true downside
- ❌ Doesn't match case structure (DES contracts)

---

## 📋 Evidence Supporting Interpretation 1

### From Case Materials (User's Input):

**Sales Contract Structure:**
```
Counterparty: Iron_Man (AA rated)
Direction: SELL
Quantity: 3,700,000 MMBtu ±10%
Price: (Brent × 0.13) + $4.00 premium + Terminal Tariff
Payment Terms: Immediate (T+0)
Nomination: M-1
```

**This is a BILATERAL CONTRACT, not spot market:**
- Specific counterparty (Iron_Man)
- Pre-agreed pricing formula
- Nomination requirement (M-1)
- Credit risk matters (ongoing relationship)

### Buyer Demand Table:

```
"Estimated demand (% Open demand)"
Singapore: Jan 10%, Feb 25%, Mar 50%...
```

**"Open demand" suggests:**
- % of buyers seeking ADDITIONAL volume
- Market tightness indicator
- NOT probability of finding any buyer

---

## 🎯 Recommended Fix

### **If Interpretation 1 is Correct** (Which I Believe It Is):

**Current Approach:**
```python
# WRONG: Treating demand as sale probability
expected_pnl = gross_margin × demand_probability
```

**Should Be:**
```python
# CORRECT: Demand affects negotiating power and pricing
def apply_demand_pricing_adjustment(month, destination, demand_pct):
    """
    Low demand = Competitive market = Price discount needed
    High demand = Tight market = Can charge premium
    """
    
    if demand_pct <= 0.15:  # Very low demand (Jan-Feb)
        price_adjustment = -1.50  # $/MMBtu discount to compete
    elif demand_pct <= 0.40:  # Low-moderate demand (Mar-Apr)
        price_adjustment = -0.75  # Moderate discount
    elif demand_pct <= 0.70:  # Moderate-high demand (May-Jun)
        price_adjustment = 0.00  # Base pricing
    else:  # High demand (peak season)
        price_adjustment = +0.50  # Scarcity premium
    
    return price_adjustment

# Calculate margin with demand-based pricing
base_margin = calculate_base_margin(...)
demand_adj = apply_demand_pricing_adjustment(month, destination, demand_pct)
pricing_impact = sales_volume × demand_adj

adjusted_margin = base_margin + pricing_impact

# Sale is CERTAIN (contracted buyer)
# Only apply credit risk
expected_pnl = adjusted_margin - expected_credit_loss
```

**Impact on Results:**

| Month | Demand % | Price Adj | Current P&L | Corrected P&L | Change |
|-------|----------|-----------|-------------|---------------|--------|
| Jan | 10% | -$1.50 | $3.20M | ~$18.1M | +$14.9M |
| Feb | 25% | -$1.00 | $8.58M | ~$16.5M | +$7.9M |
| Mar | 50% | -$0.50 | $18.35M | ~$20.3M | +$2.0M |
| Apr | 50% | -$0.50 | $18.73M | ~$20.7M | +$2.0M |
| May | 65% | $0.00 | $24.28M | ~$24.3M | +$0.0M |
| Jun | 65% | $0.00 | $23.70M | ~$23.7M | +$0.0M |

**Total impact:** Could be +$26.8M if demand is price adjustment!

---

## 🔍 How to Determine Correct Interpretation

### **Questions for Case Materials:**

1. **Are sales pre-contracted or spot?**
   - If "Counterparty: Iron_Man" means you have a contract → Interpretation 1
   - If you're selling in open market → Interpretation 2

2. **What does "open demand" mean?**
   - "% of market seeking additional volume" → Price adjustment
   - "Probability market exists" → Sale probability

3. **Can you refuse to lift if you can't find buyer?**
   - If YES → Spot market (Interpretation 2)
   - If NO → Contracted (Interpretation 1)

4. **Does M-1 nomination lock in the sale?**
   - If YES → Contracted (Interpretation 1)
   - If NO → Contingent on finding buyer (Interpretation 2)

---

## 💡 My Assessment

### **I Believe Interpretation 1 is Correct**

**Reasoning:**

1. **Contract Structure:**
   - Case shows specific buyers with pricing formulas
   - DES contracts with M-1 nomination
   - This is NOT spot market language

2. **Thor's 3-6 Month Requirement:**
   - Suggests advance contracting
   - Spot market wouldn't have lead time requirements

3. **Credit Risk Importance:**
   - Only matters for ongoing relationships
   - Spot buyers would pay upfront

4. **Industry Practice:**
   - LNG typically sold via long-term contracts
   - Spot market is minority of trade
   - "Demand %" in industry = market tightness indicator

5. **Economic Rationality:**
   - Wouldn't lift cargo with 13% sale probability
   - But WOULD lift with contracted buyer if price discount is acceptable

---

## 🎯 Recommended Action

### **CRITICAL DECISION NEEDED:**

**Option A: Keep Current Model (Conservative)**
- Pros: Very conservative (understates P&L)
- Cons: Economically irrational (wouldn't lift 13% probability cargo)
- Use if: Case explicitly says "spot market" or "uncontracted sales"

**Option B: Implement Price Adjustment (Realistic)**
- Pros: Economically rational, matches industry practice
- Cons: Need to calibrate price adjustments
- Use if: Sales are contracted (which evidence suggests)

### **Immediate Steps:**

1. **Verify from case materials:**
   - Are sales pre-contracted with specific buyers?
   - Or are you selling in spot market each month?

2. **If pre-contracted (likely):**
   - Implement demand-based price adjustment
   - Remove probability multiplication
   - Recalculate all P&L

3. **If spot market (unlikely):**
   - Keep current model
   - Add logic to NOT lift months with <50% probability
   - Document rationale

---

## 📊 Impact Analysis

### **If We Implement Price Adjustment:**

**Best Case (Conservative Adjustments):**
```
Jan: $3.20M → $18.1M (+$14.9M)
Feb: $8.58M → $16.5M (+$7.9M)
...
Total: $96.83M → ~$123M (+$26M)
```

**This would be MATERIAL** (+27% to base contract P&L)

### **Risk:**

If we're wrong and it IS probability:
- Current model is correct
- Making it price adjustment would overstate P&L
- But current model seems economically irrational...

---

## 🚨 BOTTOM LINE

**This is THE most important modeling question remaining.**

**User is right to question this!**

Current approach (multiply by probability) implies:
- 13% chance of selling January cargo
- 87% chance of disaster
- Economically irrational to lift

**I believe the model should use demand % for price adjustment, not sale probability.**

**BUT we need to confirm from case materials before implementing.**

---

## ❓ Question for User

**Can you check the case materials:**

1. **Are your sales contracted with specific buyers** (Iron_Man, Thor, etc.)?
   - If YES → Use price adjustment (Interpretation 1)
   - If NO → Keep probability approach (Interpretation 2)

2. **What does "% open demand" mean in the case?**
   - "% of buyers seeking volume" → Price adjustment
   - "Probability of sale" → Current approach

3. **Is M-1 nomination a firm commitment?**
   - If YES → Sale is certain, demand affects price
   - If NO → Sale is uncertain, demand is probability

**This could change P&L by ~$26M!**


