# Treasury Risk AI

Sistema predictivo de tesorería y riesgo de retraso en el cobro.

Treasury Risk AI es un MVP orientado a ayudar a equipos financieros a identificar qué facturas presentan mayor riesgo de retraso, priorizar la gestión de cobros y analizar cómo distintos escenarios pueden afectar a la liquidez de la empresa.

---

## Problema

Una empresa puede generar ventas y seguir sufriendo tensiones de liquidez si sus clientes pagan más tarde de lo previsto.

Los departamentos financieros necesitan responder principalmente a dos preguntas:

1. ¿Qué facturas requieren mayor atención?
2. ¿Qué impacto podrían tener los retrasos sobre la tesorería?

Este proyecto conecta ambas dimensiones mediante un modelo predictivo de riesgo de retraso y un simulador de tesorería.

---

## Propuesta de valor

Treasury Risk AI permite:

- estimar el riesgo de retraso de cada factura;
- priorizar la cartera de cobros;
- combinar riesgo y exposición monetaria;
- identificar las facturas más relevantes para el equipo financiero;
- simular retrasos adicionales en los cobros;
- medir el deterioro potencial de la liquidez;
- estimar posibles necesidades adicionales de financiación;
- exportar una cartera priorizada para su gestión operativa.

---

## Aplicación

El MVP está desarrollado con **Streamlit** y está dividido en cuatro módulos principales.

### Dashboard

Visión ejecutiva de la situación financiera:

- liquidez final;
- liquidez mínima;
- cartera analizada;
- exposición prioritaria;
- cobros acumulados;
- pagos acumulados;
- generación neta de caja;
- facturas prioritarias.

También incluye la evolución temporal de la tesorería y una visión general de la distribución del riesgo.

### Riesgo de cobros

Permite analizar y priorizar la cartera utilizando diferentes criterios:

- mayor riesgo;
- mayor importe;
- mayor exposición ajustada por riesgo.

La cartera puede filtrarse por cliente, score mínimo e importe.

La selección resultante puede exportarse a CSV como lista de trabajo para el equipo de cobros.

### Simulador de escenarios

Permite evaluar cómo distintos retrasos podrían afectar a la liquidez.

El usuario puede modificar:

- porcentaje de facturas afectadas;
- criterio de selección;
- retraso adicional;
- nivel de colchón inicial de caja.

También se incluyen escenarios rápidos:

- Moderado;
- Adverso;
- Severo.

El simulador calcula:

- liquidez mínima;
- deterioro máximo;
- días con caja negativa;
- necesidad adicional de financiación.

### Modelo y metodología

Resume el enfoque predictivo, la validación temporal y las principales limitaciones del MVP.

---

## Modelo predictivo

El objetivo del modelo es estimar si una factura se cobrará después de su fecha de vencimiento.

La variable objetivo se define como:

```text
late_payment = 1 si SettledDate > DueDate
```

El modelo final seleccionado es una **Regresión Logística**, elegida por su equilibrio entre:

- rendimiento predictivo;
- estabilidad temporal;
- interpretabilidad;
- facilidad de implementación.

El modelo utiliza **34 variables**, incluyendo:

- características de la factura;
- variables temporales;
- comportamiento histórico del cliente;
- frecuencia histórica de retrasos;
- duración histórica de los retrasos;
- información de pagos anteriores.

Todas las variables históricas se construyen respetando la fecha de emisión de la factura para evitar el uso de información futura.

---

## Validación temporal

La evaluación se realiza mediante divisiones cronológicas en lugar de una partición aleatoria.

| Periodo | Facturas |
|---|---:|
| Entrenamiento | 1.719 |
| Validación | 381 |
| Test | 366 |

Resultados principales:

| Métrica | Validación | Test |
|---|---:|---:|
| ROC-AUC | 0.904 | 0.859 |
| PR-AUC | 0.802 | 0.693 |

El conjunto de test se mantiene separado hasta la evaluación final.

El modelo se utiliza principalmente como herramienta de **ranking y priorización**, no como una probabilidad perfectamente calibrada.

---

## Integración riesgo - tesorería

El MVP conecta el score predictivo con un modelo de tesorería.

La lógica principal es:

```text
Datos históricos
        ↓
Feature engineering
        ↓
Modelo de riesgo
        ↓
Score por factura
        ↓
Priorización de cartera
        ↓
Escenarios de retraso
        ↓
Impacto sobre liquidez
```

