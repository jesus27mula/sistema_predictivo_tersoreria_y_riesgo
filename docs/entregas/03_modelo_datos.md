# Sistema predictivo de tesorería y riesgo de retraso en el cobro

## 1. Resumen de la idea y de los datos del proyecto
El proyecto tiene como finalidad desarrollar un sistema de analítica predictiva que ayude a una empresa a anticipar su evolución futura de tesorería y a identificar las facturas o clientes con mayor probabilidad de pagar fuera del plazo acordado.

La necesidad de negocio surge porque una empresa puede presentar beneficios contables y, al mismo tiempo, sufrir tensiones de liquidez si sus clientes pagan tarde o si se concentran demasiadas salidas de caja en determinados momentos. La falta de visibilidad sobre los cobros futuros dificulta la planificación financiera, la gestión de pagos y la priorización de las acciones de recobro.

La solución propuesta estará formada por tres componentes principales:
* **Un modelo de clasificación** que estime la probabilidad de que una factura se pague después de su fecha de vencimiento.
* **Un modelo o sistema de previsión de tesorería** que estime el saldo futuro de caja a distintos horizontes temporales.
* **Una segmentación de clientes** basada en su volumen de negocio y en su comportamiento histórico de pago.

Los resultados se mostrarán posteriormente en un dashboard con indicadores como:
* Saldo actual y saldo previsto.
* Cobros y pagos esperados.
* Facturas con mayor riesgo de retraso.
* Clientes prioritarios para recobro.
* Deuda vencida.
* Alertas de posibles tensiones de liquidez.

### Fuentes de datos
La principal fuente real será el dataset público *Finance Factoring — IBM Late Payment Histories*, disponible en Kaggle. Su finalidad es analizar y predecir cuándo se pagarán las facturas y qué clientes presentan un comportamiento de pago más lento.

En la copia pública revisada, el dataset contiene:
* **2.466** facturas.
* **100** clientes.
* **12** campos originales.
* Fechas de facturación, vencimiento y liquidación.
* Importe de la factura.
* País o zona del cliente.
* Existencia de disputas.
* Modalidad de factura en papel o electrónica.
* Días transcurridos hasta el cobro.
* Días de retraso.

La información real aportará principalmente:
* Facturas emitidas.
* Clientes.
* Fechas de emisión.
* Fechas de vencimiento.
* Fechas reales de pago.
* Importes.
* Comportamiento histórico de pago.
* Variable objetivo del modelo de retraso.

El dataset no contiene información sobre proveedores, nóminas, alquileres, impuestos, préstamos, saldos bancarios ni otras salidas de caja. Por este motivo se generará una segunda fuente de información de carácter sintético.

Los datos sintéticos incluirán:
* Proveedores y sus respectivas facturas y pagos.
* Nóminas y costes sociales.
* Alquileres, suministros y gastos administrativos.
* Cuotas de financiación.
* Impuestos simulados.
* Saldo bancario inicial.

Estos datos se generarán mediante reglas empresariales reproducibles, parámetros documentados y una semilla aleatoria fija. Cada registro indicará expresamente si su procedencia es real o sintética.

También se generará internamente una tabla calendario para incorporar:
* Día de la semana, mes y trimestre.
* Fin de mes y fin de trimestre.
* Día laborable.
* Período de nóminas.
* Período de impuestos.

En la primera versión no se incorporarán indicadores macroeconómicos externos, porque el objetivo principal es demostrar la integración entre cuentas a cobrar, comportamiento de pago y tesorería empresarial.

### Alcance del concepto de impago
El dataset contiene facturas que finalmente fueron liquidadas. Por tanto, permite predecir:
1. Pago puntual.
2. Pago con retraso.
3. Número de días hasta el cobro.

No permite identificar con rigor un impago definitivo, porque no contiene facturas declaradas incobrables ni facturas permanentemente abiertas. Por esta razón, el alcance inicial se formulará como: **Sistema predictivo de tesorería y riesgo de retraso en el cobro.**

El riesgo de impago definitivo quedará planteado como una posible ampliación futura, condicionada a la disponibilidad de una fuente que incluya facturas incobrables.

## 2. Tecnología y formatos de almacenamiento elegidos
Se utilizará una combinación de formatos:

*   CSV para conservar los datos originales.
*   Parquet para los datos procesados y la capa gold.
*   JSON para configuraciones, metadatos y parámetros de simulación.
*   CSV opcional para exportaciones dirigidas al dashboard o a usuarios no técnicos.

No se utilizará inicialmente una base de datos relacional porque el volumen de información es reducido y puede gestionarse correctamente mediante Python, Pandas y ficheros estructurados. Una base de datos añadiría complejidad sin aportar una ventaja proporcional durante esta fase del proyecto.

### 2.1. CSV para la capa raw
El fichero descargado de Kaggle se conservará en su formato CSV original, sin modificarlo.
Ejemplo:

`data/raw/external/accounts_receivable_ibm.csv`

La utilización de CSV tiene sentido porque:
* es el formato original de la fuente;
* puede abrirse fácilmente;
* permite comprobar los datos sin herramientas especiales;
* facilita la trazabilidad;
* evita alterar la fuente original;
* es compatible con Python, Excel, Power BI y otras herramientas.

El archivo original será considerado inmutable. Las operaciones de limpieza no se realizarán directamente sobre él.
Los primeros datos sintéticos también podrán guardarse inicialmente en CSV para facilitar su inspección:

*   `data/raw/synthetic/supplier_invoices.csv`
*   `data/raw/synthetic/recurring_expenses.csv`
*   `data/raw/synthetic/simulation_movements.csv`

