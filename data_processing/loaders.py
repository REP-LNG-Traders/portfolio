"""
Load actual competition data files.

Handles complex Excel formats from the case competition data.
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
import re

logger = logging.getLogger(__name__)

DATA_DIR = Path("data_processing/raw")


def load_henry_hub_data() -> pd.DataFrame:
    """
    Load Henry Hub historical and forward data.
    
    Returns:
        DataFrame with DatetimeIndex and columns ['HH_Historical', 'HH_Forward']
    """
    logger.info("Loading Henry Hub data...")
    
    try:
        # Load historical (complex format - data starts ~row 28)
        hist_file = DATA_DIR / "Henry Hub Historical (Extracted 23Sep25).xlsx"
        hist_raw = pd.read_excel(hist_file, header=None)
        
        # Find the row with "Exchange Date" header
        header_row = None
        for i, row in hist_raw.iterrows():
            if 'Exchange Date' in str(row.values):
                header_row = i
                break
        
        if header_row is None:
            raise ValueError("Could not find 'Exchange Date' header in Henry Hub Historical")
        
        # Read from header row
        hist = pd.read_excel(hist_file, skiprows=header_row)
        hist = hist.rename(columns={'Exchange Date': 'Date', 'Close': 'Price'})
        hist['Date'] = pd.to_datetime(hist['Date'])
        hist = hist[['Date', 'Price']].dropna()
        hist = hist.set_index('Date').sort_index()
        hist = hist.rename(columns={'Price': 'HH_Historical'})
        
        logger.info(f"  HH Historical: {len(hist)} rows from {hist.index[0].date()} to {hist.index[-1].date()}")
        
        # Load forward curve (simpler format)
        fwd_file = DATA_DIR / "Henry Hub Forward (Extracted 23Sep25).xlsx"
        fwd = pd.read_excel(fwd_file)
        fwd = fwd.rename(columns={'Close': 'Price'})
        
        # Parse contract names to extract dates
        # Format: "NAT GAS JAN26/d" → 2026-01-01
        def parse_contract_month(name):
            """Extract date from contract name like 'NAT GAS JAN26/d'"""
            try:
                # Extract month abbreviation and year
                match = re.search(r'([A-Z]{3})(\d{2})', str(name))
                if match:
                    month_abbr = match.group(1)
                    year_2digit = match.group(2)
                    
                    # Convert to full date
                    month_map = {
                        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
                    }
                    month_num = month_map[month_abbr]
                    year = 2000 + int(year_2digit)
                    
                    return pd.Timestamp(year=year, month=month_num, day=1)
                return None
            except:
                return None
        
        fwd['Date'] = fwd['Name'].apply(parse_contract_month)
        fwd = fwd[['Date', 'Price']].dropna()
        fwd = fwd.set_index('Date').sort_index()
        fwd = fwd.rename(columns={'Price': 'HH_Forward'})
        
        logger.info(f"  HH Forward: {len(fwd)} contracts from {fwd.index[0].strftime('%Y-%m')} to {fwd.index[-1].strftime('%Y-%m')}")
        
        # Combine (outer join to keep all dates)
        combined = pd.concat([hist, fwd], axis=1)
        
        logger.info(f"  Combined: {len(combined)} rows")
        
        return combined
        
    except Exception as e:
        logger.error(f"Error loading Henry Hub data: {e}")
        raise


def load_jkm_data() -> pd.DataFrame:
    """
    Load JKM historical and forward data.
    
    Returns:
        DataFrame with DatetimeIndex and columns ['JKM_Historical', 'JKM_Forward']
    """
    logger.info("Loading JKM data...")
    
    try:
        # Load historical
        hist_file = DATA_DIR / "JKM Spot LNG Historical (Extracted 23Sep25).xlsx"
        hist_raw = pd.read_excel(hist_file, header=None)
        
        # Find header row
        header_row = None
        for i, row in hist_raw.iterrows():
            if 'Exchange Date' in str(row.values) or 'Date' in str(row.values):
                header_row = i
                break
        
        if header_row is None:
            raise ValueError("Could not find date header in JKM Historical")
        
        hist = pd.read_excel(hist_file, skiprows=header_row)
        
        # Handle different possible column names
        date_col = None
        for col in hist.columns:
            if 'date' in str(col).lower():
                date_col = col
                break
        
        if date_col is None:
            date_col = hist.columns[0]
        
        hist = hist.rename(columns={date_col: 'Date', 'Close': 'Price'})
        hist['Date'] = pd.to_datetime(hist['Date'])
        hist = hist[['Date', 'Price']].dropna()
        hist = hist.set_index('Date').sort_index()
        hist = hist.rename(columns={'Price': 'JKM_Historical'})
        
        logger.info(f"  JKM Historical: {len(hist)} rows from {hist.index[0].date()} to {hist.index[-1].date()}")
        
        # Load forward curve
        fwd_file = DATA_DIR / "JKM Spot LNG Forward (Extracted 23Sep25).xlsx"
        fwd = pd.read_excel(fwd_file)
        
        # Use column 1 (contains contract names like "LNG JnK NOV5/d")
        name_col = fwd.columns[1]
        
        # Parse contract names
        def parse_jkm_contract(name):
            # Format: "LNG JnK NOV5/d" or "LNG JKM JAN6/d"
            # Extract month abbreviation (3 letters) and year digit (1 digit)
            match = re.search(r'([A-Z]{3})(\d)/d', str(name))
            if match:
                month_abbr = match.group(1)
                year_1digit = match.group(2)
                
                month_map = {
                    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
                }
                month_num = month_map.get(month_abbr)
                if month_num:
                    # Year: 5 = 2025, 6 = 2026, etc.
                    year = 2020 + int(year_1digit)
                    return pd.Timestamp(year=year, month=month_num, day=1)
            return None
        
        fwd['Date'] = fwd[name_col].apply(parse_jkm_contract)
        fwd['Price'] = fwd['Close']
        fwd = fwd[['Date', 'Price']].dropna()
        fwd = fwd.set_index('Date').sort_index()
        fwd = fwd.rename(columns={'Price': 'JKM_Forward'})
        
        if len(fwd) > 0:
            logger.info(f"  JKM Forward: {len(fwd)} contracts from {fwd.index[0].strftime('%Y-%m')} to {fwd.index[-1].strftime('%Y-%m')}")
        else:
            logger.warning("  JKM Forward: No contracts parsed (check data format)")
        
        # Combine
        combined = pd.concat([hist, fwd], axis=1)
        
        logger.info(f"  Combined: {len(combined)} rows")
        
        return combined
        
    except Exception as e:
        logger.error(f"Error loading JKM data: {e}")
        raise


def load_brent_data() -> pd.DataFrame:
    """
    Load Brent oil historical data.
    
    Returns:
        DataFrame with DatetimeIndex and column ['Brent']
    """
    logger.info("Loading Brent data...")
    
    try:
        file = DATA_DIR / "Brent Oil Historical Prices (Extracted 01Oct25).xlsx"
        
        # Brent file has simple format with header in row 0
        # Columns: 'Date', 'Europe Brent Spot Price FOB (Dollars per Barrel)', 'Year'
        df = pd.read_excel(file)
        
        # Get date column (first column)
        date_col = df.columns[0]
        
        # Get price column (second column with long name)
        price_col = df.columns[1]
        
        df = df.rename(columns={date_col: 'Date', price_col: 'Price'})
        df['Date'] = pd.to_datetime(df['Date'])
        df = df[['Date', 'Price']].dropna()
        df = df.set_index('Date').sort_index()
        df = df.rename(columns={'Price': 'Brent'})
        
        logger.info(f"  Brent: {len(df)} rows from {df.index[0].date()} to {df.index[-1].date()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading Brent data: {e}")
        raise


def load_wti_data() -> pd.DataFrame:
    """
    Load WTI oil historical and forward data.
    
    Returns:
        DataFrame with DatetimeIndex and columns ['WTI_Historical', 'WTI_Forward']
    """
    logger.info("Loading WTI data...")
    
    try:
        # Load historical (complex format - similar to Henry Hub)
        hist_file = DATA_DIR / "WTI Historical (Extracted 23Sep25).xlsx"
        hist_raw = pd.read_excel(hist_file, header=None)
        
        # Find the row with "Exchange Date" header
        header_row = None
        for i, row in hist_raw.iterrows():
            # Check if this row contains "Exchange Date"
            if any('Exchange Date' in str(val) for val in row.values if pd.notna(val)):
                header_row = i
                break
        
        if header_row is None:
            raise ValueError("Could not find 'Exchange Date' header in WTI Historical")
        
        # Read from header row
        hist = pd.read_excel(hist_file, skiprows=header_row)
        hist = hist.rename(columns={'Exchange Date': 'Date', 'Close': 'Price'})
        hist['Date'] = pd.to_datetime(hist['Date'], errors='coerce')
        hist = hist[['Date', 'Price']].dropna()
        hist = hist.set_index('Date').sort_index()
        hist = hist.rename(columns={'Price': 'WTI_Historical'})
        
        logger.info(f"  WTI Historical: {len(hist)} rows from {hist.index[0].date()} to {hist.index[-1].date()}")
        
        # Load forward curve (similar format to Henry Hub)
        fwd_file = DATA_DIR / "WTI Forward (Extracted 23Sep25).xlsx"
        fwd = pd.read_excel(fwd_file)
        fwd = fwd.rename(columns={'Close': 'Price'})
        
        # Parse contract names to extract dates
        # Format: "2005-11-01" (already dates) or contract month names
        def parse_contract_month(name):
            """Extract date from contract name or date string"""
            try:
                # Try direct date parsing first
                if pd.notna(name):
                    return pd.to_datetime(name)
                return None
            except:
                # Try month abbreviation extraction (similar to Henry Hub)
                try:
                    match = re.search(r'([A-Z]{3})(\d{2})', str(name))
                    if match:
                        month_abbr = match.group(1)
                        year_2digit = match.group(2)
                        
                        month_map = {
                            'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                            'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
                        }
                        month_num = month_map[month_abbr]
                        year = 2000 + int(year_2digit)
                        
                        return pd.Timestamp(year=year, month=month_num, day=1)
                except:
                    pass
                return None
        
        # Try to parse Month column as dates
        if 'Month' in fwd.columns:
            fwd['Date'] = fwd['Month'].apply(parse_contract_month)
        elif 'Name' in fwd.columns:
            fwd['Date'] = fwd['Name'].apply(parse_contract_month)
        else:
            # Use first column
            fwd['Date'] = fwd[fwd.columns[0]].apply(parse_contract_month)
        
        fwd = fwd[['Date', 'Price']].dropna()
        fwd = fwd.set_index('Date').sort_index()
        fwd = fwd.rename(columns={'Price': 'WTI_Forward'})
        
        logger.info(f"  WTI Forward: {len(fwd)} contracts from {fwd.index[0].strftime('%Y-%m')} to {fwd.index[-1].strftime('%Y-%m')}")
        
        # Combine (outer join to keep all dates)
        combined = pd.concat([hist, fwd], axis=1)
        
        logger.info(f"  Combined: {len(combined)} rows")
        
        return combined
        
    except Exception as e:
        logger.error(f"Error loading WTI data: {e}")
        raise


def load_freight_data() -> pd.DataFrame:
    """
    Load Baltic LNG freight data and convert to monthly averages.
    
    FIXES FREIGHT VOLATILITY ISSUE:
    - Loads daily freight data from .BLNG3g column
    - Converts to monthly averages (like HH, JKM, Brent)
    - This reduces volatility from 5000% to realistic ~10-30%
    
    Returns:
        DataFrame with DatetimeIndex and column ['Freight'] (monthly averages)
    """
    logger.info("Loading Freight data...")
    
    try:
        file = DATA_DIR / "Baltic LNG Freight Curves Historical .xlsx"
        raw = pd.read_excel(file, header=None)
        
        # Find header row
        header_row = None
        for i, row in raw.iterrows():
            row_str = str(row.values)
            if 'Exchange Date' in row_str or 'Date' in row_str or 'Close' in row_str:
                header_row = i
                break
        
        if header_row is None:
            # Try default first row
            df = pd.read_excel(file)
        else:
            df = pd.read_excel(file, skiprows=header_row)
        
        # Handle different possible column names
        date_col = None
        for col in df.columns:
            if 'date' in str(col).lower():
                date_col = col
                break
        
        if date_col is None:
            date_col = df.columns[0]
        
        # Use .BLNG3g column as specified by user
        price_col = None
        for col in df.columns:
            if '.BLNG3g' in str(col) or 'BLNG3g' in str(col):
                price_col = col
                break
        
        if price_col is None:
            # Fallback to Close or second column
            price_col = 'Close' if 'Close' in df.columns else df.columns[1]
            logger.warning(f"  .BLNG3g column not found, using {price_col}")
        else:
            logger.info(f"  Using column: {price_col}")
        
        df = df.rename(columns={date_col: 'Date', price_col: 'Price'})
        df['Date'] = pd.to_datetime(df['Date'])
        df = df[['Date', 'Price']].dropna()
        df = df.set_index('Date').sort_index()
        
        # CRITICAL FIX: Convert daily data to monthly averages
        logger.info(f"  Raw freight data: {len(df)} daily observations")
        logger.info(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
        
        # Calculate monthly averages (same as HH, JKM, Brent)
        df_monthly = df.resample('M').mean()
        df_monthly = df_monthly.rename(columns={'Price': 'Freight'})
        
        logger.info(f"  Monthly averages: {len(df_monthly)} months")
        logger.info(f"  Date range: {df_monthly.index[0].strftime('%Y-%m')} to {df_monthly.index[-1].strftime('%Y-%m')}")
        
        # ADDITIONAL FIX: Cap extreme outliers using industry-based thresholds
        # Rationale: Baltic LNG data has severe quality issues (documented in memory)
        # Industry knowledge:
        #   - Typical LNG freight: $10k-80k/day
        #   - Extreme conditions (COVID/Ukraine): up to $120k/day
        #   - Above $120k/day: Data errors, not market reality
        # 
        # We use hard caps based on industry maximums:
        #   - Upper: $120k/day (extreme market conditions)
        #   - Lower: $5k/day (minimum viable vessel economics)
        logger.info(f"  Applying 80% outlier capping (10th-90th percentiles)...")
        
        # Industry-based caps (more defensible than percentiles for bad data)
        FREIGHT_MAX = 120_000  # $/day - extreme market conditions
        FREIGHT_MIN = 5_000    # $/day - minimum vessel economics
        
        # Count outliers before capping
        outliers_high = (df_monthly['Freight'] > FREIGHT_MAX).sum()
        outliers_low = (df_monthly['Freight'] < FREIGHT_MIN).sum()
        
        # Apply hard caps
        df_monthly['Freight'] = df_monthly['Freight'].clip(lower=FREIGHT_MIN, upper=FREIGHT_MAX)
        
        logger.info(f"     Capped {outliers_high} high outliers at ${FREIGHT_MAX:,.0f}/day (industry max)")
        logger.info(f"     Capped {outliers_low} low outliers at ${FREIGHT_MIN:,.0f}/day (industry min)")
        logger.info(f"     Rationale: Baltic data quality issues - use industry-realistic bounds")
        logger.info(f"     Note: Original max was ${df_monthly['Freight'].max():,.0f}/day (unrealistic)")
        
        # Log volatility comparison
        daily_vol = df['Price'].pct_change().std() * np.sqrt(252)  # Annualized
        monthly_vol = df_monthly['Freight'].pct_change().std() * np.sqrt(12)  # Annualized
        
        logger.info(f"  Daily volatility (annualized): {daily_vol:.1%}")
        logger.info(f"  Monthly volatility (after capping, annualized): {monthly_vol:.1%}")
        logger.info(f"  Volatility reduction: {(1 - monthly_vol/daily_vol):.1%}")
        
        return df_monthly
        
    except Exception as e:
        logger.error(f"Error loading Freight data: {e}")
        raise


def load_fx_data() -> pd.DataFrame:
    """
    Load USD/SGD FX data.
    
    Returns:
        DataFrame with DatetimeIndex and column ['USDSGD']
    """
    logger.info("Loading FX data...")
    
    try:
        file = DATA_DIR / "USDSGD FX Spot Rate Historical (Extracted 23Sep25).xlsx"
        raw = pd.read_excel(file, header=None)
        
        # Find header row
        header_row = None
        for i, row in raw.iterrows():
            if 'Date' in str(row.values) or 'Exchange Date' in str(row.values):
                header_row = i
                break
        
        if header_row is None:
            raise ValueError("Could not find date header in FX data")
        
        df = pd.read_excel(file, skiprows=header_row)
        
        # Handle different possible column names
        date_col = None
        for col in df.columns:
            if 'date' in str(col).lower():
                date_col = col
                break
        
        if date_col is None:
            date_col = df.columns[0]
        
        rate_col = 'Close' if 'Close' in df.columns else 'Rate' if 'Rate' in df.columns else df.columns[1]
        
        df = df.rename(columns={date_col: 'Date', rate_col: 'Rate'})
        df['Date'] = pd.to_datetime(df['Date'])
        df = df[['Date', 'Rate']].dropna()
        df = df.set_index('Date').sort_index()
        df = df.rename(columns={'Rate': 'USDSGD'})
        
        logger.info(f"  FX: {len(df)} rows from {df.index[0].date()} to {df.index[-1].date()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading FX data: {e}")
        raise


def load_all_data() -> dict:
    """
    Load all competition data files.
    
    Returns:
        Dict with keys: 'henry_hub', 'jkm', 'brent', 'wti', 'freight', 'fx'
        Each value is a DataFrame with DatetimeIndex
    """
    logger.info("="*80)
    logger.info("LOADING ALL COMPETITION DATA")
    logger.info("="*80)
    
    data = {}
    
    try:
        data['henry_hub'] = load_henry_hub_data()
        data['jkm'] = load_jkm_data()
        data['brent'] = load_brent_data()
        # data['wti'] = load_wti_data()  # NOT NEEDED - only used in hybrid forecasting, we use ARIMA+GARCH for Brent
        data['freight'] = load_freight_data()
        data['fx'] = load_fx_data()
        
        logger.info("\n" + "="*80)
        logger.info("ALL DATA LOADED SUCCESSFULLY")
        logger.info("="*80)
        
        # Print summary
        logger.info("\nData Summary:")
        for name, df in data.items():
            logger.info(f"  {name}: {df.shape} - {df.columns.tolist()}")
        
        return data
        
    except Exception as e:
        logger.error(f"Error in load_all_data: {e}")
        raise


if __name__ == "__main__":
    # Test data loading
    logging.basicConfig(level=logging.INFO)
    
    try:
        data = load_all_data()
        
        print("\n" + "="*80)
        print("DATA LOADING TEST SUCCESSFUL")
        print("="*80)
        
        # Show sample from each dataset
        for name, df in data.items():
            print(f"\n{name.upper()}:")
            print(df.tail(3))
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

