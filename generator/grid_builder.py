"""
Construit la grille Mélimo complète à partir d'un chemin et d'une liste de mots.
Place les mots sur le chemin puis remplit les cases hors-chemin avec des lettres
aléatoires pondérées par la fréquence d'apparition en français.
"""
from __future__ import annotations
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import Cell, WordEntry, Puzzle
from validation import normalize_answer

# Fréquences relatives des lettres en français (source : analyse de corpus)
FRENCH_LETTER_FREQ: dict[str, float] = {
    "E": 14.7, "A": 7.6, "I": 7.5, "S": 7.9, "N": 7.1,
    "R": 6.6, "T": 7.2, "O": 5.4, "L": 5.5, "U": 6.3,
    "D": 3.7, "C": 3.3, "M": 3.0, "P": 3.0, "V": 1.6,
    "G": 1.1, "F": 1.1, "B": 0.9, "H": 0.7, "Q": 0.7,
    "J": 0.5, "X": 0.4, "Z": 0.1, "Y": 0.3, "K": 0.1, "W": 0.1,
}

_LETTERS = list(FRENCH_LETTER_FREQ.keys())
_WEIGHTS = [FRENCH_LETTER_FREQ[l] for l in _LETTERS]


def _random_letter() -> str:
    return random.choices(_LETTERS, weights=_WEIGHTS, k=1)[0]


def build_puzzle(
    rows: int,
    cols: int,
    path: list[Cell],
    words_with_defs: list[tuple[str, str]],
    title: str = "Mélimo",
    theme: str | None = None,
) -> Puzzle:
    """
    Construit un Puzzle complet depuis un chemin et une liste (mot, définition).

    - Les mots sont normalisés et placés en séquence sur le chemin.
    - La somme des longueurs des mots doit être <= len(path).
    - Les cellules hors-chemin sont remplies avec des lettres aléatoires.
    - Le dernier mot est automatiquement désigné MOT MYSTÈRE.

    Lève ValueError si la somme des longueurs dépasse la longueur du chemin.
    """
    total_letters = sum(len(normalize_answer(w)) for w, _ in words_with_defs)
    if total_letters > len(path):
        raise ValueError(
            f"Total des lettres ({total_letters}) > longueur du chemin ({len(path)}). "
            "Réduire le nombre de mots ou augmenter la taille de la grille."
        )

    # Initialiser la grille avec des lettres aléatoires
    grid: list[list[str]] = [
        [_random_letter() for _ in range(cols)]
        for _ in range(rows)
    ]

    # Placer les mots sur le chemin
    word_entries: list[WordEntry] = []
    path_index = 0

    for i, (word, definition) in enumerate(words_with_defs):
        normalized = normalize_answer(word)
        start_idx = path_index
        end_idx = path_index + len(normalized)
        is_mystery = (i == len(words_with_defs) - 1)

        # Écrire les lettres dans la grille
        for j, letter in enumerate(normalized):
            cell = path[path_index + j]
            grid[cell.row][cell.col] = letter

        hint = len(normalized) if is_mystery else None

        word_entries.append(WordEntry(
            number=i + 1,
            definition=definition,
            answer=normalized,
            start_index=start_idx,
            end_index=end_idx,
            letter_count_hint=hint,
            is_mystery=is_mystery,
        ))

        path_index = end_idx

    # Les cellules du chemin non utilisées (si total_letters < len(path))
    # restent avec des lettres aléatoires — elles font partie des lettres inutilisées
    path_set = set(path)
    unused_count = rows * cols - len(path_set)

    return Puzzle(
        title=title,
        theme=theme,
        rows=rows,
        cols=cols,
        grid=grid,
        path=path,
        words=word_entries,
        unused_count=unused_count,
    )


def generate_puzzle(
    rows: int = 15,
    cols: int = 15,
    n_words: int = 10,
    theme: str | None = None,
    difficulty: str = "moyen",
    title: str | None = None,
) -> Puzzle:
    """
    Point d'entrée principal : génère un puzzle complet de A à Z.

    1. Calcule la longueur cible du chemin selon la taille de grille
    2. Sélectionne les mots et récupère leurs définitions
    3. Génère le chemin labyrinthe
    4. Construit et retourne le Puzzle
    """
    from generator.path_generator import generate_path
    from generator.word_selector import load_word_list, select_words

    # Longueur cible basée sur n_words et la difficulté (moyenne des longueurs)
    avg_lengths = {"facile": 5, "moyen": 6, "difficile": 8}
    avg_len = avg_lengths.get(difficulty.lower(), 6)
    target_path_length = n_words * avg_len

    # Sélection des mots
    word_list = load_word_list(theme=theme, difficulty=difficulty)
    words_with_defs = select_words(
        word_list=word_list,
        target_path_length=target_path_length,
        n_words=n_words,
    )

    # Ajuster la longueur du chemin à la somme exacte des mots sélectionnés
    total_letters = sum(len(w) for w, _ in words_with_defs)
    # Ajouter quelques cellules supplémentaires (lettres inutilisées sur le chemin)
    path_length = total_letters + random.randint(0, max(5, rows))

    # Générer le chemin
    path = generate_path(rows=rows, cols=cols, target_length=path_length)

    if title is None:
        theme_label = theme.capitalize() if theme else "Général"
        diff_label = difficulty.capitalize()
        title = f"Mélimo — {theme_label} ({diff_label})"

    return build_puzzle(
        rows=rows,
        cols=cols,
        path=path,
        words_with_defs=words_with_defs,
        title=title,
        theme=theme,
    )
