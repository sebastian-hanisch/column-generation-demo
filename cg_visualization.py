"""Plotly-Visualisierungen: Konvergenz der Master-Zielfunktion über die
Iterationen (fallende Treppenlinie, Muster analog zu
cutting-planes-demo/cp_visualization.py's build_bound_chart), das gerade
aufgenommene Muster als Balkendiagramm, und der Dreier-Schranken-Vergleich
(einfache Schranke / Gilmore-Gomory-Schranke / wahres Optimum)."""

NEW_PATTERN_COLOR = "#137a6b"
TRUE_OPTIMUM_COLOR = "#2ca02c"


def build_bound_chart(result, true_optimum, step):
    import plotly.graph_objects as go

    xs = list(range(step + 1))
    ys = [result.iterations[i].master_objective for i in xs]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=xs, y=ys, mode="lines+markers", line=dict(color="#14233B", width=3, shape="hv"),
            marker=dict(size=8), name="Master-Zielfunktion (LP-Schranke)",
        )
    )
    fig.add_hline(
        y=true_optimum, line=dict(color=TRUE_OPTIMUM_COLOR, width=1.5, dash="dash"),
        annotation_text="Wahres Optimum", annotation_position="bottom right",
    )
    fig.update_layout(
        template="plotly_white", height=280,
        xaxis=dict(title="Iteration (Anzahl hinzugefügter Muster)", fixedrange=True, dtick=1),
        yaxis=dict(title="Master-Zielfunktion", fixedrange=True),
        showlegend=False, margin=dict(t=20, l=10, r=10, b=40),
    )
    return fig


def build_pattern_bar(instance, iteration):
    import plotly.graph_objects as go

    pattern = iteration.new_pattern
    if pattern is None:
        pattern = [0] * instance.n_types

    labels = [f"Typ {i + 1}<br>Breite {w}" for i, w in enumerate(instance.item_widths)]
    fig = go.Figure(
        go.Bar(
            x=[f"Typ {i + 1}" for i in range(instance.n_types)], y=list(pattern),
            marker_color=NEW_PATTERN_COLOR, text=list(pattern), textposition="outside",
            hovertext=labels, hoverinfo="text",
        )
    )
    fig.update_layout(
        template="plotly_white", height=260,
        xaxis=dict(title="Auftragstyp", fixedrange=True),
        yaxis=dict(title="Anzahl im Muster", fixedrange=True, dtick=1),
        margin=dict(t=20, l=10, r=10, b=40),
    )
    return fig


def build_bound_comparison_chart(comparison):
    import plotly.graph_objects as go

    labels = ["Einfache Schranke", "Gilmore-Gomory-Schranke (⌈LP⌉)", "Wahres Optimum"]
    values = [comparison["weak_bound"], comparison["ceil_lp_bound"], comparison["true_optimum"]]
    colors = ["#c4cbd8", "#137a6b", TRUE_OPTIMUM_COLOR]
    fig = go.Figure(
        go.Bar(x=labels, y=values, marker_color=colors, text=values, textposition="outside")
    )
    fig.update_layout(
        template="plotly_white", height=360,
        yaxis=dict(title="Anzahl Rollen"),
        margin=dict(t=30, l=10, r=10, b=10),
        showlegend=False,
    )
    return fig
