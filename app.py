"""
Interfaz web simple para probar el agente sin usar la terminal.

Uso:
    python3 app.py
Despues abrir http://localhost:8765 en el navegador.
"""
import os
import json
import time
import stat
import secrets
import subprocess
import traceback
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request, render_template_string, render_template, send_from_directory, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUNS_DIR = os.path.join(BASE_DIR, "output", "web_runs")
os.makedirs(RUNS_DIR, exist_ok=True)

DEMO_DATA_PATH = os.path.join(BASE_DIR, "demo_data", "datos_ejemplo.json")
KEY_FILE = os.path.join(BASE_DIR, ".anthropic_api_key")
PASSWORD_FILE = os.path.join(BASE_DIR, ".access_password_hash")
SECRET_KEY_FILE = os.path.join(BASE_DIR, ".flask_secret_key")
REGISTRO_PATH = os.path.join(BASE_DIR, "aseguradoras", "registro.json")


def cargar_registro():
    with open(REGISTRO_PATH, encoding="utf-8") as fh:
        return json.load(fh)


NOMBRES_GRUPOS_MENU = {
    "salud": "Salud",
    "danos": "Daños",
    "cobros": "Cobros",
    "reclamos": "Reclamos",
}
ORDEN_GRUPOS_MENU = ["salud", "danos", "cobros", "reclamos"]


def opciones_aseguradora_producto():
    """Lista de (valor, etiqueta, disponible) para el selector, valor = 'aseguradora:producto'."""
    opciones = []
    for aseguradora_id, aseguradora in cargar_registro().items():
        for producto_id, producto in aseguradora["productos"].items():
            valor = f"{aseguradora_id}:{producto_id}"
            etiqueta = producto.get("etiqueta_menu") or f"{aseguradora['nombre']} — {producto['nombre']}"
            opciones.append({"valor": valor, "etiqueta": etiqueta, "disponible": producto.get("disponible", False)})
    opciones.sort(key=lambda o: o["etiqueta"])
    return opciones


def opciones_agrupadas_aseguradora_producto():
    """Como opciones_aseguradora_producto() pero devuelve una lista de grupos
    {nombre, opciones} en el orden de ORDEN_GRUPOS_MENU, para armar <optgroup>
    en el selector. Un producto puede aparecer en mas de un grupo (ej. KYC en
    Salud y Danos) si su campo 'grupos' en registro.json lista varios."""
    por_grupo = {g: [] for g in ORDEN_GRUPOS_MENU}
    for aseguradora_id, aseguradora in cargar_registro().items():
        for producto_id, producto in aseguradora["productos"].items():
            valor = f"{aseguradora_id}:{producto_id}"
            etiqueta = producto.get("etiqueta_menu") or f"{aseguradora['nombre']} — {producto['nombre']}"
            opcion = {"valor": valor, "etiqueta": etiqueta, "disponible": producto.get("disponible", False)}
            for grupo in producto.get("grupos", []):
                por_grupo.setdefault(grupo, []).append(opcion)
    for opciones in por_grupo.values():
        opciones.sort(key=lambda o: o["etiqueta"])
    return [
        {"nombre": NOMBRES_GRUPOS_MENU.get(g, g), "opciones": por_grupo[g]}
        for g in ORDEN_GRUPOS_MENU
        if por_grupo.get(g)
    ]


def documentos_para(seleccion):
    """seleccion = 'aseguradora:producto' -> lista de dicts {titulo, script, mapping, salida}."""
    aseguradora_id, producto_id = seleccion.split(":", 1)
    registro = cargar_registro()
    return registro[aseguradora_id]["productos"][producto_id]["documentos"]


def _cargar_o_crear_secret_key():
    # En Render, configurar FLASK_SECRET_KEY como variable de entorno evita
    # que todas las sesiones se invaliden si el disco no es persistente.
    desde_env = os.environ.get("FLASK_SECRET_KEY")
    if desde_env:
        return desde_env
    if os.path.exists(SECRET_KEY_FILE):
        with open(SECRET_KEY_FILE, encoding="utf-8") as fh:
            return fh.read().strip()
    valor = secrets.token_hex(32)
    with open(SECRET_KEY_FILE, "w", encoding="utf-8") as fh:
        fh.write(valor)
    os.chmod(SECRET_KEY_FILE, stat.S_IRUSR | stat.S_IWUSR)
    return valor


