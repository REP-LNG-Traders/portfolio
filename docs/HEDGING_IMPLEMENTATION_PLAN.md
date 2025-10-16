# Hedging Implementation Plan: Basis Risk & FX Risk

## Overview
Implement hedging strategies to manage:
1. **Basis Risk**: Price mismatch between purchase/sale formulas and market prices
2. **FX Risk**: Currency exposure from USD-denominated transactions

---

## 1. BASIS RISK

### 1.1 What is Basis Risk in This Context?

**Purchase Side (Fixed Formula)**:
```
Purchase Cost = (Henry Hub WMA + $2.50) × Volume
```
- Exposed to: Henry Hub price movements
- Basis: Difference between HH WMA and HH futures/spot

**Sale Side (Destination-Specific)**:
```
Singapore: (Brent × 0.13 + Premium) + Terminal Tariff
Japan:     JKM(M+1) + Premium + Berthing
China:     JKM(M+1) + Premium + Berthing
```

**Basis Risks**:
1. **HH Basis**: HH WMA vs HH futures (your purchase benchmark vs hedge instrument)
2. **Brent/JKM Spread**: For Singapore, you're long Brent but market might move differently than JKM
3. **JKM Basis**: JKM spot vs JKM futures (for Japan/China sales)
4. **Cross-Commodity**: HH purchase vs JKM/Brent sale (crack spread risk)

### 1.2 Clarification Questions - BASIS RISK

#### Q1: Which Basis Risks Should We Hedge?

**Option A - Simple (Purchase Only)**:
- Hedge: Henry Hub purchase exposure only
- Instrument: NYMEX Henry Hub futures
- Rationale: Lock in gas procurement cost, accept commodity spread risk

**Option B - Sales Only**:
- Hedge: JKM (for Japan/China) and Brent (for Singapore)
- Instruments: Platts JKM swaps, ICE Brent futures
- Rationale: Lock in sale prices, accept procurement cost risk

**Option C - Full Hedge (Purchase + Sales)**:
- Hedge: Both sides (HH purchase AND sale prices)
- Instruments: HH futures + JKM swaps + Brent futures
- Rationale: Lock in spread/margin, minimize commodity exposure

**Option D - Selective (Crack Spread)**:
- Hedge: The spread itself (e.g., JKM - HH spread)
- Instruments: Calendar spread options or swaps
- Rationale: Natural long spread position, hedge the key value driver

**Which approach do you prefer?**

#### Q2: Hedge Timing - When Do We Hedge?

**Option A - At Decision Time (Month M-1)**:
- Hedge when you decide destination/buyer
- Example: December decision for January cargo → hedge in December

**Option B - At Contract Execution (Month M)**:
- Hedge when cargo is loading
- Aligns with physical delivery

**Option C - Rolling/Dynamic**:
- Start hedging months in advance
- Adjust hedge ratio as cargo date approaches

**Which timing makes sense for competition?**

#### Q3: Hedge Instruments - What Can We Use?

**Available Instruments**:
1. **Henry Hub**: NYMEX NG futures (highly liquid)
2. **JKM**: Platts JKM swaps (liquid for front months)
3. **Brent**: ICE Brent futures (most liquid oil benchmark)
4. **Spread Products**: JKM-HH calendar spreads (less liquid)

**Assumptions Needed**:
- Are these instruments available in your competition scenario?
- Transaction costs (bid-ask spread, brokerage)?
- Margin requirements?

#### Q4: Hedge Ratio - How Much to Hedge?

**Option A - Full Hedge (100%)**:
- Hedge 100% of cargo volume
- Pros: Maximum risk reduction
- Cons: Forgoes upside, locks in current prices

**Option B - Partial Hedge (50-80%)**:
- Hedge partial volume, keep some exposure
- Pros: Balanced risk/reward
- Cons: Still exposed to adverse moves

**Option C - Dynamic (Delta-Hedging)**:
- Adjust hedge ratio based on market conditions
- Complex but theoretically optimal

**What hedge ratio do you want to use?**

#### Q5: Hedge Effectiveness - How to Measure?

**Metrics**:
1. **Basis Risk**: std(hedged P&L) vs std(unhedged P&L)
2. **Hedge Ratio**: correlation(spot, futures)
3. **Cost**: Transaction costs + margin + opportunity cost
4. **P&L Impact**: Expected P&L with vs without hedge

**Should we calculate and compare hedged vs unhedged strategies?**

---

## 2. FX RISK

### 2.1 What is FX Risk in This Context?

**Current Situation**:
- All contracts appear to be **USD-denominated**
- Singapore sales: USD revenue
- Purchase: USD cost
- Freight: USD cost

