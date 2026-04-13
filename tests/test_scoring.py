"""Tests unitaires pour scoring.py"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import scoring


class TestHintPenalties:
    def test_no_hints(self):
        assert scoring.hint_total_penalty(0) == 0

    def test_one_hint(self):
        assert scoring.hint_total_penalty(1) == scoring.HINT_PENALTIES[0]

    def test_two_hints(self):
        expected = scoring.HINT_PENALTIES[0] + scoring.HINT_PENALTIES[1]
        assert scoring.hint_total_penalty(2) == expected

    def test_three_hints(self):
        expected = sum(scoring.HINT_PENALTIES)
        assert scoring.hint_total_penalty(3) == expected

    def test_over_max_capped(self):
        # Au-delà du max, la pénalité ne doit pas augmenter
        assert scoring.hint_total_penalty(10) == scoring.hint_total_penalty(scoring.MAX_HINTS)

    def test_hints_progressive(self):
        # Chaque niveau coûte plus cher que le précédent
        for i in range(1, len(scoring.HINT_PENALTIES)):
            assert scoring.HINT_PENALTIES[i] > scoring.HINT_PENALTIES[i - 1]


class TestHintNextCost:
    def test_first_hint_available(self):
        assert scoring.hint_next_cost(0) == scoring.HINT_PENALTIES[0]

    def test_second_hint_available(self):
        assert scoring.hint_next_cost(1) == scoring.HINT_PENALTIES[1]

    def test_no_more_hints(self):
        assert scoring.hint_next_cost(scoring.MAX_HINTS) is None

    def test_hint_next_label_returns_string(self):
        assert isinstance(scoring.hint_next_label(0), str)
        assert scoring.hint_next_label(scoring.MAX_HINTS) is None


class TestComputeWordScore:
    def test_fast_perfect(self):
        """Réponse rapide, sans erreur ni indice → score élevé."""
        s = scoring.compute_word_score(False, 2.0, 0, 0)
        assert s > scoring.BASE_SCORE * 0.8

    def test_score_decreases_with_time(self):
        s_fast = scoring.compute_word_score(False, 5.0, 0, 0)
        s_slow = scoring.compute_word_score(False, 30.0, 0, 0)
        assert s_fast > s_slow

    def test_score_decreases_with_errors(self):
        s_clean = scoring.compute_word_score(False, 10.0, 0, 0)
        s_error = scoring.compute_word_score(False, 10.0, 1, 0)
        assert s_clean > s_error

    def test_score_decreases_with_hints(self):
        s_no_hint = scoring.compute_word_score(False, 10.0, 0, 0)
        s_hint = scoring.compute_word_score(False, 10.0, 0, 1)
        assert s_no_hint > s_hint

    def test_mystery_word_gives_more(self):
        # Avec elapsed=0 la base double exactement ; avec elapsed>0 la pénalité temps
        # est soustraite après le doublement donc le ratio n'est pas exactement 2.
        s_normal = scoring.compute_word_score(False, 0.0, 0, 0)
        s_mystery = scoring.compute_word_score(True, 0.0, 0, 0)
        assert s_mystery == s_normal * scoring.MYSTERY_MULTIPLIER
        # Avec du temps écoulé, mystery doit rester supérieur
        assert scoring.compute_word_score(True, 20.0, 0, 0) > scoring.compute_word_score(False, 20.0, 0, 0)

    def test_minimum_score_respected(self):
        """Score plancher garanti même avec beaucoup d'erreurs et de temps."""
        s = scoring.compute_word_score(False, 999.0, 50, 3)
        assert s == scoring.MIN_WORD_SCORE

    def test_mystery_minimum_same_floor(self):
        s = scoring.compute_word_score(True, 999.0, 50, 3)
        assert s == scoring.MIN_WORD_SCORE

    def test_score_non_negative(self):
        for t in [0, 10, 60, 300]:
            for e in [0, 1, 5]:
                for h in range(scoring.MAX_HINTS + 1):
                    assert scoring.compute_word_score(False, t, e, h) >= 0
                    assert scoring.compute_word_score(True, t, e, h) >= 0


class TestScoreBreakdown:
    def test_keys_present(self):
        bd = scoring.score_breakdown(False, 10.0, 1, 1)
        for key in ("base", "time_penalty", "error_penalty", "hint_penalty", "total"):
            assert key in bd

    def test_total_matches_compute(self):
        for is_mystery in (False, True):
            for elapsed in (5.0, 30.0, 120.0):
                for errors in (0, 2):
                    for hints in (0, 1, 3):
                        bd = scoring.score_breakdown(is_mystery, elapsed, errors, hints)
                        direct = scoring.compute_word_score(is_mystery, elapsed, errors, hints)
                        assert bd["total"] == direct

    def test_mystery_base_is_doubled(self):
        bd_normal = scoring.score_breakdown(False, 0, 0, 0)
        bd_mystery = scoring.score_breakdown(True, 0, 0, 0)
        assert bd_mystery["base"] == bd_normal["base"] * scoring.MYSTERY_MULTIPLIER
