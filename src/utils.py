"""
`utils.py`:

This module contains utility functions for the school scheduling project.
These functions provide support for data preprocessing, result visualization,
and other helper tasks.
"""

import os
from typing import Dict, List, Any, Tuple
import csv
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from collections import defaultdict
import psutil

matplotlib.use('Agg')

from log_config import logger

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

def calculate_teacher_workload(schedule: Dict[int, List[Dict[str, Any]]]) -> Dict[str, int]:
    """
    Calculate the workload for each teacher based on the schedule.

    Args:
        schedule (Dict[int, List[Dict[str, Any]]]): The generated schedule

    Returns:
        Dict[str, int]: Dictionary of teacher workloads
    """
    teacher_workload = defaultdict(int)
    for day_schedule in schedule.values():
        for class_ in day_schedule:
            teacher_workload[class_['teacher']] += 1
    return dict(teacher_workload)

def visualize_teacher_workload(schedule: Dict[int, List[Dict[str, Any]]]) -> plt.Figure:
    """
    Create a bar chart visualizing the workload distribution among teachers.

    Args:
        schedule (Dict[int, List[Dict[str, Any]]]): The generated schedule

    Returns:
        plt.Figure: The matplotlib figure object
    """
    teacher_workload = calculate_teacher_workload(schedule)
    teachers = list(teacher_workload.keys())
    workloads = list(teacher_workload.values())

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(teachers, workloads)
    ax.set_title('Teacher Workload Distribution')
    ax.set_xlabel('Teachers')
    ax.set_ylabel('Number of Classes')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

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

def log_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    logger.info(f"Memory usage: {mem_info.rss / 1024 / 1024:.2f} MB")

def calculate_teacher_utilization(schedule: Dict[int, List[Dict[str, Any]]], teachers: List[Dict[str, Any]], time_slots: List[Tuple[int, int]]) -> Dict[str, float]:
    """
    Calculate the percentage of available periods each teacher is scheduled to teach.

    Args:
        schedule (Dict[int, List[Dict[str, Any]]]): The generated schedule
        teachers (List[Dict[str, Any]]): List of teacher dictionaries
        time_slots (List[Tuple[int, int]]): List of time slots

    Returns:
        Dict[str, float]: Dictionary of teacher utilization percentages
    """
    utilization = {}
    for teacher in teachers:
        scheduled_periods = sum(1 for day in schedule for class_ in schedule[day] if class_['teacher'] == teacher['Name'])
        total_available_periods = sum(sum(teacher['Availability'][d]) for d in range(len(teacher['Availability'])))
        utilization[teacher['Name']] = (scheduled_periods / total_available_periods) * 100 if total_available_periods else 0
    return utilization

def plot_teacher_utilization(utilization: Dict[str, float]) -> plt.Figure:
    """
    Create a bar chart of teacher utilization.

    Args:
        utilization (Dict[str, float]): Dictionary of teacher utilization percentages

    Returns:
        plt.Figure: The matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(utilization.keys(), utilization.values())
    ax.set_title('Teacher Utilization')
    ax.set_xlabel('Teachers')
    ax.set_ylabel('Utilization (%)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

def analyze_class_distribution(schedule: Dict[int, List[Dict[str, Any]]], teachers: List[Dict[str, Any]]) -> Dict[str, List[int]]:
    """
    Analyze how classes are distributed across the week for each teacher.

    Args:
        schedule (Dict[int, List[Dict[str, Any]]]): The generated schedule
        teachers (List[Dict[str, Any]]): List of teacher dictionaries

    Returns:
        Dict[str, List[int]]: Dictionary of class distribution for each teacher
    """
    distribution = {teacher['Name']: [0] * 5 for teacher in teachers}  # Assuming 5 days
    for day, classes in schedule.items():
        for class_ in classes:
            distribution[class_['teacher']][day] += 1
    return distribution

def plot_class_distribution(distribution: Dict[str, List[int]]) -> plt.Figure:
    """
    Create a stacked bar chart of class distribution across the week for each teacher.

    Args:
        distribution (Dict[str, List[int]]): Dictionary of class distribution for each teacher

    Returns:
        plt.Figure: The matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    bottom = np.zeros(len(distribution))
    for day in range(5):
        values = [dist[day] for dist in distribution.values()]
        ax.bar(distribution.keys(), values, bottom=bottom, label=f'Day {day+1}')
        bottom += values
    ax.set_title('Distribution of Classes Across the Week')
    ax.legend(title='Days')
    ax.set_xlabel('Teachers')
    ax.set_ylabel('Number of Classes')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

