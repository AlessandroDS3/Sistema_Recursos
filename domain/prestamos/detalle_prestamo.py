from dataclasses import dataclass


@dataclass
class DetallePrestamo:
    id_detalle: str
    id_prestamo: str
    id_recurso: str
    cantidad: int
    observacion: str = ''

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_detalle=row.get('id_detalle'),
            id_prestamo=row.get('id_prestamo'),
            id_recurso=row.get('id_recurso'),
            cantidad=row.get('cantidad', 0),
            observacion=row.get('observacion', '')
        )
