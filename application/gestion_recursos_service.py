"""Casos de uso y validaciones del catálogo de recursos."""
import re
from uuid import uuid4

import mysql.connector


TIPOS_RECURSO = ("LIBRO", "LAPTOP", "PROYECTOR", "CARGADOR", "MOUSE", "TABLET", "OTRO")
ESTADOS = ("DISPONIBLE", "PRESTADO", "RESERVADO", "DANADO", "MANTENIMIENTO", "PERDIDO")


class ValidacionRecursoError(ValueError):
    pass


class ConflictoRecursoError(ValueError):
    pass


class GestionRecursosService:
    def __init__(self, repository):
        self.repository = repository

    @staticmethod
    def _texto(data, campo, etiqueta, maximo, obligatorio=True):
        valor = data.get(campo, "")
        if not isinstance(valor, str):
            raise ValidacionRecursoError(f"{etiqueta}: valor no válido.")
        valor = valor.strip()
        if obligatorio and not valor:
            raise ValidacionRecursoError(f"{etiqueta}: es obligatorio.")
        if len(valor) > maximo:
            raise ValidacionRecursoError(f"{etiqueta}: máximo {maximo} caracteres.")
        return valor

    @classmethod
    def _datos_recurso(cls, data):
        tipo = cls._texto(data, "tipo", "Tipo", 50)
        estado = cls._texto(data, "estado", "Estado", 30)
        categoria = cls._texto(data, "id_categoria", "Categoría", 36)
        if tipo not in TIPOS_RECURSO:
            raise ValidacionRecursoError("Selecciona un tipo de recurso válido.")
        if estado not in ESTADOS:
            raise ValidacionRecursoError("Selecciona un estado válido.")
        if len(categoria) != 36:
            raise ValidacionRecursoError("Selecciona una categoría válida.")
        return {
            "nombre": cls._texto(data, "nombre", "Nombre", 100),
            "descripcion": cls._texto(data, "descripcion", "Descripción", 255, False),
            "tipo": tipo,
            "estado": estado,
            "id_categoria": categoria,
        }

    @classmethod
    def _datos_bien(cls, data, nuevo=False):
        codigo = cls._texto(data, "codigo_inventario", "Código de inventario", 100).upper()
        if not re.fullmatch(r"[A-Z0-9][A-Z0-9._-]*", codigo):
            raise ValidacionRecursoError(
                "El código solo admite letras, números, punto, guion y guion bajo."
            )
        estado = cls._texto(data, "estado", "Estado", 50) if not nuevo else "DISPONIBLE"
        if estado not in ESTADOS:
            raise ValidacionRecursoError("Selecciona un estado válido.")
        numero_serie = cls._texto(data, "numero_serie", "Número de serie", 100, False)
        if nuevo and not numero_serie:
            numero_serie = "SR-" + uuid4().hex.upper()
        return {
            "codigo_inventario": codigo,
            "numero_serie": numero_serie,
            "estado": estado,
            "ubicacion": cls._texto(data, "ubicacion", "Ubicación", 150, False),
        }

    def crear_categoria(self, data):
        nombre = self._texto(data, "nombre", "Nombre de categoría", 100)
        descripcion = self._texto(data, "descripcion", "Descripción", 255, False)
        if self.repository.existe_categoria_nombre(nombre):
            raise ConflictoRecursoError("Ya existe una categoría con ese nombre.")
        return self._guardar(self.repository.crear_categoria, nombre, descripcion)

    def crear(self, recurso_data, bien_data):
        recurso = self._datos_recurso(recurso_data)
        recurso["estado"] = "DISPONIBLE"
        bien = self._datos_bien(bien_data, nuevo=True)
        if not self.repository.existe_categoria(recurso["id_categoria"]):
            raise ValidacionRecursoError("La categoría seleccionada no existe.")
        return self._guardar(self.repository.crear, recurso, bien)

    def editar(self, id_recurso, data):
        recurso = self._datos_recurso(data)
        if not self.repository.existe_categoria(recurso["id_categoria"]):
            raise ValidacionRecursoError("La categoría seleccionada no existe.")
        return self._guardar(self.repository.editar, id_recurso, recurso)

    def agregar_bien(self, id_recurso, data):
        bien = self._datos_bien(data, nuevo=True)
        return self._guardar(self.repository.agregar_bien, id_recurso, bien)

    def editar_bien(self, id_bien, data):
        bien = self._datos_bien(data)
        return self._guardar(self.repository.editar_bien, id_bien, bien)

    def eliminar_bien(self, id_bien):
        return self._guardar(self.repository.eliminar_bien, id_bien)

    def eliminar(self, id_recurso):
        return self._guardar(self.repository.eliminar, id_recurso)

    @staticmethod
    def _guardar(operacion, *args):
        try:
            return operacion(*args)
        except mysql.connector.IntegrityError as exc:
            if exc.errno == 1062:
                raise ConflictoRecursoError(
                    "El código o el registro ya existe. Verifica que no esté duplicado."
                ) from None
            if exc.errno == 1451:
                raise ConflictoRecursoError(
                    "No se puede eliminar: el recurso está relacionado con préstamos, reservas o inventario."
                ) from None
            if exc.errno == 1452:
                raise ValidacionRecursoError("La categoría seleccionada no existe.") from None
            raise
        except LookupError:
            raise
        except ValueError:
            raise