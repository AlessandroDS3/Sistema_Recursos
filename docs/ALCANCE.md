# Alcance del hito 01 — 15% estimado

## Criterio

El archivo entregado contiene un modelo DDD por contextos y una vista de arquitectura por capas. Se consultaron como especificación del dominio, no como instrucciones para construir todo el sistema.

Sin una estimación acordada de historias y horas, el porcentaje no puede comprobarse de forma exacta. Para avanzar poco a poco se fija este hito acotado y una distribución inicial de referencia:

| Entrega | Alcance | Peso estimado | Situación |
|---|---|---:|---|
| 01 | Base por capas, catálogo inicial, alta/consulta de recursos y ejemplares, validación y documentación | 15% | Implementado |
| 02 | Personas, cuentas, autenticación, roles y permisos | 20% | Pendiente |
| 03 | Políticas, préstamo individual, detalle y control de disponibilidad | 25% | Pendiente |
| 04 | Devoluciones, historial e incidencias | 15% | Pendiente |
| 05 | Reservas, préstamos grupales y ampliaciones | 15% | Pendiente |
| 06 | Sanciones, avisos, mantenimiento y preparación de despliegue | 10% | Pendiente |

La distribución es una propuesta de planificación, reajustable conforme se definan reglas y criterios. No se ha desarrollado funcionalidad de las entregas 02–06.

## Trazabilidad al MDJ

| Elemento del modelo | Implementación de este hito |
|---|---|
| `Recurso` (Aggregate Root) | Nombre, tipo, marca, modelo, descripción e identificador asignado por SQLite |
| `BienMaterial` (Aggregate Root) | Referencia al recurso, código, serie, adquisición, estado, ubicación e identificador |
| `CategoriaRecurso` | Tabla y catálogo inicial de cuatro categorías; sin operaciones de administración |
| `TipoRecurso` | LIBRO, LAPTOP, PROYECTOR, CARGADOR, MOUSE, TABLET, OTRO |
| `EstadoBienMaterial` | Se conserva la enumeración completa; las altas solo usan DISPONIBLE |
| Categoría clasifica recurso | `recurso.idCategoriaRef` como clave foránea |
| Recurso posee bienes (1..*) | Registro atómico del recurso junto con su primer bien; alta de más ejemplares |
| `GestionRecursosService` | Casos de uso de alta; todavía no cubre toda la gestión del contexto |
| Presentación / aplicación / dominio / infraestructura | Separadas en servidor HTTP, servicio, dominio y repositorio |
| `RecursoMySQLRepository` | Adaptación inicial a `RecursoSQLiteRepository`; MySQL pendiente |

Los nombres Python de atributos conservan los del modelo. Los identificadores se generan en persistencia y se devuelven en la API; las clases de alta contienen los datos previos a la asignación del identificador. Se agregan claves foráneas para materializar las asociaciones del diagrama.

La vista detallada de `TipoRecurso` incluye TABLET y la vista resumida de arquitectura lo omite. Se tomó la vista detallada como referencia y se conservó TABLET. Las clases repetidas entre ambas vistas no se implementaron dos veces.

## Reglas iniciales propuestas

Estas validaciones son decisiones de esta entrega; el diagrama no especifica todas ellas:

- Código de inventario único en todo el catálogo, normalizado a mayúsculas.
- Código con letras sin tildes, números, punto, guion o guion bajo; máximo 40 caracteres.
- Nombre, tipo, categoría, código y ubicación obligatorios.
- Marca, modelo y descripción opcionales. Número de serie interno aleatorio generado mediante UUID4 al guardar; no representa una serie del fabricante.
- Fecha asignada automáticamente con el día local del servidor al guardar. Se conserva la columna `fechaAdquisicion` por compatibilidad con el modelo, pero para nuevas altas su significado es fecha de registro. Fecha y serie enviadas por el cliente se ignoran. Los registros anteriores conservan sus valores históricos.
- Bien nuevo en DISPONIBLE; cambios de estado reservados a futuros casos de uso.
- El alta de recurso y primer bien es atómica: si falla el código, no queda un recurso vacío.
- Tipos y estados comprobados también mediante restricciones SQL; asociaciones mediante claves foráneas.

## Criterios de aceptación

- Iniciar sin dependencias de terceros y ver un estado vacío comprensible.
- Registrar un recurso y ver un bien disponible en el detalle.
- Añadir un segundo bien sin duplicar la definición del recurso.
- Rechazar un código duplicado sin dejar datos parciales.
- Mantener registros al volver a abrir la base de datos.
- Encontrar recursos por filtros o por el código de cualquiera de sus bienes.
- Usar la interfaz en escritorio y pantalla móvil.

## Siguiente paso sugerido

Antes de implementar préstamos: definir personas y acceso (entrega 02), y después acordar políticas de préstamo y responsabilidades. No se adelantó su implementación.
