"""
Bitcoin Historical Data App

Simple Streamlit app for fetching and displaying Bitcoin historical data.
"""

import streamlit as st
from ui.components import render_app


def main():
    """Main application entry point."""
    # Streamlit page configuration
    st.set_page_config(
        page_title="Bitcoin Historical Data",
        page_icon="₿",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Render the main application UI
    render_app()


if __name__ == "__main__":
    main()
