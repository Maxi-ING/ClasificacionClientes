import pandas as pd
import pytest

from customer_segmentation.cleaning import clean_transactions


def test_overlap_preserves_multiplicity(transactions):
    raw = pd.concat(
        [
            transactions,
            transactions.iloc[[0]],
            transactions.assign(source_sheet="two"),
        ],
        ignore_index=True,
    )
    clean, quality = clean_transactions(raw)
    assert len(clean) == 5
    assert quality["cross_sheet_copies"] == 4
    assert quality["identical_lines_retained"] == 1


def test_missing_customers_are_not_invented(transactions):
    transactions.loc[0, "Customer ID"] = None
    clean, quality = clean_transactions(transactions)
    assert quality["missing_customer"] == 1
    assert clean.customer_id.notna().all()


def test_cancellation_is_retained_as_negative(transactions):
    clean, quality = clean_transactions(transactions)
    assert clean.loc[clean.status.eq("cancellation"), "amount"].sum() == -10
    assert quality["purchase_rows"] == 3
    assert quality["retained_rows"] + quality["excluded_rows"] == len(transactions)


def test_positive_cancellation_is_excluded(transactions):
    transactions.loc[3, "Quantity"] = 1
    clean, quality = clean_transactions(transactions)
    assert quality["inconsistent_cancellation"] == 1
    assert len(clean) == 3


def test_invalid_values_reconcile(transactions):
    transactions.loc[0, "Price"] = 0
    transactions.loc[1, "Quantity"] = 0
    clean, quality = clean_transactions(transactions)
    assert len(clean) == 2
    assert quality["invalid_price"] == quality["invalid_quantity"] == 1


def test_missing_schema_fails(transactions):
    with pytest.raises(ValueError, match="Faltan columnas"):
        clean_transactions(transactions.drop(columns="Invoice"))
