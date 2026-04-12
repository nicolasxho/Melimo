"""
Lance generate_puzzle() dans un thread daemon pour ne pas bloquer Streamlit.
"""
from __future__ import annotations
import threading
import sys
import os

# S'assurer que la racine du projet est dans le path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generator.grid_builder import generate_puzzle


def start_generation(config: dict, state) -> None:
    """
    Démarre la génération d'un puzzle dans un thread daemon.
    Écrit le résultat dans state.generation_result ou state.generation_error,
    puis met state.generating = False.

    config doit contenir : rows, cols, n_words, theme, difficulty.
    state est st.session_state.
    """

    def _run() -> None:
        try:
            puzzle = generate_puzzle(
                rows=config["rows"],
                cols=config["cols"],
                n_words=config["n_words"],
                theme=config.get("theme"),
                difficulty=config.get("difficulty", "moyen"),
            )
            state.generation_result = puzzle
        except Exception as exc:
            state.generation_error = str(exc)
        finally:
            state.generating = False

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
