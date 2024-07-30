"""
`run_scheduler.py`:

This module contains the main function to run the school scheduling process end-to-end automatically
(without user input).
"""


import sys
import os
import time
import logging

# Ensure the 'src' directory is added to the system path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.scheduler import Scheduler
from src import utils
from src.log_config import logger
from src.scheduler_utils import run_scheduler


def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Set up data files
    data_files = {
        "teachers_file": "./data/teachers.csv",
        "classes_file": "./data/classes.csv",
        "rooms_file": "./data/rooms.csv",
        "time_slots_file": "./data/time_slots.csv"
    }

    # Set up weights
    weights = {
        "gaps": 1.0
    }

    try:
        logger.info("Initializing scheduler")
        scheduler = Scheduler(data_files)

        logger.info("Running scheduler")
        start_time = time.time()
        schedule = run_scheduler(scheduler, weights, timeout=300)  # 5 minutes timeout
        end_time = time.time()

        if schedule is not None:
            logger.info(f"Schedule generated successfully in {end_time - start_time:.2f} seconds!")

            # Print schedule
            for day, classes in schedule.items():
                print(f"Day {day + 1}:")
                for class_ in classes:
                    print(f"  Period {class_['period'] + 1}: {class_['class']} - "
                          f"Teacher: {class_['teacher']}, Room: {class_['room']}")
                print()

            # Calculate and print statistics
            stats = utils.calculate_schedule_statistics(schedule)
            print("Schedule Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")

            # Export schedule to CSV
            utils.export_schedule_to_csv(schedule, "generated_schedule.csv")
            print("Schedule exported to output/generated_schedule.csv")

            # Generate and save teacher workload visualization
            utils.visualize_teacher_workload(schedule)
            print("Teacher workload visualization saved to output/teacher_workload.png")

        else:
            logger.error("Unable to generate a feasible schedule. Please adjust constraints or data.")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.exception("Exception details:")


if __name__ == "__main__":
    main()
