"""
This module contains the main Scheduler class and related functions for solving
the school scheduling problem using OR-Tools.
"""

from ortools.linear_solver import pywraplp
from typing import Dict, List, Any

import data_loader
import constraints
import objectives


class Scheduler:
    """
    Main class for setting up and solving the school scheduling problem.
    """

    def __init__(self, data_files: Dict[str, str]):
        """
        Initialize the Scheduler with data file paths.

        Args:
            data_files (Dict[str, str]): Dictionary containing file paths for each data type
        """
        self.solver = pywraplp.Solver.CreateSolver("SCIP")
        self.data = data_loader.load_all_data(**data_files)
        self.x: Dict[Any, pywraplp.Variable] = {}  # Decision variables
        self.solution = None

    def create_variables(self):
        """
        Create decision variables for the scheduling problem.
        """
        for teacher in self.data["teachers"]:
            for class_ in self.data["classes"]:
                for room in self.data["rooms"]:
                    for time_slot in self.data["time_slots"]:
                        self.x[teacher["ID"], class_["ID"], room["ID"], time_slot] = \
                            self.solver.IntVar(0, 1, f'{teacher["ID"]}_{class_["ID"]}_{room["ID"]}_{time_slot}')

    def apply_constraints(self):
        """
        Apply all constraints to the scheduling problem.
        """
        constraints.apply_all_constraints(
            self.solver,
            self.x,
            self.data["teachers"],
            self.data["classes"],
            self.data["rooms"],
            self.data["time_slots"]
        )

    def set_objective(self, weights: Dict[str, float]):
        """
        Set the objective function for the scheduling problem.

        Args:
            weights (Dict[str, float]): Weights for each component of the objective function
        """
        objective = objectives.combined_objective(
            self.x,
            self.data["teachers"],
            self.data["classes"],
            self.data["rooms"],
            self.data["time_slots"],
            weights
        )
        self.solver.Minimize(objective)

    def solve(self):
        """
        Solve the scheduling problem.

        Returns:
            bool: True if a solution was found, False otherwise
        """
        status = self.solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            self.solution = {(t, c, r, ts): var.solution_value()
                             for (t, c, r, ts), var in self.x.items() if var.solution_value() > 0.5}
            return True
        return False

    def get_schedule(self) -> Dict[int, List[Dict[str, Any]]]:
        """
        Get the computed schedule in a structured format.

        Returns:
            Dict[int, List[Dict[str, Any]]]: Schedule organized by day and period
        """
        if not self.solution:
            raise ValueError("No solution available. Please run solve() first.")

        schedule = {day: [] for day in range(5)}  # Assuming 5 days
        for (teacher_id, class_id, room_id, (day, period)), value in self.solution.items():
            if value > 0.5:
                teacher = next(t for t in self.data["teachers"] if t["ID"] == teacher_id)
                class_ = next(c for c in self.data["classes"] if c["ID"] == class_id)
                room = next(r for r in self.data["rooms"] if r["ID"] == room_id)

                schedule[day].append({
                    "period": period,
                    "teacher": teacher["Name"],
                    "class": class_["Subject"],
                    "room": room["ID"]
                })

        return schedule

    def print_schedule(self):
        """
        Print the computed schedule in a readable format.
        """
        schedule = self.get_schedule()
        for day, classes in schedule.items():
            print(f"Day {str(day + 1)}:")
            for class_ in sorted(classes, key=lambda x: x["period"]):
                print(f"  Period {class_['period'] + 1}: {class_['class']} - "
                      f"Teacher: {class_['teacher']}, Room: {class_['room']}")
            print()


def main():
    """
    Main function to run the school scheduling process.
    """
    data_files = {
        "teachers_file": "data/teachers.csv",
        "classes_file": "data/classes.csv",
        "rooms_file": "data/rooms.csv",
        "time_slots_file": "data/time_slots.csv"
    }

    weights = {
        "gaps": 1.0,
        "workload": 0.5,
        "distribution": 0.7
    }

    scheduler = Scheduler(data_files)
    scheduler.create_variables()
    scheduler.apply_constraints()
    scheduler.set_objective(weights)

    if scheduler.solve():
        print("Schedule found successfully!")
        scheduler.print_schedule()
    else:
        print("No feasible schedule found.")


if __name__ == "__main__":
    main()
