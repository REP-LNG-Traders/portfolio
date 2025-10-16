# LNG Portfolio Optimization - Data Dictionary

**Purpose:** Comprehensive description of all datasets used in the model  
**Date:** October 17, 2025  
**Location:** `data_processing/raw/`

---

## 📊 Dataset Overview

**Total Files:** 13 Excel files  
**Data Categories:** 5 (Natural Gas, LNG Spot, Oil, Freight, FX)  
**Date Range:** 1987-2025 (varies by dataset)  
**Source:** Competition case materials

---

## 🔥 Natural Gas Datasets (Henry Hub)

### **1. Henry Hub Historical (Extracted 23Sep25).xlsx**

**Purpose:** US natural gas spot prices (purchase cost basis)

**Content:**
- **Rows:** 753 daily observations
- **Date Range:** September 23, 2022 - September 23, 2025
- **Columns:**
  - `Exchange Date`: Trading date
  - `Close`: Settlement price ($/MMBtu)
  - Additional: Open, High, Low, Volume, etc.

**Usage in Model:**
- Purchase cost calculation: `(HH_price + $2.50 tolling) × Volume`
- Historical volatility calibration for Monte Carlo
- Correlation analysis with other commodities

**Key Statistics:**
- Price range: $1.50 - $9.50/MMBtu (typical)
- Volatility: ~61% annualized
- Correlation with JKM: 0.546

---

### **2. Henry Hub Forward (Extracted 23Sep25).xlsx**

**Purpose:** NYMEX Natural Gas futures forward curve

**Content:**
- **Rows:** 15 monthly contracts
- **Date Range:** November 2025 - January 2027
- **Columns:**
  - `Name`: Contract name (e.g., "NAT GAS JAN26/d")
  - `Close`: Forward price ($/MMBtu)

**Contract Parsing:**
```
"NAT GAS JAN26/d" → January 2026 contract
"NAT GAS FEB26/d" → February 2026 contract
```

**Usage in Model:**
- Primary forecasting for Jan-Jun 2026 cargo pricing
- Hedging reference prices (M-2 forward curve)
- Most reliable forecast (market-based, liquid)

**Key Statistics:**
- Forward curve: $3.47 - $4.17/MMBtu (2026)
- Contango/backwardation indicator
- Used for 100% of HH forecasts (no ARIMA needed)

---

## 🌏 LNG Spot Price Datasets (JKM)

### **3. JKM Spot LNG Historical (Extracted 23Sep25).xlsx**

**Purpose:** Japan-Korea Marker LNG spot prices (Asia benchmark)

**Content:**
- **Rows:** 753 daily observations
- **Date Range:** September 23, 2022 - September 23, 2025
- **Columns:**
  - `Exchange Date` or `Date`: Trading date
  - `Close`: JKM spot price ($/MMBtu)

**Usage in Model:**
- Sale price for Japan/China cargoes (JKM-linked formula)
- Historical volatility: ~54% annualized
- Correlation with Brent: 0.108

**Key Statistics:**
- Price range: $8 - $35/MMBtu (varies with season)
- Highly seasonal (winter peaks)
- Asian LNG benchmark (most liquid)

---

### **4. JKM Spot LNG Forward (Extracted 23Sep25).xlsx**

**Purpose:** JKM forward contracts (futures/swaps)

**Content:**
- **Rows:** 14 monthly contracts
- **Date Range:** November 2025 - December 2026
- **Columns:**
  - `Name`: Contract name (e.g., "LNG JnK NOV5/d", "LNG JKM JAN6/d")
  - `Close`: Forward price ($/MMBtu)

**Contract Parsing:**
```
"LNG JnK NOV5/d" → November 2025 (5 = 2025)
"LNG JKM JAN6/d" → January 2026 (6 = 2026)
```

**Usage in Model:**
- Sale price forecasting for Japan/China markets
- M+1 pricing (next month forward price)
- Forward curve: $10.84 - $11.64/MMBtu (2026)