def analyze_gaps(schedule: Dict[int, List[Dict[str, Any]]], teachers: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Analyze the gaps in teachers' schedules.

    Args:
        schedule (Dict[int, List[Dict[str, Any]]]): The generated schedule
        teachers (List[Dict[str, Any]]): List of teacher dictionaries

    Returns:
        Dict[str, int]: Dictionary of gap counts for each teacher
    """
    gaps = {teacher['Name']: 0 for teacher in teachers}
    for day, classes in schedule.items():
        day_schedule = {teacher['Name']: [0] * 8 for teacher in teachers}  # Assuming 8 periods
        for class_ in classes:
            day_schedule[class_['teacher']][class_['period']] = 1
        for teacher, periods in day_schedule.items():
            gaps[teacher] += sum(1 for i in range(1, 7) if periods[i] == 0 and periods[i-1] == 1 and periods[i+1] == 1)
    return gaps

def plot_teacher_gaps(teacher_gaps: Dict[str, int]) -> plt.Figure:
    """
    Create a bar chart of gaps in teacher schedules.

    Args:
        teacher_gaps (Dict[str, int]): Dictionary of gap counts for each teacher

    Returns:
        plt.Figure: The matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(teacher_gaps.keys(), teacher_gaps.values())
    ax.set_title('Number of Gaps in Teacher Schedules')
    ax.set_xlabel('Teachers')
    ax.set_ylabel('Number of Gaps')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

def calculate_room_utilization(schedule: Dict[int, List[Dict[str, Any]]], rooms: List[Dict[str, Any]], time_slots: List[Tuple[int, int]]) -> Dict[str, float]:
    """
    Calculate the utilization percentage for each room.

    Args:
        schedule (Dict[int, List[Dict[str, Any]]]): The generated schedule
        rooms (List[Dict[str, Any]]): List of room dictionaries
        time_slots (List[Tuple[int, int]]): List of time slots

    Returns:
        Dict[str, float]: Dictionary of room utilization percentages
    """
    utilization = {room['ID']: 0 for room in rooms}
    total_periods = len(time_slots)
    for day, classes in schedule.items():
        for class_ in classes:
            utilization[class_['room']] += 1
    return {room: (count / total_periods) * 100 for room, count in utilization.items()}

def plot_room_utilization(room_utilization: Dict[str, float]) -> plt.Figure:
    """
    Create a bar chart of room utilization.

    Args:
        room_utilization (Dict[str, float]): Dictionary of room utilization percentages

    Returns:
        plt.Figure: The matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(room_utilization.keys(), room_utilization.values())
    ax.set_title('Room Utilization')
    ax.set_xlabel('Rooms')
    ax.set_ylabel('Utilization (%)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

def analyze_subject_balance(schedule: Dict[int, List[Dict[str, Any]]], classes: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Analyze the distribution of subjects across the week.

    Args:
        schedule (Dict[int, List[Dict[str, Any]]]): The generated schedule
        classes (List[Dict[str, Any]]): List of class dictionaries

    Returns:
        Dict[str, int]: Dictionary of subject counts
    """
    subject_count = {class_['Subject']: 0 for class_ in classes}
    for day, day_classes in schedule.items():
        for class_ in day_classes:
            subject_count[class_['class']] += 1
    return subject_count

def plot_subject_balance(subject_balance: Dict[str, int]) -> plt.Figure:
    """
    Create a bar chart of subject distribution.

    Args:
        subject_balance (Dict[str, int]): Dictionary of subject counts

    Returns:
        plt.Figure: The matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(subject_balance.keys(), subject_balance.values())
    ax.set_title('Distribution of Subjects')
    ax.set_xlabel('Subjects')
    ax.set_ylabel('Number of Classes')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

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

    # Example usage of new functions (you'll need to provide appropriate data for these)
    # teacher_utilization = calculate_teacher_utilization(sample_schedule, teachers, time_slots)
    # plot_teacher_utilization(teacher_utilization)
    # class_distribution = analyze_class_distribution(sample_schedule, teachers)
    # plot_class_distribution(class_distribution)
    # teacher_gaps = analyze_gaps(sample_schedule, teachers)
    # plot_teacher_gaps(teacher_gaps)
    # room_utilization = calculate_room_utilization(sample_schedule, rooms, time_slots)
    # plot_room_utilization(room_utilization)
    # subject_balance = analyze_subject_balance(sample_schedule, classes)
    # plot_subject_balance(subject_balance)