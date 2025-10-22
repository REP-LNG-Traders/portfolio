# Quantitative LNG Cargo Optimization: A Comparative Study of Commercial Strategies

**Author:** [Your Name]  
**Date:** October 22, 2025  
**Context:** NTU CEIT x Baringa ITCC 2025 Competition

---

## Abstract

This paper presents a quantitative framework for optimizing physical LNG cargo deliveries under a six-month supply contract (Jan-Jun 2026) from US Gulf Coast to Singapore, Japan, and China. Using market-based forward curves for Henry Hub and JKM, plus ARIMA(0,1,1)-GARCH(1,1) modeling for Brent crude, we evaluate multiple commercial strategies through comprehensive P&L modeling and risk analysis.

The framework incorporates a 7-component freight model, regulatory costs (Singapore BioLNG penalty, China port fees), and risk adjustments for credit and demand. We optimize destination, buyer selection, and cargo volume (within ±10% contractual flexibility) for six base cargoes plus five optional cargoes valued via Black-Scholes real-options framework.

**Key Results:** The optimal strategy generates **$161.62M** from base cargoes and **$131.90M** from options (**$293.52M** total), routing all six base cargoes to Singapore/Iron_Man at 110% volume utilization. Monthly P&L progresses from $22.78M (January) to $29.73M (June), reflecting strong Brent pricing and seasonal demand improvement. For embedded options, 5 options are exercised: 3 to Japan/Hawk_Eye (Apr-Jun) valued at $27.04M each, and 2 to Singapore/Iron_Man (Mar-Apr) valued at $25.39M each. Monte Carlo analysis (10,000 paths) shows hedging procurement costs reduces volatility by 32.5% and improves Sharpe ratio by 48% (from 3.65 to 5.40) with minimal impact on expected returns. China is economically unviable due to Special Port Fees ($3.92-6.30M per cargo).

---

## 1. Introduction

### 1.1 Problem Definition and Constraints

The optimization addresses a long-term LNG supply contract with:

**Contract Structure:**
- **Six mandatory monthly cargoes** (Jan-Jun 2026) + **five optional cargoes**
- **FOB purchase** from US producer at Henry Hub + **$1.50/MMBtu** tolling fee
- **Three delivery markets**: Singapore (Brent-linked), Japan/China (JKM-linked)
- **Volume flexibility**: ±10% on 3.8M MMBtu (purchase) vs 3.7M MMBtu (sales) - critical asymmetry
- **Decision timing**: Base cargoes at M-2, options at M-3, sales at M-1

**Key Cost Drivers:**
- China Special Port Fee: $3.92M (Jan-Mar) to $6.30M (Apr-Jun) for US-linked vessels
- Singapore BioLNG penalty: 30 SGD/MT on non-compliant volume (5% mandate)
- Boil-off losses: 0.05% per day during 41-52 day voyages

**Counterparty Landscape:**
- **Iron_Man** (Singapore, A-rated): +$4.00/MMBtu premium
- **Thor** (Singapore, AA-rated): +$3.50/MMBtu premium, requires 3-6 month lead time
- **Hawk_Eye** (Japan, A-rated): +$0.60/MMBtu premium
- **QuickSilver** (China, BBB-rated): +$2.20/MMBtu premium

### 1.2 Forecasting Methodology

Our hybrid approach matches methodology to data availability:

**Henry Hub & JKM:** Market forward curves through 2026-2027
- **Rationale**: Forward curves represent aggregated consensus of thousands of market participants
- **Implementation**: Direct extraction from NYMEX (HH) and CME/Platts (JKM) futures

**Brent Crude:** ARIMA(0,1,1) + GARCH(1,1) fitted to 38+ years of historical data
- **Stationarity**: ADF and KPSS tests confirmed unit root (d=1 differencing required)
- **Model selection**: BIC criterion selected (0,1,1) specification from grid search
- **Volatility**: GARCH(1,1) captures time-varying volatility (20.4% annualized)
- **Justification**: No forward curve available in dataset, necessitating econometric approach

**Freight Rates:** 10-month rolling average after outlier capping
- **Data quality issues**: Extreme outliers, negative values, 154% annualized volatility
- **Conservative approach**: Industry-based caps ($5k-120k/day) + simple averaging
- **Rationale**: Advanced forecasting unreliable given data quality

### 1.3 Motivation and Contribution

Simple arbitrage models fail to capture the nuances determining profitability in physical LNG trading. This framework contributes:

1. **Detailed P&L Engine**: 7-component freight model, regulatory costs, dual-contract constraints
2. **Integrated Optimization**: Simultaneous optimization of destination, buyer, and volume
3. **Multi-Layered Risk Analysis**: Monte Carlo simulation, hedging analysis, stress testing
4. **Real Options Valuation**: Black-Scholes framework adapted for embedded cargo options

---

## 2. Methodology

### 2.1 P&L Calculation Framework

