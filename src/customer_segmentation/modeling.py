"""Clustering como complemento al análisis RFM."""

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from customer_segmentation.features import FEATURES


def make_pipeline(k: int, seed: int) -> Pipeline:
    """log1p reduce asimetría; el escalado equilibra días, pedidos y libras."""
    return Pipeline(
        [
            ("log", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
            ("scale", StandardScaler()),
            ("cluster", KMeans(n_clusters=k, random_state=seed, n_init=20)),
        ]
    )


def compare_models(rfm: pd.DataFrame, config: dict) -> tuple[Pipeline, pd.DataFrame, dict]:
    """Selecciona KMeans sin mirar compras futuras; Ward es una referencia descriptiva."""
    values = rfm[FEATURES]
    if not np.isfinite(values.to_numpy()).all() or (values < 0).any().any():
        raise ValueError("RFM debe contener valores finitos y no negativos.")
    candidates = [int(k) for k in config["clusters"] if 2 <= k < len(values)]
    if not candidates:
        raise ValueError("Se necesitan más clientes que el número de grupos candidatos.")
    transformed = make_pipeline(2, config["seed"])[:-1].fit_transform(values)
    sample = min(config["silhouette_sample"], len(values))
    records, models = [], {}
    for k in candidates:
        pipeline = make_pipeline(k, config["seed"]).fit(values)
        labels = pipeline[-1].labels_
        models[k] = pipeline
        seed_scores, subsample_scores = [], []
        for seed in config["stability_seeds"]:
            repeated = make_pipeline(k, seed).fit(values).predict(values)
            seed_scores.append(adjusted_rand_score(labels, repeated))
            subset = values.sample(frac=0.8, random_state=seed)
            if len(subset) <= k:
                raise ValueError("La muestra de estabilidad tiene menos clientes que grupos.")
            sampled = make_pipeline(k, seed).fit(subset).predict(values)
            subsample_scores.append(adjusted_rand_score(labels, sampled))
        for method, assigned in [
            ("kmeans", labels),
            ("ward", AgglomerativeClustering(n_clusters=k).fit_predict(transformed)),
        ]:
            shares = pd.Series(assigned).value_counts(normalize=True)
            records.append(
                {
                    "method": method,
                    "clusters": k,
                    "silhouette": silhouette_score(
                        transformed, assigned, sample_size=sample, random_state=config["seed"]
                    ),
                    "davies_bouldin": davies_bouldin_score(transformed, assigned),
                    "calinski_harabasz": calinski_harabasz_score(transformed, assigned),
                    "minimum_share": shares.min(),
                    "seed_ari": np.mean(seed_scores) if method == "kmeans" else np.nan,
                    "subsample_ari": np.mean(subsample_scores) if method == "kmeans" else np.nan,
                    "inertia": pipeline[-1].inertia_ if method == "kmeans" else np.nan,
                }
            )
    comparison = pd.DataFrame(records)
    valid = comparison.loc[
        comparison.method.eq("kmeans")
        & comparison.minimum_share.ge(config["minimum_cluster_share"])
        & comparison.subsample_ari.ge(config["minimum_stability"])
    ]
    fallback = valid.empty
    if fallback:
        valid = comparison.loc[comparison.method.eq("kmeans")]
    best = valid.sort_values(["silhouette", "clusters"], ascending=[False, True]).iloc[0]
    k = int(best.clusters)
    comparison["selected"] = comparison.method.eq("kmeans") & comparison.clusters.eq(k)
    selection = {
        "method": "kmeans",
        "clusters": k,
        "fallback": fallback,
        "rule": "Mayor silhouette entre KMeans con tamaño y estabilidad mínimos; "
        "Ward se compara como referencia sin asignación nativa a nuevos clientes.",
        "silhouette": float(best.silhouette),
        "subsample_ari": float(best.subsample_ari),
    }
    return models[k], comparison, selection
