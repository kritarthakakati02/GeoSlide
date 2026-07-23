"""
Animated loading indicator component for GeoSlide.
"""

import streamlit as st

from utils.theme import THEME


def loading_section(message: str = "Loading...") -> None:
    """
    Render an animated loading placeholder section.

    Intended for use while data/results are being fetched or processed,
    e.g.:

        placeholder = st.empty()
        with placeholder.container():
            loading_section("Fetching slide data...")
        # ... do work ...
        placeholder.empty()

    Args:
        message: Text shown beneath the spinner.
    """
    st.markdown(
        f"""
        <style>
        @keyframes geoslide-spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        <div style="
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            padding: 48px 0;
            font-family:{THEME['font_family']};
        ">
            <div style="
                width:40px;
                height:40px;
                border:4px solid {THEME['border']};
                border-top:4px solid {THEME['primary']};
                border-radius:50%;
                animation: geoslide-spin 0.8s linear infinite;
            "></div>
            <div style="
                margin-top:14px;
                color:{THEME['muted']};
                font-size:0.95rem;
                font-weight:500;
            ">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