---

## 🛢️ Oil Datasets (Brent)

### **5. Brent Oil Historical Prices (Extracted 01Oct25).xlsx**

**Purpose:** Brent crude oil prices (Singapore pricing basis)

**Content:**
- **Rows:** 461 monthly observations
- **Date Range:** May 1987 - September 2025 (38+ years!)
- **Columns:**
  - Date column (multiple possible names)
  - `Brent` or `Price`: Oil price ($/barrel)

**Usage in Model:**
- Singapore sale price: `(Brent × 0.13) + Premium + Terminal Tariff`
- Long historical data for ARIMA+GARCH modeling
- Volatility: ~20% annualized

**Key Statistics:**
- Historical range: $10 - $140/barrel
- Recent (2025): ~$68/barrel
- Low correlation with gas (-0.060 with HH)

**Forecasting:**
- Uses ARIMA(1,1,1) + GARCH(1,1) due to no forward curve
- 7-month forecast generated (Jan-Jul 2026)

---

## 🚢 Freight Datasets

### **6. Baltic LNG Freight Curves Historical.xlsx**

**Purpose:** LNG vessel charter rates (shipping costs)

**Content:**
- **Rows:** 463 daily observations → 55 monthly averages
- **Date Range:** March 2021 - September 2025
- **Column:** `.BLNG3g (TRDPRC_1)` - Baltic LNG 3G route
- **Units:** $/day for vessel charter

**Data Quality Issues:**
- Original had extreme outliers (negative prices, $400k/day)
- **Applied capping:** $5k/day (min) to $120k/day (max)
- **Rationale:** Baltic data quality issues, use industry bounds

**Usage in Model:**
- Freight cost: `Rate × Voyage_Days × Scaling_Factor`
- Current forecast: ~$52,834/day (recent 30-day average)
- Volatility: 268% (high due to data quality, acknowledged limitation)

**Route Scaling:**
- Singapore: 1.0 (baseline)
- Japan: 1.0 (baseline)
- China: 1.0 (baseline)

**Components Included in Freight:**
1. Base freight (Baltic rate × days)
2. Insurance ($150k per voyage)
3. Brokerage (1.5% of freight)
4. Working capital (5% annual on purchase cost × days)
5. Carbon costs ($5k/day)
6. Demurrage ($50k expected)
7. LC fees ($25k)

---

## 💱 FX Dataset

### **7. USDSGD FX Spot Rate Historical (Extracted 23Sep25).xlsx**

**Purpose:** USD/SGD exchange rate

**Content:**
- **Rows:** 782 daily observations
- **Date Range:** September 23, 2022 - September 22, 2025
- **Columns:**
  - Date
  - `USDSGD`: Exchange rate

**Usage in Model:**
- **LOADED BUT NOT USED**
- Assumption: All prices in USD (industry standard)
- Singapore pricing assumed USD-denominated
- FX risk not modeled (documented simplification)

**Key Statistics:**
- Range: 1.25 - 1.40 SGD/USD
- Relatively stable over period

---

## 📈 Singapore-Specific Datasets

### **8. Singapore Related Data.xlsx**

**Purpose:** Singapore market-specific information

**Sheets:**
1. **Singapore LNG Information**
   - SLNG terminal tariffs by fiscal year
   - Reservation charges, utilization rates
   - Peak/Shoulder/Offpeak pricing structure
   - Terminal tariff: $150k-200k per day

2. **LNG Regas Capacity Information**
   - Regasification terminal capacities
   - Not used in current model

3. **Singapore PNG Cost**
   - Piped natural gas costs (reference)

4. **Singapore Bunkering Price Data**
   - Bunker fuel pricing
   - Relevant for bunker buyers (Iron_Man type)

5. **Singapore Carbon Price**
   - Carbon credit pricing
   - Used for carbon cost estimation

6. **Brent Oil Price**
   - Duplicate of Brent dataset
   - Cross-reference for Singapore pricing formula

