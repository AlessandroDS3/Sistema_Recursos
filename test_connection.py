# test_connection.py
import mysql.connector
from config_db import DB_CONFIG
def test_conexion():
    try:
        # 1. Conectar a la base de datos
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ Conexión exitosa a 'sistema_prestamos'")

        # 2. Verificar que existen las 11 tablas
        cursor.execute("SHOW TABLES")
        tablas = [tabla[0] for tabla in cursor.fetchall()]
        
        print(f"\n📋 Tablas encontradas ({len(tablas)}):")
        for tabla in tablas:
            print(f"   - {tabla}")

        # 3. Validar estructura básica (opcional: chequear una fila)
        cursor.execute("SELECT COUNT(*) FROM recurso")
        count = cursor.fetchone()[0]
        print(f"\n📊 Registros en 'recurso': {count}")

        cursor.close()
        conn.close()
        print("\n🎉 ¡Todo listo para comenzar el dominio DDD!")

    except mysql.connector.Error as err:
        print(f"❌ Error de conexión: {err}")
        print("Revisa que MySQL esté corriendo y que las credenciales sean correctas.")

if __name__ == "__main__":
    test_conexion()
