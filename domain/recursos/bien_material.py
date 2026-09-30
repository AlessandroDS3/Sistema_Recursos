from dataclasses import dataclass
from domain.recursos.recurso import Recurso


@dataclass
class BienMaterial(Recurso):
    codigo_inventario: str = ''
    numero_serie: str = ''
    ubicacion: str = ''

    @classmethod
    def from_row(cls, row: dict):
        recurso = Recurso.from_row(row)
        return cls(
            id_recurso=recurso.id_recurso,
            nombre=recurso.nombre,
            descripcion=recurso.descripcion,
            tipo=recurso.tipo,
            estado=recurso.estado,
            id_categoria=recurso.id_categoria,
            codigo_inventario=row.get('codigo_inventario', ''),
            numero_serie=row.get('numero_serie', ''),
            ubicacion=row.get('ubicacion', '')
        )
