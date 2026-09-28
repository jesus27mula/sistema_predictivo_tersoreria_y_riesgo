import streamlit as st

from src.data_loader import load_app_data



# =========================================================
# DATA
# =========================================================

data = load_app_data()

metadata = data["integration_metadata"]


# =========================================================
# HEADER
# =========================================================

st.title(
    "Modelo y metodología"
)

st.markdown(
    """
    <div class="mvp-subtitle">
        Cómo se construye el score de riesgo y cómo se valida
        antes de utilizarlo para priorizar decisiones de tesorería.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# MENSAJE PRINCIPAL
# =========================================================

st.info(
    "El sistema estima el riesgo de retraso en el momento de emisión "
    "de una factura utilizando únicamente información disponible "
    "hasta ese momento."
)


# =========================================================
# KPIs MODELO
# =========================================================

st.subheader(
    "Rendimiento predictivo"
)

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "ROC-AUC · Validación",
    "0,904",
    border=True,
)

col2.metric(
    "PR-AUC · Validación",
    "0,802",
    border=True,
)

col3.metric(
    "ROC-AUC · Test",
    "0,859",
    border=True,
)

col4.metric(
    "PR-AUC · Test",
    "0,693",
    border=True,
)


st.caption(
    "Validación y test corresponden a periodos temporales posteriores "
    "a los utilizados para entrenar el modelo."
)


# =========================================================
# MODELO
# =========================================================

st.subheader(
    "Modelo utilizado"
)

model_col1, model_col2, model_col3 = st.columns(3)


model_col1.metric(
    "Algoritmo",
    "Logistic Regression",
    border=True,
)

model_col2.metric(
    "Variables",
    "34",
    border=True,
)

model_col3.metric(
    "Objetivo",
    "Retraso en el cobro",
    border=True,
)


with st.container(border=True):

    st.markdown(
        "#### ¿Qué intenta predecir?"
    )

    st.markdown(
        """
        Para cada factura, el modelo estima si el cobro se producirá
        **después de su fecha de vencimiento**.

        La variable objetivo se define como:

        `late_payment = 1` si `SettledDate > DueDate`.
        """
    )


# =========================================================
# METODOLOGÍA TEMPORAL
# =========================================================

st.subheader(
    "Validación temporal"
)

st.markdown(
    """
    La evaluación no utiliza una división aleatoria de las facturas.

    El histórico se divide cronológicamente para reproducir una situación
    más cercana al uso real del sistema:
    """
)


split1, split2, split3 = st.columns(3)


with split1:

    with st.container(border=True):

        st.markdown("### Entrenamiento")

        st.metric(
            "Facturas",
            "1.719",
        )

        st.caption(
            "Información histórica utilizada "
            "para aprender el modelo."
        )


with split2:

    with st.container(border=True):

        st.markdown("### Validación")

        st.metric(
            "Facturas",
            "381",
        )

        st.caption(
            "Periodo posterior utilizado para "
            "evaluar y definir decisiones."
        )


with split3:

    with st.container(border=True):

        st.markdown("### Test")

        st.metric(
            "Facturas",
            "366",
        )

        st.caption(
            "Periodo completamente reservado "
            "para la evaluación final."
        )


# =========================================================
# PRINCIPIOS METODOLÓGICOS
# =========================================================

st.subheader(
    "Principios del sistema"
)


principle1, principle2 = st.columns(2)


with principle1:

    with st.container(border=True):

        st.markdown(
            "#### Información disponible en el momento de decisión"
        )

        st.markdown(
            """
            Las variables históricas se construyen respetando la fecha
            de emisión de cada factura.

            El modelo no utiliza información futura del pago que intenta
            predecir.
            """
        )


    with st.container(border=True):

        st.markdown(
            "#### Evaluación fuera de muestra"
        )

        st.markdown(
            """
            Los scores utilizados para evaluar la integración con tesorería
            son scores **out-of-sample**.

            Esto evita evaluar el sistema utilizando predicciones generadas
            sobre datos con los que el modelo ya fue entrenado.
            """
        )


with principle2:

    with st.container(border=True):

        st.markdown(
            "#### Priorización, no automatización de decisiones"
        )

        st.markdown(
            """
            El score se utiliza para ordenar y priorizar la cartera.

            La decisión final sobre seguimiento, recobro o financiación
            continúa correspondiendo al equipo financiero.
            """
        )


    with st.container(border=True):

        st.markdown(
            "#### Riesgo + exposición"
        )

        st.markdown(
            """
            Una factura con alto riesgo no necesariamente representa
            el mayor impacto financiero.

            Por eso el MVP permite combinar:

            **riesgo estimado × importe de la factura**
            """
        )


# =========================================================
# DATOS
# =========================================================

st.subheader(
    "Datos utilizados"
)

data_col1, data_col2, data_col3 = st.columns(3)


data_col1.metric(
    "Facturas históricas",
    "2.466",
    border=True,
)

data_col2.metric(
    "Clientes",
    "100",
    border=True,
)

data_col3.metric(
    "Periodo",
    "2012 – 2013",
    border=True,
)


st.markdown(
    """
    **Cobros:** proceden del dataset histórico utilizado para el proyecto.

    **Pagos y gastos:** se generan de forma sintética para construir
    el entorno de simulación de tesorería.
    """
)


# =========================================================
# LIMITACIONES
# =========================================================

st.subheader(
    "Limitaciones del MVP"
)


with st.expander(
    "Ver limitaciones metodológicas"
):

    st.markdown(
        """
        - El dataset tiene **2.466 facturas y 100 clientes**, por lo que
            representa una muestra limitada para generalizar a cualquier empresa.

        - El histórico cubre aproximadamente **dos años**.

        - El objetivo predice **retraso sí/no**, no el número exacto de días
            de retraso.

        - El modelo no estima impagos definitivos, ya que el dataset utilizado
            contiene facturas finalmente cobradas.

        - Las salidas de caja utilizadas en el simulador son **sintéticas**.

        - El simulador aplica shocks sobre fechas de cobro observadas.
            Por tanto, debe interpretarse como una herramienta de
            **stress testing**, no como una predicción completa del cash flow futuro.

        - El score sirve principalmente como herramienta de
          **ranking y priorización**, no como una probabilidad perfectamente
                calibrada.
        """
    )


# =========================================================
# CIERRE
# =========================================================

st.success(
    "El objetivo del MVP no es sustituir al equipo financiero, "
    "sino proporcionarle una señal anticipada para priorizar cobros "
    "y evaluar su impacto potencial sobre la liquidez."
)