import datetime as _dt

app = Flask(__name__)
app.secret_key = _cargar_o_crear_secret_key()
app.config["PERMANENT_SESSION_LIFETIME"] = _dt.timedelta(days=30)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def hay_clave_de_acceso_configurada():
    # ACCESS_PASSWORD como variable de entorno (recomendado en Render) o el
    # archivo local (uso en la Mac).
    return bool(os.environ.get("ACCESS_PASSWORD")) or os.path.exists(PASSWORD_FILE)


def guardar_clave_de_acceso(valor):
    # method="pbkdf2:sha256" explicito: el default de werkzeug (scrypt) requiere
    # que el modulo hashlib del sistema tenga soporte OpenSSL scrypt, que no
    # esta disponible en este Python -- pbkdf2 no depende de eso.
    with open(PASSWORD_FILE, "w", encoding="utf-8") as fh:
        fh.write(generate_password_hash(valor.strip(), method="pbkdf2:sha256"))
    os.chmod(PASSWORD_FILE, stat.S_IRUSR | stat.S_IWUSR)


def clave_de_acceso_es_correcta(valor):
    desde_env = os.environ.get("ACCESS_PASSWORD")
    if desde_env:
        return secrets.compare_digest(valor, desde_env)
    if not hay_clave_de_acceso_configurada():
        return True
    with open(PASSWORD_FILE, encoding="utf-8") as fh:
        hash_guardado = fh.read().strip()
    return check_password_hash(hash_guardado, valor)


