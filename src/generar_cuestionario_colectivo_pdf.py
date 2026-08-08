"""
PDF llenable (AcroForm) del cuestionario de cliente para Solicitud de
Inscripcion - Seguro Colectivo de UniVivir (Vida + Medico Hospitalario +
Accidentes Personales), mismo motor que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_colectivo_pdf.py --salida cuestionario_colectivo.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL

PREGUNTAS_INICIALES = [
    "¿Goza usted y todos sus dependientes de buena salud mental y física?",
    "¿Tiene usted o alguno de sus dependientes algún defecto congénito o adquirido evidente o no "
    "físicamente?",
    "¿Ha sufrido usted o algún dependiente un accidente grave o intoxicaciones?",
    "¿Es usted o algún dependiente piloto o tripulante en aviones privados o comerciales?",
]

PREGUNTAS_SALUD = [
    "¿Se ha realizado usted o algún dependiente un examen, tratamiento o cirugía para cualquier "
    "afección médica?",
    "¿Se ha realizado usted o algún dependiente un papanicolau?",
    "¿Se ha realizado usted o algún dependiente una mamografía, ultrasonido o prueba especial?",
    "¿Está usted o algún dependiente embarazada?",
    "¿Ha tenido usted o alguna dependiente una pérdida de embarazo?",
    "¿Toma usted o algún dependiente medicamentos permanentes?",
    "¿Ha recibido usted o algún dependiente transfusiones de sangre?",
]

PREGUNTAS_ENFERMEDADES = [
    "Enfermedades del sistema nervioso (epilepsia, convulsiones, migrañas, parálisis, etc.)",
    "Trastornos mentales (psicosis, ansiedad, trastornos alimenticios, dependencia de sustancias)",
    "Enfermedades del corazón o del aparato circulatorio (hipertensión, infarto, arritmias, "
    "varices)",
    "Enfermedades de la sangre (anemia, hemofilia, leucemia, colesterol/triglicéridos altos)",
    "Trastornos autoinmunes (lupus, esclerosis múltiple, tiroiditis)",
    "Trastornos gastrointestinales (úlceras, cálculos biliares, reflujo, hepatitis, Crohn)",
    "Enfermedades del sistema endócrino (diabetes, obesidad, hipo/hipertiroidismo)",
    "Enfermedades del sistema osteomuscular (lumbago, ciática, artritis, hernias discales)",
    "Enfermedades del sistema respiratorio (asma, tuberculosis, EPOC, alergias)",
    "Enfermedades del sistema genito-urinario (próstata, riñones, ovarios, cáncer cérvico-"
    "uterino)",
    "Enfermedades de transmisión sexual (VIH/SIDA, VPH, hepatitis B/C)",
    "Enfermedades de ojos, oídos, nariz o boca (cataratas, glaucoma, sinusitis crónica)",
    "Enfermedades o lesiones de la piel (lunares atípicos, cáncer de piel)",
    "Secuelas de enfermedades infecciosas",
    "Tumores o enfermedades congénitas o hereditarias",
]


def construir(salida, num_dependientes=5):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Solicitud de Seguro Colectivo",
                     subtitulo_banner="Triple A Seguros — UniVivir (Vida, Médico y Accidentes)")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. Adjunte foto de cédula/pasaporte de "
              "cada persona a asegurar.", size=9)
    b.parrafo("IMPORTANTE: NO incluya los datos de su tarjeta de crédito en este documento.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Datos del asegurado")
    b.campo_texto("Nombre completo:")
    b.dos_campos("Cédula/pasaporte:", "Fecha de nacimiento:")
    b.opciones("Sexo:", ["F", "M"])
    b.dos_campos("Estado civil:", "Peso y estatura:")
    b.dos_campos("Profesión u ocupación:", "Cargo que desempeña:")
    b.campo_texto("Dirección residencial completa:")
    b.dos_campos("Provincia:", "Teléfono / celular:")
    b.campo_texto("Correo electrónico:")
    b.dos_campos("Contratante (empresa):", "Filial o división (si aplica):")

    b.seccion("2. Persona Expuesta Políticamente (PEP)")
    b.si_no("¿Es usted una persona políticamente expuesta?")
    b.campo_texto("Si es Sí: indicar cargo actual o anterior:")

    b.seccion("3. Autorización de pago de reclamaciones")
    b.dos_campos("Nombre de la cuenta:", "No. de cuenta:")
    b.dos_campos("Nombre del banco:", "Tipo de cuenta (Ahorro/Corriente):")
    b.campo_texto("Correo electrónico para envío de liquidaciones:")

    b.seccion("4. Dependientes")
    b.parrafo(f"Complete un bloque por dependiente (hasta {num_dependientes}).", size=8)
    b.campo_texto("Liste cada dependiente en una línea: nombre completo, parentesco, cédula/"
                   "pasaporte, nacionalidad, fecha de nacimiento, sexo, profesión u ocupación, "
                   "estatura y peso:", alto_campo=45, multilinea=True)

    b.seccion("5. Beneficiarios (Seguro de Vida y/o Accidentes Personales)")
    b.campo_texto("Beneficiarios principales: nombre completo, cédula/pasaporte, parentesco, "
                   "porcentaje (deben sumar 100%):", alto_campo=30, multilinea=True)
    b.campo_texto("Beneficiarios contingentes (si aplica, mismos datos):", alto_campo=20,
                   multilinea=True)

    b.seccion("6. Información adicional")
    b.si_no("¿Ha tenido usted o algún dependiente un seguro similar al que está solicitando?")
    b.campo_texto("Si es Sí: quién, qué seguro, con qué compañía, suma asegurada, vencimiento:")
    b.si_no("¿Usted o algún dependiente fuma o ha fumado, consume bebidas alcohólicas o drogas "
            "estupefacientes?")
    b.campo_texto("Si es Sí: quién, qué consume, frecuencia, desde/hasta cuándo:")
    b.si_no("¿Practica usted o algún dependiente algún deporte o actividad de riesgo?")
    b.campo_texto("Si es Sí: quién, qué actividad, frecuencia, desde/hasta cuándo:")

    b.seccion("7. Declaración de salud")
    b.parrafo("Conteste para el asegurado y todos los dependientes. Detalle cualquier \"Sí\" al "
              "final.", size=8)
    for pregunta in PREGUNTAS_INICIALES:
        b.si_no(pregunta)
    for pregunta in PREGUNTAS_SALUD:
        b.si_no(pregunta)

    b.seccion("8. Enfermedades y condiciones")
    b.parrafo("¿Padece o ha padecido el asegurado o algún dependiente alguna de estas "
              "condiciones? (No aplica para Accidentes Personales)", size=8)
    for pregunta in PREGUNTAS_ENFERMEDADES:
        b.si_no(pregunta)
    b.espacio(4)
    b.campo_texto("Detalle de respuestas \"Sí\" (quién, condición, atención/diagnóstico, médico, "
                   "condición actual):", alto_campo=45, multilinea=True)

    b.seccion("9. Médicos")
    b.campo_texto("Médico de cabecera, ginecólogo y/o pediatra: nombre, especialidad, teléfono, "
                   "para quién:")

    b.seccion("10. Firma")
    b.dos_campos("Nombre:", "Fecha:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_colectivo.pdf")
    parser.add_argument("--dependientes", type=int, default=5)
    args = parser.parse_args()
    construir(args.salida, num_dependientes=args.dependientes)


if __name__ == "__main__":
    main()
