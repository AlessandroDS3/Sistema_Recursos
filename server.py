"""Servidor local de desarrollo. Solo biblioteca estándar de Python."""
import argparse
import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from urllib.parse import urlsplit

from app.domain import TipoRecurso, EstadoBienMaterial, ValidationError
from app.repository import RecursoSQLiteRepository
from app.service import GestionRecursosService, ConflictError

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"


def make_server(database, port=8000):
    repository = RecursoSQLiteRepository(database)
    repository.initialize()
    service = GestionRecursosService(repository)

    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, value, mime="application/json; charset=utf-8"):
            body = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/api/catalogo":
                return self.reply(200, {"recursos": repository.listar(), "categorias": repository.categorias(),
                    "tipos": [t.value for t in TipoRecurso], "estados": [e.value for e in EstadoBienMaterial]})
            files = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"), "/styles.css": ("styles.css", "text/css")}
            if path in files:
                name, mime = files[path]
                return self.reply(200, (STATIC / name).read_bytes(), mime + "; charset=utf-8")
            return self.reply(404, {"error": "Ruta no encontrada."})

        def do_POST(self):
            # El frontend usa JSON y mismo origen; no se habilita CORS.
            expected_origin = f"http://127.0.0.1:{self.server.server_port}"
            allowed = {expected_origin, f"http://localhost:{self.server.server_port}"}
            if self.headers.get("Origin") and self.headers["Origin"] not in allowed:
                return self.reply(403, {"error": "Origen no permitido."})
            if self.headers.get_content_type() != "application/json":
                return self.reply(415, {"error": "Se requiere application/json."})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 16384:
                    return self.reply(413, {"error": "El cuerpo debe tener entre 1 y 16384 bytes."})
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValidationError("Se requiere un objeto JSON.")
                path = urlsplit(self.path).path
                if path == "/api/recursos":
                    return self.reply(201, {"idRecurso": service.registrar(data)})
                match = re.fullmatch(r"/api/recursos/([1-9][0-9]*)/bienes", path)
                if match:
                    return self.reply(201, {"idBien": service.agregar_bien(int(match[1]), data)})
                return self.reply(404, {"error": "Ruta no encontrada."})
            except (ValidationError, ValueError, UnicodeDecodeError) as exc:
                return self.reply(409 if isinstance(exc, ConflictError) else 400, {"error": str(exc)})
            except LookupError as exc:
                return self.reply(404, {"error": str(exc)})
            except Exception:
                logging.exception("Error al guardar")
                return self.reply(500, {"error": "No se pudo guardar. Intenta de nuevo."})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Catálogo local de recursos · Entrega 01")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--db", type=Path, default=BASE / "data" / "catalogo.sqlite3")
    args = parser.parse_args()
    args.db.parent.mkdir(parents=True, exist_ok=True)
    with make_server(args.db, args.port) as server:
        print(f"Catálogo disponible en http://127.0.0.1:{server.server_port} · Ctrl+C para salir", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
