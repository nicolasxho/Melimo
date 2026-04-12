"""
Rendu HTML de la liste des indices Mélimo.
"""
from __future__ import annotations
from models import Puzzle, GameState


def build_clues_html(
    puzzle: Puzzle,
    state: GameState,
    current_word_num: int | None,
) -> str:
    """Retourne un bloc HTML de la liste des indices avec statuts colorés."""

    css = """
<style>
.clue-table { width: 100%; border-collapse: collapse; font-family: 'Courier New', monospace; font-size: 0.85rem; }
.clue-table td { padding: 3px 6px; vertical-align: top; }
.clue-num  { color: #888; width: 24px; text-align: right; white-space: nowrap; }
.clue-ans  { width: 120px; font-weight: bold; white-space: nowrap; }
.clue-def  { color: #ccc; }
.ans-found   { color: #7dff7d; }
.ans-current { color: #ffd54f; }
.ans-hidden  { color: #555; letter-spacing: 2px; }
.def-current { color: #fff; font-weight: bold; }
.mystery-tag { color: #ce93d8; font-size: 0.75rem; }
.clue-row-current { background: #1e2a1e; border-radius: 4px; }
</style>
"""

    rows: list[str] = []
    max_len = max((w.length() for w in puzzle.words), default=10)

    for word in puzzle.words:
        is_current = (word.number == current_word_num)
        is_correct = state.is_word_correct(word.number)

        # Numéro
        num_html = f'<td class="clue-num">{word.number}.</td>'

        # Réponse ou tirets
        if is_correct:
            ans_html = f'<td class="clue-ans ans-found">{word.answer}</td>'
        elif is_current:
            if word.is_mystery and word.letter_count_hint:
                dashes = "_ " * word.letter_count_hint
            else:
                dashes = "_ " * word.length()
            ans_html = f'<td class="clue-ans ans-current">{dashes.strip()}</td>'
        else:
            if word.is_mystery and word.letter_count_hint:
                dashes = "_ " * word.letter_count_hint
            else:
                dashes = "_ " * word.length()
            ans_html = f'<td class="clue-ans ans-hidden">{dashes.strip()}</td>'

        # Définition
        if word.is_mystery:
            mystery_part = '<span class="mystery-tag"> ★ MOT MYSTÈRE</span>'
        else:
            mystery_part = ""

        if is_current:
            def_html = f'<td class="clue-def def-current">{word.definition}{mystery_part}</td>'
        else:
            def_html = f'<td class="clue-def">{word.definition}{mystery_part}</td>'

        row_class = ' class="clue-row-current"' if is_current else ""
        rows.append(f"<tr{row_class}>{num_html}{ans_html}{def_html}</tr>")

    table = '<table class="clue-table">' + "".join(rows) + "</table>"
    return css + table
