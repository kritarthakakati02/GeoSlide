"""
Empty state component for GeoSlide (no-data / no-results placeholders).
"""

import streamlit as st

from utils.theme import THEME


def empty_state(title: str, description: str = "", icon: str = "📭") -> None:
    """
    Render a themed empty-state placeholder.

    Args:
        title: Short headline (e.g. "No slides found").
        description: Optional supporting text.
        icon: Optional icon/emoji shown above the title.
    """
    description_html = (
        f'<div style="color:{THEME["muted"]}; font-size:0.9rem; '
        f'margin-top:6px; max-width:420px;">{description}</div>'
        if description else ""
    )

    st.markdown(
        f"""
        <div style="
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            text-align:center;
            padding: 48px 24px;
            font-family:{THEME['font_family']};
        ">
            <div style="font-size:2.4rem; margin-bottom:8px;">{icon}</div>
            <div style="font-size:1.15rem; font-weight:700; color:{THEME['text']};">{title}</div>
            {description_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
