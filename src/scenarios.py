import math

import numpy as np
import pandas as pd


# =========================================================
# CASHFLOW
# =========================================================

def build_daily_cashflow(
    movements,
    initial_cash,
    start_date,
    end_date,
):
    movements = movements.copy()

    movements["date"] = pd.to_datetime(
        movements["date"]
    ).dt.normalize()

    calendar = pd.DataFrame({
        "date": pd.date_range(
            start=start_date,
            end=end_date,
            freq="D",
        )
    })

    daily_in = (
        movements.loc[
            movements["direction"].eq(
                "CASH_IN"
            )
        ]
        .groupby("date")["amount"]
        .sum()
    )

    daily_out = (
        movements.loc[
            movements["direction"].eq(
                "CASH_OUT"
            )
        ]
        .groupby("date")["amount"]
        .sum()
    )

    calendar["cash_in"] = (
        calendar["date"]
        .map(daily_in)
        .fillna(0.0)
    )

    calendar["cash_out"] = (
        calendar["date"]
        .map(daily_out)
        .fillna(0.0)
    )

    calendar["net_cashflow"] = (
        calendar["cash_in"]
        -
        calendar["cash_out"]
    )

    calendar[
        "cumulative_net_cashflow"
    ] = (
        calendar[
            "net_cashflow"
        ].cumsum()
    )

    calendar[
        "closing_cash_balance"
    ] = (
        float(initial_cash)
        +
        calendar[
            "cumulative_net_cashflow"
        ]
    )

    return calendar


# =========================================================
# SELECCIÓN DE FACTURAS
# =========================================================

def select_portfolio(
    portfolio,
    strategy,
    share,
    random_seed=42,
):
    data = portfolio.copy()

    selection_count = max(
        1,
        int(
            math.ceil(
                len(data)
                * share
            )
        ),
    )

    if strategy == "Mayor riesgo":

        selected = (
            data
            .sort_values(
                [
                    "predicted_risk",
                    "movement_id",
                ],
                ascending=[
                    False,
                    True,
                ],
            )
            .head(selection_count)
        )

    elif strategy == "Riesgo × importe":

        if (
            "risk_weighted_exposure"
            not in data.columns
        ):
            data[
                "risk_weighted_exposure"
            ] = (
                data["predicted_risk"]
                *
                data["amount"]
            )

        selected = (
            data
            .sort_values(
                [
                    "risk_weighted_exposure",
                    "movement_id",
                ],
                ascending=[
                    False,
                    True,
                ],
            )
            .head(selection_count)
        )

    elif strategy == "Mayor importe":

        selected = (
            data
            .sort_values(
                [
                    "amount",
                    "movement_id",
                ],
                ascending=[
                    False,
                    True,
                ],
            )
            .head(selection_count)
        )

    elif strategy == "Aleatorio":

        rng = np.random.default_rng(
            random_seed
        )

        selected_ids = rng.choice(
            data["movement_id"].to_numpy(),
            size=selection_count,
            replace=False,
        )

        selected = data[
            data["movement_id"].isin(
                selected_ids
            )
        ]

    else:
        raise ValueError(
            f"Estrategia desconocida: {strategy}"
        )

    return selected.copy()


# =========================================================
# APLICAR RETRASO
# =========================================================

def apply_delay_to_selected_receipts(
    cash_movements,
    selected_ids,
    delay_days,
):
    scenario = cash_movements.copy()

    selected_mask = (
        scenario["movement_id"]
        .isin(selected_ids)
    )

    scenario.loc[
        selected_mask,
        "date"
    ] = (
        pd.to_datetime(
            scenario.loc[
                selected_mask,
                "date"
            ]
        )
        +
        pd.to_timedelta(
            int(delay_days),
            unit="D",
        )
    )

    return scenario


# =========================================================
# MÉTRICAS
# =========================================================

def calculate_scenario_metrics(
    base_daily,
    scenario_daily,
):
    base_balance = (
        base_daily[
            "closing_cash_balance"
        ]
        .to_numpy()
    )

    scenario_balance = (
        scenario_daily[
            "closing_cash_balance"
        ]
        .to_numpy()
    )

    deterioration = (
        base_balance
        -
        scenario_balance
    )

    minimum_balance = float(
        scenario_balance.min()
    )

    minimum_position = int(
        np.argmin(
            scenario_balance
        )
    )

    negative_days = int(
        (
            scenario_balance < 0
        ).sum()
    )

    return {
        "minimum_balance": (
            minimum_balance
        ),

        "minimum_balance_date": (
            scenario_daily.iloc[
                minimum_position
            ]["date"]
        ),

        "maximum_deterioration": float(
            deterioration.max()
        ),

        "average_deterioration": float(
            deterioration.mean()
        ),

        "negative_days": (
            negative_days
        ),

        "funding_gap": max(
            0.0,
            -minimum_balance,
        ),

        "final_balance": float(
            scenario_balance[-1]
        ),
    }