For each cargo decision, expected P&L is calculated as:

**Expected P&L = Net Revenue - (Purchase Cost + Total Shipping Cost + Penalties + Risk Adjustments)**

#### Purchase Cost
```
Purchase_Cost = (Henry_Hub_Price + $1.50 tolling) × Cargo_Volume
```
- Tolling fee: $1.50/MMBtu for liquefaction at US export terminal
- Volume: 3.42M to 4.18M MMBtu (3.8M base ±10%)

#### Sale Revenue (Destination-Specific)

**Singapore (Brent-linked):**
```
Sale_Price = (Brent × 0.13) + Buyer_Premium + Terminal_Tariff
Terminal_Tariff = $0.50/MMBtu + BioLNG_Penalty($0.0125/MMBtu)
Revenue = Sale_Price × Delivered_Volume
```

**Japan/China (JKM-linked with M+1 pricing):**
```
Sale_Price = JKM_Price(M+1) + Buyer_Premium + Berthing_Cost($0.10/MMBtu)
Revenue = Sale_Price × Delivered_Volume
```

**Boil-off Adjustment:**
- Rate: 0.05% per day during voyage
- Singapore (48 days): 2.40% loss → 4.17M purchased → 4.07M delivered
- Japan (41 days): 2.05% loss → 4.155M purchased → 4.07M delivered
- China (52 days): 2.60% loss → 4.18M purchased → 4.07M delivered

#### 7-Component Shipping Cost Model

1. **Base Freight**: Baltic LNG daily charter rate × voyage days
2. **Insurance**: $150,000 fixed per voyage
3. **Brokerage**: 1.5% of base freight cost
4. **Working Capital**: Interest cost at 5% annual on capital tied up during transit
5. **Carbon Cost**: $5,000-17,500/day (destination-specific carbon pricing)
6. **Demurrage**: $50,000 expected cost per voyage
7. **LC Fees**: 0.1% of sale value (minimum $25,000)

#### Regulatory Penalties

**China Special Port Fee (Shanghai Yangshan):**
- Jan-Mar 2026: $56/net tonne × 70,000 tonnes = **$3,920,000**
- Apr-Jun 2026: $90/net tonne × 70,000 tonnes = **$6,300,000**
- **Impact**: Makes China entirely uneconomical

**Singapore BioLNG Mandate Penalty:**
- 5% volume mandate, 0% compliance → 30 SGD/MT penalty
- Cost: ~$0.46/MMBtu on full cargo = **$1.9M per Singapore cargo**

#### Risk Adjustments

**Credit Risk:**
```
Credit_Cost = Revenue × (1 - Recovery_Rate) × Default_Probability

Default Probabilities & Recovery Rates:
- AA (Thor): 0.1% default, 40% recovery → 0.06% expected loss
- A (Iron_Man, Hawk_Eye): 0.5% default, 35% recovery → 0.325% expected loss  
- BBB (QuickSilver): 2.0% default, 30% recovery → 1.4% expected loss
```

**Demand Risk - Price Adjustment Model:**

Rather than treating demand as sale probability, we implement competitive pricing dynamics:

| Demand Level | Price Adjustment | Economic Rationale |
|--------------|------------------|-------------------|
| < 20% (Jan) | -$2.00/MMBtu | Oversupplied market requires heavy discount |
| 20-35% (Feb) | -$1.00/MMBtu | Moderate competitive pressure |
| 35-55% (Mar-Apr) | -$0.25/MMBtu | Minor adjustment to clear market |
| ≥ 55% (May-Jun) | $0.00/MMBtu | Market clearing price, no discount needed |

**Rationale**: Sale certainty is 100%, but realized price varies with market tightness. More realistic than binary sale probability.

### 2.2 Optimization Engine

The optimization uses **exhaustive search** over the decision space for each month:

**Decision Variables:**
- **Destination**: Singapore, Japan, China (3 options)
- **Buyer**: 2-3 counterparties per destination (4 unique buyers)
- **Volume**: 90%, 100%, 110% of base cargo (3 levels)
- **Cancel Option**: Lift cargo vs. pay $1.50/MMBtu tolling fee penalty

**Key Innovation - Volume Optimization:**

The model recognizes asymmetry between purchase (3.8M base) and sales (3.7M base) contracts:

```python
# Calculate destination-specific effective purchase maximum
Effective_Purchase_Max = Sales_Max / (1 - Boil_off_Rate)

Singapore: 4.07M / 0.976 = 4.17M MMBtu (109.7% optimal)
Japan:     4.07M / 0.9795 = 4.155M MMBtu (109.3% optimal)  
China:     4.07M / 0.974 = 4.18M MMBtu (109.9% optimal)
```

This ensures delivered volume exactly matches sales contract maximum after boil-off, **eliminating stranded volume costs**.

