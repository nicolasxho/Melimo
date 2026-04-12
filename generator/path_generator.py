"""
Génère un chemin de type "marche auto-évitante" (self-avoiding walk) dans la grille.
Le chemin ne se déplace que horizontalement ou verticalement (pas de diagonales).
"""
from __future__ import annotations
import random
from models import Cell


def generate_path(
    rows: int,
    cols: int,
    target_length: int,
    start: Cell | None = None,
    max_attempts: int = 1000,
) -> list[Cell]:
    """
    Génère un chemin auto-évitant de longueur target_length dans une grille rows×cols.

    Algorithme : marche aléatoire avec backtracking limité.
    - Commence à une cellule aléatoire (ou donnée)
    - À chaque étape, choisit aléatoirement parmi les voisins H/V non visités
    - Si bloqué avant d'atteindre target_length, recommence depuis le début
    - Retourne la première solution trouvée

    Lève ValueError si impossible après max_attempts tentatives.
    """
    if target_length > rows * cols:
        raise ValueError(
            f"target_length ({target_length}) > nombre de cellules ({rows * cols})"
        )

    for _ in range(max_attempts):
        path = _attempt_path(rows, cols, target_length, start)
        if path is not None:
            return path

    raise ValueError(
        f"Impossible de générer un chemin de longueur {target_length} "
        f"dans une grille {rows}×{cols} après {max_attempts} tentatives."
    )


def _attempt_path(
    rows: int,
    cols: int,
    target_length: int,
    start: Cell | None,
) -> list[Cell] | None:
    """Une tentative de génération. Retourne le chemin ou None si bloqué."""
    if start is None:
        current = Cell(random.randint(0, rows - 1), random.randint(0, cols - 1))
    else:
        current = start

    path: list[Cell] = [current]
    visited: set[Cell] = {current}

    while len(path) < target_length:
        neighbors = [
            n for n in current.neighbors(rows, cols)
            if n not in visited
        ]
        if not neighbors:
            return None  # Bloqué

        current = random.choice(neighbors)
        path.append(current)
        visited.add(current)

    return path


def validate_path(path: list[Cell], rows: int, cols: int) -> list[str]:
    """
    Valide un chemin existant. Retourne une liste d'erreurs (vide si valide).
    Utilisé pour les puzzles pré-définis chargés depuis JSON.
    """
    errors = []
    seen: set[Cell] = set()

    for i, cell in enumerate(path):
        if not (0 <= cell.row < rows and 0 <= cell.col < cols):
            errors.append(f"Cellule {i} hors limites : {cell.label()}")

        if cell in seen:
            errors.append(f"Cellule dupliquée à l'index {i} : {cell.label()}")
        seen.add(cell)

        if i > 0 and not path[i - 1].is_adjacent(cell):
            errors.append(
                f"Cellules non adjacentes entre index {i - 1} et {i} : "
                f"{path[i - 1].label()} → {cell.label()}"
            )

    return errors
