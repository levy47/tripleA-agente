"""
PDF llenable (AcroForm) del cuestionario de cliente para Solicitud de Seguro
Medico de Blue Cross Internacional de Seguros, mismo motor que
generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_bluecross_pdf.py --salida cuestionario_bluecross.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL

PREGUNTAS_SALUD = [
    "¿Problemas cerebrovasculares, migrañas o dolores de cabeza?",
    "¿Epilepsia, convulsiones, ataque, desmayo o pérdida de conocimiento?",
    "¿Problemas de oídos/audición, vista, cataratas, u otra alteración en los ojos?",
    "¿Problemas respiratorios, tuberculosis, asma, enfisema o fiebre reumática?",
    "¿Problemas del corazón, circulatorios, dolores en el pecho, presión arterial, angina, flebitis?",
    "¿Problemas digestivos (estómago, intestinos, hígado, vesícula, páncreas, colitis, hernia, "
    "úlceras, hepatitis)?",
    "¿Problemas en riñones, vejiga, cálculos renales, infección renal/urinaria?",
    "¿Problemas en columna vertebral, dolores de espalda, esclerosis múltiple o hernia discal?",
    "¿Enfermedades de las articulaciones, lupus, artritis, gota o reumatismo?",
    "¿Cáncer, quistes, tumor, leucemia, problemas en la sangre, diabetes, anemia o hemofilia?",
    "¿Trastornos de la piel?",
    "¿Alteración de la tiroides (bocio, hipo/hipertiroidismo)?",
    "¿Enfermedad, lesión o malformación congénita o hereditaria?",
    "¿Alguna alteración inmunológica diagnosticada?",
    "¿Algún tipo de alergia?",
    "¿Trastorno mental, ansiedad, depresión, déficit atencional?",
    "¿Enfermedades infectocontagiosas (herpes, dengue, sífilis, VPH, SIDA, u otra de transmisión "
    "sexual)?",
    "¿Consume alguna droga o bebida alcohólica?",
    "¿Ha sido sancionado o tratado por drogas/alcohol?",
    "¿Ha disminuido o aumentado de peso en los últimos 12 meses?",
    "¿Toma medicamentos, vitaminas, anabólicos u hormonas de uso regular?",
    "¿Ha fumado alguna vez cigarrillo/cigarro/pipa/tabaco?",
    "¿Se ha hecho estudios (rayos X, colonoscopia, endoscopia, electrocardiograma)?",
    "¿Cirugía y/o hospitalización por enfermedad, accidente, u otra razón?",
    "¿Le han recomendado alguna cirugía/tratamiento futuro que no se ha realizado?",
    "¿Alguna otra enfermedad o condición no mencionada?",
    "¿Antecedentes familiares de cáncer, diabetes, enfermedad del corazón o hipertensión?",
]


def construir(salida, num_dependientes=4):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Solicitud de Seguro Médico",
                     subtitulo_banner="Triple A Seguros — Blue Cross Blue Shield Panamá")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. Adjunte foto de cédula/pasaporte de "
              "cada persona a asegurar.", size=9)
    b.parrafo("IMPORTANTE: NO incluya los datos de su tarjeta de crédito en este documento.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Prospecto asegurado")
    b.campo_texto("Nombre completo:")
    b.dos_campos("Cédula/pasaporte:", "Fecha de nacimiento:")
    b.opciones("Sexo:", ["F", "M"])
    b.dos_campos("Estado civil:", "¿Extranjero? ¿De qué país?")
    b.dos_campos("Peso:", "Estatura:")
    b.campo_texto("Dirección residencial completa:")
    b.dos_campos("Teléfono(s):", "Correo electrónico:")
    b.dos_campos("Ocupación / empresa donde trabaja:", "Ingreso anual aproximado (B/.):")
    b.campo_texto("País(es) donde tributa por sus ingresos:")

    b.seccion("2. Dependientes (cónyuge / hijos)")
    b.parrafo(f"Complete un bloque por dependiente (hasta {num_dependientes}). Deje en blanco si "
              "no aplica.", size=8)
    b.campo_texto("Liste cada dependiente en una línea: parentesco, nombre completo, cédula/"
                   "pasaporte, sexo, fecha de nacimiento, peso y estatura:", alto_campo=45,
                   multilinea=True)

    b.seccion("3. Contratante y responsable de pago (solo si son diferentes al Prospecto)")
    b.campo_texto("Contratante: nombre completo o razón social, cédula/RUC, dirección, relación "
                   "con el Prospecto:")
    b.campo_texto("Responsable de pago: nombre completo o razón social, cédula/RUC, dirección, "
                   "relación con el Prospecto:")

    b.seccion("4. Persona Expuesta Políticamente (PEP)")
    b.si_no("¿Es el Prospecto, Contratante o Responsable de Pago una persona políticamente "
            "expuesta?")
    b.campo_texto("Si es Sí: quién, y cargo actual o anterior:")

    b.seccion("5. Cuestionario de salud")
    b.parrafo("Conteste Sí o No para cada persona a asegurar (Prospecto, cónyuge e hijos). Si "
              "alguna respuesta es \"Sí\", detalle al final: quién, condición, fecha, médico "
              "tratante.", size=8)
    for pregunta in PREGUNTAS_SALUD:
        b.si_no(pregunta)
    b.espacio(4)
    b.campo_texto("Detalle de respuestas \"Sí\" (quién, número de pregunta, condición, fecha, "
                   "médico tratante):", alto_campo=45, multilinea=True)

    b.seccion("6. Estilo de vida y otros")
    b.si_no("¿Fuma actualmente o ha fumado en los últimos 12 meses?")
    b.si_no("¿Practica algún deporte de riesgo (motos, buceo, paracaidismo) o tiene licencia de "
            "piloto?")
    b.si_no("¿Tiene otro seguro de hospitalización vigente, o alguna solicitud pendiente?")
    b.si_no("¿Se le ha rechazado, pospuesto o recargado una solicitud de seguro previamente?")

    b.seccion("7. Plan y forma de pago")
    b.campo_texto("Plan de interés (Medired / Xtreme Care / Plan Médico Internacional) y "
                   "deducible:")
    b.opciones("Forma de pago:", ["Tarjeta de crédito", "Descuento bancario (ACH)",
                                  "Voluntario/Corredor/Caja/Banca en línea/Yappy", "Empresa"])
    b.opciones("Frecuencia de pago:", ["Mensual", "Trimestral", "Semestral", "Anual"])

    b.seccion("8. Beneficiarios (Anexo de Vida)")
    b.campo_texto("Liste cada beneficiario en una línea: nombre completo, parentesco, "
                   "porcentaje (deben sumar 100%):", alto_campo=30, multilinea=True)

    b.seccion("9. Firma")
    b.dos_campos("Nombre:", "Fecha:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_bluecross.pdf")
    parser.add_argument("--dependientes", type=int, default=4)
    args = parser.parse_args()
    construir(args.salida, num_dependientes=args.dependientes)


if __name__ == "__main__":
    main()
