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

## P2 — UX & Interface

- [ ] **Historique des tentatives**
  Afficher sous le champ de saisie les réponses déjà essayées pour le mot courant.

- [ ] **Confirmation avant de quitter**
  Dialogue de confirmation sur le bouton "Quitter" pour éviter les abandons accidentels.

- [ ] **Grille responsive**
  Les grandes grilles (20×20) débordent sur petit écran. Réduire dynamiquement la taille des cellules en CSS selon les dimensions de la grille.

- [ ] **Tutoriel / règles du jeu**
  Ajouter une page ou un modal expliquant les règles (ordre séquentiel, premier mot offert, barème de scoring) accessible depuis l'accueil.

---

## P3 — Données & Contenu

- [ ] **Enrichir les listes de mots**
  Chaque thème contient ~50 mots → répétitions fréquentes. Viser 500+ mots par thème pour une vraie rejouabilité.

- [ ] **Fallback si Wiktionnaire est indisponible**
  Si l'API est hors ligne lors de la génération, le puzzle échoue. Ajouter un fallback sur des définitions pré-stockées en cache local.

- [ ] **Normaliser les listes de mots**
  Harmoniser les fichiers `words/*.txt` : supprimer les underscores (`ROUGE_GORGE`), uniformiser la casse et les accents entre thèmes.

---

## P4 — Architecture

- [ ] **Tests unitaires**
  Aucun test automatisé actuellement. Cibles prioritaires : `scoring.py`, `validation.py`, `path_generator.py`.

- [ ] **Logique de jeu unifiée (`GameEngine`)**
  La boucle de jeu est dupliquée entre `game.py` (CLI) et `streamlit_app/views/game.py` (Streamlit), créant des bugs différents dans chaque version. Extraire une classe `GameEngine` partagée.

- [ ] **Sauvegarde de partie**
  L'état Streamlit est volatil (perdu si le serveur redémarre). Sérialiser `GameState` en JSON pour permettre de reprendre une partie.

- [ ] **Cache Wiktionnaire en mémoire**
  `load_cache_once()` relit le fichier JSON à chaque génération. Utiliser un cache module-level (`_CACHE: dict | None = None`) pour ne lire le fichier qu'une seule fois par processus.

- [ ] **Logging structuré**
  Remplacer les `print()` de debug par un logger (`logging` stdlib) avec niveaux DEBUG/INFO/WARNING/ERROR.
