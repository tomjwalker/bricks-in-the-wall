"""
`app.py`:

This module contains the Streamlit app for the school scheduling system.
"""

import sys
import os

# Ensure the 'src' directory is added to the system path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from scheduler import Scheduler
import utils
import traceback
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from log_config import logger


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure logs from other modules are captured
logging.getLogger("scheduler").setLevel(logging.INFO)
logging.getLogger("objectives").setLevel(logging.INFO)


def run_scheduler_with_timeout(scheduler, weights, timeout=300):
    """Run the scheduler with a timeout."""
    with ThreadPoolExecutor() as executor:
        future = executor.submit(run_scheduler, scheduler, weights)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            logger.error("Scheduling process timed out")
            return None


def run_scheduler(scheduler, weights, timeout=300):
    """Run the scheduling process."""
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
def main():
    st.title("School Scheduling System")

    # File upload
    st.header("Data Input")
    teachers_file = st.file_uploader("Upload Teachers CSV", type="csv")
    classes_file = st.file_uploader("Upload Classes CSV", type="csv")
    rooms_file = st.file_uploader("Upload Rooms CSV", type="csv")
    time_slots_file = st.file_uploader("Upload Time Slots CSV", type="csv")

    if all([teachers_file, classes_file, rooms_file, time_slots_file]):
        st.success("All files uploaded successfully!")

        # Initialize scheduler
        data_files = {
            "teachers_file": teachers_file,
            "classes_file": classes_file,
            "rooms_file": rooms_file,
            "time_slots_file": time_slots_file
        }

        try:
            logger.info("Initializing scheduler")
            scheduler = Scheduler(data_files)

            # Objective weights
            st.header("Objective Weights")
            weights = {
                "gaps": st.slider("Weight for minimizing gaps", 0.0, 1.0, 0.5),
                "workload": st.slider("Weight for balancing workload", 0.0, 1.0, 0.3),
                "distribution": st.slider("Weight for optimizing class distribution", 0.0, 1.0, 0.2)
            }

            if st.button("Generate Schedule"):
                with st.spinner("Generating schedule..."):
                    try:
                        start_time = time.time()
                        schedule = run_scheduler(scheduler, weights, timeout=300)  # 5 minutes timeout
                        end_time = time.time()

                        if schedule is not None:
                            st.success(f"Schedule generated successfully in {end_time - start_time:.2f} seconds!")

                            # Display schedule
                            st.header("Generated Schedule")
                            for day, classes in schedule.items():
                                st.subheader(f"Day {day + 1}")
                                df = pd.DataFrame(classes)
                                st.dataframe(df)

                            # Visualize teacher workload
                            st.header("Teacher Workload")
                            utils.visualize_teacher_workload(schedule)
                            st.image("output/teacher_workload.png")

                            # Display statistics
                            st.header("Schedule Statistics")
                            stats = utils.calculate_schedule_statistics(schedule)
                            st.json(stats)

                            # Export option
                            if st.button("Export Schedule to CSV"):
                                utils.export_schedule_to_csv(schedule, "generated_schedule.csv")
                                st.success("Schedule exported to output/generated_schedule.csv")
                        else:
                            st.error("Unable to generate a feasible schedule. Please adjust constraints or data.")
                            st.info(
                                    "Check the console output for more detailed information about the solving process.")
                    except Exception as e:
                        logger.error(f"An error occurred during scheduling: {str(e)}")
                        st.error(f"An error occurred during scheduling: {str(e)}")
                        st.code(traceback.format_exc())
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            st.error("An error occurred:")
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