**Potential FX Exposures**:
1. **Singapore Terminal Tariff**: If paid in SGD (need clarification)
2. **Buyer Preferences**: Do Singapore buyers want SGD pricing?
3. **Company Base Currency**: Is your company USD or SGD based?
4. **Financing**: Are there SGD loans or costs?

### 2.2 Clarification Questions - FX RISK

#### Q6: What FX Exposure Exists?

**Scenario A - No Real FX Risk**:
- All contracts are USD
- No need for FX hedging
- FX data provided is just for information

**Scenario B - Singapore Revenue Exposure**:
- Singapore sales received in SGD, converted to USD
- Need to hedge USD/SGD for Singapore cargoes
- Revenue = SGD amount ÷ FX rate

**Scenario C - Company Base Currency**:
- Company reports in SGD
- All USD revenues/costs need FX translation
- Hedge ALL cash flows

**Scenario D - Selective Exposure**:
- Only terminal tariff or specific costs in SGD
- Limited hedge needed

**Which scenario applies to your competition?**

#### Q7: FX Hedge Instruments

**Available**:
1. **USD/SGD Forward**: Lock in exchange rate for future date
2. **USD/SGD Options**: Downside protection, keep upside
3. **Natural Hedge**: Match USD revenues with USD costs (no hedge needed)

**Assumptions**:
- Forward points (cost of FX forward)?
- Option premiums (if using options)?

#### Q8: FX Hedge Strategy

**Option A - Forward Hedge**:
- Lock in FX rate at decision time
- Simple, eliminates FX risk
- Cost: Forward points (small for SGD)

**Option B - Option Hedge (Collar)**:
- Buy put (floor), sell call (cap)
- Net zero or low cost
- Keep some upside, limit downside

**Option C - No Hedge**:
- Accept FX risk as diversification
- SGD historically stable vs USD
- Lower transaction costs

**Which approach?**

---

## 3. IMPLEMENTATION ARCHITECTURE

### 3.1 Proposed Code Structure

```python
# New file: src/hedging.py

class HedgingStrategy:
    """Base class for hedging strategies"""
    
    def calculate_hedge_position(self, cargo_details: Dict) -> Dict:
        """Determine hedge positions for a cargo"""
        pass
    
    def calculate_hedging_cost(self, positions: Dict) -> float:
        """Calculate transaction costs + margin + p/l"""
        pass
    
    def calculate_hedged_pnl(self, unhedged_pnl: Dict, market_prices: Dict) -> Dict:
        """Calculate P&L including hedge effects"""
        pass

class BasisRiskHedge(HedgingStrategy):
    """
    Hedge commodity price basis risk
    - Henry Hub purchase exposure
    - JKM/Brent sale exposure
    - Spread/crack hedges
    """
    
    def __init__(self, hedge_instruments: Dict, hedge_ratio: float):
        self.instruments = hedge_instruments
        self.hedge_ratio = hedge_ratio
    
    def calculate_hh_hedge(self, cargo_volume: float, hh_price: float) -> Dict:
        """Hedge Henry Hub purchase with NYMEX NG futures"""
        pass
    
    def calculate_jkm_hedge(self, delivered_volume: float, jkm_price: float) -> Dict:
        """Hedge JKM sale with Platts swaps"""
        pass
    
    def calculate_brent_hedge(self, delivered_volume: float, brent_price: float) -> Dict:
        """Hedge Brent-linked sale with ICE futures"""
        pass

class FXRiskHedge(HedgingStrategy):
    """
    Hedge foreign exchange risk
    - USD/SGD exposure
    - Forward contracts
    - Options (if applicable)
    """
    
    def __init__(self, base_currency: str, hedge_ratio: float):
        self.base_currency = base_currency
        self.hedge_ratio = hedge_ratio
    
    def calculate_fx_hedge(self, cash_flow: Dict, fx_forward_rate: float) -> Dict:
        """Hedge FX exposure with forwards"""
        pass

class CombinedHedgingStrategy:
    """
    Combines basis and FX hedging
    Integrated P&L calculation
    """
    
    def __init__(self, basis_hedge: BasisRiskHedge, fx_hedge: FXRiskHedge):
        self.basis_hedge = basis_hedge
        self.fx_hedge = fx_hedge
    
    def optimize_hedge_portfolio(self, cargo_decisions: List[Dict]) -> Dict:
        """Optimize combined hedge across all cargoes"""
        pass
```

### 3.2 Integration with Existing Code

