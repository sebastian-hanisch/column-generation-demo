"""Die Spaltengenerierungs-Schleife: Master lösen, Duals extrahieren, Pricing
lösen, bei negativen reduzierten Kosten ein neues Muster aufnehmen - sonst
stoppen (das LP-Optimum der vollen, impliziten Mustermenge ist erreicht, ohne
je alle Muster einzeln aufgezählt zu haben). Muster analog zu
cutting-planes-demo/cp_solver.py's Iteration/CuttingPlaneResult."""

import math
from dataclasses import dataclass

from cg_constants import MAX_ITERATIONS
from cg_master import solve_master
from cg_pricing import unbounded_knapsack


@dataclass(frozen=True)
class Iteration:
    master_objective: float
    duals: tuple
    new_pattern: object  # None, falls keine verbessernde Spalte mehr gefunden wurde
    reduced_cost: float
    n_patterns_before: int


@dataclass(frozen=True)
class CGResult:
    iterations: tuple
    patterns: tuple
    final_objective: float
    lambdas: tuple
    roundup_bins: int  # sum(ceil(λ_p)) - eine naive, nicht notwendig optimale Ganzzahllösung


def _initial_patterns(instance):
    """Homogene Muster - je Auftragstyp so viele Stücke wie möglich auf eine
    Rolle. Garantiert von Anfang an ein zulässiges Master-LP."""
    patterns = []
    for i, w in enumerate(instance.item_widths):
        count = instance.roll_width // w
        pattern = [0] * instance.n_types
        pattern[i] = count
        patterns.append(tuple(pattern))
    return patterns


def solve(instance, max_iterations=MAX_ITERATIONS):
    patterns = _initial_patterns(instance)
    iterations = []

    objective, lambdas = None, None
    for _ in range(max_iterations):
        objective, lambdas, duals = solve_master(instance, patterns)
        best_value, pattern = unbounded_knapsack(instance.item_widths, duals, instance.roll_width)
        reduced_cost = 1 - best_value

        if reduced_cost < -1e-6 and pattern not in patterns:
            iterations.append(Iteration(objective, tuple(duals), pattern, reduced_cost, len(patterns)))
            patterns.append(pattern)
        else:
            iterations.append(Iteration(objective, tuple(duals), None, reduced_cost, len(patterns)))
            break

    roundup_bins = sum(math.ceil(l - 1e-9) for l in lambdas)

    return CGResult(
        iterations=tuple(iterations),
        patterns=tuple(patterns),
        final_objective=objective,
        lambdas=tuple(lambdas),
        roundup_bins=roundup_bins,
    )
