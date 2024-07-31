"""
`generate_dummy_data.py`:

A script to generate dummy data for school scheduling.
"""

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


# Dataset size configuration
SMALL_DATASET = {
    "teachers": 10,
    "classes": 15,
    "rooms": 5
}

FULL_DATASET = {
    "teachers": 75,
    "classes": 150,
    "rooms": 30
}

# Set this to True for small dataset, False for full dataset
USE_SMALL_DATASET = True


def get_dataset_size():
    return SMALL_DATASET if USE_SMALL_DATASET else FULL_DATASET


def generate_teachers(num_teachers: int) -> List[Dict]:
    """Generate a list of teacher dictionaries."""
    teachers = []
    for i in range(num_teachers):
        availability = []
        for _ in range(5):  # 5 days
            day_availability = []
            available_hours = random.randint(3, 5)
            for _ in range(8):  # 8 periods
                if available_hours > 0 and random.random() > 0.3:
                    day_availability.append('1')
                    available_hours -= 1
                else:
                    day_availability.append('0')
            availability.append(','.join(day_availability))

        teacher = {
            "ID": f"T{i + 1:03d}",
            "Name": f"Teacher {i + 1}",
            "Subjects": random.sample(list(Subject), random.randint(1, 3)),
            "FullTime": random.choice([True, False]),
            "Availability": ';'.join(availability)
        }
        teachers.append(teacher)
    return teachers


def generate_classes(num_classes: int) -> List[Dict]:
    """Generate a list of class dictionaries."""
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
    """Generate a list of room dictionaries."""
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
    """Generate a list of time slots for a school week."""
    return [(day, period) for day in range(5) for period in range(8)]


def save_to_csv(data: List[Dict], filename: str):
    """Save a list of dictionaries to a CSV file in the data folder."""
    if not data:
        return

    keys = data[0].keys()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, filename)

    try:
        with open(filepath, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        print(f"Successfully saved {filename} to {filepath}")
    except PermissionError:
        print(f"Permission denied: Unable to write to {filepath}")
        print("Please check if you have write permissions for this location.")
    except Exception as e:
        print(f"An error occurred while saving {filename}: {str(e)}")


def main():
    """Main function to generate and save dummy data for school scheduling."""
    dataset_size = get_dataset_size()
    teachers = generate_teachers(dataset_size["teachers"])
    classes = generate_classes(dataset_size["classes"])
    rooms = generate_rooms(dataset_size["rooms"])
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

    print(f"Dummy data generated and saved to CSV files in the 'data' folder.")
    print(f"Dataset size: {'Small' if USE_SMALL_DATASET else 'Full'}")
    print(f"Teachers: {len(teachers)}, Classes: {len(classes)}, Rooms: {len(rooms)}")


if __name__ == "__main__":
    main()
