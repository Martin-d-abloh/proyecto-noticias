import mysql.connector
from getpass import getpass  # Para ocultar la contraseña al escribir

# Configuración en variables (podrías mover esto a un archivo .env)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    # "password": "MYSQL420",  # No recomendado tenerla hardcodeada
    "database": "proyecto_noticias",
    "charset": "utf8mb4",  # Mejor soporte para caracteres especiales
}

try:
    # Obtener contraseña de forma segura
    DB_CONFIG["password"] = getpass("Ingresa tu contraseña de MySQL: ")
    
    # Conectar a MySQL usando with statement para manejo automático de conexión
    with mysql.connector.connect(**DB_CONFIG) as conexion:
        with conexion.cursor() as cursor:
            
            # Consulta más legible con f-strings
            query = """
                SELECT 
                    fuente AS Medio, 
                    COUNT(*) AS Cantidad
                FROM titulares
                GROUP BY fuente
                ORDER BY Cantidad DESC;
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()

            # Encabezado con formato mejorado
            print("\n📰 Análisis de titulares por medio de comunicación")
            print("-" * 45)
            for medio, cantidad in resultados:
                print(f"▪ {medio.ljust(25)}: {str(cantidad).rjust(4)} titulares")
            print("-" * 45)
            
except mysql.connector.Error as err:
    print(f"🚨 Error de MySQL: {err}")
    
except Exception as e:
    print(f"⚠️ Error inesperado: {e}")

finally:
    # El with statement ya cierra la conexión automáticamente
    if 'conexion' in locals() and conexion.is_connected():
        print("\n✅ Conexión cerrada exitosamente")