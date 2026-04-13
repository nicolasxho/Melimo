"""
Écran 3 — Résumé de fin de partie.
"""
from __future__ import annotations
import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from streamlit_app.state import reset_game
import scoring


def render() -> None:
    puzzle = st.session_state.puzzle
    state = st.session_state.game_state

    if puzzle is None or state is None:
        reset_game()
        return

    total = len(puzzle.words)
    correct = sum(1 for w in puzzle.words if state.is_word_correct(w.number))
    pct = int(correct / total * 100) if total else 0
    total_errors = sum(state.errors.values())
    total_hints = sum(state.hints.values())

    st.markdown(
        "<h2 style='text-align:center; color:#4caf50;'>PARTIE TERMINÉE</h2>",
        unsafe_allow_html=True,
    )

    # Métriques
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Score", f"{state.score} pts")
    m2.metric("Mots trouvés", f"{correct}/{total}")
    m3.metric("Réussite", f"{pct}%")
    m4.metric("Erreurs", str(total_errors))
    m5.metric("Indices", str(total_hints))

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

        word_errors = state.errors.get(word.number, 0)
        word_hints = state.hints.get(word.number, 0)

        # Score par mot
        if is_correct and word.number in state.word_start_times:
            elapsed = state.word_start_times.get(word.number, 0)
            # elapsed stored as start timestamp; if not recalculated, show "?"
            # We stored the start time; without end time we can't recompute.
            # Use the score already computed — display a dash for time.
            score_cell = "—"
        elif is_correct:
            score_cell = "—"
        else:
            score_cell = "—"

        err_cell = (
            f"<span style='color:#f44336;'>✗ {word_errors}</span>" if word_errors else
            "<span style='color:#555;'>—</span>"
        )
        hint_cell = (
            f"<span style='color:#ffb300;'>💡 {word_hints}</span>" if word_hints else
            "<span style='color:#555;'>—</span>"
        )

        rows_html.append(
            f"<tr>"
            f"<td style='padding:4px 8px;color:#888;'>{word.number}{mystery}</td>"
            f"<td style='padding:4px 8px;{ans_style}font-weight:bold;'>{ans_text}</td>"
            f"<td style='padding:4px 8px;color:#ccc;'>{word.definition}</td>"
            f"<td style='padding:4px 8px;text-align:center;'>{err_cell}</td>"
            f"<td style='padding:4px 8px;text-align:center;'>{hint_cell}</td>"
            f"</tr>"
        )

    table_html = (
        "<table style='width:100%;border-collapse:collapse;font-family:monospace;font-size:0.85rem;'>"
        "<thead><tr>"
        "<th style='text-align:left;padding:4px 8px;color:#555;'>#</th>"
        "<th style='text-align:left;padding:4px 8px;color:#555;'>Réponse</th>"
        "<th style='text-align:left;padding:4px 8px;color:#555;'>Définition</th>"
        "<th style='text-align:center;padding:4px 8px;color:#555;'>Erreurs</th>"
        "<th style='text-align:center;padding:4px 8px;color:#555;'>Indices</th>"
        "</tr></thead><tbody>"
        + "".join(rows_html)
        + "</tbody></table>"
    )
    st.markdown(table_html, unsafe_allow_html=True)

    # Rappel des règles de scoring
    st.markdown("---")
    st.markdown(
        f"**Barème** : base {scoring.BASE_SCORE} pts/mot · "
        f"-{scoring.ERROR_PENALTY} pts/erreur · "
        f"-{scoring.HINT_PENALTY} pts/indice · "
        f"-{scoring.TIME_PENALTY_RATE:.0f} pts/sec · "
        f"mot mystère ×{scoring.MYSTERY_MULTIPLIER} · "
        f"minimum {scoring.MIN_WORD_SCORE} pts/mot"
    )

    st.markdown("---")
    if st.button("🔄 Rejouer", use_container_width=True):
        reset_game()
        st.rerun()
