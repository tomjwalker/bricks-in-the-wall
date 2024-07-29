from enum import Enum
import random
import csv
from typing import List, Dict, Tuple
import os


class Subject(Enum):
    """Enumeration of school subjects."""
    MATHS = "Maths"
    SCIENCE = "Science"
    ENGLISH = "English"
    HISTORY = "History"
    ART = "Art"
    MUSIC = "Music"
    PE = "PE"
    COMPUTER_SCIENCE = "Computer Science"


class RoomType(Enum):
    """Enumeration of school-room types."""
    GENERAL = "General"
    SCIENCE_LAB = "Science Lab"
    COMPUTER_LAB = "Computer Lab"
    GYM = "Gym"


def generate_teachers(num_teachers: int) -> List[Dict]:
    """
    Generate a list of teacher dictionaries.

    Args:
        num_teachers (int): The number of teachers to generate.

    Returns:
        List[Dict]: A list of dictionaries containing teacher information.
    """
    teachers = []
    for i in range(num_teachers):
        teacher = {
            "ID": f"T{i+1:03d}",
            "Name": f"Teacher {i+1}",
            "Subjects": random.sample(list(Subject), random.randint(1, 3)),
            "FullTime": random.choice([True, False]),
            "Availability": [random.randint(3, 5) for _ in range(5)]  # Hours available each day
        }
        teachers.append(teacher)
    return teachers


def generate_classes(num_classes: int) -> List[Dict]:
    """
    Generate a list of class dictionaries.

    Args:
        num_classes (int): The number of classes to generate.

    Returns:
        List[Dict]: A list of dictionaries containing class information.
    """
    classes = []
    for i in range(num_classes):
        class_ = {
            "ID": f"C{i+1:03d}",
            "Subject": random.choice(list(Subject)),
            "GradeLevel": random.randint(7, 12),
            "NumStudents": random.randint(20, 35),
            "PeriodsPerWeek": random.randint(3, 5)
        }
        classes.append(class_)
    return classes


def generate_rooms(num_rooms: int) -> List[Dict]:
    """
    Generate a list of room dictionaries.

    Args:
        num_rooms (int): The number of rooms to generate.

    Returns:
        List[Dict]: A list of dictionaries containing room information.
    """
    rooms = []
    for i in range(num_rooms):
        room = {
            "ID": f"R{i+1:03d}",
            "Capacity": random.randint(20, 40),
            "Type": random.choice(list(RoomType))
        }
        rooms.append(room)
    return rooms


def generate_time_slots() -> List[Tuple[int, int]]:
    """
    Generate a list of time slots for a school week.

    Returns:
        List[Tuple[int, int]]: A list of tuples representing (day, period) for each time slot.
    """
    return [(day, period) for day in range(5) for period in range(8)]


def save_to_csv(data: List[Dict], filename: str):
    """
    Save a list of dictionaries to a CSV file in the data folder.

    Args:
        data (List[Dict]): The data to be saved.
        filename (str): The name of the file to save the data to.
    """
    if not data:
        return
    keys = data[0].keys()
    os.makedirs('../data', exist_ok=True)  # Ensure the data folder exists
    filepath = os.path.join('../data', filename)
    with open(filepath, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def main():
    """
    Main function to generate and save dummy data for school scheduling.
    """
    teachers = generate_teachers(75)
    classes = generate_classes(150)
    rooms = generate_rooms(30)
    time_slots = generate_time_slots()

    # Convert Enum values to strings before saving
    for teacher in teachers:
        teacher['Subjects'] = [subject.value for subject in teacher['Subjects']]
    for class_ in classes:
        class_['Subject'] = class_['Subject'].value
    for room in rooms:
        room['Type'] = room['Type'].value

    save_to_csv(teachers, 'teachers.csv')
    save_to_csv(classes, 'classes.csv')
    save_to_csv(rooms, 'rooms.csv')
    save_to_csv([{"Day": day, "Period": period} for day, period in time_slots], 'time_slots.csv')

    print("Dummy data generated and saved to CSV files in the 'data' folder.")


if __name__ == "__main__":
    main()