**Usage in Model:**
- Terminal tariff estimation for Singapore sales
- Carbon cost inputs
- Market structure understanding

**NOTE:** Contains voyage time data:
- USGC → Singapore: 47.92 days (used in model as 48 days)
- USGC → Japan: 41.45 days (used as 41 days)
- USGC → China: 51.79 days (used as 52 days)

---

## 🔋 TTF Datasets (European Gas - Not Used)

### **9-10. TTF Historical & Forward (Extracted 23Sep25).xlsx**

**Purpose:** Dutch TTF (Title Transfer Facility) natural gas prices

**Content:**
- TTF Historical: European gas spot prices
- TTF Forward: European gas forward curve

**Usage in Model:**
- **LOADED BUT NOT USED**
- TTF is European benchmark (not relevant for USGC→Asia routes)
- Kept for potential future European market analysis

---

## 🛢️ WTI Datasets (US Oil - Not Used)

### **11-12. WTI Historical & Forward (Extracted 23Sep25).xlsx**

**Purpose:** West Texas Intermediate crude oil prices

**Content:**
- WTI Historical: US oil spot prices
- **WTI Forward: MISLEADING NAME - Contains historical 2005-2006 data, NOT forward curve**

**⚠️ CRITICAL NOTE:**
- **WTI "Forward" file is NOT usable for forecasting**
- File contains data from Nov 2005 - Feb 2006 (historical, not forward-looking)
- Cannot be used as Brent proxy for 2026 forecasting

**Usage in Model:**
- **NOT USED** 
- Original intent was to use as Brent proxy, but file contains wrong data
- Model uses ARIMA-GARCH for Brent instead

---

## 📋 Complete Dataset Summary Table

| # | Dataset | Type | Observations | Date Range | Used In Model | Purpose |
|---|---------|------|--------------|------------|---------------|---------|
| 1 | Henry Hub Historical | Spot | 753 daily | 2022-09 to 2025-09 | ✅ YES | Purchase cost, volatility |
| 2 | Henry Hub Forward | Futures | 15 monthly | 2025-11 to 2027-01 | ✅ YES | Purchase forecasts, hedging |
| 3 | JKM Historical | Spot | 753 daily | 2022-09 to 2025-09 | ✅ YES | Sale price, volatility |
| 4 | JKM Forward | Futures | 14 monthly | 2025-11 to 2026-12 | ✅ YES | Sale forecasts (Japan/China) |
| 5 | Brent Historical | Spot | 461 monthly | 1987-05 to 2025-09 | ✅ YES | Sale price (Singapore) |
| 6 | Baltic Freight | Spot | 55 monthly | 2021-03 to 2025-09 | ✅ YES | Shipping costs |
| 7 | USDSGD FX | Spot | 782 daily | 2022-09 to 2025-09 | ❌ NO | FX risk (not modeled) |
| 8 | Singapore Data | Reference | Multiple sheets | 2022-2025 | ✅ PARTIAL | Terminal costs, voyage times |
| 9 | TTF Historical | Spot | ~750+ daily | 2022-09 to 2025-09 | ❌ NO | European gas (not relevant) |
| 10 | TTF Forward | Futures | ~15 monthly | 2025-11+ | ❌ NO | European gas (not relevant) |
| 11 | WTI Historical | Spot | ~750+ daily | 2022-09 to 2025-09 | ❌ NO | US oil (use Brent instead) |
| 12 | WTI Forward | **HISTORICAL** | 124 monthly | **2005-11 to 2006-02** | ❌ NO | **Mislabeled - contains 2005-06 data** |

---

## 🔍 Data Processing Pipeline

### **Step 1: Loading** (`data_processing/loaders.py`)

**For each dataset:**
1. Read Excel file with custom header detection
2. Parse contract names (e.g., "NAT GAS JAN26/d" → 2026-01-01)
3. Handle multiple date formats
4. Clean and validate data

