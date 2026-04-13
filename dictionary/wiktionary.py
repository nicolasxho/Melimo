"""
Récupère les définitions de mots français depuis l'API Wiktionnaire.
Utilise l'action 'parse' pour obtenir le wikitext et extrait la première définition.
Met en cache les résultats localement pour éviter les appels répétés.
"""
from __future__ import annotations
import json
import os
import re
import urllib.request
import urllib.error
import urllib.parse

CACHE_PATH = os.path.join(os.path.dirname(__file__), "cache.json")
WIKTIONARY_API = "https://fr.wiktionary.org/w/api.php"
USER_AGENT = "Melimo/1.0 (jeu de mots en labyrinthe; python)"


def _load_cache() -> dict[str, str]:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict[str, str]) -> None:
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def fetch_definition(word: str) -> str | None:
    """
    Récupère la première définition française d'un mot depuis le Wiktionnaire.
    Retourne None si introuvable ou si la requête échoue.
    """
    word_lower = word.lower()
    params = urllib.parse.urlencode({
        "action": "parse",
        "page": word_lower,
        "prop": "wikitext",
        "format": "json",
    })
    url = f"{WIKTIONARY_API}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return None

    if "error" in data:
        return None

    wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
    if not wikitext:
        return None

    result = _extract_french_definition(wikitext)
    if result is None:
        return None
    display, _full = result
    return display


def _extract_french_definition(wikitext: str) -> tuple[str, str] | None:
    """
    Extrait la première définition de la section française du wikitext.
    Retourne (display, full) où display est tronqué à 80 chars et full à 300 chars.
    """
    # Localiser la section française (== {{langue|fr}} ==)
    fr_match = re.search(r"== \{\{langue\|fr\}\} ==", wikitext)
    if not fr_match:
        fr_start = 0
    else:
        fr_start = fr_match.start()

    # Trouver la fin de la section française (prochaine section == {{langue|...}} ==)
    next_lang = re.search(r"== \{\{langue\|(?!fr)", wikitext[fr_start + 1:])
    fr_end = fr_start + 1 + next_lang.start() if next_lang else len(wikitext)

    fr_section = wikitext[fr_start:fr_end]

    # Extraire les lignes de définition (commencent par '# ' mais pas '#*' ni '#:')
    for line in fr_section.splitlines():
        if re.match(r"^# ", line) and not re.match(r"^#[*:]", line):
            full = _clean_wikitext(line[2:])
            if full and len(full) > 10:
                full = full[:297] + "..." if len(full) > 300 else full
                display = full[:77] + "..." if len(full) > 80 else full
                return display, full

    return None


def _clean_wikitext(text: str) -> str:
    """
    Nettoie le wikitext pour obtenir du texte lisible :
    - Supprime les templates {{...}}
    - Remplace [[lien|texte]] par texte
    - Remplace [[lien]] par lien
    - Supprime le formatage ''...'' et '''...'''
    """
    # Remplacer [[lien|texte affiché]] par "texte affiché"
    text = re.sub(r"\[\[[^\]|]+\|([^\]]+)\]\]", r"\1", text)
    # Remplacer [[lien]] par "lien"
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    # Supprimer les templates simples {{nom|...}} — garder le contenu si utile
    # Pour {{lexique|domaine|fr}}, {{term|...}}, etc., on supprime
    text = re.sub(r"\{\{[^}]+\}\}", "", text)
    # Supprimer le formatage italique/gras
    text = re.sub(r"'{2,3}", "", text)
    # Nettoyer les espaces multiples
    text = re.sub(r"\s+", " ", text).strip()
    # Capitaliser la première lettre
    if text:
        text = text[0].upper() + text[1:]
    return text


def fetch_and_cache(word: str, cache_path: str = CACHE_PATH) -> str | None:
    """
    Vérifie d'abord le cache local. Si absent, appelle fetch_definition()
    et sauvegarde dans le cache. Retourne la définition ou None.
    """
    key = word.upper()
    cache = _load_cache()

    if key in cache:
        return cache[key]

    definition = fetch_definition(word)
    if definition:
        cache[key] = definition
        _save_cache(cache)

    return definition


def fetch_and_cache_full(word: str, cache_path: str = CACHE_PATH) -> tuple[str, str] | None:
    """
    Comme fetch_and_cache mais retourne (display, full).
    Stocke la définition complète dans le cache (nouvelles entrées).
    Pour les anciennes entrées tronquées, display == full (pas de tooltip).
    """
    key = word.upper()
    cache = _load_cache()

    if key in cache:
        stored = cache[key]
        display = stored[:77] + "..." if len(stored) > 80 else stored
        return display, stored

    result = _extract_french_definition_raw(word)
    if result is None:
        return None
    display, full = result
    cache[key] = full
    _save_cache(cache)
    return display, full


def _extract_french_definition_raw(word: str) -> tuple[str, str] | None:
    """Appelle l'API Wiktionnaire et retourne (display, full) sans passer par le cache."""
    word_lower = word.lower()
    params = urllib.parse.urlencode({
        "action": "parse",
        "page": word_lower,
        "prop": "wikitext",
        "format": "json",
    })
    url = f"{WIKTIONARY_API}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return None
    if "error" in data:
        return None
    wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
    if not wikitext:
        return None
    return _extract_french_definition(wikitext)


def load_cache_once(cache_path: str = CACHE_PATH) -> dict[str, str]:
    """Charge le cache depuis un chemin donné (ou le chemin par défaut)."""
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_cached_words() -> dict[str, str]:
    """Retourne tous les mots en cache."""
    return _load_cache()


def prefetch_words(words: list[str]) -> dict[str, str | None]:
    """
    Récupère les définitions pour une liste de mots.
    Retourne un dict mot → définition (None si introuvable).
    """
    results: dict[str, str | None] = {}
    for word in words:
        results[word.upper()] = fetch_and_cache(word)
    return results
