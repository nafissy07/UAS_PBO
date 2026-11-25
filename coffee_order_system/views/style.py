"""Gaya tambahan (CSS) supaya tampilan mengikuti rancangan GUI."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Londrina+Solid:wght@400;900&family=Quicksand:wght@500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, button, input, label { font-family: 'Quicksand', sans-serif; }
h1, h2, h3 { font-family: 'Londrina Solid', 'Impact', sans-serif !important; color: #7B4B3A; letter-spacing: .5px; }
h1 { font-size: 2.8rem !important; margin-bottom: 0 !important; }
[data-testid="stSidebar"] { border-right: 2px solid #cdb9a3; }
[data-testid="stVerticalBlockBorderWrapper"] { background: #F5EFE3; border-radius: 18px; }
.stButton > button { border-radius: 14px; font-weight: 700; border: 2px solid #cdb9a3; }
.stButton > button[kind="primary"] { background: #BF8461; border-color: #BF8461; color: #fff; }
.stButton > button:hover { transform: translateY(-1px); border-color: #BF8461; }
.brand { font-family: 'Londrina Solid', sans-serif; font-size: 1.9rem; color: #7B4B3A; line-height: 1; }
.brand small { display: block; font-family: 'Quicksand', sans-serif; font-size: .75rem; color: #8A6A5C; }
</style>
"""


def terapkan():
    st.markdown(CSS, unsafe_allow_html=True)
