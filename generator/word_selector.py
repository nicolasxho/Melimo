"""
Sélectionne des mots depuis les listes thématiques et récupère leurs définitions.
"""
from __future__ import annotations
import os
import random
import sys

# Ajout du répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from validation import normalize_answer

WORDS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "words")

# Longueurs de mots par difficulté
DIFFICULTY_LENGTHS = {
    "facile": (4, 6),
    "moyen": (5, 8),
    "difficile": (6, 12),
}

THEMES = {
    "general": "general.txt",
    "nature": "nature.txt",
    "sport": "sport.txt",
}


def load_word_list(theme: str | None = None, difficulty: str = "moyen") -> list[str]:
    """
    Charge une liste de mots depuis le fichier thématique correspondant.
    Filtre par longueur selon la difficulté.
    Retourne les mots en majuscules normalisés.
    """
    filename = THEMES.get(theme or "general", "general.txt")
    filepath = os.path.join(WORDS_DIR, filename)

    if not os.path.exists(filepath):
        filepath = os.path.join(WORDS_DIR, "general.txt")

    min_len, max_len = DIFFICULTY_LENGTHS.get(difficulty.lower(), (5, 8))

    words = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            normalized = normalize_answer(line)
            if min_len <= len(normalized) <= max_len:
                # Stocker (forme_normalisée, forme_originale_avec_accents)
                words.append((normalized, line.strip()))

    return words


def select_words(
    word_list: list[tuple[str, str]],
    target_path_length: int,
    n_words: int,
    cache_path: str | None = None,
    max_attempts: int = 500,
) -> list[tuple[str, str]]:
    """
    Sélectionne n_words mots dont la somme des longueurs est proche de
    target_path_length (± 15%). Récupère leurs définitions depuis le cache
    ou Wiktionnaire. Seuls les mots avec une définition réelle sont retenus.

    word_list : liste de (forme_normalisée, forme_originale_avec_accents)
    Retourne une liste de tuples (mot_normalisé, définition).
    Lève ValueError si impossible de trouver une combinaison valide.
    """
    from dictionary.wiktionary import fetch_and_cache

    if not word_list:
        raise ValueError("La liste de mots est vide.")

    if cache_path is None:
        cache_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "dictionary", "cache.json"
        )

    # Étape 1 : récupérer les définitions pour un pool de candidats.
    # On charge le cache une seule fois et on priorise les mots déjà en cache
    # pour éviter des dizaines de requêtes réseau.
    from dictionary.wiktionary import load_cache_once
    cache = load_cache_once(cache_path)

    cached_words = [(n, o) for n, o in word_list if o.upper() in cache or n in cache]
    uncached_words = [(n, o) for n, o in word_list if o.upper() not in cache and n not in cache]
    random.shuffle(cached_words)
    random.shuffle(uncached_words)

    # Priorité aux mots en cache ; compléter avec des requêtes réseau si besoin
    pool = cached_words[:n_words * 4] + uncached_words[:n_words * 2]
    pool = pool[:min(n_words * 6, len(word_list))]

    defs: dict[str, str] = {}
    for normalized, original in pool:
        key = original.upper()
        if key in cache:
            defs[normalized] = cache[key]
        elif normalized in cache:
            defs[normalized] = cache[normalized]
        else:
            defn = fetch_and_cache(original, cache_path)
            if defn:
                cache[original.upper()] = defn
                defs[normalized] = defn
        if len(defs) >= n_words * 3:
            break  # Pool suffisant, pas besoin d'aller plus loin

    if len(defs) < n_words:
        raise ValueError(
            f"Seulement {len(defs)} mot(s) avec une définition disponible "
            f"sur {len(pool)} candidats testés. Besoin de {n_words}."
        )

    # Étape 2 : trouver une combinaison dont la somme des longueurs convient
    tolerance = 0.15  # ±15% pour plus de flexibilité
    min_total = int(target_path_length * (1 - tolerance))
    max_total = int(target_path_length * (1 + tolerance))

    words_with_defs = list(defs.keys())
    selection = _find_combination(words_with_defs, n_words, min_total, max_total)

    if not selection:
        raise ValueError(
            f"Impossible de sélectionner {n_words} mots totalisant "
            f"~{target_path_length} lettres parmi les {len(defs)} mots disponibles."
        )

    return [(word, defs[word]) for word in selection]


def _find_combination(
    candidates: list[str],
    n: int,
    min_total: int,
    max_total: int,
) -> list[str] | None:
    """
    Cherche une combinaison de n mots parmi candidates dont la somme
    des longueurs est dans [min_total, max_total].
    Essaie des combinaisons aléatoires.
    """
    random.shuffle(candidates)
    for _ in range(200):
        selection = random.sample(candidates, min(n, len(candidates)))
        total = sum(len(w) for w in selection)
        if min_total <= total <= max_total:
            return selection
    return None


def available_themes() -> list[str]:
    """Retourne la liste des thèmes disponibles."""
    themes = []
    for theme, filename in THEMES.items():
        filepath = os.path.join(WORDS_DIR, filename)
        if os.path.exists(filepath):
            themes.append(theme)
    return themes