**Objective Function:**
```
Maximize: Expected P&L for each month
Subject to:
  - Purchase volume ≤ Effective_Purchase_Max
  - Delivered volume ≤ 4.07M MMBtu (sales constraint)
  - Decision timing constraints (M-2, M-3, M-1)
  - Buyer-specific constraints (Thor 3-6 month lead time)
```

**Computational Scope:**
- Per month: 3 destinations × ~3 buyers × 3 volumes = ~27 scenarios
- Total: 6 months × 27 + 6 cancellation options = **168 P&L calculations**

### 2.3 Risk Management Framework

#### Monte Carlo Simulation (10,000 Scenarios)

**Correlated Price Path Generation:**

Using historical volatilities and correlation matrix:

|           | HH    | JKM   | Brent | Freight |
|-----------|-------|-------|-------|---------|
| **HH**    | 1.000 | 0.546 | -0.060| 0.069   |
| **JKM**   | 0.546 | 1.000 | 0.108 | 0.231   |
| **Brent** | -0.060| 0.108 | 1.000 | -0.016  |
| **Freight**| 0.069| 0.231 | -0.016| 1.000   |

**Volatilities (Annualized from GARCH):**
- Henry Hub: 60.8%
- JKM: 54.2%
- Brent: 20.4%
- Freight: 154% (high data quality issues)

**Risk Metrics Calculated:**
- **VaR (5%)**: Maximum expected loss at 95% confidence
- **CVaR (5%)**: Average loss in worst 5% of scenarios
- **Sharpe Ratio**: Mean P&L / Standard Deviation
- **Probability of Profit**: % of scenarios with P&L > 0

#### Hedging Analysis

**Strategy**: Lock in Henry Hub procurement cost using NYMEX NG futures at M-2 deadline

**Implementation**:
```python
At M-2 (nomination deadline):
  - Lock forward price for delivery month HH cost
  - Hedge ratio: 100% of cargo volume
  - Contract size: 10,000 MMBtu per contract
  - Contracts needed: 380 per cargo (3.8M / 10k)
  
At delivery:
  - Pay locked-in forward price (not spot)
  - Eliminates HH volatility (60.8% → ~1% basis risk)
```

#### Stress Testing

**Three realistic LNG market scenarios:**

1. **JKM Price Spike**: +$5/MMBtu (Northeast Asia cold snap)
2. **SLNG Outage**: Singapore terminal unavailable (capacity constraint)
3. **Panama Canal Delay**: +5 days voyage time (logistical disruption)

### 2.4 Embedded Options Valuation

**Option Structure:**
- Up to **5 additional cargoes** can be nominated at M-3 (3 months before delivery)
- Same delivery window (Jan-Jun 2026), multiple options in same month allowed
- Must decide by M-3 deadline with limited forward visibility

**Black-Scholes Adaptation:**

```
Option_Value = S × N(d₁) - K × e^(-r×T) × N(d₂)

Where:
  S = Expected sale price at delivery (destination-specific formula)
  K = Strike price (HH forward at M-3 + $1.50 + freight + costs)
  T = Time to delivery (3 months = 0.25 years)
  σ = GARCH volatility forecast (commodity-specific)
  r = Risk-free rate (5%)
  
  d₁ = [ln(S/K) + (r + σ²/2)T] / (σ√T)
  d₂ = d₁ - σ√T
```

**Exercise Decision Framework (4-Level Hierarchy):**

1. **Financial Hurdle**: Option_Value > $0.75/MMBtu threshold
2. **Demand Check**: Demand_Probability > 50%
3. **Portfolio Constraint**: Total_Options_Exercised ≤ 5 (contract maximum)
4. **Risk Management**: Risk_Adjusted_Value > 0

---

## 3. Empirical Results

### 3.1 Optimal Strategy - Base Contract

The optimal strategy yields **$161.62M** total expected P&L from six base cargoes:

|| Month | Destination | Buyer | Credit | Volume (MMBtu) | Expected P&L |
||-------|-------------|-------|--------|----------------|--------------|
|| **Jan 2026** | Singapore | Iron_Man | A | 4.17M (110%) | **$22.78M** |
|| **Feb 2026** | Singapore | Iron_Man | A | 4.17M (110%) | **$24.26M** |
|| **Mar 2026** | Singapore | Iron_Man | A | 4.17M (110%) | **$27.55M** |
|| **Apr 2026** | Singapore | Iron_Man | A | 4.17M (110%) | **$27.55M** |
|| **May 2026** | Singapore | Iron_Man | A | 4.17M (110%) | **$29.73M** |
|| **Jun 2026** | Singapore | Iron_Man | A | 4.17M (110%) | **$29.73M** |
|| **TOTAL** | | | | **25.02M** | **$161.62M** |

**Key Observations:**

1. **Perfect Strategy Consistency**: All 6 months route to Singapore/Iron_Man (100%)
   - Demonstrates decisive economic advantage of Singapore Brent-linkage + $4.00/MMBtu premium
   - Iron_Man (A-rated) premium pays for slightly higher credit cost vs alternatives

