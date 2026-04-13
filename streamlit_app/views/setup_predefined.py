"""
Écran 1a — Sélection d'un puzzle pré-défini.
"""
from __future__ import annotations
import os
import sys
import time
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from loader import load_puzzle, PuzzleLoadError
from models import GameState, Puzzle


def _init_first_word(state: GameState, puzzle: Puzzle) -> None:
    """Révèle le premier mot gratuitement et initialise ses compteurs."""
    if not puzzle.words:
        return
    first = puzzle.words[0]
    state.answers[first.number] = first.answer
    state.word_elapsed[first.number] = 0.0
    state.errors[first.number] = 0
    state.hints[first.number] = 0
    state.attempts[first.number] = []

PUZZLES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "puzzles",
)

TIMER_OPTIONS: dict[str, int | None] = {
    "Pas de limite": None,
    "3 minutes": 180,
    "5 minutes": 300,
    "10 minutes": 600,
}


def render() -> None:
    st.markdown("### 📂 Choisir un puzzle")

    # Lister les fichiers JSON
    try:
        files = sorted(f for f in os.listdir(PUZZLES_DIR) if f.endswith(".json"))
    except FileNotFoundError:
        st.error("Dossier puzzles/ introuvable.")
        files = []

    if not files:
        st.warning("Aucun puzzle disponible dans puzzles/.")
    else:
        selected = st.selectbox(
            "Puzzle",
            options=files,
            format_func=lambda f: os.path.splitext(f)[0].replace("_", " "),
        )
        timer_label = st.selectbox("⏱ Limite de temps", options=list(TIMER_OPTIONS.keys()))

        if st.button("▶  Jouer", use_container_width=True):
            path = os.path.join(PUZZLES_DIR, selected)
            try:
                puzzle = load_puzzle(path)
                state = GameState(puzzle=puzzle)
                # Révéler automatiquement le premier mot (gratuit, sans pénalité)
                _init_first_word(state, puzzle)
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
            except PuzzleLoadError as exc:
                st.error(f"Erreur de chargement : {exc}")

    st.markdown("---")
    if st.button("← Retour"):
        st.session_state.screen = "home"
        st.rerun()
