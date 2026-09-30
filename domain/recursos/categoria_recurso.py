from dataclasses import dataclass


@dataclass
class CategoriaRecurso:
    id_categoria: str
    nombre: str
    descripcion: str = ''

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_categoria=row.get('id_categoria'),
            nombre=row.get('nombre'),
            descripcion=row.get('descripcion', '')
        )
