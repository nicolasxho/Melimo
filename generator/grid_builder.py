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

VOWELS: frozenset[str] = frozenset("AEIOUY")
CONSONANTS: frozenset[str] = frozenset("BCDFGHJKLMNPQRSTVWXZ")

# Règle e) du spec : lettres valides adjacentes à certaines consonnes déjà en place
_CONSONANT_FOLLOW: dict[str, frozenset[str]] = {
    "B": frozenset(["L", "R"]) | VOWELS,
    "C": frozenset(["H", "L", "R"]) | VOWELS,
    "D": frozenset(["R"]) | VOWELS,
    "F": frozenset(["L", "R"]) | VOWELS,
    "H": frozenset(["N", "L", "R"]) | VOWELS,
    "P": frozenset(["H", "L", "R", "S"]) | VOWELS,
    "Q": frozenset(["U"]),
    "R": frozenset(["H"]) | VOWELS,
    "S": frozenset(["T", "L", "P"]) | VOWELS,
    "T": frozenset(["H", "R"]) | VOWELS,
    "V": frozenset(["R"]) | VOWELS,
}

_TARGET_VOWEL_RATIO = 0.40


def _choose_filler_letter(
    grid: list[list[str]],
    row: int,
    col: int,
    rows: int,
    cols: int,
    vowel_count: int,
    total_count: int,
) -> str:
    """
    Choisit une lettre de remplissage en respectant les règles du point 11 du spec :
      a) Pas de lettre identique en diagonale.
      c) Pas de schéma X_Y_X (même lettre à 2 pas H/V).
      e) Règles de voisinage par consonne (B→L/R/voyelle, Q→U, etc.).
      13) Pas de 2 consonnes adjacentes sauf ST.
      d+12) Ratio cible 40 % voyelles / 60 % consonnes via pondération.
    """
    valid: set[str] = set(_LETTERS)

    # Règle a : pas de lettre identique en diagonale
    for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        nr, nc = row + dr, col + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc]:
            valid.discard(grid[nr][nc])

    # Règle c : pas de schéma X_Y_X (même lettre à 2 cases H/V)
    for dr, dc in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        nr, nc = row + dr, col + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc]:
            valid.discard(grid[nr][nc])

    # Règles e et 13 : contraintes selon les voisins H/V déjà posés
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = row + dr, col + dc
        if not (0 <= nr < rows and 0 <= nc < cols):
            continue
        neighbor = grid[nr][nc]
        if not neighbor:
            continue

        # Règle e : si le voisin est une consonne avec règle spéciale
        if neighbor in _CONSONANT_FOLLOW:
            valid &= _CONSONANT_FOLLOW[neighbor]

        # Règle 13 : pas de 2 consonnes adjacentes (sauf ST)
        if neighbor in CONSONANTS:
            if neighbor == "S":
                valid -= CONSONANTS - {"T"}
            elif neighbor == "T":
                valid -= CONSONANTS - {"S"}
            else:
                valid -= CONSONANTS

    # Fallback : si les contraintes s'annulent, on repart de l'alphabet complet
    if not valid:
        valid = set(_LETTERS)

    # Règles d+12 : ratio cible 40 % voyelles — biais sur les poids
    current_ratio = vowel_count / total_count if total_count > 0 else _TARGET_VOWEL_RATIO
    vowel_bias = 2.0 if current_ratio < _TARGET_VOWEL_RATIO else 0.5

    letters = list(valid)
    weights = [
        FRENCH_LETTER_FREQ.get(l, 1.0) * (vowel_bias if l in VOWELS else 1.0)
        for l in letters
    ]
    return random.choices(letters, weights=weights, k=1)[0]


def _fill_filler_cells(
    grid: list[list[str]],
    rows: int,
    cols: int,
    word_cells: set[Cell],
) -> None:
    """
    Remplit toutes les cases non-mot (gauche→droite, haut→bas) en respectant
    les règles de remplissage du spec (point 11).
    """
    # Initialiser les compteurs depuis les lettres de mots déjà posées
    vowel_count = sum(
        1 for cell in word_cells if grid[cell.row][cell.col] in VOWELS
    )
    total_count = len(word_cells)

    for r in range(rows):
        for c in range(cols):
            if Cell(r, c) not in word_cells:
                letter = _choose_filler_letter(
                    grid, r, c, rows, cols, vowel_count, total_count
                )
                grid[r][c] = letter
                if letter in VOWELS:
                    vowel_count += 1
                total_count += 1


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
    total_letters = sum(len(normalize_answer(w)) for w, _, _fd in words_with_defs)
    if total_letters > len(path):
        raise ValueError(
            f"Total des lettres ({total_letters}) > longueur du chemin ({len(path)}). "
            "Réduire le nombre de mots ou augmenter la taille de la grille."
        )

    # Initialiser la grille vide (les cases seront remplies après placement des mots)
    grid: list[list[str]] = [["" for _ in range(cols)] for _ in range(rows)]

    # Placer les mots sur le chemin
    word_entries: list[WordEntry] = []
    path_index = 0

    for i, (word, definition, full_definition) in enumerate(words_with_defs):
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
            full_definition=full_definition,
        ))

        path_index = end_idx

    # Remplir toutes les cases non-mot avec les règles du spec (point 11)
    word_cells: set[Cell] = {
        path[i]
        for entry in word_entries
        for i in range(entry.start_index, entry.end_index)
    }
    _fill_filler_cells(grid, rows, cols, word_cells)

    unused_count = rows * cols - len(set(path))

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
    total_letters = sum(len(w) for w, _, _fd in words_with_defs)
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
