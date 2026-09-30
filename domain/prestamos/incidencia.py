from dataclasses import dataclass
from datetime import datetime


@dataclass
class Incidencia:
    id_incidencia: str
    id_prestamo: str
    descripcion: str
    fecha_reporte: datetime
    estado: str = 'PENDIENTE'

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_incidencia=row.get('id_incidencia'),
            id_prestamo=row.get('id_prestamo'),
            descripcion=row.get('descripcion'),
            fecha_reporte=row.get('fecha_reporte'),
            estado=row.get('estado', 'PENDIENTE')
        )
