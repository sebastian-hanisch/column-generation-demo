import math

import pytest

from cg_bruteforce import solve_bruteforce
from cg_constants import PRESETS
from cg_evaluation import bound_comparison, roundup_quality, weak_bound_compact
from cg_scenario import generate_instance
from cg_solver import solve


def test_matches_hand_computed_example():
    from cg_scenario import CuttingStockInstance

    instance = CuttingStockInstance(roll_width=10, item_widths=(6,), item_demands=(3,))
    result = solve(instance)
    assert math.ceil(result.final_objective - 1e-6) == 3
    assert solve_bruteforce(instance) == 3


def test_lp_bound_is_always_valid_against_bruteforce():
    # Eine gültige Schranke darf das wahre Optimum nie überschätzen.
    for n_types in range(2, 6):
        for max_demand in range(1, 4):
            for seed in range(15):
                instance = generate_instance(n_types, 100, max_demand, seed)
                result = solve(instance)
                true_optimum = solve_bruteforce(instance)
                ceil_bound = math.ceil(result.final_objective - 1e-6)
                assert ceil_bound <= true_optimum, f"n={n_types} d={max_demand} seed={seed}"


def test_converges_within_safety_limit_across_a_wide_sweep():
    for n_types in range(2, 8):
        for max_demand in range(1, 5):
            for seed in range(10):
                instance = generate_instance(n_types, 100, max_demand, seed)
                result = solve(instance, max_iterations=200)
                assert len(result.iterations) < 200, f"n={n_types} d={max_demand} seed={seed} did not converge"


def test_gilmore_gomory_bound_is_never_weaker_than_the_compact_bound():
    for n_types in range(2, 7):
        for max_demand in range(1, 4):
            for seed in range(10):
                instance = generate_instance(n_types, 100, max_demand, seed)
                result = solve(instance)
                weak = weak_bound_compact(instance)
                ceil_lp = math.ceil(result.final_objective - 1e-6)
                assert ceil_lp >= weak, f"n={n_types} d={max_demand} seed={seed}"


@pytest.mark.parametrize("name", list(PRESETS.keys()))
def test_presets_lp_bound_matches_true_optimum(name):
    # Beobachtung (IRUP), keine mathematisch bewiesene Garantie - siehe
    # app.py's Formulierungs-Abschnitt. Für alle drei Presets per Prototyp
    # bestätigt.
    instance = generate_instance(**PRESETS[name])
    result = solve(instance)
    true_optimum = solve_bruteforce(instance)
    cmp = bound_comparison(instance, result, true_optimum)
    assert cmp["irup_holds"], name


def test_roundup_heuristic_can_miss_the_optimum_on_a_known_instance():
    # Regressionstest für den zentralen ehrlichen Fund dieses Stücks: eine
    # enge Schranke liefert nicht automatisch eine gute Lösung. Bei diesem
    # Preset weicht die naive Rundung nachweislich vom Optimum ab (per
    # Prototyp verifiziert: 9 statt 6 Rollen).
    instance = generate_instance(**PRESETS["Schranke eng, Rundung daneben"])
    result = solve(instance)
    true_optimum = solve_bruteforce(instance)
    quality = roundup_quality(result, true_optimum)
    assert not quality["matches_optimum"]
    assert quality["excess"] > 0


def test_every_priced_pattern_respects_the_roll_width():
    for n_types in range(2, 6):
        for max_demand in range(1, 4):
            for seed in range(8):
                instance = generate_instance(n_types, 100, max_demand, seed)
                result = solve(instance)
                for pattern in result.patterns:
                    total_width = sum(w * a for w, a in zip(instance.item_widths, pattern))
                    assert total_width <= instance.roll_width, f"n={n_types} d={max_demand} seed={seed}"
