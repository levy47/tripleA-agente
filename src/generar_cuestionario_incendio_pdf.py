"""
PDF llenable (AcroForm) del cuestionario de cliente para Solicitud de Seguro
de Incendio de Óptima, mismo motor que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_incendio_pdf.py --salida cuestionario_incendio.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Solicitud de Seguro de Incendio",
                     subtitulo_banner="Triple A Seguros")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. Esta información es para asegurar el "
              "bien inmueble (edificio y/o contenido), no para un seguro de salud o de vida.", size=9)
    b.parrafo("IMPORTANTE: NO incluya los datos de su tarjeta de crédito en este documento — esos "
              "se los solicitamos por separado, por un canal seguro.", size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Datos personales del propietario/asegurado")
    b.dos_campos("Primer nombre:", "Segundo nombre:")
    b.dos_campos("Apellido paterno:", "Apellido materno:")
    b.dos_campos("Cédula o pasaporte:", "Nacionalidad:")
    b.opciones("Sexo:", ["F", "M"])
    b.dos_campos("País de residencia:", "Estado civil:")

    b.seccion("2. Dirección residencial del propietario/asegurado")
    b.parrafo("Dirección donde usted vive actualmente (no necesariamente la del bien a asegurar).",
              size=8)
    b.dos_campos("Provincia:", "Distrito:")
    b.dos_campos("Corregimiento:", "Urbanización o barriada:")

    b.seccion("3. Datos del bien a asegurar")
    b.opciones("Tipo de póliza:", ["Fija", "Declarativa", "Edificio en construcción"])
    b.opciones("Bien cubierto:", ["Edificio", "Contenido", "Edificio y Contenido"])
    b.campo_texto("Si incluye Contenido: especifique qué contenido (muebles, equipos, mercancía, "
                   "etc.):")
    b.dos_campos("Vigencia deseada — Desde:", "Vigencia deseada — Hasta:")
    b.campo_texto("¿Existe un acreedor hipotecario sobre este bien? Indique el nombre del banco o "
                   "entidad (deje en blanco si no aplica):")
    b.dos_campos("Suma asegurada del edificio (US$):", "Suma asegurada del contenido (US$):")
    b.campo_texto("Ocupación del edificio (uso que se le da: vivienda, oficina, comercio, etc.):")

    b.seccion("4. Construcción del edificio")
    b.parrafo("Indique el material principal de cada parte del edificio.", size=8)
    b.opciones("Paredes:", ["Concreto", "Metal", "Madera", "Otro"])
    b.campo_texto("Si marcó \"Otro\" en Paredes, especifique:")
    b.opciones("Pisos:", ["Concreto", "Metal", "Madera", "Otro"])
    b.campo_texto("Si marcó \"Otro\" en Pisos, especifique:")
    b.opciones("Techo:", ["Concreto", "Metal", "Madera", "Otro"])
    b.campo_texto("Si marcó \"Otro\" en Techo, especifique:")

    b.seccion("5. Medidas de seguridad")
    b.parrafo("Indique con cuáles de estas medidas cuenta el bien a asegurar actualmente.", size=8)
    b.si_no("¿Alarma de incendio?")
    b.si_no("¿Extintores?")
    b.si_no("¿Rociadores (sprinklers)?")
    b.si_no("¿Detector de humo?")
    b.campo_texto("Estación de bomberos más cercana:")

    b.seccion("6. Coberturas y otros seguros")
    b.campo_texto("Coberturas adicionales que desea solicitar (ej. terremoto, huracán, robo, etc.):",
                   alto_campo=30, multilinea=True)
    b.campo_texto("Lucro cesante o pérdida de renta (si aplica, indique detalle; si no aplica, "
                   "escriba \"No aplica\"):")
    b.si_no("¿Existen otros seguros sobre los mismos bienes en ésta u otra compañía?")

    b.seccion("7. Forma de pago")
    b.opciones("Frecuencia de pago deseada:", ["Mensual", "Trimestral", "Semestral", "Anual"])
    b.parrafo("Los datos de la tarjeta de crédito para el cobro se solicitan por separado, nunca en "
              "este documento.", size=8)

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_incendio.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
