"""
`objectives.py`:

This module contains functions to implement objective components for the school scheduling problem.

The three main objectives are:
1. Minimize gaps in teachers' schedules.
2. Balance workload across teachers.
3. Optimize distribution of classes.
"""


import sys
import os

# Ensure the 'src' directory is added to the system path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import traceback
from ortools.linear_solver import pywraplp
from typing import Dict, List, Any, Tuple

from log_config import logger
from utils import log_memory_usage


def minimize_teacher_gaps(
        x: Dict[Tuple[str, str, str, Tuple[int, int]], pywraplp.Variable],
        teachers: List[Dict[str, Any]],
        classes: List[Dict[str, Any]],
        rooms: List[Dict[str, Any]],
        time_slots: List[Tuple[int, int]]
) -> pywraplp.Variable:
    """
    Implement objective: minimize gaps in teachers' schedules.
    """
    logger.info("Starting minimize_teacher_gaps calculation")
    log_memory_usage()
    solver = pywraplp.Solver.CreateSolver('SCIP')

    try:
        logger.debug("Creating total_gaps variable")
        total_gaps = solver.IntVar(0, solver.infinity(), 'total_gaps')

        gap_vars = []
        logger.info(f"Processing {len(teachers)} teachers")
        for i, t in enumerate(teachers):
            logger.debug(f"Processing teacher {i + 1}/{len(teachers)}: {t['ID']}")
            for d in range(5):  # Assuming 5 days in a week
                logger.debug(f"Processing day {d + 1} for teacher {t['ID']}")
                try:
                    teaching_periods = [
                        solver.Sum([x.get((t['ID'], c['ID'], r['ID'], (d, p)), 0)
                                    for c in classes for r in rooms])
                        for p in range(8)  # Assuming 8 periods per day
                    ]
                    logger.debug(f"Created teaching_periods for day {d + 1}, teacher {t['ID']}")
                except Exception as e:
                    logger.error(f"Error creating teaching_periods: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    raise

                for p in range(1, 7):
                    try:
                        gap = solver.IntVar(0, 1, f'gap_{t["ID"]}_{d}_{p}')
                        solver.Add(gap >= teaching_periods[p - 1] + teaching_periods[p + 1] - 1)
                        solver.Add(gap <= 1 - teaching_periods[p])
                        solver.Add(gap <= teaching_periods[p - 1])
                        solver.Add(gap <= teaching_periods[p + 1])
                        gap_vars.append(gap)
                        logger.debug(
                            f"Created gap variable and constraints for period {p}, day {d + 1}, teacher {t['ID']}")
                    except Exception as e:
                        logger.error(f"Error creating gap variable or constraints: {str(e)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        raise

            # Log memory usage after processing each teacher
            log_memory_usage()

        logger.debug("Adding total_gaps constraint")
        try:
            solver.Add(total_gaps == solver.Sum(gap_vars))
            logger.debug("total_gaps constraint added successfully")
        except Exception as e:
            logger.error(f"Error adding total_gaps constraint: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

        logger.info("Finished minimize_teacher_gaps calculation")
        log_memory_usage()
        return total_gaps
    except Exception as e:
        logger.error(f"Error in minimize_teacher_gaps: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


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
    logger.info("Starting balance_workload calculation")
    solver = pywraplp.Solver.CreateSolver('SCIP')

    min_classes = solver.IntVar(0, len(time_slots), 'min_classes')
    max_classes = solver.IntVar(0, len(time_slots), 'max_classes')

    workload_difference = solver.IntVar(0, len(time_slots), 'workload_difference')

    for t in teachers:
        logger.debug(f"Processing teacher {t['ID']}")
        teacher_classes = solver.Sum([
            x.get((t['ID'], c['ID'], r['ID'], ts), 0)
            for c in classes
            for r in rooms
            for ts in time_slots
        ])

        solver.Add(min_classes <= teacher_classes)
        solver.Add(max_classes >= teacher_classes)

    solver.Add(workload_difference == max_classes - min_classes)
    logger.info("Finished balance_workload calculation")
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
    """
    logger.info("Starting optimize_class_distribution calculation")
    solver = pywraplp.Solver.CreateSolver('SCIP')

    distribution_quality = solver.IntVar(0, solver.infinity(), 'distribution_quality')
    same_day_penalty = solver.IntVar(0, solver.infinity(), 'same_day_penalty')
    uneven_distribution_penalty = solver.IntVar(0, solver.infinity(), 'uneven_distribution_penalty')

    days = set(day for day, _ in time_slots)
    periods_per_day = len(set(period for _, period in time_slots))

    logger.info(f"Processing {len(classes)} classes")
    for i, class_ in enumerate(classes):
        logger.debug(f"Processing class {i + 1}/{len(classes)}: {class_['ID']}")

        for day in days:
            logger.debug(f"Processing day {day} for class {class_['ID']}")
            day_count = solver.Sum([
                x.get((t['ID'], class_['ID'], r['ID'], (day, period)), 0)
                for t in teachers
                for r in rooms
                for period in range(periods_per_day)
            ])
            solver.Add(same_day_penalty >= day_count - 1)

        logger.debug(f"Calculating day counts for class {class_['ID']}")
        day_counts = [
            solver.Sum([
                x.get((t['ID'], class_['ID'], r['ID'], (day, period)), 0)
                for t in teachers
                for r in rooms
                for period in range(periods_per_day)
            ])
            for day in days
        ]

        max_day_count = solver.IntVar(0, solver.infinity(), f'max_day_count_{class_["ID"]}')
        min_day_count = solver.IntVar(0, solver.infinity(), f'min_day_count_{class_["ID"]}')

        for day_count in day_counts:
            solver.Add(max_day_count >= day_count)
            solver.Add(min_day_count <= day_count)

        solver.Add(uneven_distribution_penalty >= max_day_count - min_day_count)

    logger.debug("Setting final distribution quality constraint")
    solver.Add(distribution_quality == same_day_penalty + uneven_distribution_penalty)

    logger.info("Finished optimize_class_distribution calculation")
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
    """
    logger.info("Starting combined_objective calculation")
    log_memory_usage()
    solver = pywraplp.Solver.CreateSolver('SCIP')

    try:
        logger.info("Calculating teacher_gaps")
        teacher_gaps = minimize_teacher_gaps(x, teachers, classes, rooms, time_slots)
        logger.info(f"Teacher gaps objective value: {teacher_gaps}")
        log_memory_usage()

        logger.info("Calculating workload_imbalance")
        workload_imbalance = balance_workload(x, teachers, classes, rooms, time_slots)
        logger.info(f"Workload imbalance objective value: {workload_imbalance}")
        log_memory_usage()

        logger.info("Calculating class_distribution")
        class_distribution = optimize_class_distribution(x, classes, teachers, rooms, time_slots)
        logger.info(f"Class distribution objective value: {class_distribution}")
        log_memory_usage()

        logger.info("Creating combined objective variable")
        combined_obj = solver.NumVar(0, solver.infinity(), 'combined_objective')
        log_memory_usage()

        logger.info("Combining objectives")
        logger.debug(
            f"Weights: gaps={weights['gaps']}, workload={weights['workload']}, distribution={weights['distribution']}")

        try:
            combined_expression = (
                    weights['gaps'] * teacher_gaps +
                    weights['workload'] * workload_imbalance +
                    weights['distribution'] * class_distribution
            )
            logger.debug("Combined expression created successfully")
            log_memory_usage()
        except Exception as e:
            logger.error(f"Error creating combined expression: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

        try:
            solver.Add(combined_obj == combined_expression)
            logger.debug("Combined objective constraint added successfully")
            log_memory_usage()
        except Exception as e:
            logger.error(f"Error adding combined objective constraint: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

        logger.info("Finished combined_objective calculation")
        log_memory_usage()
        return combined_obj
    except Exception as e:
        logger.error(f"Error in combined_objective: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

