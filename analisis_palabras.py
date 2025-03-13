import mysql.connector
import re
from collections import Counter
from getpass import getpass
from unicodedata import normalize  # Nueva importación para manejar acentos

# Ampliar lista de stopwords y mover a archivo aparte (mejor mantenimiento)
STOPWORDS = {
    # Español
    "el", "la", "los", "las", "de", "del", "en", "y", "un", "una",
    "con", "por", "para", "a", "al", "que", "es", "más", "su", "sus",
    "como", "se", "ha", "han", "no", "lo", "o", "este", "esta", "sin",
    
    # Inglés
    "the", "and", "of", "in", "to", "a", "on", "for", "with", "at", 
    "from", "by", "an", "is", "as", "it", "that", "this", "was", "be",
    "are", "but", "not", "or", "have", "has", "had", "their", "its", 
    "they", "them", "his", "her", "he", "she", "we", "you", "i", "who"
}


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "database": "proyecto_noticias",
    "charset": "utf8mb4",
}

def limpiar_texto(texto):
    """Normaliza y limpia el texto eliminando caracteres especiales"""
    texto = normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'[^\w\s]', '', texto.lower())

try:
    # Validación básica de contraseña
    if not (password := getpass("Ingresa tu contraseña de MySQL: ")):
        raise ValueError("La contraseña no puede estar vacía")
    
    DB_CONFIG["password"] = password
    
    with mysql.connector.connect(**DB_CONFIG) as conexion:
        with conexion.cursor() as cursor:
            
            # Consulta más eficiente filtrando nulos
            query = """
                SELECT escala, titular 
                FROM titulares 
                WHERE escala IS NOT NULL AND titular IS NOT NULL;
            """
            cursor.execute(query)
            resultados = cursor.fetchall()

            # Detectar escalas dinámicamente
            escalas_unicas = {escala for escala, _ in resultados}
            conteo_palabras = {escala: Counter() for escala in escalas_unicas}

            for escala, titular in resultados:
                palabras = re.findall(r'\b[a-záéíóúñ]+\b', limpiar_texto(titular), re.IGNORECASE)
                palabras_filtradas = [p for p in palabras if p not in STOPWORDS and len(p) > 2]
                
                conteo_palabras[escala].update(palabras_filtradas)

            # Mostrar resultados con formato mejorado
            print("\n📊 Palabras más usadas por escala ideológica:")
            for escala in sorted(conteo_palabras.keys()):
                print(f"\n🔵 Escala {escala} ({len(resultados)} titulares):")
                if not conteo_palabras[escala]:
                    print("   Sin palabras relevantes")
                    continue
                    
                for palabra, frecuencia in conteo_palabras[escala].most_common(10):
                    print(f"   ▫ {palabra.ljust(18)} → {str(frecuencia).zfill(2)} apariciones")

except mysql.connector.Error as err:
    print(f"🚨 Error de MySQL: {err}")

except Exception as e:
    print(f"⚠️ Error crítico: {str(e).capitalize()}")

finally:
    if 'conexion' in locals() and conexion.is_connected():
        conexion.close()