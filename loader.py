"""
Charge des puzzles pré-définis depuis des fichiers JSON.
Valide la cohérence du puzzle (chemin, lettres, longueurs).
"""
from __future__ import annotations
import json
import os
from models import Cell, WordEntry, Puzzle
from generator.path_generator import validate_path
from validation import normalize_answer


class PuzzleLoadError(Exception):
    pass


def load_puzzle(filepath: str) -> Puzzle:
    """
    Charge et valide un puzzle depuis un fichier JSON.
    Lève PuzzleLoadError si le fichier est invalide.
    """
    if not os.path.exists(filepath):
        raise PuzzleLoadError(f"Fichier introuvable : {filepath}")

    with open(filepath, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise PuzzleLoadError(f"JSON invalide : {e}")

    rows = data.get("rows", 15)
    cols = data.get("cols", 15)

    # Grille
    grid_raw = data.get("grid", [])
    grid = _parse_grid(grid_raw, rows, cols)

    # Chemin
    path_raw = data.get("path", [])
    path = _parse_path(path_raw)

    # Mots
    words_raw = data.get("words", [])
    words = _assign_word_indices(words_raw)

    unused_count = rows * cols - len(set(path))

    puzzle = Puzzle(
        title=data.get("title", "Mélimo"),
        theme=data.get("theme"),
        rows=rows,
        cols=cols,
        grid=grid,
        path=path,
        words=words,
        unused_count=unused_count,
    )

    errors = _validate_puzzle(puzzle)
    if errors:
        raise PuzzleLoadError(
            f"Puzzle invalide ({len(errors)} erreur(s)) :\n" +
            "\n".join(f"  - {e}" for e in errors)
        )

    return puzzle


def _parse_grid(grid_raw: list, rows: int, cols: int) -> list[list[str]]:
    """Convertit les lignes de la grille en liste 2D de lettres."""
    grid: list[list[str]] = []
    for i, row in enumerate(grid_raw[:rows]):
        if isinstance(row, str):
            letters = list(row.upper())
        elif isinstance(row, list):
            letters = [str(c).upper() for c in row]
        else:
            raise PuzzleLoadError(f"Format de ligne invalide à l'index {i}")
        # Compléter ou tronquer à cols
        letters = (letters + ["?"] * cols)[:cols]
        grid.append(letters)
    # Compléter les lignes manquantes
    while len(grid) < rows:
        grid.append(["?"] * cols)
    return grid


def _parse_path(path_raw: list) -> list[Cell]:
    """
    Convertit le chemin brut en list[Cell].
    Format attendu : [["a", 1], ["b", 3], ...] ou [[0, 0], [1, 2], ...]
    """
    path = []
    for entry in path_raw:
        if len(entry) != 2:
            raise PuzzleLoadError(f"Entrée de chemin invalide : {entry}")
        row_raw, col_raw = entry

        if isinstance(row_raw, str):
            row = ord(row_raw.lower()) - ord("a")
        else:
            row = int(row_raw)

        col = int(col_raw) - 1  # Conversion 1-based → 0-based

        path.append(Cell(row, col))
    return path


def _assign_word_indices(words_raw: list[dict]) -> list[WordEntry]:
    """
    Calcule les start_index/end_index de chaque mot dans le chemin.
    Les mots se suivent dans l'ordre, bout à bout.
    """
    entries = []
    current_index = 0

    for i, w in enumerate(words_raw):
        answer = normalize_answer(w.get("answer", ""))
        if not answer:
            raise PuzzleLoadError(f"Mot {i + 1} sans réponse.")

        start = current_index
        end = current_index + len(answer)

        entries.append(WordEntry(
            number=w.get("number", i + 1),
            definition=w.get("definition", ""),
            answer=answer,
            start_index=start,
            end_index=end,
            letter_count_hint=w.get("letter_count_hint"),
            is_mystery=w.get("is_mystery", False),
            full_definition=w.get("full_definition"),
        ))

        current_index = end

    return entries


def _validate_puzzle(puzzle: Puzzle) -> list[str]:
    """Retourne la liste des erreurs de validation (vide si valide)."""
    errors = []

    # Validation du chemin (adjacence, bornes, doublons)
    path_errors = validate_path(puzzle.path, puzzle.rows, puzzle.cols)
    errors.extend(path_errors)

    # Longueur du chemin vs somme des mots
    total_letters = sum(w.length() for w in puzzle.words)
    if total_letters > len(puzzle.path):
        errors.append(
            f"Somme des longueurs des mots ({total_letters}) > "
            f"longueur du chemin ({len(puzzle.path)})"
        )

    # Cohérence lettres grille ↔ chemin
    for word in puzzle.words:
        for i, cell in enumerate(word.cells(puzzle.path)):
            grid_letter = puzzle.get_letter(cell)
            expected = word.answer[i]
            if grid_letter != expected:
                errors.append(
                    f"Mot {word.number} '{word.answer}' : lettre {i + 1} "
                    f"({expected}) ≠ grille ({grid_letter}) à {cell.label()}"
                )

    return errors


def list_puzzles(puzzles_dir: str) -> list[str]:
    """Retourne la liste triée des fichiers JSON dans le répertoire de puzzles."""
    if not os.path.isdir(puzzles_dir):
        return []
    return sorted(
        os.path.join(puzzles_dir, f)
        for f in os.listdir(puzzles_dir)
        if f.endswith(".json")
    )