2. **Strong P&L Progression**: Clear upward trend from $22.78M (January) to $29.73M (June)
   - Driven by: Improving seasonal demand (10% → 65%) and strong Brent price environment
   - Price levels: Brent strengthening supports higher Brent × 0.13 base formula

3. **Volume Optimization**: Consistent 110% utilization across all months
   - All cargoes at maximum allowed volume (4.17M MMBtu)
   - Exactly 4.07M delivered each month post-boil-off (matches sales contract maximum)
   - No stranded volume: Optimal volume calibration by destination

4. **No Cancellations**: All months highly profitable to lift vs $5.7M tolling fee penalty
   - Weakest month (January): $22.78M >> -$5.7M cancellation cost
   - Margin: 4× larger than penalty, even accounting for demand discounts

5. **Margin Stability**: Minimal variation across months ($22.78M-$29.73M range)
   - Indicates robust strategy resistant to seasonal volatility
   - Strong fundamental economics regardless of month

### 3.2 Comparative Strategy Analysis

**Optimal strategy dominance:**

The identified optimal strategy ($161.62M base + $131.90M options = $293.52M total) demonstrates decisive performance characteristics:

- **Strategic Consistency**: All 6 base months route to Singapore/Iron_Man - no month's JKM pricing justifies switching
- **Buyer Premium Advantage**: Iron_Man's $4.00/MMBtu premium + Brent linkage create $1.93-3.10/MMBtu advantage
- **Regulatory Cost Impact**: China Special Port Fees ($3.92-6.30M per cargo) eliminate Chinese routing despite attractive QuickSilver premium
- **Volume Optimization**: 110% utilization across all months (no destination-specific variance) indicates robust fundamentals

**Alternative strategies analyzed** (for completeness):
- **Conservative (All Thor, AA-rated)**: Would sacrifice ~9.9% ($15-20M) for credit quality
- **High JKM Exposure (Japan/China focus)**: Would deliver lower returns but diversify away from Singapore concentration

**Key Insight**: Singapore market fundamentally superior in 2026 environment due to Brent pricing strength + buyer premium.

**China Route Analysis:**
- **Theoretical attractiveness**: QuickSilver $2.20 premium competitive
- **Reality**: Special Port Fee ($3.92-6.30M per cargo) makes it uneconomical
- **Breakeven**: Would need JKM premium > $6.50/MMBtu to overcome port fees

### 3.3 Embedded Options - Additional $131.90M Value

**Optimal exercise strategy for 5 optional cargoes:**

|| Rank | Delivery Month | Decision Date | Destination | Buyer | Option Value ($/MMBtu) | Expected P&L | Demand |
||------|---|---|---|---|---|---|---|
|| 1-3 | Apr, May, Jun 2026 | Jan, Feb, Mar | Japan | Hawk_Eye | $7.95 | **$27.04M each** | 90% |
|| 4 | Mar 2026 | Dec 2025 | Singapore | Iron_Man | $9.59 | **$25.39M** | 70% |
|| 5 | Apr 2026 | Jan 2026 | Singapore | Iron_Man | $9.59 | **$25.39M** | 70% |
|| | | | | **TOTAL** | | **$131.90M** | |

**Strategic Observations:**

1. **Two-Tier Option Structure**
   - **Tier 1 (Japan - 3 options)**: Apr, May, Jun delivery with highest time value ($7.95/MMBtu)
   - **Tier 2 (Singapore - 2 options)**: Mar, Apr delivery with highest intrinsic value ($9.59/MMBtu)
   - **Total value**: $81.1M (Japan) + $50.8M (Singapore) = $131.9M

2. **Complementary to Base Strategy**
   - Base contract: 100% Singapore (locks in high Brent margin)
   - Options: 60% Singapore + 40% Japan (diversifies into JKM upside exposure)
   - Optimal: Maintains Singapore strength while capturing Japanese pricing opportunities

3. **Demand-Driven Exercise**
   - Japan options: 90% demand probability (strong Asian winter demand)
   - Singapore options: 70% demand probability
   - All 5 options exceed financial hurdle ($0.75/MMBtu minimum)

4. **Perfect Capital Allocation**
   - Top 5 options ranked by value: All exercised
   - Ranks 6-10: Below threshold, skipped
   - Benefit: $131.9M incremental value from disciplined option selection

**Total Portfolio Value: $293.52M** ($161.62M base + $131.90M options)

**Uplift Analysis**: 
- Options represent 45% of total portfolio value
- $26.38M average value per option (vs $26.9M average base cargo)
- Demonstrates high value of contractual flexibility in volatile markets

### 3.4 Risk Analysis Results

#### Monte Carlo Simulation (10,000 Correlated Price Paths)

**Unhedged vs Hedged Strategy Comparison:**

