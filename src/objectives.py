"""
This module contains functions to implement objective components for the school scheduling problem.

The three main objectives are:
1. Minimize gaps in teachers' schedules.
2. Balance workload across teachers.
3. Optimize distribution of classes.
"""

from ortools.linear_solver import pywraplp
from typing import Dict, List, Any, Tuple


def minimize_teacher_gaps(
        x: Dict[Tuple[str, str, str, Tuple[int, int]], pywraplp.Variable],
        teachers: List[Dict[str, Any]],
        classes: List[Dict[str, Any]],
        rooms: List[Dict[str, Any]],
        time_slots: List[Tuple[int, int]]  # Included for consistency with other functions
) -> pywraplp.Variable:
    """
    Implement objective: minimize gaps in teachers' schedules.

    This function creates an optimization objective to minimize the total number
    of gaps in all teachers' schedules across the week.

    Args:
        x: Decision variables representing the schedule
        teachers: List of teacher dictionaries
        classes: List of class dictionaries
        rooms: List of room dictionaries
        time_slots: List of time slot tuples (not directly used in this function)

    Returns:
        Objective expression representing total gaps
    """
    solver = pywraplp.Solver.CreateSolver('SCIP')

    total_gaps = solver.IntVar(0, solver.infinity(), 'total_gaps')

    gap_constraints = []
    for t in teachers:
        for d in range(5):  # Assuming 5 days in a week
            teaching_periods = [
                solver.Sum([x.get((t['ID'], c['ID'], r['ID'], (d, p)), 0)
                            for c in classes for r in rooms])
                for p in range(8)  # Assuming 8 periods per day
            ]

            for p in range(1, 7):
                gap = solver.IntVar(0, 1, f'gap_{t["ID"]}_{d}_{p}')
                gap_constraints.extend([
                    gap >= teaching_periods[p - 1] + teaching_periods[p + 1] - 1,
                    gap <= 1 - teaching_periods[p],
                    gap <= teaching_periods[p - 1],
                    gap <= teaching_periods[p + 1]
                ])

    solver.Add(total_gaps == solver.Sum(gap_constraints))

    return total_gaps


def balance_workload(
        x: Dict[Tuple[str, str, str, Tuple[int, int]], pywraplp.Variable],
        teachers: List[Dict[str, Any]],
        classes: List[Dict[str, Any]],
        rooms: List[Dict[str, Any]],
        time_slots: List[Tuple[int, int]]
) -> pywraplp.Variable:
    """
    Implement objective: balance workload across teachers.

    This function creates an optimization objective to balance the teaching workload
    across all teachers. It aims to minimize the difference between the teacher with
    the most classes and the teacher with the fewest classes.

    Args:
        x: Decision variables representing the schedule
        teachers: List of teacher dictionaries
        classes: List of class dictionaries
        rooms: List of room dictionaries
        time_slots: List of time slot tuples

    Returns:
        Objective expression representing workload imbalance
    """
    solver = pywraplp.Solver.CreateSolver('SCIP')

    min_classes = solver.IntVar(0, len(time_slots), 'min_classes')
    max_classes = solver.IntVar(0, len(time_slots), 'max_classes')

    workload_difference = solver.IntVar(0, len(time_slots), 'workload_difference')

    for t in teachers:
        teacher_classes = solver.Sum([
            x.get((t['ID'], c['ID'], r['ID'], ts), 0)
            for c in classes
            for r in rooms
            for ts in time_slots
        ])

        solver.Add(min_classes <= teacher_classes)
        solver.Add(max_classes >= teacher_classes)

    solver.Add(workload_difference == max_classes - min_classes)

    return workload_difference


def optimize_class_distribution(
    x: Dict[Tuple[str, str, str, Tuple[int, int]], pywraplp.Variable],
    classes: List[Dict[str, Any]],
    teachers: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    time_slots: List[Tuple[int, int]]
) -> pywraplp.Variable:
    """
    Implement objective: optimize distribution of classes throughout the week.

    This function creates an optimization objective to ensure a good distribution
    of classes throughout the week. It aims to:
    1. Avoid scheduling the same subject for a class multiple times in a day
    2. Distribute subjects evenly across the week for each class

    Args:
        x: Decision variables representing the schedule
        classes: List of class dictionaries
        teachers: List of teacher dictionaries
        rooms: List of room dictionaries
        time_slots: List of time slot tuples

    Returns:
        Objective expression representing class distribution quality
    """
    solver = pywraplp.Solver.CreateSolver('SCIP')

    distribution_quality = solver.IntVar(0, solver.infinity(), 'distribution_quality')
    same_day_penalty = solver.IntVar(0, solver.infinity(), 'same_day_penalty')
    uneven_distribution_penalty = solver.IntVar(0, solver.infinity(), 'uneven_distribution_penalty')

    days = set(day for day, _ in time_slots)
    periods_per_day = len(set(period for _, period in time_slots))

    for class_ in classes:
        for day in days:
            day_count = solver.Sum([
                x.get((t['ID'], class_['ID'], r['ID'], (day, period)), 0)
                for t in teachers
                for r in rooms
                for period in range(periods_per_day)
            ])

            solver.Add(same_day_penalty >= day_count - 1)

        day_counts = [
            solver.Sum([
                x.get((t['ID'], class_['ID'], r['ID'], (day, period)), 0)
                for t in teachers
                for r in rooms
                for period in range(periods_per_day)
            ])
            for day in days
        ]

        max_day_count = solver.Max(day_counts)
        min_day_count = solver.Min(day_counts)
        solver.Add(uneven_distribution_penalty >= max_day_count - min_day_count)

    solver.Add(distribution_quality == same_day_penalty + uneven_distribution_penalty)

    return distribution_quality


def combined_objective(
    x: Dict[Tuple[str, str, str, Tuple[int, int]], pywraplp.Variable],
    teachers: List[Dict[str, Any]],
    classes: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    time_slots: List[Tuple[int, int]],
    weights: Dict[str, float]
) -> pywraplp.Variable:
    """
    Combine individual objectives into a single objective function.

    This function creates a weighted sum of the three individual objectives:
    1. Minimize gaps in teachers' schedules
    2. Balance workload across teachers
    3. Optimize distribution of classes

    Args:
        x: Decision variables representing the schedule
        teachers: List of teacher dictionaries
        classes: List of class dictionaries
        rooms: List of room dictionaries
        time_slots: List of time slot tuples
        weights: Dictionary of weights for each objective component

    Returns:
        Combined objective expression to be minimized
    """
    solver = pywraplp.Solver.CreateSolver('SCIP')

    teacher_gaps = minimize_teacher_gaps(x, teachers, classes, rooms, time_slots)
    workload_imbalance = balance_workload(x, teachers, classes, rooms, time_slots)
    class_distribution = optimize_class_distribution(x, classes, teachers, rooms, time_slots)

    combined_obj = solver.NumVar(0, solver.infinity(), 'combined_objective')

    solver.Add(combined_obj ==
               weights['gaps'] * teacher_gaps +
               weights['workload'] * workload_imbalance +
               weights['distribution'] * class_distribution)

    return combined_obj
