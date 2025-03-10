import os
import csv
import feedparser
from concurrent.futures import ThreadPoolExecutor
import logging
import mysql.connector
from dateutil import parser

# Configuración de logging (registrar mensajes durante la ejecución de un programa)
logging.basicConfig(filename="scraper.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Definir los medios con sus RSS y nivel en la escala (1-8: desde más pro-ruso a anti-ruso)
MEDIOS = [
    {"nombre": "RT", "rss": "https://www.rt.com/rss/", "escala": 1},
    {"nombre": "Sputnik News", "rss": "https://sputnikglobe.com/export/rss2/archive/index.xml", "escala": 2},
    {"nombre": "Al Jazeera", "rss": "https://www.aljazeera.com/xml/rss/all.xml", "escala": 3},
    {"nombre": "Reuters", "rss": "https://www.reuters.com/tools/rss", "escala": 4},
    {"nombre": "The New York Times", "rss": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "escala": 5},
    {"nombre": "BBC News", "rss": "http://feeds.bbci.co.uk/news/world/rss.xml", "escala": 6},
    {"nombre": "The Guardian", "rss": "https://www.theguardian.com/world/rss", "escala": 7},
    {"nombre": "Kyiv Independent", "rss": "https://kyivindependent.com/feed/", "escala": 8},
]

# Ruta para guardar el archivo CSV
output_path = os.path.join(os.path.dirname(__file__), "noticias_medios.csv")

def procesar_medio(medio):
    try:
        logging.info(f"Scrapeando {medio['nombre']}...")
        feed = feedparser.parse(medio["rss"])
        if not feed.entries:
            logging.warning(f"⚠️ No se encontraron noticias en {medio['nombre']}.")
            return []

        noticias = []
        for entry in feed.entries[:10]:  # Limitamos a 10 titulares por medio
            fecha_raw = entry.get("published", "")
            try:
                fecha = parser.parse(fecha_raw).date().isoformat()
            except Exception:
                fecha = "0000-00-00"  # Fecha por defecto en caso de error

            titular = entry.get("title", "Sin título")
            enlace = entry.get("link", "Sin enlace")
            noticias.append([fecha, medio["nombre"], medio["escala"], titular, enlace])

        return noticias
    except Exception as e:
        logging.error(f"⚠️ Error al procesar {medio['nombre']}: {e}")
        return []

def insertar_en_mysql(noticias):
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="MYSQL420",
            database="proyecto_noticias"
        )
        cursor = conexion.cursor()
        query = """
        INSERT INTO titulares (fecha, fuente, escala, titular, enlace)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(query, noticias)
        conexion.commit()
        cursor.close()
        conexion.close()
        logging.info("✅ Noticias guardadas en MySQL.")
    except mysql.connector.Error as err:
        logging.error(f"❌ Error al insertar en MySQL: {err}")

# Procesar medios en paralelo
with ThreadPoolExecutor() as executor:
    resultados = list(executor.map(procesar_medio, MEDIOS))

# Escribir resultados en el CSV
with open(output_path, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Fecha", "Fuente", "Escala", "Titular", "Enlace"])
    for noticias in resultados:
        writer.writerows(noticias)

logging.info(f"📌 Noticias guardadas en: {output_path}")

# Insertar resultados en la base de datos
for noticias in resultados:
    if noticias:
        insertar_en_mysql(noticias)

