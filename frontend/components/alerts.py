"""
Themed alert components for GeoSlide.

Exposes four public functions - success(), warning(), error(), info() -
which all share a single private renderer (_alert) so the markup and
styling logic is defined exactly once.
"""

import streamlit as st

from utils.theme import THEME

_ICONS = {
    "success": "✅",
    "warning": "⚠️",
    "error": "⛔",
    "info": "ℹ️",
}


def _alert(message: str, kind: str) -> None:
    """Shared renderer used by success/warning/error/info."""
    color = THEME[kind]
    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:flex-start;
            gap:10px;
            background: {color}1A;
            border-left: 4px solid {color};
            border-radius: {THEME['border_radius']};
            padding: 12px 16px;
            font-family: {THEME['font_family']};
            color: {THEME['text']};
            margin: 8px 0;
        ">
            <span style="font-size:1.1rem; line-height:1.4;">{_ICONS[kind]}</span>
            <span style="font-size:0.95rem; line-height:1.4;">{message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def success(message: str) -> None:
    """Render a themed success alert."""
    _alert(message, "success")


def warning(message: str) -> None:
    """Render a themed warning alert."""
    _alert(message, "warning")


def error(message: str) -> None:
    """Render a themed error alert."""
    _alert(message, "error")


def info(message: str) -> None:
    """Render a themed info alert."""
    _alert(message, "info")
