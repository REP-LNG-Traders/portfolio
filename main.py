"""
LNG Trading Optimization System - Main Entry Point

Simple entry point for the LNG trading optimization system.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import and run the main optimization
from main_optimization import main

if __name__ == "__main__":
    main()
