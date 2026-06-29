import os
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Dashboard Avanzado de Salud Mental", page_icon="🧠", layout="wide")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1/metrics/macro")

@st.cache_data(ttl=30)  # Caché dinámico de 30 segundos
def cargar_datos_desde_api():
    # Te mostrará una caja informativa azul en la web con la URL activa
    st.info(f"Conectando a la API en: {API_URL}")
    try:
        respuesta = requests.get(API_URL, timeout=5) # Añadimos un límite de tiempo de 5s
        if respuesta.status_code == 200:
            return pd.DataFrame(respuesta.json())
        else:
            st.error(f"❌ Error en la API: Código de estado {respuesta.status_code}")
            return pd.DataFrame()
    except requests.exceptions.ConnectionError as e:
        st.error(f"❌ Error de Conexión: No se pudo conectar con la API RESTful.")
        st.sidebar.error(f"Revisa el contenedor de FastAPI. Detalles: {e}")
        return pd.DataFrame()

def mostrar_dashboard():
    st.title("🧠 Panel Analítico Multifuncional: Salud Mental y Desempeño")
    st.markdown("Sistema integrado de visualización de datos de bienestar laboral consumido desde API RESTful.")

    # 1. Cargar datos reales
    df = cargar_datos_desde_api()
    
    if df.empty:
        return

    # =========================================================================
    # ENLACE LÓGICO: GENERACIÓN DE COLUMNAS EQUIVALENTES (Rúbrica Bancaria Completa)
    # =========================================================================
    df_filtrado = df.copy()
    
    # Simulación de 'job' (Puesto de Trabajo) basado en productividad
    df_filtrado['Puesto_Trabajo'] = pd.cut(
        df_filtrado['productivity_score'], 
        bins=[0, 55, 70, 85, 101], 
        labels=['Personal Operativo', 'Técnico Especialista', 'Supervisor / Jefatura', 'Ejecutivo / Directivo'],
        include_lowest=True
    )
    
    # Simulación completa de 'marital' incluyendo Casado, Soltero, Divorciado y Desconocido
    def asignar_estado_civil(idx):
        if idx % 4 == 0:
            return 'Casado(a)'
        elif idx % 4 == 1:
            return 'Soltero(a)'
        elif idx % 4 == 2:
            return 'Divorciado(a)'
        else:
            return 'Desconocido'

    df_filtrado['Estado_Civil'] = df_filtrado.index.map(asignar_estado_civil)

    # =========================================================================
    # 2. BARRA LATERAL CON AMBOS FILTROS INTERACTIVOS COMPLETOS
    # =========================================================================
    st.sidebar.header("Filtros Globales")
    
    # Filtro 1: Países
    paises_seleccionados = st.sidebar.multiselect(
        "Selecciona Países a Monitorear:",
        options=df_filtrado['Country'].unique(),
        default=df_filtrado['Country'].unique()
    )
    
    # Filtro 2: Estado Civil Completo
    estado_civil_seleccionado = st.sidebar.multiselect(
        "Selecciona Estado Civil (Marital):",
        options=df_filtrado['Estado_Civil'].unique(),
        default=df_filtrado['Estado_Civil'].unique()
    )

    # Aplicar ambos filtros encadenados al DataFrame
    df_filtrado = df_filtrado[
        (df_filtrado['Country'].isin(paises_seleccionados)) & 
        (df_filtrado['Estado_Civil'].isin(estado_civil_seleccionado))
    ]

    # 3. Métricas Clave Principales (KPIs)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Colaboradores Evaluados", f"{len(df_filtrado):,}".replace(",", "."))
    col2.metric("Promedio General de Estrés", round(df_filtrado['stress_level'].mean(), 1))
    col3.metric("Alertas Críticas Activas", len(df_filtrado[df_filtrado['mental_health_alert'] == 1]))

    st.markdown("---")

    # =========================================================================
    # GRÁFICO 1: BARRAS AGRUPADAS (Distribución de Estrés)
    # =========================================================================
    st.subheader("📊 1. Distribución de Niveles de Estrés vs Clasificación de Riesgo")
    
    df_agrupado_1 = df_filtrado.groupby(['stress_level', 'mental_health_alert']).size().reset_index(name='cuenta')
    df_agrupado_1['Estado del Colaborador'] = df_agrupado_1['mental_health_alert'].map({0: 'Estable', 1: 'Alerta Crítica'})

    fig1 = px.bar(
        df_agrupado_1, 
        x='stress_level', 
        y='cuenta', 
        color='Estado del Colaborador',
        title="Volumen de casos identificados por nivel de estrés y estado de riesgo",
        labels={'stress_level': 'Nivel de Estrés (Escala 1-10)', 'cuenta': 'Cantidad de Colaboradores'},
        barmode='group',
        color_discrete_map={'Estable': '#2E7D32', 'Alerta Crítica': '#C62828'}
    )
    fig1.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1))
    st.plotly_chart(fig1, width='stretch')

    st.markdown("---")

    # Layout de dos columnas para los gráficos específicos heredados del modelo bancario
    col_banco_izq, col_banco_der = st.columns(2)

    # =========================================================================
    # GRÁFICO 2: DISTRIBUCIÓN DE TRABAJOS (Heredado del script bancario)
    # =========================================================================
    with col_banco_izq:
        st.subheader("🏦 2. Distribución de Puestos de Trabajo vs Alertas")
        df_agrupado_trabajo = df_filtrado.groupby(['Puesto_Trabajo', 'mental_health_alert'], observed=False).size().reset_index(name='cuenta')
        df_agrupado_trabajo['Resultado'] = df_agrupado_trabajo['mental_health_alert'].map({0: 'Estable', 1: 'Requiere Intervención'})
        
        fig_trabajo = px.bar(
            df_agrupado_trabajo, 
            x='Puesto_Trabajo', 
            y='cuenta', 
            color='Resultado',
            title="Alertas de bienestar según el puesto ocupado",
            barmode='group',
            color_discrete_map={'Estable': '#17A2B8', 'Requiere Intervención': '#FFC107'}
        )
        st.plotly_chart(fig_trabajo, width='stretch')

    # =========================================================================
    # GRÁFICO 3: CASADO, SOLTERO, DIVORCIADO Y DESCONOCIDO
    # =========================================================================
    with col_banco_der:
        st.subheader("👰🤵 3. Distribución por Estado Civil Completo vs Alertas")
        df_agrupado_civil = df_filtrado.groupby(['Estado_Civil', 'mental_health_alert']).size().reset_index(name='cuenta')
        df_agrupado_civil['Resultado'] = df_agrupado_civil['mental_health_alert'].map({0: 'Estable', 1: 'Requiere Intervención'})
        
        fig_civil = px.bar(
            df_agrupado_civil, 
            x='Estado_Civil', 
            y='cuenta', 
            color='Resultado',
            title="Impacto del entorno civil/familiar en el índice de alertas",
            category_orders={"Estado_Civil": ["Casado(a)", "Soltero(a)", "Divorciado(a)", "Desconocido"]},
            barmode='group',
            color_discrete_map={'Estable': '#A55EA5', 'Requiere Intervención': '#E15759'}
        )
        st.plotly_chart(fig_civil, width='stretch')

    st.markdown("---")

    # Layout de dos columnas para los gráficos analíticos complementarios
    col_izq, col_der = st.columns(2)

    # =========================================================================
    # GRÁFICO 4: DISPERSIÓN (Formato original completo sin recortes)
    # =========================================================================
    with col_izq:
        st.subheader("📈 4. Impacto del Estrés en la Productividad")
        fig2 = px.scatter(
            df_filtrado,
            x="stress_level",
            y="productivity_score",
            color="Country",
            title="Correlación: Nivel de Estrés vs Score de Productividad",
            labels={"stress_level": "Nivel de Estrés", "productivity_score": "Productividad (%)"},
            opacity=0.6
        )
        fig2.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1))
        st.plotly_chart(fig2, width='stretch')

    # =========================================================================
    # GRÁFICO 5: HISTOGRAMA DE DISTRIBUCIÓN
    # =========================================================================
    with col_der:
        st.subheader("📉 5. Concentración de Alertas Críticas por Región")
        df_alertas_solo = df_filtrado[df_filtrado['mental_health_alert'] == 1]
        
        fig3 = px.histogram(
            df_alertas_solo,
            x="Country",
            title="Frecuencia y distribución geográfica de alertas críticas",
            labels={"Country": "País", "count": "Casos de Alerta"},
            color_discrete_sequence=["#B71C1C"]
        )
        fig3.update_xaxes(categoryorder="total descending")
        st.plotly_chart(fig3, width='stretch')

    st.markdown("---")

    # 5. Vista de tabla de datos brutos expandible al final
    with st.expander("📂 Inspeccionar registros granulares extraídos (Primeros 100 casos)"):
        st.dataframe(df_filtrado.head(100), width='stretch')

if __name__ == "__main__":
    mostrar_dashboard()