# Verificación de la entrega 01

Verificada el 21 de septiembre de 2026 con Python 3.12.14 y Microsoft Edge mediante Playwright.

- 8 pruebas de integración del servidor: aprobadas (`python -m unittest discover -s tests -v`).
- Sintaxis de JavaScript: validada con `node --check static/app.js`.
- Navegador: catálogo demo de 6 recursos y 18 bienes, búsqueda por código de un ejemplar, filtro sin coincidencias y limpieza de filtros.
- Navegador: registro de recurso y primer bien; apertura del detalle; rechazo de duplicado; registro de segundo bien; persistencia tras recarga.
- Vista de escritorio revisada a 1440 px y móvil a 390 px, sin desbordamiento horizontal de página.
- Consola: sin errores de JavaScript durante el recorrido.

Los datos de estas comprobaciones se guardaron en una base temporal de trabajo, no en el catálogo entregado. La captura `vista-catalogo.png` muestra datos ficticios de demostración.

No se han probado despliegue público, concurrencia de múltiples usuarios ni flujos fuera del alcance de esta entrega.

Actualización: fechas y series generadas en el servidor, incluso ante valores manuales enviados a la API. Se verifica su persistencia y que dos ejemplares reciben series distintas.
