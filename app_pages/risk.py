import math
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_loader import load_app_data
from src.ui import (
    COLORS,
    format_amount,
    format_pct,
)


# =========================================================
# DATOS
# =========================================================

data = load_app_data()

portfolio = (
    data["risk_portfolio"]
    .copy()
)


# =========================================================
# FEATURES DE PRESENTACIÓN
# =========================================================

portfolio["risk_score_pct"] = (
    portfolio["predicted_risk"]
    * 100
)

portfolio["risk_weighted_exposure"] = (
    portfolio["predicted_risk"]
    *
    portfolio["amount"]
)


# ---------------------------------------------------------
# Prioridad relativa dentro de la cartera
# ---------------------------------------------------------

portfolio["priority_rank_pct"] = (
    portfolio[
        "risk_weighted_exposure"
    ]
    .rank(
        method="first",
        ascending=False,
        pct=True,
    )
)


def assign_priority(
    rank_pct,
):
    if rank_pct <= 0.10:
        return "Crítica"

    if rank_pct <= 0.25:
        return "Alta"

    if rank_pct <= 0.50:
        return "Media"

    return "Baja"


portfolio["priority"] = (
    portfolio[
        "priority_rank_pct"
    ]
    .map(
        assign_priority
    )
)

PRIORITY_LABELS = {
    "Crítica": "🔴 Crítica",
    "Alta": "🟠 Alta",
    "Media": "🟡 Media",
    "Baja": "🟢 Baja",
}


portfolio["priority_display"] = (
    portfolio["priority"]
    .map(PRIORITY_LABELS)
)

# =========================================================
# HEADER
# =========================================================

st.title(
    "Riesgo de cobros"
)

st.markdown(
    """
    <div class="mvp-subtitle">
        Prioriza las facturas que requieren atención
        combinando riesgo estimado y exposición monetaria.
    </div>
    """,
    unsafe_allow_html=True,
)

def reset_risk_filters():
    st.session_state["risk_customers"] = []
    st.session_state["risk_min_score"] = 0
    st.session_state["risk_min_amount"] = 0.0
    st.session_state["risk_ranking_mode"] = (
        "Mayor exposición ajustada"
    )
    st.session_state["risk_top_n"] = 25


# =========================================================
# FILTROS
# =========================================================

with st.container(
    border=True
):

    title_col, reset_col = st.columns(
        [4, 1]
    )

    with title_col:

        st.markdown(
            "#### Filtros de cartera"
        )

    with reset_col:

        st.button(
            "Restablecer filtros",
            on_click=reset_risk_filters,
            type="secondary",
        )


    filter_col1, filter_col2, filter_col3 = (
        st.columns(
            [1.2, 1, 1]
        )
    )


    with filter_col1:

        available_customers = (
            sorted(
                portfolio[
                    "customer_id"
                ]
                .astype(str)
                .unique()
            )
        )

        selected_customers = (
            st.multiselect(
                "Clientes",
                options=available_customers,
                default=[],
                placeholder="Todos los clientes",
                key="risk_customers",
            )
        )


    with filter_col2:

        min_risk = st.slider(
            "Score mínimo de riesgo",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            format="%d%%",
            key="risk_min_score",
        )


    with filter_col3:

        max_amount = float(
            portfolio[
                "amount"
            ].max()
        )

        min_amount = st.number_input(
            "Importe mínimo",
            min_value=0.0,
            max_value=max_amount,
            value=0.0,
            step=50.0,
            key="risk_min_amount",
        )


    filter_col4, filter_col5 = (
        st.columns(
            [1.4, 1]
        )
    )


    with filter_col4:

        ranking_mode = (
            st.segmented_control(
                "Criterio de priorización",
                options=[
                    "Mayor riesgo",
                    "Mayor exposición ajustada",
                    "Mayor importe",
                ],
                default=(
                    "Mayor exposición ajustada"
                ),
                key="risk_ranking_mode",
            )
        )
    
    if ranking_mode is None:
        ranking_mode = (
            "Mayor exposición ajustada"
        )


    with filter_col5:

        top_n = st.selectbox(
            "Mostrar",
            options=[
                10,
                25,
                50,
                100,
                "Todas",
            ],
            index=1,
            key="risk_top_n",
        )


# =========================================================
# APLICAR FILTROS
# =========================================================

filtered = (
    portfolio
    .copy()
)


if selected_customers:

    filtered = filtered[
        filtered[
            "customer_id"
        ]
        .astype(str)
        .isin(
            selected_customers
        )
    ]


filtered = filtered[
    filtered[
        "risk_score_pct"
    ]
    >= min_risk
]


filtered = filtered[
    filtered[
        "amount"
    ]
    >= min_amount
]

filtered_portfolio = filtered.copy()

# =========================================================
# ORDEN
# =========================================================

