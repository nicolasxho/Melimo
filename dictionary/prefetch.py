"""
Pré-télécharge les définitions Wiktionnaire pour toutes les listes de mots
et les stocke dans dictionary/cache.json.

Usage :
  python dictionary/prefetch.py                    # tous les thèmes
  python dictionary/prefetch.py --theme nature      # un seul thème
  python dictionary/prefetch.py --delay 0.3         # délai entre requêtes (sec)
  python dictionary/prefetch.py --stats             # statistiques du cache, sans télécharger
"""
from __future__ import annotations
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dictionary.wiktionary import fetch_and_cache_full, load_cache_once, _load_cache
from generator.word_selector import WORDS_DIR, THEMES, DIFFICULTY_LENGTHS
from validation import normalize_answer


def _load_all_words(theme: str) -> list[tuple[str, str]]:
    """
    Charge tous les mots d'un thème (toutes difficultés confondues).
    Retourne une liste de (forme_normalisée, forme_originale).
    """
    filename = THEMES.get(theme)
    if not filename:
        return []
    filepath = os.path.join(WORDS_DIR, filename)
    if not os.path.exists(filepath):
        return []

    words: list[tuple[str, str]] = []
    seen: set[str] = set()
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            normalized = normalize_answer(line)
            if normalized and normalized not in seen:
                seen.add(normalized)
                words.append((normalized, line.strip()))
    return words


def _print_stats(themes: list[str]) -> None:
    """Affiche la couverture du cache par thème."""
    cache = load_cache_once()
    print(f"\n  Cache : {len(cache)} mots stockés\n")
    total_words = 0
    total_cached = 0
    for theme in themes:
        words = _load_all_words(theme)
        cached = sum(1 for norm, orig in words if orig.upper() in cache or norm in cache)
        pct = int(cached / len(words) * 100) if words else 0
        bar = "#" * (pct // 5) + "-" * (20 - pct // 5)
        print(f"  {theme:<12} [{bar}] {cached:>3}/{len(words)} ({pct}%)")
        total_words += len(words)
        total_cached += cached
    pct_total = int(total_cached / total_words * 100) if total_words else 0
    print(f"\n  Total  : {total_cached}/{total_words} mots en cache ({pct_total}%)")


def run_prefetch(theme: str | None = None, delay: float = 0.5) -> None:
    """
    Point d'entrée principal. Télécharge les définitions manquantes et met à jour le cache.

    Args:
        theme:  Nom du thème à traiter, ou None pour tous les thèmes.
        delay:  Délai en secondes entre chaque requête réseau (défaut 0.5 s).
    """
    themes_to_process = [theme] if theme else list(THEMES.keys())

    # Vérifier que les thèmes demandés existent
    unknown = [t for t in themes_to_process if t not in THEMES]
    if unknown:
        print(f"  Thème(s) inconnu(s) : {', '.join(unknown)}")
        print(f"  Thèmes disponibles : {', '.join(THEMES.keys())}")
        return

    print(f"\n  Mélimo — Pré-téléchargement des définitions")
    print(f"  Thèmes : {', '.join(themes_to_process)}")
    print(f"  Délai  : {delay} s entre chaque requête\n")

    added = 0
    skipped = 0
    failed = 0
    save_every = 10   # Sauvegarder le cache tous les N mots téléchargés

    for theme_name in themes_to_process:
        words = _load_all_words(theme_name)
        if not words:
            print(f"  [{theme_name}] Aucun mot trouvé — vérifier words/{THEMES.get(theme_name)}")
            continue

        # Recharger le cache à chaque thème pour prendre en compte les sauvegardes précédentes
        cache = _load_cache()
        uncached = [(n, o) for n, o in words if o.upper() not in cache and n not in cache]

        print(f"  [{theme_name.upper()}] {len(words)} mots — {len(words) - len(uncached)} en cache, "
              f"{len(uncached)} à télécharger")

        if not uncached:
            skipped += len(words)
            continue

        batch_added = 0
        for i, (normalized, original) in enumerate(uncached, 1):
            label = f"[{theme_name}/{i}/{len(uncached)}] {original:<20}"
            print(f"  {label}", end="", flush=True)

            t0 = time.time()
            result = fetch_and_cache_full(original)
            elapsed = time.time() - t0

            if result:
                display, _ = result
                short = display[:50] + "…" if len(display) > 50 else display
                print(f"  OK ({elapsed:.1f}s)  {short}")
                added += 1
                batch_added += 1
            else:
                print(f"  — introuvable ({elapsed:.1f}s)")
                failed += 1

            # Sauvegarde intermédiaire tous les `save_every` téléchargements
            if batch_added > 0 and batch_added % save_every == 0:
                print(f"  [sauvegarde intermédiaire — {batch_added} mots ajoutés]")

            if i < len(uncached) and delay > 0:
                time.sleep(delay)

        skipped += len(words) - len(uncached)

    print(f"\n  ── Résultat ──────────────────────────────")
    print(f"  Ajoutés       : {added}")
    print(f"  Déjà en cache : {skipped}")
    print(f"  Introuvables  : {failed}")
    cache_final = _load_cache()
    print(f"  Cache total   : {len(cache_final)} mots\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mélimo — Pré-téléchargement des définitions Wiktionnaire",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--theme", metavar="THEME", default=None,
                        help=f"Thème à traiter (disponibles : {', '.join(THEMES.keys())})")
    parser.add_argument("--delay", type=float, default=0.5, metavar="SEC",
                        help="Délai entre requêtes en secondes (défaut : 0.5)")
    parser.add_argument("--stats", action="store_true",
                        help="Afficher les statistiques du cache sans télécharger")
    args = parser.parse_args()

    themes = [args.theme] if args.theme else list(THEMES.keys())

    if args.stats:
        _print_stats(themes)
    else:
        run_prefetch(theme=args.theme, delay=args.delay)


if __name__ == "__main__":
    main()
