"""
Compact "AI System Status" panel for GeoSlide.

Purely decorative, read-only status card meant to sit directly below a
page's hero description and fill otherwise-empty whitespace. It does not
touch layout, navigation, or any backend/model logic — the status values
passed in are static, page-specific labels (see each page's call site).

Styling (colors, spacing, radii, shadows) lives in
`assets/design_system.css` under "21. AI SYSTEM STATUS PANEL" so every
page shares exactly one definition.
"""

from typing import List, Tuple

import streamlit as st


def render_status_panel(icon_html: str, items: List[Tuple[str, str]]) -> None:
    """
    Render the compact system-status card.

    Args:
        icon_html: Pre-rendered inline SVG (e.g. from a page's local
            `_icon("cpu")` helper) shown next to the "System Status" title.
        items: List of (label, status_text) tuples, e.g.
            [("KNN Prediction Engine", "Ready"), ...]. Each renders as one
            row with a green status dot on the left and a status pill on
            the right.
    """
    rows = "".join(
        f"""
        <div class="gs-status-row">
            <div class="gs-status-label">
                <span class="gs-status-dot"></span>{label}
            </div>
            <div class="gs-status-value">{value}</div>
        </div>
        """
        for label, value in items
    )

    st.markdown(
        f"""
        <div class="gs-status-panel">
            <div class="gs-status-panel-title">{icon_html}<span>System Status</span></div>
            {rows}
        </div>
        """,
        unsafe_allow_html=True,
    )
