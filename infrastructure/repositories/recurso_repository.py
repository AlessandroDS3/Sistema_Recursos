"""Persistencia MySQL del catálogo de recursos y bienes materiales."""
from contextlib import contextmanager
from uuid import uuid4

from infrastructure.database import get_connection


class RecursoRepository:
    @contextmanager
    def _database(self):
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            yield connection, cursor
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def categorias(self):
        with self._database() as (_, cursor):
            cursor.execute(
                "SELECT id_categoria, nombre, descripcion "
                "FROM categoria_recurso ORDER BY nombre"
            )
            return cursor.fetchall()

    def listar(self):
        with self._database() as (_, cursor):
            cursor.execute("""
                SELECT r.id_recurso, r.nombre, r.descripcion, r.tipo, r.estado,
                       r.id_categoria, c.nombre AS categoria
                FROM recurso AS r
                JOIN categoria_recurso AS c ON c.id_categoria = r.id_categoria
                ORDER BY r.nombre
            """)
            recursos = cursor.fetchall()
            if not recursos:
                return []

            ids = [recurso["id_recurso"] for recurso in recursos]
            placeholders = ", ".join(["%s"] * len(ids))
            cursor.execute(f"""
                SELECT id_bien, id_recurso, codigo_inventario, numero_serie,
                       estado, ubicacion
                FROM bien_material
                WHERE id_recurso IN ({placeholders})
                ORDER BY codigo_inventario
            """, ids)
            bienes_por_recurso = {}
            for bien in cursor.fetchall():
                bienes_por_recurso.setdefault(bien["id_recurso"], []).append(bien)

            for recurso in recursos:
                bienes = bienes_por_recurso.get(recurso["id_recurso"], [])
                recurso["bienes"] = bienes
                recurso["total"] = len(bienes)
                recurso["disponibles"] = sum(
                    bien["estado"].upper() == "DISPONIBLE" for bien in bienes
                )
            return recursos

    def existe_categoria(self, id_categoria):
        with self._database() as (_, cursor):
            cursor.execute(
                "SELECT 1 FROM categoria_recurso WHERE id_categoria = %s",
                (id_categoria,),
            )
            return cursor.fetchone() is not None

    def existe_categoria_nombre(self, nombre):
        with self._database() as (_, cursor):
            cursor.execute(
                "SELECT 1 FROM categoria_recurso WHERE LOWER(nombre) = LOWER(%s)",
                (nombre,),
            )
            return cursor.fetchone() is not None

    def crear_categoria(self, nombre, descripcion):
        id_categoria = str(uuid4())
        with self._database() as (connection, cursor):
            cursor.execute("""
                INSERT INTO categoria_recurso (id_categoria, nombre, descripcion)
                VALUES (%s, %s, %s)
            """, (id_categoria, nombre, descripcion))
            connection.commit()
        return id_categoria

    def crear(self, recurso, bien):
        id_recurso = str(uuid4())
        id_bien = str(uuid4())
        with self._database() as (connection, cursor):
            try:
                cursor.execute("""
                    INSERT INTO recurso
                        (id_recurso, nombre, descripcion, tipo, estado, id_categoria)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    id_recurso, recurso["nombre"], recurso["descripcion"],
                    recurso["tipo"], recurso["estado"], recurso["id_categoria"],
                ))
                cursor.execute("""
                    INSERT INTO bien_material
                        (id_bien, id_recurso, codigo_inventario, numero_serie, estado, ubicacion)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    id_bien, id_recurso, bien["codigo_inventario"],
                    bien["numero_serie"], bien["estado"], bien["ubicacion"],
                ))
                connection.commit()
            except Exception:
                connection.rollback()
                raise
        return id_recurso

    def editar(self, id_recurso, recurso):
        with self._database() as (connection, cursor):
            cursor.execute(
                "SELECT estado FROM recurso WHERE id_recurso = %s FOR UPDATE",
                (id_recurso,),
            )
            actual = cursor.fetchone()
            if actual is None:
                raise LookupError("El recurso no existe.")
            if (
                recurso["estado"] in {"PRESTADO", "RESERVADO"}
                and actual["estado"].upper() != recurso["estado"]
            ):
                raise ValueError("Los estados de préstamos o reservas se gestionan desde sus módulos.")
            cursor.execute("""
                UPDATE recurso
                SET nombre = %s, descripcion = %s, tipo = %s, estado = %s, id_categoria = %s
                WHERE id_recurso = %s
            """, (
                recurso["nombre"], recurso["descripcion"], recurso["tipo"],
                recurso["estado"], recurso["id_categoria"], id_recurso,
            ))
            if cursor.rowcount == 0:
                cursor.execute("SELECT 1 FROM recurso WHERE id_recurso = %s", (id_recurso,))
                if cursor.fetchone() is None:
                    raise LookupError("El recurso no existe.")
            connection.commit()

    def agregar_bien(self, id_recurso, bien):
        id_bien = str(uuid4())
        with self._database() as (connection, cursor):
            cursor.execute("SELECT 1 FROM recurso WHERE id_recurso = %s", (id_recurso,))
            if cursor.fetchone() is None:
                raise LookupError("El recurso no existe.")
            cursor.execute("""
                INSERT INTO bien_material
                    (id_bien, id_recurso, codigo_inventario, numero_serie, estado, ubicacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                id_bien, id_recurso, bien["codigo_inventario"], bien["numero_serie"],
                bien["estado"], bien["ubicacion"],
            ))
            connection.commit()
        return id_bien

    def editar_bien(self, id_bien, bien):
        with self._database() as (connection, cursor):
            cursor.execute(
                "SELECT estado FROM bien_material WHERE id_bien = %s FOR UPDATE",
                (id_bien,),
            )
            actual = cursor.fetchone()
            if actual is None:
                raise LookupError("El bien material no existe.")
            if (
                bien["estado"] in {"PRESTADO", "RESERVADO"}
                and actual["estado"].upper() != bien["estado"]
            ):
                raise ValueError("Los estados de préstamos o reservas se gestionan desde sus módulos.")
            cursor.execute("""
                UPDATE bien_material
                SET codigo_inventario = %s, numero_serie = %s, estado = %s, ubicacion = %s
                WHERE id_bien = %s
            """, (
                bien["codigo_inventario"], bien["numero_serie"], bien["estado"],
                bien["ubicacion"], id_bien,
            ))
            if cursor.rowcount == 0:
                cursor.execute("SELECT 1 FROM bien_material WHERE id_bien = %s", (id_bien,))
                if cursor.fetchone() is None:
                    raise LookupError("El bien material no existe.")
            connection.commit()

    def eliminar_bien(self, id_bien):
        with self._database() as (connection, cursor):
            cursor.execute(
                """SELECT b.estado, r.estado AS estado_recurso
                   FROM bien_material AS b
                   JOIN recurso AS r ON r.id_recurso = b.id_recurso
                   WHERE b.id_bien = %s FOR UPDATE""",
                (id_bien,),
            )
            bien = cursor.fetchone()
            if bien is None:
                raise LookupError("El bien material no existe.")
            if bien["estado"].upper() != "DISPONIBLE":
                raise ValueError("Solo se pueden eliminar bienes disponibles.")
            if bien["estado_recurso"].upper() != "DISPONIBLE":
                raise ValueError("No se pueden eliminar bienes de un recurso ocupado.")
            cursor.execute("DELETE FROM bien_material WHERE id_bien = %s", (id_bien,))
            connection.commit()

    def eliminar(self, id_recurso):
        with self._database() as (connection, cursor):
            try:
                cursor.execute(
                    "SELECT estado FROM recurso WHERE id_recurso = %s FOR UPDATE",
                    (id_recurso,),
                )
                recurso = cursor.fetchone()
                if recurso is None:
                    raise LookupError("El recurso no existe.")
                if recurso["estado"].upper() != "DISPONIBLE":
                    raise ValueError("Solo se pueden eliminar recursos disponibles.")

                cursor.execute("""
                    SELECT estado FROM bien_material
                    WHERE id_recurso = %s FOR UPDATE
                """, (id_recurso,))
                if any(row["estado"].upper() != "DISPONIBLE" for row in cursor.fetchall()):
                    raise ValueError("El recurso tiene bienes que no están disponibles.")

                cursor.execute("DELETE FROM bien_material WHERE id_recurso = %s", (id_recurso,))
                cursor.execute("DELETE FROM recurso WHERE id_recurso = %s", (id_recurso,))
                connection.commit()
            except Exception:
                connection.rollback()
                raise