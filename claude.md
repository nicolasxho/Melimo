# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projet

Mélimo est un jeu de mots en labyrinthe en français. Le joueur suit un chemin continu (H/V uniquement) tracé dans une grille de lettres. Les mots se succèdent sur ce chemin ; le joueur les trouve grâce à leurs définitions. Le dernier mot est toujours le **MOT MYSTÈRE** (longueur indiquée, pas de définition).

Les règles complètes et des exemples visuels se trouvent dans [References/jeux/](References/jeux/) (images 1.jpg à 4.jpg).

## Commandes

```bash
python melimo.py                          # Menu interactif principal
python melimo.py --generate               # Génération directe (mode rapide)
python melimo.py --puzzle puzzles/x.json  # Charger un puzzle JSON
python melimo.py --verify puzzles/x.json  # Valider un fichier puzzle JSON
```

## Architecture

```
melimo.py              # Point d'entrée : parsing args, menus interactifs
models.py              # Dataclasses : Cell, WordEntry, Puzzle, GameState
validation.py          # normalize_answer(), check_answer() — accents, casse, tirets
loader.py              # load_puzzle(JSON) → Puzzle ; lève PuzzleLoadError
display.py             # Rendu terminal : render_grid(), render_clues() (colorama)
game.py                # Boucle de jeu : run_game(), run_menu()
generator/
  path_generator.py    # generate_path() — marche aléatoire auto-évitante
  grid_builder.py      # build_puzzle(), generate_puzzle() — assemble tout
  word_selector.py     # load_word_list(), select_words() — filtre par thème/difficulté
dictionary/
  wiktionary.py        # fetch_and_cache() — API Wiktionnaire FR
  cache.json           # Cache local des définitions
words/                 # Listes de mots : general.txt, nature.txt, sport.txt
puzzles/               # Fichiers JSON de puzzles pré-définis
```

### Flux de données

1. `generate_puzzle()` dans `grid_builder.py` orchestre tout : sélection de mots → génération du chemin → construction de la grille.
2. `build_puzzle()` place les mots normalisés (`normalize_answer`) en séquence sur le chemin, remplit les cases hors-chemin avec des lettres aléatoires pondérées par fréquence française.
3. Le chemin est une liste ordonnée de `Cell(row, col)` ; les `WordEntry` référencent leur segment via `start_index`/`end_index` dans cette liste.
4. Les puzzles JSON encodent le chemin avec des étiquettes lisibles ex. `["a", 1]` (lettre = ligne 0-indexed, entier = colonne 1-indexed).

### Format JSON des puzzles

- `grid` : liste de chaînes (une par ligne), lettres majuscules sans accents.
- `path` : liste de `[lettre_ligne, colonne_1based]`, ex. `["a", 1]`.
- `words[].answer` : majuscules, sans accents ni espaces (déjà normalisé).
- `words[].is_mystery: true` sur le dernier mot uniquement ; `letter_count_hint` non null pour ce mot.

## Conventions

- Les réponses joueur passent toujours par `normalize_answer()` : majuscules, suppression des accents (NFD), espaces, tirets et apostrophes.
- Thèmes disponibles : `general`, `nature`, `sport`.
- Difficultés : `facile` (moy. 5 lettres), `moyen` (6), `difficile` (8).
- Tailles de grille : petite 10×10, normale 15×15, grande 20×20.

