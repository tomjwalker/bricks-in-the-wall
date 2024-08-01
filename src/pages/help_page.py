"""
`help_page.py`:

This module contains the Help page for the school scheduling system.
"""

import streamlit as st

def show():
    st.title("Help")

    st.header("About the School Scheduling System")
    st.write("""
    This application helps you create optimal school schedules using advanced optimization techniques. 
    Follow the steps below to generate your schedule:
    """)

    st.subheader("1. Data Input")
    st.write("""
    - Upload your own CSV files for teachers, classes, rooms, and time slots.
    - Or generate synthetic data by specifying the number of teachers, classes, and rooms.
    """)

    st.subheader("2. Solve")
    st.write("""
    - Adjust solver settings if needed.
    - Click "Generate Schedule" to create an optimized schedule.
    """)

    st.subheader("3. Results")
    st.write("""
    - View the generated schedule.
    - Analyze various metrics and visualizations.
    - Export the schedule to a CSV file.
    """)

    st.header("FAQs")
    st.subheader("Q: What format should my CSV files be in?")
    st.write("""
    A: Your CSV files should have the following columns:
    - Teachers: ID, Name, Subjects, FullTime, Availability
    - Classes: ID, Subject, GradeLevel, NumStudents, PeriodsPerWeek
    - Rooms: ID, Capacity, Type
    - Time Slots: Day, Period
    """)

    st.subheader("Q: How long does it take to generate a schedule?")
    st.write("""
    A: The time to generate a schedule depends on the complexity of your data. 
    For most cases, it should take less than 5 minutes. If it takes longer, 
    try reducing the problem size or adjusting the constraints.
    """)

    st.subheader("Q: What do I do if no feasible schedule is found?")
    st.write("""
    A: If no feasible schedule is found, try the following:
    1. Check your input data for inconsistencies.
    2. Reduce the number of constraints or relax them.
    3. Increase the number of available rooms or time slots.
    4. Reduce the number of classes or increase the number of teachers.
    """)

    st.header("Need More Help?")
    st.write("""
    If you need further assistance, please contact our support team at support@schoolscheduler.com.
    """)
