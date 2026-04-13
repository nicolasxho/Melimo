"""Tests unitaires pour models.py"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from models import Cell, WordEntry, Puzzle, GameState


def _make_puzzle(words: list[WordEntry] | None = None) -> Puzzle:
    path = [Cell(0, 0), Cell(0, 1), Cell(0, 2), Cell(1, 2), Cell(1, 1), Cell(1, 0)]
    grid = [["A", "B", "C"], ["D", "E", "F"]]
    return Puzzle(
        title="Test",
        theme=None,
        rows=2,
        cols=3,
        grid=grid,
        path=path,
        words=words or [],
        unused_count=0,
    )


class TestCell:
    def test_label(self):
        assert Cell(0, 0).label() == "a1"
        assert Cell(2, 14).label() == "c15"

    def test_is_adjacent_horizontal(self):
        assert Cell(0, 0).is_adjacent(Cell(0, 1))

    def test_is_adjacent_vertical(self):
        assert Cell(0, 0).is_adjacent(Cell(1, 0))

    def test_not_adjacent_diagonal(self):
        assert not Cell(0, 0).is_adjacent(Cell(1, 1))

    def test_not_adjacent_same(self):
        assert not Cell(0, 0).is_adjacent(Cell(0, 0))

    def test_neighbors_corner(self):
        nb = Cell(0, 0).neighbors(3, 3)
        assert Cell(0, 1) in nb
        assert Cell(1, 0) in nb
        assert len(nb) == 2

    def test_neighbors_center(self):
        nb = Cell(1, 1).neighbors(3, 3)
        assert len(nb) == 4


class TestWordEntry:
    def test_length(self):
        w = WordEntry(1, "def", "ABC", 0, 3)
        assert w.length() == 3

    def test_cells(self):
        path = [Cell(0, 0), Cell(0, 1), Cell(0, 2)]
        w = WordEntry(1, "def", "ABC", 0, 3)
        assert w.cells(path) == path


class TestGameState:
    def test_initial_score_zero(self):
        gs = GameState(puzzle=_make_puzzle())
        assert gs.score == 0

    def test_attempts_tracked(self):
        gs = GameState(puzzle=_make_puzzle())
        gs.attempts[1] = ["ESSAI1", "ESSAI2"]
        assert len(gs.attempts[1]) == 2

    def test_word_elapsed_stored(self):
        gs = GameState(puzzle=_make_puzzle())
        gs.word_elapsed[1] = 12.5
        assert gs.word_elapsed[1] == 12.5

    def test_errors_and_hints_dicts(self):
        gs = GameState(puzzle=_make_puzzle())
        gs.errors[1] = 3
        gs.hints[1] = 2
        assert gs.errors[1] == 3
        assert gs.hints[1] == 2

    def test_is_complete_empty(self):
        puzzle = _make_puzzle()
        gs = GameState(puzzle=puzzle)
        assert gs.is_complete()  # aucun mot → complet

    def test_revealed_counts_as_answered(self):
        w = WordEntry(1, "def", "ABC", 0, 3)
        puzzle = _make_puzzle([w])
        gs = GameState(puzzle=puzzle)
        gs.revealed.add(1)
        assert gs.is_complete()
