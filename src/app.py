"""
`app.py`:

This module contains the Streamlit app for the school scheduling system.
"""

import sys
import os
import threading
import time

# Ensure the 'src' directory is added to the system path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from scheduler import Scheduler
import utils
import traceback
import logging
from typing import Dict, List, Any
from log_config import logger

from scheduler_utils import run_scheduler

import psutil

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ensure logs from other modules are captured
logging.getLogger("scheduler").setLevel(logging.DEBUG)
logging.getLogger("objectives").setLevel(logging.DEBUG)

class TimeoutException(Exception):
    pass

def log_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    logger.info(f"Memory usage: {mem_info.rss / 1024 / 1024:.2f} MB")

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

def main():
    st.title("School Scheduling System")

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
                "gaps": st.slider("Weight for minimizing gaps", 0.0, 1.0, 1.0),
            }

            if st.button("Generate Schedule"):
                with st.spinner("Generating schedule..."):
                    try:
                        start_time = time.time()
                        log_memory_usage()

                        try:
                            schedule = run_with_timeout(run_scheduler, (scheduler, weights, 300), 300)
                        except TimeoutException:
                            st.error("The solver timed out. Try simplifying the problem or increasing the timeout.")
                            return

                        end_time = time.time()
                        log_memory_usage()

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
                            fig = utils.visualize_teacher_workload(schedule)
                            st.pyplot(fig)

                            # Display statistics
                            st.header("Schedule Statistics")
                            stats = utils.calculate_schedule_statistics(schedule)
                            st.json(stats)

                            # Teacher Utilization
                            st.header("Teacher Utilization")
                            teacher_utilization = utils.calculate_teacher_utilization(schedule, scheduler.data["teachers"], scheduler.data["time_slots"])
                            fig = utils.plot_teacher_utilization(teacher_utilization)
                            st.pyplot(fig)

                            # Class Distribution
                            st.header("Class Distribution")
                            class_distribution = utils.analyze_class_distribution(schedule, scheduler.data["teachers"])
                            fig = utils.plot_class_distribution(class_distribution)
                            st.pyplot(fig)

                            # Teacher Gaps
                            st.header("Teacher Gaps")
                            teacher_gaps = utils.analyze_gaps(schedule, scheduler.data["teachers"])
                            fig = utils.plot_teacher_gaps(teacher_gaps)
                            st.pyplot(fig)

                            # Room Utilization
                            st.header("Room Utilization")
                            room_utilization = utils.calculate_room_utilization(schedule, scheduler.data["rooms"], scheduler.data["time_slots"])
                            fig = utils.plot_room_utilization(room_utilization)
                            st.pyplot(fig)

                            # Subject Balance
                            st.header("Subject Balance")
                            subject_balance = utils.analyze_subject_balance(schedule, scheduler.data["classes"])
                            fig = utils.plot_subject_balance(subject_balance)
                            st.pyplot(fig)

                            # Export option
                            if st.button("Export Schedule to CSV"):
                                utils.export_schedule_to_csv(schedule, "generated_schedule.csv")
                                st.success("Schedule exported to output/generated_schedule.csv")
                        else:
                            st.error("Unable to generate a feasible schedule. Please adjust constraints or data.")
                            st.info("Check the console output for more detailed information about the solving process.")
                    except Exception as e:
                        logger.error(f"An error occurred during scheduling: {str(e)}")
                        st.error(f"An error occurred during scheduling: {str(e)}")
                        st.code(traceback.format_exc())
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            logger.error(traceback.format_exc())
            st.error(f"An error occurred: {str(e)}")
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()