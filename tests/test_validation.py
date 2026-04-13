"""Tests unitaires pour validation.py"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from validation import normalize_answer, check_answer
from models import WordEntry


def _word(answer: str) -> WordEntry:
    """Crée un WordEntry minimal pour les tests."""
    return WordEntry(
        number=1,
        definition="test",
        answer=answer,
        start_index=0,
        end_index=len(answer),
    )


class TestNormalizeAnswer:
    def test_uppercase(self):
        assert normalize_answer("bonjour") == "BONJOUR"

    def test_accents_removed(self):
        assert normalize_answer("étoile") == "ETOILE"
        assert normalize_answer("château") == "CHATEAU"
        assert normalize_answer("coïncidence") == "COINCIDENCE"

    def test_spaces_removed(self):
        assert normalize_answer("bon jour") == "BONJOUR"

    def test_hyphens_removed(self):
        assert normalize_answer("arc-en-ciel") == "ARCENCIEL"

    def test_apostrophes_removed(self):
        assert normalize_answer("aujourd'hui") == "AUJOURDHUI"       # U+0027
        assert normalize_answer("aujourd\u2019hui") == "AUJOURDHUI"  # U+2019 RIGHT SINGLE QUOTATION MARK
        assert normalize_answer("aujourd\u02BChui") == "AUJOURDHUI"  # U+02BC MODIFIER APOSTROPHE

    def test_strip_whitespace(self):
        assert normalize_answer("  soleil  ") == "SOLEIL"

    def test_mixed(self):
        # Î → I + diacritique supprimé = "I", donc "Île" → "ILE"
        assert normalize_answer("  Île-de-France  ") == "ILEDEFRANCE"

    def test_already_normalized(self):
        assert normalize_answer("SOLEIL") == "SOLEIL"


class TestCheckAnswer:
    def test_exact_match(self):
        assert check_answer("SOLEIL", _word("SOLEIL"))

    def test_case_insensitive(self):
        assert check_answer("soleil", _word("SOLEIL"))

    def test_accent_insensitive(self):
        assert check_answer("etoile", _word("ETOILE"))
        assert check_answer("étoile", _word("ETOILE"))

    def test_hyphen_insensitive(self):
        assert check_answer("arc-en-ciel", _word("ARCENCIEL"))

    def test_apostrophe_insensitive(self):
        assert check_answer("aujourd'hui", _word("AUJOURDHUI"))

    def test_wrong_answer(self):
        assert not check_answer("lune", _word("SOLEIL"))

    def test_partial_answer_rejected(self):
        assert not check_answer("solei", _word("SOLEIL"))

    def test_empty_answer_rejected(self):
        assert not check_answer("", _word("SOLEIL"))

    def test_extra_letters_rejected(self):
        assert not check_answer("soleils", _word("SOLEIL"))
