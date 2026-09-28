import streamlit as st

from src.ui import inject_global_css


st.set_page_config(
    page_title="Treasury Risk AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


inject_global_css()


dashboard_page = st.Page(
    "app_pages/dashboard.py",
    title="Dashboard",
    icon="📊",
    default=True,
)

risk_page = st.Page(
    "app_pages/risk.py",
    title="Riesgo de cobros",
    icon="⚠️",
)

scenarios_page = st.Page(
    "app_pages/scenarios.py",
    title="Simulador",
    icon="📈",
)

methodology_page = st.Page(
    "app_pages/methodology.py",
    title="Modelo",
    icon="🧠",
)


with st.sidebar:

    st.markdown(
        "## Treasury Risk AI"
    )

    st.caption(
        "Anticipación de cobros "
        "y planificación de liquidez."
    )

    st.divider()

    st.markdown(
        "**Sobre este MVP**"
    )

    st.caption(
        "✓ Cobros históricos reales"
    )

    st.caption(
        "✓ Escenarios de tesorería"
    )

    st.caption(
        "✓ Modelo validado temporalmente"
    )


navigation = st.navigation(
    [
        dashboard_page,
        risk_page,
        scenarios_page,
        methodology_page,
    ]
)

navigation.run()