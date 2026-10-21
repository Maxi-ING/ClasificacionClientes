"""Exploración comercial de los resultados; ejecutar desde la raíz del repositorio."""

import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PALETTE = ["#123B4A", "#168C85", "#E5A348", "#7084AA", "#B96E74", "#709D76"]

st.set_page_config(page_title="Clientes · Análisis RFM", page_icon="◉", layout="wide")


@st.cache_data
def load_reports(version: float):
    del version
    summary = json.loads((REPORTS / "summary.json").read_text(encoding="utf-8"))
    tables = {
        name: pd.read_csv(REPORTS / f"{name}.csv")
        for name in ["segment_profiles", "monthly_sales", "temporal_evaluation", "model_comparison"]
    }
    return summary, tables


@st.cache_data
def load_customers(version: float):
    del version
    return pd.read_csv(ROOT / "data/processed/customer_segments.csv", dtype={"customer_id": str})


def money(value):
    return f"£{value:,.0f}"


def color_encoding(segments):
    return alt.Color("segment:N", title="Segmento", scale=alt.Scale(domain=segments, range=PALETTE))


if not (REPORTS / "summary.json").exists():
    st.title("Análisis de clientes")
    st.info("Primero genera los resultados siguiendo los pasos de ejecución del README.")
    st.stop()

summary, tables = load_reports((REPORTS / "summary.json").stat().st_mtime)
profiles = tables["segment_profiles"]
segments = profiles.segment.tolist()
color = color_encoding(segments)

with st.sidebar:
    st.markdown("### CLIENTES")
    st.caption("Compras · Comportamiento · Segmentos")
    page = st.radio("Explorar", ["Resumen", "Segmentos", "Clientes", "Método"])
    st.divider()
    st.caption("Online Retail II · UCI")
    st.caption("Moneda: libras esterlinas (GBP).")
    st.caption("Datos históricos de una tienda británica con compradores mayoristas.")

st.title(
    {
        "Resumen": "Entender a los clientes para decidir mejor",
        "Segmentos": "Perfiles de compra y acciones propuestas",
        "Clientes": "Explorar la cartera de clientes",
        "Método": "Cómo se construyeron los resultados",
    }[page]
)
last_day = (pd.Timestamp(summary["cutoff"]) - pd.Timedelta(days=1)).strftime("%d/%m/%Y")
first_day = pd.Timestamp(summary["observation_start"]).strftime("%d/%m/%Y")
st.caption(f"Compras observadas del {first_day} al {last_day} · Corte histórico común para RFM.")

if page == "Resumen":
    st.markdown(
        f"El 10 % de los clientes con mayor gasto concentra el "
        f"**{summary['top_10pct_revenue_share']:.1%} de las ventas brutas**. "
        "La segmentación permite distinguir comportamientos antes de proponer campañas."
    )
    cols = st.columns(4)
    cols[0].metric("Clientes analizados", f"{summary['customers']:,}")
    cols[1].metric("Pedidos", f"{summary['orders']:,}")
    cols[2].metric("Ventas brutas", money(summary["gross_amount"]))
    cols[3].metric("Clientes con más de un pedido", f"{summary['repeat_customer_share']:.1%}")
    st.subheader("Evolución de las compras")
    monthly = tables["monthly_sales"]
    chart = (
        alt.Chart(monthly)
        .mark_line(point=True, color=PALETTE[1], strokeWidth=3)
        .encode(
            x=alt.X("month:O", title="Mes", axis=alt.Axis(labelAngle=-35)),
            y=alt.Y("gross_amount:Q", title="Ventas brutas (GBP)"),
            tooltip=[
                alt.Tooltip("month:N", title="Mes"),
                alt.Tooltip("gross_amount:Q", title="Ventas brutas (GBP)", format=",.0f"),
                alt.Tooltip("orders:Q", title="Pedidos", format=","),
            ],
        )
        .properties(height=290)
    )
    st.altair_chart(chart, width="stretch")
    left, right = st.columns(2)
    with left:
        st.subheader("Clientes y ventas por segmento")
        shares = profiles.melt(
            id_vars="segment",
            value_vars=["customer_share", "revenue_share"],
            var_name="measure",
            value_name="share",
        )
        shares["measure"] = shares.measure.map(
            {
                "customer_share": "Clientes",
                "revenue_share": "Ventas brutas",
            }
        )
        st.altair_chart(
            alt.Chart(shares)
            .mark_bar()
            .encode(
                x=alt.X("segment:N", title="Segmento", axis=alt.Axis(labelAngle=0)),
                xOffset="measure:N",
                y=alt.Y("share:Q", title="Participación", axis=alt.Axis(format="%")),
                color=alt.Color("measure:N", title="", scale=alt.Scale(range=PALETTE[:2])),
                tooltip=["segment", "measure", alt.Tooltip("share:Q", format=".1%")],
            )
            .properties(height=260),
            width="stretch",
        )
    with right:
        st.subheader("Recompra en los 90 días posteriores")
        st.altair_chart(
            alt.Chart(tables["temporal_evaluation"])
            .mark_bar()
            .encode(
                x=alt.X("segment:N", title="Segmento", axis=alt.Axis(labelAngle=0)),
                y=alt.Y(
                    "repurchase_rate:Q",
                    title="Clientes que volvieron a comprar",
                    scale=alt.Scale(domain=[0, 1]),
                    axis=alt.Axis(format="%"),
                ),
                color=color,
                tooltip=["segment", alt.Tooltip("repurchase_rate:Q", format=".1%")],
            )
            .properties(height=260),
            width="stretch",
        )
    st.caption("La recompra es un resultado observado. No mide el efecto de una campaña.")

