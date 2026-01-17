"""
Anapyze: a collection of neuroimaging biomarker tools.

This package exposes:
  - core         (low-level processing utilities)
  - analysis     (statistical routines: two-sample t-tests, correlations)
  - io           (I/O helpers for SPM, CAT12, ADNI, etc.)
"""

from .core import *
from .analysis import *
from .io import *
from .config import config

import logging

# Configure logging
logging.basicConfig(
    level=config.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config.log_file,
    filemode='a'
)

# Create a logger for the package
logger = logging.getLogger(__name__)

__all__ = ['core', 'analysis', 'io', 'config']