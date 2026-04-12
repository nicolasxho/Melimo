"""
Rendu HTML de la grille Mélimo.
"""
from __future__ import annotations
from models import Cell, Puzzle
from models import GameState


def build_grid_html(
    puzzle: Puzzle,
    state: GameState,
    hint_active: bool,
    current_word_num: int | None,
    start_hint_cell: Cell | None = None,
) -> str:
    """Retourne un bloc HTML (style + table) représentant la grille colorée."""

    # Cellules des mots correctement trouvés
    found_cells: set[Cell] = set()
    for word in puzzle.words:
        if state.is_word_correct(word.number):
            found_cells.update(word.cells(puzzle.path))

    # Cellules du mot courant (indice)
    hint_cells: set[Cell] = set()
    if hint_active and current_word_num is not None:
        word = puzzle.word_by_number(current_word_num)
        if word:
            hint_cells = set(word.cells(puzzle.path))

    path_set = puzzle.path_set()

    css = """
<style>
.melimo-wrap { overflow-x: auto; }
.melimo-grid {
    border-collapse: collapse;
    font-family: 'Courier New', monospace;
    font-size: 1.13rem;
    margin: 0 auto;
}
.melimo-grid td {
    width: 35px;
    height: 35px;
    text-align: center;
    vertical-align: middle;
    border: 1px solid #2a2a2a;
    user-select: none;
}
.melimo-grid .lbl {
    color: #555;
    font-size: 0.75rem;
    border: none;
    padding: 0 3px;
}
.g-found  { background: #1a5c1a; color: #7dff7d; font-weight: bold; }
.g-start  { background: #1a3a5c; color: #7db8ff; font-weight: bold; }
.g-hint   { background: #7a5900; color: #ffd54f; font-weight: bold; }
.g-path   { background: #2b2b2b; color: #999; }
.g-off    { background: #2b2b2b; color: #999; }
</style>
"""

    rows_html: list[str] = []

    # Ligne d'en-tête des colonnes
    header = '<td class="lbl"></td>' + "".join(
        f'<td class="lbl">{c + 1}</td>' for c in range(puzzle.cols)
    )
    rows_html.append(f"<tr>{header}</tr>")

    for r in range(puzzle.rows):
        row_label = chr(ord("a") + r)
        cells = f'<td class="lbl">{row_label}</td>'
        for c in range(puzzle.cols):
            cell = Cell(r, c)
            letter = puzzle.grid[r][c]
            if start_hint_cell and cell == start_hint_cell:
                cls = "g-start"
            elif cell in found_cells:
                cls = "g-found"
            elif cell in hint_cells:
                cls = "g-hint"
            elif cell in path_set:
                cls = "g-path"
            else:
                cls = "g-off"
            cells += f'<td class="{cls}">{letter}</td>'
        rows_html.append(f"<tr>{cells}</tr>")

    table = (
        '<div class="melimo-wrap">'
        '<table class="melimo-grid">'
        + "".join(rows_html)
        + "</table></div>"
    )
    return css + table
