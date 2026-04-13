"""
Mélimo — Application Streamlit
Point d'entrée : streamlit run app.py
"""
from __future__ import annotations
import os
import sys

# Racine du projet dans le path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from streamlit_app.state import init_state
from streamlit_app.views import home, setup_predefined, setup_generate, game, summary, rules, about

st.set_page_config(
    page_title="Mélimo",
    page_icon="🔤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_state()

screen = st.session_state.screen

if screen == "home":
    home.render()
elif screen == "setup_predefined":
    setup_predefined.render()
elif screen == "setup_generate":
    setup_generate.render()
elif screen == "game":
    game.render()
elif screen == "summary":
    summary.render()
elif screen == "rules":
    rules.render()
elif screen == "about":
    about.render()
else:
    st.session_state.screen = "home"
    st.rerun()
