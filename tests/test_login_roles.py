from app import app


def test_login_guarda_sesion_y_rol():
    app.config['TESTING'] = True
    client = app.test_client()

    original = app.view_functions['login']
    def fake_validar_usuario(email, password, rol):
        return {
            'id_usuario': 1,
            'nombres': 'Ana',
            'apellidos': 'García',
            'correo': 'ana@utp.edu',
            'rol': 'ADMINISTRADOR',
            'nombre_usuario': 'ana'
        }

    app.view_functions['login'] = original
    import app as app_module
    app_module.validar_usuario = fake_validar_usuario

    response = client.post('/login', data={
        'email': 'ana@utp.edu',
        'password': '1234',
        'rol': 'Administrador'
    }, follow_redirects=False)

    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session['usuario']['rol'] == 'ADMINISTRADOR'
        assert session['rol'] == 'ADMINISTRADOR'


def test_dashboard_muestra_panel_segundo_rol():
    app.config['TESTING'] = True
    client = app.test_client()

    with client.session_transaction() as session:
        session['usuario'] = {
            'id_usuario': 2,
            'nombres': 'Luis',
            'apellidos': 'Pérez',
            'correo': 'luis@utp.edu',
            'rol': 'ENCARGADO_DE_PRESTAMOS',
            'nombre_usuario': 'luis'
        }
        session['rol'] = 'ENCARGADO_DE_PRESTAMOS'

    response = client.get('/dashboard')

    assert response.status_code == 200
    assert b'Panel de Encargado de Pr\xc3\xa9stamos' in response.data
