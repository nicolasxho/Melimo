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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _elapsed_now(word_number: int, state) -> float:
    """Secondes écoulées depuis le début du mot courant."""
    start = state.word_start_times.get(word_number)
    return time.time() - start if start else 0.0


def _score_details(word_score: int, elapsed: int, errors: int, hints: int) -> str:
    """Ligne de détail du score pour le feedback."""
    parts: list[str] = [f"⏱ {elapsed}s"]
    if errors:
        parts.append(f"✗ {errors} erreur{'s' if errors > 1 else ''} (−{errors * scoring.ERROR_PENALTY} pts)")
    if hints:
        hp = scoring.hint_total_penalty(hints)
        parts.append(f"💡 {hints} indice{'s' if hints > 1 else ''} (−{hp} pts)")
    return " · ".join(parts)


def _timer_remaining() -> float | None:
    """Secondes restantes, ou None si pas de timer."""
    duration = st.session_state.get("game_timer_duration")
    start = st.session_state.get("game_start_time")
    if duration is None or start is None:
        return None
    return max(0.0, duration - (time.time() - start))


def _fmt_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


# ── Vue principale ────────────────────────────────────────────────────────────

def render() -> None:
    puzzle = st.session_state.puzzle
    state = st.session_state.game_state

    if puzzle is None or state is None:
        st.session_state.screen = "home"
        st.rerun()
        return

    # ── Vérification du timer ─────────────────────────────────────────────────
    remaining = _timer_remaining()
    if remaining is not None and remaining <= 0:
        st.session_state.screen = "summary"
        st.rerun()
        return

    # Mot courant (0-based index dans puzzle.words)
    idx = st.session_state.current_word_idx
    total_words = len(puzzle.words)
    game_complete = idx >= total_words

    current_word = puzzle.words[idx] if not game_complete else None
    current_word_num = current_word.number if current_word else None

    # Initialiser le chronomètre et les compteurs dès qu'on arrive sur un nouveau mot
    if current_word is not None:
        if st.session_state.word_start_time is None:
            st.session_state.word_start_time = time.time()
            state.word_start_times[current_word.number] = st.session_state.word_start_time
            state.errors[current_word.number] = 0
            state.hints[current_word.number] = 0
            state.attempts[current_word.number] = []

    # Dernière lettre du dernier mot trouvé (repère de départ pour le joueur)
    start_hint_cell: Cell | None = None
    if idx > 0 and idx <= total_words:
        prev_word = puzzle.words[idx - 1]
        if state.is_word_correct(prev_word.number) and prev_word.end_index > 0:
            start_hint_cell = puzzle.path[prev_word.end_index - 1]

    # ── Titre + timer + progression ───────────────────────────────────────────
    title_col, timer_col = st.columns([4, 1])
    with title_col:
        st.markdown(
            f"<h3 style='color:#4caf50; margin-bottom:4px;'>{puzzle.title}</h3>",
            unsafe_allow_html=True,
        )
    with timer_col:
        if remaining is not None:
            color = "#f44336" if remaining < 60 else "#ff9800" if remaining < 120 else "#4caf50"
            st.markdown(
                f"<div style='text-align:right; font-size:1.4rem; font-weight:bold;"
                f" color:{color}; padding-top:8px;'>⏱ {_fmt_time(remaining)}</div>",
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
            kind = feedback["kind"]
            if kind in ("correct", "mystery"):
                ws = feedback.get("word_score", 0)
                details = _score_details(
                    ws,
                    feedback.get("elapsed", 0),
                    feedback.get("errors", 0),
                    feedback.get("hints", 0),
                )
                icon = "🎉 MOT MYSTÈRE !" if kind == "mystery" else "✓ Correct !"
                st.success(f"{icon}  **{feedback['word'].answer}**  — +{ws} pts\n\n{details}")
                if kind == "mystery":
                    st.balloons()
            elif kind == "wrong":
                st.error(f"✗ Mauvaise réponse. — −{scoring.ERROR_PENALTY} pts de pénalité")
            elif kind == "hint":
                level = feedback.get("hint_level", 1)
                cost = scoring.HINT_PENALTIES[level - 1]
                label = scoring.HINT_LABELS[level - 1]
                st.warning(f"💡 Indice {level} — {label} (−{cost} pts)")
            elif kind == "reveal":
                st.info(f"👁 Mot révélé : **{feedback['word'].answer}** — 0 pt")
            st.session_state.last_feedback = None

        # ── Fin de partie ─────────────────────────────────────────────────────
        if game_complete:
            st.success("Partie terminée !")
            if st.button("Voir le résumé", use_container_width=True):
                st.session_state.screen = "summary"
                st.rerun()

        # ── Saisie de la réponse ──────────────────────────────────────────────
        elif current_word is not None:
            if current_word.is_mystery:
                prompt = f"Mot {current_word.number} — ★ MOT MYSTÈRE ({current_word.letter_count_hint} lettres)"
            else:
                prompt = f"Mot {current_word.number}"

            answer_key = f"answer_{st.session_state.answer_input_key}"
            hints_used = state.hints.get(current_word.number, 0)
            next_cost = scoring.hint_next_cost(hints_used)

            with st.form(key="answer_form", clear_on_submit=True):
                user_input = st.text_input(prompt, key=answer_key)
                fc1, fc2, fc3, fc4 = st.columns(4)
                with fc1:
                    submitted = st.form_submit_button("✓ Valider", use_container_width=True)
                with fc2:
                    hint_label = (
                        f"💡 Indice {hints_used + 1} (−{next_cost} pts)"
                        if next_cost is not None
                        else "💡 Indices épuisés"
                    )
                    hint_clicked = st.form_submit_button(hint_label, use_container_width=True)
                with fc3:
                    reveal_clicked = st.form_submit_button("👁 Révéler (0 pt)", use_container_width=True)
                with fc4:
                    quit_label = "⚠️ Confirmer ?" if st.session_state.confirm_quit else "🚪 Quitter"
                    quit_clicked = st.form_submit_button(quit_label, use_container_width=True)

            # ── Historique des tentatives ─────────────────────────────────────
            prev_attempts = state.attempts.get(current_word.number, [])
            if prev_attempts:
                attempts_str = "  ·  ".join(f"~~{a}~~" for a in prev_attempts[-5:])
                st.caption(f"Essais précédents : {attempts_str}")

            # ── Traitement des actions ────────────────────────────────────────
            if submitted and user_input.strip():
                st.session_state.confirm_quit = False
                if check_answer(user_input, current_word):
                    state.answers[current_word.number] = current_word.answer
                    elapsed = _elapsed_now(current_word.number, state)
                    state.word_elapsed[current_word.number] = elapsed
                    errors = state.errors.get(current_word.number, 0)
                    hints = state.hints.get(current_word.number, 0)
                    word_score = scoring.compute_word_score(current_word.is_mystery, elapsed, errors, hints)
                    state.score += word_score
                    if current_word.is_mystery:
                        state.mystery_found = True
                    st.session_state.last_feedback = {
                        "kind": "mystery" if current_word.is_mystery else "correct",
                        "word": current_word,
                        "word_score": word_score,
                        "elapsed": int(elapsed),
                        "errors": errors,
                        "hints": hints,
                    }
                    st.session_state.answer_input_key += 1
                    st.session_state.hint_active = False
                    st.session_state.word_start_time = None
                    st.session_state.current_word_idx = idx + 1
                else:
                    state.errors[current_word.number] = state.errors.get(current_word.number, 0) + 1
                    attempts = state.attempts.setdefault(current_word.number, [])
                    attempts.append(user_input.strip().upper())
                    st.session_state.last_feedback = {"kind": "wrong", "word": current_word}
                st.rerun()

            if hint_clicked and next_cost is not None:
                st.session_state.confirm_quit = False
                if not state.is_word_correct(current_word.number):
                    new_level = hints_used + 1
                    state.hints[current_word.number] = new_level
                    if new_level >= 3:
                        st.session_state.hint_active = True
                    st.session_state.last_feedback = {
                        "kind": "hint",
                        "word": current_word,
                        "hint_level": new_level,
                    }
                    st.rerun()

            if reveal_clicked:
                st.session_state.confirm_quit = False
                state.revealed.add(current_word.number)
                state.answers[current_word.number] = current_word.answer
                elapsed = _elapsed_now(current_word.number, state)
                state.word_elapsed[current_word.number] = elapsed
                st.session_state.last_feedback = {"kind": "reveal", "word": current_word}
                st.session_state.answer_input_key += 1
                st.session_state.hint_active = False
                st.session_state.word_start_time = None
                st.session_state.current_word_idx = idx + 1
                st.rerun()

            if quit_clicked:
                if st.session_state.confirm_quit:
                    # Deuxième clic → on quitte vraiment
                    st.session_state.confirm_quit = False
                    st.session_state.screen = "summary"
                    st.rerun()
                else:
                    # Premier clic → demande confirmation
                    st.session_state.confirm_quit = True
                    st.rerun()

        # Annuler la confirmation si le joueur fait autre chose
        if not game_complete and current_word is not None:
            if st.session_state.confirm_quit:
                st.warning("Clique à nouveau sur **⚠️ Confirmer ?** pour abandonner la partie, ou joue pour annuler.")

    # ── Panneau droit : score + score potentiel + indices révélés ────────────
    with col_play:
        st.metric("Score", f"{state.score} pt{'s' if state.score > 1 else ''}")

        # Score potentiel en temps réel
        if current_word is not None and not game_complete:
            elapsed_now = _elapsed_now(current_word.number, state)
            errors_now = state.errors.get(current_word.number, 0)
            hints_now = state.hints.get(current_word.number, 0)
            potential = scoring.compute_word_score(
                current_word.is_mystery, elapsed_now, errors_now, hints_now
            )
            label = "★ Score potentiel" if current_word.is_mystery else "Score potentiel"
            st.metric(label, f"+{potential} pts")

            # Indices déjà obtenus
            if hints_now >= 1:
                st.markdown(f"**Indice 1** — {current_word.length()} lettres")
            if hints_now >= 2:
                st.markdown(f"**Indice 2** — Commence par **{current_word.answer[0]}**")

        clues_html = build_clues_html(puzzle, state, current_word_num)
        st.markdown(clues_html, unsafe_allow_html=True)

    # ── Auto-refresh si timer actif ───────────────────────────────────────────
    if remaining is not None:
        st.markdown(
            "<script>setTimeout(function(){window.location.reload()}, 10000);</script>",
            unsafe_allow_html=True,
        )
