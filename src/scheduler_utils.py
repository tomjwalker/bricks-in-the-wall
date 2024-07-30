"""
`scheduler_utils.py`:

This module contains the function run_scheduler, which runs the scheduler with a timeout. The function is common to
both the Streamlit app and the script to run the scheduler automatically.
"""


import traceback
from typing import Dict, List, Any
from scheduler import Scheduler
from log_config import logger


def run_scheduler(scheduler: Scheduler, weights: Dict[str, float], timeout: int = 300) -> Dict[int, List[Dict[str, Any]]]:
    """Run the scheduler with a timeout."""
    try:
        logger.info("Creating variables")
        scheduler.create_variables()
        logger.info("Applying constraints")
        scheduler.apply_constraints()
        logger.info("Setting objective")
        scheduler.set_objective(weights)
        logger.info(f"Solving (timeout: {timeout} seconds)")
        if scheduler.solve(timeout=timeout):
            logger.info("Solution found")
            return scheduler.get_schedule()
        else:
            logger.info("No solution found")
            return None
    except Exception as e:
        logger.error(f"Error in run_scheduler: {str(e)}")
        logger.error(traceback.format_exc())
        return None