LOGIN_PAGE = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Ingresar — Agente de Formularios Triple A</title>
<style>
  body { font-family: -apple-system, sans-serif; max-width: 400px; margin: 100px auto; padding: 0 20px; color: #1a1a1a; }
  input[type=password] { width: 100%; font-size: 15px; padding: 10px; box-sizing: border-box; margin-top: 10px; }
  button { background: #0b6cb3; color: white; border: none; padding: 12px 22px; font-size: 15px;
           border-radius: 6px; cursor: pointer; margin-top: 14px; width: 100%; }
  .error { background: #fde8e8; border: 1px solid #e08a8a; padding: 10px 14px; border-radius: 6px; margin: 14px 0; font-size: 14px; }
</style>
</head>
<body>
  <div style="text-align:center;"><img src="/static/logo_triple_a.jpg" alt="Triple A Seguros" style="max-width:180px; margin-bottom:10px;"></div>
  <h2>Agente de formularios — Seguros Triple A</h2>
  <p>Ingresá la clave de acceso para continuar.</p>
  {% if error %}<div class="error">Clave incorrecta.</div>{% endif %}
  <form method="post" autocomplete="off">
    <input type="text" style="position:absolute; left:-9999px;" tabindex="-1" aria-hidden="true">
    <input type="password" name="clave" id="clave-input" placeholder="Clave de acceso"
           autocomplete="new-password" autocorrect="off" autocapitalize="off" spellcheck="false" required>
    <button type="submit">Entrar</button>
  </form>
  <script>
    var campo = document.getElementById('clave-input');
    function limpiar() { campo.value = ''; }
    limpiar();
    setTimeout(limpiar, 100);
    setTimeout(limpiar, 400);
    campo.addEventListener('focus', function() {
      if (campo.dataset.tocado !== '1') { campo.value = ''; }
    });
    campo.addEventListener('input', function() { campo.dataset.tocado = '1'; });
  </script>
</body>
</html>
"""


def get_api_key():
    """Nunca se imprime ni se loguea en ningun lado -- solo se lee y se pasa
    directamente al proceso hijo que la necesita."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, encoding="utf-8") as fh:
            valor = fh.read().strip()
        if valor:
            return valor
    return os.environ.get("ANTHROPIC_API_KEY")


def guardar_api_key(valor):
    valor = valor.strip()
    with open(KEY_FILE, "w", encoding="utf-8") as fh:
        fh.write(valor)
    os.chmod(KEY_FILE, stat.S_IRUSR | stat.S_IWUSR)  # solo el dueño puede leer/escribir


CONFIG_PAGE = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Configurar clave de API</title>
<style>
  body { font-family: -apple-system, sans-serif; max-width: 600px; margin: 60px auto; padding: 0 20px; color: #1a1a1a; }
  input[type=password] { width: 100%; font-size: 15px; padding: 10px; box-sizing: border-box; }
  button { background: #0b6cb3; color: white; border: none; padding: 12px 22px; font-size: 15px;
           border-radius: 6px; cursor: pointer; margin-top: 14px; }
  .ok { background: #e8f6ec; border: 1px solid #7bc79e; padding: 10px 14px; border-radius: 6px; margin: 14px 0; font-size: 14px; }
  a { color: #0b6cb3; }
</style>
</head>
<body>
  <h2>Configurar tu clave de API de Anthropic</h2>
  <p>Pegá acá la clave que copiaste de console.anthropic.com (empieza con <code>sk-ant-</code>).
  Se guarda solo en tu computadora, en un archivo que solo vos podés leer -- nunca se muestra en pantalla despues de guardarla.</p>
  {% if guardado %}<div class="ok">Clave guardada correctamente.</div>{% endif %}
  <form method="post" action="/configurar/guardar">
    <input type="password" name="clave" placeholder="sk-ant-..." autocomplete="off" required>
    <br>
    <button type="submit">Guardar clave</button>
  </form>

  <hr style="margin: 30px 0;">

  <h2>Clave de acceso para el equipo</h2>
  <p>Esta es la clave que van a usar tus socios/equipo para entrar a la página (no es la clave de
  Anthropic). {% if clave_acceso_configurada %}Ya hay una configurada -- si ponés una nueva, reemplaza
  la anterior.{% else %}Todavía no hay ninguna configurada -- por ahora la página es de acceso libre.
  {% endif %}</p>
  {% if guardado_acceso %}<div class="ok">Clave de acceso guardada.</div>{% endif %}
  <form method="post" action="/configurar/guardar-acceso">
    <input type="password" name="clave_acceso" placeholder="Nueva clave de acceso" autocomplete="off" required>
    <br>
    <button type="submit">Guardar clave de acceso</button>
  </form>

  <p><a href="/">&larr; Volver</a></p>
</body>
</html>
"""

PAGE = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Agente de Formularios Triple A</title>
<style>
  body { font-family: -apple-system, sans-serif; color: #1a1a1a; margin: 0; padding: 0; }
  h1 { font-size: 22px; }
  textarea { width: 100%; height: 220px; font-size: 14px; padding: 10px; box-sizing: border-box; }
  button { background: #0b6cb3; color: white; border: none; padding: 12px 22px; font-size: 15px;
           border-radius: 6px; cursor: pointer; margin-top: 12px; }
  button:hover { background: #095a94; }
  .aviso { background: #fff6e0; border: 1px solid #e8c766; padding: 10px 14px; border-radius: 6px; margin: 14px 0; font-size: 14px; }
  .ok { background: #e8f6ec; border: 1px solid #7bc79e; padding: 10px 14px; border-radius: 6px; margin: 14px 0; font-size: 14px; }
  .error { background: #fde8e8; border: 1px solid #e08a8a; padding: 10px 14px; border-radius: 6px; margin: 14px 0; font-size: 13px; white-space: pre-wrap; }
  .doc { border: 1px solid #ddd; border-radius: 8px; padding: 14px; margin: 16px 0; }
  .doc img { max-width: 100%; border: 1px solid #eee; margin-top: 8px; }
  a.btn { display: inline-block; margin-top: 8px; text-decoration: none; color: #0b6cb3; font-weight: 600; }
  .faltantes { color: #9a6700; font-size: 13px; }
  .revision { background: #fdecec; border: 1px solid #e08a8a; color: #a12a2a; padding: 12px 16px; border-radius: 6px; margin: 14px 0; font-size: 14px; }
  .revision ul { margin: 6px 0 0 0; padding-left: 20px; }
  .revision li { margin-bottom: 4px; }
  .revision b { color: #a12a2a; }
  input[type=file] { margin-top: 6px; }
  .o { text-align: center; color: #888; margin: 10px 0; font-size: 13px; }
</style>
</head>
<body>
  <div style="background:#033860;padding:0 20px;display:flex;align-items:center;gap:0;font-family:-apple-system,sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.25);">
    <span style="color:#fff;font-weight:700;font-size:14px;padding:14px 20px 14px 0;white-space:nowrap;">Triple A Seguros</span>
    <a href="/" style="color:#fff;text-decoration:none;padding:14px 20px;font-size:14px;border-bottom:3px solid #4C8CB8;display:block;">Formularios</a>
    <a href="/refutador" style="color:rgba(255,255,255,.65);text-decoration:none;padding:14px 20px;font-size:14px;border-bottom:3px solid transparent;display:block;">Refutador de Reclamos</a>
    <span style="flex:1;"></span>
    <a href="/logout" style="color:rgba(255,255,255,.65);text-decoration:none;font-size:13px;">Cerrar sesión</a>
  </div>
  <div style="max-width:780px;margin:30px auto;padding:0 20px;">
  <div style="text-align:center;"><img src="/static/logo_triple_a.jpg" alt="Triple A Seguros" style="max-width:160px; margin-bottom:6px;"></div>
  <h1>Agente de formularios — Seguros Triple A</h1>

  <p>Elegí la aseguradora y el tipo de trámite, pegá el mensaje del cliente y/o subí archivos.
  Podés agregar varios archivos de a poco, sin perder los que ya elegiste.</p>
  <form method="post" action="/generar" enctype="multipart/form-data" id="form-generar">
    <label for="aseguradora_producto" style="font-size:13px; font-weight:600;">Aseguradora / tipo de trámite</label><br>
    <select name="aseguradora_producto" id="aseguradora_producto" required
            style="width:100%; font-size:15px; padding:10px; box-sizing:border-box; margin:6px 0 16px;">
      <option value="" disabled {% if not seleccion_previa %}selected{% endif %}>Elegir opción</option>
      {% for grupo in grupos_opciones %}
        <optgroup label="{{ grupo.nombre }}">
          {% for op in grupo.opciones %}
            <option value="{{ op.valor }}" {% if not op.disponible %}disabled{% endif %} {% if op.valor==seleccion_previa %}selected{% endif %}>
              {{ op.etiqueta }}{% if not op.disponible %} (próximamente){% endif %}
            </option>
          {% endfor %}
        </optgroup>
      {% endfor %}
    </select>
    <textarea name="mensaje" placeholder="Ej: Nombre completo: Juan Perez...">{{ mensaje_previo }}</textarea>
    <div class="o">— y/o —</div>

    <label for="cedula_pasaporte" style="font-size:13px; font-weight:600;">Fotos de cédula o pasaporte</label><br>
    <input type="file" name="cedula_pasaporte" id="cedula_pasaporte" accept="application/pdf,image/*" multiple>
    <ul id="lista-cedula_pasaporte" style="list-style:none; padding:0; margin:6px 0 0; font-size:13px;"></ul>

    <br>
    <label for="info_cliente" style="font-size:13px; font-weight:600;">Cuestionario / información del cliente</label><br>
    <input type="file" name="info_cliente" id="info_cliente" accept="application/pdf,image/*" multiple>
    <ul id="lista-info_cliente" style="list-style:none; padding:0; margin:6px 0 0; font-size:13px;"></ul>

    <br><br>
    <label for="tarjeta_foto" style="font-size:13px; font-weight:600;">Foto de la tarjeta de crédito (opcional, para el formulario de pago)</label><br>
    <small style="color:#666;">Se usa una sola vez para leer los datos y se borra del servidor apenas se genera el PDF.</small><br>
    <input type="file" name="tarjeta_foto" id="tarjeta_foto" accept="image/*">
    <br><br>
    <label for="vehiculo_doc" style="font-size:13px; font-weight:600;">Registro vehicular o proforma del vehículo (opcional, para solicitudes de auto)</label><br>
    <input type="file" name="vehiculo_doc" id="vehiculo_doc" accept="application/pdf,image/*">
    <br>
    <button type="submit" id="btn-generar">Generar los formularios</button>
  </form>

  <script>
    document.getElementById('form-generar').addEventListener('submit', function () {
      var btn = document.getElementById('btn-generar');
      btn.disabled = true;
      btn.textContent = 'Generando... esto puede tardar un minuto';
    });
  </script>

  <script>
    function activarAcumulador(inputId, listaId) {
      var input = document.getElementById(inputId);
      var lista = document.getElementById(listaId);
      var archivos = [];

      function refrescar() {
        var dt = new DataTransfer();
        archivos.forEach(function (f) { dt.items.add(f); });
        input.files = dt.files;

        lista.innerHTML = '';
        archivos.forEach(function (f, idx) {
          var li = document.createElement('li');
          li.style.cssText = 'display:flex; align-items:center; justify-content:space-between; ' +
            'background:#f4f6f8; border-radius:5px; padding:5px 8px; margin-bottom:4px;';
          var nombre = document.createElement('span');
          nombre.textContent = f.name;
          nombre.style.cssText = 'overflow:hidden; text-overflow:ellipsis; white-space:nowrap; margin-right:8px;';
          var quitar = document.createElement('button');
          quitar.type = 'button';
          quitar.textContent = '×';
          quitar.title = 'Quitar este archivo';
          quitar.style.cssText = 'background:#e08a8a; color:white; border:none; border-radius:4px; ' +
            'width:22px; height:22px; cursor:pointer; font-size:14px; line-height:1; flex-shrink:0;';
          quitar.addEventListener('click', function () {
            archivos.splice(idx, 1);
            refrescar();
          });
          li.appendChild(nombre);
          li.appendChild(quitar);
          lista.appendChild(li);
        });
      }

      input.addEventListener('change', function () {
        Array.prototype.forEach.call(input.files, function (f) {
          archivos.push(f);
        });
        refrescar();
      });
    }

    activarAcumulador('cedula_pasaporte', 'lista-cedula_pasaporte');
    activarAcumulador('info_cliente', 'lista-info_cliente');
  </script>

  {% if error %}
    <div class="error"><b>Ocurrio un error:</b>\n{{ error }}</div>
  {% endif %}

  {% if resultado %}
    {% if usando_demo %}
      <div class="aviso">
        No encontre una ANTHROPIC_API_KEY configurada, asi que esto se generó con datos de EJEMPLO
        para que veas cómo se ve el resultado final. Cuando configuren su clave, este mismo botón
        va a extraer los datos reales del mensaje de arriba.
      </div>
    {% else %}
      <div class="ok">Datos extraídos y formularios generados.</div>
    {% endif %}

    {% for doc in resultado %}
      <div class="doc">
        <b>{{ doc.titulo }}</b><br>
        <img src="/preview/{{ run_id }}/{{ doc.preview }}">
        <br>
        <a class="btn" href="/descargar/{{ run_id }}/{{ doc.pdf }}">Descargar PDF completo</a>
      </div>
    {% endfor %}

    {% if revision %}
      <div class="revision">
        <b>Falta completar / confirmar con el cliente:</b>
        <ul>
          {% if revision.ambiguo_principal %}<li>Quién es el Asegurado Principal / titular — no quedó claro en el documento.</li>{% endif %}
          {% if revision.falta_medico_detallado %}<li>Las preguntas médicas detalladas (Sección A/B) no fueron contestadas de forma específica.</li>{% endif %}
          {% if revision.falta_pep %}<li>Persona Expuesta Políticamente (PEP) — no fue preguntado en el documento de origen.</li>{% endif %}
          {% for c in revision.campos_faltantes %}<li>{{ c }}</li>{% endfor %}
        </ul>
        {% if revision.notas %}<p><b>Notas:</b> {{ revision.notas }}</p>{% endif %}
      </div>
    {% endif %}

    {% if campos_faltantes %}
      <div class="faltantes">Campos que el mensaje no mencionaba: {{ campos_faltantes }}</div>
    {% endif %}
  {% endif %}
  </div>
</body>
</html>
"""


def generar_previews(run_dir, pdf_filename):
    import fitz
    pdf_path = os.path.join(run_dir, pdf_filename)
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(dpi=110)
    preview_name = pdf_filename.replace(".pdf", "_p1.png")
    pix.save(os.path.join(run_dir, preview_name))
    return preview_name


@app.before_request
def exigir_login():
    rutas_publicas = {"login", "static"}
    if request.endpoint in rutas_publicas:
        return None
    if not hay_clave_de_acceso_configurada():
        return None  # todavia no configuraron clave -- no bloquear (modo inicial)
    if session.get("autenticado"):
        return None
    return redirect(url_for("login", next=request.path))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = False
    if request.method == "POST":
        clave = request.form.get("clave", "")
        if clave_de_acceso_es_correcta(clave):
            session["autenticado"] = True
            session.permanent = True
            destino = request.args.get("next") or url_for("index")
            return redirect(destino)
        error = True
    return render_template_string(LOGIN_PAGE, error=error)


@app.route("/logout")
def logout():
    session.pop("autenticado", None)
    return redirect(url_for("login"))


def _opciones_default():
    opciones = opciones_aseguradora_producto()
    return opciones, None


@app.route("/", methods=["GET"])
def index():
    opciones, seleccion_previa_default = _opciones_default()
    grupos_opciones = opciones_agrupadas_aseguradora_producto()
    ultimo = session.pop("ultimo_resultado", None)
    if ultimo:
        return render_template_string(
            PAGE, mensaje_previo=ultimo.get("mensaje_previo", ""), error=ultimo.get("error"),
            resultado=ultimo.get("resultado"), usando_demo=ultimo.get("usando_demo", False),
            campos_faltantes=None, run_id=ultimo.get("run_id"),
            clave_configurada=bool(get_api_key()), revision=ultimo.get("revision"),
            opciones=opciones, grupos_opciones=grupos_opciones,
            seleccion_previa=ultimo.get("seleccion_previa", seleccion_previa_default),
        )
    return render_template_string(PAGE, mensaje_previo="", error=None, resultado=None,
                                   usando_demo=False, campos_faltantes=None, run_id=None,
                                   clave_configurada=bool(get_api_key()), revision=None,
                                   opciones=opciones, grupos_opciones=grupos_opciones,
                                   seleccion_previa=seleccion_previa_default)


@app.route("/configurar", methods=["GET"])
def configurar():
    return render_template_string(CONFIG_PAGE, guardado=False, guardado_acceso=False,
                                   clave_acceso_configurada=hay_clave_de_acceso_configurada())


@app.route("/configurar/guardar", methods=["POST"])
def configurar_guardar():
    clave = request.form.get("clave", "")
    if clave.strip():
        guardar_api_key(clave)
    return redirect(url_for("index"))


@app.route("/configurar/guardar-acceso", methods=["POST"])
def configurar_guardar_acceso():
    clave_acceso = request.form.get("clave_acceso", "")
    if clave_acceso.strip():
        guardar_clave_de_acceso(clave_acceso)
        session["autenticado"] = True  # quien la configura no queda afuera
    return render_template_string(CONFIG_PAGE, guardado=False, guardado_acceso=True,
                                   clave_acceso_configurada=hay_clave_de_acceso_configurada())


EXTENSIONES_PERMITIDAS = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".gif"}

CAMPOS_TARJETA_SENSIBLES = {
    "numero_tarjeta", "tarjeta_codigo_seguridad", "tarjeta_fecha_exp_mmaa",
}


def _borrar_datos_tarjeta(tarjeta_path, *json_paths):
    """Borra la foto de la tarjeta y los datos sensibles de tarjeta de los JSON intermedios,
    una vez que ya se generó el PDF de pago (no hace falta conservarlos despues de eso)."""
    if tarjeta_path and os.path.exists(tarjeta_path):
        os.remove(tarjeta_path)
    for path in json_paths:
        if not path or not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            datos = json.load(fh)
        cambiado = False
        for clave in CAMPOS_TARJETA_SENSIBLES:
            if clave in datos:
                datos[clave] = "[borrado tras generar el PDF]"
                cambiado = True
        if "pago_tarjeta" in datos:
            datos["pago_tarjeta"] = "[borrado tras generar el PDF]"
            cambiado = True
        if cambiado:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(datos, fh, ensure_ascii=False, indent=2)


@app.route("/generar", methods=["POST"])
def generar():
    mensaje = request.form.get("mensaje", "").strip()
    seleccion = request.form.get("aseguradora_producto", "")
    archivos_subidos = [f for f in request.files.getlist("cedula_pasaporte") if f and f.filename]
    archivos_subidos += [f for f in request.files.getlist("info_cliente") if f and f.filename]
    tarjeta_file = request.files.get("tarjeta_foto")
    vehiculo_file = request.files.get("vehiculo_doc")

    run_id = time.strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(RUNS_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)

    usando_demo = False
    revision = None

    try:
        mensaje_path = None
        if mensaje:
            mensaje_path = os.path.join(run_dir, "mensaje.txt")
            with open(mensaje_path, "w", encoding="utf-8") as fh:
                fh.write(mensaje)

        adjunto_paths = []
        for i, f in enumerate(archivos_subidos):
            ext = os.path.splitext(f.filename)[1].lower()
            if ext not in EXTENSIONES_PERMITIDAS:
                continue
            destino = os.path.join(run_dir, f"adjunto_{i}{ext}")
            f.save(destino)
            adjunto_paths.append(destino)

        tarjeta_path = None
        if tarjeta_file and tarjeta_file.filename:
            ext = os.path.splitext(tarjeta_file.filename)[1].lower()
            if ext in EXTENSIONES_PERMITIDAS and ext != ".pdf":
                tarjeta_path = os.path.join(run_dir, f"tarjeta{ext}")
                tarjeta_file.save(tarjeta_path)

        vehiculo_path = None
        if vehiculo_file and vehiculo_file.filename:
            ext = os.path.splitext(vehiculo_file.filename)[1].lower()
            if ext in EXTENSIONES_PERMITIDAS:
                vehiculo_path = os.path.join(run_dir, f"vehiculo{ext}")
                vehiculo_file.save(vehiculo_path)

        datos_crudos_path = os.path.join(run_dir, "extraccion_cruda.json")
        datos_combinados_path = os.path.join(run_dir, "datos_combinados.json")

        extraction_ok = False
        tarjeta_texto_detectada = False
        api_key = get_api_key()
        if api_key and (mensaje_path or adjunto_paths or tarjeta_path or vehiculo_path):
            child_env = dict(os.environ, ANTHROPIC_API_KEY=api_key)
            cmd = ["python3", "src/extract_family.py", "--salida", datos_crudos_path,
                   "--salida-plana", datos_combinados_path]
            if mensaje_path:
                cmd += ["--texto", mensaje_path]
            for p in adjunto_paths:
                cmd += ["--adjunto", p]
            if tarjeta_path:
                cmd += ["--tarjeta", tarjeta_path]
            if vehiculo_path:
                cmd += ["--vehiculo", vehiculo_path]
            proc = subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True, env=child_env, timeout=180)
            if proc.returncode == 0:
                extraction_ok = True
                with open(datos_crudos_path, encoding="utf-8") as fh:
                    crudo = json.load(fh)
                tarjeta_texto_detectada = bool(crudo.get("tarjeta_desde_texto"))
                if tarjeta_texto_detectada:
                    # El cliente escribio los datos de la tarjeta en el mensaje -- no lo
                    # conservamos ni en el archivo en disco ni en la sesion/pantalla, misma
                    # logica que con la foto. Se hace apenas se detecta (antes de generar los
                    # PDFs) para que ningun camino de error mas abajo llegue a exponerlo.
                    if mensaje_path and os.path.exists(mensaje_path):
                        os.remove(mensaje_path)
                    mensaje = "[mensaje borrado tras leer los datos de la tarjeta de crédito]"
                rev = crudo.get("revision", {})
                ap_cumplimiento = crudo.get("asegurado_principal", {}).get("cumplimiento", {})
                revision = {
                    "ambiguo_principal": rev.get("quien_es_asegurado_principal_es_ambiguo", False),
                    "falta_medico_detallado": rev.get("requiere_cuestionario_medico_detallado", True),
                    "falta_pep": not ap_cumplimiento.get("pep_fue_preguntado_en_el_documento", False),
                    "campos_faltantes": rev.get("campos_faltantes", []),
                    "notas": rev.get("notas_para_el_corredor"),
                }
            else:
                raise RuntimeError(f"Fallo la extraccion:\n{proc.stderr[-3000:]}")

        if not extraction_ok:
            usando_demo = True
            with open(DEMO_DATA_PATH, encoding="utf-8") as fh:
                datos = json.load(fh)
            with open(datos_combinados_path, "w", encoding="utf-8") as fh:
                json.dump(datos, fh, ensure_ascii=False, indent=2)

        docs = documentos_para(seleccion)

        def _generar_un_documento(doc):
            pdf_name = doc["salida"]
            out_pdf = os.path.join(run_dir, pdf_name)
            subprocess.run(
                ["python3", doc["script"], doc["mapping"], datos_combinados_path, out_pdf],
                cwd=BASE_DIR, check=True, capture_output=True, text=True, timeout=60,
            )
            preview = generar_previews(run_dir, pdf_name)
            return {"titulo": doc["titulo"], "pdf": pdf_name, "preview": preview}

        # Los documentos son independientes entre si (mismo datos_combinados_path de
        # solo lectura), asi que se generan en paralelo en vez de uno por uno.
        with ThreadPoolExecutor(max_workers=max(1, len(docs))) as executor:
            resultado = list(executor.map(_generar_un_documento, docs))

        if tarjeta_path or tarjeta_texto_detectada:
            _borrar_datos_tarjeta(tarjeta_path, datos_crudos_path, datos_combinados_path)

        session["ultimo_resultado"] = {
            "mensaje_previo": mensaje, "error": None, "resultado": resultado,
            "usando_demo": usando_demo, "run_id": run_id, "revision": revision,
            "seleccion_previa": seleccion,
        }
        return redirect(url_for("index"))

    except subprocess.TimeoutExpired:
        session["ultimo_resultado"] = {
            "mensaje_previo": mensaje,
            "error": "La extracción tardó demasiado y se cortó. Probá de nuevo, con un mensaje "
                     "más corto o con menos archivos adjuntos a la vez.",
            "resultado": None, "usando_demo": False, "run_id": None, "revision": None,
            "seleccion_previa": seleccion,
        }
        return redirect(url_for("index"))

    except (Exception, SystemExit):
        session["ultimo_resultado"] = {
            "mensaje_previo": mensaje, "error": traceback.format_exc(),
            "resultado": None, "usando_demo": False, "run_id": None, "revision": None,
            "seleccion_previa": seleccion,
        }
        return redirect(url_for("index"))


@app.route("/preview/<run_id>/<filename>")
def preview(run_id, filename):
    return send_from_directory(os.path.join(RUNS_DIR, run_id), filename)


@app.route("/descargar/<run_id>/<filename>")
def descargar(run_id, filename):
    return send_from_directory(os.path.join(RUNS_DIR, run_id), filename, as_attachment=True)


@app.route("/refutador")
def refutador():
    return render_template("refutador.html")


@app.route("/api/claude", methods=["POST"])
def api_claude():
    if hay_clave_de_acceso_configurada() and not session.get("autenticado"):
        return jsonify({"error": {"message": "No autenticado."}}), 401
    api_key = get_api_key()
    if not api_key:
        return jsonify({"error": {"message": "API key no configurada."}}), 500
    payload = request.get_data()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=150) as resp:
            return resp.read(), resp.status, {"Content-Type": "application/json"}
    except urllib.error.HTTPError as e:
        return e.read(), e.code, {"Content-Type": "application/json"}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8765, debug=False)
