"""
GeoSlide AI — Design System tokens (Python mirror).

STATUS: FOUNDATION ONLY. This module is not imported anywhere yet — it
exists so charts, tables, and any other Python-rendered UI can pull the
exact same values documented in frontend/assets/design_system.css once a
page is actually migrated to the new system, instead of hard-coding hex
strings that quietly drift out of sync with the CSS.

Keep this file's values in lockstep with design_system.css by hand; there
is intentionally no build step / codegen here to keep the project's
existing "no extra tooling" footprint.
"""

from __future__ import annotations

# ==========================================================================
# 1. Color palette (mirrors design_system.css :root)
# ==========================================================================

COLORS = {
    # Neutral / surface
    "bg": "#F7F5F2",
    "bg_subtle": "#F1EEE8",
    "bg_inset": "#ECE8E1",
    "surface": "#FFFFFF",
    "border": "#E6E1D8",
    "border_strong": "#D6CFC1",

    # Text
    "text_primary": "#1C231F",
    "text_secondary": "#4B564F",
    "text_tertiary": "#7C8780",
    "text_inverse": "#FFFFFF",

    # Brand (primary accent)
    "brand_50": "#EBF3EE",
    "brand_100": "#D3E6DA",
    "brand_200": "#A7CDB6",
    "brand_500": "#2F6B4F",
    "brand_600": "#255943",
    "brand_700": "#1C4433",

    # Secondary accent
    "accent_50": "#E7F1F6",
    "accent_500": "#2D7DA9",
    "accent_600": "#24657F",

    # Tertiary accent
    "amber_50": "#FBF3E2",
    "amber_500": "#C88A2E",

    # Semantic
    "success_500": "#2E7D32",
    "warning_500": "#B7791F",
    "error_500": "#B3392A",
    "info_500": "#2D7DA9",
}

# Ordinal risk-level scale (Very Low -> Very High). Keys match the
# lowercase, underscore-joined form of the model's risk-level labels so
# callers can do RISK_COLORS[level.lower().replace(" ", "_")].
RISK_COLORS = {
    "very_low": "#2E7D32",
    "low": "#6FA84A",
    "moderate": "#C88A2E",
    "high": "#C1591F",
    "very_high": "#B3392A",
}

# Qualitative categorical sequence for multi-series charts (feature
# comparisons, category breakdowns) — NOT for risk-level charts, which
# should use RISK_COLORS in ordinal order instead.
CHART_COLORWAY = [
    "#2F6B4F",  # brand green
    "#2D7DA9",  # ocean blue
    "#C88A2E",  # amber
    "#8A5FA8",  # muted violet
    "#B3392A",  # muted red
    "#4B564F",  # neutral slate
]


# ==========================================================================
# 2. Typography
# ==========================================================================

FONT_FAMILY = "Inter, Segoe UI, Roboto, -apple-system, sans-serif"
FONT_FAMILY_MONO = "JetBrains Mono, SFMono-Regular, Consolas, monospace"

FONT_SIZES = {
    "display": 36,
    "h1": 28,
    "h2": 22,
    "h3": 18,
    "body_lg": 16,
    "body": 15,
    "sm": 13,
    "xs": 11,
}


# ==========================================================================
# 3. Spacing / radius (px)
# ==========================================================================

SPACING = {"1": 4, "2": 8, "3": 12, "4": 16, "5": 20, "6": 24, "8": 32, "10": 40, "12": 48, "16": 64}
RADIUS = {"xs": 8, "sm": 12, "md": 16, "lg": 20, "full": 999}


# ==========================================================================
# 4. Plotly template
# ==========================================================================
# Usage in a chart page (once migrated):
#
#   import plotly.express as px
#   from utils.design_tokens import PLOTLY_LAYOUT, CHART_COLORWAY
#   fig = px.bar(df, x="feature", y="importance", color_discrete_sequence=CHART_COLORWAY)
#   fig.update_layout(**PLOTLY_LAYOUT)

PLOTLY_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {
        "family": FONT_FAMILY,
        "color": COLORS["text_secondary"],
        "size": FONT_SIZES["sm"],
    },
    "title": {
        "font": {"family": FONT_FAMILY, "size": FONT_SIZES["h3"], "color": COLORS["text_primary"]},
    },
    "legend": {
        "font": {"family": FONT_FAMILY, "size": FONT_SIZES["xs"], "color": COLORS["text_secondary"]},
        "bgcolor": "rgba(0,0,0,0)",
    },
    "margin": {"l": 32, "r": 24, "t": 32, "b": 32},
    "xaxis": {
        "gridcolor": COLORS["border"],
        "zerolinecolor": COLORS["border_strong"],
        "linecolor": COLORS["border"],
    },
    "yaxis": {
        "gridcolor": COLORS["border"],
        "zerolinecolor": COLORS["border_strong"],
        "linecolor": COLORS["border"],
    },
    "colorway": CHART_COLORWAY,
}


def risk_color(level: str) -> str:
    """Return the token color for a risk-level label.

    Accepts labels like "Very High", "very_high", "VERY-HIGH" etc.
    Falls back to text_tertiary (neutral gray) if the label doesn't
    match a known risk level, rather than raising, since this is a
    display helper.
    """
    key = level.strip().lower().replace(" ", "_").replace("-", "_")
    return RISK_COLORS.get(key, COLORS["text_tertiary"])
