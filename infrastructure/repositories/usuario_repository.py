from infrastructure.database import get_connection
from domain.personas.usuario_sistema import UsuarioSistema


class UsuarioSistemaRepository:
    def autenticar(self, email: str, password: str, rol: str):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT us.id_usuario,
                       us.id_persona,
                       us.activo,
                       us.ultimo_acceso,
                       us.id_rol,
                       c.nombre_usuario,
                       p.correo,
                       p.nombres,
                       p.apellidos,
                       r.nombre AS rol
                FROM usuario_sistema us
                JOIN persona p ON us.id_persona = p.id_persona
                JOIN rol r ON us.id_rol = r.id_rol
                JOIN credenciales c ON c.id_usuario = us.id_usuario
                WHERE us.activo = 1
                  AND (p.correo = %s OR c.nombre_usuario = %s)
                  AND c.contrasena_hash = SHA2(%s, 256)
                  AND r.nombre = %s
            """

            cursor.execute(query, (email, email, password, rol))
            row = cursor.fetchone()

            if not row:
                return None

            return UsuarioSistema.from_row(row)

        except Exception as exc:
            print(f"❌ Error al autenticar usuario: {exc}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_por_id(self, id_usuario):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT us.id_usuario, us.id_persona, us.activo, us.ultimo_acceso, us.id_rol,
                       c.nombre_usuario, p.correo, p.nombres, p.apellidos, r.nombre AS rol
                FROM usuario_sistema us
                JOIN persona p ON us.id_persona = p.id_persona
                JOIN rol r ON us.id_rol = r.id_rol
                LEFT JOIN credenciales c ON c.id_usuario = us.id_usuario
                WHERE us.id_usuario = %s
            """

            cursor.execute(query, (id_usuario,))
            row = cursor.fetchone()
            return UsuarioSistema.from_row(row) if row else None
        except Exception as exc:
            print(f"❌ Error al obtener usuario: {exc}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
