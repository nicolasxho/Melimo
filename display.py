"""
Rendu terminal du jeu Mélimo.
Utilise colorama pour la couleur (compatible Windows).
"""
from __future__ import annotations
import os
import sys

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init(autoreset=True)
    _COLOR = True
except ImportError:
    _COLOR = False

    class _Stub:
        def __getattr__(self, _): return ""

    Fore = Back = Style = _Stub()

from models import Cell, Puzzle, GameState, WordEntry


# ── Couleurs et styles ────────────────────────────────────────────────────────

def _c(text: str, fore: str = "", back: str = "", bold: bool = False) -> str:
    if not _COLOR:
        return text
    prefix = (Style.BRIGHT if bold else "") + fore + back
    return f"{prefix}{text}{Style.RESET_ALL}"


def _green(t: str) -> str:  return _c(t, Fore.GREEN, bold=True)
def _yellow(t: str) -> str: return _c(t, Fore.YELLOW, bold=True)
def _magenta(t: str) -> str: return _c(t, Fore.MAGENTA, bold=True)
def _cyan(t: str) -> str:   return _c(t, Fore.CYAN, bold=True)
def _dim(t: str) -> str:    return _c(t, Style.DIM if _COLOR else "")
def _bold(t: str) -> str:   return _c(t, bold=True)
def _red(t: str) -> str:    return _c(t, Fore.RED, bold=True)


# ── Utilitaires ───────────────────────────────────────────────────────────────

def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_banner() -> None:
    print()
    print(_bold("  ╔══════════════════════════════╗"))
    print(_bold("  ║") + _magenta("   M É L I M O               ") + _bold("║"))
    print(_bold("  ║") + _dim("   Jeu de mots en labyrinthe  ") + _bold("║"))
    print(_bold("  ╚══════════════════════════════╝"))
    print()


# ── Rendu de la grille ────────────────────────────────────────────────────────

def render_grid(
    puzzle: Puzzle,
    state: GameState,
    highlight_word: int | None = None,
) -> None:
    """
    Affiche la grille :
    - Mots déjà trouvés : lettres en vert
    - Mot en surbrillance (mode indice) : lettres en jaune
    - Tout le reste : grisé
    """
    # Cellules des mots déjà trouvés
    found_cells: set[Cell] = set()
    for word in puzzle.words:
        if state.is_word_correct(word.number):
            found_cells.update(word.cells(puzzle.path))

    # Cellules du mot en surbrillance (indice seulement)
    hint_cells: set[Cell] = set()
    if highlight_word is not None:
        word = puzzle.word_by_number(highlight_word)
        if word:
            hint_cells = set(word.cells(puzzle.path))

    # En-tête des colonnes
    col_header = "       " + "".join(f"{c + 1:>3}" for c in range(puzzle.cols))
    print(_dim(col_header))
    print(_dim("       " + "─" * (puzzle.cols * 3 + 1)))

    # Lignes
    for r in range(puzzle.rows):
        row_label = chr(ord("a") + r)
        line = f"  {_dim(row_label)} {_dim('│')} "

        for c in range(puzzle.cols):
            cell = Cell(r, c)
            letter = puzzle.grid[r][c]

            if cell in hint_cells:
                rendered = f" {_yellow(letter)} "
            elif cell in found_cells:
                rendered = f" {_green(letter)} "
            else:
                rendered = f" {_dim(letter)} "

            line += rendered

        print(line)

    print()


# ── Rendu des définitions ─────────────────────────────────────────────────────

def render_clues(
    puzzle: Puzzle,
    state: GameState,
    current_word_number: int | None = None,
) -> None:
    """
    Affiche les définitions en colonne unique, toutes alignées.
    - Mots trouvés : réponse en vert + définition grisée
    - Mot en cours : tirets jaunes + définition en gras
    - Mots à venir : tirets + définition grisée
    """
    print(_bold("  DÉFINITIONS :"))
    print()

    # Largeur fixe pour la colonne "réponse/tirets" : longueur du mot le plus long
    max_len = max(w.length() for w in puzzle.words)

    for word in puzzle.words:
        print("  " + _format_clue(word, state, current_word_number, max_len))

    print()


