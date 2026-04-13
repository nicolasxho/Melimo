"""
Écran 2 — Boucle de jeu principale.
"""
from __future__ import annotations
import os
import sys
import time
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models import Cell
from validation import check_answer
from streamlit_app.components.grid import build_grid_html
from streamlit_app.components.clues import build_clues_html
import scoring


def render() -> None:
    puzzle = st.session_state.puzzle
    state = st.session_state.game_state

    if puzzle is None or state is None:
        st.session_state.screen = "home"
        st.rerun()
        return

    # Mot courant (0-based index dans puzzle.words)
    idx = st.session_state.current_word_idx
    total_words = len(puzzle.words)
    game_complete = idx >= total_words

    current_word = puzzle.words[idx] if not game_complete else None
    current_word_num = current_word.number if current_word else None

    # Initialiser le chronomètre dès qu'on arrive sur un nouveau mot
    if current_word is not None:
        if st.session_state.word_start_time is None:
            st.session_state.word_start_time = time.time()
            state.word_start_times[current_word.number] = st.session_state.word_start_time
            state.errors[current_word.number] = 0
            state.hints[current_word.number] = 0

    # Dernière lettre du dernier mot trouvé (repère de départ pour le joueur)
    start_hint_cell: Cell | None = None
    if idx > 0 and idx <= total_words:
        prev_word = puzzle.words[idx - 1]
        if state.is_word_correct(prev_word.number) and prev_word.end_index > 0:
            start_hint_cell = puzzle.path[prev_word.end_index - 1]

    # ── Titre + progression ───────────────────────────────────────────────────
    st.markdown(
        f"<h3 style='color:#4caf50; margin-bottom:4px;'>{puzzle.title}</h3>",
        unsafe_allow_html=True,
    )
    answered = sum(1 for w in puzzle.words if state.is_word_correct(w.number))
    st.progress(answered / total_words, text=f"{answered}/{total_words} mots trouvés")

    # ── Layout : grille (gauche) + indices/score (droite) ────────────────────
    col_grid, col_play = st.columns([3, 2])

    with col_grid:
        grid_html = build_grid_html(
            puzzle=puzzle,
            state=state,
            hint_active=st.session_state.hint_active,
            current_word_num=current_word_num,
            start_hint_cell=start_hint_cell,
        )
        st.markdown(grid_html, unsafe_allow_html=True)

        # ── Feedback du tour précédent ────────────────────────────────────────
        feedback = st.session_state.last_feedback
        if feedback:
            if feedback["kind"] == "correct":
                word_score = feedback.get("word_score", 0)
                elapsed = feedback.get("elapsed", 0)
                errors = feedback.get("errors", 0)
                hints = feedback.get("hints", 0)
                details = _score_details(word_score, elapsed, errors, hints)
                st.success(f"✓ Correct !  **{feedback['word'].answer}**  — +{word_score} pts\n\n{details}")
            elif feedback["kind"] == "mystery":
                word_score = feedback.get("word_score", 0)
                elapsed = feedback.get("elapsed", 0)
                errors = feedback.get("errors", 0)
                hints = feedback.get("hints", 0)
                details = _score_details(word_score, elapsed, errors, hints)
                st.success(f"🎉 MOT MYSTÈRE !  **{feedback['word'].answer}**  — +{word_score} pts\n\n{details}")
                st.balloons()
            elif feedback["kind"] == "wrong":
                penalty = scoring.ERROR_PENALTY
                st.error(f"✗ Mauvaise réponse. — -{penalty} pts de pénalité")
            elif feedback["kind"] == "hint":
                penalty = scoring.HINT_PENALTY
                st.warning(f"💡 Indice affiché — -{penalty} pts de pénalité")
            st.session_state.last_feedback = None

        # ── Fin de partie ─────────────────────────────────────────────────────
        if game_complete:
            st.success("Partie terminée !")
            if st.button("Voir le résumé", use_container_width=True):
                st.session_state.screen = "summary"
                st.rerun()

        # ── Saisie de la réponse (sous la grille, Enter = Valider) ────────────
        elif current_word is not None:
            if current_word.is_mystery:
                prompt = f"Mot {current_word.number} — ★ MOT MYSTÈRE ({current_word.letter_count_hint} lettres)"
            else:
                prompt = f"Mot {current_word.number}"

            answer_key = f"answer_{st.session_state.answer_input_key}"

            with st.form(key="answer_form", clear_on_submit=True):
                user_input = st.text_input(prompt, key=answer_key)
                form_col1, form_col2, form_col3 = st.columns(3)
                with form_col1:
                    submitted = st.form_submit_button("✓ Valider", use_container_width=True)
                with form_col2:
                    hint_clicked = st.form_submit_button("💡 Indice", use_container_width=True)
                with form_col3:
                    quit_clicked = st.form_submit_button("🚪 Quitter", use_container_width=True)

            if submitted and user_input.strip():
                if check_answer(user_input, current_word):
                    state.answers[current_word.number] = current_word.answer
                    elapsed = time.time() - (state.word_start_times.get(current_word.number) or time.time())
                    errors = state.errors.get(current_word.number, 0)
                    hints = state.hints.get(current_word.number, 0)
                    word_score = scoring.compute_word_score(current_word.is_mystery, elapsed, errors, hints)
                    state.score += word_score
                    if current_word.is_mystery:
                        state.mystery_found = True
                        st.session_state.last_feedback = {
                            "kind": "mystery",
                            "word": current_word,
                            "word_score": word_score,
                            "elapsed": int(elapsed),
                            "errors": errors,
                            "hints": hints,
                        }
                    else:
                        st.session_state.last_feedback = {
                            "kind": "correct",
                            "word": current_word,
                            "word_score": word_score,
                            "elapsed": int(elapsed),
                            "errors": errors,
                            "hints": hints,
                        }
                    st.session_state.answer_input_key += 1
                    st.session_state.hint_active = False
                    st.session_state.word_start_time = None  # reset pour le prochain mot
                    st.session_state.current_word_idx = idx + 1
                else:
                    state.errors[current_word.number] = state.errors.get(current_word.number, 0) + 1
                    st.session_state.last_feedback = {"kind": "wrong", "word": current_word}
                st.rerun()

            if hint_clicked:
                state.hints[current_word.number] = state.hints.get(current_word.number, 0) + 1
                st.session_state.hint_active = True
                st.session_state.last_feedback = {"kind": "hint", "word": current_word}
                st.rerun()

            if quit_clicked:
                st.session_state.screen = "summary"
                st.rerun()

    with col_play:
        st.metric("Score", f"{state.score} pt{'s' if state.score > 1 else ''}")
        clues_html = build_clues_html(puzzle, state, current_word_num)
        st.markdown(clues_html, unsafe_allow_html=True)


def _score_details(word_score: int, elapsed: int, errors: int, hints: int) -> str:
    """Construit une ligne de détail du score pour le feedback."""
    parts: list[str] = [f"⏱ {elapsed}s"]
    if errors:
        parts.append(f"✗ {errors} erreur{'s' if errors > 1 else ''} (-{errors * scoring.ERROR_PENALTY} pts)")
    if hints:
        parts.append(f"💡 {hints} indice{'s' if hints > 1 else ''} (-{hints * scoring.HINT_PENALTY} pts)")
    return " · ".join(parts)
