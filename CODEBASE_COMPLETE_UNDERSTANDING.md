# 🚀 Complete Codebase Understanding - LNG Trading Optimization System

**Status:** ✅ Fully Analyzed and Documented  
**Project:** NTU CEIT x Baringa Partnership Trading Competition 2025  
**Last Updated:** October 21, 2025

---

## 📑 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture & Design](#architecture--design)
3. [Module-by-Module Guide](#module-by-module-guide)
4. [Data Flow](#data-flow)
5. [Key Algorithms](#key-algorithms)
6. [Business Logic](#business-logic)
7. [How to Run](#how-to-run)
8. [File Organization](#file-organization)

---

## 🎯 System Overview

### Purpose
Optimize LNG cargo trading decisions for a 6-month period (Jan-Jun 2026) involving:
- **6 base cargoes** (3.8M MMBtu each, guaranteed purchases)
- **5 optional cargoes** (embedded call options, exercisable with >3 month notice)
- **3 destinations**: Singapore (Brent-linked pricing), Japan/China (JKM-linked pricing)
- **4 buyers** across destinations with varying credit ratings (AA/A)
- **Volume flexibility**: ±10% from base volume (contract terms)

### Expected Output
- **Strategy P&L**: $96.83M (6 base cargoes) + $126.6M (5 optional) = $223.4M
- **Risk metrics**: VaR, CVaR, Sharpe ratio via Monte Carlo
- **Hedging analysis**: Henry Hub futures hedge impact
- **Scenario testing**: Bull/bear/stress scenarios

---

## 🏗️ Architecture & Design

### System Layers

```
┌─────────────────────────────────────────────────────────────┐
│  OUTPUT LAYER: Results, Reports, Visualizations             │
│  (save_results, create_sensitivity_plots)                   │
└─────────────────────────────────────────────────────────────┘
                           ▲
┌─────────────────────────────────────────────────────────────┐
│  ANALYSIS LAYER: Risk, Options, Sensitivity                 │
│  (MonteCarloRiskAnalyzer, EmbeddedOptionAnalyzer,          │
│   SensitivityAnalyzer, ScenarioAnalyzer)                    │
└─────────────────────────────────────────────────────────────┘
                           ▲
┌─────────────────────────────────────────────────────────────┐
│  OPTIMIZATION LAYER: Strategy Generation                    │
│  (CargoPnLCalculator, StrategyOptimizer)                    │
└─────────────────────────────────────────────────────────────┘
                           ▲
┌─────────────────────────────────────────────────────────────┐
│  FORECASTING LAYER: Price Predictions                       │
│  (ARIMA+GARCH, Forward Curves, Volatility)                  │
└─────────────────────────────────────────────────────────────┘
                           ▲
┌─────────────────────────────────────────────────────────────┐
│  DATA LAYER: Loading, Parsing, Validation                   │
│  (loaders.py: 13 Excel files → processed DataFrames)        │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles
1. **Modularity**: Each module has single responsibility
2. **Configurability**: Business parameters in `config/constants.py`
3. **Logging**: Comprehensive logging to both file and console
4. **Validation**: Input/output validation at each stage
5. **Reproducibility**: Fixed random seed (42) for consistent results

---

## 📦 Module-by-Module Guide

### 1. **main_optimization.py** (1,385 lines) - Orchestrator

**Purpose**: Main execution pipeline that coordinates all system components

**Key Functions**:

#### `main(run_monte_carlo=True, run_scenarios=True, use_arima_garch=True, run_hedging=True, run_sensitivity=True)`

The master controller that executes 7-step pipeline:

```
Step 1: Load Data (load_all_data)
        ↓
Step 2: Prepare Forecasts (prepare_forecasts_arima_garch)
        ↓
Step 3: Run Optimization (generate_all_strategies)
        ↓
Step 4: Validate Constraints (DecisionValidator)
        ↓
Step 5: Monte Carlo Analysis (run_monte_carlo)
        ↓
Step 6: Hedging Analysis (generate_hedged_strategies)
        ↓
Step 7: Save Results (save_results)
```

**Key Sub-Functions**:

#### `prepare_forecasts_arima_garch(data) → Dict[str, pd.Series]`
- **Input**: Raw market data dictionary
- **Process**: 
  - Henry Hub: Uses forward curve (most accurate)
  - JKM: Uses forward curve
  - Brent: Fits ARIMA+GARCH model (no forward available)
  - Freight: Uses naive forecast (recent average)
- **Output**: Dictionary with 6-month forecasts for each commodity
- **Logic**: 
  ```python
  for commodity in ['henry_hub', 'jkm', 'brent', 'freight']:
      if has_forward_curve(commodity):
          use forward prices from market data
      else:
          fit ARIMA model to historical data
          fit GARCH model to residuals
          generate point forecasts + confidence intervals
  ```

#### `generate_hedged_strategies(unhedged, forecasts, data) → Dict`
- **Input**: Unhedged strategies, forecasts, market data
- **Process**:
  - For each month and destination decision:
    - Calculate base P&L (unhedged)
    - Add Henry Hub futures hedge P&L
    - Hedge locks in HH cost at M-2 forward price
  - Reduces HH volatility to near-zero in Monte Carlo
- **Output**: Parallel set of hedged strategies
- **Hedge Formula**:
  ```
  Hedge P&L = (HH_Spot_M - HH_Forward_M-2) × Volume
  Total P&L = Unhedged P&L + Hedge P&L
  ```

#### `calculate_volatilities_and_correlations(data) → (Dict, DataFrame)`
- **Purpose**: Calculate historical volatilities and correlations for Monte Carlo
- **Process**:
  1. Resample all daily data to monthly (reduces noise)
  2. Calculate monthly returns (pct_change)
  3. Annualize volatilities (multiply by √12)
  4. Create correlation matrix
- **Output**: 
  - `volatilities`: Dict with annualized volatilities for 4 commodities
  - `correlations`: 4×4 correlation matrix (used for Cholesky decomposition in MC)

#### `save_results(strategies, monte_carlo_results, scenario_results, ...)`
- **Purpose**: Export all results to Excel/CSV files
- **Outputs**:
  1. `strategies_comparison_*.xlsx` - All strategies P&L comparison
  2. `optimal_strategy_*.csv` - Decision table (what to sell to whom each month)
  3. `monte_carlo_risk_metrics_*.xlsx` - VaR, CVaR, Sharpe ratios
  4. `scenario_analysis_*.xlsx` - Bull/Bear/Stress scenario results
  5. `hedging_comparison_*.xlsx` - Hedged vs unhedged risk metrics

---

### 2. **data_processing/loaders.py** (557 lines) - Data Ingestion

**Purpose**: Load and parse 13 Excel files with complex formats

**Key Functions**:

#### `load_all_data() → Dict[str, pd.DataFrame]`
Master loader that calls all commodity loaders:
- Calls: `load_henry_hub_data()`, `load_jkm_data()`, `load_brent_data()`, `load_wti_data()`, `load_freight_data()`, `load_fx_data()`
- Returns: Dictionary with DataFrames for each commodity
- Handles all Excel format variations automatically

#### `load_henry_hub_data() → pd.DataFrame`
- **Challenge**: Complex Excel format with metadata header (~30 rows)
- **Solution**: 
  1. Find "Exchange Date" header row dynamically
  2. Read from that row onwards
  3. Parse contract month from names: "NAT GAS JAN26/d" → 2026-01
- **Output**: DataFrame with columns ['HH_Historical', 'HH_Forward']

#### `load_freight_data() → pd.DataFrame`
- **Challenge**: Daily data has extreme volatility (~5000% annualized)
- **Solution**:
  1. Load daily Baltic LNG data (.BLNG3g column)
  2. Resample to monthly averages (reduces volatility to ~10-30%)
  3. Apply hard caps at industry limits ($120k/day max, $5k/day min)
- **Output**: Monthly aggregated freight prices

#### `load_jkm_data() → pd.DataFrame`
- **Challenge**: Contract names have non-standard format ("LNG JnK NOV5/d")
- **Solution**: Parse with regex pattern `([A-Z]{3})(\d)/d` to extract month/year
- **Output**: DataFrame with ['JKM_Historical', 'JKM_Forward']

**Data Quality Fixes**:
- All loaders handle missing values (dropna)
- All loaders sort by date and set DatetimeIndex
- All loaders convert Excel dates to pandas Timestamps
- All loaders log row counts and date ranges

---

### 3. **models/optimization.py** (1,497 lines) - Core Optimization

**Purpose**: Calculate P&L and optimize routing strategies

#### **Class: CargoPnLCalculator**

Master calculator for single cargo P&L

**Methods**:

##### `calculate_purchase_cost(hh_price, month, cargo_volume) → Dict`
```python
Purchase_Cost = (HH_Price + $2.50/MMBtu) × Cargo_Volume
# $2.50 = tolling fee at US export terminal (case pack, page 15)
```
- **Input**: Henry Hub price, delivery month, purchase volume
- **Output**: Dict with `price_per_mmbtu`, `total_cost`, `volume`

##### `calculate_sale_revenue(destination, buyer, brent, jkm, jkm_next, month, volume) → Dict`

Destination-specific pricing formulas:

**Singapore (Brent-linked)**:
```python
Price_per_MMBtu = (Brent × 0.13) + Buyer_Premium + Terminal_Tariff + BioLNG_Penalty
Revenue = Price_per_MMBtu × Delivered_Volume × (1 - Boil_off)
```

**Japan/China (JKM-linked)**:
```python
Price_per_MMBtu = JKM(M+1) + Buyer_Premium + Berthing_Cost
Revenue = Price_per_MMBtu × Delivered_Volume × (1 - Boil_off)
```

- **Special handling**: 
  - Sales contract volume is DIFFERENT from purchase (3.7M vs 3.8M)
  - Must cap sales at max (accounts for boil-off so nothing stranded)
  - Accounts for stranded volume (paid for, can't sell)

##### `calculate_freight_cost(destination, freight_rate, purchase_cost, sale_value, cargo_volume) → Dict`

Comprehensive freight cost with 7 components:

```python
Total_Freight = Base_Freight + Insurance + Brokerage + Working_Capital 
              + Carbon_Cost + Demurrage + LC_Cost

Base_Freight = Daily_Rate × Voyage_Days × Route_Scaling_Factor
Insurance = $150k per voyage
Brokerage = 1.5% of base freight
Working_Capital = Purchase_Cost × 5% × (Voyage_Days/365)
                  [+ additional 30 days for China T+30 payment]
Carbon_Cost = Daily_CO2_Tons × Carbon_Price_per_Ton × Voyage_Days
              (Varies by destination: Singapore $37/ton, Japan $20/ton, China $12/ton)
Demurrage = $50k expected cost
LC_Cost = 0.1% of sale value (minimum $25k)
```

**Route-specific voyage days** (from case pack, page 14):
- Singapore: 48 days (47.92)
- Japan: 41 days (41.45)
- China: 52 days (51.79)

##### `calculate_boil_off_loss(destination, cargo_volume) → float`

```python
Boil_off_Rate = 0.05% per day  # Industry standard for modern LNG carriers
Total_Boil_off = Cargo_Volume × Voyage_Days × 0.0005

Singapore (48d): 2.40% loss
Japan (41d):     2.05% loss
China (52d):     2.60% loss
```

##### `calculate_credit_risk_cost(buyer, sale_revenue) → float`

Credit default probability and recovery:

```python
Credit_Risk_Cost = Sale_Revenue × Default_Probability × (1 - Recovery_Rate)

Buyers in analysis (A-rated and above only):
- Iron_Man (A, Singapore):     Default prob 0.5%, Recovery 35%
- Thor (AA, Singapore):        Default prob 0.1%, Recovery 40%
- Hawk_Eye (AA, Japan/China):  Default prob 0.1%, Recovery 40%
- QuickSilver (A, China):      Default prob 0.5%, Recovery 35%
```

##### `calculate_demand_adjustment(destination, month, sale_revenue) → float`

Price adjustment model (NOT binary probability):

```python
# Treat demand as competitive pressure on pricing
Demand_by_Month:
  Jan: 10%, Feb: 25%, Mar: 50%, Apr: 50%, May: 65%, Jun: 65%

Price_Adjustment:
  demand < 20%:  -$2.00/MMBtu  (strong pressure to discount)
  demand < 40%:  -$1.00/MMBtu  (moderate discount)
  demand < 60%:  -$0.25/MMBtu  (slight discount)
  demand >= 60%: $0.00/MMBtu   (market price, no adjustment)

# Smooth adjustment using polynomial interpolation (not step function)
Adjusted_Revenue = Base_Revenue + (Price_Adjustment × Volume)
```

##### `calculate_cargo_pnl(month, destination, buyer, cargo_volume, forecasts) → Dict`

**Main method** that combines all components:

```python
Total_PnL = Sale_Revenue 
          - Purchase_Cost 
          - Freight_Cost 
          - Terminal_Cost 
          - Boil_off_Loss_Value 
          - Credit_Risk_Cost 
          - Demand_Adjustment 
          - Working_Capital_Cost
          + Any_Hedging_PnL

Returns: Dict with all component details for analysis
```

#### **Class: StrategyOptimizer**

Generates optimal routing decisions

**Methods**:

##### `generate_optimal_strategy(forecasts) → Dict`

For each month, test ALL combinations:
- 3 destinations × 2-4 buyers/destination × 3 volumes = ~30-36 options/month
- 6 months × ~36 options = ~216 scenarios tested
- Also tests CANCELLATION option (pay $5.7M penalty, avoid risky sales)

Algorithm:
```python
optimal_strategy = {}

for month in delivery_months:  # Jan-Jun 2026
    best_pnl = -infinity
    best_decision = None
    
    # Test all routing combinations
    for destination in ['Singapore', 'Japan', 'China']:
        for buyer in BUYERS[destination]:
            for volume_pct in [0.90, 1.00, 1.10]:
                pnl = calculator.calculate_cargo_pnl(
                    month, destination, buyer, 
                    volume=3.8M * volume_pct,
                    forecasts
                )
                
                if pnl > best_pnl:
                    best_pnl = pnl
                    best_decision = (destination, buyer, volume_pct)
    
    # Also test cancellation
    cancellation_pnl = -3.8M * $1.50  # Penalty
    if cancellation_pnl > best_pnl:
        best_decision = ('CANCEL',)
    
    optimal_strategy[month] = best_decision

return optimal_strategy
```

##### `generate_all_strategies(forecasts) → Dict[str, Dict]`

Generates 3 different strategies:
1. **Optimal**: Highest expected P&L
2. **Conservative**: Lower volatility, safer buyers
3. **High_JKM**: Maximum exposure to JKM (Japan/China focus)

---

### 4. **models/forecasting.py** (1,142+ lines) - Time Series Forecasting

**Purpose**: Forecast future commodity prices using ARIMA+GARCH

#### **ARIMA Model** (Autoregressive Integrated Moving Average)

Steps:
1. **Stationarity Testing**: ADF and KPSS tests to determine differencing order (d)
2. **Model Selection**: Grid search over p, d, q parameters
3. **Fitting**: ARIMA(p,d,q) fitted to historical data
4. **Forecasting**: Point forecasts + 95% confidence intervals

```python
# Example: Brent oil forecasting
historical_monthly = monthly_brent_prices  # e.g., 38 years of data

# Step 1: Test stationarity
adf_test(historical_monthly)  # Determines d value
kpss_test(historical_monthly)

# Step 2: Fit ARIMA - grid search
best_aic = infinity
for p in range(0, 4):
    for d in range(0, 3):
        for q in range(0, 4):
            model = ARIMA(historical_monthly, order=(p, d, q))
            fit = model.fit()
            if fit.aic < best_aic:
                best_model = fit
                best_aic = fit.aic

# Step 3: Forecast 6 months ahead
forecast = best_model.get_forecast(steps=6)
point_forecast = forecast.predicted_mean  # Expected value
ci = forecast.conf_int(alpha=0.05)  # 95% CI
```

#### **GARCH Model** (Generalized Autoregressive Conditional Heteroskedasticity)

Fits volatility model to ARIMA residuals:

```python
residuals = best_arima_model.resid

garch_model = GARCH(p=1, q=1).fit(residuals)

# Outputs: Time-varying volatility estimates
# Used in Monte Carlo simulation and option pricing
```

#### **Key Forecasting Strategy** (from config.py):

```python
CARGO_FORECASTING_METHOD = {
    'henry_hub': {
        'method': 'forward_curve',
        'reason': 'NYMEX futures are most liquid, best market data'
    },
    'jkm': {
        'method': 'forward_curve',
        'reason': 'Forward contracts available through Dec 2026'
    },
    'brent': {
        'method': 'arima_garch',
        'reason': 'No forward curve; 38+ years historical data available'
    },
    'freight': {
        'method': 'naive',
        'reason': 'Data quality issues; simple average of last 10 months most reliable'
    }
}
```

**Why this mix?**
- Forward curves capture market expectations directly
- ARIMA+GARCH needed when forward unavailable but historical data good
- Naive for poor-quality data (freight has extreme outliers)

---

### 5. **models/option_valuation.py** (806 lines) - Embedded Options

**Purpose**: Value optional cargoes using Black-Scholes framework

**Contract Terms**:
- 6 base cargoes: Mandatory (Jan-Jun 2026)
- Up to 5 ADDITIONAL optional cargoes: Exercisable with >3 month notice (M-3)

#### **Class: EmbeddedOptionAnalyzer**

##### `calculate_intrinsic_value(delivery_month, decision_date) → Dict`

Intrinsic value = Value if exercised TODAY

```python
Intrinsic_Value = Max(Expected_Sale_Price - Strike_Price - Costs, 0)

Strike_Price = HH_Forward(M-2) + $1.50/MMBtu tolling fee

For each destination/buyer combo:
  Sale_Price = Destination-specific formula (Brent or JKM based)
  Costs = Freight + Boil_off + Terminal
  Intrinsic = Max(Sale_Price - Strike - Costs, 0)

Select best destination/buyer with highest intrinsic value
```

##### `calculate_time_value(delivery_month, decision_date, intrinsic) → Dict`

Time value = Value of future optionality (Black-Scholes)

```python
Uses standard Black-Scholes for European call option:

d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
d2 = d1 - σ√T

Call_Value = S×N(d1) - K×e^(-rT)×N(d2)

Where:
  S = Current JKM price
  K = Strike price (HH forward at M-2)
  r = Risk-free rate (5%)
  T = Time to delivery (0.25 years for M-3 to M delivery)
  σ = Volatility from GARCH forecast (e.g., 30-40%)
```

##### `evaluate_exercise_decision(intrinsic, time_value, demand) → bool`

Hierarchical decision framework:

```python
Tier 1: Intrinsic value > threshold ($0.75/MMBtu)
        AND Demand > 50% probability
        → EXERCISE

Tier 2: If intrinsic < $0.75M but time value + intrinsic > threshold
        AND Demand > 30%
        → EXERCISE with lower confidence

Tier 3: Otherwise
        → DO NOT EXERCISE
```

---

### 6. **models/decision_constraints.py** (434 lines) - Deadline Validation

**Purpose**: Enforce realistic trading constraints (information set, deadlines)

#### **Key Principle**: NO PERFECT FORESIGHT
Only use information that would actually be available at decision time

#### **Timelines**:

```
M-3 (3 months before delivery) - OPTION EXERCISE DECISION
  Available data: Historical through M-3, forward curves through M-3
  Decision: Exercise 5 optional cargoes?
  
M-2 (2 months before delivery) - BASE CARGO NOMINATION
  Available data: Historical through M-2, forward curves through M-2
  Decision: Nominate destination for base cargo
  
M-1 (1 month before delivery) - SALES CONFIRMATION
  Available data: Historical through M-1
  Decision: Confirm sales to buyer (some can change last minute)
  
M (Month of delivery) - CARGO LOADING
  Spot prices become known
  Cargo loads and voyage begins
```

#### **Class: InformationSetValidator**

##### `get_available_data_date(cargo_month, decision_type) → Timestamp`

Calculates data cutoff based on decision type:

```python
if decision_type == 'base':       # M-2
    decision_date = cargo_month - 2 months
elif decision_type == 'option':   # M-3
    decision_date = cargo_month - 3 months
elif decision_type == 'sales':    # M-1
    decision_date = cargo_month - 1 month
```

#### **Class: DeadlineValidator**

Validates all decisions meet contract deadlines:
- Base cargoes: M-2 nomination deadline (2 months before delivery)
- Options: M-3 exercise deadline (3 months before delivery)
- Sales: M-1 confirmation deadline (1 month before delivery)

---

### 7. **models/risk_management.py** (300+ lines) - Hedging

**Purpose**: Implement Henry Hub futures hedge for price risk management

#### **Hedge Strategy**:

```
Timeline:
  M-2: Nominate cargo, BUY HH futures at forward price
  M:   Cargo loads, futures settle to spot, we pay actual spot
  
P&L EFFECT:
  Purchase Cost = (HH_Spot_M + $2.50) × Volume
  Hedge P&L = (HH_Spot_M - HH_Forward_M-2) × Volume
  
  Net HH Cost = (HH_Forward_M-2 + $2.50) × Volume
  
  ✓ HH price LOCKED IN at M-2 forward rate
  ✓ Future spot movements fully hedged
  ✓ Reduces total P&L volatility by ~20-30%
```

#### **Class: HenryHubHedge**

##### `calculate_hedge_position(month, hh_forward_m2) → Dict`

Determines number of futures contracts needed:

```python
Contracts_Needed = Cargo_Volume / Contract_Size
                 = 3,800,000 MMBtu / 10,000 MMBtu
                 = 380 contracts

Notional_Value = 380 × 10,000 × HH_Forward_Price
```

##### `calculate_hedge_pnl(hh_forward_m2, hh_spot_m, cargo_volume) → float`

Simple calculation:

```python
Hedge_P&L = (HH_Spot_M - HH_Forward_M-2) × Volume

If HH rises (Spot > Forward):
  Futures gain (positive P&L)
  Offsets higher purchase cost
  
If HH falls (Spot < Forward):
  Futures loss (negative P&L)
  Offsets lower purchase cost
```

---

### 8. **models/sensitivity_analysis.py** (900+ lines) - Robustness Testing

**Purpose**: Test how sensitive strategy is to price forecast errors

#### **Tests Performed**:

##### 1. **Price Sensitivity**
For each commodity, test adjustments: 0.8× to 1.2×
- Q: How much do P&L and strategy change?
- Output: Sensitivity tornado chart

##### 2. **Tornado Analysis**
Ranked sensitivity for each parameter:
- Which factor has biggest P&L impact?
- Order: Brent > JKM > HH > Freight > Operational

##### 3. **Spread Sensitivity**
Test JKM-HH spread (main profitability driver)
- Narrow spread → Lower margin
- Wide spread → Higher margin

##### 4. **Operational Sensitivity**
- Voyage days ±5% impact
- Boil-off rate impact
- Tolling fee sensitivity

##### 5. **Stress Test Scenarios**
Realistic market events:
- **COVID-like**: 50% supply shock + 20% demand collapse
- **Energy crisis**: 150% price spike
- **Recession**: 30% price decline
- **Oil crisis**: Brent ×1.5, HH ×0.8

---

### 9. **config/constants.py** (552 lines) - Business Rules

**Purpose**: Central repository for all business parameters

#### **Key Constants**:

```python
# Contract specifications
CARGO_CONTRACT = {
    'volume_mmbtu': 3_800_000,
    'delivery_period': ['2026-01', ..., '2026-06'],
    'tolling_fee': 1.50,  # $/MMBtu at US terminal
}

# Voyage specifications
VOYAGE_DAYS = {
    'USGC_to_Singapore': 48,
    'USGC_to_Japan': 41,
    'USGC_to_China': 52
}

# Operational parameters
OPERATIONAL = {
    'boil_off_rate_per_day': 0.0005,  # 0.05%
    'storage_cost_per_mmbtu_per_month': 0.05,
}

# Buyers (A-rated and above only)
BUYERS = {
    'Singapore': {
        'Iron_Man': {'premium': 4.00, 'credit_rating': 'A'},
        'Thor': {'premium': 3.50, 'credit_rating': 'AA'}
    },
    'Japan': {
        'Hawk_Eye': {'premium': 0.60, 'credit_rating': 'AA'}
    },
    'China': {
        'QuickSilver': {'premium': 2.20, 'credit_rating': 'A'}
    }
}

# Special cost structures
SPECIAL_PORT_FEE = {...}  # Shanghai Yangshan fee for US vessels
BIOLNG_MANDATE = {...}    # Singapore 5% BioLNG penalty
TERMINAL_COSTS = {...}     # Destination-specific
CARBON_COSTS = {...}       # Regional carbon pricing
```

---

### 10. **config/settings.py** - Configuration Parameters

```python
# Feature toggles
VOLUME_FLEXIBILITY_CONFIG = {
    'enabled': True,
    'tolerance_pct': 0.10,
    'min_volume_mmbtu': 3_420_000,
    'max_volume_mmbtu': 4_180_000
}

HEDGING_CONFIG = {
    'enabled': True,
    'henry_hub_hedge': {
        'enabled': True,
        'contract_size_mmbtu': 10_000,
        'hedge_ratio': 1.0,
        'timing': 'M-2'
    }
}

MONTE_CARLO_CONFIG = {
    'enabled': True,
    'n_simulations': 10_000,
    'confidence_levels': [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
}
```

---

## 🔄 Data Flow

### End-to-End Pipeline

```
1. DATA LOADING
   ├─ 13 Excel files loaded from data_processing/raw/
   ├─ Complex formats parsed (dates extracted from contract names)
   ├─ Daily → Monthly aggregation (freight)
   └─ Output: Dict[commodity] → pd.DataFrame

2. FORECASTING
   ├─ Henry Hub: Extract forward curve from loaded data
   ├─ JKM: Extract forward curve from loaded data
   ├─ Brent: ARIMA(p,d,q) fitted to historical data
   ├─ Freight: Recent average (last 10 months)
   └─ Output: Dict[commodity] → pd.Series [Jan-Jul 2026]

3. OPTIMIZATION
   ├─ For each month (6 months):
   │  ├─ For each destination (3):
   │  │  ├─ For each buyer (2-4):
   │  │  │  ├─ For each volume % (3: 90%, 100%, 110%):
   │  │  │  │  ├─ Calculate purchase cost
   │  │  │  │  ├─ Calculate sale revenue
   │  │  │  │  ├─ Calculate freight cost
   │  │  │  │  ├─ Calculate all other costs
   │  │  │  │  └─ Sum P&L
   │  │  │  └─ Track best option
   │  │  └─ Also test CANCELLATION option
   │  └─ Select best destination/buyer/volume
   └─ Output: Optimal strategy (6 months × best decision)

4. VALIDATION
   ├─ Check decision constraints (M-2, M-3, M-1 deadlines)
   ├─ Verify information set (no future data used)
   └─ Flag any violations

5. RISK ANALYSIS
   ├─ Monte Carlo (10,000 simulations):
   │  ├─ Sample correlated price paths
   │  ├─ Run optimization for each scenario
   │  ├─ Calculate P&L distribution
   │  └─ Compute VaR, CVaR, Sharpe ratio
   │
   ├─ Scenario Analysis:
   │  ├─ Bull market (prices +20-30%)
   │  ├─ Bear market (prices -20-30%)
   │  └─ Stress (realistic shocks)
   │
   └─ Hedging Analysis:
      ├─ Add HH futures hedge to all decisions
      ├─ Reduce HH volatility to ~1% (price locked in)
      └─ Recalculate risk metrics with hedge

6. RESULTS EXPORT
   ├─ strategies_comparison.xlsx - All strategies summary
   ├─ optimal_strategy.csv - Decision table (who, what, where, when)
   ├─ monte_carlo_risk_metrics.xlsx - Risk metrics
   ├─ scenario_analysis.xlsx - Scenario comparison
   ├─ hedging_comparison.xlsx - Hedged vs unhedged
   └─ sensitivity_analysis.xlsx - Price sensitivity tests

Final Output: 4-6 Excel/CSV files with all analysis
```

---

## 🧮 Key Algorithms

### Algorithm 1: Strategy Optimization

```pseudocode
FUNCTION generate_optimal_strategy(forecasts):
    optimal_decisions = {}
    
    FOR each month in [Jan, Feb, Mar, Apr, May, Jun]:
        best_pnl = -∞
        best_decision = None
        
        # Test all routing combinations
        FOR each destination in [Singapore, Japan, China]:
            FOR each buyer in BUYERS[destination]:
                FOR each volume_pct in [0.90, 1.00, 1.10]:
                    
                    # Calculate full P&L with all costs
                    pnl = calculate_cargo_pnl(
                        month, destination, buyer,
                        volume=3.8M * volume_pct,
                        forecasts
                    )
                    
                    IF pnl > best_pnl:
                        best_pnl = pnl
                        best_decision = {
                            destination,
                            buyer,
                            volume_pct,
                            pnl
                        }
        
        # Test cancellation option (pay $1.50/MMBtu penalty)
        cancellation_cost = -3.8M * $1.50
        IF cancellation_cost > best_pnl:
            best_decision = {CANCEL, cancellation_cost}
        
        optimal_decisions[month] = best_decision
    
    RETURN optimal_decisions
END FUNCTION
```

### Algorithm 2: P&L Calculation

```pseudocode
FUNCTION calculate_cargo_pnl(month, destination, buyer, volume, forecasts):
    
    # 1. PURCHASE COST
    hh_price = forecasts['henry_hub'][month]
    purchase_price_per_mmbtu = hh_price + $2.50
    purchase_cost = purchase_price_per_mmbtu * volume
    
    # 2. BOIL-OFF LOSS
    voyage_days = VOYAGE_DAYS[destination]
    boil_off_rate = 0.0005
    boil_off_volume = volume * boil_off_rate * voyage_days
    delivered_volume = volume - boil_off_volume
    
    # 3. SALE REVENUE
    IF destination == 'Singapore':
        brent_price = forecasts['brent'][month]
        base_price = brent_price * 0.13
        buyer_premium = BUYERS['Singapore'][buyer]['premium']
        terminal_tariff = 0.75  # Includes BioLNG penalty
        sale_price = base_price + buyer_premium + terminal_tariff
    ELSE:  # Japan or China
        jkm_price = forecasts['jkm'][month]
        buyer_premium = BUYERS[destination][buyer]['premium']
        berthing_cost = 0.10
        sale_price = jkm_price + buyer_premium + berthing_cost
    
    # Sales capped at contract maximum (3.7M ±10%)
    max_sales_volume = min(delivered_volume, 4.07M)
    stranded_volume = delivered_volume - max_sales_volume
    
    sale_revenue = sale_price * max_sales_volume
    
    # 4. FREIGHT COST (7 components)
    freight_rate = forecasts['freight'][month]
    base_freight = freight_rate * voyage_days
    insurance = $150k
    brokerage = 0.015 * base_freight
    wc_cost = purchase_cost * 0.05 * (voyage_days / 365)
    carbon_cost = carbon_rate[destination] * voyage_days
    demurrage = $50k
    lc_cost = max(0.001 * sale_revenue, $25k)
    total_freight = base_freight + insurance + brokerage + wc_cost + carbon_cost + demurrage + lc_cost
    
    # 5. TERMINAL COSTS
    terminal_cost = TERMINAL_COSTS[destination] * delivered_volume
    
    # 6. CREDIT RISK COST
    buyer_credit_rating = BUYERS[destination][buyer]['credit_rating']
    default_prob = CREDIT_DEFAULT_PROBABILITY[buyer_credit_rating]
    recovery_rate = CREDIT_RECOVERY_RATE[buyer_credit_rating]
    credit_risk = sale_revenue * default_prob * (1 - recovery_rate)
    
    # 7. DEMAND ADJUSTMENT
    demand_level = DEMAND_PROFILE[destination][month]
    price_adjustment = DEMAND_PRICING_MODEL['adjustments'][demand_level_bucket]
    demand_cost = price_adjustment * max_sales_volume
    
    # 8. COMBINE ALL
    total_pnl = sale_revenue
              - purchase_cost
              - total_freight
              - terminal_cost
              - credit_risk
              - demand_cost
    
    RETURN {
        pnl: total_pnl,
        components: {purchase, sale, freight, ...}
    }
END FUNCTION
```

### Algorithm 3: Monte Carlo Risk Analysis

```pseudocode
FUNCTION run_monte_carlo(strategy, forecasts, volatilities, correlations, n_sim=10000):
    
    pnl_distribution = []
    
    FOR i = 1 TO n_sim:
        # 1. Generate correlated random returns
        Z = multivariate_normal(mean=0, cov=correlations, size=4)  # 4 commodities
        
        # 2. Convert to price paths (Geometric Brownian Motion)
        price_paths = {}
        FOR each commodity in [HH, JKM, Brent, Freight]:
            annual_return = Z[commodity] * volatilities[commodity]
            simulated_price = forecast_price * exp(annual_return)
            price_paths[commodity] = simulated_price
        
        # 3. Calculate P&L under simulated prices
        pnl_sim = calculate_cargo_pnl(
            strategy_decisions,
            price_paths,
            forecasts
        )
        
        pnl_distribution.append(pnl_sim)
    
    # 4. Calculate risk metrics
    metrics = {
        mean: mean(pnl_distribution),
        std: std(pnl_distribution),
        var_5pct: percentile(pnl_distribution, 5),
        cvar_5pct: mean(pnl_distribution[pnl_distribution <= var_5pct]),
        sharpe_ratio: (mean - risk_free_rate) / std,
        prob_profit: count(pnl_distribution > 0) / n_sim
    }
    
    RETURN metrics
END FUNCTION
```

---

## 💼 Business Logic

### P&L Waterfall Example (Mar 2026)

**Decision**: Singapore → Iron_Man → 4.17M MMBtu

| Component | Calculation | Amount |
|-----------|---|---|
| **REVENUE** | | |
| Sale Price (Brent-linked) | $75 × 0.13 + $4.00 + $0.75 | $14.50/MMBtu |
| Boil-off (48 days × 0.05%) | 4.17M × 2.4% lost | -100k MMBtu |
| Delivered Volume | 4.17M - 0.10M | 4.07M MMBtu |
| Gross Sale Revenue | 4.07M × $14.50 | **$59.0M** |
| **COSTS** | | |
| Purchase Cost | (HH + $2.50) × 4.17M | -$52.0M |
| Freight | $55k/day × 48 days + other | -$2.8M |
| Terminal | $0.50 × 4.07M | -$2.0M |
| Credit Risk | $59.0M × 0.5% × 65% (A-rated) | -$0.2M |
| Demand Adjustment | No discount (50% demand) | $0 |
| **NET P&L** | | **$1.9M** |

**Note**: Actual calculated P&L is higher (detailed calc with all sub-components)

---

## 🚀 How to Run

### Quick Start
```bash
cd "C:\Users\nicko\Desktop\LNG Case Comp\portfolio"
python main_optimization.py
```

**Output**:
- 4-6 Excel files in `outputs/results/`
- Logging to `optimization.log`
- Console output with execution trace

### Custom Execution
```python
from main_optimization import main

# Run full pipeline
results = main(
    run_monte_carlo=True,
    run_scenarios=True,
    use_arima_garch=True,
    run_hedging=True,
    run_sensitivity=True
)

# Access results
strategies = results['strategies']
mc = results['monte_carlo_results']
output_files = results['output_files']

# Print summary
for strategy_name, strategy in strategies.items():
    print(f"{strategy_name}: ${strategy['total_pnl']/1e6:.1f}M")
```

---

## 📁 File Organization

```
portfolio/
│
├── main_optimization.py              # Main orchestrator [1,385 lines]
├── main.py                           # Simple wrapper
│
├── config/
│   ├── __init__.py
│   ├── constants.py                  # Business rules [552 lines]
│   ├── settings.py                   # Configuration parameters
│   └── paths.py                      # File paths
│
├── data_processing/
│   ├── __init__.py
│   ├── loaders.py                    # Data loading from Excel [557 lines]
│   └── processors.py                 # Data validation
│
├── models/
│   ├── __init__.py
│   ├── optimization.py               # Core P&L and optimization [1,497 lines]
│   ├── forecasting.py                # ARIMA+GARCH models [1,142+ lines]
│   ├── option_valuation.py           # Embedded options analysis [806 lines]
│   ├── decision_constraints.py       # Deadline validation [434 lines]
│   ├── risk_management.py            # Hedging strategies [300+ lines]
│   └── sensitivity_analysis.py       # Robustness testing [900+ lines]
│
├── data_processing/raw/              # 13 Excel input files
│   ├── Henry Hub Historical (Extracted 23Sep25).xlsx
│   ├── Henry Hub Forward (Extracted 23Sep25).xlsx
│   ├── JKM Spot LNG Historical (Extracted 23Sep25).xlsx
│   ├── JKM Spot LNG Forward (Extracted 23Sep25).xlsx
│   ├── Brent Oil Historical Prices (Extracted 01Oct25).xlsx
│   ├── WTI Historical (Extracted 23Sep25).xlsx
│   ├── WTI Forward (Extracted 23Sep25).xlsx
│   ├── Baltic LNG Freight Curves Historical.xlsx
│   ├── USDSGD FX Spot Rate Historical (Extracted 23Sep25).xlsx
│   ├── TTF Historical (Extracted 23Sep25).xlsx
│   ├── TTF Forward (Extracted 23Sep25).xlsx
│   └── Singapore Related Data.xlsx
│
├── outputs/
│   ├── results/
│   │   ├── strategies_comparison_*.xlsx
│   │   ├── optimal_strategy_*.csv
│   │   ├── monte_carlo_risk_metrics_*.xlsx
│   │   ├── scenario_analysis_*.xlsx
│   │   └── hedging_comparison_*.xlsx
│   │
│   ├── diagnostics/
│   │   ├── sensitivity/
│   │   │   ├── price_sensitivities.png
│   │   │   ├── spread_sensitivity.png
│   │   │   └── tornado_diagram.png
│   │   │
│   │   └── arima_garch/
│   │       ├── brent_forecast.png
│   │       └── freight_forecast.png
│   │
│   └── figures/
│
├── docs/
│   ├── README.md                     # System overview
│   ├── QUICK_START.md               # Quick reference
│   ├── MODEL_COMPREHENSIVE_OVERVIEW.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── SYSTEM_CAPABILITIES_REPORT.md
│   │
│   └── implementation_notes/
│       ├── CRITICAL_GAPS_ANALYSIS.md
│       ├── DEMAND_MODELING_ISSUE.md
│       ├── FINAL_MODEL_VALIDATION.md
│       ├── TEST_RESULTS.md
│       └── VALIDATION_DEEP_DIVE.md
│
├── tests/
│   ├── __init__.py
│   ├── test_models/
│   ├── test_analysis/
│   └── test_data/
│
├── requirements.txt                  # Python dependencies
├── optimization.log                  # Execution log
│
└── Documentation files (*.md)
    ├── CODEBASE_SUMMARY_FOR_EXTERNAL_AGENT.md
    ├── MODEL_TECHNICAL_SPECIFICATION.md
    ├── ASSUMPTIONS.md
    ├── CARBON_COST_VERIFICATION.md
    └── ... (20+ documentation files)
```

---

## 📈 Performance Metrics

- **Runtime**: ~2 seconds end-to-end
- **Monte Carlo**: 10,000 simulations in ~1 second
- **Optimization**: 216 scenarios tested in <100ms
- **Code Quality**: 0 linting errors
- **Total Lines of Code**: ~7,500+ (models + orchestration)
- **Documentation**: 2,000+ lines of inline comments + 20+ markdown docs

---

## ✅ Verification Checklist

- ✅ All 13 Excel files load correctly
- ✅ ARIMA+GARCH models fit successfully
- ✅ Optimization converges in reasonable time
- ✅ Monte Carlo produces stable distributions
- ✅ All output files generate correctly
- ✅ No floating-point or data errors
- ✅ All constraints validated
- ✅ Reproducible results (fixed random seed)

---

**Complete codebase understood and ready for enhancement!**
