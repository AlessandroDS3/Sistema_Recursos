from dataclasses import dataclass
from domain.personas.persona import Persona


@dataclass
class Docente(Persona):
    especialidad: str = ''
    categoria: str = ''

    @classmethod
    def from_row(cls, row: dict):
        persona = Persona.from_row(row)
        return cls(
            id_persona=persona.id_persona,
            nombres=persona.nombres,
            apellidos=persona.apellidos,
            correo=persona.correo,
            estado=persona.estado,
            especialidad=row.get('especialidad', ''),
            categoria=row.get('categoria', '')
        )
