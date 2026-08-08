"""
PDF llenable (AcroForm) del cuestionario de cliente para Solicitud Combinada de
Seguro de Pan-American Life, mismo motor que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_palig_pdf.py --salida cuestionario_palig.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL

PREGUNTAS_MEDICAS = [
    "¿Infecciones?",
    "¿Desórdenes de ojos, oídos, nariz o garganta?",
    "¿Depresión, desórdenes psiquiátricos, convulsiones, migraña, parálisis u otro trastorno "
    "neurológico?",
    "¿Alergias, asma, bronquitis, dificultad respiratoria, tos crónica o tuberculosis?",
    "¿Corazón, arritmia, soplo, circulatorios, presión arterial, trombosis o colesterol alto?",
    "¿Esófago, estómago, intestinos, páncreas, hepatitis, colitis, hígado o vesícula?",
    "¿Riñones, tracto urinario, infección urinaria, piedras renales o insuficiencia renal?",
    "¿Columna, espalda, ciática, escoliosis, artritis, gota, músculos o articulaciones?",
    "¿Tumores benignos o cáncer?",
    "¿Anemia, leucemia, linfoma, u otro trastorno de sangrado o coagulación?",
    "¿Diabetes, azúcar alta o baja, tiroides u otro trastorno hormonal/endocrino?",
    "¿Próstata, prostatitis, u otra dificultad urinaria?",
    "¿Enfermedades de transmisión sexual u otro trastorno reproductivo?",
    "¿Mamas, ovarios, trompas o útero (quistes, miomas, endometriosis)?",
    "¿Piel (psoriasis, vitiligo, melanoma, lesiones)?",
    "¿Enfermedades congénitas, hereditarias, genéticas o autoinmunes?",
    "¿VIH o SIDA?",
    "¿Ha estado bajo observación/seguimiento por un especialista?",
    "¿Pies (juanetes, pies planos, u otra alteración)?",
    "¿Cualquier otra enfermedad, lesión, hospitalización o cirugía no mencionada?",
    "¿Positivo a COVID-19, o tratamiento/hospitalización por COVID?",
    "¿Síntomas posteriores a COVID (pulmonares, renales, hepáticos, cardíacos, neurológicos)?",
    "¿Recibió el esquema completo de vacunación contra COVID-19?",
]


def construir(salida, num_solicitantes_adicionales=5):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Solicitud de Seguro de Salud",
                     subtitulo_banner="Triple A Seguros — Pan-American Life")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. Adjunte foto de cédula/pasaporte de "
              "cada persona a asegurar.", size=9)
    b.parrafo("IMPORTANTE: NO incluya los datos de su tarjeta de crédito en este documento.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Asegurado principal (Solicitante 1)")
    b.campo_texto("Nombre completo:")
    b.dos_campos("Cédula/pasaporte:", "Fecha de nacimiento:")
    b.opciones("Sexo:", ["F", "M"])
    b.dos_campos("Estado civil:", "Peso y estatura:")
    b.dos_campos("Ocupación:", "Descripción exacta de la ocupación:")
    b.campo_texto("Dirección de trabajo:")
    b.dos_campos("Correo electrónico personal:", "Correo electrónico de trabajo:")
    b.dos_campos("Teléfono de trabajo:", "Nacionalidad:")
    b.dos_campos("Ingreso anual:", "País(es) donde tributa por sus ingresos:")

    b.seccion("2. Información demográfica")
    b.campo_texto("Dirección residencial completa (ciudad, provincia, país, tiempo de "
                   "residencia):")
    b.dos_campos("Teléfono de casa:", "Celular:")
    b.si_no("¿Tiene usted y todos los solicitantes residencia legal y permanente en Panamá?")
    b.si_no("¿Reside usted o algún solicitante en Estados Unidos 6+ meses continuos al año?")
    b.si_no("¿Usted o algún solicitante tiene múltiple nacionalidad o pasaporte?")
    b.campo_texto("Si es Sí: ¿de qué país(es)?")

    b.seccion("3. Persona Expuesta Políticamente (PEP)")
    b.si_no("¿Es usted o alguna de las personas nombradas en esta solicitud una Persona "
            "Expuesta Políticamente?")
    b.campo_texto("Si es Sí: favor indicar cargo:")

    b.seccion("4. Solicitantes adicionales (dependientes)")
    b.parrafo(f"Complete un bloque por dependiente (hasta {num_solicitantes_adicionales}).",
              size=8)
    b.campo_texto("Liste cada dependiente en una línea: parentesco, nombre completo, cédula, "
                   "correo electrónico, sexo, estado civil, ocupación, fecha de nacimiento, "
                   "peso y estatura:", alto_campo=45, multilinea=True)
    b.si_no("¿Alguno de los solicitantes practica algún deporte de forma profesional?")
    b.campo_texto("Si es Sí: quién, y qué deporte practica:")

    b.seccion("5. Plan de interés")
    b.campo_texto("Producto (IMM Private Client, Health Trust, Plan de Enfermedades Graves) y "
                   "deducible de interés:")
    b.campo_texto("Fecha de efectividad que solicita para la cobertura:")

    b.seccion("6. Beneficiarios")
    b.campo_texto("Liste cada beneficiario en una línea: nombre completo, parentesco, "
                   "porcentaje, cédula/identificación:", alto_campo=30, multilinea=True)

    b.seccion("7. Otros seguros")
    b.si_no("¿La cobertura solicitada reemplazará a otro seguro existente?")
    b.si_no("¿Después de comenzar la cobertura, tendrá usted o algún dependiente otro seguro "
            "médico?")
    b.si_no("¿Alguna solicitud de seguro de salud/accidentes/vida ha sido negada, restringida o "
            "recargada?")
    b.si_no("¿Ha solicitado seguro o ha sido asegurado antes por Pan-American Life de Panamá?")
    b.campo_texto("Si contestó Sí a alguna: compañía, producto, número de póliza, detalles:")

    b.seccion("8. Médico de cabecera")
    b.campo_texto("Nombre del médico, especialidad y teléfono (por cada solicitante):")

    b.seccion("9. Cuestionario médico")
    b.parrafo("Conteste Sí o No para cada persona a asegurar. Detalle al final: quién, "
              "condición, período, tratamiento, médico.", size=8)
    for pregunta in PREGUNTAS_MEDICAS:
        b.si_no(pregunta)
    b.espacio(4)
    b.campo_texto("Detalle de respuestas \"Sí\" (quién, número de pregunta, condición, período, "
                   "tratamiento, médico):", alto_campo=45, multilinea=True)

    b.seccion("10. Exámenes, maternidad, medicamentos e historia familiar")
    b.si_no("¿Alguno de los solicitantes ha tenido un examen pediátrico o ginecológico "
            "reciente?")
    b.si_no("¿Alguna solicitante ha estado embarazada anteriormente, o está embarazada "
            "actualmente?")
    b.campo_texto("Si es Sí: quién, número de embarazos, complicaciones (si aplica):")
    b.si_no("¿Alguno de los solicitantes toma medicamentos de forma continua?")
    b.campo_texto("Si es Sí: quién, medicamento, motivo, dosis:")
    b.si_no("¿Historia familiar de diabetes, hipertensión, enfermedad del corazón, cáncer o "
            "enfermedad congénita/hereditaria?")
    b.campo_texto("Si es Sí: quién, familiar afectado, condición:")

    b.seccion("11. Hábitos")
    b.si_no("¿Alguno de los solicitantes fuma, consume nicotina, alcohol o drogas ilícitas?")
    b.campo_texto("Si es Sí: quién, tipo, cantidad, frecuencia, previo o actual:")

    b.seccion("12. Firma")
    b.dos_campos("Nombre:", "Fecha:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_palig.pdf")
    parser.add_argument("--solicitantes", type=int, default=5)
    args = parser.parse_args()
    construir(args.salida, num_solicitantes_adicionales=args.solicitantes)


if __name__ == "__main__":
    main()
