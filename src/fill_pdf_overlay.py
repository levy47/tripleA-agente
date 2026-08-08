"""
Llena un PDF que NO tiene campos AcroForm (texto dibujado como contornos
vectoriales, no extraible), superponiendo una capa de texto/marcas generada
con reportlab en las coordenadas indicadas por un archivo de mapeo.

El mapeo (mapping.json) usa coordenadas en sistema reportlab/PDF nativo
(origen abajo-izquierda), ya con el flip de Y aplicado -- ver
mappings/kyc_persona_natural.json para el formato y comentarios en el
prompt/README del proyecto.

Tipos de campo soportados:
  - "text": dibuja data[data_key] en (x, y) de la pagina indicada.
  - "date_split": separa data[data_key] (formato input_format, ej "dd/mm/aaaa")
    por "/" y dibuja cada parte en su propia posicion (parts.day/month/year).
  - "checkbox_mark": dibuja una "X" en options[valor] si data[data_key] ==
    alguna de las keys de options (comparacion case-insensitive con str()).
  - "manual": se ignora (campos que se llenan a mano, ej. firma).

Uso:
    python3 fill_pdf_overlay.py <mapping.json> <datos.json> <salida.pdf>
"""
import sys
import json
import io

from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def draw_text(c, x, y, value, font_size):
    if value in (None, ""):
        return
    texto = str(value)
    c.setFont("Helvetica", font_size)
    # Tapa con un fondo blanco cualquier texto ya impreso en el PDF original debajo
    # (ej. placeholders tipo "0.0%" preimpresos en algunas celdas de tabla), para
    # que no quede superpuesto con el valor real.
    ancho = c.stringWidth(texto, "Helvetica", font_size)
    c.setFillColorRGB(1, 1, 1)
    c.rect(x - 8, y - 2, ancho + 16, font_size + 3, fill=1, stroke=0)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(x, y, texto)


def draw_mark(c, x, y, font_size):
    c.setFont("Helvetica-Bold", font_size)
    c.drawString(x, y, "X")


def build_overlay_pages(mapping, data, num_pages):
    """Devuelve una lista (1-indexed via dict) de buffers PDF de una sola
    pagina cada uno, para las paginas que tengan al menos un campo."""
    page_w = mapping.get("page_width", 595.32)
    page_h = mapping.get("page_height", 841.92)
    default_font_size = mapping.get("font_size", 9)

    # Agrupar campos por pagina
    fields_by_page = {}
    for spec in mapping["fields"]:
        page_num = spec.get("page", 1)
        fields_by_page.setdefault(page_num, []).append(spec)

    overlays = {}
    for page_num, specs in fields_by_page.items():
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=(page_w, page_h))
        font_size = default_font_size

        for spec in specs:
            ftype = spec.get("type")
            key = spec.get("data_key")

            if ftype == "manual":
                continue

            elif ftype == "text":
                value = data.get(key) if key else None
                fs = spec.get("font_size", font_size)
                draw_text(c, spec["x"], spec["y"], value, fs)

            elif ftype == "date_split":
                raw = data.get(key)
                if raw in (None, ""):
                    continue
                sep = "/"
                parts_val = [p.strip() for p in str(raw).split(sep)]
                # input_format ej "dd/mm/aaaa" -> orden de las partes
                fmt_parts = spec.get("input_format", "dd/mm/aaaa").split(sep)
                parts_spec = spec.get("parts", {})
                name_map = {"dd": "day", "mm": "month", "aaaa": "year", "yyyy": "year"}
                for fmt_token, val in zip(fmt_parts, parts_val):
                    part_name = name_map.get(fmt_token.lower())
                    if part_name and part_name in parts_spec:
                        pos = parts_spec[part_name]
                        fs = spec.get("font_size", font_size)
                        draw_text(c, pos["x"], pos["y"], val, fs)

            elif ftype == "checkbox_mark":
                value = data.get(key) if key else None
                if value in (None, ""):
                    continue
                options = spec.get("options", {})
                value_norm = str(value).strip().lower()
                for opt_key, pos in options.items():
                    if opt_key.strip().lower() == value_norm:
                        # Las marcas van dentro de casilleros chicos (~7pt), asi
                        # que por defecto usan una fuente mas chica que el texto.
                        fs = spec.get("font_size", 7)
                        draw_mark(c, pos["x"], pos["y"], fs)
                        break

        # showPage() asegura que la pagina se genere aunque no se haya dibujado
        # nada en ella (un canvas sin ninguna operacion de dibujo produce un PDF
        # de 0 paginas al guardar, lo que rompe el merge mas abajo).
        c.showPage()
        c.save()
        buf.seek(0)
        overlays[page_num] = buf

    return overlays


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    mapping_path, data_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    mapping = load_json(mapping_path)
    data = load_json(data_path)

    template_path = mapping["template"]
    reader = PdfReader(template_path)
    writer = PdfWriter()
    writer.append(reader)

    num_pages = len(writer.pages)
    overlays = build_overlay_pages(mapping, data, num_pages)

    filled_count = 0
    for page_num, buf in overlays.items():
        idx = page_num - 1
        if idx < 0 or idx >= len(writer.pages):
            continue
        overlay_reader = PdfReader(buf)
        if not overlay_reader.pages:
            continue
        overlay_page = overlay_reader.pages[0]
        writer.pages[idx].merge_page(overlay_page)
        filled_count += 1

    with open(out_path, "wb") as fh:
        writer.write(fh)

    print(f"PDF generado: {out_path} ({filled_count} paginas con overlay de {len(mapping['fields'])} campos definidos)")


if __name__ == "__main__":
    main()
