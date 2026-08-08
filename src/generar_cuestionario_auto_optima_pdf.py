"""
PDF llenable (AcroForm) del cuestionario de cliente para la Solicitud de Seguro
de Automovil de Optima, mismo motor que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_auto_optima_pdf.py --salida cuestionario_auto_optima.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Solicitud de Seguro de Automóvil",
                     subtitulo_banner="Triple A Seguros — Óptima")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Por favor complete todos los campos de este PDF y guárdelo antes de enviarlo de "
              "vuelta.", size=9)
    b.parrafo("IMPORTANTE: no incluya los datos de su tarjeta de crédito en este documento.",
              size=9, bold=True)
    b.parrafo("Además de este cuestionario, adjunte por favor una foto o PDF legible de su "
              "cédula o pasaporte, y el registro vehicular (tarjeta de circulación) o la "
              "proforma del vehículo. Los datos del vehículo (marca, modelo, año, color, placa, "
              "motor, chasis) se extraen automáticamente de ese documento, por lo que no hace "
              "falta que los escriba aquí.", size=9)
    b.espacio(6)

    b.seccion("1. Datos personales del asegurado")
    b.campo_texto("Nombre completo:")
    b.dos_campos("Cédula o pasaporte:", "Nacionalidad:")
    b.opciones("Sexo:", ["F", "M"])
    b.dos_campos("País de residencia:", "Estado civil:")
    b.dos_campos("Fecha de nacimiento:", "Celular:")
    b.campo_texto("Empresa o lugar donde trabaja:")
    b.campo_texto("Correo electrónico:")

    b.seccion("2. Dirección residencial")
    b.dos_campos("Provincia:", "Distrito:")
    b.dos_campos("Corregimiento:", "Urbanización o barriada:")

    b.seccion("3. Datos de la póliza deseada")
    b.dos_campos("Vigencia deseada — Desde:", "Vigencia deseada — Hasta:")
    b.si_no("¿El vehículo tiene acreedor hipotecario (préstamo con algún banco o financiera)?")
    b.campo_texto("Si contestó Sí: indique el nombre del banco o financiera:")
    b.campo_texto("Valor del auto (para efectos de la póliza):")
    b.si_no("¿Habrá un conductor adicional del vehículo, aparte de usted?")
    b.dos_campos("Si contestó Sí: nombre completo del conductor adicional:",
                 "Fecha de nacimiento del conductor adicional:")
    b.opciones("Experiencia de manejo:", ["Menos de 2 años", "3 a 5 años", "Más de 6 años"])
    b.si_no("¿Ha tenido siniestros (accidentes o reclamos) en los últimos 5 años?")
    b.opciones("Frecuencia de pago deseada:", ["Mensual", "Trimestral", "Semestral", "Anual"])

    b.seccion("4. Firma")
    b.dos_campos("Nombre:", "Fecha:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_auto_optima.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
