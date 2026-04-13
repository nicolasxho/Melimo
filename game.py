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
        while not state.is_word_correct(word.number):
            _render_full_screen(state, current_word=word.number)
            _print_word_prompt(word)

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
                state.hints[word.number] = state.hints.get(word.number, 0) + 1
                _show_hint(state, word)
                continue

            # Tentative de réponse
            state.answers[word.number] = raw
            if check_answer(raw, word):
                elapsed = time.time() - state.word_start_times[word.number]
                errors = state.errors.get(word.number, 0)
                hints = state.hints.get(word.number, 0)
                word_score = scoring.compute_word_score(word.is_mystery, elapsed, errors, hints)
                state.score += word_score
                if word.is_mystery:
                    state.mystery_found = True
                display.print_correct(word, word_score, int(elapsed), errors, hints)
                input("  [Entrée] pour continuer...")
                break  # Passer au mot suivant
            else:
                state.errors[word.number] = state.errors.get(word.number, 0) + 1
                display.print_wrong(raw, word)
                # Effacer la mauvaise réponse pour permettre de réessayer
                del state.answers[word.number]
                input("  [Entrée] pour réessayer...")

    # Tous les mots trouvés
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


def _print_word_prompt(word: WordEntry) -> None:
    """Affiche les instructions pour le mot courant."""
    mystery_tag = "  ★ MOT MYSTÈRE ★" if word.is_mystery else ""
    hint = f"  ({word.letter_count_hint} lettres)" if word.letter_count_hint else ""
    print(f"  Mot {word.number}{mystery_tag}{hint}")
    print()
    print("  'h' = indice sur la grille   'q' = quitter")


def _show_hint(state: GameState, word: WordEntry) -> None:
    """Affiche la position du mot en surbrillance sur la grille."""
    _render_full_screen(state, current_word=word.number, grid_highlight=word.number)
    first = word.start_cell(state.puzzle.path)
    mystery_tag = "  ★ MOT MYSTÈRE ★" if word.is_mystery else ""
    print(f"  Mot {word.number}{mystery_tag}")
    print(f"  Première lettre dans la grille : {first.label()}")
    if word.letter_count_hint:
        print(f"  Nombre de lettres : {word.letter_count_hint}")
    print()
    input("  [Entrée] pour revenir...")


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