### 2.2. Parquet para processed y gold
Las capas processed y gold se almacenarán principalmente en formato Parquet.
Parquet es un formato columnar diseñado para almacenar y recuperar datos analíticos de manera eficiente. Permite conservar tipos de datos, aplicar compresión y seleccionar solo las columnas necesarias durante la lectura.
Aunque el volumen inicial no es elevado, tiene sentido utilizar Parquet porque:

*   conserva mejor los tipos de fechas, booleanos y números;
*   evita reinterpretaciones frecuentes de tipos;
*   ocupa menos espacio que un CSV equivalente;
*   mejora la velocidad de lectura;
*   es compatible con Pandas, PyArrow, DuckDB y herramientas de analítica;
*   representa una práctica habitual en pipelines de datos;
*   permite que el proyecto pueda crecer sin cambiar su arquitectura.

Ejemplos:
*   `data/processed/customer_invoices.parquet`
*   `data/processed/cash_movements.parquet`
*   `data/gold/gold_invoice_risk.parquet`
*   `data/gold/gold_daily_cashflow.parquet`

### 2.3. JSON para configuración y metadatos
Se utilizarán ficheros JSON para guardar información que no corresponde a una tabla transaccional.
Por ejemplo:

*   `data/metadata/simulation_config.json`
*   `data/metadata/data_quality_report.json`
*   `data/metadata/dataset_lineage.json`

El fichero `simulation_config.json` contendrá parámetros como:
*   semilla aleatoria;
*   porcentaje simulado de costes de proveedores;
*   porcentaje de nóminas;
*   importe del alquiler;
*   periodicidad de los pagos;
*   saldo inicial;
*   umbral de tensión de liquidez.

JSON es adecuado porque permite organizar parámetros mediante pares clave-valor y estructuras jerárquicas, manteniendo la configuración separada del código.

### 2.4. Exportaciones CSV
Los datasets definitivos podrán exportarse también como CSV cuando sea necesario compartirlos o conectarlos con determinadas herramientas.
Por ejemplo:

*   `exports/dashboard_cashflow.csv`
*   `exports/dashboard_customer_risk.csv`

Estos CSV serán copias de consumo, no la fuente principal de datos.

### 2.5. Tecnologías descartadas inicialmente
**Excel**
No se utilizará como almacenamiento principal porque:
*   permite modificaciones manuales difíciles de auditar;
*   puede alterar fechas y tipos de datos;
*   no es adecuado para automatizar un pipeline reproducible;
*   puede introducir fórmulas o formatos no controlados.

Podrá emplearse únicamente para revisar resultados o presentar pequeñas muestras.

**Base de datos relacional**
No se considera necesaria en la primera versión porque el proyecto tendrá unos pocos miles de facturas y menos de mil registros diarios.
Si posteriormente se construye una aplicación multiusuario o un dashboard que necesite consultas permanentes, podría añadirse SQLite o PostgreSQL como capa de servicio. No sería necesario rediseñar la lógica principal, ya que los datasets ya estarán organizados de forma relacional.

# Estructura de Capas de Datos y Gestión de Metadatos

## 3. Estructura de capas de datos
Se utilizará una arquitectura basada en las capas *raw*, *processed* y *gold*, añadiendo una carpeta específica para metadatos.

```text
data/
│
├── raw/
│   ├── external/
│   │   └── accounts_receivable_ibm.csv
│   │
│   └── synthetic/
│       ├── suppliers.csv
│       ├── supplier_invoices.csv
│       ├── recurring_expenses.csv
│       └── generated_movements.csv
│
├── processed/
│   ├── customers.parquet
│   ├── customer_invoices.parquet
│   ├── suppliers.parquet
│   ├── supplier_invoices.parquet
│   ├── cash_movements.parquet
│   └── calendar.parquet
│
├── gold/
│   ├── gold_invoice_risk.parquet
│   ├── gold_customer_segmentation.parquet
│   └── gold_daily_cashflow.parquet
│
└── metadata/
    ├── simulation_config.json
    ├── data_quality_report.json
    ├── dataset_lineage.json
    └── data_dictionary.json
```

---

### 3.1. Capa *raw*
La capa *raw* contendrá los datos tal como se reciben o generan por primera vez.

Se dividirá en:
*   **external:** datos descargados de fuentes externas.
*   **synthetic:** primera salida del generador de datos sintéticos.

Sus características serán:
*   No se modificarán los datos originales.
*   Se conservarán los nombres originales de las columnas.
*   Se mantendrán los formatos originales.
*   No se eliminarán duplicados ni registros incorrectos.
*   Se registrará la fecha y procedencia de cada archivo.

> 💡 **Nota:** Esta capa permitirá repetir todo el procesamiento desde el principio.

---

### 3.2. Capa *processed*
La capa *processed* contendrá los datos después de realizar los siguientes procesos de curación:
*   Normalizar nombres de columnas.
*   Convertir tipos de datos.
*   Limpiar identificadores.
*   Interpretar fechas.
*   Comprobar duplicados.
*   Recalcular métricas temporales.
*   Normalizar categorías.
*   Separar entidades.
*   Construir las relaciones básicas.
*   Incorporar indicadores de procedencia.

Los datos estarán limpios, pero todavía no necesariamente preparados para un modelo concreto. Por ejemplo, `customer_invoices.parquet` contendrá una fila por factura, pero no todas las variables históricas del cliente necesarias para el modelo.

---

