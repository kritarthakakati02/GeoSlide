"""
Section header component for GeoSlide pages.
"""

from typing import Optional

import streamlit as st

from utils.theme import THEME


def section_header(
    title: str,
    subtitle: Optional[str] = None,
    icon: str = "",
) -> None:
    """
    Render a themed section header with an optional subtitle and icon.

    Args:
        title: Main heading text.
        subtitle: Optional supporting text shown beneath the title.
        icon: Optional icon/emoji shown to the left of the title.
    """
    icon_html = (
        f'<span style="font-size:1.5rem; margin-right:10px;">{icon}</span>'
        if icon else ""
    )
    subtitle_html = (
        f'<div style="color:{THEME["muted"]}; font-size:0.95rem; '
        f'margin-top:4px;">{subtitle}</div>'
        if subtitle else ""
    )

    st.markdown(
        f"""
        <div style="
            font-family:{THEME['font_family']};
            padding: 6px 0 14px 0;
            border-bottom: 1px solid {THEME['border']};
            margin-bottom: 16px;
        ">
            <div style="
                display:flex;
                align-items:center;
                font-size:1.4rem;
                font-weight:700;
                color:{THEME['text']};
            ">
                {icon_html}{title}
            </div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