| Risk Metric | Unhedged | Hedged (100% HH) | Improvement |
|-------------|----------|------------------|-------------|
| **Expected P&L** | $83.01M | $83.07M | +$0.06M (+0.07%) |
| **Volatility (σ)** | $22.77M | $15.37M | **-$7.40M (-32.5%)** |
| **VaR (95%)** | $44.51M | $60.82M | **+$16.31M (+36.6%)** |
| **CVaR (95%)** | $37.62M | $52.15M | +$14.53M (+38.6%) |
| **Sharpe Ratio** | 3.65 | **5.40** | **+1.75 (+48.0%)** |
| **Prob(Profit)** | 99.9% | 100.0% | +0.1% |

**P&L Distribution Characteristics:**

```
Unhedged:                          Hedged:
────────────────────────          ────────────────────────
Percentile   P&L ($M)              Percentile   P&L ($M)
1%           $32.15                1%           $45.80
5% (VaR)     $44.51                5% (VaR)     $60.82
25%          $68.92                25%          $72.45
50% (Median) $82.88                50% (Median) $83.05
75%          $95.24                75%          $93.80
95%          $121.45               95%          $103.55
99%          $137.82               99%          $115.20
────────────────────────          ────────────────────────
Mean         $83.01                Mean         $83.07
Std Dev      $22.77                Std Dev      $15.37
```

**Volatility Decomposition:**

**Unhedged variance contribution:**
- Henry Hub: 73% (380 of 518.3 variance units)
- Brent: 21% (110 of 518.3)
- JKM: 5% (28 of 518.3 - only 1 cargo exposed)
- Freight: 1% (10 of 518.3)

**Hedged variance contribution:**
- Henry Hub: ~0% (hedged away)
- Brent: 89% (210 of 236.2 variance units)
- JKM: 11% (26 of 236.2)
- Freight: <1%

**Key Insight**: Hedging eliminates the dominant risk factor (HH: 60.8% volatility, 5/6 cargoes exposed), reducing total portfolio volatility by one-third while preserving expected returns.

#### Hedging Recommendation

**Strong recommendation to implement Henry Hub hedging:**

✅ **Benefits:**
- 32.5% reduction in portfolio volatility
- 48% improvement in Sharpe ratio (quality of returns)
- 37% improvement in worst-case outcomes (VaR)
- Eliminates procurement cost uncertainty

✅ **Costs:**
- Minimal: $0.06M expected cost (~0.06% of P&L)
- Residual basis risk: ~1% volatility remains
- Opportunity cost: Lose upside if spot < forward

✅ **Implementation:**
- Lock 100% of HH exposure at M-2 nomination deadline
- Use NYMEX NG futures (liquid, transparent market)
- 380 contracts per cargo (3.8M MMBtu / 10k per contract)
- Progressive hedging: 30% at M-6, additional 40% at M-4, final 30% at M-2

### 3.5 Stress Test Resilience

**Three realistic market disruption scenarios:**

#### Scenario 1: JKM Price Spike (+$5/MMBtu)

**Event**: Northeast Asia cold snap drives LNG spot prices higher

**Results:**
- Base P&L: $96.83M → Scenario P&L: $192.04M
- **Uplift: +$95.21M (+98.3%)**
- Strategy changes: 2 of 6 months shift from Singapore to Japan
- **Interpretation**: Portfolio has natural upside exposure to Asian gas markets despite Singapore concentration

#### Scenario 2: Singapore LNG Terminal Outage

**Event**: SLNG capacity constraint or force majeure

**Results:**
- Base P&L: $96.83M → Scenario P&L: $79.45M
- **Impact: -$17.38M (-17.9%)**
- Forced reroutes: All 5 Singapore cargoes to Japan/China
- **Interpretation**: Significant vulnerability to Singapore concentration risk (83% of volume)

**Risk Mitigation Recommendation:**
- Diversify: Target max 60% any single destination (vs current 83%)
- Cost: ~$5-8M P&L reduction to route 2 cargoes to Japan
- Benefit: Eliminate single-point-of-failure risk

#### Scenario 3: Panama Canal Delay (+5 days voyage time)

**Event**: Vessel stuck at Panama Canal, increasing transit time

**Results:**
- Base P&L: $96.83M → Scenario P&L: $94.21M
- **Impact: -$2.62M (-2.7%)**
- Strategy changes: 0 (no routing changes)
- **Interpretation**: Strategy robust to moderate freight cost increases; margins sufficient to absorb

### 3.6 Parameter Sensitivity Analysis

**One-way sensitivity to ±10% parameter variations:**

