"""
Data Processing Module for LNG Trading Optimization.

This module handles loading, cleaning, validating, and saving LNG market data.
Designed for flexibility to handle various data formats from competition datasets.

Functions:
    load_raw_data: Load Excel files from data/raw/
    clean_price_data: Transform prices to wide format, handle missing values
    calculate_total_costs: Compute total costs per market
    validate_data: Perform data quality checks
    save_processed_data: Save cleaned data as pickle file

Author: Nickolas Chua
Date: 2025-10-15
"""

import logging
import warnings
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime
import pickle

import pandas as pd
import numpy as np

# Import configuration
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    DATA_RAW, DATA_PROCESSED, DATA_FILES, COLUMN_MAPPING, MARKET_MAPPING,
    MARKETS, DATE_FORMAT, MIN_HISTORY_DAYS, MAX_MISSING_PCT,
    FORWARD_FILL_LIMIT_DAYS, DATA_VALIDATION_STRICT, TERMINAL_COSTS,
    VALIDATION_THRESHOLDS, get_market_standard_name,
    DATA_FREQUENCY, ANALYSIS_FREQUENCY, DECISION_FREQUENCY, RESAMPLE_METHOD,
    days_to_periods, periods_to_days
)

# Configure logging for this module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def _convert_to_numeric(series: pd.Series, column_name: str) -> pd.Series:
    """
    Attempt to convert string values to numeric, handling common formats.
    
    Handles:
        - Currency symbols ($, USD, EUR, etc.)
        - Comma separators (1,234.56)
        - European format (1.234,56)
        - Whitespace
    
    Args:
        series: Pandas Series to convert
        column_name: Name of column (for logging)
        
    Returns:
        Series with numeric values
    """
    if pd.api.types.is_numeric_dtype(series):
        return series
    
    logger.info(f"Attempting to convert '{column_name}' from string to numeric...")
    
    # Make a copy to avoid modifying original
    converted = series.copy()
    
    # If already numeric, return as-is
    if pd.api.types.is_numeric_dtype(converted):
        return converted
    
    # Convert to string and clean
    converted = converted.astype(str)
    
    # Remove common currency symbols and text
    converted = converted.str.replace('$', '', regex=False)
    converted = converted.str.replace('USD', '', regex=False)
    converted = converted.str.replace('EUR', '', regex=False)
    converted = converted.str.replace('£', '', regex=False)
    
    # Remove whitespace
    converted = converted.str.strip()
    
    # Try to detect European format (1.234,56)
    # If we see periods used as thousands separator, replace with nothing
    # Then replace comma with period
    if converted.str.contains(',', regex=False).any():
        # Check if format is European (comma as decimal separator)
        sample = converted.dropna().iloc[0] if len(converted.dropna()) > 0 else ""
        if ',' in str(sample) and '.' in str(sample):
            # Both present - likely European format (1.234,56)
            converted = converted.str.replace('.', '', regex=False)
            converted = converted.str.replace(',', '.', regex=False)
        elif ',' in str(sample):
            # Only comma - could be thousands or decimal separator
            # Heuristic: if more than one comma, it's thousands; otherwise decimal
            if str(sample).count(',') > 1:
                converted = converted.str.replace(',', '', regex=False)
            else:
                converted = converted.str.replace(',', '.', regex=False)
    
    # Convert to numeric, coercing errors to NaN
    converted = pd.to_numeric(converted, errors='coerce')
    
    # Log conversion results
    n_converted = converted.notna().sum()
    n_failed = converted.isna().sum() - series.isna().sum()
    
    if n_failed > 0:
        logger.warning(f"Failed to convert {n_failed} values in '{column_name}' to numeric")
    else:
        logger.info(f"Successfully converted {n_converted} values in '{column_name}' to numeric")
    
    return converted