**Special Processing:**
- **Freight:** Monthly aggregation + outlier capping (80% method)
- **Brent:** Long historical series for ARIMA+GARCH
- **Forward curves:** Contract name parsing to extract delivery months

### **Step 2: Forecasting** (`models/forecasting.py`)

**Method by commodity:**
1. **Henry Hub:** Forward curve (market-based, most reliable)
2. **JKM:** Forward curve (market-based)
3. **Brent:** ARIMA(p,d,q) + GARCH(1,1) (no forward curve; WTI Forward unusable)
4. **Freight:** Naive forecast (recent average, due to data quality)

### **Step 3: Risk Analysis** (`main_optimization.py`)

**Volatility Calculation (from monthly returns):**
- Henry Hub: 60.8% annualized
- JKM: 54.2% annualized
- Brent: 20.4% annualized
- Freight: 153.9% annualized (high due to data issues)

**Correlation Matrix (36 overlapping monthly observations):**
```
              HH      JKM    Brent  Freight
Henry Hub   1.000   0.546  -0.060    0.069
JKM         0.546   1.000   0.108    0.231
Brent      -0.060   0.108   1.000   -0.016
Freight     0.069   0.231  -0.016    1.000
```

---

## 📈 How Data Flows Through Model

### **Purchase Cost (Henry Hub):**
```
Henry Hub Historical → Volatility calculation
Henry Hub Forward → Price forecasts (Jan-Jul 2026)
↓
Purchase Cost = (HH_Forward + $2.50 tolling) × Purchase_Volume
```

### **Sale Revenue (JKM or Brent):**

**For Japan/China (JKM-linked):**
```
JKM Historical → Volatility
JKM Forward → M+1 pricing (next month)
↓
Sale Price = JKM(M+1) + Premium + Berthing_Fee + Demand_Adjustment
```

**For Singapore (Brent-linked):**
```
Brent Historical → ARIMA+GARCH forecast
↓
Sale Price = (Brent × 0.13) + Premium + Terminal_Tariff + Demand_Adjustment
```

### **Freight Cost (Baltic LNG):**
```
Baltic Historical → Monthly average with outlier capping
↓
Freight Cost = Rate × Voyage_Days + Insurance + Brokerage + WC + Carbon + LC
```

### **Risk Analysis (All Datasets):**
```
All Historical → Monthly returns → Correlation matrix
All Volatilities → Monte Carlo simulation (10,000 paths)
↓
Risk Metrics: VaR, CVaR, Sharpe Ratio, Prob(Profit)
```

---

## 🎯 Key Data Insights

### **What the Data Tells Us:**

**1. Henry Hub - JKM Spread is Profitable:**
- HH Forward (2026): $3.47 - $4.17/MMBtu
- JKM Forward (2026): $10.84 - $11.64/MMBtu
- **Gross spread:** ~$7/MMBtu (before tolling $1.50 = $5.50 net)
- **Profit driver:** Gas arbitrage (US cheap, Asia expensive)

**2. Singapore vs Japan Pricing:**
- Singapore: Brent-linked ($68 × 0.13 = $8.84/MMBtu base)
- Japan: JKM-linked ($11.64/MMBtu base)
- **Japan premium:** ~$2.80/MMBtu
- **BUT:** Singapore buyers offer higher premiums (Iron_Man $4.00 vs Hawk_Eye $0.60)

**3. Freight Economics:**
- Cost: ~$52,834/day × 48 days = $2.5M per Singapore voyage
- Impact: ~6-7% of cargo value
- **Volatility concern:** 268% (data limitation, acknowledged)

**4. Seasonality Patterns:**
- JKM: Winter peaks (demand driven)
- HH: Summer peaks (cooling demand)
- **Opportunity:** Counter-seasonal spread widens in winter

**5. Credit Risk Distribution:**
- AA buyers (Iron_Man, Thor): 0.1% default probability
- BBB buyers (QuickSilver): 2.0% default probability
- **Impact:** $268k expected loss difference per $20M cargo

---

## 🔧 Data Quality & Handling

