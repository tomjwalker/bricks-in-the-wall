"""
`objectives.py`:

This module contains functions to implement objective components for the school scheduling problem.

The two main objectives are:
1. Minimize gaps in teachers' schedules.
2. Optimize distribution of classes.
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
                teaching_periods = []
                for p in range(8):  # Assuming 8 periods per day
                    dummy_var = solver.IntVar(0, 0, f'dummy_{t["ID"]}_{d}_{p}')
                    period_sum = solver.Sum([
                        x.get((t['ID'], c['ID'], r['ID'], (d, p)), dummy_var)
                        for c in classes
                        for r in rooms
                    ])
                    teaching_periods.append(period_sum)

                for p in range(1, 7):
                    # gap is a binary variable
                    gap = solver.IntVar(0, 1, f'gap_{t["ID"]}_{d}_{p}')

                    # Necessary condition: gap can only exist if periods either side are occupied
                    solver.Add(gap >= teaching_periods[p - 1] + teaching_periods[p + 1] - 1)

                    # Necessary condition: gap can only exist if the current period is empty
                    solver.Add(gap <= 1 - teaching_periods[p])

                    # Necessary condition: gap can only exist if the periods either side are occupied
                    solver.Add(gap <= teaching_periods[p - 1])
                    solver.Add(gap <= teaching_periods[p + 1])

                    gap_vars.append(gap)

            log_memory_usage()

        logger.debug("Adding total_gaps constraint")
        solver.Add(total_gaps == solver.Sum(gap_vars))

        logger.info("Finished minimize_teacher_gaps calculation")
        log_memory_usage()
        return total_gaps
    except Exception as e:
        logger.error(f"Error in minimize_teacher_gaps: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


def combined_objective(
        x: Dict[Tuple[str, str, str, Tuple[int, int]], pywraplp.Variable],
        teachers: List[Dict[str, Any]],
        classes: List[Dict[str, Any]],
        rooms: List[Dict[str, Any]],
        time_slots: List[Tuple[int, int]],
        weights: Dict[str, float]
) -> pywraplp.Variable:
    """
    Use only the minimize_teacher_gaps objective.
    """
    logger.info("Starting combined_objective calculation")
    return minimize_teacher_gaps(x, teachers, classes, rooms, time_slots)


# def optimize_class_distribution(
#         x: Dict[Tuple[str, str, str, Tuple[int, int]], pywraplp.Variable],
#         classes: List[Dict[str, Any]],
#         teachers: List[Dict[str, Any]],
#         rooms: List[Dict[str, Any]],
#         time_slots: List[Tuple[int, int]]
# ) -> pywraplp.Variable:
#     """
#     Implement objective: optimize distribution of classes throughout the week.
#     """
#     logger.info("Starting optimize_class_distribution calculation")
#     solver = pywraplp.Solver.CreateSolver('SCIP')
#
#     distribution_quality = solver.IntVar(0, solver.infinity(), 'distribution_quality')
#     same_day_penalty = solver.IntVar(0, solver.infinity(), 'same_day_penalty')
#     uneven_distribution_penalty = solver.IntVar(0, solver.infinity(), 'uneven_distribution_penalty')
#
#     days = set(day for day, _ in time_slots)
#     periods_per_day = len(set(period for _, period in time_slots))
#
#     logger.info(f"Processing {len(classes)} classes")
#     for i, class_ in enumerate(classes):
#         logger.debug(f"Processing class {i + 1}/{len(classes)}: {class_['ID']}")
#
#         day_counts = []
#         for day in days:
#             logger.debug(f"Processing day {day} for class {class_['ID']}")
#             day_count = solver.Sum([
#                 x.get((t['ID'], class_['ID'], r['ID'], (day, period)), 0)
#                 for t in teachers
#                 for r in rooms
#                 for period in range(periods_per_day)
#             ])
#             solver.Add(same_day_penalty >= day_count - 1)
#             day_counts.append(day_count)
#
#         logger.debug(f"Calculating day counts for class {class_['ID']}")
#         max_day_count = solver.IntVar(0, solver.infinity(), f'max_day_count_{class_["ID"]}')
#         min_day_count = solver.IntVar(0, solver.infinity(), f'min_day_count_{class_["ID"]}')
#
#         for day_count in day_counts:
#             solver.Add(max_day_count >= day_count)
#             solver.Add(min_day_count <= day_count)
#
#         solver.Add(uneven_distribution_penalty >= max_day_count - min_day_count)
#
#         # Log memory usage after processing each class
#         if (i + 1) % 5 == 0:
#             log_memory_usage()
#
#     logger.debug("Setting final distribution quality constraint")
#     solver.Add(distribution_quality == same_day_penalty + uneven_distribution_penalty)
#
#     logger.info("Finished optimize_class_distribution calculation")
#     return distribution_quality


# def combined_objective(
#         x: Dict[Tuple[str, str, str, Tuple[int, int]], pywraplp.Variable],
#         teachers: List[Dict[str, Any]],
#         classes: List[Dict[str, Any]],
#         rooms: List[Dict[str, Any]],
#         time_slots: List[Tuple[int, int]],
#         weights: Dict[str, float]
# ) -> pywraplp.Variable:
#     """
#     Combine individual objectives into a single objective function.
#     """
#     logger.info("Starting combined_objective calculation")
#     log_memory_usage()
#     solver = pywraplp.Solver.CreateSolver('SCIP')
#
#     try:
#         logger.info("Calculating teacher_gaps")
#         teacher_gaps = minimize_teacher_gaps(x, teachers, classes, rooms, time_slots)
#         logger.info(f"Teacher gaps objective value calculated")
#         log_memory_usage()
#
#         logger.info("Calculating class_distribution")
#         class_distribution = optimize_class_distribution(x, classes, teachers, rooms, time_slots)
#         logger.info(f"Class distribution objective value calculated")
#         log_memory_usage()
#
#         logger.info("Creating combined objective variable")
#         combined_obj = solver.NumVar(0, solver.infinity(), 'combined_objective')
#         log_memory_usage()
#
#         logger.info("Combining objectives")
#         logger.debug(f"Weights: gaps={weights['gaps']}, distribution={weights['distribution']}")
#
#         try:
#             logger.debug("Creating combined expression")
#             combined_expression = (
#                     weights['gaps'] * teacher_gaps +
#                     weights['distribution'] * class_distribution
#             )
#             logger.debug("Combined expression created successfully")
#             log_memory_usage()
#         except Exception as e:
#             logger.error(f"Error creating combined expression: {str(e)}")
#             logger.error(f"Traceback: {traceback.format_exc()}")
#             raise
#
#         try:
#             logger.debug("Adding combined objective constraint")
#             solver.Add(combined_obj == combined_expression)
#             logger.debug("Combined objective constraint added successfully")
#             log_memory_usage()
#         except Exception as e:
#             logger.error(f"Error adding combined objective constraint: {str(e)}")
#             logger.error(f"Traceback: {traceback.format_exc()}")
#             raise
#
#         logger.info("Finished combined_objective calculation")
#         log_memory_usage()
#         return combined_obj
#     except Exception as e:
#         logger.error(f"Error in combined_objective: {str(e)}")
#         logger.error(f"Traceback: {traceback.format_exc()}")
#         raise
