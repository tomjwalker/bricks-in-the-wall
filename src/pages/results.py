"""
`results.py`:

This module contains the Results page for the school scheduling system.
"""

import streamlit as st
import pandas as pd
from src import utils


def show():
    st.title("Results")

    if st.session_state.schedule is None:
        st.warning("No schedule has been generated yet. Please go to the Solve page to generate a schedule.")
        return

    schedule = st.session_state.schedule
    scheduler = st.session_state.scheduler

    st.success(f"Schedule generated in {st.session_state.solve_time:.2f} seconds!")

    # Display schedule
    st.header("Generated Schedule")
    for day, classes in schedule.items():
        with st.expander(f"Day {day + 1}"):
            df = pd.DataFrame(classes)
            st.dataframe(df)

    # Visualizations
    st.header("Schedule Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Teacher Workload
        st.subheader("Teacher Workload")
        teacher_workload = utils.calculate_teacher_workload(schedule)
        st.bar_chart(teacher_workload)

        # Class Distribution
        st.subheader("Class Distribution")
        class_distribution = utils.analyze_class_distribution(schedule, scheduler.data["teachers"])
        st.bar_chart(pd.DataFrame(class_distribution).T)

        # Room Utilization
        st.subheader("Room Utilization")
        room_utilization = utils.calculate_room_utilization(schedule, scheduler.data["rooms"], scheduler.data["time_slots"])
        st.bar_chart(room_utilization)

    with col2:
        # Teacher Utilization
        try:
            teacher_utilization = utils.calculate_teacher_utilization(schedule, scheduler.data["teachers"],
                                                                      scheduler.data["time_slots"])
            st.subheader("Teacher Utilization")
            st.bar_chart(teacher_utilization)
        except Exception as e:
            st.error(f"Error calculating teacher utilization: {str(e)}")
            st.text("Teacher data format:")
            st.write(scheduler.data["teachers"][0])  # Display the first teacher's data for debugging

        # Teacher Gaps
        st.subheader("Teacher Gaps")
        teacher_gaps = utils.analyze_gaps(schedule, scheduler.data["teachers"])
        st.bar_chart(teacher_gaps)

        # Subject Balance
        st.subheader("Subject Balance")
        subject_balance = utils.analyze_subject_balance(schedule, scheduler.data["classes"])
        st.bar_chart(subject_balance)

    # Statistics
    st.header("Schedule Statistics")
    stats = utils.calculate_schedule_statistics(schedule)
    st.dataframe(pd.DataFrame([stats]))

    # Export option
    if st.button("Export Schedule to CSV"):
        utils.export_schedule_to_csv(schedule, "generated_schedule.csv")
        st.success("Schedule exported to output/generated_schedule.csv")
