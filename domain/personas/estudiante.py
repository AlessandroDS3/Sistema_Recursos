from dataclasses import dataclass
from domain.personas.persona import Persona


@dataclass
class Estudiante(Persona):
    carrera: str = ''
    ciclo: str = ''

    @classmethod
    def from_row(cls, row: dict):
        persona = Persona.from_row(row)
        return cls(
            id_persona=persona.id_persona,
            nombres=persona.nombres,
            apellidos=persona.apellidos,
            correo=persona.correo,
            estado=persona.estado,
            carrera=row.get('carrera', ''),
            ciclo=row.get('ciclo', '')
        )
