from pathlib import Path
import json

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

GOLD_DIR = PROJECT_ROOT / "data" / "gold"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
METADATA_DIR = PROJECT_ROOT / "data" / "metadata"


DAILY_CASHFLOW_FILE = (
    GOLD_DIR
    / "gold_daily_cashflow.parquet"
)

RISK_TREASURY_FILE = (
    GOLD_DIR
    / "gold_risk_treasury_validation_oos.parquet"
)

STRATEGY_RESULTS_FILE = (
    PROCESSED_DIR
    / "risk_treasury_strategy_results.parquet"
)

MONTE_CARLO_FILE = (
    PROCESSED_DIR
    / "risk_treasury_monte_carlo.parquet"
)

INTEGRATION_METADATA_FILE = (
    METADATA_DIR
    / "risk_treasury_integration_metadata.json"
)

CASH_MOVEMENTS_FILE = (
    PROCESSED_DIR
    / "cash_movements.parquet"
)


@st.cache_data(
    show_spinner=False
)
def load_app_data():

    required_files = [
        DAILY_CASHFLOW_FILE,
        RISK_TREASURY_FILE,
        STRATEGY_RESULTS_FILE,
        MONTE_CARLO_FILE,
        CASH_MOVEMENTS_FILE,
        INTEGRATION_METADATA_FILE,
    ]

    missing_files = [
        path
        for path in required_files
        if not path.exists()
    ]

    if missing_files:
        missing_text = "\n".join(
            str(path)
            for path in missing_files
        )

        raise FileNotFoundError(
            "Faltan artefactos necesarios:\n"
            f"{missing_text}"
        )

    daily_cashflow = pd.read_parquet(
        DAILY_CASHFLOW_FILE
    )

    cash_movements = pd.read_parquet(
        CASH_MOVEMENTS_FILE
    )

    risk_portfolio = pd.read_parquet(
        RISK_TREASURY_FILE
    )

    strategy_results = pd.read_parquet(
        STRATEGY_RESULTS_FILE
    )

    monte_carlo = pd.read_parquet(
        MONTE_CARLO_FILE
    )

    with open(
        INTEGRATION_METADATA_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        integration_metadata = (
            json.load(
                file
            )
        )

    # -------------------------
    # Normalizar fechas
    # -------------------------

    daily_cashflow[
        "date"
    ] = pd.to_datetime(
        daily_cashflow[
            "date"
        ]
    )
    
    cash_movements[
    "date"
    ] = pd.to_datetime(
        cash_movements[
            "date"
        ]
    )

    for column in [
        "invoice_date",
        "due_date",
        "receipt_date",
    ]:
        if column in risk_portfolio.columns:

            risk_portfolio[
                column
            ] = pd.to_datetime(
                risk_portfolio[
                    column
                ]
            )

    # -------------------------
    # Score riesgo × exposición
    # -------------------------

    if (
        "risk_weighted_exposure"
        not in risk_portfolio.columns
    ):
        risk_portfolio[
            "risk_weighted_exposure"
        ] = (
            risk_portfolio[
                "predicted_risk"
            ]
            *
            risk_portfolio[
                "amount"
            ]
        )

    return {
        "daily_cashflow": (
            daily_cashflow
        ),
        
        "cash_movements": (
            cash_movements
        ),

        "risk_portfolio": (
            risk_portfolio
        ),

        "strategy_results": (
            strategy_results
        ),

        "monte_carlo": (
            monte_carlo
        ),

        "integration_metadata": (
            integration_metadata
        ),
    }