### **High Quality (Reliable):**
✅ Henry Hub: NYMEX official data, highly liquid  
✅ JKM: Platts benchmark, industry standard  
✅ Brent: ICE official data, 38 years of history  

### **Medium Quality (Usable with Caveats):**
⚠️ Freight (Baltic LNG):
- Issue: Extreme outliers (negative prices, $400k/day spikes)
- Fix: 80% percentile capping ($5k-$120k/day)
- Result: 268% volatility (vs industry 40-60%)
- Status: Documented limitation, acceptable for competition

### **Not Used:**
❌ FX (USDSGD): All prices assumed USD  
❌ TTF: European market not relevant  
❌ WTI: Use Brent for international benchmark  

---

## 📊 Critical Data Validations

### **Validation 1: Date Alignment**
```
Henry Hub: 2022-09-23 to 2025-09-23 ✓
JKM:       2022-09-23 to 2025-09-23 ✓
Brent:     1987-05-15 to 2025-09-15 ✓ (extends earlier)
Freight:   2021-03-05 to 2025-09-26 ✓ (shorter period)

Overlapping monthly data: 36 months ✓ (sufficient for correlation)
```

### **Validation 2: Forward Curve Coverage**
```
HH Forward: Nov 2025 - Jan 2027 ✓ (covers all cargo months)
JKM Forward: Nov 2025 - Dec 2026 ✓ (covers M+1 needs)
Brent Forward: None (use ARIMA+GARCH) ✓
```

### **Validation 3: Data Completeness**
```
Missing data: < 1% in all primary series ✓
Forward fill limit: 7 days
Outlier handling: Applied to freight only
Price reasonability: All positive, within industry norms ✓
```

---

## 🎓 Dataset Usage Summary

### **Primary Datasets (Drive All Decisions):**
1. **Henry Hub Forward** → Purchase cost forecasts
2. **JKM Forward** → Japan/China sale price forecasts  
3. **Brent Historical** → Singapore sale price (via ARIMA+GARCH)
4. **Baltic Freight** → Shipping cost forecasts

### **Supporting Datasets (Risk & Validation):**
5. **Historical series** → Volatility calibration
6. **All series** → Correlation matrix (Monte Carlo)
7. **Singapore Data** → Terminal costs, voyage times

### **Reference Only:**
8. **TTF, WTI, FX** → Loaded but not actively used

---

## 📁 File Locations & Naming

**Directory:** `data_processing/raw/`

**Naming Convention:** `[Commodity] [Type] [Extract Date].xlsx`
- Example: `Henry Hub Historical (Extracted 23Sep25).xlsx`
- Extract dates vary: 23Sep25, 01Oct25 (within 1 week)

**File Sizes:**
- Historical files: 50-500 KB (daily data)
- Forward files: 10-30 KB (monthly contracts)
- Singapore data: ~100 KB (multiple sheets)

---

## 🎯 Key Takeaways

### **Data Strengths:**
✅ **Long history:** 38 years Brent, 3+ years gas/LNG  
✅ **Forward curves:** Market-based forecasts for HH & JKM  
✅ **High frequency:** Daily data aggregated to monthly for stability  
✅ **Multiple sources:** Independent validation of relationships  

### **Data Limitations:**
⚠️ **Freight volatility:** 268% (vs industry 40-60%) - data quality issue  
⚠️ **Limited overlap:** 36 monthly observations for correlation (acceptable)  
⚠️ **No Brent forward:** Must use ARIMA+GARCH instead of market curve  

### **Modeling Decisions Driven by Data:**
- Use forward curves where available (HH, JKM) - most reliable
- Use ARIMA+GARCH for Brent (no forward curve)
- Use naive forecast for freight (data quality issues)
- Monthly frequency (matches cargo decision frequency, smooths daily noise)
- Correlation from aligned monthly returns (handles different data periods)

---

**All datasets documented and validated. Model uses best available data with appropriate handling of quality issues.** ✅


