"""Das Restricted-Master-LP der Spaltengenerierung: minimiere die Anzahl
benötigter Rollen (Summe der Muster-Nutzungen λ_p) unter der Bedingung, dass
jeder Auftragstyp mindestens seinen Bedarf erhält. Gelöst mit
scipy.optimize.linprog - das erste Mal in dieser Linie, dass ein LP nicht nur
eine SCHRANKE innerhalb einer Suche liefert (wie in
cutting-stock-branch-cut-demo), sondern selbst das Kernverfahren ist."""

import numpy as np
from scipy.optimize import linprog


def solve_master(instance, patterns):
    """patterns: Liste von Mustern (Tupel `(a_1, ..., a_n)`, wie oft jeder
    Auftragstyp in diesem Muster vorkommt). Minimiere sum(λ_p) unter
    sum_p(a_p_i * λ_p) >= q_i für jeden Auftragstyp i, λ_p >= 0.

    scipy.linprog kennt nur <=-Ungleichungen, daher wird die Bedeckungs-
    bedingung negiert: -sum_p(a_p_i * λ_p) <= -q_i. Die von scipy für diese
    negierte Form zurückgegebenen Dual-Werte (`ineqlin.marginals`) sind
    empirisch (per Prototyp) nicht-positiv - das Vorzeichen wird umgedreht,
    damit die Dual-Werte als nicht-negative "Schattenpreise" (wie viel ein
    zusätzlicher Bedarf an Auftragstyp i den Zielfunktionswert erhöhen würde)
    direkt als Pricing-Werte verwendbar sind.

    Gibt (Zielfunktionswert, λ-Werte, Dual-Werte) zurück."""
    n_types = instance.n_types
    n_patterns = len(patterns)

    c = np.ones(n_patterns)
    A_ub = np.zeros((n_types, n_patterns))
    for p_idx, pattern in enumerate(patterns):
        for i in range(n_types):
            A_ub[i, p_idx] = -pattern[i]
    b_ub = np.array([-d for d in instance.item_demands], dtype=float)
    bounds = [(0, None)] * n_patterns

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
    duals = -result.ineqlin.marginals
    return result.fun, result.x, duals
