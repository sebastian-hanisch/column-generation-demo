"""Kennzahlen und Kernvergleiche dieses Stücks: wie eng ist die Gilmore-Gomory-
LP-Schranke gegenüber der einfachen Summenschranke - und liefert eine enge
Schranke automatisch auch eine gute Ganzzahllösung?"""

import math


def weak_bound_compact(instance):
    """Die einfache Summenschranke aus cutting-stock-branch-cut-demo, hier
    eigenständig neu berechnet (kein Cross-Import zwischen den Repos dieser
    Linie): Gesamtbreite aller Aufträge durch die Rollenbreite geteilt,
    aufgerundet."""
    total_width = sum(w * d for w, d in zip(instance.item_widths, instance.item_demands))
    return -(-total_width // instance.roll_width)


def bound_comparison(instance, cg_result, true_optimum):
    weak = weak_bound_compact(instance)
    lp_bound = cg_result.final_objective
    ceil_lp = math.ceil(lp_bound - 1e-6)
    return {
        "weak_bound": weak,
        "lp_bound": lp_bound,
        "ceil_lp_bound": ceil_lp,
        "true_optimum": true_optimum,
        "irup_holds": ceil_lp == true_optimum,
    }


def roundup_quality(cg_result, true_optimum):
    return {
        "roundup_bins": cg_result.roundup_bins,
        "true_optimum": true_optimum,
        "matches_optimum": cg_result.roundup_bins == true_optimum,
        "excess": cg_result.roundup_bins - true_optimum,
    }
