"""
Reusable card components for GeoSlide.

This module currently exposes:
    - metric_card: a themed KPI/metric display card.

Layout helpers that arrange multiple metric cards together live in
`frontend.components.metrics` and reuse `metric_card` rather than
duplicating its markup/styling.
"""

from typing import Optional

import streamlit as st

from utils.theme import THEME


def metric_card(
    title: str,
    value,
    icon: str = "",
    delta: Optional[str] = None,
) -> None:
    """
    Render a themed metric/KPI card.

    Args:
        title: Label shown above the value (e.g. "Total Slides").
        value: The metric value to display (str, int, or float).
        icon: Optional icon/emoji shown next to the title.
        delta: Optional delta text (e.g. "+12%", "-3 this week"). The
            color is inferred from the leading sign: "+" -> success,
            "-" -> error, otherwise -> neutral/muted.
    """
    delta_html = ""
    if delta:
        delta_color = THEME["muted"]
        stripped = delta.strip()
        if stripped.startswith("+"):
            delta_color = THEME["success"]
        elif stripped.startswith("-"):
            delta_color = THEME["error"]
        delta_html = f"""
            <div style="
                font-size: 0.85rem;
                font-weight: 600;
                color: {delta_color};
                margin-top: 4px;
            ">{delta}</div>
        """

    icon_html = (
        f'<span style="font-size:1.4rem; margin-right:8px;">{icon}</span>'
        if icon else ""
    )

    st.markdown(
        f"""
        <div style="
            background: {THEME['card_bg']};
            border: 1px solid {THEME['border']};
            border-radius: {THEME['border_radius']};
            padding: 18px 20px;
            font-family: {THEME['font_family']};
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        ">
            <div style="
                display:flex;
                align-items:center;
                color:{THEME['muted']};
                font-size:0.85rem;
                font-weight:600;
                text-transform:uppercase;
                letter-spacing:0.03em;
            ">
                {icon_html}{title}
            </div>
            <div style="
                font-size:1.9rem;
                font-weight:700;
                color:{THEME['text']};
                margin-top:6px;
            ">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
