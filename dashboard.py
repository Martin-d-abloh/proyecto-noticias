import streamlit as st
import mysql.connector
import pandas as pd
from mysql.connector import errorcode
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
import os

# Configuración inicial
st.set_page_config(
    page_title="Análisis de noticias",
    layout="wide",
    page_icon="📰",
    initial_sidebar_state="expanded"
)
st.title("📰 Dashboard de titulares por escala ideológica")

# Configuración de estilo
sns.set_theme(style="whitegrid", palette="pastel")
plt.style.use('ggplot')

# Paleta de colores mejorada
PALETA_ESCALAS = {
    1: '#1f77b4', 2: '#aec7e8', 3: '#2ca02c', 4: '#ffbb78',
    5: '#d62728', 6: '#9467bd', 7: '#8c564b', 8: '#e377c2'
}

# Stopwords optimizadas
STOPWORDS = frozenset({
    "the", "and", "of", "in", "to", "a", "on", "for", "with", "at",
    "from", "by", "an", "is", "as", "it", "that", "this", "was", "be",
    "are", "but", "or", "have", "has", "had", "their", "its", "they",
    "them", "his", "her", "he", "she", "we", "you", "i", "who", "what",
    "which", "will", "can", "all", "not", "been", "were", "also", "more",
    "after", "one", "new", "about", "would", "could", "just", "into",
    "over", "than", "when", "out", "up", "no", "so", "if", "do", "did",
    "may", "me", "us", "our", "because", "it's", "they're", "we're", 
    "that's", "don't", "isn't", "you're", "i'm", "he's", "she's"
})

@st.cache_resource(ttl=3600, show_spinner="Conectando a la base de datos...")
def init_connection():
    """Pool de conexiones persistente con manejo de errores"""
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password=st.secrets.get("MYSQL_PASSWORD", os.getenv("MYSQL_PASSWORD", "")),
            database="proyecto_noticias",
            charset="utf8mb4",
            pool_size=3,
            pool_name="news_pool",
            connect_timeout=5
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            st.error("Error de autenticación en la base de datos")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            st.error("Base de datos no encontrada")
        else:
            st.error(f"Error de conexión: {err}")
        st.stop()

@st.cache_data(ttl=600, show_spinner="Cargando datos...")
def cargar_datos():
    """Carga optimizada con manejo de errores"""
    query = """
        SELECT escala, titular 
        FROM titulares 
        WHERE escala IS NOT NULL 
        AND titular IS NOT NULL
        AND LENGTH(titular) > 10
    """
    try:
        conn = init_connection()
        return pd.read_sql(query, conn)
    except mysql.connector.Error as err:
        st.error(f"Error en consulta SQL: {err}")
        st.stop()
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

def limpiar_texto(texto):
    """Limpieza optimizada con manejo de contracciones"""
    texto = re.sub(r"[^a-zA-Z\s']", '', texto.lower())
    return re.sub(r"\s+", ' ', texto).strip()

def generar_grafico_conteo(df):
    """Genera gráfico de barras para conteo de titulares"""
    conteo = df["escala"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [PALETA_ESCALAS.get(e, "#888") for e in conteo.index]
    sns.barplot(x=conteo.index, y=conteo.values, palette=colors, ax=ax)
    ax.set(xlabel="Escala ideológica", ylabel="Número de titulares")
    ax.set_title("Distribución de titulares por escala ideológica", pad=20)
    ax.bar_label(ax.containers[0], label_type='edge', padding=3)
    return fig

def generar_grafico_palabras(df, escala):
    """Genera gráfico de palabras frecuentes para una escala específica"""
    titulares_escala = df[df["escala"] == escala]["titular"].str.cat(sep=' ')
    palabras = [p for p in limpiar_texto(titulares_escala).split() 
               if p not in STOPWORDS and len(p) > 3]
    
    if not palabras:
        return None
    
    conteo_palabras = Counter(palabras).most_common(10)
    palabras, frecuencias = zip(*conteo_palabras)
    
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.barh(palabras, frecuencias, color=PALETA_ESCALAS.get(escala, "#666"))
    ax.set_title(f"Escala {escala} - Palabras más frecuentes", pad=15)
    ax.invert_yaxis()
    ax.bar_label(ax.containers[0], label_type='edge', padding=3)
    return fig

# Carga de datos
with st.spinner("📦 Cargando dataset de noticias..."):
    df = cargar_datos()
    if df.empty:
        st.warning("⚠️ No se encontraron datos válidos")
        st.stop()

# Sidebar para filtros
with st.sidebar:
    st.header("Filtros")
    escalas = sorted(df["escala"].unique())
    seleccionadas = st.multiselect(
        "Selecciona escalas:",
        options=escalas,
        default=escalas
    )
    df_filtrado = df[df["escala"].isin(seleccionadas)]

# Gráfico principal
st.subheader("📊 Distribución de titulares")
st.pyplot(generar_grafico_conteo(df_filtrado))

# Tabla de datos
st.subheader(f"🔍 {len(df_filtrado)} titulares encontrados")
st.dataframe(
    df_filtrado,
    use_container_width=True,
    height=350,
    column_config={
        "escala": "Escala",
        "titular": "Titular"
    }
)

# Gráficos de palabras
st.subheader("🔠 Análisis de palabras clave")
for escala in seleccionadas:
    fig = generar_grafico_palabras(df_filtrado, escala)
    if fig:
        st.pyplot(fig)
    else:
        st.warning(f"No se encontraron palabras relevantes para la escala {escala}")