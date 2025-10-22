# Figure Placement Guide - LNG Cargo Optimization Paper

**Objective**: Strategic placement of 6-8 visualizations to enhance comprehension and professional presentation

---

## 📊 Recommended Figure Placements

### FIGURE 1: Monthly P&L Progression
**Location**: Section 3.1, after base contract table  
**Current Reference**: None (add after line 300)

**What to show:**
- Line chart with 6 months (Jan-Jun) on x-axis
- P&L values on y-axis ($20M-$30M range)
- Single line for Singapore/Iron_Man strategy
- Color: Professional blue (#2E86AB)

**Caption:**
```
Figure 1: Base Contract P&L Progression by Month
All six cargoes route to Singapore/Iron_Man, generating $22.78M to $29.73M per month 
(+30.5% improvement Jan-Jun). Strong Brent pricing and seasonal demand improvement 
drive increasing margins.
```

**Integration Point:**
After the results table (around line 300), add:
```
[FIGURE 1 HERE]

This progression reflects two key drivers: (1) strengthening Brent prices providing higher 
(Brent × 0.13) base value, and (2) improving seasonal demand (10% Jan → 65% Jun) reducing 
competitive discounts required for sales confirmation.
```

---

### FIGURE 2: Strategy Comparison - Why Singapore Dominates
**Location**: Section 3.1, Key Observations  
**Current Reference**: None (add around line 310)

**What to show:**
- Bar chart comparing 4 strategies: Singapore/Iron_Man (base), Japan/Hawk_Eye, China/QuickSilver, Singapore/Thor
- Show monthly P&L for each
- Mark optimal (Singapore/Iron_Man) in bold or highlight

**Alternative: Heatmap**
- Rows: 6 months
- Columns: 4 destination/buyer combinations
- Color intensity = P&L value
- Darker = higher value

**Caption:**
```
Figure 2: Strategy Comparison Heatmap
Singapore/Iron_Man (highlighted) dominates all six months. Alternatives underperform by 
$3.10M (Japan) and $10.23M (China) per cargo due to premium differentials and regulatory costs.
```

---

### FIGURE 3: Options Exercise Tiers
**Location**: Section 3.2, embedded options  
**Current Reference**: None (add after options table, around line 335)

**What to show:**
- Vertical stacked bar chart showing 5 options
- Stack 1 (top): 3 Japan Hawk_Eye options (Apr, May, Jun) = $81.1M
- Stack 2 (bottom): 2 Singapore Iron_Man options (Mar, Apr) = $50.8M
- Add value labels on each segment

**Caption:**
```
Figure 3: Embedded Options Value Decomposition ($131.90M Total)
Top tier: 3 Japan/Hawk_Eye options (Apr-Jun delivery) with $7.95/MMBtu value and 90% demand 
probability total $81.1M. Bottom tier: 2 Singapore/Iron_Man options with $9.59/MMBtu intrinsic 
value and 70% demand, total $50.8M.
```

---

### FIGURE 4: P&L Distribution - Hedged vs Unhedged
**Location**: Section 3.3, after Monte Carlo table  
**Current Reference**: Variance decomposition (line 365-390 conceptually)

**What to show:**
- Dual distribution curves (overlaid or side-by-side)
- X-axis: P&L ($M)
- Y-axis: Probability density
- Blue: Unhedged (wider distribution, $22.77M volatility)
- Green: Hedged (narrower distribution, $15.37M volatility)
- Mark mean ($83M) with vertical line
- Mark VaR (5%) threshold

**Caption:**
```
Figure 4: Monte Carlo P&L Distribution (10,000 scenarios)
Hedged strategy (green) shows 32.5% volatility reduction vs unhedged (blue). Both maintain 
similar mean (~$83M), but hedging eliminates Henry Hub downside tail, improving worst-case 
outcomes from $44.51M (VaR) to $60.82M.
```

**Add after table:**
```
The distribution analysis reveals that hedging's value derives not from higher expected returns 
(which remain nearly identical at $83.07M vs $83.01M), but from volatility compression and tail 
risk reduction. The 32.5% volatility reduction corresponds directly to eliminating the 73% HH 
component from the unhedged portfolio variance.
```

---

### FIGURE 5: Variance Decomposition Pie Charts
**Location**: Section 3.3 Risk Analysis, after variance decomposition text  
**Current Reference**: Lines 395-408 ("Unhedged vs Hedged variance contribution")

**What to show:**
- Two pie charts side-by-side
- Left: Unhedged (HH 73%, Brent 21%, JKM 5%, Freight 1%)
- Right: Hedged (Brent 89%, JKM 11%, HH ~0%, Freight <1%)
- Use contrasting colors for each commodity

**Caption:**
```
Figure 5: Variance Decomposition - Unhedged vs Hedged (10,000 scenarios)
Left: Unhedged portfolio dominated by Henry Hub risk (73%), with secondary Brent exposure (21%). 
Right: Hedged portfolio shifts dominance to Brent (89%) and JKM (11%), essentially eliminating 
HH variance. This reallocation explains the 32.5% total volatility reduction.
```

---

### FIGURE 6: Tornado Sensitivity Analysis
**Location**: Section 4.1, Key Drivers of Profitability  
**Current Reference**: Lines 475-512 (discuss drivers but no visual)

**What to show:**
- Horizontal tornado chart showing parameter sensitivity
- Base case: $293.52M (center line)
- Parameters (top to bottom): Brent price, JKM price, Freight rate, HH price, Demand level, Volume flexibility
- Left arrow: Parameter at -10%
- Right arrow: Parameter at +10%
- Length of arrow = sensitivity magnitude

**Caption:**
```
Figure 6: Tornado Sensitivity Analysis - Total Portfolio Value
Portfolio most sensitive to Brent price (±10% = ±$12M range), followed by JKM ($8M range), 
and freight ($2M range). Conversely, volume flexibility and demand variations produce minor 
impacts, suggesting decision robustness around operational parameters.
```

---

### FIGURE 7: Risk-Return Profile (Sharpe Ratio Comparison)
**Location**: Section 4.2, Risk-Return Trade-Offs  
**Current Reference**: Implicit in discussion (lines 515-530)

**What to show:**
- Scatter plot showing:
  - X-axis: Volatility ($M)
  - Y-axis: Expected Return ($M)
  - 3 points: Unhedged, Hedged, Conservative
  - Size of bubble = Sharpe ratio (larger = better)
  - Labeled with values

**Alternative: Bar chart**
- 3 bars comparing Unhedged vs Hedged vs Conservative
- Show Sharpe ratio, volatility, expected P&L side-by-side

**Caption:**
```
Figure 7: Risk-Return Profile - Strategy Comparison
Hedged strategy (green) achieves highest risk-adjusted returns (Sharpe 5.40) with moderate 
volatility ($15.37M). Conservative strategy (blue) offers lower volatility but sacrifices $12.21M 
in expected returns. Unhedged (orange) shows highest volatility ($22.77M) but intermediate 
Sharpe ratio (3.65).
```

---

### FIGURE 8: Stress Test Impact Summary
**Location**: Section 3.4, after stress test table  
**Current Reference**: Lines 432-470 (interpretation text)

**What to show:**
- Horizontal bar chart showing 3 scenarios
- Scenario names on left (JKM Spike, SLNG Outage, Panama Delay)
- Bars show impact: green for positive, red for negative
- Center line at $0 impact
- Label with dollar amounts and percentage changes

**Caption:**
```
Figure 8: Stress Test Scenario Impact on Portfolio P&L
Base case $293.52M portfolio shows asymmetric stress resilience. Upside scenario (JKM spike) 
generates +$95.21M uplift (+98%), demonstrating embedded convexity. Downside scenarios show 
manageable impacts: SLNG outage (-$17.38M, -18%) and Panama delay (-$2.62M, -3%), reflecting 
robust margin structure.
```

---

## 📍 Specific Integration Instructions

### After Section 3.1 Table (Line ~300):
**ADD FIGURES 1 & 2**
- Figure 1: P&L progression line chart
- Figure 2: Strategy comparison heatmap

### After Section 3.2 Options Table (Line ~335):
**ADD FIGURE 3**
- Figure 3: Options value stacked bar chart

### After Section 3.3 Risk Table (Line ~360):
**ADD FIGURES 4 & 5**
- Figure 4: P&L distribution overlay
- Figure 5: Variance decomposition pie charts

### Section 3.4 Stress Tests (Line ~470):
**ADD FIGURE 8**
- Figure 8: Stress scenario bar chart

### Section 4.1 Discussion (Line ~485):
**ADD FIGURE 6**
- Figure 6: Tornado sensitivity chart

### Section 4.2 Discussion (Line ~515):
**ADD FIGURE 7**
- Figure 7: Risk-return scatter/comparison

---

## 📋 Figure Summary Checklist

| Figure | Type | Location | Current Status |
|--------|------|----------|---|
| 1 | Line chart | Section 3.1 | `outputs/diagnostics/sensitivity/price_sensitivities.png` |
| 2 | Heatmap | Section 3.1 | Can be generated from results data |
| 3 | Stacked bar | Section 3.2 | Can be generated from options data |
| 4 | Distribution | Section 3.3 | Monte Carlo output visualization |
| 5 | Pie charts | Section 3.3 | From variance decomposition |
| 6 | Tornado | Section 4.1 | `outputs/diagnostics/sensitivity/tornado_diagram.png` |
| 7 | Scatter/bars | Section 4.2 | From risk metrics comparison |
| 8 | Bar chart | Section 3.4 | From stress test results |

---

## 🎨 Professional Styling Guidelines

**Color Scheme:**
- Primary: #2E86AB (Professional blue) - Use for optimal strategy, hedged scenarios
- Secondary: #A23B72 (Purple) - Alternative/comparison strategies
- Accent: #F18F01 (Orange) - Warnings, unhedged strategy
- Success: #06A77D (Green) - Hedged improvements, positive scenarios
- Alert: #C1121F (Red) - Negative impacts, risks

**Typography:**
- Title: 12-14pt bold
- Axis labels: 10pt
- Legend: 9pt
- Caption: 10pt italic

**Resolution:**
- Save all figures as 300 DPI PNG
- Dimensions: 6"×4" (1800×1200px) for landscape, 4"×5" for portrait
- Professional sans-serif font (Arial, Calibri, or similar)

---

## 📄 Caption Format Template

Each caption should follow this structure:
```
Figure N: [Title]
[Interpretation]: [What the figure shows and why it matters]
[Key insight]: [The main takeaway or conclusion from the figure]
```

Example (Figure 4):
```
Figure 4: Monte Carlo P&L Distribution (10,000 scenarios)
Distribution analysis: Hedged strategy (green) shows 32.5% volatility reduction vs unhedged (blue). 
Both maintain similar mean (~$83M), but hedging eliminates downside tail risk.
Key insight: Hedging's value derives from volatility compression and risk reduction, not return sacrifice.
```

---

## 🚀 Next Steps

1. **Generate Figures 1-8** using your existing output data
2. **Insert after each section** using the placement guide above
3. **Update table of contents** with "List of Figures"
4. **Verify figure references** are numbered consistently
5. **Professional review** - ensure consistent styling and captioning

**Total figures**: 8 visualizations  
**Estimated pages added**: 4-6 pages (allowing for spacing)  
**Final paper length**: ~24-28 pages (from current ~20 pages)

This creates a professional, visually-supported research paper ready for competition submission.
