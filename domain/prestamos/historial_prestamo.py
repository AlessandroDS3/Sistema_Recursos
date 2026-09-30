from dataclasses import dataclass
from datetime import datetime


@dataclass
class HistorialPrestamo:
    id_historial: str
    id_prestamo: str
    accion: str
    fecha_accion: datetime
    detalle: str = ''

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_historial=row.get('id_historial'),
            id_prestamo=row.get('id_prestamo'),
            accion=row.get('accion'),
            fecha_accion=row.get('fecha_accion'),
            detalle=row.get('detalle', '')
        )
