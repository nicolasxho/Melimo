# Mélimo

> *« Un jeu instructif comme les mots croisés et familier comme les mots mystères. Un jeu qui
> stimule votre mémoire, votre concentration et votre intuition tout en améliorant grandement
> votre orthographe et votre vocabulaire. »*
>
> — Yvon Ferland, © 1999

**Mélimo** est une adaptation numérique du jeu de mots en labyrinthe québécois inventé par
**Yvon Ferland** en 1999. Les mots se suivent les uns après les autres sur un chemin caché
dans une grille de lettres — le joueur les retrouve grâce à leurs définitions.

---

## Historique

Mélimo est un jeu de lettres et de mots inventé par le Québécois **Yvon Ferland** et publié
pour la première fois en **1999**. Le nom *Mélimo* — ainsi que sa variante abrégée — est une
marque de commerce déposée appartenant à son créateur. Les grilles et les règles correspondantes
sont également protégées.

L'édition originale était publiée par la compagnie **9036-8184 Québec inc.** (Charlesbourg,
Québec), imprimée par l'Imprimerie d'Arthabaska à Victoriaville et distribuée par *Les
Messageries de presse Benjamin inc.*

Dès l'origine, les grilles étaient générées par logiciel — un programme PC conçu par
*Normand Gagnon* et adapté pour Macintosh par *Dominique Jacques*.

---

## Comment jouer

Les mots sont placés les uns à la suite des autres dans une grille de lettres, formant un
chemin en labyrinthe. Les lettres se déploient **à l'horizontale ou à la verticale uniquement**
— les diagonales sont interdites.

1. **Le premier mot** est donné gratuitement pour repérer le point de départ.
2. **Lis la définition** du mot courant et saisit ta réponse — les accents, majuscules et tirets ne comptent pas.
3. Chaque mot débute là où le précédent s'est terminé ; tu ne peux pas sauter un mot.
4. Le dernier mot est le **★ Mot Mystère** — aucune définition fournie, seul le nombre de lettres est indiqué. Il rapporte le double de points !

### Indices et score

| Élément | Effet |
|---|---|
| Réponse correcte | +100 pts de base |
| Mot Mystère | ×2 (base doublée) |
| Temps écoulé | −1,5 pt/seconde |
| Mauvaise réponse | −20 pts |
| Indice 1 (nombre de lettres) | −10 pts |
| Indice 2 (première lettre) | −20 pts |
| Indice 3 (position sur la grille) | −30 pts |
| Minimum garanti | 10 pts par mot trouvé |

---

## Lancer l'application

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Architecture

```
app.py                  # Point d'entrée Streamlit
models.py               # Dataclasses : Cell, WordEntry, Puzzle, GameState
validation.py           # normalize_answer(), check_answer()
scoring.py              # Calcul des scores et pénalités
loader.py               # Chargement de puzzles JSON
generator/
  path_generator.py     # Marche aléatoire auto-évitante
  grid_builder.py       # Assemblage de la grille
  word_selector.py      # Sélection des mots par thème/difficulté
dictionary/
  wiktionary.py         # Récupération des définitions (API Wiktionnaire FR)
  prefetch.py           # Pré-téléchargement du cache
  cache.json            # Cache local des définitions
words/                  # Listes de mots par thème (*.txt)
puzzles/                # Puzzles pré-définis (*.json)
streamlit_app/
  views/                # Écrans : accueil, jeu, résumé, règles, à propos…
  components/           # Composants HTML : grille, indices
```

### Thèmes disponibles

Les thèmes sont **auto-découverts** depuis le dossier `words/` — ajouter un thème = créer un fichier `words/<theme>.txt` (un mot par ligne, minuscules avec accents).

Thèmes inclus : `animaux`, `cuisine`, `géographie`, `général`, `nature`, `sport`.

### Pré-télécharger les définitions

La génération d'une partie interroge l'API Wiktionnaire en temps réel. Pour accélérer le jeu,
pré-remplissez le cache avant de jouer :

```bash
python melimo.py --prefetch              # tous les thèmes
python melimo.py --prefetch --theme animaux   # un seul thème
python dictionary/prefetch.py --stats    # état du cache par thème
```

---

## Commandes CLI

```bash
python melimo.py                          # Menu interactif
python melimo.py --generate               # Génération rapide
python melimo.py --puzzle puzzles/x.json  # Charger un puzzle JSON
python melimo.py --verify puzzles/x.json  # Valider un fichier puzzle
python melimo.py --prefetch               # Pré-télécharger les définitions
```
