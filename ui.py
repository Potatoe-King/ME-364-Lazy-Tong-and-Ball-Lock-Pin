"""Shared Streamlit layout helpers."""

from __future__ import annotations

import streamlit as st

from mechanics.units import SI, US, Units


CSS = """
<style>
    .stApp { background: #F7F9FC; }
    [data-testid="stSidebar"] { background: #17324D; }
    [data-testid="stSidebar"] * { color: #F7FAFC; }
    [data-testid="stSidebar"] div[data-baseweb="select"] * { color: #1D2733; }
    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 18px;
        color: white;
        background: linear-gradient(120deg, #17324D 0%, #245B78 64%, #00A6A6 100%);
        margin-bottom: 1.2rem;
    }
    .hero h1 { margin: 0 0 .35rem 0; font-size: 2rem; }
    .hero p { margin: 0; opacity: .94; font-size: 1.02rem; }
    .callout {
        background: white;
        border: 1px solid #DCE5EC;
        border-left: 5px solid #00A6A6;
        border-radius: 10px;
        padding: .8rem 1rem;
        margin: .5rem 0 1rem 0;
    }
    .warning-callout { border-left-color: #F3B61F; }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #DCE5EC;
        border-radius: 12px;
        padding: .7rem .85rem;
    }
    .small-note { color: #526575; font-size: .88rem; }
</style>
"""


def setup_page(title: str, icon: str = "⚙️") -> None:
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def unit_selector(key: str) -> Units:
    choice = st.sidebar.radio("Unit system", ["SI", "US customary"], key=key)
    return SI if choice == "SI" else US


def default(units: Units, si_value: float, us_value: float) -> float:
    return si_value if units.is_si else us_value


def number(
    label: str,
    value: float,
    *,
    key: str,
    minimum: float = 0.0,
    step: float | None = None,
    help_text: str | None = None,
) -> float:
    kwargs = {"min_value": minimum, "value": float(value), "key": key, "help": help_text}
    if step is not None:
        kwargs["step"] = float(step)
    return st.number_input(label, **kwargs)


def status_box(passed: bool, pass_text: str, fail_text: str) -> None:
    (st.success if passed else st.error)(pass_text if passed else fail_text)

