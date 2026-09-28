import streamlit as st

COLORS = {
    # Producto
    "primary": "#2563EB",
    "secondary": "#64748B",

    # Finanzas
    "cash_in": "#16A34A",
    "cash_out": "#DC2626",

    # Escenarios
    "base": "#2563EB",
    "scenario": "#F97316",
    "stress": "#DC2626",

    # Riesgo
    "critical": "#DC2626",
    "high": "#F97316",
    "medium": "#EAB308",
    "low": "#16A34A",

    # Neutros
    "grey": "#94A3B8",
}

def format_amount(
    value,
    decimals=2,
):
    value = float(value)

    formatted = (
        f"{value:,.{decimals}f}"
    )

    return (
        formatted
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def format_pct(
    value,
    decimals=1,
):
    return (
        f"{float(value) * 100:.{decimals}f}%"
        .replace(".", ",")
    )


def inject_global_css():

    st.markdown(
        """
        <style>

        /* =========================================
            LAYOUT GENERAL
        ========================================= */

        .block-container {
            max-width: 1450px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }


        /* =========================================
            TÍTULOS
        ========================================= */

        h1 {
            letter-spacing: -0.035em;
            font-weight: 750;
            margin-bottom: 0.25rem;
        }

        h2 {
            letter-spacing: -0.025em;
            font-weight: 700;
            margin-top: 1.5rem;
        }

        h3 {
            letter-spacing: -0.015em;
            font-weight: 650;
        }


        /* =========================================
            SUBTÍTULO DE PÁGINA
        ========================================= */

        .mvp-subtitle {
            font-size: 1.05rem;
            color: #64748B;
            margin-top: -0.3rem;
            margin-bottom: 1.75rem;
            line-height: 1.6;
        }


        /* =========================================
            KPI CARDS
        ========================================= */

        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 1.15rem 1.25rem;
            min-height: 108px;

            box-shadow:
                0 1px 2px rgba(15, 23, 42, 0.04),
                0 2px 6px rgba(15, 23, 42, 0.03);

            transition:
                border-color 0.2s ease,
                box-shadow 0.2s ease,
                transform 0.2s ease;
        }


        div[data-testid="stMetric"]:hover {
            border-color: #CBD5E1;

            box-shadow:
                0 2px 4px rgba(15, 23, 42, 0.05),
                0 6px 14px rgba(15, 23, 42, 0.05);

            transform: translateY(-1px);
        }


        /* Título KPI */

        div[data-testid="stMetricLabel"] {
            font-size: 0.82rem;
            font-weight: 600;
            color: #64748B;
        }


        div[data-testid="stMetricLabel"] p {
            font-size: 0.82rem;
            font-weight: 600;
            color: #64748B;
        }


        /* Valor KPI */

        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 750;
            letter-spacing: -0.025em;
            color: #0F172A;
            white-space: nowrap;
            overflow: visible;
        }


        /* Delta KPI */

        div[data-testid="stMetricDelta"] {
            font-size: 0.78rem;
            font-weight: 500;
        }


        /* =========================================
            SIDEBAR
        ========================================= */

        section[data-testid="stSidebar"] {
            background-color: #F8FAFC;
            border-right: 1px solid #E2E8F0;
        }


        section[data-testid="stSidebar"] > div {
            padding-top: 1rem;
        }


        /* Título producto */

        section[data-testid="stSidebar"] h2 {
            font-size: 1.25rem;
            font-weight: 750;
            letter-spacing: -0.025em;
            color: #0F172A;
            margin-bottom: 0.3rem;
        }


        /* Texto secundario sidebar */

        section[data-testid="stSidebar"] small {
            color: #64748B;
            line-height: 1.5;
        }


        /* Separadores */

        section[data-testid="stSidebar"] hr {
            border-color: #E2E8F0;
            margin-top: 1.25rem;
            margin-bottom: 1.25rem;
        }


        /* Elementos navegación */

        section[data-testid="stSidebar"] button {
            border-radius: 9px;
            transition: background-color 0.15s ease;
        }


        section[data-testid="stSidebar"] button:hover {
            background-color: #E2E8F0;
        }


        /* =========================================
            SEPARADORES DE CONTENIDO
        ========================================= */

        hr {
            border-color: #E2E8F0;
        }


        /* =========================================
            NOTAS
        ========================================= */

        .section-note {
            color: #64748B;
            font-size: 0.88rem;
            line-height: 1.5;
        }


        /* =========================================
            DATAFRAMES
        ========================================= */

        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
        }


        /* =========================================
            GRÁFICOS
        ========================================= */

        div[data-testid="stPlotlyChart"] {
            border-radius: 12px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )