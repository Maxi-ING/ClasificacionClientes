"""Perfiles de segmentos en días, pedidos y libras esterlinas."""

import pandas as pd


def profile_segments(customers: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Ordena códigos por gasto mediano para facilitar la lectura del informe."""
    data = customers.copy()
    order = data.groupby("cluster").monetary.median().sort_values().index
    codes = {label: f"S{i + 1:02d}" for i, label in enumerate(order)}
    data["segment"] = data.cluster.map(codes)
    profiles = (
        data.groupby("segment")
        .agg(
            customers=("customer_id", "size"),
            recency_median=("recency", "median"),
            frequency_median=("frequency", "median"),
            monetary_median=("monetary", "median"),
            gross_amount=("monetary", "sum"),
            cancelled_amount=("cancelled_amount", "sum"),
        )
        .reset_index()
    )
    profiles["customer_share"] = profiles.customers / len(data)
    profiles["revenue_share"] = profiles.gross_amount / data.monetary.sum()
    profiles["net_amount"] = profiles.gross_amount - profiles.cancelled_amount
    recency_median = data.recency.median()
    spending_upper = data.monetary.quantile(0.75)
    names, actions = [], []
    for row in profiles.itertuples():
        if row.frequency_median <= 1:
            name = (
                "Compra única reciente"
                if row.recency_median <= recency_median
                else "Compra única distante"
            )
            action = "Probar un incentivo de segunda compra y medir conversión incremental."
        elif row.monetary_median >= spending_upper:
            name = "Recurrentes de alto gasto"
            action = "Probar beneficios de fidelización y medir recompra y margen."
        elif row.recency_median > recency_median:
            name = "Recurrentes distantes"
            action = "Probar una campaña de reactivación frente a un grupo de control."
        else:
            name = "Recurrentes recientes"
            action = "Probar recomendaciones de productos y medir segunda conversión."
        names.append(name)
        actions.append(action)
    profiles["name"] = names
    profiles["proposed_action"] = actions
    data = data.merge(profiles[["segment", "name"]], on="segment", validate="many_to_one")
    return data, profiles
