"""
Column Generation am Cutting-Stock-Problem – interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Sechstes Stück der Cutting-Stock-Linie, das erste mit eigenständigem Namen -
der eigentliche Anlass der ganzen zweiten Linie: ein Problem mit natürlich
exponentiell vielen impliziten Variablen (Mustern). Löst zum ersten Mal in
dieser Linie NICHT über Verzweigung, sondern über LP + Spaltengenerierung.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import cg_constants as C
from cg_bruteforce import solve_bruteforce
from cg_evaluation import bound_comparison, roundup_quality
from cg_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from cg_scenario import generate_instance
from cg_solver import solve
from cg_visualization import build_bound_chart, build_bound_comparison_chart, build_pattern_bar

st.set_page_config(page_title="Column Generation am Cutting-Stock-Problem – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _compute_solve(n_types, roll_width, max_demand, seed):
    instance = generate_instance(n_types, roll_width, max_demand, seed)
    result = solve(instance)
    true_optimum = solve_bruteforce(instance)
    return instance, result, true_optimum


st.title("📐📦 Column Generation am Cutting-Stock-Problem")
st.markdown(
    """
Sechstes Stück der Cutting-Stock-Linie - das erste mit einem eigenständigen
Namen. Genau dieses Verfahren war der ursprüngliche Anlass für die ganze
zweite Linie: Column Generation braucht ein Problem mit natürlich
**exponentiell vielen impliziten Variablen** (Mustern) - das gibt reines
Rucksack nicht her. Anders als jedes vorherige Stück dieser Linie löst diese
Demo NICHT über einen Suchbaum, sondern über eine echte **LP + schrittweise
Spaltengenerierung** (Gilmore-Gomory-Formulierung).
"""
)
st.caption(
    "Anders als die Fall-Demos im Portfolio, die an einem Anwendungsfall mehrere Verfahren "
    "vergleichen, zeigt diese Demo - wie jedes Stück dieser Linie - ein Verfahren an einem "
    "wachsenden Beispiel."
)

with st.expander("So funktioniert Spaltengenerierung", expanded=True):
    st.markdown(
        r"""
Statt vorab ALLE möglichen Schnittmuster aufzuzählen (exponentiell viele),
beginnt die Suche mit ein paar naheliegenden Mustern und fragt bei Bedarf
gezielt nach einem besseren: löse das **Master-LP** (wie viele Rollen mit den
bisher bekannten Mustern mindestens nötig sind), lies daraus **Dual-Werte**
ab (wie "wertvoll" jeder Auftragstyp gerade ist), und löse damit ein kleines
**Pricing-Teilproblem** - selbst wieder ein Rucksackproblem: welches Muster
nutzt die aktuell wertvollsten Auftragstypen am besten aus? Verbessert dieses
Muster den Master, wird es aufgenommen und die Runde beginnt von vorn - sonst
ist das LP-Optimum erreicht, OHNE je alle Muster einzeln durchprobiert zu
haben.

