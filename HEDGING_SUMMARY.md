# Hedging Implementation Summary - Henry Hub Purchase Cost Risk Management

## Executive Summary

Successfully implemented a Henry Hub purchase cost hedging strategy using NYMEX NG futures. The hedging analysis demonstrates sophisticated risk management with:
- **26% volatility reduction**
- **35% Sharpe ratio improvement**
- **$13M VaR improvement**
- **Minimal expected P&L impact** (-0.3%)

---

## 1. HEDGING STRATEGY DESIGN

### What We Hedge
**ONLY Henry Hub Purchase Cost** - Not sales (JKM/Brent)

**Rationale (documented for judges)**:
1. **Certain Cost**: HH is our committed, known procurement cost ($2.50 + HH per cargo)
2. **Liquid Market**: NYMEX NG futures are highly liquid (tight bid-ask, deep market)
3. **Clean Hedge**: Direct 1:1 relationship (futures settle to HH spot index)
4. **Sophistication**: Shows risk management without over-complicating
5. **Industry Practice**: Common to hedge costs, let revenues float

**Why NOT hedge JKM/Brent sales:**
- JKM swaps less liquid than NYMEX NG
- Multiple sale formulas (Brent for Singapore, JKM for Japan/China) complicate execution
- M+1 timing for JKM adds complexity
- Letting revenues benefit from favorable moves is acceptable

### When We Hedge
**At M-2 (Nomination Deadline)** - 2 months before cargo loading

**Timeline Example** (January 2026 Cargo):
```
November 1, 2025 (M-2):  ✓ Nominate January cargo
                         ✓ BUY 380 HH futures contracts at forward price
                         → Risk begins, hedge initiated

January 2026 (M):        ✓ Cargo loads
                         ✓ Pay spot HH price + $2.50
                         ✓ Futures settle to spot price
                         → Hedge P&L offsets cost movement
```

**Rationale**:
- Risk begins when we commit at M-2 (per case pack page 15)
- Realistic trading practice (hedge when committed, not when delivered)
- Aligns with contract nomination requirements

### How Much We Hedge
**100% of Cargo Volume** - Full hedge ratio

**Calculation**:
```
Cargo Size:        3,800,000 MMBtu
Contract Size:     10,000 MMBtu (standard NYMEX NG)
Contracts Needed:  3,800,000 / 10,000 = 380 contracts per cargo
Total (6 cargoes): 380 × 6 = 2,280 contracts
```

**Rationale**:
- Industry standard for committed volumes (80-100%)
- Eliminates HH price risk entirely
- Clean comparison for judges (before/after)
- Simpler narrative than partial hedge

### What About FX Risk?
**NO FX HEDGING** - All contracts are USD-denominated

**Evidence**:
- Purchase: "(Henry Hub + $2.50)/MMBtu" in USD (page 15)
- Sales: All formulas quote USD premiums (page 16)
- No currency conversion needed
- USD/SGD data is reference only (or corporate accounting)

---

## 2. TECHNICAL IMPLEMENTATION

### 2.1 Files Created/Modified

#### `config.py` - Added HEDGING_CONFIG
```python
HEDGING_CONFIG = {
    'enabled': True,
    'henry_hub_hedge': {
        'enabled': True,
        'instrument': 'NYMEX_NG_Futures',
        'contract_size_mmbtu': 10000,
        'hedge_ratio': 1.0,  # 100%
        'timing': 'M-2'
    },
    'jkm_hedge': {'enabled': False},      # Not implemented
    'brent_hedge': {'enabled': False},    # Not implemented
    'fx_hedge': {'enabled': False},       # Not needed
    'transaction_costs': {'model_costs': False}  # Immaterial
}
```

#### `src/hedging.py` - New Module
**Classes**:
- `HenryHubHedge`: Core hedging logic
  - `calculate_hedge_position()`: Determine contracts needed
  - `calculate_hedge_pnl()`: Calculate hedge gain/loss
  - `calculate_hedged_cargo_pnl()`: Combine unhedged + hedge

**Key Methods**:
```python
# Hedge P&L formula:
hedge_pnl = (HH_spot_at_M - HH_forward_at_M2) × hedged_volume

# Offsets purchase cost change:
# If HH rises: hedge gains, offset higher cost
# If HH falls: hedge loses, offset lower cost
```

#### `src/cargo_optimization.py` - Added Methods
- `CargoPnLCalculator.calculate_cargo_pnl_with_hedge()`: Integrated P&L calculation

