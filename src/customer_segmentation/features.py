"""Indicadores de clientes con una ventana temporal explícita."""

import pandas as pd

FEATURES = ["recency", "frequency", "monetary"]


def period(data: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Ventana [inicio, fin), común para análisis, RFM y evaluación."""
    if pd.Timestamp(start) >= pd.Timestamp(end):
        raise ValueError("El inicio debe ser anterior al fin.")
    return data.loc[data.date.ge(pd.Timestamp(start)) & data.date.lt(pd.Timestamp(end))].copy()


def build_rfm(data: pd.DataFrame, start: str, cutoff: str) -> pd.DataFrame:
    """RFM de compras positivas; cancelaciones se informan por separado.

    Monetary representa gasto bruto observado, no beneficio ni gasto neto.
    """
    observed = period(data, start, cutoff)
    purchases = observed.loc[observed.status.eq("purchase")]
    if purchases.empty:
        raise ValueError("No hay compras válidas en el periodo de observación.")
    customers = purchases.groupby("customer_id").agg(
        last_purchase=("date", "max"),
        frequency=("invoice", "nunique"),
        monetary=("amount", "sum"),
    )
    customers["recency"] = (
        pd.Timestamp(cutoff).normalize() - customers.last_purchase.dt.normalize()
    ).dt.days
    customers["average_order"] = customers.monetary / customers.frequency
    refunds = (
        observed.loc[observed.status.eq("cancellation")].groupby("customer_id").amount.sum().abs()
    )
    customers["cancelled_amount"] = refunds.reindex(customers.index, fill_value=0)
    customers["net_amount"] = customers.monetary - customers.cancelled_amount
    customers["country"] = purchases.sort_values("date").groupby("customer_id").country.last()
    return customers.reset_index()


def future_outcomes(data: pd.DataFrame, cutoff: str, end: str) -> pd.DataFrame:
    """Compras posteriores: no se usan para ajustar transformaciones ni segmentos."""
    future = period(data, cutoff, end)
    return (
        future.loc[future.status.eq("purchase")]
        .groupby("customer_id")
        .agg(future_orders=("invoice", "nunique"), future_amount=("amount", "sum"))
        .reset_index()
    )
