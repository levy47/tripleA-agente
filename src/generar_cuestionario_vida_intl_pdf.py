"""
PDF llenable (AcroForm) del cuestionario de cliente para Solicitud de Seguro de
Vida de Internacional de Seguros, mismo motor que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_vida_intl_pdf.py --salida cuestionario_vida_intl.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL

PREGUNTAS_OTRAS_COMPANIAS = [
    "¿Le han ofrecido seguro de vida o accidentes diferente en condiciones, suma o prima, al "
    "solicitado por usted?",
    "¿Se le ha rechazado, diferido, modificado o recargado alguna vez un seguro de vida, "
    "accidentes/enfermedades, o la rehabilitación de alguna póliza?",
    "¿Está pendiente alguna solicitud o rehabilitación de seguro de vida, accidentes o "
    "enfermedades en otra compañía?",
    "¿Ha recibido beneficios o reclamado indemnización/renta por algún accidente o enfermedad "
    "en otra compañía?",
    "¿Ha participado, está participando, o sospecha que puede estar participando (individualmente "
    "o con otros) en actividades ilícitas o de lavado de dinero?",
    "¿Es usted una persona políticamente expuesta?",
    "¿El total de primas anuales que paga entre todas las compañías de seguros es igual o supera "
    "los B/.10,000.00?",
    "¿Ha estado más de 183 días en Estados Unidos u otro país, en los últimos tres años?",
    "¿Ha solicitado órdenes de pago desde o hacia Estados Unidos u otro país?",
    "¿Es usted o el Contratante contribuyente fiscal de Estados Unidos o de algún otro país?",
    "¿Tiene licencia de piloto, ha piloteado, piensa pilotear una aeronave, o viaja en aviones "
    "que no sean de líneas comerciales autorizadas?",
    "¿Practica algún deporte?",
    "¿Participa o planea participar en carreras de autos/motos, paracaidismo, buceo, u otra "
    "actividad o deporte arriesgado?",
]

PREGUNTAS_MEDICAS = [
    "¿Padece alguna enfermedad crónica? ¿Cuál?",
    "¿Trastorno de los ojos, oídos, nariz o garganta?",
    "¿Palpitaciones, soplo cardíaco, infarto, valvulopatías u otra enfermedad del corazón/"
    "circulatoria?",
    "¿Tensión arterial alta?",
    "¿Bronquitis, tos persistente, asma, enfisema, pleuresía, tuberculosis u otro trastorno "
    "respiratorio?",
    "¿Úlcera de estómago/duodeno, colitis, diverticulitis, hernia, hemorroides u otra molestia "
    "digestiva?",
    "¿Enfermedades del hígado, vesícula biliar o páncreas?",
    "¿Infecciones urinarias, hematuria, litiasis renal, o enfermedades de vejiga/próstata/riñón?",
    "¿Hemorragia de cualquier índole o hemofilia?",
    "¿Diabetes, bocio, u otro trastorno de glándulas endocrinas?",
    "¿Cáncer, quiste o algún otro tumor?",
    "¿Pérdida del conocimiento, ataque, convulsiones o epilepsia?",
    "¿Reumatismo, gota, artritis, u otro trastorno de músculos/huesos/columna?",
    "¿Deformidad, cojera o amputación?",
    "¿Alergias, anemias u otros trastornos de la sangre?",
    "¿Ha consultado algún psiquiatra?",
    "¿Chancro o reacciones de sangre positiva a sífilis o herpes genital?",
    "¿Intervenciones quirúrgicas?",
    "¿Alguna otra enfermedad o lesión no mencionada?",
    "¿Ha recibido transfusiones?",
    "¿Se ha estudiado o diagnosticado por alguna alteración inmunológica?",
    "En los últimos 10 años: ¿SIDA, CRS, o condición relacionada; consejo/tratamiento por lo "
    "mismo; o resultado positivo de VIH?",
    "¿Consume o ha consumido algún tipo de droga ilícita?",
    "¿Ha recibido tratamiento por uso de licor o drogas?",
    "¿Toma actualmente medicamentos o vitaminas?",
    "¿Ingiere licor? Indicar cantidad y frecuencia.",
    "¿Ha estado internado en hospital/clínica/sanatorio para examen, diagnóstico o tratamiento?",
    "¿Se encuentra bajo observación/tratamiento médico o anticonceptivos?",
    "¿Se le han hecho estudios con rayos X, para diagnóstico de cáncer, o electrocardiogramas?",
    "¿Le han aconsejado algún examen/hospitalización/cirugía que no se ha realizado?",
]

PREGUNTAS_MUJER = [
    "¿Está embarazada? ¿Cuántos meses?",
    "¿Ha tenido abortos, partos prematuros, o dificultad en sus partos?",
    "¿Ha tenido algún tumor o enfermedad en los pechos, ovarios, o la matriz?",
    "¿Ha tenido hemorragias vaginales?",
    "¿Son regulares sus períodos menstruales? Fecha de la última menstruación:",
]


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Solicitud de Seguro de Vida",
                     subtitulo_banner="Triple A Seguros — Internacional de Seguros")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Complete y guarde este PDF antes de enviarlo. Adjunte foto de cédula/pasaporte "
              "del Asegurado, Contratante (si aplica) y beneficiarios.", size=9)
    b.parrafo("IMPORTANTE: NO incluya los datos de su tarjeta de crédito en este documento.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Asegurado propuesto")
    b.campo_texto("Nombre completo:")
    b.dos_campos("Cédula/pasaporte:", "Fecha de nacimiento:")
    b.opciones("Sexo:", ["F", "M"])
    b.dos_campos("Estado civil:", "Ocupación / empresa donde trabaja:")
    b.campo_texto("Dirección residencial completa:")
    b.dos_campos("Teléfono(s):", "Correo electrónico:")
    b.dos_campos("Ingreso anual aproximado (B/.):", "¿Es extranjero? ¿De qué país?")

    b.seccion("2. Contratante (solo si es diferente al Asegurado)")
    b.campo_texto("Nombre completo, cédula/RUC, dirección, relación con el Asegurado:")

    b.seccion("3. FATCA / CRS")
    b.si_no("¿Posee algún accionista, director o dignatario de la sociedad contratante alguna "
            "nacionalidad, ciudadanía, residencia o green card distinta a la panameña?")
    b.campo_texto("Si es Sí: especifique. (Debe completar formulario FATCA o CRS aparte)")

    b.seccion("4. Preguntas sobre otras compañías de seguros")
    for pregunta in PREGUNTAS_OTRAS_COMPANIAS:
        b.si_no(pregunta)
    b.campo_texto("Si tiene otro seguro de vida/accidente vigente: compañía, no. de póliza, "
                   "suma asegurada, fecha de emisión:", alto_campo=30, multilinea=True)

    b.seccion("5. Beneficiarios")
    b.parrafo("Liste cada beneficiario principal en una línea: nombre completo, cédula/RUC, "
              "parentesco, edad, % de participación (deben sumar 100%).", size=8)
    b.campo_texto("Beneficiarios principales:", alto_campo=35, multilinea=True)
    b.campo_texto("Beneficiarios contingentes (si aplica, mismos datos):", alto_campo=25,
                   multilinea=True)
    b.campo_texto("Si algún beneficiario es menor de edad: nombre y cédula de quien administrará "
                   "el beneficio en su representación:")

    b.seccion("6. Datos del seguro")
    b.opciones("Plan:", ["Vida Universal", "Vida Tradicional"])
    b.dos_campos("Plazo de cobertura:", "Plazo de pago:")
    b.campo_texto("Coberturas deseadas (marque las que apliquen y su suma asegurada): Seguro "
                   "Básico, Beneficio por Invalidez Total y Permanente, Beneficio por Muerte "
                   "Accidental, Enfermedades Catastróficas, Accidentes Personales, u otras:",
                   alto_campo=30, multilinea=True)
    b.opciones("Frecuencia de pago:", ["Mensual", "Trimestral", "Semestral", "Anual"])

    b.seccion("7. Cuestionario médico — declaración de fumador")
    b.si_no("¿Fuma actualmente, o ha fumado en los últimos 12 meses?")
    b.campo_texto("Si es Sí: cuántos cigarrillos al día, y desde cuándo:")
    b.dos_campos("Estatura:", "Peso:")

    b.seccion("8. Antecedentes patológicos y enfermedades actuales")
    b.parrafo("Conteste Sí o No para el Asegurado propuesto. Detalle cualquier \"Sí\" al final: "
              "condición, fechas, médico, resultados.", size=8)
    for pregunta in PREGUNTAS_MEDICAS:
        b.si_no(pregunta)
    b.parrafo("Solo para mujeres:", size=9, bold=True)
    for pregunta in PREGUNTAS_MUJER:
        b.si_no(pregunta)
    b.espacio(4)
    b.campo_texto("Historial médico familiar (esposo/a, madre, padre, hermanos): edad/si vive, "
                   "estado de salud, edad y causa de muerte si aplica:", alto_campo=30,
                   multilinea=True)
    b.campo_texto("Detalle de respuestas \"Sí\" (número de pregunta, condición, fecha, médico, "
                   "resultado):", alto_campo=50, multilinea=True)

    b.seccion("9. Firma")
    b.dos_campos("Nombre:", "Fecha:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_vida_intl.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
