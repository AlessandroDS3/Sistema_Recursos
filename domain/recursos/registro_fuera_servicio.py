from dataclasses import dataclass
from datetime import datetime


@dataclass
class RegistroFueraServicio:
    id_registro: str
    id_recurso: str
    motivo: str
    fecha_inicio: datetime
    fecha_fin: datetime | None = None

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_registro=row.get('id_registro'),
            id_recurso=row.get('id_recurso'),
            motivo=row.get('motivo'),
            fecha_inicio=row.get('fecha_inicio'),
            fecha_fin=row.get('fecha_fin')
        )
