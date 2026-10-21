"""Proceso completo: original → calidad → análisis → segmentos → evidencia."""

import argparse
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path

import joblib
import pandas as pd
import yaml

from customer_segmentation.analysis import sales_tables
from customer_segmentation.cleaning import clean_transactions, read_transactions
from customer_segmentation.download import download_data
from customer_segmentation.evaluation import evaluate_future
from customer_segmentation.features import FEATURES, build_rfm, future_outcomes, period
from customer_segmentation.modeling import compare_models
from customer_segmentation.plotting import save_figures
from customer_segmentation.profiling import profile_segments


def write_json(path: Path, content: dict) -> None:
    path.write_text(
        json.dumps(content, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )


def run_pipeline(root: Path, config: dict, raw: pd.DataFrame | None = None) -> dict:
    """Exporta resultados reproducibles; raw permite pruebas sin acceso a internet."""
    start, cutoff, end = (config[k] for k in ["observation_start", "cutoff", "evaluation_end"])
    if not pd.Timestamp(start) < pd.Timestamp(cutoff) < pd.Timestamp(end):
        raise ValueError("Las fechas deben cumplir inicio < corte < fin de evaluación.")
    folders = {
        key: root / path
        for key, path in {
            "data": "data/processed",
            "models": "models",
            "reports": "reports",
        }.items()
    }
    for folder in folders.values():
        folder.mkdir(parents=True, exist_ok=True)
    print("1/6 · Cargar y validar transacciones", flush=True)
    source_hash = None
    if raw is None:
        source = download_data(config["source_url"], root / config["raw_file"])
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        raw = read_transactions(source)
    data, quality = clean_transactions(raw)
    if data.date.max() < pd.Timestamp(end) - pd.Timedelta(days=1):
        raise ValueError("El dataset no cubre el final del periodo de evaluación.")
    data.to_parquet(folders["data"] / "transactions.parquet", index=False)
    print("2/6 · Construir RFM y analizar las compras", flush=True)
    rfm = build_rfm(data, start, cutoff)
    rfm.to_parquet(folders["data"] / "customer_rfm.parquet", index=False)
    observed = period(data, start, cutoff)
    monthly, summary = sales_tables(observed, rfm)
    summary.update({"observation_start": start, "cutoff": cutoff, "evaluation_end": end})
    quality["observation_rows"] = len(observed)
    quality["outside_observation_rows"] = len(data) - len(observed)
    print("3/6 · Comparar agrupamientos", flush=True)
    pipeline, comparison, selection = compare_models(rfm, config)
    rfm["cluster"] = pipeline.predict(rfm[FEATURES])
    print("4/6 · Describir segmentos y evaluar recompra posterior", flush=True)
    customers, profiles = profile_segments(rfm)
    outcomes = future_outcomes(data, cutoff, end)
    temporal = evaluate_future(customers, outcomes)
    summary["future_customers_new_to_snapshot"] = int(
        (~outcomes.customer_id.isin(customers.customer_id)).sum()
    )
    summary["clusters"] = selection["clusters"]
    summary["future_repurchase_rate"] = float(temporal.repurchasers.sum() / len(customers))
    summary["observed_cancellations_without_purchase_customer"] = float(
        -observed.loc[
            observed.status.eq("cancellation") & ~observed.customer_id.isin(customers.customer_id),
            "amount",
        ].sum()
    )
    print("5/6 · Exportar tablas, modelo y gráficos", flush=True)
    customers.to_csv(folders["data"] / "customer_segments.csv", index=False)
    for name, frame in {
        "monthly_sales": monthly,
        "segment_profiles": profiles,
        "model_comparison": comparison,
        "temporal_evaluation": temporal,
    }.items():
        frame.to_csv(folders["reports"] / f"{name}.csv", index=False)
    write_json(folders["reports"] / "quality_report.json", quality)
    write_json(folders["reports"] / "summary.json", summary)
    versions = {
        package: importlib.metadata.version(package)
        for package in ["pandas", "numpy", "scikit-learn", "matplotlib", "pyarrow", "streamlit"]
    }
    metadata = {
        "config": config,
        "features": FEATURES,
        "selection": selection,
        "source_sha256": source_hash,
        "python": platform.python_version(),
        "versions": versions,
        "label_map": customers[["cluster", "segment", "name"]].drop_duplicates().to_dict("records"),
        "scope": "Histórico de clientes con compras positivas en la ventana. "
        "Monetary mide gasto bruto; las cancelaciones se informan aparte.",
    }
    joblib.dump(pipeline, folders["models"] / "segmentation_pipeline.joblib")
    write_json(folders["models"] / "model_metadata.json", metadata)
    write_json(folders["reports"] / "run_metadata.json", metadata)
    save_figures(monthly, customers, profiles, comparison, temporal, folders["reports"] / "figures")
    print("6/6 · Proceso terminado. Consultar reports/ y abrir el dashboard.", flush=True)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config/settings.yaml"))
    args = parser.parse_args()
    config_path = args.config.resolve()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    run_pipeline(config_path.parent.parent, config)


if __name__ == "__main__":
    main()
