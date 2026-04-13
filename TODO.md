# TODO — Améliorations Mélimo

## P0 — Bugs critiques

- [ ] **Temps mal calculé dans le résumé** (`summary.py:66`)
  Le code récupère le timestamp de début brut au lieu de calculer `time.time() - start_time`. Les métriques de temps sont incorrectes.

- [ ] **Indice dépensable après la bonne réponse** (`views/game.py:160`)
  Un joueur peut cliquer "Indice" alors que son mot est déjà validé et perdre 20 pts inutilement. Ajouter une vérification avant d'incrémenter `state.hints`.

- [ ] **Crash sur puzzle vide** (`display.py:129`)
  `max(w.length() for w in puzzle.words)` lève une `ValueError` si la liste est vide. Ajouter un `default=10` comme dans la version web (`clues.py:54`).

---

## P1 — Gameplay

- [ ] **Indices progressifs** (3 niveaux de pénalité croissante)
  - Indice 1 : nombre de lettres (−10 pts)
  - Indice 2 : première lettre (−20 pts)
  - Indice 3 : position sur la grille (−30 pts)
  Remplace l'indice unique actuel à −20 pts.

- [ ] **Option "Révéler le mot"** pour se débloquer
  Permettre de révéler la réponse pour 0 point et passer au mot suivant, plutôt que d'être bloqué ou de quitter.

- [ ] **Score potentiel en temps réel**
  Afficher dans le panneau de droite le score que le joueur obtiendrait s'il répondait maintenant (base − temps écoulé − erreurs − indices), pour rendre l'enjeu visible.

- [ ] **Mode contre-la-montre**
  Timer global (ex : 5 min) pour trouver le maximum de mots. Variante rapide du mode normal.

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
