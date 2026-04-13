# TODO — Améliorations Mélimo

## P0 — Bugs critiques ✅

- [x] **Temps mal calculé dans le résumé** — `word_elapsed` ajouté à `GameState`, enregistré à la validation, affiché correctement dans `summary.py`.
- [x] **Indice dépensable après la bonne réponse** — garde ajoutée dans `views/game.py` (`if not state.is_word_correct`).
- [x] **Crash sur puzzle vide** — `max(..., default=10)` dans `display.py`.

---

## P1 — Gameplay ✅

- [x] **Indices progressifs** (3 niveaux) — niveau 1 : nb lettres (−10 pts), niveau 2 : 1re lettre (−20 pts), niveau 3 : grille (−30 pts). Implémenté dans `scoring.py`, `game.py`, `views/game.py`.
- [x] **Option "Révéler le mot"** — bouton "👁 Révéler (0 pt)" en web, commande `r` en CLI. Le mot est ajouté à `state.revealed`, 0 point accordé.
- [x] **Score potentiel en temps réel** — affiché dans le panneau de droite (mis à jour à chaque rerun).
- [x] **Mode contre-la-montre** — choix 3/5/10 min dans les deux écrans setup. Compte à rebours affiché en haut à droite, auto-redirect vers le résumé à expiration.

---

## P2 — UX & Interface ✅

- [x] **Historique des tentatives** — `state.attempts` tracké dans `GameState`, affiché sous le champ de saisie (web) et après chaque erreur (CLI).
- [x] **Confirmation avant de quitter** — double clic requis sur "Quitter" (premier clic → "⚠️ Confirmer ?", second clic → résumé). Message d'avertissement affiché entre les deux.
- [x] **Grille responsive** — taille des cellules calculée dynamiquement selon `puzzle.cols` : 35 px (≤10), 28 px (≤15), 22 px (≤20).
- [x] **Tutoriel / règles du jeu** — nouvel écran `rules.py` accessible depuis l'accueil via "❓ Règles du jeu". Explique le déroulement, le barème et les indices.

---

## P3 — Données & Contenu ✅

- [x] **Enrichir les listes de mots** — `nature.txt` : 50 → 155 mots, `sport.txt` : 40 → 105 mots, `general.txt` : 108 → 280 mots.
- [x] **Fallback si Wiktionnaire est indisponible** — `word_selector.py` : si l'API échoue et le cache est vide, une définition générique est utilisée pour ne pas bloquer la génération.
- [x] **Cache Wiktionnaire en mémoire** — variable `_MEM_CACHE` module-level dans `wiktionary.py` : le fichier JSON n'est lu qu'une seule fois par processus.

---

## P4 — Architecture ✅ (partiel)

- [x] **Tests unitaires** — 53 tests dans `tests/` couvrant `scoring.py`, `validation.py` et `models.py`. Lancer avec `python -m pytest tests/ -v`.
- [x] **Bug validation.py** (découvert via les tests) — U+2019 (apostrophe courbe) non supprimé ; corrigé en ajoutant toutes les variantes Unicode d'apostrophe.
- [ ] **Logique de jeu unifiée (`GameEngine`)** — Reporté : la boucle synchrone (CLI) et la boucle réactive (Streamlit) sont fondamentalement différentes. Refactoring majeur à planifier séparément.
- [ ] **Sauvegarde de partie** — Reporté : nécessite de sérialiser `Puzzle` + `GameState` en JSON et d'offrir un écran "Reprendre". À planifier en sprint dédié.
- [ ] **Logging structuré** — Reporté : priorité faible, aucun `print()` de debug dans le code de production actuel.
