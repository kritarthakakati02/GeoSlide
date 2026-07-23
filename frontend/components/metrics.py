"""
Layout helpers for arranging metric cards across a page.

These helpers reuse `frontend.components.cards.metric_card` for
rendering each individual card, so card markup/styling lives in exactly
one place.
"""

from typing import Optional, Sequence, TypedDict

import streamlit as st

from components.cards import metric_card


class MetricSpec(TypedDict, total=False):
    """Shape of a single metric entry passed to metric_row/metric_grid."""
    title: str
    value: object
    icon: str
    delta: Optional[str]


def metric_row(metrics: Sequence[MetricSpec], gap: str = "medium") -> None:
    """
    Render a single row of metric cards, evenly spaced across columns.

    Args:
        metrics: List of dicts with keys "title", "value", and
            optionally "icon" and "delta". Each entry is passed straight
            through to `metric_card`.
        gap: Column gap size passed to `st.columns`
            ("small", "medium", "large").
    """
    if not metrics:
        return

    columns = st.columns(len(metrics), gap=gap)
    for col, spec in zip(columns, metrics):
        with col:
            metric_card(
                title=spec.get("title", ""),
                value=spec.get("value", ""),
                icon=spec.get("icon", ""),
                delta=spec.get("delta"),
            )


def metric_grid(
    metrics: Sequence[MetricSpec],
    columns_per_row: int = 3,
    gap: str = "medium",
) -> None:
    """
    Render metric cards in a wrapping grid, `columns_per_row` per row.

    Args:
        metrics: List of metric specs (see `metric_row`).
        columns_per_row: Number of cards per row before wrapping.
        gap: Column gap size passed to `st.columns`.
    """
    if not metrics:
        return

    for start in range(0, len(metrics), columns_per_row):
        metric_row(metrics[start:start + columns_per_row], gap=gap)
