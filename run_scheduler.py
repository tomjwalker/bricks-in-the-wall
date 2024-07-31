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

import psutil


def log_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    logger.info(f"Memory usage: {mem_info.rss / 1024 / 1024:.2f} MB")


def main():

    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
        log_memory_usage()
        schedule = run_scheduler(scheduler, weights, timeout=300)  # 5 minutes timeout
        end_time = time.time()
        log_memory_usage()

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

            # Generate and save all visualizations
            fig = utils.visualize_teacher_workload(schedule)
            fig.savefig(os.path.join(output_dir, "teacher_workload.png"))
            print("Teacher workload visualization saved to output/teacher_workload.png")

            teacher_utilization = utils.calculate_teacher_utilization(schedule, scheduler.data["teachers"],
                                                                      scheduler.data["time_slots"])
            fig = utils.plot_teacher_utilization(teacher_utilization)
            fig.savefig(os.path.join(output_dir, "teacher_utilization.png"))
            print("Teacher utilization plot saved to output/teacher_utilization.png")

            class_distribution = utils.analyze_class_distribution(schedule, scheduler.data["teachers"])
            fig = utils.plot_class_distribution(class_distribution)
            fig.savefig(os.path.join(output_dir, "class_distribution.png"))
            print("Class distribution plot saved to output/class_distribution.png")

            teacher_gaps = utils.analyze_gaps(schedule, scheduler.data["teachers"])
            fig = utils.plot_teacher_gaps(teacher_gaps)
            fig.savefig(os.path.join(output_dir, "teacher_gaps.png"))
            print("Teacher gaps plot saved to output/teacher_gaps.png")

            room_utilization = utils.calculate_room_utilization(schedule, scheduler.data["rooms"],
                                                                scheduler.data["time_slots"])
            fig = utils.plot_room_utilization(room_utilization)
            fig.savefig(os.path.join(output_dir, "room_utilization.png"))
            print("Room utilization plot saved to output/room_utilization.png")

            subject_balance = utils.analyze_subject_balance(schedule, scheduler.data["classes"])
            fig = utils.plot_subject_balance(subject_balance)
            fig.savefig(os.path.join(output_dir, "subject_balance.png"))
            print("Subject balance plot saved to output/subject_balance.png")

            # Print additional statistics
            print("Teacher Utilization:", teacher_utilization)
            print("Room Utilization:", room_utilization)
            print("Teacher Gaps:", teacher_gaps)
            print("Subject Balance:", subject_balance)

        else:
            logger.error("Unable to generate a feasible schedule. Please adjust constraints or data.")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.exception("Exception details:")


if __name__ == "__main__":
    main()
