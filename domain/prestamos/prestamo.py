from dataclasses import dataclass
from datetime import datetime


@dataclass
class Prestamo:
    id_prestamo: str
    id_usuario: str
    id_recurso: str
    fecha_prestamo: datetime
    fecha_limite: datetime
    estado: str

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_prestamo=row.get('id_prestamo'),
            id_usuario=row.get('id_usuario'),
            id_recurso=row.get('id_recurso'),
            fecha_prestamo=row.get('fecha_prestamo'),
            fecha_limite=row.get('fecha_limite'),
            estado=row.get('estado')
        )
