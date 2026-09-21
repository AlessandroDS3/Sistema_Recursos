"""Casos de uso de esta primera entrega."""
import sqlite3
from .domain import Recurso, BienMaterial, ValidationError


class ConflictError(ValueError):
    pass


class GestionRecursosService:
    def __init__(self, repository):
        self.repository = repository

    def registrar(self, data):
        recurso = Recurso.desde_datos(data.get("recurso"))
        bien = BienMaterial.desde_datos(data.get("bien"))
        if recurso.idCategoriaRef not in [c["idCategoria"] for c in self.repository.categorias()]:
            raise ValidationError("La categoría no existe.")
        try:
            return self.repository.crear(recurso, bien)
        except sqlite3.IntegrityError:
            raise ConflictError("El código de inventario ya está registrado.") from None

    def agregar_bien(self, recurso_id, data):
        bien = BienMaterial.desde_datos(data)
        try:
            return self.repository.agregar_bien(recurso_id, bien)
        except sqlite3.IntegrityError:
            raise ConflictError("El código de inventario ya está registrado.") from None
