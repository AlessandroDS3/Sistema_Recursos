"""Crea una base de demostración separada; nunca modifica el catálogo real."""
from pathlib import Path
from app.repository import RecursoSQLiteRepository
from app.service import GestionRecursosService

BASE = Path(__file__).resolve().parent


def crear_demo(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    repo = RecursoSQLiteRepository(path)
    repo.initialize()
    if repo.listar():
        print("La base demo ya contiene recursos; no se agregaron datos.")
        return
    service = GestionRecursosService(repo)
    samples = [
        ("Laptop de laboratorio", "LAPTOP", "Lenovo", "ThinkPad E14", 1, "Equipo de ejemplo para programación y actividades académicas.", "LAP", 3),
        ("Proyector multimedia", "PROYECTOR", "Epson", "PowerLite", 2, "Equipo de ejemplo para exposiciones en el aula.", "PRO", 2),
        ("Introducción a los algoritmos", "LIBRO", "MIT Press", "Material de consulta", 3, "Registro ficticio para demostrar el catálogo de bibliografía.", "LIB", 4),
        ("Tablet de apoyo académico", "TABLET", "Samsung", "Galaxy Tab", 1, "Equipo de ejemplo para lectura y actividades de clase.", "TAB", 2),
        ("Mouse óptico", "MOUSE", "Logitech", "M90", 4, "Periférico de ejemplo para equipos de laboratorio.", "MOU", 5),
        ("Cargador USB-C", "CARGADOR", "Lenovo", "65 W", 4, "Accesorio de ejemplo para laptops compatibles.", "CAR", 2),
    ]
    for nombre, tipo, marca, modelo, categoria, descripcion, prefix, count in samples:
        def bien(index):
            return {"codigoInventario": f"DEMO-{prefix}-{index:03}",
                    "ubicacion": "Laboratorio 01 · Datos de ejemplo"}
        rid = service.registrar({"recurso": {"nombre": nombre, "tipo": tipo, "marca": marca,
            "modelo": modelo, "descripcion": descripcion, "idCategoriaRef": categoria}, "bien": bien(1)})
        for index in range(2, count + 1):
            service.agregar_bien(rid, bien(index))
    print("Demo creada: 6 recursos y 18 bienes ficticios, todos disponibles.")


if __name__ == "__main__":
    crear_demo(BASE / "data" / "demo.sqlite3")
