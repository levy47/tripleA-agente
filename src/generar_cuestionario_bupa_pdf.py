"""
PDF llenable (AcroForm) del cuestionario de cliente para Solicitud de Salud de
Bupa Panamá, mismo motor que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_bupa_pdf.py --salida cuestionario_bupa.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL

PREGUNTAS_SECCION1 = [
    "¿Padece o ha padecido enfermedad o accidente en los últimos 5 años?",
    "¿Está o ha estado ingresado, o intervenido en algún centro hospitalario?",
    "¿Se encuentra actualmente bajo algún tratamiento prescrito por un médico?",
    "¿Tiene algún síntoma o dolor persistente o reiterado, no diagnosticado?",
    "¿Está embarazada o ha estado embarazada alguna vez (con complicaciones)?",
]

PREGUNTAS_SECCION2 = [
    "Enfermedades de corazón o sistema circulatorio (hipertensión, angina, arritmias, etc.)",
    "Trastornos del sistema endocrino (diabetes, tiroides)",
    "Trastornos del sistema respiratorio (asma, EPOC, bronquitis)",
    "Trastornos digestivos (gastritis, úlceras, hepatitis, cálculos, hernias)",
    "Dermatología (eczema, dermatitis, psoriasis, acné)",
    "Sistema neurológico (esclerosis múltiple, epilepsia, migrañas)",
    "Sistema músculo-esquelético (artritis, dolor de espalda, fracturas, cirugías)",
    "Urología / sistema genitourinario masculino",
    "Urología / ginecología",
    "Hematología e inmunología (Lupus, anemias, autoinmunes)",
    "Enfermedades de ojos, nariz, oídos o garganta",
    "Psiquiatría y psicología (trastornos de ánimo, alimentación, TDAH)",
    "Cáncer o enfermedades linfoproliferativas",
    "Enfermedades congénitas o hereditarias",
    "Enfermedades infecciosas relevantes o de transmisión sexual",
    "Cualquier otra enfermedad, lesión, accidente o cirugía no mencionada",
]


def construir(salida, num_dependientes=4):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Solicitud de Seguro de Salud",
                     subtitulo_banner="Triple A Seguros — Bupa Panamá")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. Adjunte foto de cédula/pasaporte de "
              "cada persona a asegurar.", size=9)
    b.parrafo("IMPORTANTE: NO incluya los datos de su tarjeta de crédito en este documento.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Contratante")
    b.campo_texto("Nombre completo o razón social:")
    b.dos_campos("Cédula/RUC:", "Fecha de nacimiento:")
    b.opciones("Sexo:", ["F", "M"])
    b.dos_campos("Estado civil:", "Peso y estatura:")
    b.dos_campos("País de nacimiento:", "País de residencia:")
    b.dos_campos("Ocupación o profesión:", "Ingresos anuales promedio:")
    b.campo_texto("Lugar(es) donde tributa:")
    b.campo_texto("Dirección residencial completa:")
    b.dos_campos("Teléfono residencial/celular:", "Correo electrónico:")
    b.dos_campos("Lugar de trabajo y cargo:", "Dirección y teléfono laboral:")

    b.seccion("2. Asegurado principal titular (solo si es diferente al contratante)")
    b.campo_texto("Mismos datos que arriba para esta persona, si aplica:")

    b.seccion("3. Persona Expuesta Políticamente (PEP)")
    b.si_no("¿Es el contratante o el asegurado titular una Persona Expuesta Políticamente, "
            "tiene parentesco con una, o es asociado cercano?")
    b.campo_texto("Si es Sí: detalle:")
    b.si_no("¿Es contribuyente fiscal? Indique número de RUC y DV si es Sí:")

    b.seccion("4. Integrantes adicionales (dependientes)")
    b.parrafo(f"Complete un bloque por dependiente (hasta {num_dependientes}).", size=8)
    b.campo_texto("Liste cada dependiente en una línea: nombre completo, parentesco, estado "
                   "civil, sexo, peso y estatura, nacionalidad, país de residencia, tipo y "
                   "número de identificación, fecha de nacimiento, profesión u ocupación, "
                   "correo electrónico:", alto_campo=45, multilinea=True)
    b.si_no("Si algún dependiente es recién nacido: ¿nació por tratamiento de infertilidad, "
            "adopción o maternidad subrogada?")

    b.seccion("5. Plan de interés")
    b.campo_texto("Producto y deducible de interés:")

    b.seccion("6. Contacto de emergencia")
    b.campo_texto("Nombre completo, nacionalidad, tipo y número de identificación, teléfono, "
                   "correo electrónico:")

    b.seccion("7. Otros seguros")
    b.si_no("¿Cuenta el solicitante o algún dependiente con cobertura de gastos médicos "
            "mayores vigente en otra compañía?")
    b.campo_texto("Si es Sí: compañía, número de póliza, fecha de renovación, deducible:")

    b.seccion("8. Cuestionario médico — sección 1")
    b.parrafo("Conteste Sí o No para cada persona a asegurar. Indique el nombre del "
              "solicitante en cada pregunta afirmativa.", size=8)
    for pregunta in PREGUNTAS_SECCION1:
        b.si_no(pregunta)

    b.seccion("9. Cuestionario médico — sección 2 (por sistema/categoría)")
    for pregunta in PREGUNTAS_SECCION2:
        b.si_no(pregunta)
    b.espacio(4)
    b.campo_texto("Detalle de respuestas \"Sí\" (nombre del solicitante, número de pregunta, "
                   "descripción, zona del cuerpo, tratamiento, fechas, medicamentos):",
                   alto_campo=50, multilinea=True)

    b.seccion("10. Historial médico y hábitos")
    b.si_no("¿Ha tenido examen pediátrico, ginecológico o de rutina en los últimos 5 años?")
    b.campo_texto("Si es Sí: quién, tipo de examen, fecha, resultado:")
    b.si_no("¿Fuma, consume nicotina, alcohol o drogas ilegales?")
    b.campo_texto("Si es Sí: quién, tipo, cuánto tiempo, cantidad por día:")
    b.si_no("¿Historial familiar de diabetes, hipertensión, cáncer o desorden cardiovascular "
            "congénito/hereditario?")
    b.campo_texto("Si es Sí: quién, familiar (padre/madre/hermano/hijo), desorden:")
    b.campo_texto("Médico tratante (si aplica): nombre, especialidad, teléfono, para quién:")

    b.seccion("11. Forma de pago")
    b.opciones("Modalidad de la póliza:", ["Anual", "Semestral", "Trimestral", "Mensual"])
    b.opciones("Método de pago:", ["Tarjeta de crédito", "Giro bancario", "Cheque personal",
                                   "Transferencia bancaria"])

    b.seccion("12. Firma")
    b.dos_campos("Nombre:", "Fecha:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_bupa.pdf")
    parser.add_argument("--dependientes", type=int, default=4)
    args = parser.parse_args()
    construir(args.salida, num_dependientes=args.dependientes)


if __name__ == "__main__":
    main()
