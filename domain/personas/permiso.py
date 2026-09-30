from dataclasses import dataclass


@dataclass
class Permiso:
    id_permiso: int
    nombre: str
    descripcion: str = ''

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_permiso=row.get('id_permiso'),
            nombre=row.get('nombre'),
            descripcion=row.get('descripcion', '')
        )
