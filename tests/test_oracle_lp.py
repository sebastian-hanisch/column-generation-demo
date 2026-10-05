"""Unabhängiges Orakel für die Spaltengenerierung: LP-Relaxierung über die
VOLLSTÄNDIGE Mustermenge (alle Muster aufgezählt, ein einziges `linprog`),
Dual-LP und ganzzahliges Optimum per `scipy.optimize.milp` (HiGHS) - ein anderer
Rechenweg als Restricted Master + Pricing-DP + Bruteforce-Suchbaum."""

import math

import numpy as np
import pytest

scipy_opt = pytest.importorskip("scipy.optimize")

from cg_bruteforce import solve_bruteforce
from cg_scenario import generate_instance
from cg_solver import solve


def _all_patterns(instance):
    widths = instance.item_widths
    out = []

    def rec(i, remaining, current):
        if i == len(widths):
            if any(current):
                out.append(tuple(current))
            return
        for k in range(remaining // widths[i] + 1):
            current.append(k)
            rec(i + 1, remaining - k * widths[i], current)
            current.pop()

    rec(0, instance.roll_width, [])
    return out


def _oracle(instance):
    A = np.array(_all_patterns(instance), dtype=float).T  # Typen x Muster
    q = np.array(instance.item_demands, dtype=float)
    m = A.shape[1]
    primal = scipy_opt.linprog(np.ones(m), A_ub=-A, b_ub=-q, bounds=(0, None), method="highs")
    ip = scipy_opt.milp(
        np.ones(m),
        constraints=scipy_opt.LinearConstraint(A, q, np.inf),
        integrality=np.ones(m),
        bounds=scipy_opt.Bounds(0, np.inf),
    )
    return primal.fun, round(ip.fun), A, q


CASES = [(n, w, d, s) for n in (2, 4, 6) for w in (50, 100, 173) for d in (1, 3) for s in range(3)]


@pytest.mark.parametrize("n_types,roll_width,max_demand,seed", CASES)
def test_column_generation_matches_full_pattern_lp(n_types, roll_width, max_demand, seed):
    instance = generate_instance(n_types, roll_width, max_demand, seed)
    result = solve(instance)
    lp, ip, A, q = _oracle(instance)

    # Das LP-Optimum der vollen Mustermenge wird ohne Aufzählung erreicht.
    assert result.final_objective == pytest.approx(lp, abs=1e-6)

    # Duale Zulässigkeit/starke Dualität am Ende: kein Muster hat negative reduzierte Kosten.
    y = np.array(result.iterations[-1].duals)
    assert (y >= -1e-9).all()
    assert (A.T @ y).max() <= 1 + 1e-6
    assert q @ y == pytest.approx(lp, abs=1e-6)

    # Master-Zielwert fällt monoton; Pricing-Wert = Maximum über ALLE Muster.
    objs = [it.master_objective for it in result.iterations]
    assert all(b <= a + 1e-9 for a, b in zip(objs, objs[1:]))
    for it in result.iterations:
        assert 1 - it.reduced_cost == pytest.approx((A.T @ np.array(it.duals)).max(), abs=1e-6)

    # Schranke gültig, Rundungslösung zulässig; Bruteforce = milp (wo klein genug).
    assert math.ceil(lp - 1e-6) <= ip <= result.roundup_bins
    if sum(instance.item_demands) <= 12:
        assert solve_bruteforce(instance) == ip