### 3.3. Capa *gold*
La capa *gold* será la capa final de preparación de datos. Cada fichero estará diseñado para un uso concreto:
*   Modelo de riesgo de retraso.
*   Segmentación de clientes.
*   Previsión de tesorería.
*   Dashboard.
*   Informe final.

Los datasets de esta capa no serán simples copias de los datos procesados. Incluirán variables derivadas, agregaciones, objetivos predictivos y características preparadas para su consumo final.

---

### 3.4. Capa *metadata*
La carpeta *metadata* permitirá documentar exhaustivamente los procesos:
*   Cómo se generaron los datos sintéticos.
*   Qué versiones de datos se utilizaron.
*   Qué reglas de limpieza se aplicaron.
*   Resultados de controles de calidad.
*   Procedencia de cada campo (lineaje).
*   Diccionario de datos.
*   Parámetros y semilla de la simulación.

Esto será especialmente importante para diferenciar claramente los datos reales de los sintéticos.


## 4. Definición de la capa gold
La capa *gold* estará formada inicialmente por tres datasets.

---

### 4.1. gold_invoice_risk.parquet

#### Descripción funcional
Dataset preparado para analizar y predecir el retraso en el pago de cada factura. Contendrá las características originales conocidas en la fecha de emisión de la factura y variables históricas calculadas únicamente con facturas anteriores del mismo cliente.

*   **Granularidad:** Una fila por factura de cliente.
*   **Número aproximado de registros:** Entre 2.400 y 2.466 registros. El dataset original contiene 2.466 facturas; la cifra final dependerá de si se detectan registros inválidos durante la limpieza.
*   **Clave primaria:** `invoice_id`

#### Campos principales

| Campo | Tipo esperado | Descripción |
| :--- | :--- | :--- |
| `invoice_id` | string | Identificador único de factura |
| `customer_id` | string | Identificador del cliente |
| `country_code` | category/string | Código de país o zona |
| `invoice_date` | datetime | Fecha de emisión |
| `due_date` | datetime | Fecha de vencimiento |
| `settled_date` | datetime | Fecha real de cobro; solo se usa para construir el objetivo |
| `invoice_amount` | float64 | Importe de la factura |
| `disputed` | boolean | Indica si existió disputa |
| `paperless_bill` | category | Papel o factura electrónica |
| `payment_term_days` | int16 | Días entre emisión y vencimiento |
| `days_to_settle` | int16 | Días desde emisión hasta cobro |
| `days_delay_signed` | int16 | Diferencia firmada entre liquidación y vencimiento |
| `days_late` | int16 | Días de retraso, con mínimo cero |
| `late_payment` | boolean/int8 | Variable objetivo: pago posterior al vencimiento |
| `invoice_month` | int8 | Mes de emisión |
| `invoice_quarter` | int8 | Trimestre de emisión |
| `invoice_weekday` | int8 | Día de la semana |
| `customer_previous_invoices` | int32 | Número de facturas anteriores |
| `customer_previous_late_rate` | float64 | Porcentaje histórico de retrasos |
| `customer_previous_avg_delay` | float64 | Retraso medio anterior |
| `customer_previous_max_delay` | float64 | Máximo retraso anterior |
| `customer_previous_dispute_rate` | float64 | Proporción histórica de disputas |
| `amount_vs_customer_average` | float64 | Importe frente a la media histórica del cliente |

#### Variable objetivo principal
*   `late_payment = 1` si `settled_date > due_date`
*   `late_payment = 0` si `settled_date <= due_date`

> 💡 **Nota sobre el target:** Esta variable será preferible a `late_30_days`. En la copia revisada, 877 facturas se pagan después del vencimiento (~35,6 %), mientras que únicamente ocho superan los 30 días de retraso. Utilizar 30 días como objetivo produciría un problema de clasificación extremadamente desequilibrado.

**Objetivos secundarios de regresión:**
*   `days_to_settle`
*   `days_late`

#### ⚠️ Precaución sobre fuga de información (*Data Leakage*)
Los campos siguientes **no podrán utilizarse** como variables predictoras (solo se usarán para crear el objetivo y evaluar el modelo):
*   `settled_date`
*   `days_to_settle`
*   `days_delay_signed`
*   `days_late`
*   Cualquier variable calculada después del pago.

*Las variables históricas del cliente deberán calcularse con ventanas acumuladas desplazadas, de forma que cada factura utilice exclusivamente información disponible antes de su emisión.*

#### Fases que consumirán el dataset
*   EDA de facturas y pagos.
*   Clasificación del riesgo de retraso.
*   Regresión de días hasta el cobro.
*   Explicabilidad del modelo.
*   Priorización de recobros.
*   Dashboard de facturas de riesgo.
*   Informe final.

---

### 4.2. gold_customer_segmentation.parquet

#### Descripción funcional
Dataset agregado a nivel de cliente para analizar patrones de comportamiento y construir segmentos de clientes.

*   **Granularidad:** Una fila por cliente.
*   **Número aproximado de registros:** Aproximadamente 100 registros.
*   **Clave primaria:** `customer_id`

#### Campos principales

