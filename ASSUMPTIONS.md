# Key Assumptions and Data Sources

## Pricing Data

### Henry Hub
- **Source**: NYMEX Natural Gas futures (most liquid US gas benchmark)
- **Date Range**: 2022-09 to 2025-09 (historical) + forward curve to 2027-01
- **Frequency**: Daily historical, monthly forward contracts

### JKM (Japan Korea Marker)
- **Source**: LNG spot prices for Northeast Asia
- **Date Range**: 2022-09 to 2025-09 (historical) + forward curve to 2026-12
- **Frequency**: Daily historical, monthly forward contracts

### Brent Oil
- **Source**: ICE Brent crude oil futures
- **Date Range**: 1987-05 to 2025-09 (extended historical coverage)
- **Frequency**: Daily historical data

### Freight Rates
- **Source**: Baltic LNG freight index (.BLNG3g)
- **Date Range**: 2021-03 to 2025-09
- **Data Quality Issue**: Original data contained negative prices and extreme outliers (>$120k/day)

**Resolution**: Applied industry-based outlier capping:
- **Upper Cap**: $120,000/day (extreme market conditions)
- **Lower Cap**: $5,000/day (minimum viable vessel economics)
- **Resulting Volatility**: 268% (high but documented limitation)

**Note**: High volatility (268% vs. industry norm 40-60%) is acknowledged as a data quality limitation. Results should be interpreted with this caveat.

## Volume Optimization

### Contract Flexibility
- **Volume Range**: ±10% per contract terms (case pack page 15)
- **Implementation**: All months optimized to 110% volume based on margin analysis

### Cargo Specifications
- **Standard Size**: 165,000 cubic meters (typical LNG carrier)
- **Boil-off Rate**: 0.05%/day (modern LNG carrier standard)
- **Volume Delivered**: 165,000 × 0.9995^voyage_days cubic meters

## Voyage Economics

### Voyage Times
- **USGC to Singapore**: 25 days
- **USGC to Japan**: 20 days  
- **USGC to China**: 22 days

### Freight Cost Components
1. **Base Freight**: Baltic LNG rates (with outlier capping)
2. **Insurance**: 0.25% of cargo value
3. **Brokerage**: 1.25% of freight cost
4. **Working Capital**: 8% annual cost on freight amount
5. **Carbon Cost**: $50/tonne CO2 (voyage emissions)
6. **Demurrage**: $50,000/day for delays
7. **LC Fees**: $25,000 per cargo

## Hedging Strategy

### Henry Hub Hedging
- **Instrument**: NYMEX Natural Gas futures
- **Timing**: M-2 (two months before delivery)
- **Hedge Ratio**: 100% of Henry Hub purchase price component
- **Contract Size**: 10,000 MMBtu per contract

### Rationale
- Reduces exposure to US gas price volatility
- Maintains exposure to JKM-Brent spreads (core value driver)
- Standard industry practice for LNG trading

## Currency Assumptions

### USD Denomination
- **All prices**: Assumed to be in USD
- **Singapore LNG**: Quoted in USD despite local SGD market
- **Rationale**: Industry standard for international LNG trading
- **FX Data**: Loaded but not used (out of scope)

## Risk Management

### Monte Carlo Simulation
- **Simulations**: 10,000 correlated price paths
- **Correlation Calculation**: 36 overlapping monthly observations (2022-09 to 2025-09)
- **Risk Metrics**: VaR (95%), CVaR, Sharpe Ratio
- **Data Quality**: Freight volatility high (268%) but correlation matrix valid

### Stress Testing
- **Scenarios**: JKM price spikes, terminal outages, canal delays
- **Purpose**: Test model resilience to market disruptions
- **Implementation**: Real-time strategy reoptimization

## Model Limitations

### Data Quality Issues
1. **Freight Volatility**: 268% (high due to Baltic data quality)
2. **Limited Historical Data**: Only 3+ years of overlapping observations
3. **Forward Curve Gaps**: Some months use ARIMA+GARCH extensions

### Simplifying Assumptions
1. **Static Voyage Times**: No weather/routing optimization
2. **Fixed Buyer Relationships**: No competitive bidding
3. **No Liquidity Constraints**: Assumes market depth for all volumes
4. **No Market Impact**: Model doesn't affect market prices

### Scope Limitations
1. **FX Risk**: Not modeled (USD assumption)
2. **Credit Risk**: Simplified probability adjustments
3. **Operational Risk**: Limited to demurrage modeling
4. **Regulatory Risk**: Not considered

## Validation Results

### Correlation Matrix (36 observations, 2022-09 to 2025-09)
```
            henry_hub    jkm  brent  freight
henry_hub      1.000  0.546 -0.060    0.069
jkm            0.546  1.000  0.108    0.231
brent         -0.060  0.108  1.000   -0.016
freight        0.069  0.231 -0.016    1.000
```

### Volatilities (Annualized from Monthly Data)
- **Henry Hub**: 60.8%
- **JKM**: 54.2%
- **Brent**: 20.4%
- **Freight**: 153.9% (data limitation)

### Validation Checks
- ✅ Price data loaded successfully
- ✅ Date range covers forecast period (2026)
- ✅ All forecasts positive
- ✅ Buyers properly configured
- ✅ Correlation matrix valid (4×4)
- ⚠️ Freight volatility high (documented limitation)
