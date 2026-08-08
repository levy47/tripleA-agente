"""
PDF llenable (AcroForm) del cuestionario de cliente para la Autorizacion para el
Plan de Descuento / Tarjeta de Credito (TCR) de la Internacional de Seguros, mismo
motor que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_tcr_is_pdf.py --salida cuestionario_tcr_is.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Autorización de Débito de Tarjeta de Crédito",
                     subtitulo_banner="Triple A Seguros — Internacional de Seguros")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. Además, adjunte por separado una foto "
              "de su cédula o pasaporte y una foto clara de la tarjeta de crédito (frente y dorso) "
              "— de ahí se leen automáticamente su nombre, número de cédula, el nombre del "
              "tarjetahabiente, el banco emisor, y el número, vencimiento y código de seguridad de "
              "la tarjeta, por lo que no hace falta que los escriba aquí.", size=9)
    b.parrafo("IMPORTANTE: NO escriba los datos de su tarjeta de crédito en este documento.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Pólizas a cobrar")
    b.parrafo("Complete al menos la Póliza 1. Puede agregar hasta 5 pólizas.", size=8)
    b.espacio(4)
    for i in range(1, 6):
        b.campos_fila([f"Póliza {i} — Nombre del asegurado:", "Número de póliza:", "Monto del descuento:"])

    b.seccion("2. Monto y forma de pago")
    b.campo_texto("Suma total en balboas (B/.) que autoriza descontar:")
    b.opciones("Frecuencia del descuento:", ["Mensual", "Trimestral", "Anual"])
    b.si_no("¿Autoriza la renovación automática de la póliza y del descuento?")

    b.seccion("3. Contacto")
    b.dos_campos("Correo electrónico:", "Celular:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_tcr_is.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
