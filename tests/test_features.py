import pandas as pd
import pytest

from customer_segmentation.cleaning import clean_transactions
from customer_segmentation.evaluation import evaluate_future
from customer_segmentation.features import build_rfm, future_outcomes


def test_rfm_counts_orders_not_lines(transactions):
    clean, _ = clean_transactions(transactions)
    rfm = build_rfm(clean, "2011-08-01", "2011-09-01").set_index("customer_id")
    assert rfm.loc["123", "frequency"] == 1
    assert rfm.loc["123", "recency"] == 31
    assert rfm.loc["123", "monetary"] == 25
    assert rfm.loc["123", "cancelled_amount"] == 10
    assert rfm.loc["123", "net_amount"] == 15


def test_cutoff_is_exclusive(transactions):
    clean, _ = clean_transactions(transactions)
    rfm = build_rfm(clean, "2011-08-01", "2011-08-20")
    assert rfm.customer_id.tolist() == ["123"]
    future = future_outcomes(clean, "2011-08-20", "2011-09-01")
    assert future.customer_id.tolist() == ["456"]


def test_future_customers_do_not_change_denominator():
    customers = pd.DataFrame({"customer_id": ["a", "b"], "segment": ["S01", "S01"]})
    future = pd.DataFrame(
        {
            "customer_id": ["a", "new"],
            "future_orders": [2, 5],
            "future_amount": [100, 500],
        }
    )
    result = evaluate_future(customers, future).iloc[0]
    assert result.customers == 2
    assert result.repurchase_rate == 0.5
    assert result.future_gross_amount == 100


def test_empty_window_fails(transactions):
    clean, _ = clean_transactions(transactions)
    with pytest.raises(ValueError, match="No hay compras"):
        build_rfm(clean, "2012-01-01", "2012-02-01")