| Campo | Tipo esperado | Descripción |
| :--- | :--- | :--- |
| `customer_id` | string | Identificador del cliente |
| `country_code` | category/string | País o zona principal |
| `first_invoice_date` | datetime | Primera factura observada |
| `last_invoice_date` | datetime | Última factura observada |
| `customer_tenure_days` | int32 | Días entre primera y última factura |
| `invoice_count` | int32 | Número total de facturas |
| `total_invoiced` | float64 | Importe total facturado |
| `average_invoice_amount` | float64 | Importe medio |
| `median_invoice_amount` | float64 | Importe mediano |
| `late_invoice_count` | int32 | Facturas pagadas tarde |
| `late_payment_rate` | float64 | Porcentaje de retrasos |
| `average_days_late` | float64 | Retraso medio |
| `maximum_days_late` | int16 | Máximo retraso |
| `average_days_to_settle` | float64 | Tiempo medio hasta el cobro |
| `dispute_rate` | float64 | Proporción de facturas disputadas |
| `electronic_invoice_rate` | float64 | Proporción de facturas electrónicas |
| `recent_late_payment_rate` | float64 | Retraso en las facturas más recientes |
| `payment_behavior_trend` | float64 | Evolución reciente del retraso |

#### Variables especialmente relevantes
No tendrá inicialmente una variable objetivo supervisada. Las principales variables de segmentación serán:
*   Volumen total facturado.
*   Frecuencia de facturación.
*   Importe medio.
*   Porcentaje de facturas tardías.
*   Retraso medio.
*   Retraso máximo.
*   Tasa de disputas.
*   Tendencia reciente.

> 📈 **Nota:** En una fase posterior se añadirá el campo `customer_cluster`, el cual será el resultado del algoritmo de clustering y no una variable original.

#### Fases que consumirán el dataset
*   EDA de clientes.
*   Segmentación mediante clustering.
*   Perfilado de grupos.
*   Dashboard de clientes.
*   Priorización comercial y de recobro.
*   Informe de comportamiento de pago.

---

### 4.3. gold_daily_cashflow.parquet

#### Descripción funcional
Dataset diario de tesorería construido mediante la combinación de:
*   Cobros reales de clientes.
*   Pagos sintéticos a proveedores.
*   Gastos recurrentes sintéticos.
*   Impuestos simulados.
*   Cuotas de financiación simuladas.
*   Saldo bancario inicial simulado.

Servirá para analizar la evolución de caja y entrenar modelos sencillos de previsión de tesorería.

*   **Granularidad:** Una fila por fecha.
*   **Número aproximado de registros:** Entre 730 y 800 registros diarios. El número exacto dependerá del intervalo final cubierto por los pagos sintéticos (el histórico real disponible cubre aprox. 2 años).
*   **Clave primaria:** `date`

#### Campos principales

| Campo | Tipo esperado | Descripción |
| :--- | :--- | :--- |
| `date` | datetime | Fecha |
| `opening_balance` | float64 | Saldo inicial del día |
| `real_customer_receipts` | float64 | Cobros reales de clientes |
| `synthetic_supplier_payments` | float64 | Pagos sintéticos a proveedores |
| `synthetic_payroll` | float64 | Nóminas simuladas |
| `synthetic_social_costs` | float64 | Costes sociales simulados |
| `synthetic_rent` | float64 | Alquiler simulado |
| `synthetic_utilities` | float64 | Suministros simulados |
| `synthetic_taxes` | float64 | Impuestos simulados |
| `synthetic_loan_payments` | float64 | Cuotas de financiación |
| `other_synthetic_outflows` | float64 | Otras salidas |
| `total_cash_in` | float64 | Entradas totales |
| `total_cash_out` | float64 | Salidas totales |
| `net_cash_flow` | float64 | Flujo neto diario |
| `closing_balance` | float64 | Saldo final |
| `weekday` | int8 | Día de la semana |
| `month` | int8 | Mes |
| `quarter` | int8 | Trimestre |
| `is_month_end` | boolean | Indicador de fin de mes |
| `balance_lag_1` | float64 | Saldo del día anterior |
| `balance_lag_7` | float64 | Saldo de hace siete días |
| `cash_in_rolling_7` | float64 | Entradas acumuladas de siete días |
| `cash_out_rolling_7` | float64 | Salidas acumuladas de siete días |
| `cash_in_rolling_30` | float64 | Entradas acumuladas de treinta días |
| `cash_out_rolling_30` | float64 | Salidas acumuladas de treinta días |
| `balance_t_plus_7` | float64 | Saldo futuro a siete días |
| `balance_t_plus_30` | float64 | Saldo futuro a treinta días |
| `liquidity_stress_next_7d` | boolean/int8 | Tensión prevista en siete días |
| `liquidity_stress_next_30d` | boolean/int8 | Tensión prevista en treinta días |
| `data_origin` | category | Real, sintético o mixto |

#### Variables objetivo
*   **Para regresión:** `balance_t_plus_7` y `balance_t_plus_30`
*   **Para clasificación:** `liquidity_stress_next_7d` y `liquidity_stress_next_30d`

> 📊 **Criterio de tensión de liquidez:** Se definirá inicialmente como `1` si el saldo cae por debajo del umbral configurado, y `0` en caso contrario.
> El umbral podrá ser cero, un saldo mínimo absoluto o un porcentaje del gasto mensual medio. La definición definitiva se guardará en `simulation_config.json`.

#### Fases que consumirán el dataset
*   EDA de tesorería.
*   Análisis temporal.
*   Modelos de previsión.
*   Detección de tensión de liquidez.
*   Construcción de escenarios.
*   Dashboard financiero.
*   Informe final.

# Diseño y Arquitectura de Datos: Relaciones y Modelado

## 5. Relaciones entre los datos
El proyecto utilizará varias tablas relacionadas para conformar el modelo de datos.

---

### 5.1. Esquema principal
A continuación se detalla la cardinalidad y relaciones lógicas entre las entidades del sistema:

```text
customers.customer_id
        1
        │
        └─── N  customer_invoices.customer_id

suppliers.supplier_id
        1
        │
        └─── N  supplier_invoices.supplier_id

customer_invoices.invoice_id
        1
        │
        └─── 1  customer_receipts.invoice_id

supplier_invoices.supplier_invoice_id
        1
        │
        └─── 1  supplier_payments.supplier_invoice_id

calendar.date
        1
        │
        └─── N  cash_movements.date
```

---

### 5.2. Tablas principales

*   **`customers`**
    *   **Descripción:** Una fila por cliente.
    *   **Clave primaria:** `customer_id`
*   **`customer_invoices`**
    *   **Descripción:** Una fila por factura emitida a clientes.
    *   **Claves:** `invoice_id` (PK), `customer_id` (FK)
*   **`customer_receipts`**
    *   **Descripción:** Una fila por cobro.
    *   **Comentario estructural:** En el dataset inicial cada factura tiene una única fecha de liquidación, por lo que la relación será `1:1`. No obstante, un sistema empresarial real podría tener pagos parciales, en cuyo caso la relación evolucionaría a:
        $$\text{customer\\_invoices } 1 \\longrightarrow N \\text{ customer\\_receipts}$$
*   **`suppliers`**
    *   **Descripción:** Una fila por proveedor sintético.
    *   **Clave primaria:** `supplier_id`
*   **`supplier_invoices`**
    *   **Descripción:** Una fila por factura de proveedor.
    *   **Claves:** `supplier_invoice_id` (PK), `supplier_id` (FK)
*   **`cash_movements`**
    *   **Descripción:** Una fila por movimiento de caja. Contendrá tanto entradas como salidas.
    *   **Campos clave:** `movement_id`, `date`, `amount`, `movement_type`, `reference_id`, `data_origin`
*   **`calendar`**
    *   **Descripción:** Una fila por fecha para dimensiones temporales.
    *   **Clave primaria:** `date`

---

### 5.3. Joins y agregaciones necesarias

#### Joins Operacionales
*   **Facturas y clientes:**
    ```sql
    SELECT * FROM customer_invoices
    LEFT JOIN customers ON customer_invoices.customer_id = customers.customer_id;
    ```
*   **Facturas y cobros:**
    ```sql
    SELECT * FROM customer_invoices
    LEFT JOIN customer_receipts ON customer_invoices.invoice_id = customer_receipts.invoice_id;
    ```
*   **Facturas de proveedor y proveedores:**
    ```sql
    SELECT * FROM supplier_invoices
    LEFT JOIN suppliers ON supplier_invoices.supplier_id = suppliers.supplier_id;
    ```
*   **Movimientos y calendario:**
    ```sql
    SELECT * FROM cash_movements
    LEFT JOIN calendar ON cash_movements.date = calendar.date;
    ```

#### Agregaciones requeridas
1.  **Agregaciones por cliente:** Agrupar facturas por `customer_id` para calcular métricas como: número de facturas, importe total, retraso medio, porcentaje de retrasos, tasa de disputas y comportamiento reciente.
2.  **Agregaciones diarias:** Agrupar movimientos por `date` para calcular: entradas diarias, salidas diarias, flujo neto, saldo de cierre y acumulados móviles (ventanas rodantes).

---

### 5.4. Posibles relaciones N:M (Muchos a Muchos)
La versión inicial **no** contendrá relaciones de tipo Muchos a Muchos ($N:M$). Sin embargo, en datos bancarios o ERPs reales podría ocurrir que:
*   Un mismo cobro liquide varias facturas.
*   Una única factura sea pagada mediante varios movimientos parciales.
*   Un pago consolidado agrupe varias facturas de proveedores distintos.

> 🛠️ **Mitigación arquitectónica:** En dicho escenario se requerirá una tabla puente llamada **`payment_allocations`** con la siguiente estructura básica de campos: `movement_id`, `invoice_id`, `allocated_amount`.

---

### 5.5. Problemas y desafíos al combinar las fuentes
Durante el proceso de integración se prevén los siguientes puntos de dolor:
*   La fuente de datos real no viene con una tabla de entidades de clientes normalizada y separada.
*   Toda la información referente a proveedores será puramente sintética.
*   Los importes monetarios carecen de un código de divisa explícito e identificado (ej. ISO 4217).
*   Las fechas originales están registradas en formatos ambiguos o en formato estadounidense (MM/DD/YYYY).
*   Los códigos geográficos de país pueden no mapear directamente con el estándar ISO 3166-1.
*   No se cuenta con un proceso automatizado o real de conciliación bancaria.
*   Los conjuntos reales y simulados cubren conceptos radicalmente diferentes en el negocio.
*   La distribución en el tiempo de los gastos sintéticos (nóminas, suministros fijados) podría sesgar e introducir estacionalidad artificial en el flujo de caja.
*   Existencia de días huérfanos o fines de semana sin movimientos registrados.
*   Riesgo de colisión de identificadores clave (IDs) entre los registros generados sintéticamente y los reales.

#### Trazabilidad del origen de datos
Para mitigar la mezcla de datos y mantener el linaje claro, cada tabla incluirá de forma obligatoria el campo **`data_origin`**, restringido a los siguientes valores categóricos:
*   `REAL`: Datos verídicos provenientes del sistema de origen.
*   `SYNTHETIC`: Datos simulados por el motor de generación.
*   `DERIVED`: Métricas y variables calculadas post-procesamiento.
*   `MIXED`: Agregaciones o filas híbridas que consolidan componentes reales y simulados.