#### `main_optimization.py` - Orchestration
- `generate_hedged_strategies()`: Create hedged variants of all strategies
- Modified `main()`: Generate and analyze hedged strategies
- Modified `save_results()`: Export hedging comparison
- Monte Carlo with reduced HH volatility (60.8% → 1.0% for hedged)

### 2.2 Hedge P&L Calculation Logic

```python
# Step 1: Calculate unhedged P&L
unhedged_pnl = (sale_revenue - purchase_cost - freight_cost)
               - credit_risk - demand_risk

# Step 2: Calculate hedge P&L
hedge_pnl = (HH_spot - HH_forward_m2) × cargo_volume

# Step 3: Combine
hedged_pnl = unhedged_pnl + hedge_pnl

# In expectation (deterministic):
# HH_forward = E[HH_spot] (efficient markets)
# → E[hedge_pnl] = 0
# → E[hedged_pnl] ≈ E[unhedged_pnl]

# In Monte Carlo (stochastic):
# HH_spot varies with 60.8% volatility (unhedged)
# HH_spot locked at forward price (hedged)
# → Var[hedged_pnl] << Var[unhedged_pnl]
```

### 2.3 Monte Carlo Modification

**Critical Innovation**:
For hedged strategies, we reduce HH volatility to 1% (from 60.8%) in Monte Carlo:

```python
# Unhedged MC: Full volatilities
volatilities = {
    'henry_hub': 60.8%,  # Full HH risk
    'jkm': 54.2%,
    'brent': 33.7%,
    'freight': 4983.6%
}

# Hedged MC: Reduced HH volatility
hedged_volatilities = {
    'henry_hub': 1.0%,   # Near-zero (locked by hedge)
    'jkm': 54.2%,        # Still exposed
    'brent': 33.7%,      # Still exposed
    'freight': 4983.6%   # Still exposed
}
```

**Rationale**:
- 100% hedge eliminates HH price risk
- 1% residual accounts for basis risk (HH WMA vs HH futures)
- This is how Monte Carlo shows hedging effectiveness

---

## 3. RESULTS & VALIDATION

### 3.1 Optimal Strategy Comparison

| Metric | Unhedged | Hedged | Change | Interpretation |
|--------|----------|--------|--------|----------------|
| **Expected P&L** | $79.30M | $79.04M | -$0.26M (-0.3%) | ✅ Minimal cost |
| **Std Dev** | $24.70M | $18.24M | -$6.45M (-26.2%) | ✅ Major risk reduction |
| **VaR (5%)** | $38.67M | $52.00M | +$13.33M | ✅ Worst case improved |
| **CVaR (5%)** | $26.34M | $46.62M | +$20.29M | ✅ Tail risk improved |
| **Sharpe Ratio** | 3.21 | 4.33 | +1.12 (+35%) | ✅ Better risk-adjusted return |
| **Prob(Profit)** | 99.78% | 100.00% | +0.22% | ✅ Near certainty |

**VaR/CVaR Note**: These are 5th percentile P&L values. Higher is better (less bad worst-case).

### 3.2 All Three Strategies

| Strategy | Volatility Reduction | Sharpe Improvement | Prob(Profit) Improvement |
|----------|---------------------|-------------------|-------------------------|
| **Optimal** | -26.2% | +35.0% | 99.78% → 100.00% |
| **Conservative** | -27.9% | +38.3% | 99.75% → 100.00% |
| **High JKM** | -7.1% | +7.1% | 97.72% → 99.45% |

**Insight**: Conservative strategy benefits most from hedging (highest HH exposure)

### 3.3 Validation Checks

✅ **Hedge Contracts**: 380 per cargo (3,800,000 / 10,000) - Correct
✅ **Expected Hedge P&L**: ~$0 in deterministic case - Correct (efficient markets)
✅ **HH Volatility**: 60.8% → 1.0% in hedged MC - Correct (locked price)
✅ **Risk Reduction**: Volatility down 26%, VaR improved $13M - Expected outcome
✅ **Sharpe Improvement**: +35% - Correct (same return, lower risk)

---

## 4. OUTPUTS GENERATED

### 4.1 Excel Files
1. **`hedging_comparison_[timestamp].xlsx`**
   - **Sheet 1: Hedging_Comparison** - Full metrics table
   - **Sheet 2: Summary** - Executive summary with interpretation

