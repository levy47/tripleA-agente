"""
PDF llenable (AcroForm) del cuestionario de cliente para la Autorizacion de pago
de Primas Por Tarjeta de Credito (TCR) de ASSA, mismo motor que
generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_tcr_assa_pdf.py --salida cuestionario_tcr_assa.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Autorización de Débito (Tarjeta de Crédito)",
                     subtitulo_banner="Triple A Seguros — ASSA")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. Además, adjunte por separado una foto "
              "de su cédula y una foto clara de la tarjeta de crédito (frente y dorso) — de ahí se "
              "leen automáticamente su nombre (tal como aparece en la tarjeta), número de cédula, y "
              "el número, vencimiento, código de seguridad y banco emisor de la tarjeta, por lo que "
              "no hace falta que los escriba aquí.", size=9)
    b.parrafo("IMPORTANTE: NO escriba los datos de su tarjeta de crédito en este documento.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Pólizas a debitar")
    b.parrafo("Complete al menos la Póliza 1. Puede agregar hasta 4 pólizas.", size=8)
    b.espacio(4)
    for i in range(1, 5):
        b.campos_fila([f"Póliza {i} — Nombre del asegurado:", "Número de póliza:",
                        "Día de cobro:", "Monto del descuento:"])

    b.seccion("2. Contacto")
    b.dos_campos("Correo electrónico:", "Celular:")
    b.campo_texto("Dirección completa:", alto_campo=30, multilinea=True)

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_tcr_assa.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
