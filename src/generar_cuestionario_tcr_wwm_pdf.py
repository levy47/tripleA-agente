"""
PDF llenable (AcroForm) del cuestionario de cliente para la Autorizacion de Pago
de Primas Mediante Tarjeta de Credito (TCR) de WorldWide Medical, mismo motor
que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_tcr_wwm_pdf.py --salida cuestionario_tcr_wwm.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Pago de Primas con Tarjeta de Crédito",
                     subtitulo_banner="Triple A Seguros — WorldWide Medical")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. Además, adjunte por separado una foto "
              "de su cédula o pasaporte y una foto clara de la tarjeta de crédito (frente y dorso) "
              "— de ahí se leen automáticamente su nombre, el nombre del tarjetahabiente, el banco "
              "emisor, y el número, vencimiento y código de seguridad de la tarjeta, por lo que no "
              "hace falta que los escriba aquí.", size=9)
    b.parrafo("IMPORTANTE: NO escriba los datos de su tarjeta de crédito en este documento.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Asegurado (si es distinto del tarjetahabiente)")
    b.campo_texto("Nombre del asegurado:")

    b.seccion("2. Datos de la póliza")
    b.campos_fila(["Número de póliza:", "Número de factura:", "Número de certificado (si aplica):"])
    b.campo_texto("Valor de la prima (US$):")

    b.seccion("3. Forma de pago")
    b.opciones("Frecuencia de cobro deseada:", ["Anual", "Semestral", "Trimestral", "Mensual"])

    b.seccion("4. Contacto")
    b.dos_campos("Correo electrónico:", "Celular:")
    b.campo_texto("Observaciones (opcional):", alto_campo=30, multilinea=True)

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_tcr_wwm.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
