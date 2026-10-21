"""Resumen comercial calculado desde las tablas finales."""

from pathlib import Path

import pandas as pd


def write_summary(
    summary: dict, profiles: pd.DataFrame, temporal: pd.DataFrame, selection: dict, path: Path
) -> None:
    days = (pd.Timestamp(summary["evaluation_end"]) - pd.Timestamp(summary["cutoff"])).days
    joined = profiles.merge(temporal[["segment", "repurchase_rate"]], on="segment")
    lines = [
        "# Resumen ejecutivo",
        "",
        f"El 10 % de los clientes con mayor gasto concentra el "
        f"**{summary['top_10pct_revenue_share']:.1%} de las ventas brutas**. "
        "Conviene probar acciones distintas según la actividad de compra de cada grupo.",
        "",
        f"Se analizaron **{summary['customers']:,} clientes** y "
        f"**{summary['orders']:,} pedidos**, con ventas brutas de "
        f"**£{summary['gross_amount']:,.2f}**. "
        f"El **{summary['repeat_customer_share']:.1%}** realizó más de un pedido.",
        "",
        "## Perfiles y evidencia",
        "",
        "| Segmento | Perfil | Clientes | Ventas brutas | Recompra posterior |",
        "|---|---|---:|---:|---:|",
    ]
    for row in joined.itertuples():
        lines.append(
            f"| {row.segment} | {row.name} | {row.customers:,} | "
            f"{row.revenue_share:.1%} | {row.repurchase_rate:.1%} |"
        )
    lines += ["", "## Decisiones para probar", ""]
    for row in profiles.itertuples():
        lines.append(f"- **{row.segment}:** {row.proposed_action}")
    lines += [
        "",
        "## Cómo leer estos resultados",
        "",
        f"Observación: `{summary['observation_start']}` ≤ fecha < `{summary['cutoff']}`. "
        f"Evaluación: `{summary['cutoff']}` ≤ fecha < `{summary['evaluation_end']}` "
        f"({days} días). Se cuenta como recompra al menos un pedido positivo posterior. "
        "El denominador incluye todos los clientes del segmento, compren después o no.",
        "",
        f"KMeans seleccionó **{selection['clusters']} grupos**. "
        f"Silhouette: **{selection['silhouette']:.3f}**. "
        f"ARI medio por submuestreo: **{selection['subsample_ari']:.3f}**. "
        "La selección usa exclusivamente el periodo de observación.",
        "",
        "El gasto es bruto, en GBP. Las cancelaciones se informan aparte. "
        "Los registros sin ID no forman parte de los segmentos. La tienda incluye mayoristas: "
        "un gasto alto no permite inferir por sí solo fidelidad, rentabilidad ni satisfacción.",
        "",
        "Las tasas posteriores son descriptivas. No demuestran efectos de las acciones "
        "propuestas ni constituyen una predicción individual de abandono.",
        "",
    ]
    if selection["fallback"]:
        lines += ["Ningún candidato cumplió los mínimos de tamaño y estabilidad configurados.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