def _format_clue(
    word: WordEntry,
    state: GameState,
    current_word_number: int | None,
    max_len: int,
) -> str:
    """
    Formate une ligne de définition avec alignement fixe.
    Colonnes : [numéro]  [réponse/tirets padded]  [définition]
    Le padding est appliqué sur le texte visible AVANT la couleur,
    pour que les codes ANSI ne décalent pas l'alignement.
    """
    num = f"{word.number:>2}."
    hint = f" ({word.letter_count_hint})" if word.letter_count_hint else ""
    definition = word.definition or "(pas de définition)"
    is_current = (word.number == current_word_number)

    if state.is_word_correct(word.number):
        # Réponse visible — padder d'abord, coloriser ensuite
        answer_padded = f"{word.answer:<{max_len}}"
        mystery_tag = " ★" if word.is_mystery else ""
        return f"{num} {_green(answer_padded + mystery_tag)}  {_dim(definition)}"

    elif is_current:
        blanks_padded = f"{'_' * word.length():<{max_len}}"
        if word.is_mystery:
            mystery_label = _magenta(f"★ MOT MYSTÈRE{hint}")
            return f"{num} {_yellow(blanks_padded)}  {mystery_label}  {_bold(definition)}"
        return f"{num} {_yellow(blanks_padded)}  {_bold(definition)}"

    else:
        blanks_padded = f"{'_' * word.length():<{max_len}}"
        if word.is_mystery:
            mystery_label = _dim(f"★ MOT MYSTÈRE{hint}")
            return f"{num} {_dim(blanks_padded)}  {mystery_label}  {_dim(definition)}"
        return f"{num} {_dim(blanks_padded)}  {_dim(definition)}"


# ── Rendu du score ────────────────────────────────────────────────────────────

def render_score(state: GameState) -> None:
    """Affiche le score et la progression."""
    correct = state.answered_count()
    total = len(state.puzzle.words)

    score_str = _green(f"{state.score} pt{'s' if state.score > 1 else ''}")
    progress = f"{correct}/{total}"
    mystery_str = _magenta(" + MOT MYSTÈRE !") if state.mystery_found else ""

    print(f"  Score : {score_str}{mystery_str}   |   Trouvés : {progress}   |   Lettres inutiles : {state.puzzle.unused_count}")
    print()


# ── Affichage d'un résultat ───────────────────────────────────────────────────

def print_correct(word: WordEntry) -> None:
    print()
    print(f"  {_green('✓ CORRECT !')}  {_bold(word.answer)}")
    if word.is_mystery:
        print(f"  {_magenta('🎉 MOT MYSTÈRE découvert ! +1 point bonus !')}")
    print()


def print_wrong(player_input: str, word: WordEntry) -> None:
    print()
    print(f"  {_red('✗ Mauvaise réponse.')}  Vous avez saisi : {_bold(player_input.upper())}")
    print()


# ── Écran de fin ──────────────────────────────────────────────────────────────

def render_final_score(state: GameState) -> None:
    """Affiche le score final et toutes les réponses."""
    clear_screen()
    print_banner()
    print(_bold("  ══ PARTIE TERMINÉE ══"))
    print()

    for word in state.puzzle.words:
        correct = state.is_word_correct(word.number)
        marker = _green("✓") if correct else _dim("○")
        mystery_tag = _magenta(" ★") if word.is_mystery else ""
        answer_str = _green(word.answer) if correct else _dim("?????")
        print(f"  {marker} {word.number:>2}. {answer_str:<15} {_dim(word.definition)}{mystery_tag}")

    print()
    render_score(state)

    total = len(state.puzzle.words)
    correct = state.answered_count()
    if correct == total:
        print(_green("  Bravo ! Puzzle complété à 100% !"))
    elif correct >= total * 0.7:
        print(_yellow(f"  Bien joué ! {correct}/{total} mots trouvés."))
    else:
        print(_dim(f"  {correct}/{total} mots trouvés. Continuez à vous entraîner !"))
    print()