Además del riesgo individual de una factura, se utiliza una medida de exposición ajustada:

```text
score de riesgo × importe de la factura
```

Esta métrica se utiliza como criterio de ranking y no debe interpretarse como una pérdida esperada.

---

## Simulación de tesorería

Los cobros proceden del histórico real del dataset.

Las salidas de caja utilizadas para construir el entorno financiero son sintéticas e incluyen conceptos como:

- proveedores;
- nóminas;
- seguridad social;
- alquiler;
- suministros;
- software y administración;
- pagos financieros;
- impuestos.

El simulador debe interpretarse como una herramienta de **stress testing de liquidez**, no como una predicción completa del cash flow futuro.

Los importes se expresan en las unidades monetarias originales del dataset.

---

## Dataset

El proyecto utiliza un histórico de facturas con aproximadamente:

- **2.466 facturas**;
- **100 clientes**;
- aproximadamente **dos años de histórico**.

El dataset contiene información sobre:

- fecha de emisión;
- fecha de vencimiento;
- importe;
- cliente;
- fecha final de cobro;
- comportamiento histórico de pago.

El dataset no contiene impagos definitivos suficientes para modelarlos, por lo que el problema se redefine como **riesgo de retraso en el cobro**.

---

## Estructura del proyecto

```text
.
├── app.py
│
├── app_pages/
│   ├── dashboard.py
│   ├── risk.py
│   ├── scenarios.py
│   └── methodology.py
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── scenarios.py
│   └── ui.py
│
├── data/
│   ├── gold/
│   ├── metadata/
│   ├── processed/
│   ├── raw/
│   └── synthetic/
│
├── notebooks/
│   ├── 01_eda_accounts.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_baseline.ipynb
│   ├── 04_model_interpretability.ipynb
│   ├── 05_model_comparison.ipynb
│   ├── 06_model_calibration.ipynb
│   ├── 07_final_evaluation.ipynb
│   ├── 08_cashflow_simulation.ipynb
│   ├── 09_treasury_analysis.ipynb
│   └── 10_risk_treasury_integration.ipynb
│
├── docs/
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Ejecución local

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd sistema_predictivo_tesoreria_y_riesgo_de_impago
```

### 2. Crear un entorno virtual

Windows:

```powershell
py -3.12 -m venv .venv
```

Activarlo:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación estará disponible por defecto en:

```text
http://localhost:8501
```

---

## Demo

🚀 **Aplicación:** [Treasury Risk AI](https://sistemapredictivotersoreriayriesgo-x22tqke3qzfqwpmakbu3gk.streamlit.app/)


## Tecnologías

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- LightGBM
- PyArrow
- Plotly
- Matplotlib
- Streamlit
- Jupyter

---

## Principios metodológicos

El proyecto se ha desarrollado siguiendo varios principios:

- separación temporal entre entrenamiento, validación y test;
- prevención de data leakage;
- variables históricas construidas con lógica as-of;
- evaluación out-of-sample;
- test final no utilizado para reajustar el modelo;
- separación explícita entre datos reales y datos sintéticos;
- interpretación empresarial de las métricas predictivas.

---

## Limitaciones

Este proyecto es un MVP y presenta varias limitaciones:

- el dataset es reducido;
- el histórico cubre aproximadamente dos años;
- el modelo predice retraso binario y no el número exacto de días;
- no se modelan impagos definitivos;
- las salidas de caja son sintéticas;
- el score no está perfectamente calibrado como probabilidad;
- la simulación aplica shocks sobre cobros históricos observados;
- el sistema todavía no está conectado a un ERP o sistema contable real.

---

## Roadmap

Para convertir el MVP en una solución productiva, los siguientes pasos serían:

- integración con ERP o sistema de facturación;
- ingestión automática de nuevas facturas;
- scoring periódico de la cartera;
- autenticación y control de usuarios;
- alertas de riesgo;
- integración con información bancaria;
- reentrenamiento periódico del modelo;
- monitorización del rendimiento y drift;
- generación de previsiones de cobro completamente ex-ante;
- despliegue empresarial.

---

## Objetivo del MVP

El objetivo del proyecto no es automatizar las decisiones financieras.

Su propósito es proporcionar una señal anticipada que ayude al equipo financiero a:

**priorizar cobros, entender su exposición y anticipar posibles tensiones de liquidez.**