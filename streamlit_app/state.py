"""
Initialisation et gestion de st.session_state pour Mélimo.
"""
from __future__ import annotations
import streamlit as st


def init_state() -> None:
    """Initialise toutes les clés de session_state avec leurs valeurs par défaut.
    N'écrase pas les clés déjà présentes (reruns).
    """
    defaults = {
        "screen": "home",
        "puzzle": None,
        "game_state": None,
        "current_word_idx": 1,
        "hint_active": False,
        "last_feedback": None,
        "answer_input_key": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_game() -> None:
    """Réinitialise l'état de jeu (pour rejouer)."""
    st.session_state.puzzle = None
    st.session_state.game_state = None
    st.session_state.current_word_idx = 1
    st.session_state.hint_active = False
    st.session_state.last_feedback = None
    st.session_state.answer_input_key = 0
    st.session_state.screen = "home"


def go_to(screen: str) -> None:
    """Change d'écran et force un rerun."""
    st.session_state.screen = screen
    st.rerun()