# 6. Diccionario de datos inicial

## 6.1. Facturas de clientes
| Campo | Tipo | Descripción | Origen |
| :--- | :--- | :--- | :--- |
| invoice_id | string | Identificador único de factura | Real |
| customer_id | string | Identificador del cliente | Real |
| country_code | string/category | Código de país o zona | Real |
| invoice_date | datetime | Fecha de emisión | Real |
| due_date | datetime | Fecha de vencimiento | Real |
| settled_date | datetime | Fecha de pago | Real |
| invoice_amount | float64 | Importe facturado | Real |
| disputed | boolean | Existencia de disputa | Real |
| paperless_bill | category | Papel o electrónica | Real |
| days_to_settle | int16 | Días entre emisión y cobro | Derivado/real |
| days_delay_signed | int16 | Diferencia entre pago y vencimiento | Derivado |
| days_late | int16 | Retraso con mínimo igual a cero | Derivado |
| late_payment | boolean | Pago posterior al vencimiento | Derivado |

## 6.2. Variables históricas de cliente
| Campo | Tipo | Descripción | Origen |
| :--- | :--- | :--- | :--- |
| customer_previous_invoices | int32 | Facturas anteriores del cliente | Derivado |
| customer_previous_late_rate | float64 | Porcentaje previo de retrasos | Derivado |
| customer_previous_avg_delay | float64 | Retraso medio anterior | Derivado |
| customer_previous_max_delay | float64 | Retraso máximo anterior | Derivado |
| customer_previous_dispute_rate | float64 | Tasa previa de disputas | Derivado |
| amount_vs_customer_average | float64 | Factura respecto al importe histórico medio | Derivado |

## 6.3. Facturas y pagos de proveedores
| Campo | Tipo | Descripción | Origen |
| :--- | :--- | :--- | :--- |
| supplier_id | string | Identificador del proveedor | Sintético |
| supplier_invoice_id | string | Identificador de factura | Sintético |
| supplier_category | category | Tipo de proveedor o gasto | Sintético |
| invoice_date | datetime | Fecha de factura | Sintético |
| due_date | datetime | Fecha de vencimiento | Sintético |
| payment_date | datetime | Fecha de pago | Sintético |
| payment_terms | int16 | Plazo de pago | Sintético |
| invoice_amount | float64 | Importe | Sintético |

## 6.4. Movimientos de tesorería
| Campo | Tipo | Descripción | Origen |
| :--- | :--- | :--- | :--- |
| movement_id | string | Identificador del movimiento | Real/sintético |
| date | datetime | Fecha del movimiento | Real/sintético |
| amount | float64 | Importe con signo | Real/sintético |
| direction | category | Entrada o salida | Derivado |
| movement_type | category | Cobro, proveedor, nómina, etc. | Derivado |
| reference_id | string | Factura o gasto relacionado | Real/sintético |
| data_origin | category | Procedencia | Derivado |

## 6.5. Tesorería diaria
| Campo | Tipo | Descripción | Origen |
| :--- | :--- | :--- | :--- |
| date | datetime | Fecha | Derivado |
| opening_balance | float64 | Saldo inicial | Derivado |
| total_cash_in | float64 | Entradas del día | Derivado |
| total_cash_out | float64 | Salidas del día | Derivado |
| net_cash_flow | float64 | Flujo neto | Derivado |
| closing_balance | float64 | Saldo final | Derivado |
| balance_t_plus_7 | float64 | Saldo dentro de siete días | Objetivo |
| balance_t_plus_30 | float64 | Saldo dentro de treinta días | Objetivo |
| liquidity_stress_next_7d | boolean | Alerta a siete días | Objetivo |
| liquidity_stress_next_30d | boolean | Alerta a treinta días | Objetivo |


# 7. Problemas de calidad esperados

## 7.1. Valores nulos
La copia pública inicial no presenta valores nulos en las doce columnas originales. Sin embargo, la ausencia de nulos no garantiza que todos los valores sean correctos.
Podrían aparecer nulos durante:
* conversiones de fechas incorrectas;
* joins sin correspondencia;
* creación de variables históricas;
* primeras facturas de cada cliente;
* generación de lags y ventanas móviles;
* incorporación de datos sintéticos.

La primera factura de cada cliente, por ejemplo, no tendrá un comportamiento histórico anterior.

## 7.2. Duplicados
`invoiceNumber` debería ser único.
Se comprobarán:
* duplicados exactos;
* identificadores repetidos;
* facturas con el mismo cliente, fecha e importe;
* movimientos sintéticos generados dos veces;
* duplicación derivada de joins 1:N.

No se eliminarán registros únicamente porque sus importes y fechas sean iguales. Se exigirá evidencia de que representan la misma factura.

## 7.3. Formato de fechas
Las fechas originales presentan un formato similar a:
`1/26/2013`

Este formato debe interpretarse como mes/día/año.
Utilizar automáticamente `dayfirst=True` produciría fechas incorrectas. La conversión se realizará explícitamente mediante:
`%m/%d/%Y`

## 7.4. Definición de días de retraso
La variable original `DaysLate` no conserva los días negativos de las facturas pagadas antes del vencimiento. Los pagos anticipados aparecen con valor cero.
Por tanto, se recalculará:
`days_delay_signed = settled_date - due_date`

Y después:
`days_late = max(days_delay_signed, 0)`

Esto permitirá distinguir:
* pago anticipado;
* pago en vencimiento;
* pago retrasado.