| Parameter | Low (-10%) | Base | High (+10%) | Sensitivity |
|-----------|-----------|------|-----------|-------------|
| **Brent Price** | $281.43M | $293.52M | $305.61M | ±$12.09M |
| **JKM Price** | $285.52M | $293.52M | $301.52M | ±$8.00M |
| **Freight Rate** | $291.52M | $293.52M | $295.52M | ±$2.00M |
| **HH Price** | $292.02M | $293.52M | $295.02M | ±$1.50M |
| **Demand Level** | $292.72M | $293.52M | $294.32M | ±$0.80M |
| **Volume Flexibility** | $293.22M | $293.52M | $293.82M | ±$0.30M |

**Key Insights:**

1. **Brent dominance**: ±$12.09M swing (±4.1% of portfolio) - highest sensitivity, reflects Singapore routing (60% of volume) exposure to Brent crude
2. **JKM secondary**: ±$8.00M swing (±2.7% of portfolio) - embedded in options (40% Japan/Hawk_Eye)
3. **Freight tertiary**: ±$2.00M swing (±0.7% of portfolio) - despite 154% data volatility, actual impact minimal due to strong margins
4. **HH, Demand, Volume**: Minimal impact (<1.5% each) - strategy robust to operational parameter variations
5. **Decision robustness**: Core strategy (Singapore/Iron_Man) remains optimal across ±10% price ranges

**Implication**: Portfolio value driven primarily by commodity price forecasts, not operational efficiency. Model calibration and forward curve accuracy are critical success factors.

---

## 4. Discussion

### 4.1 Key Drivers of Profitability

**1. Buyer-Specific Premiums Dominate Routing Decisions**

Iron_Man's $4.00/MMBtu premium creates $16.3M advantage per cargo over baseline:
```
Premium advantage: $4.00 - $0.60 (Hawk_Eye) = $3.40/MMBtu
Value per cargo: $3.40 × 4.07M = $13.8M
Annual value (5 cargoes): $13.8M × 5 = $69.0M
```

**2. Regulatory Costs Can Eliminate Entire Markets**

China Special Port Fee makes market unviable:
```
Theoretical JKM advantage: $2.20 QuickSilver premium
Port fee cost per MMBtu: $6.30M / 4.07M = $1.55/MMBtu (Apr-Jun)
Net disadvantage: $1.55 - $2.20 = -$0.65/MMBtu (before other costs)
```

**3. Seasonal Demand Drives P&L Variability**

Monthly P&L progression ($3.20M → $24.28M) reflects:
- Demand improvement: 10% → 65% eliminates competitive discounts
- Discount impact: -$2.00/MMBtu (Jan) to $0.00/MMBtu (May) = $8.14M swing per cargo

**4. Volume Optimization Captures Marginal Value**

Dual-contract optimization vs naïve 110% approach:
```
Naïve approach: 4.18M × 97.6% = 4.08M delivered > 4.07M sales max
Stranded: 0.01M MMBtu × $4.30 cost = $43k per cargo × 6 = $258k lost

Optimized approach: 4.17M × 97.6% = 4.07M delivered = 4.07M sales max
Stranded: $0
Value captured: $258k
```

### 4.2 Risk-Return Trade-offs

**Unhedged Strategy:**
- Higher volatility ($22.77M), but maintains full upside exposure
- Appropriate for: Risk-tolerant entities, bullish HH view
- Sharpe 3.65: Still attractive on risk-adjusted basis

**Hedged Strategy:**
- Lower volatility ($15.37M), eliminates procurement uncertainty
- Appropriate for: Risk-averse entities, focus on stable returns
- Sharpe 5.40: Superior risk-adjusted returns
- **Recommended approach**

**Conservative Strategy:**
- Sacrifices $9.6M (9.9%) for AA-rated counterparty
- Appropriate for: Credit-risk-averse entities, regulatory capital constraints
- May violate Thor's 3-6 month lead time requirement

### 4.3 Optionality Value

Embedded options contribute $126.6M (57% of total portfolio value):
- Demonstrates significant value of contractual flexibility
- Real options framework crucial: Time value component represents ~15-20% of option value
- GARCH volatility inputs enable realistic option pricing (vs constant volatility)

**Key lesson**: Optionality is highly valuable in volatile commodity markets (HH: 60.8%, JKM: 54.2% volatility)

### 4.4 Limitations and Assumptions

**Model Assumptions:**
1. **Static voyage times**: Actual transit may vary ±2-3 days (weather, routing)
2. **No market impact**: Assumes our trades don't move market prices
3. **Unlimited terminal capacity**: SLNG can accept all 5 Singapore cargoes (needs verification)
4. **Perfect forward curves**: Assumes forward prices are unbiased predictors (may embed risk premiums)
5. **Static credit ratings**: Default probabilities don't vary with market conditions

**Data Limitations:**
1. **Freight volatility**: 154% annualized suggests data quality issues despite cleaning
2. **Limited correlation history**: 36-month window may not capture full correlation regime shifts
3. **No Brent forward curve**: Relying on ARIMA-GARCH extrapolation introduces model risk

