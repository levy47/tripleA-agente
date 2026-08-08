"""
PDF llenable (AcroForm) del cuestionario de cliente para la Solicitud de Seguro
de Automovil de Aliado Seguros, mismo motor que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_auto_aliado_pdf.py --salida cuestionario_auto_aliado.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Solicitud de Seguro de Automóvil — Aliado Seguros",
                     subtitulo_banner="Triple A Seguros — Aliado")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Por favor complete todos los campos de este PDF y guárdelo antes de enviarlo de "
              "vuelta.", size=9)
    b.parrafo("Además de este cuestionario, adjunte por favor una foto o PDF legible de su "
              "cédula o pasaporte, y el registro vehicular (tarjeta de circulación) o la "
              "proforma del vehículo. Los datos físicos del vehículo (marca, modelo, año, "
              "color, placa, motor, chasis) se extraen automáticamente de ese documento, por lo "
              "que no hace falta que los escriba aquí.", size=9)
    b.parrafo("IMPORTANTE: si va a pagar con tarjeta de crédito, no escriba los datos de la "
              "tarjeta en este documento — adjunte por separado una foto de la tarjeta.", size=9,
              bold=True)
    b.espacio(6)

    b.seccion("1. Datos personales del asegurado")
    b.parrafo("Los siguientes datos no se pueden leer automáticamente de su cédula o pasaporte, "
              "por lo que le pedimos completarlos aquí.", size=8)
    b.espacio(4)
    b.dos_campos("Provincia de residencia:", "Distrito:")
    b.campo_texto("Corregimiento:")
    b.campo_texto("País de residencia (si es distinto de Panamá):")
    b.dos_campos("Profesión:", "Ocupación / cargo:")
    b.si_no("¿Tributa impuestos en un país distinto a Panamá?")
    b.campo_texto("Si contestó Sí: indique el o los países, y su Id Tributario:")

    b.seccion("2. Persona Expuesta Políticamente (PEP)")
    b.parrafo("Obligatorio por regulación — no se puede omitir.", size=8)
    b.espacio(4)
    b.si_no("¿Es usted una Persona Expuesta Políticamente, o familiar cercano, o estrecho "
            "colaborador de una?")
    b.campo_texto("Si contestó Sí: indique el nombre y cargo de la persona PEP con la cual se "
                  "encuentra relacionado:")

    b.seccion("3. Vigencia de la póliza deseada")
    b.dos_campos("Vigencia deseada — Desde (dd/mm/aaaa):", "Vigencia deseada — Hasta (dd/mm/aaaa):")
    b.si_no("¿El vehículo tiene acreedor hipotecario (préstamo con algún banco o financiera)?")
    b.campo_texto("Si contestó Sí: indique el nombre del banco o financiera (Acreedor Hipotecario):")

    b.seccion("4. Forma de pago deseada")
    b.opciones("¿Cómo desea pagar?:", ["Tarjeta de crédito (VISA)", "Tarjeta de crédito (Master Card)",
                                        "ACH (débito bancario)"])
    b.campo_texto("Si paga con tarjeta: nombre del banco emisor:")
    b.opciones("Frecuencia de pago deseada:", ["Trimestral", "Semestral", "Anual", "Mensual"])
    b.parrafo("Recuerde: si su forma de pago es con tarjeta de crédito, NO escriba el número de "
              "tarjeta ni la fecha de vencimiento aquí — adjunte una foto de la tarjeta por "
              "separado, por un canal seguro.", size=8, bold=True)

    b.seccion("5. Firma")
    b.dos_campos("Nombre completo:", "Fecha:")

    b.nueva_pagina("6. Solo si el contratante es una empresa (persona jurídica)")
    b.parrafo("Complete esta sección ÚNICAMENTE si quien contrata la póliza es una empresa, y no "
              "una persona natural.", size=9, bold=True)
    b.espacio(6)
    b.campo_texto("Nombre de la Razón Social:")
    b.dos_campos("RUC:", "País de Constitución:")
    b.campo_texto("Dirección física de la empresa:")
    b.campo_texto("Actividad económica de la empresa:")
    b.dos_campos("Nombre del Representante Legal:", "Cédula/Pasaporte del Representante Legal:")
    b.si_no("¿Tributa la empresa impuestos en un país distinto a Panamá?")
    b.campo_texto("Si contestó Sí: indique el o los países, y el Id Tributario de la empresa:")
    b.si_no("¿Existe una persona expuesta políticamente (PEP) en los miembros de esta persona "
            "jurídica (directores, dignatarios, representante legal, apoderado, socios, "
            "accionistas o beneficiarios finales)?")
    b.campo_texto("Si contestó Sí: indique el nombre y cargo de la persona PEP con la cual se "
                  "encuentra relacionada:")

    b.espacio(6)
    b.parrafo("Accionistas/Socios/Asociados (hasta 4). Complete un bloque por cada uno:", size=9,
              bold=True)
    b.espacio(4)
    for i in range(1, 5):
        b.parrafo(f"Accionista/Socio {i}", size=9, color=AZUL, bold=True)
        b.campos_fila(["Nombre completo:", "Cédula/Pasaporte/RUC:", "Nacionalidad:", "%:"])
        b.espacio(2)

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_auto_aliado.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
