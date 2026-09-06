"""Zufällige 1D-Cutting-Stock-Instanzen, EIN Rollentyp - identische Erzeugung wie
in jedem vorherigen Stück dieser Linie (eigene Kopie, kein Cross-Import
zwischen den Repos)."""

from dataclasses import dataclass

import numpy as np

from cg_constants import WIDTH_FRACTION_RANGE


@dataclass(frozen=True)
class CuttingStockInstance:
    roll_width: int
    item_widths: tuple  # eine Breite je Auftragstyp
    item_demands: tuple  # Bedarf (Menge) je Auftragstyp, parallel zu item_widths

    @property
    def n_types(self):
        return len(self.item_widths)


def generate_instance(n_types, roll_width, max_demand, seed):
    rng = np.random.default_rng(seed)
    lo = max(1, round(WIDTH_FRACTION_RANGE[0] * roll_width))
    hi = max(lo + 1, round(WIDTH_FRACTION_RANGE[1] * roll_width))
    widths = rng.integers(lo, hi + 1, size=n_types)
    demands = rng.integers(1, max_demand + 1, size=n_types)
    return CuttingStockInstance(
        roll_width=int(roll_width),
        item_widths=tuple(int(w) for w in widths),
        item_demands=tuple(int(d) for d in demands),
    )
