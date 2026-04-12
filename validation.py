import unicodedata
from models import WordEntry


def normalize_answer(text: str) -> str:
    """
    Normalise une réponse pour la comparaison :
    - Majuscules
    - Suppression des espaces, tirets et apostrophes
    - Suppression des accents (décomposition NFD)
    """
    text = text.upper().strip()
    text = text.replace(" ", "").replace("-", "").replace("'", "").replace("'", "")
    nfd = unicodedata.normalize("NFD", text)
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def check_answer(player_input: str, word: WordEntry) -> bool:
    """Retourne True si la réponse du joueur correspond à la bonne réponse."""
    return normalize_answer(player_input) == normalize_answer(word.answer)
