# LNG Cargo Trading Optimization Model - User Guide

## Quick Start

### Running the Model
```bash
# Full analysis with all features
python main_optimization.py

# Customized run (disable specific features if needed)
python main_optimization.py --no-monte-carlo --no-scenarios --no-sensitivity
```

### Key Outputs
- **Optimal Strategy**: `outputs/results/optimal_strategy.xlsx`
- **Risk Analysis**: `outputs/results/monte_carlo_results.xlsx`
- **Sensitivity Tests**: `outputs/results/sensitivity_analysis.xlsx`
- **Visualizations**: `outputs/diagnostics/figures/`

## Model Logic Overview

### 1. **Data Input & Forecasting**
- **Henry Hub**: NYMEX forward curve (most liquid US gas benchmark)
- **JKM**: LNG spot prices for Asia (Japan/Korea Marker)
- **Brent**: Oil prices (affects Singapore LNG pricing)
- **Freight**: Baltic LNG freight rates (with quality fixes applied)
- **Forecasting**: ARIMA+GARCH for price/volatility predictions

### 2. **P&L Calculation Engine**
Each cargo's profitability depends on:
```
P&L = Revenue - Costs
Revenue = Volume × (JKM + Premium) × (1 - Boil-off)
Costs = Henry Hub + Freight + Insurance + Brokerage + Working Capital + Carbon + Demurrage + LC Fees + Tolling Fee
```

### 3. **Optimization Logic**
- **Objective**: Maximize total expected P&L across 6 cargoes (Jan-Jul 2026)
- **Constraints**: 
  - Volume flexibility: ±10% per cargo (case requirement)
  - Credit risk adjustments for different buyers
  - Demand seasonality factors
- **Decision Variables**: Destination (Singapore/Japan/China) and buyer for each month

### 4. **Risk Management**
- **Monte Carlo**: 10,000 correlated price simulations
- **Risk Metrics**: VaR (95%), CVaR, Sharpe Ratio
- **Hedging**: Henry Hub futures to reduce gas price exposure
- **Stress Tests**: JKM spikes, terminal outages, canal delays

## Key Assumptions

### Business Assumptions
- **Currency**: All prices in USD (industry standard for LNG)
- **Boil-off**: 0.05%/day (modern LNG carrier standard)
- **Voyage Times**: USGC→Singapore (25d), Japan (20d), China (22d)
- **Volume Flexibility**: ±10% per contract terms

### Market Assumptions
- **Singapore Pricing**: Brent-linked (oil-indexed)
- **Japan/China Pricing**: JKM-linked (gas-indexed)
- **Freight Quality**: Baltic data with industry-based outlier capping ($5k-$120k/day)
- **Data Limitation**: Freight volatility 268% (high due to data quality issues)

## Model Strengths

### 1. **Realistic Market Modeling**
- Uses actual forward curves where available
- Incorporates LNG-specific factors (boil-off, freight, seasonality)
- Accounts for different pricing mechanisms (oil vs. gas indexation)

### 2. **Comprehensive Risk Analysis**
- Monte Carlo simulation with correlated price paths
- Multiple scenario testing (bull/bear/volatile markets)
- Stress testing for operational disruptions

### 3. **Operational Flexibility**
- Tests volume flexibility within contract terms
- Considers multiple destinations and buyers
- Incorporates credit risk and demand seasonality

## Model Limitations

### 1. **Data Quality Issues**
- Baltic LNG freight data has high volatility (268% vs. industry norm 40-60%)
- Applied industry-based capping to handle extreme outliers
- **Note**: Results are conservative due to data limitations
- **Correlation Matrix**: Fixed date alignment issues (36 overlapping observations)

### 2. **Simplified Assumptions**
- USD currency assumption (no FX risk modeling)
- Static voyage times (no weather/routing optimization)
- Fixed buyer relationships (no competitive bidding)

### 3. **Market Limitations**
- No liquidity constraints in price forecasting
- No consideration of model's impact on market prices
- Simplified hedging strategy (Henry Hub only)

## Interpretation Guide

### Key Metrics to Watch
1. **Total Expected P&L**: Primary optimization objective
2. **VaR (95%)**: Maximum expected loss with 95% confidence
3. **Sharpe Ratio**: Risk-adjusted return measure
4. **Strategy Changes**: Number of months changing destinations

### Red Flags
- **High VaR**: Indicates significant downside risk
- **Low Sharpe Ratio**: Poor risk-adjusted returns
- **Many Strategy Changes**: Unstable optimal strategy
- **Extreme Sensitivity**: Model too dependent on specific parameters

## Competition Talking Points

### Model Sophistication
- "We use actual forward curves and ARIMA+GARCH forecasting"
- "Our model accounts for LNG-specific factors like boil-off and freight"
- "We test operational resilience with stress scenarios"

### Risk Management
- "Monte Carlo analysis with 10,000 correlated simulations"
- "We hedge Henry Hub exposure to reduce gas price risk"
- "Stress tests show model adapts to market disruptions"

### Practical Application
- "Model handles real LNG trading constraints (volume flexibility, credit risk)"
- "Results are conservative due to data quality limitations"
- "Strategy is robust across different market scenarios"

## Troubleshooting

### Common Issues
- **Import Errors**: Ensure all dependencies installed (`pip install -r requirements.txt`)
- **Data Loading**: Check Excel files are in `data_processing/` directory
- **Memory Issues**: Reduce Monte Carlo simulations in `config/settings.py`

### Performance Tips
- Use `--no-monte-carlo` for faster runs during development
- Disable scenarios/sensitivity for quick strategy optimization
- Check `optimization.log` for detailed execution logs