def load_raw_data() -> Dict[str, pd.DataFrame]:
    """
    Load raw LNG market data from Excel files.
    
    Loads three Excel files:
        1. LNG prices by market
        2. Production costs
        3. Freight costs
    
    Handles:
        - Multi-sheet Excel files (tries first sheet)
        - Missing files (graceful error messages)
        - Various Excel formats (.xlsx, .xls)
    
    Returns:
        Dictionary with keys 'prices', 'production', 'freight' containing DataFrames
        
    Raises:
        FileNotFoundError: If required data files are missing
        ValueError: If data files are empty or corrupted
    """
    logger.info("="*70)
    logger.info("LOADING RAW DATA")
    logger.info("="*70)
    
    data = {}
    
    for key, filename in DATA_FILES.items():
        filepath = DATA_RAW / filename
        
        logger.info(f"Loading {key} data from: {filepath}")
        
        try:
            # Check if file exists
            if not filepath.exists():
                error_msg = (
                    f"File not found: {filepath}\n"
                    f"Expected file: {filename}\n"
                    f"Please ensure Excel files are in: {DATA_RAW}\n"
                    f"Run 'python generate_sample_data.py' to create test data"
                )
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # Try to load Excel file
            # First, try reading first sheet
            try:
                df = pd.read_excel(filepath, sheet_name=0, engine='openpyxl')
                logger.info(f"  Loaded from first sheet (index 0)")
            except Exception as e_sheet:
                # If that fails, try without specifying sheet
                try:
                    df = pd.read_excel(filepath, engine='openpyxl')
                    logger.info(f"  Loaded using default settings")
                except Exception as e_default:
                    # If still fails, try to get sheet names for helpful error
                    try:
                        xl_file = pd.ExcelFile(filepath)
                        sheet_names = xl_file.sheet_names
                        error_msg = (
                            f"Failed to read Excel file: {filepath}\n"
                            f"Available sheets: {sheet_names}\n"
                            f"Try specifying correct sheet in config.py\n"
                            f"Original error: {str(e_default)}"
                        )
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    except:
                        error_msg = f"Failed to read Excel file: {filepath}\nError: {str(e_default)}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
            
            # Check if DataFrame is empty
            if df.empty:
                error_msg = f"Loaded DataFrame is empty: {filepath}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Log basic info
            logger.info(f"  Shape: {df.shape}")
            logger.info(f"  Columns: {list(df.columns)}")
            
            data[key] = df
            
        except Exception as e:
            logger.error(f"Failed to load {key} data: {str(e)}")
            raise
    
    logger.info(f"\n[OK] Successfully loaded {len(data)} datasets")
    logger.info("="*70)
    logger.info("")
    
    return data


