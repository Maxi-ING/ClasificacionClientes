"""Tablas de análisis comercial antes de aplicar machine learning."""

import pandas as pd


def sales_tables(observed: pd.DataFrame, rfm: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    purchases = observed.loc[observed.status.eq("purchase")].copy()
    purchases["month"] = purchases.date.dt.to_period("M").astype(str)
    monthly = (
        purchases.groupby("month")
        .agg(
            gross_amount=("amount", "sum"),
            orders=("invoice", "nunique"),
            customers=("customer_id", "nunique"),
        )
        .reset_index()
    )
    refunds = observed.loc[observed.status.eq("cancellation")].copy()
    refunds["month"] = refunds.date.dt.to_period("M").astype(str)
    monthly["cancelled_amount"] = monthly.month.map(
        refunds.groupby("month").amount.sum().abs()
    ).fillna(0)
    monthly["net_amount"] = monthly.gross_amount - monthly.cancelled_amount
    ranked = rfm.monetary.sort_values(ascending=False)
    top_n = max(1, int(len(rfm) * 0.1))
    return monthly, {
        "customers": len(rfm),
        "orders": int(purchases.invoice.nunique()),
        "gross_amount": float(purchases.amount.sum()),
        "cancelled_amount": float(-refunds.amount.sum()),
        "repeat_customer_share": float(rfm.frequency.gt(1).mean()),
        "top_10pct_revenue_share": float(ranked.iloc[:top_n].sum() / ranked.sum()),
        "median_recency": float(rfm.recency.median()),
        "median_frequency": float(rfm.frequency.median()),
        "median_monetary": float(rfm.monetary.median()),
    }
