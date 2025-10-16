# LNG Trading Risk Assessment Model

## Overview
This project implements a comprehensive LNG trading model for Atlantic Trading Pte Ltd that combines:
- Credit risk assessment with country-specific discount factors
- GARCH volatility modeling for price variability
- ARIMA time-series forecasting
- Integrated risk-adjusted pricing model

## Features
- **Credit Risk Model**: Assigns discount factors based on buyer credit ratings (AAA to D)
- **Volatility Modeling**: Uses GARCH to capture time-varying volatility in LNG prices
- **Time-Series Forecasting**: ARIMA models for price prediction
- **Integrated Trading Model**: Combines all components for risk-adjusted pricing decisions

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from src.models.lng_trading_model import LNGTradingModel
from src.data.buyer_data import load_buyer_data

# Initialize model
model = LNGTradingModel()

# Load buyer data
buyers = load_buyer_data()

# Run analysis
results = model.analyze_portfolio(buyers)
```

## Project Structure
```
├── src/
│   ├── models/          # Core trading models
│   ├── data/            # Data handling and buyer profiles
│   ├── utils/           # Utility functions
│   └── visualization/   # Charts and dashboards
├── notebooks/           # Jupyter notebooks for analysis
├── tests/              # Unit tests
└── requirements.txt    # Dependencies
```
