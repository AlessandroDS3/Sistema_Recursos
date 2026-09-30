from app import app as flask_app


CATEGORIA_ID = "2dcb77fa-df90-4f3a-90dd-1b1ef0a90826"


class RepositorioFalso:
    def __init__(self):
        self.creados = []

    def listar(self):
        return []

    def categorias(self):
        return [{"id_categoria": CATEGORIA_ID, "nombre": "Equipos", "descripcion": ""}]

    def existe_categoria(self, id_categoria):
        return id_categoria == CATEGORIA_ID

    def crear(self, recurso, bien):
        self.creados.append((recurso, bien))
        return "nuevo-id"


def _sesion_admin(client):
    with client.session_transaction() as state:
        state["usuario"] = {"nombres": "Ana", "apellidos": "Pérez"}
        state["rol"] = "ADMINISTRADOR"


def test_gestion_recursos_requiere_rol_administrador():
    client = flask_app.test_client()
    with client.session_transaction() as state:
        state["usuario"] = {"nombres": "Luis"}
        state["rol"] = "USUARIO"

    response = client.get("/admin/recursos")

    assert response.status_code == 403


def test_admin_puede_abrir_catalogo(monkeypatch):
    monkeypatch.setattr("app.RecursoRepository", RepositorioFalso)
    client = flask_app.test_client()
    _sesion_admin(client)

    response = client.get("/admin/recursos")

    assert response.status_code == 200
    assert "Recursos y bienes materiales" in response.get_data(as_text=True)
    assert "Registrar artículo" in response.get_data(as_text=True)


def test_alta_crea_articulo_y_primer_bien_en_la_misma_operacion(monkeypatch):
    repository = RepositorioFalso()
    monkeypatch.setattr("app.RecursoRepository", lambda: repository)
    client = flask_app.test_client()
    _sesion_admin(client)
    with client.session_transaction() as state:
        state["csrf_token"] = "csrf-prueba"

    response = client.post("/admin/recursos/crear", data={
        "csrf_token": "csrf-prueba",
        "nombre": "Laptop académica",
        "descripcion": "Equipo de laboratorio",
        "tipo": "LAPTOP",
        "estado": "DISPONIBLE",
        "id_categoria": CATEGORIA_ID,
        "codigo_inventario": "cc-lap-001",
        "numero_serie": "",
        "ubicacion": "Laboratorio 1",
    })

    assert response.status_code == 302
    assert len(repository.creados) == 1
    recurso, bien = repository.creados[0]
    assert recurso["nombre"] == "Laptop académica"
    assert bien["codigo_inventario"] == "CC-LAP-001"
    assert bien["estado"] == "DISPONIBLE"
    assert bien["numero_serie"].startswith("SR-")


def test_mutacion_rechaza_formulario_sin_token_csrf():
    client = flask_app.test_client()
    _sesion_admin(client)

    response = client.post("/admin/recursos/crear", data={"nombre": "No autorizado"})

    assert response.status_code == 400