Das Pricing-Teilproblem ist hier ein **unbeschränktes** Rucksackproblem
(jeder Auftragstyp beliebig oft wiederverwendbar) - ein bewusster Kontrast zu
`dynamic-programming-demo`s BESCHRÄNKTER Variante aus der ersten Linie.
        """
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
PRESET_HELP = {
    "Winzige Instanz (jede Iteration sichtbar)": "3 Auftragstypen - alle paar Iterationen der Spaltengenerierung nachvollziehbar.",
    "Deutlich engere Schranke": "Die Gilmore-Gomory-Schranke liegt hier deutlich über der einfachen Summenschranke - und trifft exakt das wahre Optimum.",
    "Schranke eng, Rundung daneben": "Die Schranke selbst ist exakt - aber naives Aufrunden der Muster-Nutzungen verfehlt das Optimum deutlich.",
}
preset_cols = st.columns(len(C.PRESETS))
for i, name in enumerate(C.PRESETS.keys()):
    with preset_cols[i]:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=PRESET_HELP[name])

st.caption(
    "🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, "
    "um ein Szenario zu teilen."
)

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_types = st.slider("Anzahl Auftragstypen", *bounds("n_types_slider"), key="n_types_slider")
    roll_width = st.slider("Rollenbreite", *bounds("roll_width_slider"), key="roll_width_slider")
    max_demand = st.slider(
        "Maximaler Bedarf je Auftragstyp", *bounds("max_demand_slider"), key="max_demand_slider",
    )
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)

    st.button(
        "🎲 Neue Instanz generieren",
        width="stretch",
        on_click=randomize_seed,
        help="Würfelt neue Auftragsbreiten und -mengen.",
    )

sync_query_params(n_types, roll_width, max_demand, seed)

scenario_key = (int(n_types), int(roll_width), int(max_demand), int(seed))

with st.spinner("Generiere Spalten..."):
    instance, result, true_optimum = _compute_solve(*scenario_key)

st.caption(
    f"🔗 {instance.n_types} Auftragstypen, Breiten {instance.item_widths} mit Bedarf "
    f"{instance.item_demands}, Rollenbreite {instance.roll_width}."
)

st.markdown("## 🎯 Die Spaltengenerierung Schritt für Schritt")

max_step = len(result.iterations) - 1
if "cg_step" not in st.session_state or st.session_state.get("cg_step_owner") != scenario_key:
    st.session_state["cg_step"] = max_step
    st.session_state["cg_step_owner"] = scenario_key

if max_step == 0:
    step = 0
    st.caption("Schon das erste Master-LP war optimal - kein Regler nötig.")
else:
    step = st.slider(
        "Iteration", 0, max_step, key="cg_step",
        help="Ein Schritt = ein Master-LP-Aufruf plus ein Pricing-Aufruf.",
    )

current = result.iterations[step]

chart_col, pattern_col = st.columns([3, 2])
with chart_col:
    st.plotly_chart(build_bound_chart(result, true_optimum, step), width="stretch", key=f"bound_{step}")
with pattern_col:
    if current.new_pattern is not None:
        st.markdown(f"**Neu aufgenommenes Muster** (reduzierte Kosten: {current.reduced_cost:.3f})")
    else:
        st.markdown("**Kein verbesserndes Muster mehr gefunden - LP-Optimum erreicht.**")
    st.plotly_chart(build_pattern_bar(instance, current), width="stretch", key=f"pattern_{step}")

lm1, lm2, lm3 = st.columns(3)
lm1.metric("Master-Zielfunktion (bisher)", f"{current.master_objective:.3f}")
lm2.metric("Anzahl Muster (bisher)", current.n_patterns_before)
lm3.metric("Iterationen insgesamt", len(result.iterations))

st.markdown("---")

st.subheader("📐 Wie eng ist diese Schranke wirklich?")
cmp = bound_comparison(instance, result, true_optimum)
st.plotly_chart(build_bound_comparison_chart(cmp), width="stretch", key="bound_comparison")

bc1, bc2, bc3 = st.columns(3)
bc1.metric("Einfache Schranke", cmp["weak_bound"], help="Gesamtbreite aller Aufträge geteilt durch Rollenbreite, aufgerundet - wie in cutting-stock-branch-cut-demo.")
bc2.metric("Gilmore-Gomory-Schranke", f"⌈{cmp['lp_bound']:.2f}⌉ = {cmp['ceil_lp_bound']}", help="Aufgerundete LP-Schranke der Spaltengenerierung.")
bc3.metric("Wahres Optimum", cmp["true_optimum"])

if cmp["irup_holds"]:
    st.success(
        f"✅ Die aufgerundete Gilmore-Gomory-Schranke trifft hier EXAKT das wahre Optimum "
        f"({cmp['ceil_lp_bound']}) - deutlich enger als die einfache Schranke ({cmp['weak_bound']}). "
        f"Das ist die aus der Literatur bekannte \"Integer-Round-Up-Property\": in der weit "
        f"überwiegenden Praxis (in jedem hier geprüften Fall) trifft sie zu - eine mathematische "
        f"Garantie ist das aber NICHT (bekannte, extrem seltene Gegenbeispiele existieren)."
    )
else:
    st.warning(
        f"⚠️ Bei dieser Instanz weicht die aufgerundete Schranke ({cmp['ceil_lp_bound']}) vom "
        f"wahren Optimum ({cmp['true_optimum']}) ab - eines der bekannten, seltenen Gegenbeispiele "
        f"zur Integer-Round-Up-Property, oder ein Melden wert."
    )

st.markdown("---")

st.subheader("🔀 Von der Schranke zur echten Lösung")
st.markdown(
    """
