"""
`constraints.py`:

This module contains functions to implement constraints for the school scheduling problem.
"""

from ortools.linear_solver import pywraplp
from typing import Dict, List, Any, Tuple


def room_capacity_constraint(
    solver: pywraplp.Solver,
    x: Dict[Tuple[str, str, str, Tuple[int, int]], pywraplp.Variable],
    classes: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    time_slots: List[Tuple[int, int]],
    teachers: List[Dict[str, Any]]  # Add teachers as a parameter
) -> List[pywraplp.Constraint]:
    """
    Ensure that room capacity is not exceeded for any time slot.

    Args:
        solver: The OR-Tools solver instance
        x: Decision variables representing the schedule
        classes: List of class dictionaries
        rooms: List of room dictionaries
        time_slots: List of time slot tuples
        teachers: List of teacher dictionaries

    Returns:
        List of room capacity constraints
    """
    constraints = []
    for r in rooms:
        for ts in time_slots:
            constraint = solver.Constraint(0, r["Capacity"])
            for c in classes:
                for t in teachers:  # Iterate over all teachers
                    constraint.SetCoefficient(x.get((t["ID"], c["ID"], r["ID"], ts), 0), c["NumStudents"])
            constraints.append(constraint)
    return constraints


def teacher_availability_constraint(
        solver: pywraplp.Solver,
        x: Dict[Tuple[str, str, str, Tuple[int, int]], pywraplp.Variable],
        teachers: List[Dict[str, Any]],
        classes: List[Dict[str, Any]],
        rooms: List[Dict[str, Any]],
        time_slots: List[Tuple[int, int]]
) -> List[pywraplp.Constraint]:
    """
    Ensure that teachers are only scheduled when they are available.

    Args:
        solver: The OR-Tools solver instance
        x: Decision variables representing the schedule
        teachers: List of teacher dictionaries
        classes: List of class dictionaries
        rooms: List of room dictionaries
        time_slots: List of time slot tuples

    Returns:
        List of teacher availability constraints
    """
    constraints = []
    for t in teachers:
        for ts in time_slots:
            day, period = ts
            if day >= len(t["Availability"]) or period >= len(t["Availability"][day]):
                print(f"Warning: Availability data missing for teacher {t['ID']} at time slot {ts}")
                continue

            if not t["Availability"][day][period]:  # If teacher is not available
                constraint = solver.Constraint(0, 0)
                for c in classes:
                    for r in rooms:
                        constraint.SetCoefficient(x.get((t["ID"], c["ID"], r["ID"], ts), 0), 1)
                constraints.append(constraint)
    return constraints


def one_class_per_teacher_per_period(
    solver: pywraplp.Solver,
    x: Dict[tuple, pywraplp.Variable],
    teachers: List[Dict[str, Any]],
    classes: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    time_slots: List[tuple]
) -> List[pywraplp.Constraint]:
    """
    Ensure that each teacher is assigned to at most one class per time slot.

    Args:
        solver: The OR-Tools solver instance
        x: Decision variables representing the schedule
        teachers: List of teacher dictionaries
        classes: List of class dictionaries
        rooms: List of room dictionaries
        time_slots: List of time slot tuples

    Returns:
        List of constraints
    """
    constraints = []
    for t in teachers:
        for ts in time_slots:
            # For each teacher and time slot, sum of assignments must be <= 1
            constraint = solver.Constraint(0, 1)
            for c in classes:
                for r in rooms:
                    constraint.SetCoefficient(x[t["ID"], c["ID"], r["ID"], ts], 1)
            constraints.append(constraint)
    return constraints


def required_periods_per_class(
    solver: pywraplp.Solver,
    x: Dict[tuple, pywraplp.Variable],
    classes: List[Dict[str, Any]],
    teachers: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    time_slots: List[tuple]
) -> List[pywraplp.Constraint]:
    """
    Ensure that each class is scheduled for the required number of periods per week.

    Args:
        solver: The OR-Tools solver instance
        x: Decision variables representing the schedule
        classes: List of class dictionaries
        teachers: List of teacher dictionaries
        rooms: List of room dictionaries
        time_slots: List of time slot tuples

    Returns:
        List of constraints
    """
    constraints = []
    for c in classes:
        # For each class, sum of assignments must equal required periods
        constraint = solver.Constraint(c["PeriodsPerWeek"], c["PeriodsPerWeek"])
        for t in teachers:
            for r in rooms:
                for ts in time_slots:
                    constraint.SetCoefficient(x[t["ID"], c["ID"], r["ID"], ts], 1)
        constraints.append(constraint)
    return constraints


def apply_all_constraints(
    solver: pywraplp.Solver,
    x: Dict[Tuple[str, str, str, Tuple[int, int]], pywraplp.Variable],
    teachers: List[Dict[str, Any]],
    classes: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    time_slots: List[Tuple[int, int]]
) -> List[pywraplp.Constraint]:
    """
    Apply all defined constraints to the solver.

    Args:
        solver: The OR-Tools solver instance
        x: Decision variables representing the schedule
        teachers: List of teacher dictionaries
        classes: List of class dictionaries
        rooms: List of room dictionaries
        time_slots: List of time slot tuples

    Returns:
        List of all applied constraints
    """
    all_constraints = []
    all_constraints.extend(room_capacity_constraint(solver, x, classes, rooms, time_slots, teachers))
    all_constraints.extend(teacher_availability_constraint(solver, x, teachers, classes, rooms, time_slots))
    all_constraints.extend(one_class_per_teacher_per_period(solver, x, teachers, classes, rooms, time_slots))
    all_constraints.extend(required_periods_per_class(solver, x, classes, teachers, rooms, time_slots))
    # Add calls to any additional constraint functions here
    return all_constraints


# Note: The decision variable x is assumed to be structured as:
# x[teacher_id, class_id, room_id, time_slot] = 1 if the assignment is made, 0 otherwise

# Additional constraints you might consider:
# - Ensuring specific classes are in appropriate room types (e.g., science classes in labs)
# - Limiting the number of classes a teacher can have per day
# - Avoiding back-to-back classes for teachers (if desired)
# - Scheduling certain classes at specific times (e.g., PE always after lunch)
