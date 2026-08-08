"""
Genera un mapeo candidato: nombre_de_campo_pdf -> etiqueta de texto más cercana.
Cruza la posicion (rect) de cada campo AcroForm con las palabras extraidas por pdfplumber
en la misma pagina, para adivinar que dato representa cada campo.

Uso:
    python3 build_mapping.py <template.pdf> <salida.json>
"""
import sys
import json
from pypdf import PdfReader
import pdfplumber


def full_field_name(annot):
    parts = []
    obj = annot
    while obj is not None:
        t = obj.get("/T")
        if t is not None:
            parts.insert(0, str(t))
        parent = obj.get("/Parent")
        obj = parent.get_object() if parent is not None else None
    return ".".join(parts)


def on_state(annot):
    ap = annot.get("/AP")
    if ap is None:
        return None
    n = ap.get("/N")
    if n is None or not hasattr(n, "keys"):
        return None
    states = [str(k) for k in n.keys() if str(k) != "/Off"]
    return states[0] if states else None


def get_form_fields_with_rects(pdf_path):
    reader = PdfReader(pdf_path)
    fields = []
    for page_index, page in enumerate(reader.pages):
        annots = page.get("/Annots")
        if not annots:
            continue
        for annot_ref in annots:
            annot = annot_ref.get_object()
            if annot.get("/Subtype") != "/Widget":
                continue
            name = full_field_name(annot)
            if not name:
                continue
            ft = annot.get("/FT")
            parent = annot.get("/Parent")
            if ft is None and parent is not None:
                ft = parent.get_object().get("/FT")
            rect = annot.get("/Rect")
            fields.append({
                "page": page_index,
                "name": name,
                "type": str(ft) if ft else None,
                "on_state": on_state(annot),
                "rect": [float(x) for x in rect],
            })
    return fields


def get_words_by_page(pdf_path):
    words_by_page = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
            page_height = float(page.height)
            norm = []
            for w in words:
                # pdfplumber origin is top-left; PDF rect origin is bottom-left. Convert.
                norm.append({
                    "text": w["text"],
                    "x0": w["x0"],
                    "x1": w["x1"],
                    "top": page_height - w["top"],
                    "bottom": page_height - w["bottom"],
                })
            words_by_page.append(norm)
    return words_by_page


def nearest_label(field, words):
    fx0, fy0, fx1, fy1 = field["rect"]
    fy_mid = (fy0 + fy1) / 2
    candidates = []
    for w in words:
        wy_mid = (w["top"] + w["bottom"]) / 2
        same_line = abs(wy_mid - fy_mid) < 8
        to_left = w["x1"] <= fx0 + 2
        above = (w["bottom"] >= fy1 - 2) and (w["bottom"] - fy1) < 20 and abs(w["x0"] - fx0) < 150
        if same_line and to_left:
            dist = fx0 - w["x1"]
            candidates.append((dist, w["text"], "left"))
        elif above:
            dist = (w["bottom"] - fy1) + abs(w["x0"] - fx0) * 0.3
            candidates.append((dist, w["text"], "above"))
    candidates.sort(key=lambda c: c[0])
    return [c[1] for c in candidates[:6]]


def main():
    pdf_path = sys.argv[1]
    out_path = sys.argv[2]

    fields = get_form_fields_with_rects(pdf_path)
    words_by_page = get_words_by_page(pdf_path)

    result = []
    for f in fields:
        words = words_by_page[f["page"]] if f["page"] < len(words_by_page) else []
        labels = nearest_label(f, words)
        result.append({
            "field": f["name"],
            "type": f["type"],
            "on_state": f["on_state"],
            "page": f["page"] + 1,
            "rect": f["rect"],
            "label_guess": " ".join(labels),
        })

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)

    print(f"{len(result)} campos escritos en {out_path}")


if __name__ == "__main__":
    main()