ranking_column_map = {
    "Mayor riesgo": (
        "predicted_risk"
    ),

    "Mayor exposición ajustada": (
        "risk_weighted_exposure"
    ),

    "Mayor importe": (
        "amount"
    ),
}

ranking_column = (
    ranking_column_map.get(
        ranking_mode,
        "risk_weighted_exposure"
    )
)


displayed_portfolio = (
    filtered_portfolio
    .sort_values(
        ranking_column,
        ascending=False,
    )
)

if top_n != "Todas":
    displayed_portfolio = (
        displayed_portfolio
        .head(
            int(top_n)
        )
    )


# =========================================================
# KPIs
# =========================================================

filtered_count = len(
    filtered_portfolio
)

filtered_amount = float(
    filtered_portfolio[
        "amount"
    ].sum()
)

filtered_mean_risk = (
    float(
        filtered_portfolio[
            "predicted_risk"
        ].mean()
    )
    if filtered_count
    else 0.0
)

high_priority_count = int(
    filtered_portfolio[
        "priority"
    ]
    .isin(
        [
            "Crítica",
            "Alta",
        ]
    )
    .sum()
)

high_priority_count = int(
    filtered[
        "priority"
    ]
    .isin(
        [
            "Crítica",
            "Alta",
        ]
    )
    .sum()
)


kpi1, kpi2, kpi3, kpi4 = (
    st.columns(4)
)


kpi1.metric(
    "Facturas visibles",
    f"{filtered_count}",
    border=True,
)


kpi2.metric(
    "Exposición",
    format_amount(
        filtered_amount
    ),
    border=True,
)


kpi3.metric(
    "Score medio",
    format_pct(
        filtered_mean_risk
    ),
    help=(
        "Score medio del modelo sobre "
        "las facturas visibles."
    ),
    border=True,
)


kpi4.metric(
    "Prioridad alta / crítica",
    f"{high_priority_count}",
    help=(
        "Prioridad relativa según "
        "riesgo × exposición."
    ),
    border=True,
)


st.divider()


# =========================================================
# VISUALIZACIONES
# =========================================================

left, right = st.columns(
    [1.4, 1]
)


# ---------------------------------------------------------
# Scatter riesgo vs importe
# ---------------------------------------------------------

with left:

    st.subheader(
        "Mapa de riesgo y exposición"
    )

    st.caption(
        "Cada punto representa una factura."
    )

    scatter_df = (
        filtered_portfolio
        .copy()
    )

    scatter_df[
        "Riesgo"
    ] = (
        scatter_df[
            "predicted_risk"
        ]
        * 100
    )

    scatter_df[
        "Importe"
    ] = (
        scatter_df[
            "amount"
        ]
    )

    scatter_chart = px.scatter(
        scatter_df,
        x="Riesgo",
        y="Importe",
        size="risk_weighted_exposure",
        color="priority",
        category_orders={
            "priority": [
                "Crítica",
                "Alta",
                "Media",
                "Baja",
            ]
        },
        color_discrete_map={
            "Crítica": COLORS["critical"],
            "Alta": COLORS["high"],
            "Media": COLORS["medium"],
            "Baja": COLORS["low"],
        },
        hover_data={
            "invoice_id": True,
            "customer_id": True,
            "Riesgo": ":.1f",
            "Importe": ":.2f",
            "risk_weighted_exposure": ":.2f",
        },
    )

    scatter_chart.update_layout(
        xaxis_title=(
            "Score de riesgo (%)"
        ),
        yaxis_title="Importe",
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),
    )

    st.plotly_chart(
        scatter_chart,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Distribución por prioridad
# ---------------------------------------------------------

with right:

    st.subheader(
        "Cartera por prioridad"
    )

    priority_summary = (
        filtered_portfolio[
            "priority"
        ]
        .value_counts()
        .reindex(
            [
                "Crítica",
                "Alta",
                "Media",
                "Baja",
            ],
            fill_value=0,
        )
        .rename_axis(
            "Prioridad"
        )
        .reset_index(
            name="Facturas"
        )
    )

    priority_chart = px.bar(
        priority_summary,
        x="Prioridad",
        y="Facturas",
        color="Prioridad",
        category_orders={
            "Prioridad": [
                "Crítica",
                "Alta",
                "Media",
                "Baja",
            ]
        },
    color_discrete_map={
        "Crítica": COLORS["critical"],
        "Alta": COLORS["high"],
        "Media": COLORS["medium"],
        "Baja": COLORS["low"],
        },
    )

    priority_chart.update_layout(
        xaxis_title="",
        yaxis_title="Facturas",
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),
        showlegend=False,
    )

    st.plotly_chart(
        priority_chart,
        use_container_width=True,
    )


# =========================================================
# TABLA OPERATIVA
# =========================================================

st.subheader(
    "Cartera priorizada"
)

