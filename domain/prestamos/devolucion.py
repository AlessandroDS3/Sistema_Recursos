from dataclasses import dataclass
from datetime import datetime


@dataclass
class Devolucion:
    id_devolucion: str
    id_prestamo: str
    fecha_devolucion: datetime

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_devolucion=row.get('id_devolucion'),
            id_prestamo=row.get('id_prestamo'),
            fecha_devolucion=row.get('fecha_devolucion')
        )
