from infrastructure.repositories.usuario_repository import UsuarioSistemaRepository


def _normalizar_rol(rol):
    if not rol:
        return ""
    return rol.strip().upper().replace(' ', '_').replace('-', '_')


def validar_usuario(email, password, rol):
    """
    Valida si el usuario existe en la BD con las credenciales correctas.
    Retorna datos del usuario si es válido, None si no.
    """
    try:
        rol_normalizado = _normalizar_rol(rol)
        repository = UsuarioSistemaRepository()
        usuario = repository.autenticar(email, password, rol_normalizado)

        if not usuario:
            return None

        return {
            'id_usuario': usuario.id_usuario,
            'nombres': usuario.nombres,
            'apellidos': usuario.apellidos,
            'correo': usuario.correo,
            'rol': usuario.rol,
            'nombre_usuario': usuario.nombre_usuario,
        }

    except Exception as e:
        print(f"❌ Error en validación: {e}")
        return None
