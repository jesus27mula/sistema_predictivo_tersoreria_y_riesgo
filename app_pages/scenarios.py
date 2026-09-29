import plotly.graph_objects as go
import streamlit as st

from src.data_loader import load_app_data

from src.scenarios import (
    apply_delay_to_selected_receipts,
    build_daily_cashflow,
    calculate_scenario_metrics,
    select_portfolio,
)

from src.ui import (
    COLORS,
    format_amount,
    format_pct,
)


# =========================================================
# DATA
# =========================================================

data = load_app_data()

cash_movements = (
    data["cash_movements"]
    .copy()
)

portfolio = (
    data["risk_portfolio"]
    .copy()
)

daily_reference = (
    data["daily_cashflow"]
    .copy()
)


# =========================================================
# HEADER
# =========================================================

st.title(
    "Simulador de escenarios"
)

st.markdown(
    """
    <div class="mvp-subtitle">
        Simula cómo un deterioro en los cobros
        puede afectar a la liquidez disponible.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# REFERENCIAS DEL ESCENARIO BASE
# =========================================================

simulation_start = (
    daily_reference[
        "date"
    ].min()
)

simulation_end = (
    daily_reference[
        "date"
    ].max()
)

base_initial_cash = float(
    daily_reference[
        "opening_cash_balance"
    ].iloc[0]
)


SCENARIO_PRESETS = {

    "moderado": {
        "strategy": (
            "Mayor exposición ajustada"
        ),
        "portfolio_pct": 15,
        "delay_days": 5,
        "cash_multiplier": 1.0,
    },

    "adverso": {
        "strategy": (
            "Mayor exposición ajustada"
        ),
        "portfolio_pct": 25,
        "delay_days": 10,
        "cash_multiplier": 0.75,
    },

    "severo": {
        "strategy": (
            "Mayor exposición ajustada"
        ),
        "portfolio_pct": 50,
        "delay_days": 20,
        "cash_multiplier": 0.50,
    },
}


def apply_scenario_preset(
    preset_name,
):

    preset = (
        SCENARIO_PRESETS[
            preset_name
        ]
    )

    st.session_state[
        "scenario_strategy"
    ] = preset[
        "strategy"
    ]

    st.session_state[
        "scenario_portfolio_pct"
    ] = preset[
        "portfolio_pct"
    ]

    st.session_state[
        "scenario_delay_days"
    ] = preset[
        "delay_days"
    ]

    st.session_state[
        "scenario_cash_multiplier"
    ] = preset[
        "cash_multiplier"
    ]

# =========================================================
# CONTROLES
# =========================================================

with st.container(
    border=True
):

    st.markdown(
        "#### Escenarios rápidos"
    )

    preset1, preset2, preset3 = (
        st.columns(3)
    )


    with preset1:

        st.button(
            "🟢 Moderado",
            on_click=(
                apply_scenario_preset
            ),
            args=("moderado",),
        )


    with preset2:

        st.button(
            "🟠 Adverso",
            on_click=(
                apply_scenario_preset
            ),
            args=("adverso",),
        )


    with preset3:

        st.button(
            "🔴 Severo",
            on_click=(
                apply_scenario_preset
            ),
            args=("severo",),
        )


    st.divider()

    st.markdown(
        "#### Configuración del escenario"
    )


    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        strategy = st.selectbox(
            "Criterio de selección",
            options=[
                "Mayor exposición ajustada",
                "Mayor riesgo",
                "Mayor importe",
                "Aleatorio",
            ],
            index=0,
            key="scenario_strategy",
            help=(
                "Determina qué facturas "
                "serán sometidas al shock."
            ),
        )


    with col2:

        portfolio_pct = st.slider(
            "Facturas afectadas",
            min_value=5,
            max_value=100,
            value=25,
            step=5,
            format="%d%%",
            key="scenario_portfolio_pct",
        )


    with col3:

        delay_days = st.slider(
            "Retraso adicional",
            min_value=0,
            max_value=30,
            value=10,
            step=1,
            format="%d días",
            key="scenario_delay_days",
        )


    st.markdown(
        "##### Colchón inicial"
    )


    cash_multiplier = st.slider(
        "Saldo inicial respecto al escenario base",
        min_value=0.0,
        max_value=2.0,
        value=1.0,
        step=0.05,
        key="scenario_cash_multiplier",
        help=(
            "1,0 = saldo inicial utilizado "
            "en la simulación base."
        ),
    )


scenario_initial_cash = (
    base_initial_cash
    *
    cash_multiplier
)


# =========================================================
# SELECCIÓN
# =========================================================

strategy_internal_map = {

    "Mayor exposición ajustada":
        "Riesgo × importe",

    "Mayor riesgo":
        "Mayor riesgo",

    "Mayor importe":
        "Mayor importe",

    "Aleatorio":
        "Aleatorio",
}


strategy_internal = (
    strategy_internal_map[
        strategy
    ]
)

selected = select_portfolio(
    portfolio=portfolio,
    strategy=strategy_internal,
    share=(
        portfolio_pct
        / 100
    ),
    random_seed=42,
)

selected_ids = set(
    selected[
        "movement_id"
    ]
)

selected_amount = float(
    selected[
        "amount"
    ].sum()
)

selected_mean_risk = float(
    selected[
        "predicted_risk"
    ].mean()
)


# =========================================================
# CONSTRUIR BASE
# =========================================================

base_daily = build_daily_cashflow(
    movements=cash_movements,
    initial_cash=scenario_initial_cash,
    start_date=simulation_start,
    end_date=simulation_end,
)


# =========================================================
# CONSTRUIR ESCENARIO
# =========================================================

scenario_movements = (
    apply_delay_to_selected_receipts(
        cash_movements=(
            cash_movements
        ),
        selected_ids=selected_ids,
        delay_days=delay_days,
    )
)

scenario_daily = (
    build_daily_cashflow(
        movements=scenario_movements,
        initial_cash=(
            scenario_initial_cash
        ),
        start_date=simulation_start,
        end_date=simulation_end,
    )
)


metrics = (
    calculate_scenario_metrics(
        base_daily=base_daily,
        scenario_daily=scenario_daily,
    )
)


base_minimum = float(
    base_daily[
        "closing_cash_balance"
    ].min()
)

base_final = float(
    base_daily[
        "closing_cash_balance"
    ].iloc[-1]
)


if scenario_initial_cash > 0:

    deterioration_pct = (
        metrics[
            "maximum_deterioration"
        ]
        /
        scenario_initial_cash
    )

else:

    deterioration_pct = None

# =========================================================
# SUMMARY DEL ESCENARIO
# =========================================================

st.markdown(
    "### Resultado del escenario"
)


kpi1, kpi2, kpi3, kpi4 = (
    st.columns(4)
)


kpi1.metric(
    "Facturas afectadas",
    len(
        selected
    ),
    delta=(
        f"{portfolio_pct}% "
        "de la cartera"
    ),
    delta_color="off",
    border=True,
)


kpi2.metric(
    "Exposición afectada",
    format_amount(
        selected_amount
    ),
    help=(
        "Importe total de los "
        "cobros seleccionados."
    ),
    border=True,
)


kpi3.metric(
    "Score medio",
    format_pct(
        selected_mean_risk
    ),
    border=True,
)


kpi4.metric(
    "Retraso aplicado",
    f"+{delay_days} días",
    border=True,
)


# =========================================================
# IMPACTO FINANCIERO
# =========================================================

metric1, metric2, metric3, metric4 = (
    st.columns(4)
)


minimum_delta = (
    metrics[
        "minimum_balance"
    ]
    -
    base_minimum
)


metric1.metric(
    "Liquidez mínima",
    format_amount(
        metrics[
            "minimum_balance"
        ]
    ),
    help=(
        "Saldo de caja mínimo alcanzado "
        "durante el escenario simulado."
    ),
    border=True,
)


metric2.metric(
    "Deterioro máximo",
    format_amount(
        metrics[
            "maximum_deterioration"
        ]
    ),
    delta=(
        (
            f"{format_pct(deterioration_pct)} "
            "del saldo inicial"
        )
        if deterioration_pct
        is not None
        else
        "Sin saldo inicial de referencia"
    ),
    delta_color="off",
    help=(
        "Mayor reducción diaria de caja "
        "respecto al escenario base."
    ),
    border=True,
)


metric3.metric(
    "Días con caja negativa",
    metrics[
        "negative_days"
    ],
    border=True,
)


metric4.metric(
    "Necesidad de financiación",
    format_amount(
        metrics[
            "funding_gap"
        ]
    ),
    help=(
        "Financiación adicional necesaria "
        "para evitar saldo negativo."
    ),
    border=True,
)


# =========================================================
# GRÁFICO BASE VS ESCENARIO
# =========================================================

st.subheader(
    "BASE vs escenario simulado"
)


chart = go.Figure()


chart.add_trace(
    go.Scatter(
        x=base_daily["date"],
        y=base_daily["closing_cash_balance"],
        mode="lines",
        name="BASE",
        line=dict(
            color=COLORS["base"],
            width=3,
        ),
    )
)


chart.add_trace(
    go.Scatter(
        x=scenario_daily["date"],
        y=scenario_daily["closing_cash_balance"],
        mode="lines",
        name="ESCENARIO",
        line=dict(
            color=COLORS["scenario"],
            width=3,
        ),
    )
)


chart.add_hline(
    y=0,
    line_dash="dash",
)


chart.update_layout(
    xaxis_title="",
    yaxis_title="Saldo de caja",
    hovermode="x unified",
    margin=dict(
        l=10,
        r=10,
        t=20,
        b=10,
    ),
)


st.plotly_chart(
    chart,
    width="stretch",
)


# =========================================================
# DETERIORO DE LIQUIDEZ
# =========================================================

st.subheader(
    "Deterioro diario de liquidez"
)


deterioration = (
    base_daily[
        "closing_cash_balance"
    ]
    -
    scenario_daily[
        "closing_cash_balance"
    ]
)


deterioration_chart = go.Figure()


deterioration_chart.add_trace(
    go.Scatter(
        x=base_daily["date"],
        y=deterioration,
        mode="lines",
        fill="tozeroy",
        name="Liquidez no disponible",
        line=dict(
            color=COLORS["stress"],
            width=2,
        ),
    )
)


deterioration_chart.update_layout(
    xaxis_title="",
    yaxis_title=(
        "Reducción de liquidez"
    ),
    margin=dict(
        l=10,
        r=10,
        t=20,
        b=10,
    ),
)


st.plotly_chart(
    deterioration_chart,
    width="stretch",
)


# =========================================================
# CARTERA AFECTADA
# =========================================================

st.subheader(
    "Facturas afectadas"
)

st.caption(
    f"Criterio: {strategy} · "
    f"{portfolio_pct}% de la cartera · "
    f"+{delay_days} días."
)


selected_table = (
    selected[
        [
            "invoice_id",
            "customer_id",
            "amount",
            "predicted_risk",
            "due_date",
            "receipt_date",
        ]
    ]
    .copy()
    .rename(
        columns={
            "invoice_id": "Factura",
            "customer_id": "Cliente",
            "amount": "Importe",
            "predicted_risk": "Riesgo",
            "due_date": "Vencimiento",
            "receipt_date": "Cobro histórico base",
        }
    )
)


st.dataframe(
    selected_table,
    hide_index=True,
    width="stretch",
    column_config={
        "Importe": (
            st.column_config.NumberColumn(
                "Importe",
                format="%.2f",
            )
        ),

        "Riesgo": (
            st.column_config.ProgressColumn(
                "Score",
                min_value=0.0,
                max_value=1.0,
                format="%.2f",
            )
        ),

        "Vencimiento": (
            st.column_config.DateColumn(
                "Vencimiento",
                format="DD/MM/YYYY",
            )
        ),

        "Cobro histórico base": (
            st.column_config.DateColumn(
                "Cobro histórico base",
                format="DD/MM/YYYY",
            )
        ),
    },
)


# =========================================================
# RESUMEN EJECUTIVO
# =========================================================

st.subheader(
    "Lectura ejecutiva"
)


if delay_days == 0:

    st.success(
        "No se ha aplicado ningún retraso "
        "adicional. El escenario coincide "
        "con la situación base."
    )


elif (
    metrics[
        "negative_days"
    ] > 0
):

    st.error(
        f"El escenario afecta a "
        f"**{len(selected)} facturas**, "
        f"con una exposición de "
        f"**{format_amount(selected_amount)}**, "
        f"y retrasa sus cobros "
        f"**{delay_days} días**. "
        f"La liquidez se reduce como máximo "
        f"en **{format_amount(metrics['maximum_deterioration'])}**. "
        f"Esto provoca "
        f"**{metrics['negative_days']} días con caja negativa** "
        f"y una necesidad máxima de financiación de "
        f"**{format_amount(metrics['funding_gap'])}**."
    )


elif (
    metrics[
        "maximum_deterioration"
    ] > 0
):

    st.warning(
        f"El escenario afecta a "
        f"**{len(selected)} facturas**, "
        f"con una exposición de "
        f"**{format_amount(selected_amount)}**, "
        f"y retrasa sus cobros "
        f"**{delay_days} días**. "
        f"La liquidez se reduce como máximo "
        f"en **{format_amount(metrics['maximum_deterioration'])}**, "
        f"pero la empresa mantiene "
        f"**saldo de caja positivo durante todo el periodo**."
    )


else:

    st.success(
        "Con los parámetros seleccionados "
        "no se observa un deterioro de liquidez "
        "respecto al escenario base."
    )