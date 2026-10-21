"""Gráficos reproducibles para documentación y análisis."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter, PercentFormatter

COLORS = ["#123B4A", "#168C85", "#E5A348", "#7084AA", "#B96E74", "#709D76"]


def save_figures(
    monthly: pd.DataFrame,
    customers: pd.DataFrame,
    profiles: pd.DataFrame,
    comparison: pd.DataFrame,
    temporal: pd.DataFrame,
    destination: Path,
) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.labelcolor": "#334155",
            "text.color": "#123B4A",
            "axes.titleweight": "bold",
            "figure.facecolor": "white",
        }
    )

    def save(fig, name):
        fig.savefig(destination / f"{name}.png", dpi=160, bbox_inches="tight", facecolor="white")
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 4.3), layout="constrained")
    x = np.arange(len(monthly))
    ax.plot(x, monthly.gross_amount, color=COLORS[1], marker="o", linewidth=2.5)
    ax.set_xticks(x, monthly.month.str[2:], rotation=35)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, pos: f"£{value / 1000:,.0f} mil"))
    ax.set(title="Ventas brutas durante el periodo de observación", xlabel="Mes", ylabel="")
    ax.grid(axis="y", alpha=0.12)
    save(fig, "monthly_sales")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.3), layout="constrained")
    x = np.arange(len(profiles))
    width = 0.36
    axes[0].bar(x - width / 2, profiles.customer_share, width, color=COLORS[0], label="Clientes")
    axes[0].bar(
        x + width / 2, profiles.revenue_share, width, color=COLORS[1], label="Ventas brutas"
    )
    axes[0].set_xticks(x, profiles.segment)
    axes[0].yaxis.set_major_formatter(PercentFormatter(1))
    axes[0].set(title="Peso de cada segmento", xlabel="Segmento")
    axes[0].legend(frameon=False)
    temporal = temporal.set_index("segment").reindex(profiles.segment)
    axes[1].bar(profiles.segment, temporal.repurchase_rate, color=COLORS[: len(profiles)])
    axes[1].yaxis.set_major_formatter(PercentFormatter(1))
    axes[1].set(title="Recompra observada en los 90 días posteriores", xlabel="Segmento")
    axes[1].set_ylim(0, 1)
    for ax in axes:
        ax.grid(axis="y", alpha=0.12)
    save(fig, "segment_overview")

    fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
    for i, row in enumerate(profiles.itertuples()):
        group = customers.loc[customers.segment.eq(row.segment)]
        ax.scatter(
            group.recency,
            group.monetary,
            alpha=0.45,
            s=13,
            color=COLORS[i],
            label=f"{row.segment} · {row.name}",
        )
    ax.set_yscale("log")
    ax.set(
        title="Recencia y gasto de los clientes",
        xlabel="Días desde la última compra",
        ylabel="Gasto bruto en GBP · escala logarítmica",
    )
    ax.legend(frameon=False, fontsize=9, loc="upper right")
    save(fig, "customer_map")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
    for i, method in enumerate(["kmeans", "ward"]):
        group = comparison.loc[comparison.method.eq(method)]
        axes[0].plot(group.clusters, group.silhouette, marker="o", label=method, color=COLORS[i])
    km = comparison.loc[comparison.method.eq("kmeans")]
    axes[1].plot(km.clusters, km.inertia, marker="o", color=COLORS[1])
    axes[0].set(title="Separación de los grupos", xlabel="Número de grupos", ylabel="Silhouette")
    axes[1].set(title="Dispersión interna de KMeans", xlabel="Número de grupos", ylabel="Inercia")
    axes[0].legend(frameon=False)
    save(fig, "model_comparison")