st.caption(
    f"Orden actual: {ranking_mode}"
)


table_df = (
    displayed_portfolio[
        [
            "priority_display",
            "invoice_id",
            "customer_id",
            "amount",
            "risk_score_pct",
            "risk_weighted_exposure",
            "invoice_date",
            "due_date",
        ]
    ]
    .copy()
)


table_df = table_df.rename(
    columns={
        "priority_display": "Prioridad",
        "invoice_id": "Factura",
        "customer_id": "Cliente",
        "amount": "Importe",
        "risk_score_pct": "Riesgo",
        "risk_weighted_exposure":
            "Exposición ajustada",
        "invoice_date": "Emisión",
        "due_date": "Vencimiento",
    }
)


st.dataframe(
    table_df,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Prioridad": (
            st.column_config.TextColumn(
                "Prioridad",
                width="small",
            )
        ),

        "Factura": (
            st.column_config.TextColumn(
                "Factura",
                width="medium",
            )
        ),

        "Cliente": (
            st.column_config.TextColumn(
                "Cliente",
                width="small",
            )
        ),

        "Importe": (
            st.column_config.NumberColumn(
                "Importe",
                format="%.2f",
            )
        ),

        "Riesgo": (
            st.column_config.ProgressColumn(
                "Score de riesgo",
                min_value=0.0,
                max_value=100,
                format="%.0f%%",
            )
        ),

        "Exposición ajustada": (
            st.column_config.NumberColumn(
                "Exposición ajustada",
                format="%.2f",
            )
        ),

        "Emisión": (
            st.column_config.DateColumn(
                "Emisión",
                format="DD/MM/YYYY",
            )
        ),

        "Vencimiento": (
            st.column_config.DateColumn(
                "Vencimiento",
                format="DD/MM/YYYY",
            )
        ),
    },
)

# =========================================================
# EXPORTAR CARTERA
# =========================================================

export_df = (
    displayed_portfolio[
        [
            "priority_display",
            "invoice_id",
            "customer_id",
            "amount",
            "predicted_risk",
            "risk_weighted_exposure",
            "invoice_date",
            "due_date",
        ]
    ]
    .copy()
)


export_df[
    "predicted_risk"
] = (
    export_df[
        "predicted_risk"
    ]
    * 100
)


export_df = export_df.rename(
    columns={
        "priority_display": "Prioridad",
        "invoice_id": "Factura",
        "customer_id": "Cliente",
        "amount": "Importe",
        "predicted_risk": "Riesgo (%)",
        "risk_weighted_exposure":
            "Exposición ajustada",
        "invoice_date": "Emisión",
        "due_date": "Vencimiento",
    }
)


export_df[
    "Riesgo (%)"
] = (
    export_df[
        "Riesgo (%)"
    ].round(1)
)


export_df[
    "Exposición ajustada"
] = (
    export_df[
        "Exposición ajustada"
    ].round(2)
)


export_df[
    "Emisión"
] = pd.to_datetime(
    export_df[
        "Emisión"
    ]
).dt.strftime(
    "%d/%m/%Y"
)


export_df[
    "Vencimiento"
] = pd.to_datetime(
    export_df[
        "Vencimiento"
    ]
).dt.strftime(
    "%d/%m/%Y"
)

export_df[
    "Factura"
] = (
    export_df[
        "Factura"
    ]
    .astype(str)
)

export_df[
    "Cliente"
] = (
    export_df[
        "Cliente"
    ]
    .astype(str)
)



csv_data = (
    export_df
    .to_csv(
        index=False,
        sep=";",
        decimal=",",
    )
    .encode(
        "utf-8-sig"
    )
)


excel_buffer = BytesIO()

with pd.ExcelWriter(
    excel_buffer,
    engine="openpyxl",
) as writer:

    export_df.to_excel(
        writer,
        index=False,
        sheet_name="Cartera priorizada",
    )

excel_buffer.seek(0)


st.download_button(
    label="⬇ Descargar cartera priorizada",
    data=excel_buffer,
    file_name="cartera_priorizada.xlsx",
    mime=(
        "application/vnd.openxmlformats-"
        "officedocument.spreadsheetml.sheet"
    ),
)


# =========================================================
# INSIGHT COMERCIAL
# =========================================================

if len(
    displayed_portfolio
) > 0:

    top_invoice = (
        filtered
        .iloc[0]
    )

    st.info(
        "Factura más prioritaria según "
        f"**{ranking_mode}**: "
        f"`{top_invoice['invoice_id']}` · "
        f"cliente `{top_invoice['customer_id']}` · "
        f"importe **{format_amount(top_invoice['amount'])}** · "
        f"score **{format_pct(top_invoice['predicted_risk'])}**."
    )

else:

    st.warning(
        "No existen facturas que cumplan "
        "los filtros seleccionados."
    )