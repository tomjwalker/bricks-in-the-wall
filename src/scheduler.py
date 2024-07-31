"""
`scheduler.py`:

This module contains the main Scheduler class and related functions for solving
the school scheduling problem using OR-Tools.
"""
import sys
import os

# Ensure the 'src' directory is added to the system path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import logging
import traceback
from ortools.linear_solver import pywraplp
from typing import Dict, List, Any, Tuple
import data_loader
import constraints
from log_config import logger
import objectives
import time

from utils import log_memory_usage
#
# logger = logging.getLogger(__name__)


class Scheduler:
    """
    Main class for setting up and solving the school scheduling problem.
    """

    def __init__(self, data_files: Dict[str, Any]):
        """
        Initialize the Scheduler with data file paths or file-like objects.

        Args:
            data_files (Dict[str, Any]): Dictionary containing file paths or file-like objects for each data type
        """
        logger.info("Initializing Scheduler")
        self.solver = pywraplp.Solver.CreateSolver("CBC")
        self.data = data_loader.load_all_data(**data_files)
        self.x: Dict[Tuple[str, str, str, Tuple[int, int]], pywraplp.Variable] = {}  # Decision variables
        self.solution = None
        logger.info("Scheduler initialized")

    def create_variables(self):
        """
        Create decision variables for the scheduling problem.
        """
        logger.info("Creating decision variables")
        for teacher in self.data["teachers"]:
            for class_ in self.data["classes"]:
                for room in self.data["rooms"]:
                    for time_slot in self.data["time_slots"]:
                        self.x[teacher["ID"], class_["ID"], room["ID"], time_slot] = \
                            self.solver.IntVar(0, 1, f'{teacher["ID"]}_{class_["ID"]}_{room["ID"]}_{time_slot}')
        logger.info(f"Created {len(self.x)} decision variables")

    def apply_constraints(self):
        """
        Apply all constraints to the scheduling problem.
        """
        logger.info("Applying constraints")
        constraints.apply_all_constraints(
            self.solver,
            self.x,
            self.data["teachers"],
            self.data["classes"],
            self.data["rooms"],
            self.data["time_slots"]
        )
        logger.info("Constraints applied")

    def set_objective(self, weights: Dict[str, float]):
        logger.info("Setting objective function")
        log_memory_usage()
        try:
            objective = objectives.combined_objective(
                self.x,
                self.data["teachers"],
                self.data["classes"],
                self.data["rooms"],
                self.data["time_slots"],
                weights
            )
            logger.info("Objective created successfully")
            log_memory_usage()

            try:
                self.solver.Minimize(objective)
                logger.info("Objective function set successfully")
                log_memory_usage()
            except Exception as e:
                logger.error(f"Error setting minimize objective: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise
        except Exception as e:
            logger.error(f"Error setting objective function: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

        logger.info("Objective function setting completed")
        log_memory_usage()

    def solve(self, timeout: int = 300) -> bool:
        logger.info(f"Starting to solve the scheduling problem with a {timeout} second timeout")
        start_time = time.time()
        try:
            # Set a time limit for the solver
            self.solver.set_time_limit(timeout * 1000)  # OR-Tools uses milliseconds

            logger.info("Calling solver.Solve()")
            logger.info(f"Number of variables: {self.solver.NumVariables()}")
            logger.info(f"Number of constraints: {self.solver.NumConstraints()}")

            status = self.solver.Solve()

            logger.info(f"Solver finished with status: {status}")

            end_time = time.time()
            solve_time = end_time - start_time
            logger.info(f"Solve process took {solve_time:.2f} seconds")

            if status == pywraplp.Solver.OPTIMAL:
                logger.info(f"Optimal solution found in {solve_time:.2f} seconds")
                self.solution = {(t, c, r, ts): var.solution_value()
                                 for (t, c, r, ts), var in self.x.items() if var.solution_value() > 0.5}
                return True
            elif status == pywraplp.Solver.FEASIBLE:
                logger.info(f"Feasible solution found in {solve_time:.2f} seconds")
                self.solution = {(t, c, r, ts): var.solution_value()
                                 for (t, c, r, ts), var in self.x.items() if var.solution_value() > 0.5}
                return True
            elif status == pywraplp.Solver.INFEASIBLE:
                logger.warning("Problem is infeasible")
                return False
            elif status == pywraplp.Solver.UNBOUNDED:
                logger.warning("Problem is unbounded")
                return False
            else:
                logger.warning(f"Solving process stopped with status: {status}")
                return False

        except Exception as e:
            logger.error(f"An error occurred during solving: {str(e)}")
            logger.error(traceback.format_exc())
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
