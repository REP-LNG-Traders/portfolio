# Stress Test Scenarios - LNG Market Events

## Overview

This document outlines the stress test scenarios implemented in the sensitivity analysis module. These scenarios test how the LNG cargo optimization model responds to realistic market disruptions and operational challenges.

## Key Questions for Judges

1. **Model Resilience**: How does our strategy adapt when unexpected events occur?
2. **Risk Management**: What are the P&L impacts of different stress scenarios?
3. **Operational Flexibility**: Can we quickly reroute cargo when infrastructure fails?
4. **Commercial Decision Making**: How do we rebalance flows in real-time?

## Implemented Scenarios

### 1. JKM Price Spike (Cold Snap in Northeast Asia)

**Event**: Sudden cold snap in Northeast Asia  
**Impact**: JKM prices spike by +$5.00/MMBtu due to demand surge  
**Expected Model Response**: 
- Shift cargoes from Singapore (Brent-linked) to Japan/China (JKM-linked)
- Capture higher prices in Northeast Asia markets
- Optimize destination mix based on new price spreads

**Key Metrics**:
- P&L impact from price spike capture
- Number of strategy changes (destination switches)
- Optimal buyer reallocation

### 2. SLNG Terminal Outage

**Event**: SLNG terminal outage or capacity constraint  
**Impact**: Singapore destination becomes unavailable  
**Expected Model Response**:
- Force reroute Singapore-bound cargoes to Japan/China
- Cascade effects on other cargoes due to capacity constraints
- Maintain volume commitments despite infrastructure failure

**Key Metrics**:
- Number of forced reroutes from Singapore
- P&L impact from suboptimal destinations
- Strategy robustness under operational constraints

### 3. Panama Canal Delay

**Event**: Vessel stuck at Panama Canal  
**Impact**: Voyage time increases by 5 days for all routes  
**Expected Model Response**:
- Increased freight costs change destination economics
- Potential shift to shorter routes (if available)
- Reoptimize based on new voyage cost structure

**Key Metrics**:
- P&L impact from increased freight costs
- Strategy changes due to cost structure shifts
- Operational flexibility under logistics constraints

## Implementation Details

### Technical Approach

1. **Scenario Setup**: Each scenario modifies specific parameters while keeping others constant
2. **Strategy Reoptimization**: Full optimization run with modified parameters
3. **Change Analysis**: Compare new strategy against base case
4. **Impact Quantification**: Measure P&L and operational impacts

### Code Structure

```python
# Example usage
sensitivity_analyzer = SensitivityAnalyzer(calculator, optimizer)
stress_tests = sensitivity_analyzer.run_stress_test_scenarios(forecasts)
```

### Output Analysis

Each scenario produces:
- **P&L Impact**: Dollar and percentage change from base case
- **Strategy Changes**: Monthly destination/buyer switches
- **Risk Assessment**: High/Medium/Low risk classification
- **Detailed Logs**: Step-by-step decision changes

## Expected Results

### Cold Snap Scenario
- **Positive P&L Impact**: Capturing JKM price spike
- **Strategy Changes**: 2-4 months likely to switch destinations
- **Risk Level**: Low (favorable market event)

### SLNG Outage Scenario
- **Negative P&L Impact**: Suboptimal rerouting costs
- **Strategy Changes**: All Singapore cargoes forced to reroute
- **Risk Level**: High (operational disruption)

### Canal Delay Scenario
- **Negative P&L Impact**: Increased freight costs
- **Strategy Changes**: 1-3 months may change destinations
- **Risk Level**: Medium (logistics disruption)

## Visualization Outputs

The analysis generates comprehensive visualizations:

1. **P&L Impact Comparison**: Bar chart showing scenario impacts
2. **Strategy Robustness**: Count of strategy changes per scenario
3. **Monthly Changes Heatmap**: Which months change strategies
4. **Risk-Return Profile**: Scatter plot of risk vs. return impacts

## Excel Output Structure

### Stress Tests Summary Sheet
- Scenario names and P&L impacts
- Strategy change counts
- Risk level classifications

### Individual Scenario Sheets
- Detailed event descriptions
- Monthly strategy changes
- Rerouting decisions and rationale

## Business Value

### For Competition Judges

1. **Demonstrates Model Sophistication**: Shows ability to handle real-world disruptions
2. **Risk Management Capability**: Quantifies downside scenarios
3. **Operational Resilience**: Proves model can adapt to constraints
4. **Commercial Intelligence**: Shows understanding of LNG market dynamics

### For Real-World Application

1. **Scenario Planning**: Prepare for various market disruptions
2. **Risk Assessment**: Understand potential P&L impacts
3. **Operational Planning**: Develop contingency strategies
4. **Stakeholder Communication**: Explain model behavior under stress

## Integration with Main Analysis

The stress test scenarios are automatically included when running:

```bash
python main_optimization.py --run_sensitivity
```

Results are saved to:
- `outputs/diagnostics/sensitivity/stress_test_analysis.png`
- `outputs/results/sensitivity_analysis.xlsx`

## Key Assumptions

1. **Price Spike Magnitude**: +$5/MMBtu is realistic for winter demand surges
2. **Outage Duration**: Assumes temporary outage (not permanent closure)
3. **Canal Delay**: 5 days represents typical congestion delays
4. **Model Response Time**: Assumes immediate reoptimization capability

## Limitations and Future Enhancements

### Current Limitations
- Scenarios are independent (no correlation between events)
- Fixed magnitude impacts (no probability weighting)
- No consideration of market liquidity constraints

### Potential Enhancements
- **Correlated Scenarios**: Multiple events occurring simultaneously
- **Probability Weighting**: Risk-adjusted scenario analysis
- **Dynamic Response**: Time-varying model adjustments
- **Market Impact**: Consider model's effect on market prices

## Conclusion

The stress test scenarios provide comprehensive coverage of realistic LNG market disruptions. They demonstrate the model's ability to:

1. **Adapt Quickly**: Reoptimize strategies in real-time
2. **Manage Risk**: Quantify and respond to various threats
3. **Maintain Performance**: Continue generating value under stress
4. **Provide Transparency**: Clear reporting of decision changes

This analysis is essential for judges to understand the model's robustness and practical applicability in real LNG trading environments.
