"""
`log_config.py`:

This module contains the configuration for logging in the school scheduling system.
"""


import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure logs from other modules are captured
logging.getLogger("scheduler").setLevel(logging.INFO)
logging.getLogger("objectives").setLevel(logging.INFO)
