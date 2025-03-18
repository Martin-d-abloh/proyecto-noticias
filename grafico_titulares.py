import mysql.connector
import matplotlib.pyplot as plt
from getpass import getpass
import textwrap  # Para mejor formato de texto

# Configuración de la base de datos (mejor manejo de credenciales)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "database": "proyecto_noticias",
    "charset": "utf8mb4",
    "password": getpass("🔐 Ingresa tu contraseña de MySQL: ")
}

try:
    # Conexión y consulta mejor estructurada
    with mysql.connector.connect(**DB_CONFIG) as conexion:
        consulta = textwrap.dedent("""
            SELECT 
                fuente, 
                COUNT(*) as cantidad
            FROM titulares
            GROUP BY fuente
            ORDER BY cantidad DESC;
        """)
        
        with conexion.cursor(dictionary=True) as cursor:  # Usar diccionarios para mayor claridad
            cursor.execute(consulta)
            datos = cursor.fetchall()

    # Verificar si hay datos antes de procesar
    if not datos:
        raise ValueError("⚠️ No se encontraron registros en la base de datos")
    
    # Separar datos con nombres más descriptivos
    medios = [registro['fuente'] for registro in datos]
    cantidades = [registro['cantidad'] for registro in datos]

    # Configuración del gráfico mejorada
    plt.style.use('ggplot')  # Estilo profesional
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Crear gráfico con colores y formato mejorado
    barras = ax.barh(
        medios, 
        cantidades, 
        color='#2c5c8a', 
        edgecolor='black',
        height=0.8
    )
    
    # Añadir etiquetas de datos
    for barra in barras:
        width = barra.get_width()
        ax.text(
            width + (max(cantidades) * 0.01),  # Offset para mejor legibilidad
            barra.get_y() + barra.get_height()/2,
            f'{width:,}',  # Formato con separadores de miles
            va='center',
            ha='left',
            fontsize=9
        )

    # Configuración de ejes y títulos
    ax.set_xlabel("Cantidad de titulares", fontsize=12, labelpad=15)
    ax.set_ylabel("Medios de comunicación", fontsize=12, labelpad=15)
    ax.set_title(
        "Distribución de titulares por medio de comunicación\n",
        fontsize=14,
        fontweight='bold',
        pad=20
    )
    
    # Mejores márgenes y orden
    ax.invert_yaxis()  # Mayor cantidad arriba
    plt.xlim(0, max(cantidades) * 1.15)  # Espacio para las etiquetas
    plt.tight_layout()
    
    # Opciones de guardado/mostrado
    guardar = input("¿Deseas guardar el gráfico? (s/n): ").lower()
    if guardar == 's':
        nombre_archivo = input("Nombre del archivo (sin extensión): ")
        plt.savefig(f"{nombre_archivo}.png", dpi=300, bbox_inches='tight')
        print(f"✅ Gráfico guardado como {nombre_archivo}.png")
    else:
        plt.show()

except mysql.connector.Error as err:
    print(f"🚨 Error de MySQL: {err}")
except ValueError as ve:
    print(ve)
except Exception as e:
    print(f"🚨 Error inesperado: {str(e)}")
finally:
    if 'conexion' in locals() and conexion.is_connected():
        conexion.close()
        print("🔒 Conexión a BD cerrada")