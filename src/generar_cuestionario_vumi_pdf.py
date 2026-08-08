"""
PDF llenable (AcroForm) del cuestionario de cliente para Solicitud de Gastos
Médicos Mayores de VUMI, mismo motor que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_vumi_pdf.py --salida cuestionario_vumi.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL

PREGUNTAS_GENERALES = [
    "¿Se encuentra(n) actualmente en buen estado de salud?",
    "¿Ha(n) variado de peso en los últimos años?",
    "¿Se ha(n) practicado algún chequeo o consulta médica por enfermedad o cirugía en los "
    "últimos 5 años?",
    "¿Ha(n) tenido accidente(s), herida(s) o fractura(s)?",
    "¿Ha(n) recibido transfusión(es) de sangre en los últimos 5 años?",
    "¿Alguna de las personas a asegurar practica algún deporte, hobby o pasatiempo?",
    "¿Consume(n) bebidas alcohólicas?",
    "¿Mantiene(n) el hábito de fumar?",
    "¿Alguna de las mujeres a incluir está embarazada?",
]

PREGUNTAS_ENFERMEDADES = [
    "Enfermedades de la piel, ojos, nariz, oídos y/o garganta",
    "Enfermedades respiratorias (asma, bronquitis, tuberculosis)",
    "Enfermedades cardiovasculares (presión arterial, infarto, arritmia)",
    "Enfermedades del sistema digestivo (gastritis, úlceras, cálculos)",
    "Enfermedades venéreas, contagiosas o infecciosas (hepatitis, sífilis, VPH)",
    "SIDA, VIH+, complejo relacionado con el SIDA",
    "Enfermedades renales o urinarias",
    "Enfermedades del sistema endocrino (diabetes, obesidad, tiroides)",
    "Enfermedades osteomusculares (artritis, hernias, columna)",
    "Enfermedades del sistema nervioso (epilepsia, Parkinson, Alzheimer)",
    "Enfermedades de la sangre (anemia, leucemia, cáncer)",
    "Enfermedades de la mujer (fibromas, alteraciones menstruales)",
    "Defectos físicos, congénitos o adquiridos",
    "Otras enfermedades no mencionadas",
]


def construir(salida, num_dependientes=4):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Solicitud de Seguro de Salud",
                     subtitulo_banner="Triple A Seguros — VUMI")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. Adjunte foto de cédula/pasaporte de "
              "cada persona a asegurar.", size=9)
    b.parrafo("IMPORTANTE: NO incluya los datos de su tarjeta de crédito en este documento.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Contratante / Propuesto asegurado")
    b.campo_texto("Nombre completo o razón social:")
    b.dos_campos("Cédula/RUC/pasaporte:", "Fecha de nacimiento:")
    b.dos_campos("Lugar de nacimiento:", "País de residencia:")
    b.opciones("Sexo:", ["F", "M"])
    b.dos_campos("Estado civil:", "Tipo de actividad (comercial/estudiante/"
                 "gub./independiente):")
    b.dos_campos("Nombre del empleador:", "Ocupación y descripción de funciones:")
    b.campo_texto("Dirección de trabajo completa:")
    b.campo_texto("Dirección de residencia completa:")
    b.dos_campos("Teléfono / celular:", "Correo electrónico:")

    b.seccion("2. Asegurado (solo si es diferente al Contratante)")
    b.campo_texto("Nombre completo, cédula/pasaporte, fecha de nacimiento, sexo, estado civil, "
                   "dirección residencial:")

    b.seccion("3. Forma de pago")
    b.opciones("Forma de pago:", ["Tarjeta de crédito", "Transferencia ACH",
                                  "Transferencia banca en línea", "Descuento en planilla"])
    b.opciones("Frecuencia:", ["Mensual", "Trimestral", "Semestral", "Anual"])

    b.seccion("4. Grupo familiar (dependientes)")
    b.parrafo(f"Complete un bloque por dependiente (hasta {num_dependientes}).", size=8)
    b.campo_texto("Liste cada dependiente en una línea: parentesco, apellidos y nombres, "
                   "cédula/pasaporte, fecha de nacimiento, sexo, estado civil, estatura y peso:",
                   alto_campo=45, multilinea=True)
    b.si_no("¿Algún hijo entre 19 y 24 años es estudiante a tiempo completo?")
    b.campo_texto("Si es Sí: nombre de la universidad:")

    b.seccion("5. Plan de interés")
    b.campo_texto("Fecha de efectividad solicitada:")
    b.opciones("Plan:", ["Absolute VIP", "Universal VIP", "Special VIP", "Access VIP",
                         "Optimum VIP", "Senior VIP", "Prime VIP"])
    b.campo_texto("Opción (I a VII) y coberturas adicionales (maternidad, trasplante de "
                   "órganos):")

    b.seccion("6. Declaración de salud — preguntas generales")
    b.parrafo("Conteste para el titular y cada dependiente. Detalle cualquier \"Sí\" al final.",
              size=8)
    for pregunta in PREGUNTAS_GENERALES:
        b.si_no(pregunta)

    b.seccion("7. Enfermedades y condiciones")
    b.parrafo("¿Padece o ha padecido el titular o algún dependiente alguna de estas "
              "condiciones?", size=8)
    for pregunta in PREGUNTAS_ENFERMEDADES:
        b.si_no(pregunta)
    b.espacio(4)
    b.campo_texto("Detalle de respuestas \"Sí\" (nombre, diagnóstico, fecha de inicio, "
                   "duración del tratamiento, médico, clínica, estado actual):", alto_campo=45,
                   multilinea=True)

    b.seccion("8. Otros seguros")
    b.si_no("¿Mantiene otras pólizas vigentes con esta u otra compañía?")
    b.si_no("¿Ha sido alguna solicitud de seguro rechazada o aceptada con restricciones o "
            "recargo?")
    b.si_no("¿Ha hecho alguna reclamación contra alguna compañía de seguros?")
    b.campo_texto("Si contestó Sí a alguna: compañía, póliza, plan, deducible, fechas, causas, "
                   "monto:")

    b.seccion("9. Historial familiar")
    b.campo_texto("Esposo/a, padre, madre, hermanos: edad (si vive), estado de salud, edad y "
                   "causa de muerte (si aplica):", alto_campo=30, multilinea=True)

    b.seccion("10. Firma")
    b.dos_campos("Nombre:", "Fecha:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_vumi.pdf")
    parser.add_argument("--dependientes", type=int, default=4)
    args = parser.parse_args()
    construir(args.salida, num_dependientes=args.dependientes)


if __name__ == "__main__":
    main()