elif page == "Segmentos":
    choice = st.selectbox("Seleccionar segmento", segments)
    row = profiles.set_index("segment").loc[choice]
    st.subheader(f"{choice} · {row['name']}")
    cols = st.columns(4)
    cols[0].metric("Clientes", f"{row.customers:,.0f}")
    cols[1].metric("Días desde la última compra · mediana", f"{row.recency_median:,.0f}")
    cols[2].metric("Pedidos por cliente · mediana", f"{row.frequency_median:,.0f}")
    cols[3].metric("Gasto bruto por cliente · mediana", money(row.monetary_median))
    st.markdown(f"**Acción para probar:** {row.proposed_action}")
    st.markdown(
        f"Este grupo representa el **{row.customer_share:.1%} de los clientes** "
        f"y el **{row.revenue_share:.1%} de las ventas brutas**."
    )
    display = profiles[
        [
            "segment",
            "name",
            "customers",
            "recency_median",
            "frequency_median",
            "monetary_median",
        ]
    ].rename(
        columns={
            "segment": "Segmento",
            "name": "Perfil",
            "customers": "Clientes",
            "recency_median": "Recencia mediana (días)",
            "frequency_median": "Pedidos medianos",
            "monetary_median": "Gasto bruto mediano (GBP)",
        }
    )
    st.dataframe(display, hide_index=True, width="stretch")
    st.download_button(
        "Descargar perfiles",
        profiles.to_csv(index=False).encode("utf-8-sig"),
        file_name="perfiles_segmentos.csv",
        mime="text/csv",
    )

elif page == "Clientes":
    customer_path = ROOT / "data/processed/customer_segments.csv"
    if not customer_path.exists():
        st.info("La tabla individual se genera al ejecutar el proceso indicado en el README.")
        st.stop()
    customers = load_customers(customer_path.stat().st_mtime)
    left, right = st.columns(2)
    chosen = left.multiselect("Segmentos", segments, default=segments)
    countries = sorted(customers.country.dropna().unique())
    country = right.selectbox("País", ["Todos"] + countries)
    filtered = customers.loc[customers.segment.isin(chosen)]
    if country != "Todos":
        filtered = filtered.loc[filtered.country.eq(country)]
    st.metric("Clientes en la selección", f"{len(filtered):,}")
    if filtered.empty:
        st.info("No hay clientes para los filtros seleccionados.")
    else:
        chart = (
            alt.Chart(filtered)
            .mark_circle(opacity=0.5, size=35)
            .encode(
                x=alt.X("recency:Q", title="Días desde la última compra"),
                y=alt.Y("monetary:Q", title="Gasto bruto (GBP)", scale=alt.Scale(type="log")),
                color=color,
                tooltip=[
                    alt.Tooltip("customer_id:N", title="Cliente"),
                    "segment",
                    alt.Tooltip("frequency:Q", title="Pedidos"),
                    alt.Tooltip("monetary:Q", title="Gasto bruto (GBP)", format=",.2f"),
                ],
            )
            .properties(height=340)
        )
        st.altair_chart(chart, width="stretch")
        columns = ["customer_id", "segment", "country", "recency", "frequency", "monetary"]
        labels = ["Cliente", "Segmento", "País", "Recencia (días)", "Pedidos", "Gasto bruto (GBP)"]
        st.dataframe(
            filtered[columns].rename(columns=dict(zip(columns, labels))),
            hide_index=True,
            width="stretch",
        )
    st.download_button(
        "Descargar selección",
        filtered.to_csv(index=False).encode("utf-8-sig"),
        file_name="clientes_seleccionados.csv",
        mime="text/csv",
    )

else:
    st.markdown("""
    1. **Validar compras:** identificar copias entre hojas, faltantes y cancelaciones.
    2. **Analizar clientes:** medir recencia, pedidos distintos y gasto bruto.
    3. **Agrupar comportamientos:** transformar RFM y comparar agrupamientos.
    4. **Describir y contrastar:** interpretar perfiles y observar recompra posterior.
    """)
    meta = json.loads((REPORTS / "run_metadata.json").read_text(encoding="utf-8"))
    selection = meta["selection"]
    st.markdown(
        f"Se seleccionaron **{selection['clusters']} grupos con KMeans**. "
        f"Silhouette: **{selection['silhouette']:.3f}**. "
        f"Estabilidad por submuestreo (ARI): **{selection['subsample_ari']:.3f}**."
    )
    if selection["fallback"]:
        st.warning("Ningún candidato cumplió ambos mínimos de tamaño y estabilidad.")
    st.caption(selection["rule"])
    st.dataframe(tables["model_comparison"], hide_index=True, width="stretch")
    st.markdown("""
    **Interpretación.** Recencia alta significa más tiempo sin comprar. El gasto es bruto y
    está expresado en GBP. Las cancelaciones se analizan aparte. Los nombres de los segmentos
    describen sus medianas; no todos sus integrantes tienen el mismo comportamiento.

    **Alcance.** Los registros sin ID de cliente no se asignan a ningún grupo. Las propuestas
    comerciales requieren una prueba con control para medir su efecto.
    """)
