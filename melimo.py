#!/usr/bin/env python3
"""
Mélimo — Jeu de mots en labyrinthe
Point d'entrée principal.

Usage :
  python melimo.py                          # Menu interactif
  python melimo.py --puzzle FILE            # Charger un puzzle JSON directement
  python melimo.py --verify FILE            # Valider un fichier puzzle JSON
  python melimo.py --generate               # Générer et jouer une partie
  python melimo.py --prefetch               # Pré-télécharger les définitions (tous thèmes)
  python melimo.py --prefetch --theme THEME # Pré-télécharger un thème spécifique
"""
from __future__ import annotations
import argparse
import sys
import os

# Répertoire du projet dans le path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import display
from game import run_game, run_menu

PUZZLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "puzzles")

from generator.word_selector import available_themes as _available_themes
THEMES = _available_themes()
DIFFICULTIES = ["facile", "moyen", "difficile"]
SIZES = {
    "petite": (10, 10),
    "normale": (15, 15),
    "grande": (20, 20),
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mélimo — Jeu de mots en labyrinthe français",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--puzzle", "-p", metavar="FICHIER",
                        help="Charger et jouer un puzzle JSON directement")
    parser.add_argument("--verify", "-v", metavar="FICHIER",
                        help="Valider l'intégrité d'un fichier puzzle JSON")
    parser.add_argument("--generate", "-g", action="store_true",
                        help="Générer une partie directement (mode rapide)")
    parser.add_argument("--prefetch", action="store_true",
                        help="Pré-télécharger les définitions Wiktionnaire dans le cache")
    parser.add_argument("--theme", metavar="THEME", default=None,
                        help="Limiter le prefetch à un thème spécifique")

    args = parser.parse_args()

    display.print_banner()

    # ── Mode pré-téléchargement ────────────────────────────────────────────
    if args.prefetch:
        from dictionary.prefetch import run_prefetch
        run_prefetch(theme=args.theme)
        return

    # ── Mode vérification ──────────────────────────────────────────────────
    if args.verify:
        _cmd_verify(args.verify)
        return

    # ── Charger un puzzle spécifique ───────────────────────────────────────
    if args.puzzle:
        _cmd_play_file(args.puzzle)
        return

    # ── Mode génération rapide ─────────────────────────────────────────────
    if args.generate:
        puzzle = _interactive_generate()
        if puzzle:
            run_game(puzzle)
        return

    # ── Menu principal interactif ──────────────────────────────────────────
    _main_menu()


def _main_menu() -> None:
    """Menu principal : choix entre générer ou charger un puzzle."""
    while True:
        display.clear_screen()
        display.print_banner()

        print("  Que voulez-vous faire ?\n")
        print("    1. Générer une nouvelle partie")
        print("    2. Jouer un puzzle pré-défini")
        print("    q. Quitter")
        print()

        try:
            choice = input("  Votre choix : ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice == "1":
            puzzle = _interactive_generate()
            if puzzle:
                run_game(puzzle)

        elif choice == "2":
            puzzle = run_menu(PUZZLES_DIR)
            if puzzle:
                run_game(puzzle)

        elif choice == "q":
            break

    print("\n  À bientôt !")


def _interactive_generate() -> object | None:
    """Affiche le menu de paramètres et génère un puzzle."""
    from generator.grid_builder import generate_puzzle

    display.clear_screen()
    display.print_banner()
    print("  ── Nouvelle partie ──\n")

    # Thème
    print("  Thème :")
    for i, t in enumerate(THEMES, 1):
        print(f"    {i}. {t.capitalize()}")
    theme = _choose("  Thème (Entrée = Général) : ", THEMES, default="general")

    # Difficulté
    print("\n  Difficulté :")
    for i, d in enumerate(DIFFICULTIES, 1):
        print(f"    {i}. {d.capitalize()}")
    difficulty = _choose("  Difficulté (Entrée = Moyen) : ", DIFFICULTIES, default="moyen")

    # Taille
    print("\n  Taille de la grille :")
    size_names = list(SIZES.keys())
    for i, s in enumerate(size_names, 1):
        r, c = SIZES[s]
        print(f"    {i}. {s.capitalize()} ({r}×{c})")
    size_name = _choose("  Taille (Entrée = Normale) : ", size_names, default="normale")
    rows, cols = SIZES[size_name]

    # Nombre de mots
    print("\n  Nombre de mots :")
    print("    1. 8 mots")
    print("    2. 12 mots")
    print("    3. 17 mots")
    n_words_options = [8, 12, 17]
    n_choice = _choose_index("  Nombre de mots (Entrée = 12) : ", 3, default=1)
    n_words = n_words_options[n_choice]

    print("\n  Génération en cours...")

    try:
        puzzle = generate_puzzle(
            rows=rows,
            cols=cols,
            n_words=n_words,
            theme=theme,
            difficulty=difficulty,
        )
        print(f"  Grille générée : {len(puzzle.path)} cases de chemin, {puzzle.unused_count} lettres inutiles.")
        input("  [Entrée] pour commencer...")
        return puzzle

    except Exception as e:
        print(f"\n  Erreur lors de la génération : {e}")
        input("  [Entrée] pour revenir...")
        return None


def _choose(prompt: str, options: list[str], default: str) -> str:
    """Demande un choix numéroté parmi des options. Retourne la valeur choisie."""
    while True:
        try:
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return default

        if not raw:
            return default

        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass

        print(f"  Entrez un numéro entre 1 et {len(options)}.")


def _choose_index(prompt: str, n: int, default: int) -> int:
    """Demande un index numéroté. Retourne l'index 0-based."""
    while True:
        try:
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return default

        if not raw:
            return default

        try:
            idx = int(raw) - 1
            if 0 <= idx < n:
                return idx
        except ValueError:
            pass

        print(f"  Entrez un numéro entre 1 et {n}.")


def _cmd_play_file(filepath: str) -> None:
    """Charge et lance un puzzle depuis un fichier JSON."""
    from loader import load_puzzle, PuzzleLoadError
    try:
        puzzle = load_puzzle(filepath)
        run_game(puzzle)
    except PuzzleLoadError as e:
        print(f"Erreur : {e}")
        sys.exit(1)


def _cmd_verify(filepath: str) -> None:
    """Valide un fichier puzzle JSON et affiche le résultat."""
    from loader import load_puzzle, PuzzleLoadError
    try:
        puzzle = load_puzzle(filepath)
        print(f"✓ Puzzle valide : {puzzle.title}")
        print(f"  Grille      : {puzzle.rows}×{puzzle.cols}")
        print(f"  Chemin      : {len(puzzle.path)} cellules")
        print(f"  Mots        : {len(puzzle.words)}")
        print(f"  Inutilisées : {puzzle.unused_count} lettres")
        for w in puzzle.words:
            mystery = " [MYSTÈRE]" if w.is_mystery else ""
            print(f"    {w.number:>2}. {w.answer:<15} — {w.definition}{mystery}")
    except PuzzleLoadError as e:
        print(f"✗ Puzzle invalide : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
