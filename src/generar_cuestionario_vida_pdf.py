"""
PDF llenable (AcroForm) del cuestionario de cliente para Solicitud de Seguro de Vida
de WorldWide Medical, mismo motor que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_vida_pdf.py --salida cuestionario_vida_worldwide.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor

from generar_cuestionario_pdf import Constructor, AZUL

PREGUNTAS_MEDICAS = [
    "¿Dolor en el pecho, palpitaciones, hipertensión, fiebre reumática, soplo cardíaco, ataque "
    "cardíaco u otra enfermedad del corazón?",
    "¿Ahogos, ronquera, tos persistente, esputos de sangre, bronquitis, pleuresía, asma, "
    "enfisema, tuberculosis u otro trastorno respiratorio?",
    "¿Mareos, desmayos, epilepsia, convulsiones, dolor de cabeza, afección del habla, parálisis "
    "u otro trastorno neurológico?",
    "¿Ictericia, hemorragia intestinal, úlcera, hernia, apendicitis, colitis, diverticulitis, "
    "hemorroides u otro trastorno digestivo?",
    "¿Diabetes, tiroides u otro trastorno endocrino?",
    "¿Neuritis, ciática, reumatismo, artritis, gota o desorden de músculos/huesos, incluyendo la "
    "columna vertebral?",
    "¿Enfermedad de la piel, ganglios linfáticos, quiste, tumor, cáncer, sudores nocturnos, "
    "fatiga u otro síntoma similar?",
    "¿Albúmina, azúcar, sangre o pus en la orina, enfermedades venéreas, cálculos renales u otro "
    "trastorno renal/reproductivo?",
    "¿Algún problema de los ojos, oídos, nariz o garganta?",
    "¿Alergias, anemia u otro desorden sanguíneo?",
    "¿Alguna deformidad, enfermedad o defecto congénito?",
    "En los últimos 10 años, ¿examen médico, consulta, enfermedad, lesión o procedimiento médico "
    "ambulatorio reciente?",
    "¿Ha sido paciente en un hospital, clínica, sanatorio u otra institución médica?",
    "¿Se ha hecho un electrocardiograma, radiografía u otra prueba especializada?",
    "¿Le aconsejaron alguna prueba diagnóstica, hospitalización o cirugía que no se ha llevado a "
    "cabo?",
    "¿Ha tomado en los últimos 12 meses algún medicamento prescrito, o recibido tratamiento "
    "médico?",
    "¿Tiene previsto obtener tratamiento u opinión médica en los próximos 6 meses?",
    "¿Ha tenido resultados positivos de VIH, o ha sido diagnosticado con SIDA o alguna condición "
    "derivada?",
    "¿Existe historial familiar de muertes por enfermedad coronaria, embolia, cáncer o "
    "enfermedad renal antes de los 60 años (o diabetes antes de los 50)?",
]

PREGUNTAS_MEDICAS_MUJER = [
    "¿Trastorno en la menstruación, el embarazo, los órganos reproductivos o los senos?",
    "¿Está embarazada? Indicar semanas.",
]

PREGUNTAS_ADICIONALES = [
    "¿Ha fumado cigarrillos/cigarros/pipas o usado tabaco/nicotina en los últimos 24 meses?",
    "¿Consume bebidas alcohólicas? Indicar cantidad y frecuencia.",
    "¿Ha sido arrestado por uso/posesión/venta/distribución de drogas, o algún acto delictivo "
    "relacionado?",
    "¿Se le ha suspendido/revocado la licencia de conducir, o tiene convicciones/accidentes de "
    "tránsito?",
    "¿Ha participado en actividades de riesgo (motocicleta, deportes submarinos/buceo, "
    "paracaidismo, u otras similares)?",
    "¿Tiene intención de reemplazar, descontinuar o cambiar alguna cobertura de vida/accidentes "
    "existente?",
]


def construir(salida, num_beneficiarios_primarios=3, num_beneficiarios_contingentes=2,
              num_coberturas_previas=2):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Solicitud de Seguro de Vida",
                     subtitulo_banner="Triple A Seguros — WorldWide Medical")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Por favor complete todos los campos de este PDF y guárdelo antes de enviarlo de vuelta.",
              size=9)
    b.parrafo("Adjunte junto con este PDF una foto legible de la cédula o pasaporte de cada "
              "persona mencionada.", size=9)
    b.parrafo("IMPORTANTE: NO incluya los datos de su tarjeta de crédito en este documento — "
              "esos se los solicitamos por separado, por un canal seguro.", size=9, bold=True)
    b.espacio(10)

    b.seccion("1. Asegurado propuesto")
    b.campo_texto("Nombre completo (para relacionar con la foto de cédula adjunta):")
    b.parrafo("(Adjunte junto con este PDF una foto legible de su cédula o pasaporte)", size=8)
    b.opciones("Sexo:", ["F", "M"])
    b.campo_texto("Fecha de nacimiento:")
    b.dos_campos("País de nacimiento:", "Nacionalidad(es):")
    b.campo_texto("País de residencia:")
    b.campo_texto("Dirección residencial completa (país, provincia, distrito, corregimiento, "
                   "urbanización, calle, edificio/casa):", alto_campo=15, multilinea=True)
    b.dos_campos("Teléfono de residencia / celular:", "Correo electrónico:")
    b.dos_campos("Profesión:", "Ocupación (si es independiente, indique a qué actividad se dedica):")
    b.campo_texto("Empresa donde labora, dirección y actividad económica de la empresa:")
    b.campo_texto("Años de empleo en la compañía actual:")
    b.campo_texto("Deberes/funciones de su empleo:")
    b.dos_campos("Ingreso anual (monto y moneda):", "Ingresos por otras actividades (si aplica):")
    b.dos_campos("Médico de cabecera (nombre):", "Nombre del corredor:")

    b.seccion("2. Contratante (solo si es una persona distinta del Asegurado)")
    b.campo_texto("Nombre completo, cédula o pasaporte, fecha de nacimiento, sexo:")
    b.campo_texto("Nacionalidad(es), país de nacimiento, país de residencia:")
    b.campo_texto("Parentesco con el Asegurado:")
    b.campo_texto("Dirección residencial y laboral, teléfonos, correo:")
    b.campo_texto("Ocupación/cargo, empresa donde labora, actividad económica de la empresa:")
    b.dos_campos("País(es) donde tributa por sus ingresos:", "Propósito de este seguro:")

    b.seccion("3. Persona Expuesta Políticamente (PEP)")
    b.parrafo("Obligatorio por regulación, para el Asegurado, Contratante y Pagador si son "
              "personas distintas.", size=8)
    b.espacio(6)
    b.si_no("¿Es usted, tiene un familiar directo, o es colaborador cercano de una Persona "
            "Expuesta Políticamente?")
    b.campo_texto("Si respondió Sí: cargo (y tiempo en el cargo), o nombre/cargo/relación con el PEP:")

    b.seccion("4. Beneficiarios primarios")
    b.parrafo(f"Complete un bloque por cada beneficiario primario (hasta "
              f"{num_beneficiarios_primarios}). El porcentaje debe sumar 100% entre todos.", size=8)
    b.espacio(6)
    for i in range(1, num_beneficiarios_primarios + 1):
        b.parrafo(f"Beneficiario primario {i}", size=10, color=AZUL, bold=True)
        b.parrafo("(Adjunte junto con este PDF una foto legible de su cédula o pasaporte)", size=8)
        b.campo_texto("Nombre completo (para relacionar con la foto adjunta):")
        b.dos_campos("Parentesco con el Asegurado:", "Ocupación:")
        b.campo_texto("Porcentaje asignado (deben sumar 100%):")
        b.espacio(4)

    b.seccion("5. Beneficiarios contingentes (si aplica)")
    b.parrafo("Reciben el beneficio solo si un beneficiario primario no puede recibirlo.", size=8)
    b.espacio(6)
    for i in range(1, num_beneficiarios_contingentes + 1):
        b.parrafo(f"Beneficiario contingente {i}", size=10, color=AZUL, bold=True)
        b.campo_texto("Nombre completo:")
        b.dos_campos("Parentesco con el Asegurado:", "Ocupación:")
        b.campo_texto("Porcentaje asignado:")
        b.espacio(4)

    b.campo_texto("Si algún beneficiario es menor de edad: nombre y cédula/pasaporte de quien "
                   "recibirá el beneficio en su representación, y parentesco con el Asegurado:",
                   alto_campo=30, multilinea=True)

    b.seccion("6. Cesión bancaria (solo si aplica)")
    b.dos_campos("Producto bancario / contacto del banco:", "Suma cedida:")

    b.seccion("7. Coberturas previas o solicitudes pendientes con otras compañías")
    b.parrafo("Si tiene o tuvo otro seguro de vida/accidentes.", size=8)
    b.espacio(6)
    for i in range(1, num_coberturas_previas + 1):
        b.parrafo(f"Cobertura previa {i}", size=10, color=AZUL, bold=True)
        b.dos_campos("Nombre y dirección de la compañía:", "Número de póliza:")
        b.dos_campos("Monto del seguro:", "Fecha de solicitud:")
        b.espacio(4)

    b.seccion("8. Cuestionario médico")
    b.parrafo("Conteste para el Asegurado propuesto. Si alguna respuesta es \"Sí\", detalle "
              "abajo: condición, cuándo, médico tratante, tratamiento/medicamentos, resultados, "
              "nombre y dirección del hospital.", size=8)
    b.espacio(6)
    for pregunta in PREGUNTAS_MEDICAS:
        b.si_no(pregunta)
    b.parrafo("Solo para mujeres:", size=9, bold=True)
    for pregunta in PREGUNTAS_MEDICAS_MUJER:
        b.si_no(pregunta)
    b.parrafo("Adicionales:", size=9, bold=True)
    for pregunta in PREGUNTAS_ADICIONALES:
        b.si_no(pregunta)
    b.espacio(4)
    b.campo_texto("Detalle de respuestas \"Sí\" (indique el número de pregunta, condición, "
                   "cuándo, médico tratante, tratamiento/medicamentos, resultados, hospital):",
                   alto_campo=50, multilinea=True)

    b.seccion("9. Perfil financiero y otros")
    b.campo_texto("Ingresos anuales por actividades distintas a la principal (si aplica):")
    b.opciones("Forma de pago de la prima:", ["Anual", "Semestral", "Trimestral", "Mensual"])

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_vida_worldwide.pdf")
    parser.add_argument("--beneficiarios-primarios", type=int, default=3)
    parser.add_argument("--beneficiarios-contingentes", type=int, default=2)
    parser.add_argument("--coberturas-previas", type=int, default=2)
    args = parser.parse_args()
    construir(args.salida, num_beneficiarios_primarios=args.beneficiarios_primarios,
              num_beneficiarios_contingentes=args.beneficiarios_contingentes,
              num_coberturas_previas=args.coberturas_previas)


if __name__ == "__main__":
    main()
