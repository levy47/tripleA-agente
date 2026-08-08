"""
PDF llenable (AcroForm) del cuestionario de cliente para la Autorizacion para
Debito de Tarjeta de Credito (TCR) de Optima, mismo motor que
generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_tcr_optima_pdf.py --salida cuestionario_tcr_optima.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Autorización de Débito de Tarjeta de Crédito",
                     subtitulo_banner="Triple A Seguros — Óptima")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. Además, adjunte por separado una foto "
              "de su cédula y una foto clara de la tarjeta de crédito (frente y dorso) — de ahí se "
              "leen automáticamente su nombre, número de cédula, y el número, vencimiento, código "
              "de seguridad y banco emisor de la tarjeta, por lo que no hace falta que los escriba "
              "aquí.", size=9)
    b.parrafo("IMPORTANTE: NO escriba los datos de su tarjeta de crédito en este documento.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Pólizas a cobrar")
    b.parrafo("Complete al menos la Póliza 1. Puede agregar hasta 2 pólizas.", size=8)
    b.espacio(4)
    for i in range(1, 3):
        b.campos_fila([f"Póliza {i} — Número de póliza:", "Nombre del asegurado:"])

    b.seccion("2. Monto y forma de pago")
    b.opciones("Frecuencia del cargo:", ["Anual", "Semestral", "Mensual"])
    b.campo_texto("Suma en balboas (B/.) que autoriza cargar:")

    b.seccion("3. Contacto")
    b.dos_campos("Correo electrónico:", "Celular:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_tcr_optima.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