Eine enge Schranke zu kennen ist NICHT dasselbe wie eine gute Lösung zu
haben. Die fraktionalen Muster-Nutzungen (λ) des finalen Master-LP naiv
aufgerundet ergibt eine zulässige, aber nicht notwendig optimale
Ganzzahllösung:
"""
)
ru = roundup_quality(result, true_optimum)
rc1, rc2 = st.columns(2)
rc1.metric(
    "Naive Rundungslösung", f"{ru['roundup_bins']} Rollen",
    delta=f"+{ru['excess']} ggü. Optimum" if ru["excess"] > 0 else "trifft das Optimum",
    delta_color="inverse" if ru["excess"] > 0 else "off",
)
rc2.metric("Wahres Optimum", f"{ru['true_optimum']} Rollen")

if ru["matches_optimum"]:
    st.info(
        "Bei dieser Instanz trifft sogar die naive Rundung das Optimum - probieren Sie das Preset "
        "\"Schranke eng, Rundung daneben\" für ein Gegenbeispiel."
    )
else:
    st.warning(
        f"⚠️ Obwohl die Schranke selbst exakt bei **{cmp['ceil_lp_bound']}** liegt, braucht die naive "
        f"Rundung **{ru['excess']}** Rollen mehr. Das nächste Stück dieser Linie, "
        f"**branch-and-price-demo**, erzwingt über echte Ryan-Foster-Verzweigung eine tatsächlich "
        f"optimale Ganzzahllösung - der direkte Aufhänger."
    )

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Master-LP**: $\min \sum_p \lambda_p$ unter $\sum_p a_{p,i} \lambda_p \geq
q_i\ \forall i$, $\lambda_p \geq 0$ - $a_{p,i}$ ist, wie oft Auftragstyp $i$
in Muster $p$ vorkommt.

**Pricing-Teilproblem** (unbeschränkter Rucksack): gegeben Dual-Werte
$\pi_i$, finde $a_i \geq 0$ ganzzahlig mit $\sum_i w_i a_i \leq W$, das
$\sum_i \pi_i a_i$ maximiert. Reduzierte Kosten $= 1 - \sum_i \pi_i a_i$;
solange negativ, verbessert das gefundene Muster den Master.

$$
f(c) = \max\left(f(c-1),\ \max_{i:\ w_i \leq c} f(c - w_i) + \pi_i\right)
$$

**Integer-Round-Up-Property (IRUP)**: in der weit überwiegenden Praxis (und
in jedem hier per Sweep geprüften Fall) gilt $\lceil \text{LP-Optimum}
\rceil = $ wahres Ganzzahl-Optimum für Cutting Stock - eine der bekanntesten
empirischen Beobachtungen der Cutting-Stock-Literatur. Sie ist aber NICHT
allgemein bewiesen; bekannte, extrem seltene und künstlich konstruierte
Gegenbeispiele existieren (z. B. Marcotte 1985).

**Warum die Schranke nicht automatisch die Lösung liefert**: das Master-LP
liefert fraktionale $\lambda_p$ - naives Aufrunden kann beliebig viele Rollen
zu viel verwenden. Implementiert in `cg_master.py` (Master-LP),
`cg_pricing.py` (Pricing-DP), `cg_solver.py` (die Schleife) und
`cg_bruteforce.py` (unabhängige Referenzlösung für Tests).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