def clean_price_data(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and transform LNG price data to wide format.
    
    Performs the following operations:
        1. Map column names using COLUMN_MAPPING
        2. Convert date column to datetime
        3. Standardize market names
        4. Handle duplicate entries (average them)
        5. Pivot to wide format (Date index, Market columns)
        6. Sort by date
        7. Handle missing values (limited forward fill)
        8. Filter to configured markets only
    
    Args:
        prices: Raw price DataFrame in long format
        
    Returns:
        Cleaned DataFrame in wide format with DatetimeIndex and market columns
        
    Raises:
        ValueError: If required columns are missing or data is invalid
    """
    logger.info("="*70)
    logger.info("CLEANING PRICE DATA")
    logger.info("="*70)
    
    df = prices.copy()
    
    # Step 1: Map column names
    logger.info("Step 1: Mapping column names...")
    col_map = COLUMN_MAPPING['prices']
    
    # Check if required columns exist (either mapped or original names)
    required_cols = ['date', 'market', 'price']
    missing_cols = []
    
    for col_key in required_cols:
        expected_name = col_map[col_key]
        if expected_name not in df.columns:
            missing_cols.append(f"{col_key} (looking for '{expected_name}')")
    
    if missing_cols:
        error_msg = (
            f"Missing required columns: {missing_cols}\n"
            f"Available columns: {list(df.columns)}\n"
            f"Update COLUMN_MAPPING in config.py to match your data"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Rename to standard names
    df = df.rename(columns={
        col_map['date']: 'Date',
        col_map['market']: 'Market',
        col_map['price']: 'Price'
    })
    
    logger.info(f"  Mapped columns: {col_map}")
    
    # Step 2: Convert date column to datetime
    logger.info("Step 2: Converting dates...")
    try:
        df['Date'] = pd.to_datetime(df['Date'], format=DATE_FORMAT)
    except:
        # Try without format specification (pandas will infer)
        try:
            df['Date'] = pd.to_datetime(df['Date'])
            logger.warning(f"  Date format '{DATE_FORMAT}' didn't work, used automatic parsing")
        except Exception as e:
            error_msg = f"Failed to parse dates: {str(e)}\nSample dates: {df['Date'].head()}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    logger.info(f"  Date range: {df['Date'].min()} to {df['Date'].max()}")
    
    # Step 3: Standardize market names
    logger.info("Step 3: Standardizing market names...")
    original_markets = df['Market'].unique()
    logger.info(f"  Original markets: {list(original_markets)}")
    
    # Try to standardize each market name
    def standardize_market(market_name):
        try:
            return get_market_standard_name(market_name)
        except ValueError:
            # Unknown market
            logger.warning(f"  Unknown market: '{market_name}' - will be filtered out")
            return None
    
    df['Market_Standardized'] = df['Market'].apply(standardize_market)
    
    # Filter out unknown markets
    unknown_count = df['Market_Standardized'].isna().sum()
    if unknown_count > 0:
        logger.warning(f"  Filtering out {unknown_count} rows with unknown markets")
        df = df[df['Market_Standardized'].notna()].copy()
    
    df['Market'] = df['Market_Standardized']
    df = df.drop(columns=['Market_Standardized'])
    
    # Filter to configured markets only
    df = df[df['Market'].isin(MARKETS)].copy()
    logger.info(f"  Standardized to: {MARKETS}")
    logger.info(f"  Remaining rows: {len(df)}")
    
    # Step 4: Convert price to numeric
    logger.info("Step 4: Converting prices to numeric...")
    df['Price'] = _convert_to_numeric(df['Price'], 'Price')
    
    # Step 5: Handle duplicates (same date + market)
    logger.info("Step 5: Checking for duplicates...")
    duplicates = df.duplicated(subset=['Date', 'Market'], keep=False)
    n_duplicates = duplicates.sum()
    
    if n_duplicates > 0:
        logger.warning(f"  Found {n_duplicates} duplicate entries")
        logger.warning(f"  Taking average of duplicate prices for same date+market")
        
        # Group by Date and Market, take mean of Price
        df = df.groupby(['Date', 'Market'], as_index=False)['Price'].mean()
        logger.info(f"  After averaging duplicates: {len(df)} rows")
    else:
        logger.info(f"  No duplicates found")
    
    # Step 6: Pivot to wide format
    logger.info("Step 6: Pivoting to wide format...")
    try:
        df_wide = df.pivot(index='Date', columns='Market', values='Price')
    except Exception as e:
        error_msg = f"Failed to pivot data: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Ensure columns are in config order
    available_markets = [m for m in MARKETS if m in df_wide.columns]
    df_wide = df_wide[available_markets]
    
    logger.info(f"  Shape after pivot: {df_wide.shape}")
    logger.info(f"  Columns: {list(df_wide.columns)}")
    
    # Step 7: Sort by date
    logger.info("Step 7: Sorting by date...")
    df_wide = df_wide.sort_index()
    logger.info(f"  Date range: {df_wide.index.min()} to {df_wide.index.max()}")
    logger.info(f"  Shape before resampling: {df_wide.shape}")
    
    # Step 7.5: Resample if analysis frequency differs from data frequency
    if DATA_FREQUENCY != ANALYSIS_FREQUENCY:
        logger.info(f"Step 7.5: Resampling data...")
        logger.info(f"  From: {DATA_FREQUENCY} (input data)")
        logger.info(f"  To: {ANALYSIS_FREQUENCY} (analysis frequency)")
        logger.info(f"  Method: {RESAMPLE_METHOD}")
        
        # Determine resampling rule
        resample_rule = ANALYSIS_FREQUENCY
        
        # Resample using specified method
        if RESAMPLE_METHOD == 'mean':
            df_wide = df_wide.resample(resample_rule).mean()
        elif RESAMPLE_METHOD == 'median':
            df_wide = df_wide.resample(resample_rule).median()
        elif RESAMPLE_METHOD == 'last':
            df_wide = df_wide.resample(resample_rule).last()
        elif RESAMPLE_METHOD == 'first':
            df_wide = df_wide.resample(resample_rule).first()
        else:
            logger.warning(f"  Unknown RESAMPLE_METHOD '{RESAMPLE_METHOD}', using 'mean'")
            df_wide = df_wide.resample(resample_rule).mean()
        
        logger.info(f"  Shape after resampling: {df_wide.shape}")
        logger.info(f"  Date range: {df_wide.index.min()} to {df_wide.index.max()}")
    else:
        logger.info(f"Step 7.5: No resampling needed (DATA_FREQUENCY == ANALYSIS_FREQUENCY)")
    
    # Step 8: Handle missing values
    logger.info("Step 8: Handling missing values...")
    missing_before = df_wide.isna().sum()
    logger.info(f"  Missing values before cleaning:\n{missing_before}")
    
    if missing_before.sum() > 0:
        # Forward fill with limit (convert days to periods based on frequency)
        forward_fill_periods = days_to_periods(FORWARD_FILL_LIMIT_DAYS, ANALYSIS_FREQUENCY)
        logger.info(f"  Applying forward fill...")
        logger.info(f"    Limit: {FORWARD_FILL_LIMIT_DAYS} days = {forward_fill_periods} periods at {ANALYSIS_FREQUENCY} frequency")
        df_wide = df_wide.ffill(limit=forward_fill_periods)
        
        # Check remaining missing values
        missing_after = df_wide.isna().sum()
        
        if missing_after.sum() > 0:
            logger.warning(f"  Missing values after forward fill:\n{missing_after}")
            logger.warning(f"  NOTE: Forward fill limited to {FORWARD_FILL_LIMIT_DAYS} days ({forward_fill_periods} periods)")
            logger.warning(f"  Consider: 1) Increasing FORWARD_FILL_LIMIT_DAYS in config.py")
            logger.warning(f"            2) Using backfill or interpolation")
            logger.warning(f"            3) Removing rows/columns with missing data")
            
            # For now, drop any remaining NaN rows
            df_wide = df_wide.dropna()
            logger.warning(f"  Dropped rows with remaining NaN. New shape: {df_wide.shape}")
        else:
            logger.info(f"  [OK] All missing values filled")
    else:
        logger.info(f"  No missing values detected")
    
    # Final validation
    if df_wide.empty:
        error_msg = "DataFrame is empty after cleaning!"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info(f"\n[OK] Price data cleaning complete")
    logger.info(f"  Final shape: {df_wide.shape}")
    logger.info(f"  Date range: {df_wide.index.min()} to {df_wide.index.max()}")
    logger.info(f"  Markets: {list(df_wide.columns)}")
    logger.info("="*70)
    logger.info("")
    
    return df_wide


def calculate_total_costs(production: pd.DataFrame, freight: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate total costs per market (production + freight + terminal).
    
    Cost components:
        - Production: Latest value from time series (assuming constant going forward)
        - Freight: Market-specific freight costs
        - Terminal: Market-specific terminal costs (from config)
    
    NOTE: This function uses the MOST RECENT production cost value and assumes
          it remains constant for forecasting. Review this assumption after seeing
          the actual dataset - you may want to forecast production costs separately
          if they show strong trends.
    
    Args:
        production: Production cost DataFrame (Date, Cost_per_MMBtu)
        freight: Freight cost DataFrame (Route, Market, Cost_per_MMBtu)
        
    Returns:
        DataFrame with columns: Market, Production, Freight, Terminal, Total_Cost
    """
    logger.info("="*70)
    logger.info("CALCULATING TOTAL COSTS")
    logger.info("="*70)
    
    # Step 1: Get production cost (most recent value)
    logger.info("Step 1: Extracting production costs...")
    
    prod_df = production.copy()
    
    # Map column names
    col_map = COLUMN_MAPPING['production']
    if col_map['date'] in prod_df.columns:
        prod_df = prod_df.rename(columns={col_map['date']: 'Date'})
    if col_map['cost'] in prod_df.columns:
        prod_df = prod_df.rename(columns={col_map['cost']: 'Cost_per_MMBtu'})
    
    # Convert date to datetime and sort
    prod_df['Date'] = pd.to_datetime(prod_df['Date'])
    prod_df = prod_df.sort_values('Date')
    
    # Convert cost to numeric
    prod_df['Cost_per_MMBtu'] = _convert_to_numeric(prod_df['Cost_per_MMBtu'], 'Cost_per_MMBtu')
    
    # Get most recent production cost
    production_cost = prod_df['Cost_per_MMBtu'].iloc[-1]
    
    logger.info(f"  Production cost time series:")
    logger.info(f"    Date range: {prod_df['Date'].min()} to {prod_df['Date'].max()}")
    logger.info(f"    Mean: ${prod_df['Cost_per_MMBtu'].mean():.2f}/MMBtu")
    logger.info(f"    Latest: ${production_cost:.2f}/MMBtu")
    logger.info(f"  >> USING MOST RECENT VALUE: ${production_cost:.2f}/MMBtu")
    logger.info(f"  >> ASSUMPTION: Production cost remains constant for forecasting")
    logger.info(f"  >> TODO: Review this after seeing dataset - may need to forecast costs")
    
    # Step 2: Get freight costs by market
    logger.info("Step 2: Extracting freight costs...")
    
    freight_df = freight.copy()
    
    # Map column names
    col_map = COLUMN_MAPPING['freight']
    if col_map['market'] in freight_df.columns:
        freight_df = freight_df.rename(columns={col_map['market']: 'Market'})
    if col_map['cost'] in freight_df.columns:
        freight_df = freight_df.rename(columns={col_map['cost']: 'Cost_per_MMBtu'})
    
    # Standardize market names
    freight_df['Market'] = freight_df['Market'].apply(
        lambda x: get_market_standard_name(x) if x in sum(MARKET_MAPPING.values(), []) else None
    )
    freight_df = freight_df[freight_df['Market'].notna()]
    
    # Convert cost to numeric
    freight_df['Cost_per_MMBtu'] = _convert_to_numeric(freight_df['Cost_per_MMBtu'], 'Cost_per_MMBtu')
    
    # If multiple routes per market, take average
    freight_costs = freight_df.groupby('Market')['Cost_per_MMBtu'].mean()
    
    logger.info(f"  Freight costs by market:")
    for market in MARKETS:
        if market in freight_costs.index:
            logger.info(f"    {market}: ${freight_costs[market]:.2f}/MMBtu")
    
    # Step 3: Build total cost table
    logger.info("Step 3: Building total cost table...")
    
    cost_data = []
    
    for market in MARKETS:
        # Production cost (same for all markets)
        prod_cost = production_cost
        
        # Freight cost (market-specific)
        if market in freight_costs.index:
            freight_cost = freight_costs[market]
        else:
            freight_cost = 0.0
            logger.warning(f"  No freight cost found for {market}, using $0.00")
        
        # Terminal cost (from config)
        terminal_cost = TERMINAL_COSTS.get(market, 0.0)
        
        # Total cost
        total_cost = prod_cost + freight_cost + terminal_cost
        
        cost_data.append({
            'Market': market,
            'Production': prod_cost,
            'Freight': freight_cost,
            'Terminal': terminal_cost,
            'Total_Cost': total_cost
        })
    
    costs_df = pd.DataFrame(cost_data)
    
    logger.info(f"\n  Total costs by market:")
    logger.info(f"\n{costs_df.to_string(index=False)}")
    
    logger.info(f"\n[OK] Cost calculation complete")
    logger.info("="*70)
    logger.info("")
    
    return costs_df


def validate_data(prices: pd.DataFrame, costs: pd.DataFrame) -> bool:
    """
    Validate cleaned data for quality and completeness.
    
    Checks:
        1. Required columns present
        2. Sufficient historical data (>= MIN_HISTORY_MONTHS)
        3. No missing values
        4. Price ranges are reasonable
        5. Cost ranges are reasonable
        6. All configured markets present
    
    Behavior controlled by DATA_VALIDATION_STRICT in config:
        - If True: Raise ValueError on any failed check
        - If False: Log warnings and return False (continue execution)
    
    Args:
        prices: Cleaned price DataFrame (wide format)
        costs: Cost DataFrame
        
    Returns:
        True if all validation checks pass, False otherwise
        
    Raises:
        ValueError: If DATA_VALIDATION_STRICT=True and validation fails
    """
    logger.info("="*70)
    logger.info("VALIDATING DATA")
    logger.info("="*70)
    
    validation_passed = True
    issues = []
    
    # Check 1: Required columns in prices
    logger.info("Check 1: Required market columns...")
    missing_markets = [m for m in MARKETS if m not in prices.columns]
    if missing_markets:
        msg = f"Missing markets in price data: {missing_markets}"
        logger.warning(f"  [FAIL] {msg}")
        issues.append(msg)
        validation_passed = False
    else:
        logger.info(f"  [PASS] All markets present: {list(prices.columns)}")
    
    # Check 2: Sufficient historical data
    logger.info("Check 2: Sufficient historical data...")
    n_periods = len(prices)
    
    # Calculate actual days spanned (inclusive of start and end dates)
    if len(prices) > 0:
        date_range_days = (prices.index.max() - prices.index.min()).days + 1
    else:
        date_range_days = 0
    
    # Check against minimum (use >= for inclusive check)
    if date_range_days < MIN_HISTORY_DAYS:
        msg = f"Insufficient history: {date_range_days} days ({n_periods} periods at {ANALYSIS_FREQUENCY} freq, required: >= {MIN_HISTORY_DAYS} days)"
        logger.warning(f"  [FAIL] {msg}")
        issues.append(msg)
        validation_passed = False
    else:
        logger.info(f"  [PASS] {date_range_days} days of data ({n_periods} periods at {ANALYSIS_FREQUENCY} freq, >= {MIN_HISTORY_DAYS} days required)")
    
    # Check 3: No missing values
    logger.info("Check 3: Missing values...")
    missing_count = prices.isna().sum().sum()
    if missing_count > 0:
        msg = f"Found {missing_count} missing values in price data"
        logger.warning(f"  [FAIL] {msg}")
        logger.warning(f"  Missing by market:\n{prices.isna().sum()}")
        issues.append(msg)
        validation_passed = False
    else:
        logger.info(f"  [PASS] No missing values")
    
    # Check 4: Price ranges
    logger.info("Check 4: Price value ranges...")
    price_issues = []
    
    for market in prices.columns:
        market_prices = prices[market].dropna()
        
        # Check for negative prices
        if (market_prices < VALIDATION_THRESHOLDS['min_price']).any():
            n_negative = (market_prices < VALIDATION_THRESHOLDS['min_price']).sum()
            msg = f"{market}: {n_negative} prices below ${VALIDATION_THRESHOLDS['min_price']}"
            price_issues.append(msg)
        
        # Check for unreasonably high prices
        if (market_prices > VALIDATION_THRESHOLDS['max_price']).any():
            n_high = (market_prices > VALIDATION_THRESHOLDS['max_price']).sum()
            msg = f"{market}: {n_high} prices above ${VALIDATION_THRESHOLDS['max_price']}"
            price_issues.append(msg)
        
        # Log price stats
        logger.info(f"  {market}: ${market_prices.min():.2f} - ${market_prices.max():.2f} "
                   f"(mean: ${market_prices.mean():.2f})")
    
    if price_issues:
        msg = "Price range issues: " + "; ".join(price_issues)
        logger.warning(f"  [FAIL] {msg}")
        issues.append(msg)
        validation_passed = False
    else:
        logger.info(f"  [PASS] All prices within reasonable range")
    
    # Check 5: Cost ranges
    logger.info("Check 5: Cost value ranges...")
    cost_issues = []
    
    for _, row in costs.iterrows():
        market = row['Market']
        total_cost = row['Total_Cost']
        
        if total_cost < VALIDATION_THRESHOLDS['min_cost']:
            cost_issues.append(f"{market}: ${total_cost:.2f} below minimum")
        
        if total_cost > VALIDATION_THRESHOLDS['max_cost']:
            cost_issues.append(f"{market}: ${total_cost:.2f} above maximum")
        
        logger.info(f"  {market}: ${total_cost:.2f}/MMBtu")
    
    if cost_issues:
        msg = "Cost range issues: " + "; ".join(cost_issues)
        logger.warning(f"  [FAIL] {msg}")
        issues.append(msg)
        validation_passed = False
    else:
        logger.info(f"  [PASS] All costs within reasonable range")
    
    # Check 6: All markets in both datasets
    logger.info("Check 6: Market consistency...")
    price_markets = set(prices.columns)
    cost_markets = set(costs['Market'])
    
    if price_markets != cost_markets:
        msg = f"Market mismatch - Prices: {price_markets}, Costs: {cost_markets}"
        logger.warning(f"  [FAIL] {msg}")
        issues.append(msg)
        validation_passed = False
    else:
        logger.info(f"  [PASS] Consistent markets across datasets")
    
    # Summary
    logger.info("")
    logger.info("="*70)
    if validation_passed:
        logger.info("[OK] VALIDATION PASSED - Data quality checks successful")
    else:
        logger.warning("[WARNING] VALIDATION FAILED - Issues detected:")
        for i, issue in enumerate(issues, 1):
            logger.warning(f"  {i}. {issue}")
        
        if DATA_VALIDATION_STRICT:
            error_msg = f"Data validation failed with {len(issues)} issue(s). See log for details."
            logger.error(f"  STRICT MODE: Raising error")
            raise ValueError(error_msg)
        else:
            logger.warning(f"  LENIENT MODE: Continuing despite issues (DATA_VALIDATION_STRICT=False)")
    
    logger.info("="*70)
    logger.info("")
    
    return validation_passed


def save_processed_data(data: Dict, filepath: str = None) -> Path:
    """
    Save processed data as pickle file.
    
    Saves data dictionary with metadata including timestamp and version info.
    
    Args:
        data: Dictionary containing processed DataFrames
        filepath: Optional custom filepath. If None, uses default location.
        
    Returns:
        Path to saved file
    """
    logger.info("="*70)
    logger.info("SAVING PROCESSED DATA")
    logger.info("="*70)
    
    if filepath is None:
        filepath = DATA_PROCESSED / 'cleaned_data.pkl'
    else:
        filepath = Path(filepath)
    
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Add metadata
    data_with_metadata = {
        'data': data,
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'markets': MARKETS,
            'frequencies': {
                'data_frequency': DATA_FREQUENCY,
                'analysis_frequency': ANALYSIS_FREQUENCY,
                'decision_frequency': DECISION_FREQUENCY
            },
            'config': {
                'forward_fill_limit_days': FORWARD_FILL_LIMIT_DAYS,
                'validation_strict': DATA_VALIDATION_STRICT,
                'min_history_days': MIN_HISTORY_DAYS
            }
        }
    }
    
    # Save as pickle
    try:
        with open(filepath, 'wb') as f:
            pickle.dump(data_with_metadata, f)
        
        file_size = filepath.stat().st_size / 1024  # KB
        logger.info(f"  [OK] Saved to: {filepath}")
        logger.info(f"  File size: {file_size:.1f} KB")
        logger.info(f"  Timestamp: {data_with_metadata['metadata']['timestamp']}")
        
    except Exception as e:
        error_msg = f"Failed to save processed data: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg)
    
    logger.info("="*70)
    logger.info("")
    
    return filepath


