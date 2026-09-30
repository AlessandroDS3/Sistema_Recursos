# app.py
from functools import wraps
import hmac
import os
import secrets

import mysql.connector
from flask import Flask, abort, render_template, request, redirect, url_for, flash, session
from application.gestion_acceso_service import validar_usuario
from application.gestion_recursos_service import (
    ConflictoRecursoError,
    ESTADOS,
    GestionRecursosService,
    TIPOS_RECURSO,
    ValidacionRecursoError,
)
from infrastructure.repositories.recurso_repository import RecursoRepository

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)


def _requiere_administrador(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "usuario" not in session:
            flash("Debes iniciar sesión primero.", "error")
            return redirect(url_for("login"))
        if (session.get("rol") or "").upper() != "ADMINISTRADOR":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def _token_csrf():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def _validar_csrf():
    token_sesion = session.get("csrf_token", "")
    token_formulario = request.form.get("csrf_token", "")
    if not token_sesion or not hmac.compare_digest(token_sesion, token_formulario):
        abort(400, description="La sesión del formulario expiró. Vuelve a intentarlo.")


def _servicio_recursos():
    return GestionRecursosService(RecursoRepository())


def _fin_formulario(operacion, mensaje):
    try:
        operacion()
        flash(mensaje, "success")
    except (ValidacionRecursoError, ConflictoRecursoError, LookupError, ValueError) as exc:
        flash(str(exc), "error")
    except mysql.connector.Error:
        app.logger.exception("No se pudo guardar el catálogo de recursos")
        flash("No se pudo completar la operación en la base de datos.", "error")
    return redirect(url_for("administrar_recursos"))


def _nombre_rol(rol):
    rol_normalizado = (rol or "").upper()
    mapeo = {
        "ADMINISTRADOR": "Administrador",
        "ENCARGADO_DE_PRESTAMOS": "Encargado de Préstamos",
        "USUARIO": "Usuario",
    }
    return mapeo.get(rol_normalizado, "Usuario")


def _panel_por_rol(rol):
    rol_normalizado = (rol or "").upper()

    if rol_normalizado == "ADMINISTRADOR":
        return {
            "titulo": "Panel de Administrador",
            "mensaje": "Puedes gestionar usuarios, recursos y reportes del sistema.",
            "opciones": [
                "Usuarios",
                "Recursos",
                "Reportes",
                "Configuración",
            ],
        }

    if rol_normalizado == "ENCARGADO_DE_PRESTAMOS":
        return {
            "titulo": "Panel de Encargado de Préstamos",
            "mensaje": "Puedes registrar préstamos, renovaciones y devolver materiales al inventario.",
            "opciones": [
                "Préstamos",
                "Devoluciones",
                "Reservas",
                "Sanciones",
            ],
        }

    return {
        "titulo": "Panel de Usuario",
        "mensaje": "Puedes consultar tus reservas y préstamos activos desde tu cuenta.",
        "opciones": [
            "Mis préstamos",
            "Mis reservas",
            "Historial",
            "Perfil",
        ],
    }


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        rol = request.form.get('rol')

        usuario = validar_usuario(email, password, rol)

        if usuario:
            session.clear()
            session['usuario'] = usuario
            session['rol'] = usuario['rol']
            flash(f"¡Bienvenido, {usuario['nombres']} {usuario['apellidos']}! Has ingresado como {_nombre_rol(usuario['rol'])}.", "success")
            return redirect(url_for('dashboard'))

        return render_template('login.html')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        flash("Debes iniciar sesión primero.", "error")
        return redirect(url_for('login'))

    usuario = session['usuario']
    rol = session.get('rol', 'USUARIO')
    panel = _panel_por_rol(rol)

    return render_template(
        'dashboard.html', usuario=usuario, rol=rol, panel=panel,
        csrf_token=_token_csrf(),
    )


@app.route('/admin/recursos', methods=['GET'])
@_requiere_administrador
def administrar_recursos():
    recursos = []
    categorias = []
    try:
        servicio = _servicio_recursos()
        recursos = servicio.repository.listar()
        categorias = servicio.repository.categorias()
    except mysql.connector.Error:
        app.logger.exception("No se pudo cargar el catálogo de recursos")
        flash("No se pudo cargar el inventario. Comprueba la conexión con MySQL.", "error")
    return render_template(
        'admin_recursos.html',
        usuario=session['usuario'],
        recursos=recursos,
        categorias=categorias,
        tipos=TIPOS_RECURSO,
        estados=ESTADOS,
        csrf_token=_token_csrf(),
    )


@app.route('/admin/categorias', methods=['POST'])
@_requiere_administrador
def crear_categoria():
    _validar_csrf()
    servicio = _servicio_recursos()
    return _fin_formulario(
        lambda: servicio.crear_categoria(request.form),
        "Categoría creada correctamente.",
    )


@app.route('/admin/recursos/crear', methods=['POST'])
@_requiere_administrador
def crear_recurso():
    _validar_csrf()
    servicio = _servicio_recursos()
    return _fin_formulario(
        lambda: servicio.crear(request.form, request.form),
        "Recurso y primer bien material registrados correctamente.",
    )


@app.route('/admin/recursos/<id_recurso>/editar', methods=['POST'])
@_requiere_administrador
def editar_recurso(id_recurso):
    _validar_csrf()
    servicio = _servicio_recursos()
    return _fin_formulario(
        lambda: servicio.editar(id_recurso, request.form),
        "Recurso actualizado correctamente.",
    )


@app.route('/admin/recursos/<id_recurso>/bienes', methods=['POST'])
@_requiere_administrador
def agregar_bien(id_recurso):
    _validar_csrf()
    servicio = _servicio_recursos()
    return _fin_formulario(
        lambda: servicio.agregar_bien(id_recurso, request.form),
        "Ejemplar agregado correctamente.",
    )


@app.route('/admin/bienes/<id_bien>/editar', methods=['POST'])
@_requiere_administrador
def editar_bien(id_bien):
    _validar_csrf()
    servicio = _servicio_recursos()
    return _fin_formulario(
        lambda: servicio.editar_bien(id_bien, request.form),
        "Bien material actualizado correctamente.",
    )


@app.route('/admin/bienes/<id_bien>/eliminar', methods=['POST'])
@_requiere_administrador
def eliminar_bien(id_bien):
    _validar_csrf()
    servicio = _servicio_recursos()
    return _fin_formulario(
        lambda: servicio.eliminar_bien(id_bien),
        "Bien material eliminado correctamente.",
    )


@app.route('/admin/recursos/<id_recurso>/eliminar', methods=['POST'])
@_requiere_administrador
def eliminar_recurso(id_recurso):
    _validar_csrf()
    servicio = _servicio_recursos()
    return _fin_formulario(
        lambda: servicio.eliminar(id_recurso),
        "Recurso y sus bienes disponibles eliminados correctamente.",
    )


@app.route('/logout', methods=['POST'])
def logout():
    if 'usuario' in session:
        _validar_csrf()
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
