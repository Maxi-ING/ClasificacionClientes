import json

import joblib
import numpy as np
import pandas as pd

from customer_segmentation.features import FEATURES
from customer_segmentation.pipeline import run_pipeline


def test_pipeline_exports_consistent_results(tmp_path):
    rows = []
    rng = np.random.default_rng(42)
    for customer in range(60):
        for order in range(1 if customer < 30 else 5):
            rows.append(
                {
                    "Invoice": f"{customer}-{order}",
                    "StockCode": "A",
                    "Description": "A",
                    "Quantity": 1,
                    "Price": float(rng.integers(10, 100)),
                    "InvoiceDate": pd.Timestamp("2011-01-01")
                    + pd.Timedelta(
                        days=int(rng.integers(0, 100) if customer < 30 else rng.integers(180, 240))
                    ),
                    "Customer ID": customer,
                    "Country": "United Kingdom",
                    "source_sheet": "one",
                }
            )
    rows.append({**rows[-1], "Invoice": "future", "InvoiceDate": pd.Timestamp("2011-11-29")})
    config = {
        "observation_start": "2011-01-01",
        "cutoff": "2011-09-01",
        "evaluation_end": "2011-11-30",
        "seed": 42,
        "clusters": [2, 3],
        "stability_seeds": [7],
        "silhouette_sample": 60,
        "minimum_cluster_share": 0.03,
        "minimum_stability": 0.5,
    }
    summary = run_pipeline(tmp_path, config, pd.DataFrame(rows))
    customers = pd.read_csv(tmp_path / "data/processed/customer_segments.csv")
    profiles = pd.read_csv(tmp_path / "reports/segment_profiles.csv")
    assert summary["customers"] == len(customers) == 60
    assert profiles.customers.sum() == 60
    assert np.isclose(profiles.revenue_share.sum(), 1)
    assert np.isclose(profiles.gross_amount.sum(), summary["gross_amount"])
    model = joblib.load(tmp_path / "models/segmentation_pipeline.joblib")
    assert np.array_equal(model.predict(customers[FEATURES]), customers.cluster)
    metadata = json.loads((tmp_path / "reports/run_metadata.json").read_text())
    assert metadata["config"]["cutoff"] == "2011-09-01"
    assert (tmp_path / "reports/figures/segment_overview.png").exists()
