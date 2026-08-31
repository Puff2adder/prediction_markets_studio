"""Presentation helpers for the Prediction Market Studio."""

import streamlit as st


CSS = """
<style>
.stApp{background:linear-gradient(180deg,#f7f7ff 0%,#fff 18%)}
.block-container{max-width:1220px;padding-top:1.2rem;padding-bottom:4rem}
h1,h2,h3{color:#22205d;letter-spacing:-.02em} h1{font-size:2.05rem!important}
h2{font-size:1.42rem!important;margin-top:1.2rem!important} h3{font-size:1.08rem!important}
div[data-testid="stMetric"]{background:#fff;border:1px solid #dfdef3;border-radius:12px;padding:.7rem 1rem;box-shadow:0 2px 8px rgba(34,32,93,.05)}
.hero{background:linear-gradient(120deg,#27246d,#6b3ec7);color:white;border-radius:18px;padding:1.3rem 1.55rem;margin:.4rem 0 1.1rem;box-shadow:0 8px 24px rgba(39,36,109,.16)}
.hero h2{color:white!important;margin:0 0 .35rem!important}.hero p{margin:0;color:#f7f3ff;font-size:1.02rem}
.concept{background:#eeedff;border-left:5px solid #6b3ec7;border-radius:8px;padding:.8rem 1rem;margin:.65rem 0}
.why{background:#fff5d9;border-left:5px solid #e3a315;border-radius:8px;padding:.8rem 1rem;margin:.65rem 0}
.success-box{background:#ebf8ef;border-left:5px solid #268652;border-radius:8px;padding:.8rem 1rem;margin:.65rem 0}
.warning-box{background:#fff0eb;border-left:5px solid #d15c3d;border-radius:8px;padding:.8rem 1rem;margin:.65rem 0}
.stButton>button{border-radius:9px;font-weight:600}
</style>
"""


def configure_page():
    st.set_page_config(page_title="Prediction Market Studio", page_icon="🔮", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title, subtitle):
    st.markdown(f'<div class="hero"><h2>{title}</h2><p>{subtitle}</p></div>', unsafe_allow_html=True)


def concept(title, text):
    st.markdown(f'<div class="concept"><strong>{title}</strong><br>{text}</div>', unsafe_allow_html=True)


def why(text):
    st.markdown(f'<div class="why"><strong>Why this matters</strong><br>{text}</div>', unsafe_allow_html=True)


def success(title, text):
    st.markdown(f'<div class="success-box"><strong>{title}</strong><br>{text}</div>', unsafe_allow_html=True)


def warning(title, text):
    st.markdown(f'<div class="warning-box"><strong>{title}</strong><br>{text}</div>', unsafe_allow_html=True)
