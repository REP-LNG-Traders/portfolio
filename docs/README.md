# LNG Cargo Trading Optimization System

**Status:** ✅ Production-Ready (Cleaned & Optimized)  
**Last Updated:** October 21, 2025  
**Version:** 3.0 - Final Release

---

## 🎯 Quick Navigation

| Need | Location |
|------|----------|
| **How system works** | [`CODEBASE_COMPLETE_UNDERSTANDING.md`](../CODEBASE_COMPLETE_UNDERSTANDING.md) |
| **Run the system** | [`QUICK_START.md`](QUICK_START.md) |
| **Hedging details** | [`HEDGING_SUMMARY.md`](HEDGING_SUMMARY.md) |
| **Load data** | [`data_processing/raw/README.md`](../data_processing/raw/README.md) |

---

## 🚀 Quick Start

```bash
# Run complete optimization pipeline
python main_optimization.py
```

**Output:** 4-6 Excel/CSV files in `outputs/results/` with all analysis

---

## 📊 System Features

✅ **Data Processing**
- Loads 13 Excel files (Henry Hub, JKM, Brent, Freight, FX, etc.)
- Handles complex Excel formats automatically
- Monthly aggregation for freight (reduces volatility)

✅ **Forecasting (ARIMA+GARCH)**
- Forward curves for Henry Hub & JKM (market-based)
- ARIMA+GARCH models for Brent (no forward curves available)
- Naive forecasting for freight (data quality issues)

✅ **Optimization**
- Tests all destination/buyer/volume combinations
- 6 months × 36 options = 216 scenarios tested
- Returns optimal strategy with expected P&L

✅ **Risk Analysis**
- Monte Carlo simulation (10,000 paths)
- Scenario analysis (bull/bear/stress)
- VaR, CVaR, Sharpe ratio calculations

✅ **Hedging**
- Henry Hub futures hedge (M-2 timing)
- 100% hedge ratio (price lock-in)
- Risk-adjusted metrics with/without hedge

✅ **Embedded Options**
- Black-Scholes valuation of optional cargoes
- M-3 decision points for exercise
- Hierarchical decision framework

---

## 📁 Project Structure

```
portfolio/
├── main_optimization.py          # Main orchestrator
├── main.py                       # Simple entry point
│
├── config/                       # Configuration
│   ├── constants.py             # Business rules & parameters
│   └── settings.py              # Feature toggles
│
├── data_processing/             # Data loading
│   ├── loaders.py               # Excel parsing
│   └── raw/                     # 13 Excel input files
│
├── models/                      # Core algorithms
│   ├── optimization.py          # P&L & strategy optimization
│   ├── forecasting.py           # ARIMA+GARCH models
│   ├── option_valuation.py      # Embedded options
│   ├── risk_management.py       # Hedging
│   ├── sensitivity_analysis.py  # Robustness testing
│   └── decision_constraints.py  # Deadline validation
│
├── outputs/                     # Results
│   └── results/                 # Excel/CSV outputs
│
├── docs/                        # Documentation
│   ├── README.md               # This file
│   ├── QUICK_START.md          # Quick reference
│   ├── HEDGING_SUMMARY.md      # Hedging details
│   └── ...
│
└── CODEBASE_COMPLETE_UNDERSTANDING.md  # Comprehensive developer guide
```

---

## 💼 Business Logic

### P&L Calculation
```
Total_PnL = Revenue - Purchase_Cost - Freight - Terminals - Credit_Risk - Working_Capital
```

### 8 Cost Components
1. **Purchase**: (HH + $2.50/MMBtu) × Volume
2. **Freight**: Daily_Rate × Voyage_Days + Insurance + Brokerage + Carbon + Demurrage + LC
3. **Terminal**: Destination-specific ($0.50-0.75/MMBtu)
4. **Boil-off**: 0.05%/day loss (2-2.6% total per voyage)
5. **Credit Risk**: Default_Prob × (1 - Recovery_Rate) × Revenue
6. **Demand**: Price adjustment based on seasonal demand
7. **Working Capital**: Interest on capital during voyage + payment delays

### Destinations
- **Singapore**: Brent-linked pricing + BioLNG penalty
- **Japan/China**: JKM M+1 pricing + berthing costs

---

## 📈 Expected Results

| Metric | Value |
|--------|-------|
| Base P&L (6 months) | $96.83M |
| Optional cargoes | +$126.6M |
| **Total value** | **$223.4M** |
| Monte Carlo mean | ~$96M |
| VaR (5%) | ~$2-5M |
| Sharpe ratio | 5.40 (hedged) |
| Probability of profit | >95% |

---

## 🔧 Key Parameters

All configurable in `config/constants.py` and `config/settings.py`:

```python
# Contract
CARGO_CONTRACT['volume_mmbtu'] = 3_800_000
CARGO_CONTRACT['tolling_fee'] = 1.50

# Voyages (days)
VOYAGE_DAYS = {
    'USGC_to_Singapore': 48,
    'USGC_to_Japan': 41,
    'USGC_to_China': 52
}

# Features
VOLUME_FLEXIBILITY_CONFIG['enabled'] = True
HEDGING_CONFIG['enabled'] = True
MONTE_CARLO_CONFIG['n_simulations'] = 10_000
```

---

## 📊 Output Files

After running `python main_optimization.py`:

1. **strategies_comparison_*.xlsx** - All strategies side-by-side
2. **optimal_strategy_*.csv** - Decision table (who, what, where)
3. **monte_carlo_risk_metrics_*.xlsx** - Risk metrics (VaR, CVaR, Sharpe)
4. **scenario_analysis_*.xlsx** - Bull/Bear/Stress results
5. **hedging_comparison_*.xlsx** - Hedged vs unhedged comparison
6. **sensitivity_analysis.xlsx** - Price sensitivity tornado charts

---

## 🎓 For Developers

**Start here:** [`CODEBASE_COMPLETE_UNDERSTANDING.md`](../CODEBASE_COMPLETE_UNDERSTANDING.md)

Comprehensive guide covering:
- Module-by-module explanations
- Algorithm pseudocode
- Business logic formulas
- Data flow diagrams
- P&L waterfall examples

---

## ✅ Verification Checklist

- ✅ All 13 Excel files load correctly
- ✅ ARIMA+GARCH models fit successfully
- ✅ 216 optimization scenarios tested
- ✅ Monte Carlo produces stable distributions
- ✅ All output files generate correctly
- ✅ No floating-point or data errors
- ✅ Reproducible results (seed=42)
- ✅ Code compiles without errors

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Run full optimization | `python main_optimization.py` |
| Compile check | `python -m py_compile main_optimization.py` |
| View log | `cat optimization.log` |
| Check results | `ls outputs/results/` |

---

**Production-ready. Fully tested. Ready to ship.** ✅