**Modified Files**:
1. **`config.py`**: Add hedging configuration
   ```python
   HEDGING_CONFIG = {
       'enabled': True,
       'basis_hedge': {
           'henry_hub': True,
           'jkm': True,
           'brent': True,
           'hedge_ratio': 1.0,  # 100%
           'instruments': {...}
       },
       'fx_hedge': {
           'enabled': False,  # TBD based on your answer
           'base_currency': 'USD',
           'hedge_ratio': 1.0
       },
       'transaction_costs': {
           'futures_bps': 0.5,  # 0.5 bps
           'swaps_bps': 1.0,
           'fx_forward_bps': 0.3
       }
   }
   ```

2. **`src/cargo_optimization.py`**: Add hedge calculations to P&L
   ```python
   def calculate_cargo_pnl_with_hedge(self, ...):
       # Existing unhedged P&L
       unhedged_pnl = self.calculate_cargo_pnl(...)
       
       # Calculate hedge positions
       hedge_positions = self.hedging_strategy.calculate_hedge_position(...)
       
       # Calculate hedge P&L
       hedge_pnl = self.hedging_strategy.calculate_hedging_cost(...)
       
       # Combine
       hedged_pnl = unhedged_pnl + hedge_pnl
       
       return {
           'unhedged_pnl': unhedged_pnl,
           'hedge_pnl': hedge_pnl,
           'hedged_pnl': hedged_pnl,
           'hedge_positions': hedge_positions
       }
   ```

3. **`main_optimization.py`**: Add hedged strategy comparison
   ```python
   # Compare strategies with/without hedging
   strategies_unhedged = optimizer.generate_all_strategies(forecasts)
   strategies_hedged = optimizer.generate_all_strategies_with_hedge(forecasts, hedging_config)
   
   # Show comparison
   results = {
       'Optimal (Unhedged)': strategies_unhedged['Optimal'],
       'Optimal (Hedged)': strategies_hedged['Optimal'],
       ...
   }
   ```

### 3.3 Outputs to Add

1. **Hedge Position Report**:
   - Month-by-month hedge positions (futures, swaps, forwards)
   - Notional exposure
   - Mark-to-market P&L

2. **Risk Reduction Metrics**:
   - Standard deviation: hedged vs unhedged
   - VaR improvement
   - Hedge effectiveness ratio

3. **Cost-Benefit Analysis**:
   - Transaction costs
   - Margin requirements
   - Expected P&L improvement

---

## 4. MY CLARIFICATION QUESTIONS SUMMARY

### BASIS RISK:
1. **Q1**: Which exposures to hedge? (HH only / Sales only / Both / Spread)
2. **Q2**: When to hedge? (Decision time / Loading month / Rolling)
3. **Q3**: Are futures/swaps available in competition scenario? Transaction costs?
4. **Q4**: Hedge ratio? (100% / Partial / Dynamic)
5. **Q5**: Should we compare hedged vs unhedged strategies?

### FX RISK:
6. **Q6**: What is the actual FX exposure? (None / Singapore revenue / Company base currency / Selective)
7. **Q7**: Are FX forwards available? Cost assumptions?
8. **Q8**: FX hedge strategy? (Forward / Options / No hedge)

### IMPLEMENTATION:
9. **Q9**: Should hedging be:
   - **Option A**: Separate analysis (hedged vs unhedged comparison)
   - **Option B**: Integrated into main optimization (hedged is default)
   - **Option C**: Optional toggle (user can enable/disable)

10. **Q10**: Priority for competition deadline?
    - **Must-have**: Critical for final submission
    - **Nice-to-have**: If time permits after core model
    - **Showcase feature**: To demonstrate sophistication to judges

---

## 5. RECOMMENDED APPROACH (For Discussion)

**My Suggestion for Competition Context**:

### Phase 1 - Basis Risk (PRIORITY)
- **Hedge**: HH purchase + JKM sales only (not Brent - Singapore is smaller)
- **Instruments**: NYMEX NG futures, Platts JKM swaps
- **Ratio**: 100% for showcase, then compare 0%/50%/100%
- **Timing**: At decision time (Month M-1)
- **Output**: "Hedged" strategy variant showing risk reduction

### Phase 2 - FX Risk (IF APPLICABLE)
- **First**: Confirm if FX exposure actually exists
- **If yes**: Simple forward hedge for Singapore sales
- **If no**: Skip this part, focus on basis risk

### Implementation Timeline
1. **Config setup**: 15 min (add HEDGING_CONFIG to config.py)
2. **Core hedging logic**: 1 hour (src/hedging.py)
3. **Integration**: 30 min (modify cargo_optimization.py)
4. **Testing**: 30 min
5. **Output/visualization**: 30 min
Total: ~3 hours for basic implementation

**Does this approach work for you?**

---

## Next Steps

Please answer the clarification questions above, then I'll:
1. Implement the hedging module
2. Integrate with existing optimization
3. Generate comparison outputs
4. Update documentation

**What are your preferences on the questions above?**

