from dataclasses import dataclass
from datetime import datetime


@dataclass
class Reserva:
    id_reserva: str
    id_usuario: str
    id_recurso: str
    fecha_reserva: datetime
    fecha_expiracion: datetime
    estado: str

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_reserva=row.get('id_reserva'),
            id_usuario=row.get('id_usuario'),
            id_recurso=row.get('id_recurso'),
            fecha_reserva=row.get('fecha_reserva'),
            fecha_expiracion=row.get('fecha_expiracion'),
            estado=row.get('estado')
        )
