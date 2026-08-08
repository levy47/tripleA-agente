"""
PDF llenable (AcroForm) del cuestionario KYC - Persona Juridica, mismo motor que
generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_kyc_juridico_pdf.py --salida cuestionario_kyc_juridico.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor

from generar_cuestionario_pdf import Constructor, AZUL


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario Conoce a su Cliente (KYC) — Persona Jurídica",
                     subtitulo_banner="Triple A Seguros")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. NO incluya datos de tarjeta de crédito.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Rol / Datos de la sociedad")
    b.opciones("¿Quién completa este formulario?",
               ["Contratante", "Asegurado", "Corredor", "Pagador", "Cía. de Seguros", "Beneficiario"])
    b.dos_campos("Razón social:", "Razón comercial (si es distinta):")
    b.dos_campos("RUC:", "NIT (si es distinto):")
    b.campo_texto("Dirección física completa:")
    b.dos_campos("País de constitución:", "Fecha de constitución:")
    b.dos_campos("País donde opera:", "Actividad a la que se dedica:")
    b.dos_campos("Teléfono:", "Correo electrónico:")
    b.campo_texto("País(es) donde tributa por sus ingresos:")

    b.seccion("2. Directores, dignatarios y accionistas (10%+)")
    b.parrafo("Adjunte copia de cédula o pasaporte de cada uno.", size=8)
    b.parrafo("Directores y dignatarios — liste cada uno en una línea con estos 6 datos: nombre "
              "completo, cédula/pasaporte, fecha de nacimiento, dirección, cargo, nacionalidad.",
              size=8)
    b.campo_texto("Directores y dignatarios:", alto_campo=45, multilinea=True)
    b.parrafo("Accionistas / beneficiarios finales — liste cada uno en una línea con estos 5 "
              "datos: nombre completo, cédula/pasaporte, fecha de nacimiento, % de "
              "participación, nacionalidad.", size=8)
    b.campo_texto("Accionistas / beneficiarios finales:", alto_campo=45, multilinea=True)

    b.seccion("3. Representante legal y agente residente")
    b.campo_texto("Representante legal / apoderado: nombre completo, cédula, fecha de "
                   "nacimiento y dirección (adjunte copia de cédula o pasaporte):")
    b.campo_texto("Agente residente: nombre y dirección:")

    b.seccion("4. Persona Expuesta Políticamente (PEP)")
    b.parrafo("¿Algún director, accionista, representante legal o apoderado es, tiene familiar "
              "directo, o es colaborador cercano de una Persona Expuesta Políticamente?", size=8)
    b.si_no("Responder:")
    b.campo_texto("Si es Sí: quién, cargo y relación:")

    b.seccion("5. Perfil financiero y firma")
    b.opciones("Ingreso anual aproximado de la sociedad (balboas):",
               ["Menos de 50 mil", "50 mil a 250 mil", "250 mil a 500 mil", "500 mil a 3 millones",
                "3 a 5 millones", "5 a 10 millones", "Más de 10 millones"])
    b.campo_texto("Documentos adjuntos: cédula del Representante Legal, Certificado del "
                   "Registro Público, Aviso de Operación (si aplica).")
    b.dos_campos("Nombre de quien firma:", "Fecha:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_kyc_juridico.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