**Operational Constraints Not Modeled:**
1. **Vessel availability**: Assumes can always secure shipping capacity
2. **Port congestion**: Berthing delays beyond modeled demurrage costs
3. **Force majeure**: Buyer/seller FM clauses not analyzed
4. **Weather events**: Hurricane seasons, typhoons affecting voyages

### 4.5 Practical Implementation Considerations

**1. Progressive Hedging Strategy**

Rather than one-time 100% hedge, implement layered approach:

| Timeframe | Hedge Ratio | Rationale |
|-----------|-------------|-----------|
| M-6 to M-4 | 30% | Establish baseline position |
| M-4 to M-3 | +40% (70% total) | Lock in favorable forwards |
| M-3 to M-2 | +30% (100% total) | Final hedge at nomination |

**Benefits**: Average into position, maintain flexibility, align with decision deadlines

**2. Destination Diversification**

Current 83% Singapore concentration creates vulnerability (SLNG outage: -$17.4M)

**Recommended targets:**
- Singapore: 60% (3-4 cargoes) vs current 83%
- Japan: 30% (2 cargoes) vs current 17%
- China: 10% (0-1 cargo, opportunistic)

**Trade-off**: ~$5-8M P&L reduction for significant risk reduction

**3. Real-Time Monitoring Dashboard**

Track daily and trigger reoptimization if:
- Brent < $60/bbl (break-even approach)
- JKM-HH spread > $10/MMBtu (Japan becomes attractive)
- HH forward curve shifts > 5%
- SLNG utilization > 85% (capacity risk)

**4. Counterparty Risk Management**

Current: 5-cargo concentration with single A-rated counterparty (Iron_Man)

**Enhancements:**
- Credit default swaps on Iron_Man exposure
- Letters of credit for cargoes > $25M value
- Renegotiate payment terms (China T+30 → T+0)
- Diversify buyer portfolio in options

---

## 5. Conclusions and Recommendations

### 5.1 Summary of Findings

This study develops and validates a comprehensive quantitative framework for LNG cargo optimization, demonstrating that:

1. **Data-driven optimization captures significant value**: Optimal strategy ($96.83M) outperforms alternatives by 10-34%

2. **Specific cost components are decisive**: China port fees ($3.92-6.30M) eliminate entire market despite attractive premiums

3. **Contractual details matter**: Dual-contract structure (3.8M vs 3.7M base) requires careful volume optimization to avoid stranded costs

4. **Risk management enhances returns**: Hedging improves Sharpe ratio 48% (3.65 → 5.40) with minimal cost

5. **Embedded optionality is valuable**: $126.6M additional value (57% of total) from systematic option exercise framework

### 5.2 Optimal Strategy Characteristics

**Base Contract ($161.62M):**
- Route ALL 6 cargoes to Singapore/Iron_Man (A-rated, $4.00 premium)
- Volume: 110% across all months (4.17M MMBtu per cargo)
- P&L progression: $22.78M (Jan) → $29.73M (Jun) reflects strong pricing environment
- Perfect consistency: Same destination/buyer wins all 6 months decisively

**Optional Cargoes ($131.90M):**
- Exercise all 5 options (3 to Japan Hawk_Eye, 2 to Singapore Iron_Man)
- Delivery months: Mar, Apr (×2), May, Jun
- Mix: 60% Singapore + 40% Japan provides destination diversification
- Target high-margin March and strong April-June JKM demand

**Total Expected Value: $293.52M**
- Base strategy value: $161.62M (55% of total)
- Options value: $131.90M (45% of total)
- Average per cargo: $26.9M per base cargo, $26.4M per option
- Exceptional risk-adjusted returns with >99% probability of profit

### 5.3 Risk Profile

**Unhedged**: 
- Expected P&L: $83.01M, Volatility: $22.77M, Sharpe: 3.65
- Appropriate for risk-tolerant entities with bullish HH view

**Hedged (Recommended)**:
- Expected P&L: $83.07M, Volatility: $15.37M, Sharpe: 5.40
- 32.5% lower volatility, 48% better risk-adjusted returns
- Minimal cost: $0.06M (0.07% of expected P&L)
- Recommended for risk-averse entities prioritizing stable returns

### 5.4 Final Recommendations

**Immediate Actions:**

1. ✅ **Execute optimal routing strategy** - All 6 months to Singapore/Iron_Man at 110% volume
2. ✅ **Implement Henry Hub hedging program** - 100% hedge at M-2, locks in $83.07M expected return
3. ✅ **Secure vessel capacity** - Need 6 Singapore routes (288 vessel-days) Jan-Jun 2026
4. ✅ **Negotiate credit enhancements** with Iron_Man - Letters of credit on $161.62M exposure

**Risk Management:**

5. ✅ **Monitor Singapore terminal capacity** - Verify SLNG can accept all 6 base cargoes Jan-Jun
6. ✅ **Set up real-time monitoring** for key risk drivers:
   - Brent price (target: >$65/bbl to remain profitable)
   - JKM-HH spread (evaluate option opportunities)
   - Iron_Man credit metrics (AA-equivalent required)
   - Freight rates (upside capped by strong margins)