## 7.5. Plazo de pago constante
En el dataset revisado, la fecha de vencimiento se sitúa treinta días después de la emisión para todas las facturas.
Esto implica que `payment_term_days` no aporta variabilidad y probablemente no será útil como predictor en esta fuente.
También limita la capacidad para estudiar si los plazos de 30, 60 o 90 días influyen en el retraso.

## 7.6. Falta de verdaderos impagos
Todas las facturas tienen una fecha de liquidación.
Por tanto, no hay ejemplos de:
* facturas permanentemente abiertas;
* insolvencias;
* créditos incobrables;
* bajas contables;
* concursos de acreedores.

El modelo no podrá afirmar que predice impago definitivo. Solo podrá predecir retraso.

## 7.7. Desequilibrio de clases
Una definición de retraso superior a treinta días produciría muy pocos casos positivos.
Por este motivo, se utilizará como objetivo principal cualquier pago posterior al vencimiento.
También se podrán analizar umbrales secundarios, por ejemplo:
* retraso superior a 5 días
* retraso superior a 10 días

Siempre que exista una cantidad suficiente de observaciones positivas.

## 7.8. Unidades monetarias
El campo de importe no identifica claramente la divisa.
No se asumirirá que los importes están expresados en euros.
Los datos sintéticos utilizarán la misma unidad monetaria abstracta para conservar la coherencia interna.

## 7.9. Datos antiguos
Las facturas se concentran aproximadamente entre 2012 y 2013.
El comportamiento de pago puede no representar plenamente:
* medios de pago actuales;
* facturación electrónica moderna;
* condiciones económicas recientes;
* comportamiento de empresas españolas;
* tipos de interés actuales.

El proyecto demostrará una metodología, pero no podrá presentarse como un modelo directamente desplegable en una empresa actual sin reentrenamiento.

## 7.10. Sesgo de cobertura
El dataset contiene:
* 100 clientes;
* cinco códigos de país o zona;
* un único tipo general de operativa;
* facturas que finalmente fueron cobradas.

Esto puede provocar que el modelo aprenda patrones muy específicos de la fuente.

## 7.11. Valores extremos
Se revisararán:
* importes anormalmente altos o bajos;
* retrasos extremos;
* clientes con muy pocas facturas;
* clientes con una tasa de retraso del 0 % o 100 %;
* días con grandes movimientos sintéticos;
* saldos de caja excesivamente negativos o positivos.

Los outliers no se eliminarán automáticamente. Primero se determinará si representan errores o casos válidos.

## 7.12. Riesgo de los datos sintéticos
Los resultados de tesorería dependerán de hipótesis como:
* porcentaje de costes sobre ventas;
* frecuencia de las facturas de proveedores;
* importe de nóminas;
* fecha de pago de impuestos;
* saldo inicial;
* distribución temporal de los gastos.

Una configuración incorrecta podría generar una empresa artificialmente solvente o permanentemente insolvente.
Por ello se construirán diferentes escenarios y se almacenarán todos los parámetros utilizados.


# 8. Decisiones de limpieza y transformación previstas

## 8.1. Conservación de los datos originales
El archivo original se conservará sin modificaciones.
Se registrará:
* nombre;
* ruta;
* fecha de descarga;
* número de registros;
* número de columnas;
* hash o suma de comprobación;
* fuente.

## 8.2. Normalización de nombres
Los nombres de columnas pasarán a formato `snake_case`.
Ejemplos:
* `InvoiceDate` → `invoice_date`
* `InvoiceAmount` → `invoice_amount`
* `PaperlessBill` → `paperless_bill`
* `DaysToSettle` → `days_to_settle`

## 8.3. Conversión de fechas
Se utilizará el formato explícito:
`%m/%d/%Y`

Las fechas que no puedan convertirse pasarán temporalmente a nulo y se incluirán en el informe de calidad.

## 8.4. Normalización de categorías
Se estandarizarán campos como:
* `Yes / No` → `True / False`
* `Paper / Electronic` → `PAPER / ELECTRONIC`

Se eliminarán:
* espacios al principio o final;
* diferencias de mayúsculas;
* caracteres innecesarios.

No se traducirán ni reinterpretarán los códigos de país sin una fuente fiable que confirme su significado.

## 8.5. Tratamiento de importes
Los importes se convertirán a número decimal o `float64`.
Se comprobará que:
* no sean nulos;
* sean mayores que cero;
* tengan una precisión máxima de dos decimales;
* utilicen la misma unidad monetaria dentro de la simulación.

Las facturas con importe cero o negativo se considerarán inválidas, salvo que se identifiquen explícitamente como abonos.

## 8.6. Tratamiento de duplicados
Un registro se considerará duplicado cuando:
* tenga el mismo `invoice_id`;
* o sea idéntico en todas las columnas relevantes.

Si dos facturas tienen el mismo cliente, fecha e importe, pero identificadores distintos, se mantendrán hasta comprobar su naturaleza.

## 8.7. Recalculo de variables temporales
Se calcularán de nuevo:
* `payment_term_days = due_date - invoice_date`
* `days_to_settle_calc = settled_date - invoice_date`
* `days_delay_signed = settled_date - due_date`
* `days_late = max(days_delay_signed, 0)`

Los resultados se compararán con las columnas originales para detectar inconsistencias.

## 8.8. Construcción de la variable objetivo
La variable principal será:
`late_payment = settled_date > due_date`

No se utilizará inicialmente `late_30_days` como objetivo principal debido a la escasez de casos positivos.

