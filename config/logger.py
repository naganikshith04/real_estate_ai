"""
Logging configuration for Real Estate AI
"""

import logging
import logging.config
from .config import LOGGING_CONFIG

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)

# Create loggers
def get_logger(name):
    """Get a logger with the specified name"""
    return logging.getLogger(name)

# Default logger
logger = get_logger('real_estate_ai')