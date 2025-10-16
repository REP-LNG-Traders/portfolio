# LNG Cargo Trading Optimization System

Portfolio optimization of LNG Trading using ARIMA, GARCH, and cargo routing optimization with Monte Carlo risk analysis.

---

## 🚀 Quick Start

```bash
# Run complete optimization pipeline
python main_optimization.py
```

**Runtime:** ~2 seconds  
**Outputs:** 4 Excel/CSV files in `outputs/results/`

---

## 📊 Current Results

### Optimal Strategy - $80.84M (6 months)

| Month | Destination | Buyer | P&L |
|-------|-------------|-------|-----|
| Jan 2026 | China | QuickSilver | $2.67M |
| Feb 2026 | Singapore | Iron_Man | $7.10M |
| Mar 2026 | Singapore | Iron_Man | $15.27M |
| Apr 2026 | Japan | Hawk_Eye | $15.87M |
| May 2026 | Singapore | Iron_Man | $20.23M |
| Jun 2026 | Singapore | Iron_Man | $19.70M |

### Risk Metrics (Monte Carlo - 10,000 simulations)
- **Mean P&L:** $79.40M
- **VaR (5%):** $2.13M
- **Probability of Profit:** 95.7%
- **Sharpe Ratio:** 1.04

---

## 📁 Project Structure

```
portfolio/
├── main_optimization.py          # Main execution script
├── config.py                      # Configuration parameters
├── requirements.txt               # Python dependencies
│
├── Data/                          # Competition Excel files
│   └── raw/                       # HH, JKM, Brent, Freight, FX data
│
├── src/
│   ├── data_loader.py            # Excel data loading
│   ├── cargo_optimization.py     # P&L, strategies, MC, scenarios
│   ├── forecasting.py            # ARIMA/GARCH models
│   └── data_processing.py        # Data utilities
│
├── outputs/
│   └── results/                  # Excel/CSV outputs
│
├── tests/
│   └── test_cargo_optimization.py
│
├── Models/                        # ARIMA/GARCH models
├── Analysis/                      # Time series analysis
│
└── Documentation/
    ├── IMPLEMENTATION_SUMMARY.md  # Technical report
    ├── QUICK_START.md            # Quick reference
    └── SYSTEM_CAPABILITIES_REPORT.md
```

---

## 🎯 System Features

### ✅ Implemented
- **Data Loading:** Automated Excel parsing with complex format handling
- **P&L Calculator:** Purchase, sale, freight, boil-off, demand, credit risk
- **Strategy Optimizer:** Optimal, Conservative, High_JKM strategies
- **Monte Carlo:** 10,000 correlated price path simulations
- **Scenario Analysis:** Bull/Bear/Stress testing
- **Professional Outputs:** Excel/CSV reports

### 📊 Output Files
1. `strategies_comparison_TIMESTAMP.xlsx` - Strategy comparison
2. `optimal_strategy_TIMESTAMP.csv` - Decision table
3. `monte_carlo_risk_metrics_TIMESTAMP.xlsx` - Risk metrics
4. `scenario_analysis_TIMESTAMP.xlsx` - Scenario results

---

## ⚙️ Configuration

Edit `config.py` before running:

```python
# Key parameters
CARGO_CONTRACT = {
    'volume_mmbtu': 3_400_000,
    'tolling_fee': 0.50,
    'delivery_period': ['2026-01', '2026-02', ..., '2026-06']
}

VOYAGE_DAYS = {
    'USGC_to_Singapore': 30,
    'USGC_to_Japan': 35,
    'USGC_to_China': 32
}

BUYERS = {
    'Singapore': {...},  # 4 buyers
    'Japan': {...},      # 2 buyers
    'China': {...}       # 2 buyers
}

MONTE_CARLO_CARGO_CONFIG = {
    'n_simulations': 10000,
    'random_seed': 42
}
```

---

## 🔧 Usage

### Option 1: Full Analysis (Default)
```bash
python main_optimization.py
```
Runs optimization + Monte Carlo + Scenario analysis

### Option 2: Custom Execution
```python
from main_optimization import main

# Skip Monte Carlo for faster execution
results = main(run_monte_carlo=False, run_scenarios=True)

# Access results
strategies = results['strategies']
output_files = results['output_files']
```

### Option 3: Test P&L Calculator
```bash
python tests/test_cargo_optimization.py
```

---

## 📈 Strategy Comparison

| Strategy | Total P&L | Risk (σ) | VaR (5%) | Sharpe |
|----------|-----------|----------|----------|--------|
| **Optimal** | $80.84M | $76.43M | $2.13M | 1.04 |
| Conservative | $74.95M | $90.19M | -$14.49M | 0.79 |
| High_JKM | $66.37M | $39.03M | $12.12M | **1.80** ⭐ |

