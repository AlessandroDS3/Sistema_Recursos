# Recurso · Sistema de préstamos de recursos

**Entrega 01: base y catálogo de recursos — hito inicial del 15% estimado.**

Proyecto para la Escuela Profesional de Ciencia de la Computación, basado en `ddd_completo.mdj`. Esta entrega implementa solamente el inicio del contexto **Recursos Materiales**. El flujo de préstamos se desarrollará en entregas posteriores.

## Ejecutar

Requiere **Python 3.10 o posterior**. No hay paquetes que instalar ni conexión a Internet requerida. HTML, CSS y JavaScript funcionan desde el servidor Python; no abras el HTML por separado.

Desde esta carpeta:

En Windows puedes hacer doble clic en **`iniciar.cmd`** y dejar abierta su terminal. El iniciador detecta Python instalado y también el runtime local de Codex de este equipo. Después abre **http://127.0.0.1:8000**.

Si prefieres la terminal:

```powershell
python server.py
```

En Windows también puedes usar `py server.py`, si tienes el lanzador de Python. Abre **http://127.0.0.1:8000**. Para cerrar, usa Ctrl+C en la terminal. Si el puerto está ocupado: `python server.py --port 8001`.

La base `data/catalogo.sqlite3` se crea automáticamente, vacía de recursos y con cuatro categorías iniciales. Los registros se conservan al reiniciar. Para respaldarlos, detén el servidor y copia ese archivo.

## Probar con ejemplos opcionales

```powershell
python demo.py
python server.py --db data/demo.sqlite3 --port 8001
```

Abre **http://127.0.0.1:8001**. Son 6 recursos y 18 bienes **ficticios**, en una base separada. Ejecutar de nuevo `demo.py` no duplica los datos. El catálogo normal sigue vacío hasta registrar tus propios recursos.

## Qué puedes hacer

1. Registrar un recurso con nombre, tipo, categoría, marca, modelo y descripción.
2. Registrar su primer bien material con código y ubicación; la fecha actual y la serie aleatoria se asignan automáticamente al guardar.
3. Consultar el catálogo, el detalle y sus ejemplares físicos.
4. Añadir varios ejemplares al mismo recurso.
5. Buscar por nombre, marca, modelo o código; filtrar por tipo y disponibilidad.
6. Consultar los totales reales de recursos, bienes y bienes disponibles.

Un **Recurso** describe el modelo compartido. Un **BienMaterial** identifica un ejemplar físico. Por ejemplo, un recurso “Laptop ThinkPad E14” puede tener los bienes `CC-LAP-001` y `CC-LAP-002`.

## Alcance deliberadamente limitado

No se implementaron autenticación, personas, roles, permisos, préstamos, devoluciones, reservas, sanciones, políticas, incidencias, avisos, mantenimiento, edición o eliminación. Los nuevos bienes empiezan `DISPONIBLE`; no hay botones que simulen préstamos. Las categorías son de consulta y selección, sin administración en esta entrega.

El 15% es una **estimación de alcance del hito**, no una medición matemática de líneas de código ni una certificación de avance del modelo entero. Consulta [el alcance y la trazabilidad](docs/ALCANCE.md).

## Organización

```text
server.py              Presentación: rutas HTTP y arranque local
app/domain.py          Dominio: Recurso, BienMaterial, enumeraciones y validaciones
app/service.py         Aplicación: registrar recurso y agregar ejemplar
app/repository.py      Infraestructura: SQLite, relaciones y transacciones
static/                Interfaz HTML, CSS y JavaScript sin frameworks
tests/test_catalogo.py Pruebas de integración HTTP y persistencia
demo.py                Datos ficticios opcionales en una base separada
docs/ALCANCE.md         Relación con el modelo y trabajo pendiente
```

**Tecnología adicional: SQLite/SQL**, incluida con Python, para guardar los datos sin instalar un servidor de base de datos. El modelo contiene repositorios MySQL; esta entrega utiliza un repositorio SQLite separado para simplificar el inicio. No se ha implementado ni probado una migración a MySQL.

Este es un servidor de desarrollo local, ligado a `127.0.0.1`, sin acceso de usuarios. Su publicación y autenticación están fuera del hito.

## Verificación

```powershell
python -m unittest discover -s tests -v
```

Las pruebas usan bases temporales y no alteran tus registros. Cubren persistencia, varios bienes por recurso, duplicados y reversión de transacciones, entradas inválidas, rutas y restricciones de origen.

Comprobación manual: crea un recurso, agrega un segundo ejemplar, busca su código, revisa los contadores, intenta repetir el código y reinicia el servidor. Los dos bienes deben seguir registrados.

## API implementada

| Método | Ruta | Función |
|---|---|---|
| GET | `/api/catalogo` | Recursos con sus bienes, categorías y enumeraciones |
| POST | `/api/recursos` | Crear recurso y primer bien en una transacción |
| POST | `/api/recursos/{id}/bienes` | Agregar un ejemplar |

Los POST aceptan JSON. El registro de recurso recibe `{"recurso": {...}, "bien": {...}}`; agregar ejemplar recibe los campos del bien directamente. Los nombres de campos están definidos en `app/domain.py`. Las respuestas usan 201 al crear, 400 ante datos inválidos, 404 cuando no existe el recurso y 409 si se repite el código.
