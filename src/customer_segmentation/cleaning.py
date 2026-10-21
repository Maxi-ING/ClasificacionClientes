"""Normalización y trazabilidad de cada línea de compra."""

from pathlib import Path

import pandas as pd

COLUMNS = {
    "Invoice": "invoice",
    "StockCode": "product",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "date",
    "Price": "price",
    "Customer ID": "customer_id",
    "Country": "country",
}
KEYS = list(COLUMNS.values())


def read_transactions(path: Path) -> pd.DataFrame:
    """Lee ambas hojas. La caché acelera ejecuciones sin alterar el original."""
    cache = path.with_suffix(".parquet")
    if cache.exists() and cache.stat().st_mtime >= path.stat().st_mtime:
        return pd.read_parquet(cache)
    sheets = pd.read_excel(path, sheet_name=None)
    frame = pd.concat(
        [sheet.assign(source_sheet=name) for name, sheet in sheets.items()], ignore_index=True
    )
    for column in ["Invoice", "StockCode", "Description", "Country"]:
        frame[column] = frame[column].astype("string")
    temporary = cache.with_suffix(".tmp")
    frame.to_parquet(temporary, index=False)
    temporary.replace(cache)
    return frame


def clean_transactions(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Conserva repetidos dentro de una hoja; elimina copias entre hojas por multiplicidad.

    Las exclusiones son secuenciales y mutuamente excluyentes para reconciliar el total.
    Las cancelaciones se conservan aparte con su importe firmado.
    """
    required = set(COLUMNS) | {"source_sheet"}
    if missing := required - set(raw.columns):
        raise ValueError(f"Faltan columnas: {sorted(missing)}")
    data = raw.rename(columns=COLUMNS).copy()
    for column in ["invoice", "product", "description", "country"]:
        data[column] = data[column].astype("string").str.strip()
    data["customer_id"] = pd.to_numeric(data.customer_id, errors="coerce").astype("Int64")
    data["date"] = pd.to_datetime(data.date, errors="coerce")
    for column in ["quantity", "price"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    report = {"raw_rows": len(data), "sheets": data.source_sheet.value_counts().to_dict()}
    # El número de ocurrencia conserva líneas idénticas legítimas en la misma hoja.
    data["occurrence"] = data.groupby(KEYS + ["source_sheet"], dropna=False).cumcount()
    duplicate = data.duplicated(KEYS + ["occurrence"])
    report["cross_sheet_copies"] = int(duplicate.sum())
    data = data.loc[~duplicate].drop(columns="occurrence").copy()
    report["identical_lines_retained"] = int(data.duplicated(KEYS).sum())
    reasons = {
        "missing_customer": lambda d: d.customer_id.isna(),
        "invalid_date": lambda d: d.date.isna(),
        "invalid_invoice": lambda d: d.invoice.isna() | d.invoice.eq(""),
        "invalid_quantity": lambda d: d.quantity.isna() | d.quantity.eq(0),
        "invalid_price": lambda d: d.price.isna() | d.price.le(0),
    }
    for reason, condition in reasons.items():
        excluded = condition(data)
        report[reason] = int(excluded.sum())
        data = data.loc[~excluded].copy()
    cancellation = data.invoice.str.upper().str.startswith("C") | data.quantity.lt(0)
    data["status"] = "purchase"
    data.loc[cancellation, "status"] = "cancellation"
    data["amount"] = data.quantity * data.price
    # Códigos C con cantidad positiva son inconsistentes; no se inventa un reembolso.
    inconsistent = cancellation & data.quantity.gt(0)
    report["inconsistent_cancellation"] = int(inconsistent.sum())
    data = data.loc[~inconsistent].copy()
    data["customer_id"] = data.customer_id.astype("int64").astype(str)
    report["retained_rows"] = len(data)
    report["purchase_rows"] = int(data.status.eq("purchase").sum())
    report["cancellation_rows"] = int(data.status.eq("cancellation").sum())
    report["excluded_rows"] = report["raw_rows"] - report["retained_rows"]
    report["date_min"] = str(data.date.min())
    report["date_max"] = str(data.date.max())
    report["customers"] = data.customer_id.nunique()
    return data.reset_index(drop=True), report
