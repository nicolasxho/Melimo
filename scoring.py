"""
Système de pointage de Mélimo.

Principes :
- Plus le joueur répond vite, plus il gagne de points.
- Chaque mauvaise réponse inflige une lourde pénalité.
- Demander un indice inflige une pénalité modérée.
- Le mot mystère rapporte le double.
- Un score minimal de 10 points est garanti par mot trouvé.
"""
from __future__ import annotations

# ── Constantes ────────────────────────────────────────────────────────────────

BASE_SCORE: int = 100          # Points de base par mot ordinaire
MYSTERY_MULTIPLIER: int = 2    # Multiplicateur pour le mot mystère
TIME_PENALTY_RATE: float = 1.5 # Points perdus par seconde écoulée
ERROR_PENALTY: int = 30        # Points perdus par mauvaise réponse
HINT_PENALTY: int = 20         # Points perdus par indice demandé
MIN_WORD_SCORE: int = 10       # Score minimum garanti par mot trouvé


# ── Calcul du score ───────────────────────────────────────────────────────────

def compute_word_score(
    is_mystery: bool,
    elapsed_seconds: float,
    errors: int,
    hints: int,
) -> int:
    """
    Calcule le score obtenu pour un mot.

    Args:
        is_mystery:      Le mot est-il le mot mystère ?
        elapsed_seconds: Temps écoulé depuis l'affichage du mot (en secondes).
        errors:          Nombre de mauvaises réponses saisies.
        hints:           Nombre d'indices demandés.

    Returns:
        Score (entier positif ≥ MIN_WORD_SCORE).
    """
    base = BASE_SCORE * MYSTERY_MULTIPLIER if is_mystery else BASE_SCORE
    time_penalty = int(elapsed_seconds * TIME_PENALTY_RATE)
    error_penalty = errors * ERROR_PENALTY
    hint_penalty = hints * HINT_PENALTY
    return max(MIN_WORD_SCORE, base - time_penalty - error_penalty - hint_penalty)


def score_breakdown(
    is_mystery: bool,
    elapsed_seconds: float,
    errors: int,
    hints: int,
) -> dict[str, int]:
    """
    Retourne le détail du calcul du score (utile pour l'affichage).
    """
    base = BASE_SCORE * MYSTERY_MULTIPLIER if is_mystery else BASE_SCORE
    time_penalty = int(elapsed_seconds * TIME_PENALTY_RATE)
    error_penalty = errors * ERROR_PENALTY
    hint_penalty = hints * HINT_PENALTY
    total = max(MIN_WORD_SCORE, base - time_penalty - error_penalty - hint_penalty)
    return {
        "base": base,
        "time_penalty": time_penalty,
        "error_penalty": error_penalty,
        "hint_penalty": hint_penalty,
        "total": total,
    }
