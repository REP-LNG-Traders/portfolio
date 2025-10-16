# LNG Cargo Optimization - Quick Start Guide

## 🚀 Run the System

### Full Analysis (Recommended)
```bash
python main_optimization.py
```

**Runtime:** ~2 seconds  
**Output:** 4 Excel/CSV files in `outputs/results/`

---

## 📊 Output Files

1. **`strategies_comparison_TIMESTAMP.xlsx`**
   - Strategy comparison summary
   - Monthly breakdown for each strategy
   - Best for: Executive presentation

2. **`optimal_strategy_TIMESTAMP.csv`**
   - Month-by-month routing decisions
   - Best for: Quick reference table

3. **`monte_carlo_risk_metrics_TIMESTAMP.xlsx`**
   - VaR, CVaR, Sharpe ratios
   - Best for: Risk analysis discussion

4. **`scenario_analysis_TIMESTAMP.xlsx`**
   - Stress test results (4 scenarios)
   - Best for: What-if analysis

---

## 📈 Key Results (Current Configuration)

### Optimal Strategy - $80.84M Total
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
- **VaR (5%):** $2.13M (95% of outcomes better than this)
- **Probability of Profit:** 95.7%
- **Sharpe Ratio:** 1.04

### Alternative Strategies
- **Conservative (Singapore only):** $74.95M - Lower risk, lower return
- **High JKM Exposure (Japan/China):** $66.37M - Best Sharpe ratio (1.80)

---

## 🔧 Quick Customization

### Skip Monte Carlo (faster)
```python
from main_optimization import main
results = main(run_monte_carlo=False)
```

### Skip Scenario Analysis
```python
results = main(run_scenarios=False)
```

### Fast Mode (no simulations)
```python
results = main(run_monte_carlo=False, run_scenarios=False)
# Runtime: <1 second
```

---

## 📝 Before Presentation

### 1. Validate Assumptions
- [ ] Check `config.py` buyer premiums with mentors
- [ ] Confirm freight rate interpretation ($/day vs $/MMBtu)
- [ ] Review demand profile (Jan: 50%, Jun: 105%)

### 2. Customize Scenarios (Optional)
Edit `config.py` → `CARGO_SCENARIOS`:
```python
'Bull_Asia': {
    'jkm': 1.20,        # JKM +20%
    'henry_hub': 1.0,
    'brent': 1.0,
    'freight': 1.0
}
```

### 3. Review Risk Metrics
- **High freight volatility (3,230%)** - flag for discussion
- **Optimal strategy: 95.7% profit probability** - key selling point
- **High_JKM: Best Sharpe ratio (1.80)** - risk-adjusted champion

---

## 🏆 Competition Checklist

- ✅ Optimal strategy with P&L: **$80.84M**
- ✅ 2-3 alternative strategies: **Conservative, High_JKM**
- ✅ Monte Carlo simulation: **10,000 paths**
- ✅ Risk metrics: **VaR, CVaR, Sharpe, Prob(Profit)**
- ✅ Scenario analysis: **4 scenarios**
- ✅ Excel/CSV outputs: **Professional formatting**
- ✅ Audit trail: **Detailed logs in `optimization.log`**

---

## 📞 Troubleshooting

### "No module named 'src'"
```bash
cd "c:\Users\nicko\Desktop\LNG Case Comp\portfolio"
python main_optimization.py
```

### "Data file not found"
- Ensure Data/ folder contains the 5 Excel files
- Check filenames match exactly

### Results look strange
- Check `optimization.log` for warnings
- Verify data loaded correctly (check log: "753 rows from 2022-09-23...")

---

## 🎯 Next Steps

1. **Run the system** ✅
2. **Review outputs** ✅
3. **Validate with mentors** 
4. **Prepare presentation slides**
5. **Win the competition** 🏆

---

**Good luck with your 6 PM presentation!** 🚀

