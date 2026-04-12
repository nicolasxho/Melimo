"""
Écran 3 — Résumé de fin de partie.
"""
from __future__ import annotations
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from streamlit_app.state import reset_game


def render() -> None:
    puzzle = st.session_state.puzzle
    state = st.session_state.game_state

    if puzzle is None or state is None:
        reset_game()
        return

    total = len(puzzle.words)
    correct = sum(1 for w in puzzle.words if state.is_word_correct(w.number))
    pct = int(correct / total * 100) if total else 0

    st.markdown(
        "<h2 style='text-align:center; color:#4caf50;'>PARTIE TERMINÉE</h2>",
        unsafe_allow_html=True,
    )

    # Métriques
    m1, m2, m3 = st.columns(3)
    m1.metric("Score", f"{state.score} pts")
    m2.metric("Mots trouvés", f"{correct}/{total}")
    m3.metric("Réussite", f"{pct}%")

    if pct == 100:
        st.balloons()
        st.success("🏆 Parfait ! Tous les mots trouvés !")
    elif pct >= 70:
        st.info("👍 Bien joué !")
    else:
        st.warning("Continuez à vous entraîner !")

    st.markdown("---")
    st.markdown("#### Récapitulatif")

    # Tableau des mots
    rows_html: list[str] = []
    for word in puzzle.words:
        is_correct = state.is_word_correct(word.number)
        mystery = " ★" if word.is_mystery else ""
        ans_style = "color:#7dff7d;" if is_correct else "color:#f44336;"
        ans_text = word.answer if is_correct else "—"
        rows_html.append(
            f"<tr>"
            f"<td style='padding:4px 8px;color:#888;'>{word.number}{mystery}</td>"
            f"<td style='padding:4px 8px;{ans_style}font-weight:bold;'>{ans_text}</td>"
            f"<td style='padding:4px 8px;color:#ccc;'>{word.definition}</td>"
            f"</tr>"
        )

    table_html = (
        "<table style='width:100%;border-collapse:collapse;font-family:monospace;font-size:0.85rem;'>"
        "<thead><tr>"
        "<th style='text-align:left;padding:4px 8px;color:#555;'>#</th>"
        "<th style='text-align:left;padding:4px 8px;color:#555;'>Réponse</th>"
        "<th style='text-align:left;padding:4px 8px;color:#555;'>Définition</th>"
        "</tr></thead><tbody>"
        + "".join(rows_html)
        + "</tbody></table>"
    )
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 Rejouer", use_container_width=True):
        reset_game()
        st.rerun()
