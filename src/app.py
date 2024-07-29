"""
This module contains the Streamlit app for the school scheduling system.
"""

import streamlit as st
import pandas as pd
from scheduler import Scheduler
import utils
import traceback


def main():
    st.title("School Scheduling System")

    # File upload
    st.header("Data Input")
    teachers_file = st.file_uploader("Upload Teachers CSV", type="csv")
    classes_file = st.file_uploader("Upload Classes CSV", type="csv")
    rooms_file = st.file_uploader("Upload Rooms CSV", type="csv")
    time_slots_file = st.file_uploader("Upload Time Slots CSV", type="csv")

    if all([teachers_file, classes_file, rooms_file, time_slots_file]):
        st.success("All files uploaded successfully!")

        # Initialize scheduler
        data_files = {
            "teachers_file": teachers_file,
            "classes_file": classes_file,
            "rooms_file": rooms_file,
            "time_slots_file": time_slots_file
        }

        try:
            scheduler = Scheduler(data_files)

            # Objective weights
            st.header("Objective Weights")
            weights = {
                "gaps": st.slider("Weight for minimizing gaps", 0.0, 1.0, 0.5),
                "workload": st.slider("Weight for balancing workload", 0.0, 1.0, 0.3),
                "distribution": st.slider("Weight for optimizing class distribution", 0.0, 1.0, 0.2)
            }

            if st.button("Generate Schedule"):
                with st.spinner("Generating schedule..."):
                    scheduler.create_variables()
                    scheduler.apply_constraints()
                    scheduler.set_objective(weights)
                    if scheduler.solve():
                        st.success("Schedule generated successfully!")
                        schedule = scheduler.get_schedule()

                        # Display schedule
                        st.header("Generated Schedule")
                        for day, classes in schedule.items():
                            st.subheader(f"Day {day + 1}")
                            df = pd.DataFrame(classes)
                            st.dataframe(df)

                        # Visualize teacher workload
                        st.header("Teacher Workload")
                        utils.visualize_teacher_workload(schedule)
                        st.image("output/teacher_workload.png")

                        # Display statistics
                        st.header("Schedule Statistics")
                        stats = utils.calculate_schedule_statistics(schedule)
                        st.json(stats)

                        # Export option
                        if st.button("Export Schedule to CSV"):
                            utils.export_schedule_to_csv(schedule, "generated_schedule.csv")
                            st.success("Schedule exported to output/generated_schedule.csv")
                    else:
                        st.error("Unable to generate a feasible schedule. Please adjust constraints or data.")
        except Exception as e:
            st.error("An error occurred:")
            st.code(traceback.format_exc())
            st.error(f"Error details: {str(e)}")


if __name__ == "__main__":
    main()
