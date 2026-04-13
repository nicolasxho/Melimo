"""
Écran 1b — Configuration et lancement de la génération.
"""
from __future__ import annotations
import os
import sys
import time
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models import GameState
from generator.grid_builder import generate_puzzle

THEMES = ["general", "nature", "sport"]
DIFFICULTIES = ["facile", "moyen", "difficile"]
SIZES = {
    "Petite (10×10)":  (10, 10),
    "Normale (15×15)": (15, 15),
    "Grande (20×20)":  (20, 20),
}
WORD_COUNTS = [8, 12, 17]
TIMER_OPTIONS: dict[str, int | None] = {
    "Pas de limite": None,
    "3 minutes": 180,
    "5 minutes": 300,
    "10 minutes": 600,
}


def render() -> None:
    st.markdown("### ⚙️ Nouvelle partie")

    # ── Formulaire de configuration ───────────────────────────────────────────
    theme = st.selectbox(
        "Thème",
        options=THEMES,
        format_func=lambda t: t.capitalize(),
    )
    difficulty = st.selectbox(
        "Difficulté",
        options=DIFFICULTIES,
        format_func=lambda d: d.capitalize(),
    )
    size_label = st.selectbox("Taille de la grille", options=list(SIZES.keys()))
    n_words = st.selectbox("Nombre de mots", options=WORD_COUNTS, index=1)
    timer_label = st.selectbox("⏱ Limite de temps", options=list(TIMER_OPTIONS.keys()))

    if st.button("🎲  Générer", use_container_width=True):
        rows, cols = SIZES[size_label]
        with st.spinner("Génération en cours — récupération des définitions Wiktionnaire…"):
            try:
                puzzle = generate_puzzle(
                    rows=rows,
                    cols=cols,
                    n_words=n_words,
                    theme=theme,
                    difficulty=difficulty,
                )
            except Exception as exc:
                st.error(f"Erreur de génération : {exc}")
                st.stop()

        state = GameState(puzzle=puzzle)
        state.answers[puzzle.words[0].number] = puzzle.words[0].answer
        st.session_state.puzzle = puzzle
        st.session_state.game_state = state
        st.session_state.current_word_idx = 1
        st.session_state.hint_active = False
        st.session_state.last_feedback = None
        st.session_state.answer_input_key = 0
        st.session_state.word_start_time = None
        st.session_state.game_timer_duration = TIMER_OPTIONS[timer_label]
        st.session_state.game_start_time = time.time() if TIMER_OPTIONS[timer_label] else None
        st.session_state.screen = "game"
        st.rerun()

    st.markdown("---")
    if st.button("← Retour"):
        st.session_state.screen = "home"
        st.rerun()
