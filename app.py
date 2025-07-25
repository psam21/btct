"""
Bitcoin Futures Trading Signal App

Minimal entry point that orchestrates components and handles Streamlit configuration.
Implements FR001, FR002, and FR004: Minimal entry point architecture.
"""

import streamlit as st
from ui.components import render_app


def main():
    """
    Main application entry point.
    
    Implements FR001: Streamlit Framework
    Implements FR002: Deployable on Streamlit Community Cloud
    Implements FR004: Minimal entry point that orchestrates components
    """
    # Streamlit page configuration
    st.set_page_config(
        page_title="Bitcoin Futures Trading Signals",
        page_icon="₿",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Render the main application UI
    render_app()


if __name__ == "__main__":
    main()