# =============================================================================
# CONVENIENCE FUNCTION FOR COMPLETE PIPELINE
# =============================================================================

def process_all_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run complete data processing pipeline.
    
    Convenience function that:
        1. Loads raw data
        2. Cleans price data
        3. Calculates costs
        4. Validates data
        5. Saves processed data
    
    Returns:
        Tuple of (prices_wide, costs_df)
    """
    # Load
    raw_data = load_raw_data()
    
    # Clean prices
    prices_wide = clean_price_data(raw_data['prices'])
    
    # Calculate costs
    costs_df = calculate_total_costs(raw_data['production'], raw_data['freight'])
    
    # Validate
    validate_data(prices_wide, costs_df)
    
    # Save
    processed_data = {
        'prices': prices_wide,
        'costs': costs_df
    }
    save_processed_data(processed_data)
    
    return prices_wide, costs_df


if __name__ == "__main__":
    # Test the module
    print("Testing data processing module...")
    print()
    
    try:
        prices, costs = process_all_data()
        print("\n" + "="*70)
        print("SUCCESS - Data processing complete!")
        print("="*70)
        print(f"\nPrices shape: {prices.shape}")
        print(f"Costs shape: {costs.shape}")
        print("\nFirst 5 rows of prices:")
        print(prices.head())
        print("\nCosts:")
        print(costs)
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()