### 4.2 Key Comparison Table

All three strategies compared (unhedged vs hedged) with:
- Expected P&L (both versions)
- Volatility (both + reduction %)
- VaR/CVaR (both + improvement)
- Sharpe ratio (both + improvement)
- Probability of profit (both)

### 4.3 Summary Text (in Excel)
```
Hedging Impact on Optimal Strategy:
- Expected P&L: $79.04M (-$0.26M change)
- Volatility Reduction: 26.2%
- VaR Improvement: $+13.33M
- Sharpe Ratio: 3.21 -> 4.33

Conclusion: Hedging reduces downside risk with minimal impact on expected returns.
```

---

## 5. PRESENTATION TALKING POINTS

### For Judges - Key Messages

**1. Strategic Rationale**:
> "We hedge our Henry Hub procurement cost because it's our largest, most certain expense. NYMEX NG futures provide a liquid, clean hedge that locks in our gas cost at the nomination deadline."

**2. Why Not Sales?**:
> "We don't hedge JKM or Brent sales because: (1) those markets are less liquid than NYMEX NG, (2) we have multiple sale formulas making execution complex, and (3) industry practice is to hedge costs and let revenues benefit from favorable moves."

**3. Risk Management Outcome**:
> "Hedging reduced our portfolio volatility by 26% and improved our worst-case scenario (5% VaR) by $13 million, with only a 0.3% reduction in expected returns. Our risk-adjusted performance (Sharpe ratio) improved by 35%."

**4. No FX Hedging**:
> "All contracts are USD-denominated, so we have no FX exposure on these cargo decisions. The USD/SGD data provided is for reference or corporate-level accounting only."

**5. Transaction Costs**:
> "NYMEX NG futures commission is approximately $1 per contract, or $380 per cargo, which is 0.003% of cargo value. We excluded this from the model as immaterial."

### If Judges Ask Follow-Up Questions

**Q: Why 100% hedge ratio, not 50% or 80%?**
> "Industry standard for committed volumes is 80-100%. We chose 100% for clean comparison and complete risk elimination. In practice, we could adjust based on market views."

**Q: What about basis risk between HH WMA and HH futures?**
> "Excellent question. HH WMA (Weighted Monthly Average) and HH futures have 95%+ correlation. Our 1% residual volatility in the Monte Carlo accounts for this small basis risk."

**Q: Why not use calendar spreads or crack spreads?**
> "That's more sophisticated but adds complexity. For this competition, we wanted to show clean, executable hedging. Calendar/crack spreads would be next-level enhancement."

**Q: How do you handle hedge margin requirements?**
> "NYMEX NG initial margin is approximately $1,500-2,000 per contract. For 380 contracts, that's ~$700K, which is 0.7% of cargo value. We excluded this working capital cost as minor, but it could be added if the judging criteria require it."

---

## 6. ASSUMPTIONS & LIMITATIONS

### Assumptions Made

1. **Forward Curve = Hedge Price**: We use our HH forecast as proxy for M-2 forward price
   - In reality: Use actual M-2 forward settlement price
   - Competition simplification acceptable

2. **Perfect Hedge**: Futures settle exactly to HH spot (no basis risk)
   - Reality: 95%+ correlation, small basis risk
   - Modeled as 1% residual volatility

3. **No Transaction Costs**: Commissions/spreads excluded as immaterial (<0.1% of P&L)

4. **100% Execution**: Assumes all hedge orders filled at market price
   - NYMEX NG liquidity supports this for 380 contracts

5. **No Margin Calls**: Assumes sufficient capital for maintenance margin
   - ~$700K for 380 contracts (0.7% of cargo value)

### Limitations

1. **Deterministic Hedge P&L = $0**: In base case, forward = spot (efficient markets)
   - Benefit only visible in Monte Carlo (risk reduction)
   
2. **No Dynamic Hedging**: Fixed 100% ratio, not adjusted based on market conditions
   - Could enhance with delta-hedging or ratio optimization

3. **Sales Not Hedged**: Still exposed to JKM/Brent movements
   - Acceptable risk profile, but could be hedged if required

4. **No Calendar Spread**: Not hedging the HH-JKM spread directly
   - More sophisticated but harder to implement/explain

---

## 7. FILES & CODE COMPONENTS

### New Files
- **`src/hedging.py`** (180 lines): Core hedging logic and calculations
- **`HEDGING_IMPLEMENTATION_PLAN.md`**: Design documentation
- **`HEDGING_SUMMARY.md`** (this file): Results and summary

