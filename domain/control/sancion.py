from dataclasses import dataclass
from datetime import datetime


@dataclass
class Sancion:
    id_sancion: str
    id_usuario: str
    motivo: str
    fecha_inicio: datetime
    fecha_fin: datetime | None = None
    activa: bool = True

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_sancion=row.get('id_sancion'),
            id_usuario=row.get('id_usuario'),
            motivo=row.get('motivo'),
            fecha_inicio=row.get('fecha_inicio'),
            fecha_fin=row.get('fecha_fin'),
            activa=bool(row.get('activa', True))
        )
