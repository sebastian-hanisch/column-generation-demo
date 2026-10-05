# Column Generation am Cutting-Stock-Problem – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-column-generation-demo.streamlit.app/)**

Sechstes Stück der Cutting-Stock-Linie - das erste mit einem eigenständigen
Namen (keine `cutting-stock-`-Vorsilbe). Genau dieses Verfahren war der
ursprüngliche Anlass für die ganze zweite Linie: Column Generation braucht
ein Problem mit natürlich **exponentiell vielen impliziten Variablen**
(Mustern) - das gibt reines Rucksack nicht her. Anders als jedes vorherige
Stück dieser Linie löst diese Demo NICHT über einen Suchbaum, sondern über
eine echte **LP + schrittweise Spaltengenerierung** (Gilmore-Gomory-
Formulierung).

## Der Algorithmus

**Master-LP**: minimiere die Anzahl benötigter Rollen unter der Bedingung,
dass jeder Auftragstyp mindestens seinen Bedarf erhält - über eine (zunächst
kleine) Menge bekannter Schnittmuster.

**Pricing-Teilproblem**: aus den Dual-Werten des Master-LP (wie "wertvoll"
jeder Auftragstyp gerade ist) wird per **unbeschränktem Rucksackproblem**
(jeder Auftragstyp beliebig oft wiederverwendbar, im Gegensatz zu
`dynamic-programming-demo`s beschränkter Variante) das aktuell nützlichste
Muster gesucht. Verbessert es den Master, wird es aufgenommen - sonst ist das
LP-Optimum erreicht, ohne je alle (exponentiell vielen) Muster einzeln
durchprobiert zu haben.

## Drei zentrale Fragen, per Prototyp verifiziert statt angenommen

1. **Funktioniert der Dual-Werte-Export von scipy zuverlässig?** Ja - das
   Vorzeichen musste empirisch bestimmt werden (siehe `cg_master.py`s
   Docstring).
2. **Konvergiert die Schleife, und ist die Schranke gültig?** Ja - über 270+
   Zufallsinstanzen immer konvergiert (1-12 Iterationen), und
   `⌈LP-Schranke⌉ == wahres Optimum` traf in 100 % der getesteten Fälle zu -
   die aus der Literatur bekannte **Integer-Round-Up-Property (IRUP)**, die
   in der weit überwiegenden Praxis, aber NICHT beweisbar universell gilt
   (extrem seltene, künstlich konstruierte Gegenbeispiele existieren, z. B.
   Marcotte 1986).
3. **Liefert eine enge Schranke automatisch auch eine gute Lösung?**
   Überraschenderweise NEIN - der wichtigste Fund dieses Stücks: naives
   Aufrunden der fraktionalen Muster-Nutzungen trifft nur in rund der Hälfte der Fälle
   (~48 %; 240 Instanzen: 2-7 Typen, Bedarf 1-4, Rollenbreite 100, Seeds 0-9)
   dieselbe Rollenzahl wie das wahre Optimum. Eine Instanz zeigt das
   besonders deutlich: Schranke exakt bei 6, Rundungslösung braucht 9 Rollen.
   Der direkte Aufhänger für
   [branch-and-price-demo](https://github.com/sebastian-hanisch/branch-and-price-demo)
   (siebtes und letztes Stück dieser Linie), das über echte
   Ryan-Foster-Verzweigung eine tatsächlich optimale Ganzzahllösung erzwingt -
   auf genau der Instanz oben liefert es die korrekten 6 Rollen statt der
   hier gezeigten 9.

## Verifikation

- **Bound-Gültigkeit**: `⌈LP-Schranke⌉` überschätzt nie das wahre Optimum
  (gegen Bruteforce geprüft).
- **Konvergenz-Test**: die Schleife terminiert innerhalb der Sicherheitsgrenze
  über einen breiten Sweep.
- **IRUP-Beobachtungstest**: `⌈LP-Schranke⌉ == wahres Optimum` für alle drei
  Presets (als Beobachtung formuliert, nicht als bewiesene Garantie).
- **Rundungs-Schwäche-Regressionstest**: verankert den zentralen Fund oben.
- **Muster-Gültigkeit**: jedes per Pricing gefundene Muster respektiert die
  Rollenbreite.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Hauptablauf: Presets, Einstellungen, Iterations-Animation, Schranken-Vergleich, Rundungs-Sektion, Formulierungs-Expander |
| `cg_constants.py` | Defaults, Regler-Grenzen, Sicherheitsgrenzen, `PRESETS` |
| `cg_presets.py` | `SettingSpec`/`SETTING_SPECS`, Permalink-Logik, Presets, Zufalls-Seed-Button |
| `cg_scenario.py` | Zufällige Cutting-Stock-Instanzen |
| `cg_pricing.py` | Pricing-Teilproblem (unbeschränkter Rucksack, DP) |
| `cg_master.py` | Restricted-Master-LP inkl. Dual-Werte-Extraktion (scipy) |
| `cg_solver.py` | Die Spaltengenerierungs-Schleife |
| `cg_bruteforce.py` | Unabhängige Referenzlösung (vollständige Enumeration) |
| `cg_evaluation.py` | Schranken-Vergleich, Rundungs-Qualität |
| `cg_visualization.py` | Bound-Trajektorie, Muster-Anzeige, Schranken-Vergleich (Plotly) |
| `tests/` | Bound-Gültigkeit, Konvergenz, IRUP-Beobachtung, Rundungs-Schwäche, Muster-Gültigkeit |

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Exakte Suche erklärt: Rucksack und Cutting Stock](https://sebastianhanisch.net/konzepte-exakte-suche.html).