**Key Insight:** High_JKM strategy has best risk-adjusted returns (Sharpe: 1.80)

---

## 📋 System Components

### 1. Data Loader (`src/data_loader.py`)
- Loads Henry Hub, JKM, Brent, Freight, FX data
- Handles complex Excel formats
- Parses JKM contract names (e.g., "LNG JnK NOV5/d")
- Combines historical + forward curves

### 2. P&L Calculator (`src/cargo_optimization.py`)
- **Purchase Cost:** Henry Hub + $2.50/MMBtu
- **Sale Revenue:** Brent-linked (Singapore) or JKM M+1 (Japan/China)
- **Freight Cost:** Baltic LNG $/day × voyage days
- **Boil-off:** 0.15%/day opportunity cost
- **Demand Adjustment:** Seasonal probability weighting
- **Credit Risk:** Default probability + recovery rate

### 3. Strategy Optimizer (`src/cargo_optimization.py`)
- Evaluates 10 options per month (8 buyers + cancel)
- Generates 3 strategies: Optimal, Conservative, High_JKM
- Returns monthly routing decisions + P&L

### 4. Monte Carlo Analyzer (`src/cargo_optimization.py`)
- 10,000 correlated price paths (Cholesky + GBM)
- Calculates VaR, CVaR, Sharpe ratio
- Probability distributions for all strategies

### 5. Scenario Analyzer (`src/cargo_optimization.py`)
- Tests strategies under 4 scenarios
- Stress testing for robustness
- Scenario P&L comparison

---

## 📊 Input Data

Place Excel files in `Data/raw/`:
- `Henry Hub Historical (Extracted 23Sep25).xlsx`
- `Henry Hub Forward (Extracted 23Sep25).xlsx`
- `JKM Spot LNG Historical (Extracted 23Sep25).xlsx`
- `JKM Spot LNG Forward (Extracted 23Sep25).xlsx`
- `Brent Oil Historical Prices (Extracted 01Oct25).xlsx`
- `Baltic LNG Freight Curves Historical.xlsx`
- `USDSGD FX Spot Rate Historical (Extracted 23Sep25).xlsx`

---

## 🧪 Testing

```bash
# Run P&L calculator tests
python tests/test_cargo_optimization.py

# Test data loading
python src/data_loader.py

# Full system test
python main_optimization.py
```

---

## 🛠️ Troubleshooting

### "File not found" error
- Check Excel files are in `Data/raw/`
- Verify filenames match exactly

### Freight volatility warning
- Expected due to Baltic LNG data volatility (3,230%)
- Does not affect optimization quality

### Excel export fails
- Close output files if currently open
- Check write permissions in `outputs/results/`

---

## 📚 Documentation

- **`IMPLEMENTATION_SUMMARY.md`** - Complete technical report
- **`QUICK_START.md`** - Quick reference guide
- **`SYSTEM_CAPABILITIES_REPORT.md`** - System capabilities
- **`PHASE3_SPECIFICATIONS.md`** - ARIMA/GARCH specifications

---

## 🏆 Competition Deliverables

| Deliverable | Status | File |
|-------------|--------|------|
| ✅ Optimal strategy | Complete | `optimal_strategy_TIMESTAMP.csv` |
| ✅ Expected P&L | Complete | $80.84M |
| ✅ Alternative strategies | Complete | 2 strategies |
| ✅ Monte Carlo | Complete | 10,000 simulations |
| ✅ Risk metrics | Complete | VaR, CVaR, Sharpe |
| ✅ Scenario analysis | Complete | 4 scenarios |
| ✅ Excel outputs | Complete | 4 files |

---

## 🎓 Key Assumptions

1. **Freight Rate:** Baltic LNG data = $/day for vessel charter
2. **Buyer Premiums:** All values ADDED to base price
3. **JKM M+1 Pricing:** Uses next month's forward price
4. **Credit Default:** Based on industry-standard ratings
5. **Demand Profile:** Monthly seasonality (50% → 105%)

---

## ⚡ Performance

- **Runtime:** ~2 seconds end-to-end
- **Monte Carlo:** 10,000 simulations in ~1 second
- **Code Quality:** 0 linting errors
- **Documentation:** 1,891+ lines of code

---

## 📞 Support

For detailed information:
1. Check `optimization.log` for execution trace
2. Review `IMPLEMENTATION_SUMMARY.md` for technical details
3. See `QUICK_START.md` for common usage patterns

---

## 📄 License

Educational/Competition Use

---

**Status:** ✅ Production-Ready  
**Last Updated:** October 16, 2025  
**Version:** 2.0 - Cargo Optimization System
