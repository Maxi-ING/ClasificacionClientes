# Datos

**Fuente elegida:** [Online Retail II · UCI](https://archive.ics.uci.edu/dataset/502/online+retail+ii).
Transacciones de una tienda británica entre el 1 de diciembre de 2009 y el 9 de diciembre de 2011.
La tienda vende principalmente artículos de regalo y tiene compradores mayoristas.

**Crédito:** Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository.
[DOI: 10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D).
Licencia de los datos: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Comparación que motivó la elección

| Fuente | Ventaja | Decisión |
|---|---|---|
| Online Retail II | Dos años de líneas de compra, clientes, fechas e importes. | Elegido: permite separar observación y evaluación posterior. |
| [Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail) | Un año y menor tamaño. | Alternativa para una versión más corta. No se mezcla con Online Retail II. |
| [Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | Pedidos, clientes, pagos y entregas en varias tablas. | Mejor para ampliar el análisis operativo. Para RFM exige uniones adicionales. |

## Obtener los archivos

Desde la raíz del proyecto, después de instalar las dependencias:

```bash
python -m customer_segmentation.pipeline
```

El proceso descarga el ZIP oficial y extrae únicamente `online_retail_II.xlsx`.
Si el archivo ya existe, lo conserva. Registra el SHA-256 y crea una caché Parquet para acelerar
las siguientes lecturas. Si cambia el original, elimina su caché `.parquet` antes de repetir.
El checksum utilizado en el análisis publicado está en `reports/run_metadata.json`.

## Campos originales y nombres del código

| Original | Código | Significado |
|---|---|---|
| `Invoice` | `invoice` | Identificador de factura. El prefijo C indica cancelación. |
| `StockCode` | `product` | Código del artículo. |
| `Description` | `description` | Descripción del artículo. |
| `Quantity` | `quantity` | Unidades de la línea. |
| `InvoiceDate` | `date` | Fecha y hora de la operación. |
| `Price` | `price` | Precio unitario en GBP. |
| `Customer ID` | `customer_id` | Identificador del cliente; se trata como texto. |
| `Country` | `country` | País asociado a la operación. |

Una fila original es una **línea de producto**, no un pedido ni un cliente.
Los nombres se comprobaron en el XLSX: no coinciden exactamente con los usados en la ficha de UCI.

## Archivos generados

| Ruta | Contenido |
|---|---|
| `raw/online_retail_II.xlsx` | Original sin editar. |
| `raw/online_retail_II.source.json` | Fuente, tamaño y checksum. |
| `raw/online_retail_II.parquet` | Caché de ambas hojas, con su origen. |
| `processed/transactions.parquet` | Líneas válidas, incluyendo cancelaciones identificadas. |
| `processed/customer_rfm.parquet` | Una fila por cliente del periodo de observación. |
| `processed/customer_segments.csv` | Indicadores y segmento para cada cliente. |

Estos archivos se generan localmente y no se versionan. Los informes agregados y los gráficos
sí se incluyen en el repositorio para poder revisar los hallazgos sin descargar el original.
