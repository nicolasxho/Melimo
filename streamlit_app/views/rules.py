"""
Écran d'aide — Règles du jeu Mélimo.
"""
from __future__ import annotations
import streamlit as st

import scoring


def render() -> None:
    st.markdown(
        "<h2 style='text-align:center; color:#4caf50;'>❓ Règles du jeu</h2>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown("""
### Comment jouer ?

**Mélimo** est un jeu de mots en labyrinthe. Les mots se suivent les uns après les autres
sur un chemin caché dans la grille. Chaque mot débute là où le précédent s'est terminé.

1. **Le premier mot** est donné gratuitement pour repérer le point de départ.
2. **Lis la définition** du mot courant (affiché en jaune dans la liste à droite).
3. **Saisie ta réponse** dans le champ de texte — les accents, majuscules et tirets ne comptent pas.
4. Les mots se résolvent **dans l'ordre**, tu ne peux pas passer à la suite sans avoir trouvé (ou révélé) le mot courant.
5. Le dernier mot est le **★ MOT MYSTÈRE** — il rapporte le double de points !
""")

    st.markdown("---")
    st.markdown("### Système de points")

    hint_costs = " / ".join(
        f"Indice {i+1} : −{c} pts" for i, c in enumerate(scoring.HINT_PENALTIES)
    )
    st.markdown(f"""
| Élément | Effet |
|---|---|
| Réponse correcte | **+{scoring.BASE_SCORE} pts** de base |
| Mot mystère | ×**{scoring.MYSTERY_MULTIPLIER}** (base doublée) |
| Temps | **−{scoring.TIME_PENALTY_RATE:g} pt/seconde** écoulée |
| Mauvaise réponse | **−{scoring.ERROR_PENALTY} pts** |
| {hint_costs} | (pénalité cumulative) |
| Minimum garanti | **{scoring.MIN_WORD_SCORE} pts** par mot trouvé |
""")

    st.markdown("---")
    st.markdown("### Les indices")
    st.markdown(f"""
Tu peux demander jusqu'à **{scoring.MAX_HINTS} indices** par mot, chacun plus coûteux que le précédent :

- 💡 **Indice 1** — Nombre de lettres du mot (−{scoring.HINT_PENALTIES[0]} pts)
- 💡 **Indice 2** — Première lettre du mot (−{scoring.HINT_PENALTIES[1]} pts)
- 💡 **Indice 3** — Position du mot sur la grille (−{scoring.HINT_PENALTIES[2]} pts)

Si tu es vraiment bloqué, tu peux **👁 Révéler** le mot pour 0 point et passer à la suite.
""")

    st.markdown("---")
    st.markdown("### Mode contre-la-montre")
    st.markdown("""
Dans les écrans de configuration, tu peux choisir une **limite de temps** (3, 5 ou 10 minutes).
Le compte à rebours s'affiche en haut à droite. À la fin du temps, la partie se termine automatiquement.
""")

    st.markdown("---")
    if st.button("← Retour à l'accueil", use_container_width=True):
        st.session_state.screen = "home"
        st.rerun()
