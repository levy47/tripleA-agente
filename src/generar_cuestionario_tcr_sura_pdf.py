"""
PDF llenable (AcroForm) del cuestionario de cliente para la Autorizacion de
Debito Automatico (Tarjeta de Credito) de Sura (Seguros Suramericana), mismo
motor que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_tcr_sura_pdf.py --salida cuestionario_tcr_sura.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Autorización de Débito Automático",
                     subtitulo_banner="Triple A Seguros — Sura (Tarjeta de Crédito)")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. Además, adjunte por separado una foto "
              "de su cédula o pasaporte y una foto clara de la tarjeta de crédito (frente y dorso) "
              "— de ahí se leen automáticamente su nombre, número de cédula, y el número, "
              "vencimiento y código de seguridad de la tarjeta, por lo que no hace falta que los "
              "escriba aquí.", size=9)
    b.parrafo("IMPORTANTE: NUNCA escriba los datos de su tarjeta de crédito (número, vencimiento, "
              "código de seguridad) en este documento.", size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Pólizas a debitar")
    b.parrafo("Complete al menos la Póliza 1. Puede agregar hasta 6 pólizas.", size=8)
    b.espacio(4)
    for i in range(1, 7):
        b.campos_fila([f"Póliza {i} — Número de póliza:", "Cantidad de pagos:", "Prima:"])

    b.seccion("2. Asegurado (si es distinto de quien autoriza el débito)")
    b.dos_campos("Nombre del asegurado:", "Identificación del asegurado:")

    b.seccion("3. Datos de contacto")
    b.dos_campos("Correo electrónico:", "Celular:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_tcr_sura.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
