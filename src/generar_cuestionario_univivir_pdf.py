"""
PDF llenable (AcroForm) del cuestionario de cliente para Solicitud de Salud de
UniVivir, mismo motor que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_univivir_pdf.py --salida cuestionario_univivir.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL

PREGUNTAS_DECLARACION = [
    "¿Goza usted y todos sus dependientes de buena salud física y mental?",
    "¿Tiene usted o alguno de sus dependientes algún defecto congénito o adquirido?",
    "¿Ha sufrido usted o alguno de sus dependientes algún accidente grave o intoxicación?",
    "¿Es usted o alguno de sus dependientes piloto o tripulante en aviones privados o "
    "comerciales?",
    "¿Se ha realizado usted o algún dependiente un examen, tratamiento o cirugía reciente?",
    "¿Toma usted o algún dependiente medicamentos permanentes?",
    "¿Ha recibido usted o algún dependiente transfusiones de sangre?",
]

PREGUNTAS_ENFERMEDADES = [
    "Enfermedades del sistema nervioso (epilepsia, convulsiones, migraña, Parkinson, etc.)",
    "Trastornos mentales (psicosis, ansiedad, depresión, trastornos alimenticios)",
    "Enfermedades del corazón o del aparato circulatorio (hipertensión, infarto, arritmias)",
    "Enfermedades de la sangre (anemia, hemofilia, leucemia, colesterol/triglicéridos altos)",
    "Trastornos autoinmunes (lupus, esclerosis múltiple, tiroiditis)",
    "Trastornos gastrointestinales (úlceras, gastritis, colitis, Crohn)",
    "Enfermedades del sistema endocrino (diabetes, obesidad, hipertiroidismo)",
    "Enfermedades del sistema osteomuscular (artritis, hernias discales, osteoporosis)",
    "Enfermedades del sistema respiratorio (asma, bronquitis, EPOC)",
    "Enfermedades del sistema genito-urinario (próstata, riñones, ovarios)",
    "Enfermedades de transmisión sexual (VIH/SIDA, VPH, hepatitis B/C)",
    "Enfermedades de los ojos, nariz o boca (cataratas, glaucoma, sinusitis crónica)",
    "Enfermedades o lesiones de la piel (lunares atípicos, cáncer de piel)",
    "Secuelas de enfermedades infecciosas",
    "Otras enfermedades no citadas (cáncer, tumores, pérdida de audición/vista, etc.)",
]


def construir(salida, num_dependientes=5):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Solicitud de Seguro de Salud",
                     subtitulo_banner="Triple A Seguros — UniVivir")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. Adjunte foto de cédula/pasaporte de "
              "cada persona a asegurar.", size=9)
    b.parrafo("IMPORTANTE: NO incluya los datos de su tarjeta de crédito en este documento.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Datos del solicitante")
    b.campo_texto("Nombre completo:")
    b.dos_campos("Cédula/pasaporte:", "Fecha de nacimiento:")
    b.opciones("Sexo:", ["F", "M"])
    b.dos_campos("Estado civil:", "Nacionalidad:")
    b.dos_campos("Estatura:", "Peso:")
    b.campo_texto("Dirección residencial completa:")
    b.dos_campos("Teléfono / celular:", "Correo electrónico:")
    b.dos_campos("Ocupación / empresa donde trabaja:", "Dirección y teléfono de la empresa:")

    b.seccion("2. Contratante (solo si es diferente al solicitante)")
    b.campo_texto("Persona Natural o Jurídica, nombre/razón social, cédula/pasaporte/RUC, "
                   "dirección, relación con el asegurado:")

    b.seccion("3. Persona Expuesta Políticamente (PEP)")
    b.si_no("¿Es el solicitante o el contratante una persona políticamente expuesta?")
    b.campo_texto("Si es Sí: quién, y cargo actual o anterior:")

    b.seccion("4. Forma de pago")
    b.opciones("Forma de pago:", ["Tarjeta de crédito", "ACH", "Pago voluntario"])
    b.opciones("Frecuencia:", ["Mensual", "Trimestral", "Cuatrimestral", "Semestral", "Anual"])
    b.campo_texto("Datos bancarios (nombre de cuenta, no. de cuenta, tipo, banco), si aplica "
                   "para reembolsos:")

    b.seccion("5. Dependientes (cónyuge / hijos)")
    b.parrafo(f"Complete un bloque por dependiente (hasta {num_dependientes}).", size=8)
    b.campo_texto("Liste cada dependiente en una línea: parentesco, nombre completo, cédula/"
                   "pasaporte, nacionalidad, profesión/ocupación, fecha de nacimiento, sexo, "
                   "estatura y peso:", alto_campo=45, multilinea=True)

    b.seccion("6. Información adicional")
    b.si_no("¿Tiene o ha tenido usted o algún dependiente un seguro similar al solicitado?")
    b.campo_texto("Si es Sí: quién, compañía, suma asegurada, vencimiento:")
    b.si_no("¿Fuma, consume alcohol o estupefacientes usted o algún dependiente?")
    b.campo_texto("Si es Sí: quién, qué consume, frecuencia, desde cuándo:")
    b.si_no("¿Practica usted o algún dependiente un deporte o actividad de alto riesgo?")
    b.campo_texto("Si es Sí: quién, qué actividad, frecuencia, desde cuándo:")

    b.seccion("7. Declaración de salud")
    b.parrafo("Conteste para el solicitante y todos los dependientes. Detalle cualquier \"Sí\" "
              "al final.", size=8)
    for pregunta in PREGUNTAS_DECLARACION:
        b.si_no(pregunta)

    b.seccion("8. Enfermedades y condiciones")
    b.parrafo("¿Padece o ha padecido el solicitante o algún dependiente alguna de estas "
              "condiciones?", size=8)
    for pregunta in PREGUNTAS_ENFERMEDADES:
        b.si_no(pregunta)
    b.espacio(4)
    b.campo_texto("Detalle de respuestas \"Sí\" (quién, condición, diagnóstico, médico/hospital, "
                   "condición actual):", alto_campo=45, multilinea=True)

    b.seccion("9. Historial familiar y médicos")
    b.campo_texto("Antecedentes familiares (cáncer, diabetes, corazón, hipertensión): quién, "
                   "familiar afectado, enfermedad, edad de manifestación:", alto_campo=25,
                   multilinea=True)
    b.campo_texto("Médico de cabecera, ginecólogo y/o pediatra: nombre, especialidad, teléfono:")

    b.seccion("10. Firma")
    b.dos_campos("Nombre:", "Fecha:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_univivir.pdf")
    parser.add_argument("--dependientes", type=int, default=5)
    args = parser.parse_args()
    construir(args.salida, num_dependientes=args.dependientes)


if __name__ == "__main__":
    main()
