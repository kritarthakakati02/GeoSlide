"""Theme helpers and design tokens for the GeoSlide Streamlit frontend."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STYLES_FILE = ROOT / "assets" / "styles.css"

COLORS = {
    "primary": "#2f6b4f",
    "secondary": "#2d7da9",
    "accent": "#f2b84b",
    "background": "#f3f5f7",
    "card": "#ffffff",
    "text": "#22313f",
    "muted": "#64748b",
    "border": "#dfe6ea",
}

FONTS = {
    "base": "Inter, Segoe UI, Roboto, sans-serif",
}

SIZES = {
    "title": "1.8rem",
    "subtitle": "1.15rem",
    "body": "1rem",
    "small": "0.9rem",
}

SPACING = {
    "sm": "0.75rem",
    "md": "1rem",
    "lg": "1.5rem",
    "xl": "2rem",
}

BORDER_RADIUS = {
    "md": "18px",
    "sm": "12px",
}


def load_styles() -> str:
    """Read the shared stylesheet for the Streamlit app."""
    return STYLES_FILE.read_text(encoding="utf-8")

THEME = {
    # Colors
    "primary": COLORS["primary"],
    "secondary": COLORS["secondary"],
    "accent": COLORS["accent"],
    "background": COLORS["background"],
    "card_bg": COLORS["card"],
    "text": COLORS["text"],
    "muted": COLORS["muted"],
    "border": COLORS["border"],

    # Status colors
    "success": "#2E7D32",
    "warning": "#F59E0B",
    "error": "#D32F2F",
    "info": "#0284C7",

    # Typography
    "font_family": FONTS["base"],

    # Radius
    "border_radius": BORDER_RADIUS["md"],
}