## 8.9. Variables históricas del cliente
Se crearán utilizando únicamente facturas anteriores:
* número de facturas previas;
* tasa previa de retrasos;
* retraso medio previo;
* máximo retraso previo;
* tasa previa de disputas;
* importe medio anterior;
* tiempo desde la factura anterior.

Para evitar fuga de información se utilizarán acumulados desplazados:
`expanding().mean().shift(1)`

La factura actual nunca formará parte de sus propias variables históricas.

## 8.10. Valores nulos en variables históricas
En la primera factura de cada cliente:
`customer_previous_invoices = 0`

Las tasas y medias previas podrán:
* rellenarse con cero cuando su interpretación sea ausencia de histórico;
* acompañarse de una variable `is_new_customer`;
* imputarse con la media del conjunto solo cuando sea metodológicamente adecuado.

No se imputarán objetivos desconocidos.

## 8.11. Generación de datos sintéticos
La simulación utilizará:
* una semilla fija;
* parámetros centralizados;
* identificadores propios;
* reglas documentadas;
* fechas coherentes;
* trazabilidad por registro.

Ejemplo:
* `SUP_001`
* `PINV_000001`
* `EXP_000001`

Cada registro incluirá:
`is_synthetic = True`

o:
`data_origin = SYNTHETIC`

## 8.12. Agregaciones de tesorería
Los movimientos se agruparán diariamente:
* `total_cash_in` = suma de movimientos positivos
* `total_cash_out` = valor absoluto de movimientos negativos
* `net_cash_flow = total_cash_in - total_cash_out`
* `closing_balance = opening_balance + net_cash_flow`

Se generarán también ventanas:
* siete días;
* treinta días;
* noventa días, si el histórico lo permite.

## 8.13. Criterios de registro válido
Una factura será válida cuando:
* `invoice_id` no sea nulo;
* `customer_id` no sea nulo;
* `invoice_date` sea válida;
* `due_date` sea válida;
* `settled_date` sea válida;
* el importe sea mayor que cero;
* el vencimiento no sea anterior a la emisión;
* el cobro no sea anterior a la emisión;
* el identificador no esté duplicado.

Un movimiento sintético será válido cuando:
* tenga identificador único;
* posea fecha válida;
* tenga importe distinto de cero;
* su categoría exista en el catálogo;
* su procedencia esté identificada;
* su referencia exista cuando sea necesaria.

## 8.14. División temporal
La división de entrenamiento, validación y prueba será cronológica.
Ejemplo:
* 70 % de fechas más antiguas → entrenamiento
* 15 % intermedio → validación
* 15 % más reciente → prueba

No se utilizará inicialmente una división aleatoria porque podría introducir información futura en el entrenamiento.


# 9. Riesgos del modelo de datos

## 9.1. Parte más clara
La parte más clara es el modelo de facturas y clientes.
Existe una relación directa entre:
* cliente
* factura
* fecha de vencimiento
* fecha real de pago
* retraso

La granularidad es sencilla y la variable objetivo puede construirse directamente a partir de las fechas.
También está clara la creación del dataset agregado de clientes.

## 9.2. Parte que genera más incertidumbre
La mayor incertidumbre corresponde a la previsión integral de tesorería.
Las entradas de clientes proceden de datos reales, pero las salidas, el saldo inicial y los compromisos financieros serán sintéticos.
En consecuencia, la serie de caja no representará una empresa real completa, sino una simulación coherente construida con fines académicos.

## 9.3. Fuente que puede dar más problemas
La fuente más problemática será la tabla de movimientos sintéticos.
No por errores técnicos, sino porque su comportamiento dependerá de las hipótesis seleccionadas.
También pueden generar limitaciones:
* la antigüedad del dataset real;
* la falta de impagos definitivos;
* el plazo de vencimiento constante;
* la falta de divisa;
* el escaso número de clientes;
* el histórico temporal de aproximadamente dos años.

## 9.4. Consecuencias de no construir la capa gold prevista
Si no fuera posible construir `gold_daily_cashflow.parquet` con suficiente calidad, no tendría sentido entrenar un modelo complejo de previsión de tesorería.
En ese caso se mantendrían:
* el modelo de riesgo de retraso;
* la predicción de días hasta el cobro;
* la segmentación de clientes;
* un dashboard de cuentas a cobrar.

La tesorería podría presentarse mediante una simulación determinista y diferentes escenarios, sin afirmar que existe un modelo predictivo validado sobre datos empresariales reales.

## 9.5. Alternativa simplificada
La alternativa mínima viable sería trabajar únicamente con dos datasets gold:
* `gold_invoice_risk.parquet`
* `gold_customer_segmentation.parquet`

El proyecto se reformularía como:
> Sistema predictivo de retraso en cobros y priorización de clientes para recobro.

Posteriormente, las probabilidades de cobro podrían utilizarse en una simulación sencilla de tesorería:
`saldo futuro = saldo inicial + cobros esperados ajustados por probabilidad - gastos fijos simulados`

Esta alternativa mantendría una utilidad empresarial clara y reduciría considerablemente el riesgo metodológico.

## 9.6. Valoración final
El modelo de datos propuesto es viable para un proyecto académico de Data Science siempre que se mantenga una distinción explícita entre:
* datos reales de cuentas a cobrar

y:
* datos sintéticos de pagos y tesorería

La parte con mayor validez predictiva será el modelo de retraso de facturas.
La previsión de tesorería deberá interpretarse como una demostración de arquitectura, integración y simulación financiera, no como una estimación directamente aplicable a una empresa real sin disponer de sus movimientos bancarios y compromisos de pago.
