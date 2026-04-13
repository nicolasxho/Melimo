"""
Écran 0 — Accueil : choix du mode de jeu.
"""
from __future__ import annotations
import streamlit as st


def render() -> None:
    st.markdown(
        "<h1 style='text-align:center; letter-spacing:0.3em; color:#4caf50;'>M É L I M O</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:#888;'>Jeu de mots en labyrinthe</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📂  Puzzle pré-défini", use_container_width=True):
            st.session_state.screen = "setup_predefined"
            st.rerun()
    with col2:
        if st.button("⚙️  Générer une partie", use_container_width=True):
            st.session_state.screen = "setup_generate"
            st.rerun()

    st.markdown("")
    if st.button("❓  Règles du jeu", use_container_width=True):
        st.session_state.screen = "rules"
        st.rerun()
