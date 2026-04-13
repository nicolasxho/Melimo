"""
Boucle de jeu Mélimo.
Les mots sont résolus dans l'ordre. Aucune sélection ni révélation possible.
"""
from __future__ import annotations
import os
import time

from models import Puzzle, GameState, WordEntry
from validation import check_answer
import display
import scoring


def run_game(puzzle: Puzzle) -> None:
    """Boucle principale d'une partie — résolution séquentielle des mots."""
    state = GameState(puzzle=puzzle)

    # Le mot #1 est le mot de départ, révélé gratuitement
    if puzzle.words:
        first = puzzle.words[0]
        state.answers[first.number] = first.answer
        _render_full_screen(state, current_word=None)
        print(f"  Le mot de départ est : {first.answer}")
        print()
        try:
            input("  [Entrée] pour commencer à jouer...")
        except (EOFError, KeyboardInterrupt):
            _quit_game(state)
            return

    for word in puzzle.words[1:]:
        # Enregistrer le moment de début pour ce mot
        state.word_start_times[word.number] = time.time()
        state.errors[word.number] = 0
        state.hints[word.number] = 0

        # Boucle interne : répéter jusqu'à la bonne réponse ou abandon
        while not state.is_word_correct(word.number) and word.number not in state.revealed:
            _render_full_screen(state, current_word=word.number)
            _print_word_prompt(word, state.hints.get(word.number, 0))

            try:
                raw = input("  > ").strip()
            except (EOFError, KeyboardInterrupt):
                _quit_game(state)
                return

            if not raw:
                continue

            if raw.lower() == "q":
                _quit_game(state)
                return

            if raw.lower() == "h":
                hints_used = state.hints.get(word.number, 0)
                if hints_used >= scoring.MAX_HINTS:
                    print("  Tous les indices ont déjà été utilisés.")
                    input("  [Entrée] pour continuer...")
                else:
                    state.hints[word.number] = hints_used + 1
                    _show_hint(state, word, state.hints[word.number])
                continue

            if raw.lower() == "r":
                _reveal_word(state, word)
                break

            # Tentative de réponse
            state.answers[word.number] = raw
            if check_answer(raw, word):
                elapsed = time.time() - state.word_start_times[word.number]
                state.word_elapsed[word.number] = elapsed
                errors = state.errors.get(word.number, 0)
                hints = state.hints.get(word.number, 0)
                word_score = scoring.compute_word_score(word.is_mystery, elapsed, errors, hints)
                state.score += word_score
                if word.is_mystery:
                    state.mystery_found = True
                display.print_correct(word, word_score, int(elapsed), errors, hints)
                input("  [Entrée] pour continuer...")
                break
            else:
                state.errors[word.number] = state.errors.get(word.number, 0) + 1
                display.print_wrong(raw, word)
                del state.answers[word.number]
                input("  [Entrée] pour réessayer...")

    # Tous les mots traités
    display.render_final_score(state)
    input("  Appuyez sur Entrée pour continuer...")


def _render_full_screen(
    state: GameState,
    current_word: int | None = None,
    grid_highlight: int | None = None,
) -> None:
    display.clear_screen()
    display.print_banner()
    print(f"  {state.puzzle.title}")
    if state.puzzle.theme:
        print(f"  Thème : {state.puzzle.theme}")
    print()
    display.render_grid(state.puzzle, state, highlight_word=grid_highlight)
    display.render_clues(state.puzzle, state, current_word_number=current_word)
    display.render_score(state)


def _print_word_prompt(word: WordEntry, hints_used: int) -> None:
    """Affiche les instructions pour le mot courant."""
    mystery_tag = "  ★ MOT MYSTÈRE ★" if word.is_mystery else ""
    print(f"  Mot {word.number}{mystery_tag}")
    print()
    next_cost = scoring.hint_next_cost(hints_used)
    if next_cost is not None:
        next_label = scoring.hint_next_label(hints_used)
        print(f"  'h' = indice suivant ({next_label}, −{next_cost} pts)   'r' = révéler (0 pt)   'q' = quitter")
    else:
        print(f"  'r' = révéler (0 pt)   'q' = quitter")


def _show_hint(state: GameState, word: WordEntry, hint_level: int) -> None:
    """Affiche l'indice du niveau demandé."""
    _render_full_screen(state, current_word=word.number, grid_highlight=word.number if hint_level >= 3 else None)
    mystery_tag = "  ★ MOT MYSTÈRE ★" if word.is_mystery else ""
    print(f"  Mot {word.number}{mystery_tag}  — Indice {hint_level}")

    if hint_level >= 1:
        print(f"  Nombre de lettres : {word.length()}")
    if hint_level >= 2:
        first_letter = word.answer[0]
        print(f"  Première lettre : {first_letter}")
    if hint_level >= 3:
        first_cell = word.start_cell(state.puzzle.path)
        print(f"  Première case dans la grille : {first_cell.label()}")

    cost = scoring.HINT_PENALTIES[hint_level - 1]
    print(f"  (Pénalité de cet indice : −{cost} pts)")
    print()
    input("  [Entrée] pour revenir...")


def _reveal_word(state: GameState, word: WordEntry) -> None:
    """Révèle la réponse du mot courant pour 0 point."""
    state.revealed.add(word.number)
    state.answers[word.number] = word.answer
    state.word_elapsed[word.number] = time.time() - state.word_start_times.get(word.number, time.time())
    display.clear_screen()
    display.print_banner()
    print(f"  Mot {word.number} révélé : {word.answer}  (0 point)")
    print()
    input("  [Entrée] pour continuer...")


def _quit_game(state: GameState) -> None:
    """Affiche le score final en cas d'abandon."""
    display.render_final_score(state)
    input("  Appuyez sur Entrée pour continuer...")


def run_menu(puzzles_dir: str = "puzzles") -> Puzzle | None:
    """
    Affiche le menu de sélection de puzzles pré-définis.
    Retourne le puzzle choisi ou None pour annuler.
    """
    from loader import list_puzzles, load_puzzle, PuzzleLoadError

    files = list_puzzles(puzzles_dir)
    if not files:
        return None

    display.clear_screen()
    display.print_banner()
    print("  Puzzles disponibles :\n")

    for i, filepath in enumerate(files, 1):
        name = os.path.splitext(os.path.basename(filepath))[0]
        print(f"    {i}. {name}")

    print()

    while True:
        try:
            raw = input("  Votre choix (ou Entrée pour annuler) : ").strip()
        except (EOFError, KeyboardInterrupt):
            return None

        if not raw:
            return None

        try:
            idx = int(raw) - 1
            if 0 <= idx < len(files):
                try:
                    return load_puzzle(files[idx])
                except PuzzleLoadError as e:
                    print(f"  Erreur : {e}")
                    return None
            else:
                print("  Numéro invalide.")
        except ValueError:
            print("  Entrez un numéro.")
