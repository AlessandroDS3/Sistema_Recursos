from dataclasses import dataclass


@dataclass
class Credenciales:
    id_usuario: str
    nombre_usuario: str
    contrasena_hash: str

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_usuario=row.get('id_usuario'),
            nombre_usuario=row.get('nombre_usuario'),
            contrasena_hash=row.get('contrasena_hash')
        )
