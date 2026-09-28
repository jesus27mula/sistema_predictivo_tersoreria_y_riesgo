import math

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import (
    load_app_data,
)

from src.ui import (
    COLORS,
    format_amount,
    format_pct,
)

# =====================================
# DATOS
# =====================================

data = load_app_data()

daily = (
    data[
        "daily_cashflow"
    ]
    .copy()
)

portfolio = (
    data[
        "risk_portfolio"
    ]
    .copy()
)

strategy_results = (
    data[
        "strategy_results"
    ]
    .copy()
)

metadata = (
    data[
        "integration_metadata"
    ]
)


# =====================================
# HEADER
# =====================================

st.title(
    "Treasury Risk AI"
)

st.markdown(
    """
    <div class="mvp-subtitle">
        Anticipa qué cobros requieren atención
        y cómo pueden afectar a la liquidez.
    </div>
    """,
    unsafe_allow_html=True,
)


# =====================================
# KPIs
# =====================================

final_balance = float(
    daily[
        "closing_cash_balance"
    ].iloc[-1]
)

minimum_balance_idx = (
    daily[
        "closing_cash_balance"
    ].idxmin()
)

minimum_balance = float(
    daily.loc[
        minimum_balance_idx,
        "closing_cash_balance"
    ]
)

minimum_balance_date = (
    daily.loc[
        minimum_balance_idx,
        "date"
    ]
)

total_cash_in = float(
    daily[
        "cash_in"
    ].sum()
)

total_cash_out = float(
    daily[
        "cash_out"
    ].sum()
)

net_cashflow = float(
    daily[
        "net_cashflow"
    ].sum()
)

invoice_count = len(
    portfolio
)


priority_count = int(
    math.ceil(
        invoice_count
        * 0.25
    )
)

priority_portfolio = (
    portfolio
    .sort_values(
        "risk_weighted_exposure",
        ascending=False,
    )
    .head(
        priority_count
    )
)

priority_exposure = float(
    priority_portfolio[
        "amount"
    ].sum()
)


kpi1, kpi2, kpi3, kpi4 = (
    st.columns(4)
)

kpi1.metric(
    "Liquidez final",
    format_amount(
        final_balance
    ),
    border=True,
)

kpi2.metric(
    "Liquidez mínima",
    format_amount(
        minimum_balance
    ),
    help=(
        "Mínimo histórico de caja "
        f"({minimum_balance_date:%d/%m/%Y})"
    ),
    border=True,
)

kpi3.metric(
    "Cartera analizada",
    f"{invoice_count:,}".replace(
        ",",
        "."
    ),
    border=True,
)

kpi4.metric(
    "Exposición prioritaria",
    format_amount(
        priority_exposure
    ),
    help=(
        "Importe de las facturas "
        "Top 25 % por riesgo × exposición."
    ),
    border=True,
)


kpi5, kpi6, kpi7, kpi8 = (
    st.columns(4)
)

kpi5.metric(
    "Cobros acumulados",
    format_amount(
        total_cash_in
    ),
    border=True,
)

kpi6.metric(
    "Pagos acumulados",
    format_amount(
        total_cash_out
    ),
    border=True,
)

kpi7.metric(
    "Generación neta de caja",
    format_amount(
        net_cashflow
    ),
    border=True,
)

kpi8.metric(
    "Facturas prioritarias",
    f"{priority_count}",
    help=(
        "Facturas situadas en el Top 25 % "
        "según riesgo × exposición."
    ),
    border=True,
)


st.divider()


# =====================================
# TESORERÍA
# =====================================

st.subheader(
    "Evolución de la tesorería"
)

st.caption(
    "Saldo diario del escenario base."
)

balance_chart = px.line(
    daily,
    x="date",
    y="closing_cash_balance",
)

balance_chart.update_traces(
    line_color=COLORS["primary"],
    line_width=3,
)

balance_chart.update_layout(
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

balance_chart.add_hline(
    y=0,
    line_dash="dash",
)

st.plotly_chart(
    balance_chart,
    use_container_width=True,
)


# =====================================
# COBROS VS PAGOS
# =====================================

left, right = st.columns(
    [1.5, 1]
)


with left:

    st.subheader(
        "Cobros vs pagos"
    )

    monthly = (
        daily
        .set_index(
            "date"
        )[
            [
                "cash_in",
                "cash_out",
            ]
        ]
        .resample(
            "MS"
        )
        .sum()
        .reset_index()
    )

    monthly_long = (
        monthly
        .melt(
            id_vars="date",
            value_vars=[
                "cash_in",
                "cash_out",
            ],
            var_name="Tipo",
            value_name="Importe",
        )
    )

    monthly_long[
        "Tipo"
    ] = (
        monthly_long[
            "Tipo"
        ]
        .replace({
            "cash_in": "Cobros",
            "cash_out": "Pagos",
        })
    )

    movement_chart = px.bar(
        monthly_long,
        x="date",
        y="Importe",
        color="Tipo",
        barmode="group",
        color_discrete_map={
            "Cobros": COLORS["cash_in"],
            "Pagos": COLORS["cash_out"],
        },
    )

    movement_chart.update_layout(
        xaxis_title="",
        yaxis_title="Importe",
        legend_title="",
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),
    )

    st.plotly_chart(
        movement_chart,
        use_container_width=True,
    )


with right:

    st.subheader(
        "Distribución del riesgo"
    )

    risk_chart = px.histogram(
        portfolio,
        x="predicted_risk",
        nbins=20,
    )

    risk_chart.update_layout(
        xaxis_title="Riesgo estimado",
        yaxis_title="Facturas",
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),
    )

    risk_chart.update_xaxes(
        tickformat=".0%"
    )

    st.plotly_chart(
        risk_chart,
        use_container_width=True,
    )


# =====================================
# PRIORIDADES
# =====================================

st.subheader(
    "Cobros prioritarios"
)

st.caption(
    "Top 10 según riesgo estimado × importe."
)


top_priority = (
    portfolio
    .sort_values(
        "risk_weighted_exposure",
        ascending=False,
    )
    .head(10)
    .copy()
)


priority_table = (
    top_priority[
        [
            "invoice_id",
            "customer_id",
            "amount",
            "predicted_risk",
            "due_date",
            "risk_weighted_exposure",
        ]
    ]
    .rename(
        columns={
            "invoice_id": "Factura",
            "customer_id": "Cliente",
            "amount": "Importe",
            "predicted_risk": "Riesgo",
            "due_date": "Vencimiento",
            "risk_weighted_exposure":
                "Exposición ajustada",
        }
    )
)


priority_table[
    "Importe"
] = (
    priority_table[
        "Importe"
    ]
    .map(
        format_amount
    )
)

priority_table[
    "Riesgo"
] = (
    priority_table[
        "Riesgo"
    ]
    .map(
        lambda value:
        format_pct(
            value
        )
    )
)

priority_table[
    "Exposición ajustada"
] = (
    priority_table[
        "Exposición ajustada"
    ]
    .map(
        format_amount
    )
)

priority_table[
    "Vencimiento"
] = pd.to_datetime(
    priority_table[
        "Vencimiento"
    ]
).dt.strftime(
    "%d/%m/%Y"
)


st.dataframe(
    priority_table,
    hide_index=True,
    use_container_width=True,
)


st.info(
    "Estas facturas combinan una probabilidad "
    "elevada de retraso con una exposición "
    "monetaria relevante."
)