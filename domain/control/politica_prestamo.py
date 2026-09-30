from dataclasses import dataclass


@dataclass
class PoliticaPrestamo:
    id_politica: str
    nombre: str
    descripcion: str
    dias_maximos: int
    cantidad_maxima: int

    @classmethod
    def from_row(cls, row: dict):
        return cls(
            id_politica=row.get('id_politica'),
            nombre=row.get('nombre'),
            descripcion=row.get('descripcion', ''),
            dias_maximos=row.get('dias_maximos', 0),
            cantidad_maxima=row.get('cantidad_maxima', 0)
        )
