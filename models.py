from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Cell:
    row: int  # 0-indexed (0 = 'a')
    col: int  # 0-indexed (0 = colonne 1)

    def label(self) -> str:
        """Retourne l'étiquette lisible, ex: 'a1', 'o15'."""
        return f"{chr(ord('a') + self.row)}{self.col + 1}"

    def is_adjacent(self, other: Cell) -> bool:
        """Vrai si les deux cellules sont voisines horizontalement ou verticalement."""
        return abs(self.row - other.row) + abs(self.col - other.col) == 1

    def neighbors(self, rows: int, cols: int) -> list[Cell]:
        """Retourne les voisins H/V valides dans une grille de taille rows×cols."""
        result = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < rows and 0 <= c < cols:
                result.append(Cell(r, c))
        return result


@dataclass
class WordEntry:
    number: int          # Numéro de la définition (1-based)
    definition: str      # Texte de la définition en français
    answer: str          # Réponse en majuscules sans accents
    start_index: int     # Index de début dans puzzle.path (inclusif)
    end_index: int       # Index de fin dans puzzle.path (exclusif)
    letter_count_hint: int | None = None  # Nombre de lettres si indiqué
    is_mystery: bool = False              # Vrai pour le MOT MYSTÈRE

    def length(self) -> int:
        return self.end_index - self.start_index

    def start_cell(self, path: list[Cell]) -> Cell:
        return path[self.start_index]

    def end_cell(self, path: list[Cell]) -> Cell:
        return path[self.end_index - 1]

    def cells(self, path: list[Cell]) -> list[Cell]:
        return path[self.start_index:self.end_index]


@dataclass
class Puzzle:
    title: str
    theme: str | None
    rows: int
    cols: int
    grid: list[list[str]]   # grid[row][col] = lettre majuscule
    path: list[Cell]        # Chemin complet ordonné (toutes les cellules du labyrinthe)
    words: list[WordEntry]
    unused_count: int       # Nombre de cellules hors-chemin

    def get_letter(self, cell: Cell) -> str:
        return self.grid[cell.row][cell.col]

    def path_set(self) -> set[Cell]:
        return set(self.path)

    def word_by_number(self, n: int) -> WordEntry | None:
        for w in self.words:
            if w.number == n:
                return w
        return None


@dataclass
class GameState:
    puzzle: Puzzle
    answers: dict[int, str] = field(default_factory=dict)   # numéro → réponse joueur
    revealed: set[int] = field(default_factory=set)         # mots révélés (0 point)
    score: int = 0
    mystery_found: bool = False

    def is_word_correct(self, word_number: int) -> bool:
        from validation import check_answer
        word = self.puzzle.word_by_number(word_number)
        if word is None or word_number not in self.answers:
            return False
        return check_answer(self.answers[word_number], word)

    def is_complete(self) -> bool:
        answered = set(self.answers.keys()) | self.revealed
        return all(w.number in answered for w in self.puzzle.words)

    def answered_count(self) -> int:
        return sum(1 for w in self.puzzle.words if self.is_word_correct(w.number))
