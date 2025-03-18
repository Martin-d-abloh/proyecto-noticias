import mysql.connector
import matplotlib.pyplot as plt
from collections import Counter
from getpass import getpass
import re
import os
import logging
from matplotlib.ticker import MaxNLocator

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Paleta de colores por escala numérica (1 a 8)
PALETA_COLORES = {
    1: '#5e3c99',   # Super pro-Rusia
    2: '#b2abd2',   # Pro-Rusia
    3: '#f7f7f7',   # Leve tendencia pro-Rusia
    4: '#d5e2d0',   # Neutral con ligera tendencia pro-Rusia
    5: '#c2e699',   # Neutral con ligera tendencia anti-Rusia
    6: '#78c679',   # Leve tendencia pro-Ucrania
    7: '#238443',   # Pro-Ucrania
    8: '#004529'    # Super anti-Rusia
}

# Stopwords en inglés con contracciones comunes
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

def limpiar_texto(texto):
    """Limpieza optimizada para texto en inglés con manejo de contracciones"""
    texto = re.sub(r"[^a-zA-Z\s']", '', texto.lower())
    return re.sub(r"\s+", ' ', texto).strip()

def obtener_datos(conexion):
    """Obtiene y agrupa textos por escala ideológica"""
    query = """
        SELECT escala, GROUP_CONCAT(titular SEPARATOR ' ') AS textos
        FROM titulares 
        WHERE escala IS NOT NULL AND titular IS NOT NULL
        GROUP BY escala
    """
    with conexion.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        return cursor.fetchall()

def procesar_textos(texto):
    """Procesamiento eficiente para inglés con filtro de longitud"""
    palabras = (p for p in limpiar_texto(texto).split() 
                if p not in STOPWORDS and len(p) > 3)
    return Counter(palabras)

try:
    # Configuración de conexión
    DB_CONFIG = {
        "host": "localhost",
        "user": "root",
        "database": "proyecto_noticias",
        "charset": "utf8mb4",
        "password": getpass("🔐 Enter MySQL password: ")
    }

    with mysql.connector.connect(**DB_CONFIG) as conexion:
        datos = obtener_datos(conexion)
        
    if not datos:
        raise ValueError("⚠️ No data found to generate the chart")

    # Procesar datos
    conteos = {}
    for grupo in datos:
        escala = int(grupo['escala'])
        conteos[escala] = procesar_textos(grupo['textos'])

    # Configurar visualización
    num_escalas = len(conteos)
    fig, axs = plt.subplots(num_escalas, 1, 
                          figsize=(12, 2.5 * num_escalas),
                          gridspec_kw={'hspace': 0.4})
    
    if num_escalas == 1:
        axs = [axs]

    # Ordenar por escala numérica de 1 a 8
    orden_escalas = sorted(conteos.keys())

    for idx, escala in enumerate(orden_escalas):
        ax = axs[idx]
        color = PALETA_COLORES.get(escala, '#333333')
        
        try:
            palabras, frecuencias = zip(*conteos[escala].most_common(10))
        except ValueError:
            logging.warning(f"Not enough words for escala {escala}")
            continue

        # Crear gráfico con anotaciones
        bars = ax.barh(palabras, frecuencias, color=color, height=0.7)
        ax.invert_yaxis()
        
        # Añadir etiquetas de valor
        max_freq = max(frecuencias)
        for bar in bars:
            width = bar.get_width()
            ax.text(width + max_freq * 0.02,
                    bar.get_y() + bar.get_height()/2,
                    f'{width:,}',
                    va='center',
                    ha='left',
                    fontsize=9)

        # Configuración estética
        ax.set_title(f"Escala {escala}", fontsize=12, pad=15, loc='left')
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='x', alpha=0.3)
        
        # Mostrar labels solo en el último gráfico
        if idx != len(orden_escalas)-1:
            ax.set_xticklabels([])
            ax.set_xlabel('')
        else:
            ax.set_xlabel("Frecuencia de palabras", labelpad=10)

    # Título general y guardado
    plt.suptitle("Palabras más frecuentes por escala ideológica\n", 
                fontsize=14, y=0.98, fontweight='bold')
    
    # Guardado en carpeta del proyecto
    output_path = os.path.join(os.path.dirname(__file__), "grafico_palabras_escala.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logging.info(f"✅ Gráfico guardado en: {output_path}")
    plt.close()

except mysql.connector.Error as err:
    logging.error(f"🚨 Error de MySQL: {err}")
except ValueError as ve:
    logging.error(ve)
except Exception as e:
    logging.error(f"⚠️ Error inesperado: {str(e)}", exc_info=True)
finally:
    if 'conexion' in locals() and conexion.is_connected():
        conexion.close()
        logging.info("🔒 Conexión cerrada")
