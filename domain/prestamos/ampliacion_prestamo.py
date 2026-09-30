from dataclasses import dataclass
from datetime import datetime


@dataclass
class AmpliacionPrestamo:
    id_ampliacion: str
    id_prestamo: str
    nueva_fecha_limite: datetime
    motivo: str

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_ampliacion=row.get('id_ampliacion'),
            id_prestamo=row.get('id_prestamo'),
            nueva_fecha_limite=row.get('nueva_fecha_limite'),
            motivo=row.get('motivo')
        )
