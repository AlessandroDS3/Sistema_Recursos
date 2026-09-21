"""Persistencia del contexto Recursos Materiales."""
from contextlib import contextmanager
from dataclasses import asdict
import sqlite3


SCHEMA = """
CREATE TABLE IF NOT EXISTS categoria_recurso (
    idCategoria INTEGER PRIMARY KEY, nombre TEXT NOT NULL UNIQUE, descripcion TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS recurso (
    idRecurso INTEGER PRIMARY KEY, nombre TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('LIBRO','LAPTOP','PROYECTOR','CARGADOR','MOUSE','TABLET','OTRO')),
    marca TEXT NOT NULL, modelo TEXT NOT NULL, descripcion TEXT NOT NULL,
    idCategoriaRef INTEGER NOT NULL REFERENCES categoria_recurso(idCategoria)
);
CREATE TABLE IF NOT EXISTS bien_material (
    idBien INTEGER PRIMARY KEY, idRecursoRef INTEGER NOT NULL REFERENCES recurso(idRecurso),
    codigoInventario TEXT NOT NULL COLLATE NOCASE UNIQUE, numeroSerie TEXT NOT NULL,
    fechaAdquisicion TEXT NOT NULL,
    estado TEXT NOT NULL CHECK(estado IN ('DISPONIBLE','PRESTADO','RESERVADO','DANADO','MANTENIMIENTO','PERDIDO')),
    ubicacion TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_bien_recurso ON bien_material(idRecursoRef);
"""


class RecursoSQLiteRepository:
    def __init__(self, path):
        self.path = path

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def initialize(self):
        with self.connection() as conn:
            conn.executescript(SCHEMA)
            conn.executemany("INSERT OR IGNORE INTO categoria_recurso VALUES (?, ?, ?)", [
                (1, "Equipos de cómputo", "Equipos para actividades académicas."),
                (2, "Audiovisuales", "Recursos para presentaciones y clases."),
                (3, "Bibliografía", "Material de consulta y estudio."),
                (4, "Accesorios", "Periféricos y complementos."),
            ])

    def categorias(self):
        with self.connection() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM categoria_recurso ORDER BY idCategoria")]

    @staticmethod
    def insert_bien(conn, recurso_id, bien):
        cursor = conn.execute("""INSERT INTO bien_material
            (idRecursoRef, codigoInventario, numeroSerie, fechaAdquisicion, estado, ubicacion)
            VALUES (:idRecursoRef, :codigoInventario, :numeroSerie, :fechaAdquisicion, :estado, :ubicacion)""",
            {**asdict(bien), "idRecursoRef": recurso_id})
        return cursor.lastrowid

    def crear(self, recurso, bien):
        # Recurso y primer ejemplar se confirman juntos o se revierten juntos.
        with self.connection() as conn:
            cursor = conn.execute("""INSERT INTO recurso
                (nombre,tipo,marca,modelo,descripcion,idCategoriaRef)
                VALUES (:nombre,:tipo,:marca,:modelo,:descripcion,:idCategoriaRef)""", asdict(recurso))
            recurso_id = cursor.lastrowid
            self.insert_bien(conn, recurso_id, bien)
            return recurso_id

    def agregar_bien(self, recurso_id, bien):
        with self.connection() as conn:
            if not conn.execute("SELECT 1 FROM recurso WHERE idRecurso=?", (recurso_id,)).fetchone():
                raise LookupError("El recurso no existe.")
            return self.insert_bien(conn, recurso_id, bien)

    def listar(self):
        with self.connection() as conn:
            recursos = [dict(row) for row in conn.execute("""SELECT r.*, c.nombre AS categoria
                FROM recurso r JOIN categoria_recurso c ON c.idCategoria=r.idCategoriaRef
                ORDER BY r.idRecurso DESC""")]
            bienes = [dict(row) for row in conn.execute("SELECT * FROM bien_material ORDER BY codigoInventario")]
        agrupados = {}
        for bien in bienes:
            agrupados.setdefault(bien["idRecursoRef"], []).append(bien)
        for recurso in recursos:
            recurso["bienes"] = agrupados.get(recurso["idRecurso"], [])
            recurso["total"] = len(recurso["bienes"])
            recurso["disponibles"] = sum(b["estado"] == "DISPONIBLE" for b in recurso["bienes"])
        return recursos
