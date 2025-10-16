"""Basic test to check imports work."""

try:
    print("Testing imports...")
    
    # Test config imports
    from config.constants import CARGO_CONTRACT
    print("✓ Config constants imported")
    
    from config.settings import VOLUME_FLEXIBILITY_CONFIG
    print("✓ Config settings imported")
    
    from config.paths import DATA_RAW
    print("✓ Config paths imported")
    
    # Test data imports
    from data_processing.loaders import load_all_data
    print("✓ Data loaders imported")
    
    # Test models imports
    from models.optimization import CargoPnLCalculator
    print("✓ Models optimization imported")
    
    from models.forecasting import prepare_forecasts_arima_garch
    print("✓ Models forecasting imported")
    
    from models.risk_management import HenryHubHedge
    print("✓ Models risk management imported")
    
    print("\n🎉 ALL IMPORTS WORKING!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
