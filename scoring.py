"""
Système de pointage de Mélimo.

Principes :
- Plus le joueur répond vite, plus il gagne de points.
- Chaque mauvaise réponse inflige une lourde pénalité.
- Les indices sont progressifs : chaque niveau coûte plus cher.
- Le mot mystère rapporte le double.
- Un score minimal de 10 points est garanti par mot trouvé.
"""
from __future__ import annotations

# ── Constantes ────────────────────────────────────────────────────────────────

BASE_SCORE: int = 100           # Points de base par mot ordinaire
MYSTERY_MULTIPLIER: int = 2     # Multiplicateur pour le mot mystère
TIME_PENALTY_RATE: float = 1.5  # Points perdus par seconde écoulée
ERROR_PENALTY: int = 30         # Points perdus par mauvaise réponse
MIN_WORD_SCORE: int = 10        # Score minimum garanti par mot trouvé

# Indices progressifs : [niveau 1, niveau 2, niveau 3]
# Niveau 1 : nombre de lettres  → −10 pts
# Niveau 2 : première lettre    → −20 pts
# Niveau 3 : position sur grille → −30 pts
HINT_PENALTIES: list[int] = [10, 20, 30]
HINT_LABELS: list[str] = [
    "Nombre de lettres",
    "Première lettre",
    "Position sur la grille",
]
MAX_HINTS: int = len(HINT_PENALTIES)


# ── Helpers indices ───────────────────────────────────────────────────────────

def hint_total_penalty(hints: int) -> int:
    """Pénalité cumulée pour `hints` indices demandés (niveaux progressifs)."""
    return sum(HINT_PENALTIES[:min(hints, MAX_HINTS)])


def hint_next_cost(hints_used: int) -> int | None:
    """Coût du prochain indice, ou None si tous les indices ont été utilisés."""
    if hints_used >= MAX_HINTS:
        return None
    return HINT_PENALTIES[hints_used]


def hint_next_label(hints_used: int) -> str | None:
    """Libellé du prochain indice, ou None si tous utilisés."""
    if hints_used >= MAX_HINTS:
        return None
    return HINT_LABELS[hints_used]


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
        hints:           Nombre d'indices demandés (pénalité progressive par niveau).

    Returns:
        Score (entier positif ≥ MIN_WORD_SCORE).
    """
    base = BASE_SCORE * MYSTERY_MULTIPLIER if is_mystery else BASE_SCORE
    time_penalty = int(elapsed_seconds * TIME_PENALTY_RATE)
    error_penalty = errors * ERROR_PENALTY
    hp = hint_total_penalty(hints)
    return max(MIN_WORD_SCORE, base - time_penalty - error_penalty - hp)


def score_breakdown(
    is_mystery: bool,
    elapsed_seconds: float,
    errors: int,
    hints: int,
) -> dict[str, int]:
    """Retourne le détail du calcul du score (utile pour l'affichage)."""
    base = BASE_SCORE * MYSTERY_MULTIPLIER if is_mystery else BASE_SCORE
    time_penalty = int(elapsed_seconds * TIME_PENALTY_RATE)
    error_penalty = errors * ERROR_PENALTY
    hp = hint_total_penalty(hints)
    total = max(MIN_WORD_SCORE, base - time_penalty - error_penalty - hp)
    return {
        "base": base,
        "time_penalty": time_penalty,
        "error_penalty": error_penalty,
        "hint_penalty": hp,
        "total": total,
    }
