"""
Écran À propos — Histoire et contexte du jeu Mélimo.
"""
from __future__ import annotations
import streamlit as st


def render() -> None:
    st.markdown(
        "<h2 style='text-align:center; color:#4caf50;'>ℹ️ À propos de Mélimo</h2>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown("""
### Un jeu québécois né en 1999

**Mélimo** est un jeu de lettres et de mots inventé par le Québécois **Yvon Ferland** et publié
pour la première fois en **1999**. Le nom *Mélimo* — ainsi que sa variante abrégée — est une marque
de commerce déposée appartenant à son créateur. Les grilles et les règles correspondantes sont
également protégées.

L'édition originale était publiée par la compagnie **9036-8184 Québec inc.** (Charlesbourg, Québec),
imprimée par l'Imprimerie d'Arthabaska à Victoriaville et distribuée par *Les Messageries de presse
Benjamin inc.*

---

### Principe du jeu original

Dans la version publiée sur papier, les mots sont placés les uns à la suite des autres dans une
grille de lettres, formant un chemin en labyrinthe. Les lettres se déploient **à l'horizontale ou
à la verticale uniquement** — les diagonales sont interdites. Le joueur repère chaque mot grâce à
sa définition, puis suit le chemin en encerclant la dernière lettre de chaque réponse pour ne pas
perdre le fil.

Le dernier mot de la grille peut être un **Mot Mystère** : aucune définition n'est fournie, seul
le nombre de lettres est indiqué. Le joueur doit le déduire du contexte et de la position restante
dans la grille.

Trois niveaux de difficulté rythmaient les livrets : *Facile*, *Moyen* et *Difficile*, distingués
par la longueur moyenne des mots et la complexité des définitions.

---

### La génération informatique

Dès l'origine, les grilles Mélimo étaient générées par **logiciel** — un programme PC conçu par
*Normand Gagnon* et adapté pour Macintosh par *Dominique Jacques*. C'est ce qui permettait de
produire des livrets entiers avec des grilles variées sans les construire à la main.

Cette version numérique s'inscrit dans cette même tradition : les grilles sont générées
algorithmiquement (marche aléatoire auto-évitante), les définitions sont récupérées en temps réel
depuis le **Wiktionnaire francophone**, et le tout est jouable directement dans le navigateur.

---

### Mélimo en quelques mots

> *« Un jeu instructif comme les mots croisés et familier comme les mots mystères. Un jeu qui
> stimule votre mémoire, votre concentration et votre intuition tout en améliorant grandement
> votre orthographe et votre vocabulaire. »*
>
> — Yvon Ferland, © 1999
""")

    st.markdown("---")
    if st.button("← Retour à l'accueil", use_container_width=True):
        st.session_state.screen = "home"
        st.rerun()
