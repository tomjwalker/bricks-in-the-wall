"""
`data_loader.py`:

This module provides functions to load data from CSV files into suitable data structures
for the school scheduling problem.
"""

import csv
from typing import List, Dict, Any, Union
from io import TextIOWrapper, BytesIO
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def ensure_text_mode(file: Union[str, BytesIO, TextIOWrapper]) -> TextIOWrapper:
    """
    Ensure the file is opened in text mode.

    Args:
        file (Union[str, BytesIO, TextIOWrapper]): The file object or path.

    Returns:
        TextIOWrapper: A file object in text mode.
    """
    if isinstance(file, str):
        return open(file, newline="", encoding="utf-8")
    elif isinstance(file, BytesIO):
        return TextIOWrapper(file, encoding="utf-8")
    elif isinstance(file, TextIOWrapper):
        return file
    else:
        raise ValueError("Unsupported file type")


def load_teachers(file: Union[str, BytesIO, TextIOWrapper]) -> List[Dict[str, Any]]:
    """
    Load teacher data from a CSV file.

    Args:
        file (Union[str, BytesIO, TextIOWrapper]): Path to the CSV file or file-like object containing teacher data.

    Returns:
        List[Dict[str, Any]]: List of teacher dictionaries.
    """
    teachers = []
    logger.debug(f"Starting to load teachers from {file}")
    try:
        with ensure_text_mode(file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                logger.debug(f"Processing row: {row}")
                teacher = {
                    "ID": row["ID"],
                    "Name": row["Name"],
                    "Subjects": row["Subjects"].split(","),
                    "FullTime": row["FullTime"].lower() == "true",
                    "Availability": parse_availability(row["Availability"], num_days=5, num_periods=8)
                }
                teachers.append(teacher)
        logger.debug(f"Successfully loaded {len(teachers)} teachers")
    except Exception as e:
        logger.error(f"Error loading teachers: {str(e)}")
        raise
    return teachers


def load_classes(file: Union[str, BytesIO, TextIOWrapper]) -> List[Dict[str, Any]]:
    """
    Load class data from a CSV file.

    Args:
        file (Union[str, BytesIO, TextIOWrapper]): Path to the CSV file or file-like object containing class data.

    Returns:
        List[Dict[str, Any]]: List of class dictionaries.
    """
    classes = []
    logger.debug(f"Starting to load classes from {file}")
    try:
        with ensure_text_mode(file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                logger.debug(f"Processing row: {row}")
                class_ = {
                    "ID": row["ID"],
                    "Subject": row["Subject"],
                    "GradeLevel": int(row["GradeLevel"]),
                    "NumStudents": int(row["NumStudents"]),
                    "PeriodsPerWeek": int(row["PeriodsPerWeek"])
                }
                classes.append(class_)
        logger.debug(f"Successfully loaded {len(classes)} classes")
    except Exception as e:
        logger.error(f"Error loading classes: {str(e)}")
        raise
    return classes


def load_rooms(file: Union[str, BytesIO, TextIOWrapper]) -> List[Dict[str, Any]]:
    """
    Load room data from a CSV file.

    Args:
        file (Union[str, BytesIO, TextIOWrapper]): Path to the CSV file or file-like object containing room data.

    Returns:
        List[Dict[str, Any]]: List of room dictionaries.
    """
    rooms = []
    logger.debug(f"Starting to load rooms from {file}")
    try:
        with ensure_text_mode(file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                logger.debug(f"Processing row: {row}")
                room = {
                    "ID": row["ID"],
                    "Capacity": int(row["Capacity"]),
                    "Type": row["Type"]
                }
                rooms.append(room)
        logger.debug(f"Successfully loaded {len(rooms)} rooms")
    except Exception as e:
        logger.error(f"Error loading rooms: {str(e)}")
        raise
    return rooms


def load_time_slots(file: Union[str, BytesIO, TextIOWrapper]) -> List[tuple]:
    """
    Load time slot data from a CSV file.

    Args:
        file (Union[str, BytesIO, TextIOWrapper]): Path to the CSV file or file-like object containing time slot data.

    Returns:
        List[tuple]: List of time slot tuples.
    """
    time_slots = []
    logger.debug(f"Starting to load time slots from {file}")
    try:
        with ensure_text_mode(file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                logger.debug(f"Processing row: {row}")
                time_slot = (int(row["Day"]), int(row["Period"]))
                time_slots.append(time_slot)
        logger.debug(f"Successfully loaded {len(time_slots)} time slots")
    except Exception as e:
        logger.error(f"Error loading time slots: {str(e)}")
        raise
    return time_slots


def parse_availability(availability_str: str, num_days: int = 5, num_periods: int = 8) -> List[List[bool]]:
    """
    Parse the availability string into a 2D list of booleans.

    Args:
        availability_str (str): String representation of availability.
        num_days (int): Number of days in the schedule.
        num_periods (int): Number of periods per day.

    Returns:
        List[List[bool]]: 2D list representing availability for each day and period.
    """
    logger.debug(f"Parsing availability string: {availability_str}")
    try:
        days = availability_str.split(";")
        availability = []
        for day in days:
            periods = day.split(",")
            day_availability = [slot == "1" for slot in periods]
            # Ensure each day has the correct number of periods
            day_availability += [False] * (num_periods - len(day_availability))
            availability.append(day_availability)

        # Ensure the correct number of days
        while len(availability) < num_days:
            availability.append([False] * num_periods)

        logger.debug(f"Parsed availability: {availability}")
        return availability
    except Exception as e:
        logger.error(f"Error parsing availability: {str(e)}")
        # Return a default availability (all False) if parsing fails
        return [[False for _ in range(num_periods)] for _ in range(num_days)]


def validate_data(teachers: List[Dict[str, Any]], classes: List[Dict[str, Any]],
                  rooms: List[Dict[str, Any]], time_slots: List[tuple]) -> None:
    """
    Validate the loaded data to ensure it meets basic requirements.

    Args:
        teachers (List[Dict[str, Any]]): List of teacher dictionaries.
        classes (List[Dict[str, Any]]): List of class dictionaries.
        rooms (List[Dict[str, Any]]): List of room dictionaries.
        time_slots (List[tuple]): List of time slot tuples.

    Raises:
        ValueError: If any validation check fails.
    """
    logger.debug("Starting data validation")
    if not teachers:
        logger.error("No teachers loaded.")
        raise ValueError("No teachers loaded.")
    if not classes:
        logger.error("No classes loaded.")
        raise ValueError("No classes loaded.")
    if not rooms:
        logger.error("No rooms loaded.")
        raise ValueError("No rooms loaded.")
    if not time_slots:
        logger.error("No time slots loaded.")
        raise ValueError("No time slots loaded.")
    logger.debug("Data validation completed successfully")


def load_all_data(teachers_file: Union[str, BytesIO, TextIOWrapper],
                  classes_file: Union[str, BytesIO, TextIOWrapper],
                  rooms_file: Union[str, BytesIO, TextIOWrapper],
                  time_slots_file: Union[str, BytesIO, TextIOWrapper]) -> Dict[str, Any]:
    """
    Load all necessary data for the school scheduling problem.

    Args:
        teachers_file: Path to the teachers CSV file or file-like object.
        classes_file: Path to the classes CSV file or file-like object.
        rooms_file: Path to the rooms CSV file or file-like object.
        time_slots_file: Path to the time slots CSV file or file-like object.

    Returns:
        Dict[str, Any]: Dictionary containing all loaded data.
    """
    logger.info("Starting to load all data")
    teachers = load_teachers(teachers_file)
    classes = load_classes(classes_file)
    rooms = load_rooms(rooms_file)
    time_slots = load_time_slots(time_slots_file)

    validate_data(teachers, classes, rooms, time_slots)

    data = {
        "teachers": teachers,
        "classes": classes,
        "rooms": rooms,
        "time_slots": time_slots
    }
    logger.info(f"Successfully loaded all data: {len(teachers)} teachers, {len(classes)} classes, "
                f"{len(rooms)} rooms, and {len(time_slots)} time slots")
    return data


if __name__ == "__main__":
    # Example usage
    data = load_all_data("teachers.csv", "classes.csv", "rooms.csv", "time_slots.csv")
    print(f"Loaded {len(data['teachers'])} teachers, {len(data['classes'])} classes, "
          f"{len(data['rooms'])} rooms, and {len(data['time_slots'])} time slots.")
