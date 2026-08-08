"""
Llena un PDF con campos AcroForm rellenables, usando un archivo de mapeo
(campo_pdf -> data_key) y un diccionario de datos del cliente.

Uso:
    python3 fill_pdf.py <mapping.json> <datos.json> <salida.pdf>
"""
import sys
import json
from pypdf import PdfReader, PdfWriter


def load_mapping(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_data(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def build_field_values(mapping, data):
    values = {}
    for pdf_field, spec in mapping["fields"].items():
        ftype = spec["type"]
        key = spec.get("data_key")

        if ftype == "manual":
            continue

        if ftype == "checkbox_group":
            selected = data.get(key)
            options = spec.get("options")
            if options is not None:
                # Radio group: un solo campo PDF (con varios "Kids"/widgets) que acepta
                # distintos on_state segun el valor -- ej. TipoTarjeta con 3 opciones.
                # "options" mapea data_value -> {"on_state": "/EstadoExacto"}.
                opt = options.get(str(selected)) if selected is not None else None
                values[pdf_field] = opt["on_state"] if opt else "/Off"
            else:
                match_value = spec.get("value")
                on_state = spec.get("on_state", "/Sí")
                if selected is not None and str(selected) == str(match_value):
                    values[pdf_field] = on_state
                else:
                    values[pdf_field] = "/Off"
            continue

        if key not in data or data[key] in (None, ""):
            continue

        values[pdf_field] = str(data[key])

    return values


def main():
    mapping_path, data_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    mapping = load_mapping(mapping_path)
    data = load_data(data_path)

    template_path = mapping["template"]
    reader = PdfReader(template_path)
    writer = PdfWriter()
    writer.append(reader)

    field_values = build_field_values(mapping, data)

    for page in writer.pages:
        writer.update_page_form_field_values(page, field_values, auto_regenerate=False)

    writer.set_need_appearances_writer(True)

    with open(out_path, "wb") as fh:
        writer.write(fh)

    print(f"PDF generado: {out_path} ({len(field_values)} campos llenados)")


if __name__ == "__main__":
    main()
