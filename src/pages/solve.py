"""
`solve.py`:

This module contains the Solve page for the school scheduling system.
"""

import streamlit as st
import time
import threading
import traceback
from src.scheduler_utils import run_scheduler
from src.utils import log_memory_usage


class TimeoutException(Exception):
    pass

def run_with_timeout(func, args, timeout):
    result = [None]
    def worker():
        result[0] = func(*args)

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        raise TimeoutException("Solver timed out")
    return result[0]

def show():
    st.title("Solve")

    if st.session_state.scheduler is None:
        st.warning("Please initialize the scheduler in the Data Input page first.")
        return

    st.header("Solver Settings")
    with st.expander("Objective Weights", expanded=False):
        weights = {
            "gaps": st.slider("Weight for minimizing gaps", 0.0, 1.0, 1.0),
        }

    if st.button("Generate Schedule"):
        with st.spinner("Generating schedule..."):
            try:
                start_time = time.time()
                log_memory_usage()

                try:
                    schedule = run_with_timeout(run_scheduler, (st.session_state.scheduler, weights, 300), 300)
                except TimeoutException:
                    st.error("The solver timed out. Try simplifying the problem or increasing the timeout.")
                    return

                end_time = time.time()
                log_memory_usage()

                if schedule is not None:
                    st.success(f"Schedule generated successfully in {end_time - start_time:.2f} seconds!")
                    st.session_state.schedule = schedule
                    st.session_state.solve_time = end_time - start_time
                else:
                    st.error("Unable to generate a feasible schedule. Please adjust constraints or data.")
                    st.info("Check the console output for more detailed information about the solving process.")
            except Exception as e:
                st.error(f"An error occurred during scheduling: {str(e)}")
                st.code(traceback.format_exc())