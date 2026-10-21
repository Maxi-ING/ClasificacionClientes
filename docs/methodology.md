# Metodología

## Pregunta de negocio

¿Cómo distribuir las acciones de recompra y fidelización según el comportamiento observado
de los clientes? Primero se estudian las compras con Python y pandas. El clustering complementa
ese análisis para resumir patrones y comparar perfiles.

## 1. Periodos comunes

| Uso | Inicio incluido | Final excluido | Finalidad |
|---|---|---|---|
| Observación | 2010-09-01 | 2011-09-01 | Análisis de ventas, RFM y ajuste de segmentos. |
| Evaluación | 2011-09-01 | 2011-11-30 | Recompra durante los 90 días posteriores. |

La selección del número de grupos no consulta las compras futuras. Los datos anteriores o
posteriores a estas ventanas se conservan en las transacciones depuradas, pero no se añaden
al cálculo RFM ni a la evaluación. Los periodos se cambian en `config/settings.yaml`.

## 2. Calidad y unión de hojas

Las dos hojas se solapan en diciembre de 2010. Para cada combinación de los ocho campos
originales se cuenta su ocurrencia dentro de cada hoja. Luego se conserva una sola copia de
cada ocurrencia entre hojas. Así, dos líneas iguales en una hoja y una en otra dejan dos líneas,
no una ni tres. La regla asume que los registros idénticos entre hojas representan copias del
solapamiento. La coincidencia exige los ocho campos, incluido fecha y hora.

Las líneas idénticas repetidas **dentro de una hoja se conservan**: no existe un identificador
de línea que permita demostrar que son errores. Es una decisión explícita que puede afectar
los importes, por lo que se informa su cantidad en el reporte de calidad.

Después se excluyen secuencialmente los registros con:

1. ID de cliente ausente.
2. Fecha inválida.
3. Factura vacía.
4. Cantidad ausente o igual a cero.
5. Precio ausente, cero o negativo.
6. Factura C con cantidad positiva, por inconsistencia.

Cada registro se cuenta una sola vez en las exclusiones. El faltante en descripción no impide
construir RFM. No se inventan clientes para recuperar líneas sin identificador.

## 3. Compras y cancelaciones

Una cantidad negativa o una factura con prefijo C se clasifica como cancelación. Su importe
conserva el signo. Las compras positivas alimentan RFM; las cancelaciones se resumen aparte.
No se intenta vincular una cancelación con una compra específica cuando el archivo no ofrece
esa relación.

| Indicador | Cálculo e interpretación |
|---|---|
| Ventas brutas | Suma de cantidad × precio de las compras positivas. |
| Importe cancelado | Valor absoluto de los importes negativos observados. |
| Saldo neto observado | Ventas brutas menos importe cancelado en la misma ventana. |

El saldo no representa beneficio y puede incluir cancelaciones de compras realizadas fuera
de la ventana. Las cancelaciones de clientes sin compras positivas en la ventana aparecen en
el total comercial, pero no en los perfiles RFM. Esa diferencia se registra como
`observed_cancellations_without_purchase_customer` en `reports/summary.json`.

Se conserva la precisión original de los importes. El formato de los gráficos y tablas redondea
solo para facilitar la lectura.

## 4. Indicadores por cliente

| Variable | Definición |
|---|---|
| Recencia | Días entre el corte común y la fecha de su última compra positiva, usando días calendario. |
| Frecuencia | Cantidad de facturas distintas con compras positivas en la ventana. |
| Valor monetario | Gasto bruto de esas compras en GBP. |
| Ticket promedio | Gasto bruto dividido por facturas distintas. |

El país es el de la última compra observada. Solo recencia, frecuencia y valor monetario se usan
para agrupar; ticket, país y cancelaciones ayudan a describir los perfiles.

El porcentaje de compradores recurrentes es la proporción de clientes con más de una factura.
La concentración del 10 % usa los `floor(n_clientes × 0.10)` clientes con mayor gasto.
En este análisis son 433 de 4 335 clientes. Las participaciones en ventas siempre usan gasto bruto.

## 5. Preparación y comparación

Se aplica `log1p` a las tres variables para reducir asimetría y luego `StandardScaler` para
equilibrar sus escalas. No se eliminan grandes compradores por gastar mucho: el origen incluye
mayoristas y sus operaciones pueden ser válidas. Esto no elimina toda influencia de valores extremos.

Se comparan KMeans y clustering jerárquico Ward con 2 a 6 grupos, sobre las mismas variables
transformadas. Se registran silhouette, Davies–Bouldin, Calinski–Harabasz y tamaño del grupo menor.
Para KMeans también se registra inercia y estabilidad mediante ARI:

- Repetición con tres semillas alternativas.
- Ajuste sobre tres submuestras del 80 %, seguido de asignación de todos los clientes.

La estabilidad de las submuestras incluye volver a ajustar las transformaciones. No equivale
a estabilidad temporal. Silhouette usa una muestra reproducible de hasta 2 000 clientes.

## 6. Selección y perfiles

Se elige el KMeans con mayor silhouette entre los que cumplen:

- Al menos un 3 % de los clientes en cada grupo.
- ARI medio por submuestreo de al menos 0.80.

Si ninguno cumple, el proceso lo indica y selecciona el mayor silhouette de KMeans como
resultado exploratorio. Ward es una referencia: no ofrece `predict` nativo para nuevos clientes.
Por eso no se afirma que KMeans sea superior a todos los métodos. En esta ejecución, Ward con
dos grupos tiene un silhouette ligeramente mayor y KMeans ofrece asignación reutilizable.

Los códigos se ordenan por gasto mediano. Los nombres se basan en medianas de frecuencia,
recencia y gasto, comparadas con la distribución general. Son descripciones del grupo; sus
integrantes pueden tener comportamientos distintos.

## 7. Evaluación posterior

Se considera recompra al menos un pedido positivo entre el 1 de septiembre y el 29 de noviembre
de 2011, inclusive. Se divide por todos los clientes originales de cada grupo. Quienes no
compran después permanecen con cero; los clientes nuevos se contabilizan aparte y no cambian
el denominador. Las cancelaciones posteriores no descuentan la señal de pedido positivo.

Esta evaluación describe asociación entre perfiles y actividad posterior. No mide exactitud
de clasificación, predicción individual de abandono ni efectos causales de campañas.

## 8. Límites y siguiente prueba comercial

El análisis representa clientes identificados de una tienda y un periodo histórico. No describe
el mercado actual ni se transfiere automáticamente a otra empresa. Los clientes recién
adquiridos tienen menos tiempo para acumular pedidos y no se ajusta por antigüedad de relación.

Las recomendaciones deben probarse con una asignación aleatoria a campaña y control dentro
de cada segmento. Mediríamos diferencia en recompra y margen por cliente, incluyendo el costo
del incentivo. El dataset no contiene el costo de productos ni resultados de estas campañas.

Referencias: [UCI](https://archive.ics.uci.edu/dataset/502/online+retail+ii),
[clustering en scikit-learn](https://scikit-learn.org/stable/modules/clustering.html).
