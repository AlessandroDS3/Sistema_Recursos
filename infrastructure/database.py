# infrastructure/database.py
import mysql.connector

from config_db import DB_CONFIG


def get_connection():
    """
    Crea y devuelve una conexión a la base de datos 'sistema_prestamos'.
    """
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        print("✅ Conexión exitosa a 'sistema_prestamos'")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error al conectar: {err}")
        raise
