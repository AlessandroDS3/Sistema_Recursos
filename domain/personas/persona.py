from dataclasses import dataclass
from typing import Optional


@dataclass
class Persona:
    id_persona: str
    nombres: str
    apellidos: str
    correo: str
    estado: str = 'ACTIVO'

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_persona=row.get('id_persona'),
            nombres=row.get('nombres'),
            apellidos=row.get('apellidos'),
            correo=row.get('correo'),
            estado=row.get('estado', 'ACTIVO')
        )
