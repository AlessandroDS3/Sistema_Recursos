from dataclasses import dataclass


@dataclass
class Recurso:
    id_recurso: str
    nombre: str
    descripcion: str
    tipo: str
    estado: str
    id_categoria: str

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_recurso=row.get('id_recurso'),
            nombre=row.get('nombre'),
            descripcion=row.get('descripcion', ''),
            tipo=row.get('tipo'),
            estado=row.get('estado'),
            id_categoria=row.get('id_categoria')
        )
