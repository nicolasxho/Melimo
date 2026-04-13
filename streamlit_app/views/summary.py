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
    # correct = mots trouvés par le joueur (sans révélation)
    correct = sum(1 for w in puzzle.words if state.is_word_correct(w.number))
    revealed_count = len(state.revealed)
    # answered = total des mots résolus (trouvés + révélés)
    answered = correct + revealed_count
    pct = int(answered / total * 100) if total else 0
    total_errors = sum(state.errors.values())
    total_hints = sum(state.hints.values())

    st.markdown(
        "<h2 style='text-align:center; color:#4caf50;'>PARTIE TERMINÉE</h2>",
        unsafe_allow_html=True,
    )

    # ── Métriques globales ────────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Score", f"{state.score} pts")
    m2.metric("Mots trouvés", f"{answered}/{total}")
    m3.metric("Réussite", f"{pct}%")
    m4.metric("Erreurs", str(total_errors))
    m5.metric("Indices", str(total_hints))

    if pct == 100 and revealed_count == 0:
        st.balloons()
        st.success("🏆 Parfait ! Tous les mots trouvés sans aide !")
    elif pct == 100:
        st.success(f"✅ Puzzle complété ! ({correct} trouvé{'s' if correct > 1 else ''}, {revealed_count} révélé{'s' if revealed_count > 1 else ''})")
    elif pct >= 70:
        st.info("👍 Bien joué !")
    else:
        st.warning("Continuez à vous entraîner !")

    st.markdown("---")
    st.markdown("#### Récapitulatif")

    # ── Tableau des mots ──────────────────────────────────────────────────────
    rows_html: list[str] = []
    for word in puzzle.words:
        is_correct = state.is_word_correct(word.number)
        is_revealed = word.number in state.revealed
        mystery = " ★" if word.is_mystery else ""

        if is_revealed:
            ans_style = "color:#aaa; font-style:italic;"
            ans_text = f"{word.answer} (révélé)"
        elif is_correct:
            ans_style = "color:#7dff7d;"
            ans_text = word.answer
        else:
            ans_style = "color:#f44336;"
            ans_text = "—"

        word_errors = state.errors.get(word.number, 0)
        word_hints = state.hints.get(word.number, 0)
        word_elapsed = state.word_elapsed.get(word.number)

        elapsed_cell = (
            f"<span style='color:#aaa;'>{int(word_elapsed)}s</span>"
            if word_elapsed is not None
            else "<span style='color:#555;'>—</span>"
        )
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
            f"<td style='padding:4px 8px;text-align:center;'>{elapsed_cell}</td>"
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
        "<th style='text-align:center;padding:4px 8px;color:#555;'>Temps</th>"
        "<th style='text-align:center;padding:4px 8px;color:#555;'>Erreurs</th>"
        "<th style='text-align:center;padding:4px 8px;color:#555;'>Indices</th>"
        "</tr></thead><tbody>"
        + "".join(rows_html)
        + "</tbody></table>"
    )
    st.markdown(table_html, unsafe_allow_html=True)

    # ── Barème ────────────────────────────────────────────────────────────────
    st.markdown("---")
    hint_costs = " / ".join(f"−{c} pts" for c in scoring.HINT_PENALTIES)
    st.markdown(
        f"**Barème** : base {scoring.BASE_SCORE} pts/mot · "
        f"−{scoring.TIME_PENALTY_RATE:.0f} pts/sec · "
        f"−{scoring.ERROR_PENALTY} pts/erreur · "
        f"indices progressifs {hint_costs} · "
        f"mot mystère ×{scoring.MYSTERY_MULTIPLIER} · "
        f"minimum {scoring.MIN_WORD_SCORE} pts/mot"
    )

    st.markdown("---")
    if st.button("🔄 Rejouer", use_container_width=True):
        reset_game()
        st.rerun()
