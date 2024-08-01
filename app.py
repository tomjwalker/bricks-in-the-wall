import streamlit as st
from PIL import Image
import sys
import os

# Add the src directory to the Python path
root_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(root_dir, 'src')
sys.path.append(src_dir)

# Now import your page modules
from src.pages import data_input, solve, results, help_page

# Set up logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# LOGO_PATH = "images/flowsquircle_curbar.png"
LOGO_PATH = "images/flowsquircle_darkmode_transparent.png"
LOGO_AND_NAME_PATH = "images/flowsquircle_name.png"


def main():
    st.set_page_config(page_title="School Scheduling System", layout="wide")

    # Sidebar
    st.sidebar.title("Navigation")

    # Add logo
    # logo = Image.open("images/flowsquircle_curbar.png")
    # st.sidebar.image(logo, use_column_width=True)
    st.logo(LOGO_AND_NAME_PATH, icon_image=LOGO_PATH)

    # Session state initialization
    if 'scheduler' not in st.session_state:
        st.session_state.scheduler = None
    if 'schedule' not in st.session_state:
        st.session_state.schedule = None

    # Navigation
    pages = ["Data Input", "Help"]
    if 'scheduler_initialized' in st.session_state and st.session_state.scheduler_initialized:
        pages.extend(["Solve", "Results"])

    page = st.sidebar.radio("Go to", pages)

    # Page routing
    if page == "Data Input":
        data_input.show()
    elif page == "Solve":
        solve.show()
    elif page == "Results":
        results.show()
    elif page == "Help":
        help_page.show()


if __name__ == "__main__":
    main()
