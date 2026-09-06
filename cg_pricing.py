"""Das Pricing-Teilproblem der Spaltengenerierung: gegeben Dual-Werte (einen
"Wert" je Auftragstyp), finde das Muster, das den Gesamtwert maximiert, ohne
die Rollenbreite zu überschreiten. Das ist ein UNBESCHRÄNKTES Rucksackproblem
- jeder Auftragstyp beliebig oft wiederverwendbar, nur durch die Rollenbreite
begrenzt (nicht durch den tatsächlichen Bedarf `q_i`) - bewusst ein Kontrast zu
dynamic-programming-demos BESCHRÄNKTER Variante aus der ersten Linie."""


def unbounded_knapsack(widths, values, capacity):
    """DP über Kapazität 0..capacity: best[c] = maximaler Wert, den man mit
    Kapazität c erreichen kann, wenn jeder Auftragstyp beliebig oft verwendet
    werden darf. Klassische unbeschränkte-Rucksack-Rekursion:
    best[c] = max(best[c-1], max_i(best[c-w_i] + values[i]) für w_i <= c).
    Gibt (bester Wert, Muster) zurück - Muster ist ein Tupel mit der Anzahl
    jedes Auftragstyps im gefundenen Muster."""
    n = len(widths)
    best = [0.0] * (capacity + 1)
    choice = [-1] * (capacity + 1)  # welcher Auftragstyp zuletzt zu best[c] beitrug

    for c in range(1, capacity + 1):
        best[c] = best[c - 1]
        choice[c] = -1  # von c-1 geerbt, kein neuer Auftragstyp
        for i in range(n):
            if widths[i] <= c:
                candidate = best[c - widths[i]] + values[i]
                if candidate > best[c] + 1e-9:
                    best[c] = candidate
                    choice[c] = i

    pattern = [0] * n
    c = capacity
    while c > 0:
        i = choice[c]
        if i == -1:
            c -= 1
        else:
            pattern[i] += 1
            c -= widths[i]

    return best[capacity], tuple(pattern)
