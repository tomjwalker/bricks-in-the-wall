"""
`data_input.py`:

This module contains the Data Input page for the school scheduling system.
"""

import streamlit as st
import pandas as pd
from src.scheduler import Scheduler
from src import utils
from src.generate_dummy_data import generate_teachers, generate_classes, generate_rooms, generate_time_slots, Subject

def show():
    st.title("Data Input")

    tab1, tab2 = st.tabs(["Generate Synthetic Data", "Upload Data"])

    with tab1:
        show_generate_data()

    with tab2:
        show_upload_data()

    # Display status of scheduler initialization
    if 'scheduler_initialized' in st.session_state and st.session_state.scheduler_initialized:
        st.success("Scheduler is initialized and ready for use!")
        st.info("You can now proceed to the 'Solve' page.")

def show_upload_data():
    st.header("Upload Your Data")

    teachers_file = st.file_uploader("Upload Teachers CSV", type="csv")
    classes_file = st.file_uploader("Upload Classes CSV", type="csv")
    rooms_file = st.file_uploader("Upload Rooms CSV", type="csv")
    time_slots_file = st.file_uploader("Upload Time Slots CSV", type="csv")

    if all([teachers_file, classes_file, rooms_file, time_slots_file]):
        st.success("All files uploaded successfully!")

        data_files = {
            "teachers_file": teachers_file,
            "classes_file": classes_file,
            "rooms_file": rooms_file,
            "time_slots_file": time_slots_file
        }

        if st.button("Initialize Scheduler"):
            try:
                scheduler = Scheduler(data_files)
                st.session_state.scheduler = scheduler
                st.session_state.scheduler_initialized = True
                # st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

def show_generate_data():
    st.header("Generate Synthetic Data")

    num_teachers = st.slider("Number of Teachers", 5, 100, 10)
    num_classes = st.slider("Number of Classes", 10, 200, 15)
    num_rooms = st.slider("Number of Rooms", 5, 50, 10)

    if st.button("Generate Data"):
        try:
            teachers = generate_teachers(num_teachers)
            classes = generate_classes(num_classes)
            rooms = generate_rooms(num_rooms)
            time_slots = generate_time_slots()

            # Convert Subject enum to string for teachers
            for teacher in teachers:
                teacher['Subjects'] = [subject.value for subject in teacher['Subjects']]

            # Convert Subject enum to string for classes
            for class_ in classes:
                class_['Subject'] = class_['Subject'].value

            # Convert RoomType enum to string for rooms
            for room in rooms:
                room['Type'] = room['Type'].value

            # Save generated data to session state
            st.session_state.generated_data = {
                "teachers": teachers,
                "classes": classes,
                "rooms": rooms,
                "time_slots": time_slots
            }

            st.session_state.data_generated = True
            st.success("Synthetic data generated successfully!")
            # st.rerun()

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    if 'data_generated' in st.session_state and st.session_state.data_generated:
        # Display sample of generated data
        st.subheader("Sample of Generated Data")
        st.write("Teachers:", pd.DataFrame(st.session_state.generated_data["teachers"][:5]))
        st.write("Classes:", pd.DataFrame(st.session_state.generated_data["classes"][:5]))
        st.write("Rooms:", pd.DataFrame(st.session_state.generated_data["rooms"][:5]))

        if st.button("Initialize Scheduler with Generated Data"):
            try:
                scheduler = Scheduler(st.session_state.generated_data)
                st.session_state.scheduler = scheduler
                st.session_state.scheduler_initialized = True
                # st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
