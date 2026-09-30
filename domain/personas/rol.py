from dataclasses import dataclass


@dataclass
class Rol:
    id_rol: int
    nombre: str

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_rol=row.get('id_rol'),
            nombre=row.get('nombre')
        )
