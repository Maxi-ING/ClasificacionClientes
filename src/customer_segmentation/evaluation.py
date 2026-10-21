"""Evaluación posterior al corte, sin atribuir efectos a campañas inexistentes."""

import pandas as pd


def evaluate_future(customers: pd.DataFrame, outcomes: pd.DataFrame) -> pd.DataFrame:
    """Evalúa solo clientes existentes; los compradores nuevos no se añaden al denominador."""
    merged = customers[["customer_id", "segment"]].merge(
        outcomes, on="customer_id", how="left", validate="one_to_one"
    )
    merged[["future_orders", "future_amount"]] = merged[["future_orders", "future_amount"]].fillna(
        0
    )
    merged["repurchased"] = merged.future_orders.gt(0)
    return (
        merged.groupby("segment")
        .agg(
            customers=("customer_id", "size"),
            repurchasers=("repurchased", "sum"),
            repurchase_rate=("repurchased", "mean"),
            future_orders=("future_orders", "sum"),
            future_gross_amount=("future_amount", "sum"),
            future_amount_per_customer=("future_amount", "mean"),
        )
        .reset_index()
    )