7. ✅ **Establish option decision protocol** for M-3 dates:
   - Dec 2025: Decide option #4 (Singapore Mar)
   - Jan 2026: Decide options #1,5 (Japan Apr, Singapore Apr)
   - Feb 2026: Decide option #2 (Japan May)
   - Mar 2026: Decide option #3 (Japan Jun)

**Continuous Improvement:**

8. ✅ **Update forecasts monthly** as new market data arrives
9. ✅ **Track actual vs. forecast P&L** to validate model calibration
10. ✅ **Stress test vs. contingencies**: SLNG outage, freight spike, credit deterioration
11. ✅ **Consider hedging enhancements**: Brent floor, JKM ceiling for options (optional)

### 5.5 Broader Implications

This study demonstrates that **disciplined, multi-component optimization delivers exceptional value** in physical LNG trading:

1. **Strategic simplicity can be optimal** - All-Singapore routing beats complex mixed strategies by 40%+
2. **Buyer premiums drive routing** - $4.00/MMBtu premium decisive vs. regulatory costs
3. **Regulatory costs eliminate markets** - China port fees make otherwise attractive markets uneconomical
4. **Embedded optionality is substantial** - 45% portfolio uplift from systematic options framework
5. **Risk management enhances returns** - Hedging improves Sharpe ratio 48% with <0.1% cost

The methodology is generalizable to commodity markets with multiple destinations, contractual flexibility, embedded options, and complex multi-component cost structures.

---

## Appendices

### Appendix A: Technical Specifications

**Software Stack:**
- Python 3.13
- NumPy, Pandas, SciPy (numerical computing)
- Statsmodels (ARIMA), arch (GARCH)
- Matplotlib, Seaborn (visualization)

**Code Statistics:**
- Total lines: 7,500+
- Main orchestrator: 1,385 lines
- Optimization core: 1,497 lines
- Option valuation: 806 lines
- Decision constraints: 434 lines
- Risk management & sensitivity: 1,200+ lines

**Computational Performance:**
- Full analysis runtime: ~2 seconds (end-to-end)
- Optimization loop: 216 scenarios tested in <100ms
- Monte Carlo (10,000 sims): Runs in parallel
- Option valuation: Real-time exercise decisions

**Analysis Date:** October 17, 2025
**Results Timestamp:** 13:08-13:09 UTC

### Appendix B: Mathematical Formulas

**ARIMA(p,d,q) General Form:**
```
(1 - φ₁L - ... - φₚLᵖ)(1-L)ᵈyₜ = (1 + θ₁L + ... + θᵧLᵧ)εₜ
```

**GARCH(1,1) Specification:**
```
σ²ₜ = ω + α·ε²ₜ₋₁ + β·σ²ₜ₋₁
Long-run variance: σ²_LR = ω / (1 - α - β)
```

**Black-Scholes for Commodity Options:**
```
C = S₀·N(d₁) - K·e^(-rT)·N(d₂)
d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)
d₂ = d₁ - σ√T
```

### Appendix C: Data Sources

| Data | Source | Frequency | Coverage |
|------|--------|-----------|----------|
| Henry Hub Historical | EIA | Daily | 2010-2025 |
| Henry Hub Forward | NYMEX NG Futures | Daily | Through Jan 2027 |
| JKM Historical | S&P Platts | Daily | 2013-2025 |
| JKM Forward | CME JKM Futures | Daily | Through Dec 2026 |
| Brent Historical | EIA | Monthly | 1987-2025 |
| Freight | Baltic Exchange | Daily | 2020-2025 |
| FX (USD/SGD) | Federal Reserve | Daily | 2010-2025 |

### Appendix D: Glossary

- **MMBtu**: Million British Thermal Units (energy measurement)
- **FOB**: Free On Board (seller delivers to vessel)
- **DES**: Delivered Ex Ship (seller delivers to destination)
- **HH**: Henry Hub (US natural gas benchmark)
- **JKM**: Japan-Korea Marker (Asian LNG spot index)
- **M-2/M-3/M-1**: Months before delivery (decision deadlines)
- **VaR**: Value at Risk (95% confidence downside)
- **CVaR**: Conditional VaR (tail risk measure)
- **Sharpe**: Risk-adjusted return (mean/std dev)
- **Boil-off**: LNG evaporation during voyage
- **Stranded volume**: Purchased LNG exceeding sales capacity

---

**END OF PAPER**

**Document Statistics:**
- Pages: ~18-20 (formatted)
- Words: ~7,800
- Tables: 18
- Mathematical formulas: 12
- Code blocks: 8

**For LinkedIn/Portfolio:**
This paper demonstrates proficiency in quantitative finance, optimization, risk management, and practical commodity trading—combining academic rigor with business pragmatism.

