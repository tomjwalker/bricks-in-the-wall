"""
`utils.py`:

This module contains utility functions for the school scheduling project.
These functions provide support for data preprocessing, result visualization,
and other helper tasks.
"""

import os
from typing import Dict, List, Any
import csv
import matplotlib
import matplotlib.pyplot as plt
from collections import defaultdict

import psutil

from log_config import logger

matplotlib.use('TkAgg')


# Configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')


def ensure_dir_exists(directory):
    """Ensure that a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def export_schedule_to_csv(schedule: Dict[int, List[Dict[str, Any]]], filename: str) -> None:
    """
    Export the generated schedule to a CSV file in the output directory.

    Args:
        schedule (Dict[int, List[Dict[str, Any]]]): The schedule to export
        filename (str): The name of the file to save the schedule to
    """
    ensure_dir_exists(OUTPUT_DIR)
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, 'w', newline='') as csvfile:
        fieldnames = ['Day', 'Period', 'Class', 'Teacher', 'Room']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for day, classes in schedule.items():
            for class_ in classes:
                writer.writerow({
                    'Day': day + 1,
                    'Period': class_['period'] + 1,
                    'Class': class_['class'],
                    'Teacher': class_['teacher'],
                    'Room': class_['room']
                })
    print(f"Schedule exported to {filepath}")


def visualize_teacher_workload(schedule: Dict[int, List[Dict[str, Any]]]) -> None:
    """
    Create a bar chart visualizing the workload distribution among teachers.

    Args:
        schedule (Dict[int, List[Dict[str, Any]]]): The generated schedule
    """
    teacher_workload = defaultdict(int)
    for day_schedule in schedule.values():
        for class_ in day_schedule:
            teacher_workload[class_['teacher']] += 1

    teachers = list(teacher_workload.keys())
    workloads = list(teacher_workload.values())

    plt.figure(figsize=(12, 6))
    plt.bar(teachers, workloads)
    plt.title('Teacher Workload Distribution')
    plt.xlabel('Teachers')
    plt.ylabel('Number of Classes')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    ensure_dir_exists(OUTPUT_DIR)
    output_path = os.path.join(OUTPUT_DIR, 'teacher_workload.png')
    plt.savefig(output_path)
    print(f"Teacher workload visualization saved to {output_path}")
    plt.close()


def calculate_schedule_statistics(schedule: Dict[int, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Calculate various statistics about the generated schedule.

    Args:
        schedule (Dict[int, List[Dict[str, Any]]]): The generated schedule

    Returns:
        Dict[str, Any]: A dictionary containing various schedule statistics
    """
    stats = {
        'total_classes': 0,
        'classes_per_day': {},
        'teacher_workload': defaultdict(int),
        'room_utilization': defaultdict(int)
    }

    for day, classes in schedule.items():
        stats['classes_per_day'][day] = len(classes)
        stats['total_classes'] += len(classes)

        for class_ in classes:
            stats['teacher_workload'][class_['teacher']] += 1
            stats['room_utilization'][class_['room']] += 1

    stats['avg_classes_per_day'] = stats['total_classes'] / len(schedule)
    stats['max_teacher_workload'] = max(stats['teacher_workload'].values())
    stats['min_teacher_workload'] = min(stats['teacher_workload'].values())

    return stats


def preprocess_time_slots(time_slots: List[tuple]) -> Dict[int, List[int]]:
    """
    Preprocess time slots into a more usable format.

    Args:
        time_slots (List[tuple]): List of (day, period) tuples

    Returns:
        Dict[int, List[int]]: Dictionary mapping days to lists of periods
    """
    processed_slots = defaultdict(list)
    for day, period in time_slots:
        processed_slots[day].append(period)
    return dict(processed_slots)


if __name__ == "__main__":
    # Example usage of the utility functions
    sample_schedule = {
        0: [{'period': 0, 'teacher': 'Mr. Smith', 'class': 'Math', 'room': 'R101'},
            {'period': 1, 'teacher': 'Ms. Johnson', 'class': 'English', 'room': 'R102'}],
        1: [{'period': 0, 'teacher': 'Mr. Smith', 'class': 'Physics', 'room': 'R103'},
            {'period': 1, 'teacher': 'Ms. Johnson', 'class': 'Literature', 'room': 'R102'}]
    }

    export_schedule_to_csv(sample_schedule, 'sample_schedule.csv')
    visualize_teacher_workload(sample_schedule)
    stats = calculate_schedule_statistics(sample_schedule)
    print("Schedule Statistics:", stats)

    sample_time_slots = [(0, 1), (0, 2), (1, 1), (1, 2), (2, 1), (2, 2)]
    processed_slots = preprocess_time_slots(sample_time_slots)
    print("Processed Time Slots:", processed_slots)


def log_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    logger.info(f"Memory usage: {mem_info.rss / 1024 / 1024:.2f} MB")