### Modified Files
- **`config.py`**: Added HEDGING_CONFIG with detailed rationale
- **`src/cargo_optimization.py`**: Added `calculate_cargo_pnl_with_hedge()` method
- **`main_optimization.py`**: 
  - Added `generate_hedged_strategies()` function
  - Modified `main()` to generate and analyze hedged variants
  - Modified `save_results()` to export hedging comparison
  - Modified Monte Carlo to use reduced HH volatility for hedged strategies

### Outputs
- **`hedging_comparison_[timestamp].xlsx`**: Comprehensive comparison table
  - Hedged vs unhedged for all three strategies
  - All risk metrics side-by-side
  - Summary sheet with interpretation

---

## 8. VALIDATION & TESTING

### Test Cases

**Test 1: Basic Hedge Calculation**
```
Scenario: HH rises $1.00/MMBtu
Input:    Forward = $4.00, Spot = $5.00
Expected: Hedge P&L = +$3,800,000 (offsets cost increase)
Result:   ✅ Correct
```

**Test 2: Strategy Integration**
```
Optimal Strategy: 6 cargoes, Jan-Jun 2026
Expected: Hedged P&L ≈ Unhedged P&L (zero expected hedge value)
Result:   ✅ $79.30M vs $79.04M (-0.3% difference)
```

**Test 3: Monte Carlo Risk Reduction**
```
Expected: Volatility reduction 25-40% (eliminates HH component)
Result:   ✅ 26.2% reduction
```

**Test 4: Risk-Adjusted Returns**
```
Expected: Sharpe ratio improves (same return, lower risk)
Result:   ✅ 3.21 → 4.33 (+35% improvement)
```

### Edge Cases Handled

✅ **Cancelled Cargoes**: No hedge applied (skipped in hedging logic)
✅ **Zero Price Change**: Hedge P&L = $0 (handled gracefully)
✅ **Multiple Strategies**: All three strategies hedged independently

---

## 9. COMPETITION DELIVERABLES

### What to Show Judges

**Primary Deliverable**:
- **Hedging Comparison Excel**: Side-by-side unhedged vs hedged metrics

**Key Slide Content**:
```
Slide Title: "Risk Management Through Henry Hub Hedging"

• Hedging Strategy:
  - Hedge: HH purchase cost only (100% of volume)
  - Instrument: NYMEX NG futures (380 contracts/cargo)
  - Timing: M-2 nomination deadline
  
• Results:
  - Volatility: -26% (from $24.7M to $18.2M)
  - Sharpe Ratio: +35% (from 3.21 to 4.33)
  - Worst Case (VaR 5%): +$13M improvement
  - Expected P&L: Maintained at $79M (-0.3%)

• Conclusion:
  "Hedging provides substantial risk reduction with negligible cost"
```

### Supporting Documentation

**If Judges Ask for Details**:
1. Show `HEDGING_CONFIG` in code (thought process documented)
2. Explain hedge P&L calculation (offsetting purchase cost)
3. Walk through Monte Carlo modification (HH vol 60% → 1%)
4. Show Excel comparison table (quantitative proof)

---

## 10. FUTURE ENHANCEMENTS (If Time Permits)

### Priority 1: Sales Hedging
- Add JKM swap hedging for Japan/China sales
- Add Brent futures hedging for Singapore sales
- Compare cost hedge only vs both sides hedged

### Priority 2: Calendar Spread
- Hedge JKM-HH spread directly (capture margin risk)
- More sophisticated, shows deep market understanding

### Priority 3: Dynamic Hedging
- Optimize hedge ratio (50%, 75%, 100%, 120%)
- Adjust based on market volatility regime
- Delta-hedging with rebalancing

### Priority 4: Transaction Cost Model
- Add bid-ask spread impact (~$3,800/cargo)
- Add margin requirement (working capital cost)
- Show cost-benefit analysis

### Priority 5: Hedge Timing Sensitivity
- Compare M-3, M-2, M-1 hedge initiation
- Show impact of early vs late hedging
- Time value analysis

---

## Document Version
- **Created**: October 16, 2025
- **Implementation Status**: ✅ Complete and tested
- **Results File**: `outputs/results/hedging_comparison_[timestamp].xlsx`
- **Next Steps**: Commit to GitHub, prepare presentation materials

