"""
PDF llenable (AcroForm) del cuestionario KYC - Persona Natural, mismo motor que
generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_kyc_natural_pdf.py --salida cuestionario_kyc_natural.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario Conoce a su Cliente (KYC) — Persona Natural",
                     subtitulo_banner="Triple A Seguros")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. NO incluya datos de tarjeta de crédito.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Datos personales")
    b.opciones("¿Quién completa este formulario?",
               ["Contratante", "Asegurado", "Corredor", "Pagador", "Cía. de Seguros", "Beneficiario"])
    b.parrafo("(Adjunte junto con este PDF una foto legible de su cédula o pasaporte)", size=8)
    b.dos_campos("Nombre completo:", "Fecha de nacimiento:")
    b.dos_campos("Género (F/M):", "Nacionalidad:")
    b.dos_campos("País de nacimiento:", "País de residencia:")
    b.campo_texto("Dirección residencial completa:")
    b.dos_campos("Teléfono / celular:", "Correo electrónico:")

    b.seccion("2. Datos laborales")
    b.dos_campos("Profesión / ocupación:", "Empresa donde labora:")
    b.campo_texto("Dirección de la empresa:")
    b.campo_texto("Si es independiente o comerciante, ¿a qué actividad se dedica?")
    b.opciones("Ingreso anual aproximado (US$):",
               ["Menos de 10 mil", "10 mil a 30 mil", "30 mil a 50 mil", "Más de 50 mil"])
    b.dos_campos("¿Otras fuentes de ingreso? ¿Cuáles y cuánto?", "País(es) donde tributa / NIT:")

    b.seccion("3. Persona Expuesta Políticamente (PEP)")
    b.parrafo("¿Es usted, tiene un familiar directo, o es colaborador cercano de una Persona "
              "Expuesta Políticamente? Obligatorio por regulación.", size=8)
    b.si_no("Responder:")
    b.campo_texto("Si es Sí: quién, cargo y relación:")

    b.seccion("4. Firma")
    b.dos_campos("Nombre:", "Fecha:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_kyc_natural.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
