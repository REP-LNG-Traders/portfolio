"""
File paths and directory configuration.
"""

from pathlib import Path

# =============================================================================
# PROJECT PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS_MODELS = PROJECT_ROOT / "outputs" / "models"
OUTPUTS_RESULTS = PROJECT_ROOT / "outputs" / "results"
OUTPUTS_FIGURES = PROJECT_ROOT / "outputs" / "figures"
OUTPUTS_SUBMISSION = PROJECT_ROOT / "outputs" / "submission"
OUTPUTS_DIAGNOSTICS = PROJECT_ROOT / "outputs" / "diagnostics"
