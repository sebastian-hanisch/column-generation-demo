"""Defaults, slider bounds und Presets für die Column-Generation-Demo."""

DEFAULT_N_TYPES = 4
DEFAULT_MAX_DEMAND = 2
DEFAULT_ROLL_WIDTH = 100
DEFAULT_SEED = 7

N_TYPES_MIN, N_TYPES_MAX = 2, 7
MAX_DEMAND_MIN, MAX_DEMAND_MAX = 1, 4
ROLL_WIDTH_MIN, ROLL_WIDTH_MAX = 50, 200

# Auftragsbreiten werden als Anteil der Rollenbreite gezogen - hält die Instanzen
# unabhängig von der absoluten Rollenbreite vergleichbar (wie in jedem
# vorherigen Stück dieser Linie).
WIDTH_FRACTION_RANGE = (0.15, 0.6)

# Per Prototyp kalibriert: die Spaltengenerierung konvergiert bei allen
# getesteten Instanzen (n_types bis 7, max_demand bis 4) innerhalb weniger
# Iterationen (1-12) - 200 lässt reichlich Sicherheitsabstand.
MAX_ITERATIONS = 200

PRESETS = {
    "Winzige Instanz (jede Iteration sichtbar)": {
        "n_types": 3, "roll_width": 100, "max_demand": 1, "seed": 2,
    },
    "Deutlich engere Schranke": {
        "n_types": 7, "roll_width": 100, "max_demand": 4, "seed": 13,
    },
    "Schranke eng, Rundung daneben": {
        "n_types": 7, "roll_width": 100, "max_demand": 4, "seed": 14,
    },
}
