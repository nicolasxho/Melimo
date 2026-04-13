"""
Rendu HTML de la liste des indices Mélimo.
"""
from __future__ import annotations
from models import Puzzle, GameState


def _def_cell_content(word) -> str:
    """Retourne le HTML de la définition, avec tooltip si elle est tronquée."""
    display = word.definition
    full = getattr(word, "full_definition", None)
    if display.endswith("...") and full and full != display:
        escaped = full.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
        return (
            f'<span class="tooltip-wrap">{display}'
            f'<span class="tooltip-box">{escaped}</span></span>'
        )
    return display


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
.clue-num  { color: #aaa; width: 24px; text-align: right; white-space: nowrap; }
.clue-ans  { width: 120px; font-weight: bold; white-space: nowrap; }
.clue-def  { color: #d8d8d8; }
.ans-found   { color: #50ff80; }
.ans-current { color: #ffd740; }
.ans-hidden  { color: #888; letter-spacing: 2px; }
.def-current { color: #fff; font-weight: bold; }
.mystery-tag { color: #d9a0f0; font-size: 0.75rem; }
.clue-row-current { background: #0d2d1a; border-left: 3px solid #50ff80; border-radius: 4px; }
.tooltip-wrap { position: relative; cursor: help; border-bottom: 1px dotted #888; }
.tooltip-wrap .tooltip-box {
    display: none; position: absolute; bottom: 125%; left: 0;
    background: #2a2a2a; color: #eee; border: 1px solid #555;
    border-radius: 6px; padding: 6px 10px; font-size: 0.8rem;
    width: 280px; z-index: 999; white-space: normal; line-height: 1.4;
    box-shadow: 0 4px 12px rgba(0,0,0,0.6);
}
.tooltip-wrap:hover .tooltip-box { display: block; }
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

        content = _def_cell_content(word)
        if is_current:
            def_html = f'<td class="clue-def def-current">{content}{mystery_part}</td>'
        else:
            def_html = f'<td class="clue-def">{content}{mystery_part}</td>'

        row_class = ' class="clue-row-current"' if is_current else ""
        rows.append(f"<tr{row_class}>{num_html}{ans_html}{def_html}</tr>")

    table = '<table class="clue-table">' + "".join(rows) + "</table>"
    return css + table
