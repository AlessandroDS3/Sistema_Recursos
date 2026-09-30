from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UsuarioSistema:
    id_usuario: str
    id_persona: str
    activo: bool = True
    ultimo_acceso: Optional[datetime] = None
    id_rol: int = 0
    nombre_usuario: Optional[str] = None
    correo: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    rol: Optional[str] = None

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_usuario=row.get('id_usuario'),
            id_persona=row.get('id_persona'),
            activo=bool(row.get('activo', True)),
            ultimo_acceso=row.get('ultimo_acceso'),
            id_rol=row.get('id_rol', 0),
            nombre_usuario=row.get('nombre_usuario'),
            correo=row.get('correo'),
            nombres=row.get('nombres'),
            apellidos=row.get('apellidos'),
            rol=row.get('rol')
        )
