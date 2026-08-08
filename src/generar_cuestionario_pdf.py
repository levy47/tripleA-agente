"""
Genera un PDF llenable (AcroForm) con el cuestionario recomendado para el cliente,
como alternativa al mensaje de texto libre / Google Form: el cliente abre el PDF,
lo llena en su celular/computadora (Adobe Acrobat Reader, Preview, etc.), lo guarda
y lo manda de vuelta por WhatsApp/email. El agente ya sabe leer PDFs adjuntos
directamente (ver extract_family.py), asi que no hace falta ningun cambio ahi --
Claude lee el contenido visible del PDF igual que leeria un formulario escaneado.

Uso:
    python3 src/generar_cuestionario_pdf.py --salida cuestionario_cliente.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor

AZUL = HexColor("#0b2545")
GRIS_TEXTO = HexColor("#1a2733")
ANCHO, ALTO = letter
MARGEN = 42
Y_TOPE = ALTO - MARGEN


class Constructor:
    def __init__(self, c, titulo_banner="Cuestionario para Solicitud de Seguro Salud",
                 subtitulo_banner="Triple A Seguros — WorldWide Medical",
                 etiqueta_si="Sí", etiqueta_no="No"):
        self.c = c
        self.form = c.acroForm
        self.y = Y_TOPE
        self._contador_campo = 0
        self._pagina = 0
        self.titulo_banner = titulo_banner
        self.subtitulo_banner = subtitulo_banner
        self.etiqueta_si = etiqueta_si
        self.etiqueta_no = etiqueta_no

    def _siguiente_nombre(self, base):
        self._contador_campo += 1
        return f"{base}_{self._contador_campo}"

    def _banner_pagina(self):
        if self._pagina > 0:
            self.c.showPage()
        self._pagina += 1
        self.c.setFillColor(AZUL)
        self.c.rect(0, ALTO - 70, ANCHO, 70, fill=1, stroke=0)
        self.c.setFillColor(HexColor("#ffffff"))
        self.c.setFont("Helvetica-Bold", 15)
        self.c.drawString(MARGEN, ALTO - 45, self.titulo_banner)
        self.c.setFont("Helvetica", 10)
        self.c.drawString(MARGEN, ALTO - 62, self.subtitulo_banner)
        self.c.setFillColor(GRIS_TEXTO)
        self.y = ALTO - 95

    def nueva_pagina(self, titulo):
        """Fuerza pagina nueva y arranca una seccion con titulo -- usar solo para la
        primera pagina del documento. El resto del flujo pasa de pagina solo() cuando
        el contenido no entra (ver salto_si_necesario), sin forzar cortes por seccion."""
        self._banner_pagina()
        self.seccion(titulo)

    def espacio(self, n=10):
        self.y -= n

    def salto_si_necesario(self, alto_necesario=30, titulo_continuacion=None):
        if self.y - alto_necesario < MARGEN + 20:
            self._banner_pagina()

    def seccion(self, texto):
        self.salto_si_necesario(28)
        self.c.setFillColor(AZUL)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(MARGEN, self.y, texto)
        self.c.setFillColor(GRIS_TEXTO)
        self.c.line(MARGEN, self.y - 4, ANCHO - MARGEN, self.y - 4)
        self.y -= 22

    def parrafo(self, texto, size=9, color=None, bold=False):
        fuente = "Helvetica-Bold" if bold else "Helvetica"
        ancho_disponible = ANCHO - 2 * MARGEN
        lineas = []
        actual = ""
        for palabra in texto.split(" "):
            candidato = f"{actual} {palabra}".strip()
            if self.c.stringWidth(candidato, fuente, size) > ancho_disponible and actual:
                lineas.append(actual)
                actual = palabra
            else:
                actual = candidato
        if actual:
            lineas.append(actual)

        self.salto_si_necesario(16 * len(lineas))
        self.c.setFont(fuente, size)
        self.c.setFillColor(color or GRIS_TEXTO)
        for i, linea in enumerate(lineas):
            self.c.drawString(MARGEN, self.y - i * (size + 4), linea)
        self.c.setFillColor(GRIS_TEXTO)
        self.y -= (size + 6) + (len(lineas) - 1) * (size + 4)

    def campo_texto(self, etiqueta, ancho=None, alto_campo=15, multilinea=False):
        self.salto_si_necesario(alto_campo + 18)
        self.c.setFont("Helvetica", 9)
        self.c.drawString(MARGEN, self.y, etiqueta)
        self.y -= 13
        ancho = ancho or (ANCHO - 2 * MARGEN)
        nombre = self._siguiente_nombre("campo")
        self.form.textfield(
            name=nombre, x=MARGEN, y=self.y - alto_campo + 12, width=ancho, height=alto_campo,
            borderStyle="underlined", borderColor=HexColor("#888888"), fillColor=HexColor("#f4f6f8"),
            textColor=GRIS_TEXTO, fontSize=9, forceBorder=True,
            fieldFlags="multiline" if multilinea else "",
        )
        self.y -= alto_campo + 6

    def dos_campos(self, etiqueta1, etiqueta2, alto_campo=15):
        self.salto_si_necesario(alto_campo + 18)
        mitad = (ANCHO - 2 * MARGEN - 20) / 2
        self.c.setFont("Helvetica", 9)
        self.c.drawString(MARGEN, self.y, etiqueta1)
        self.c.drawString(MARGEN + mitad + 20, self.y, etiqueta2)
        self.y -= 13
        n1 = self._siguiente_nombre("campo")
        n2 = self._siguiente_nombre("campo")
        self.form.textfield(name=n1, x=MARGEN, y=self.y - alto_campo + 12, width=mitad, height=alto_campo,
                             borderStyle="underlined", borderColor=HexColor("#888888"),
                             fillColor=HexColor("#f4f6f8"), textColor=GRIS_TEXTO, fontSize=9, forceBorder=True)
        self.form.textfield(name=n2, x=MARGEN + mitad + 20, y=self.y - alto_campo + 12, width=mitad,
                             height=alto_campo, borderStyle="underlined", borderColor=HexColor("#888888"),
                             fillColor=HexColor("#f4f6f8"), textColor=GRIS_TEXTO, fontSize=9, forceBorder=True)
        self.y -= alto_campo + 6

    def campos_fila(self, etiquetas, alto_campo=15):
        """N campos de texto en una sola fila, mismo ancho cada uno (ej. Numero de poliza /
        Cantidad de pagos / Prima). etiquetas es una lista de 2 a 4 strings."""
        self.salto_si_necesario(alto_campo + 18)
        n = len(etiquetas)
        espacio = 14
        ancho_util = ANCHO - 2 * MARGEN - espacio * (n - 1)
        ancho_campo = ancho_util / n
        for i, etiqueta in enumerate(etiquetas):
            x = MARGEN + i * (ancho_campo + espacio)
            size = 9
            while size > 6 and self.c.stringWidth(etiqueta, "Helvetica", size) > ancho_campo:
                size -= 1
            self.c.setFont("Helvetica", size)
            self.c.drawString(x, self.y, etiqueta)
        self.y -= 13
        for i in range(n):
            x = MARGEN + i * (ancho_campo + espacio)
            nombre = self._siguiente_nombre("campo")
            self.form.textfield(name=nombre, x=x, y=self.y - alto_campo + 12, width=ancho_campo,
                                 height=alto_campo, borderStyle="underlined", borderColor=HexColor("#888888"),
                                 fillColor=HexColor("#f4f6f8"), textColor=GRIS_TEXTO, fontSize=9,
                                 forceBorder=True)
        self.y -= alto_campo + 6

    def si_no(self, etiqueta):
        x_si = ANCHO - MARGEN - 90
        x_no = ANCHO - MARGEN - 40
        ancho_disponible = x_si - MARGEN - 10

        self.c.setFont("Helvetica", 9)
        lineas = []
        actual = ""
        for palabra in etiqueta.split(" "):
            candidato = f"{actual} {palabra}".strip()
            if self.c.stringWidth(candidato, "Helvetica", 9) > ancho_disponible and actual:
                lineas.append(actual)
                actual = palabra
            else:
                actual = candidato
        if actual:
            lineas.append(actual)

        alto_total = 14 * len(lineas) + 6
        self.salto_si_necesario(alto_total)

        for i, linea in enumerate(lineas):
            self.c.setFont("Helvetica", 9)
            self.c.drawString(MARGEN, self.y - i * 13, linea)

        grupo = self._siguiente_nombre("sino")
        self.c.setFont("Helvetica", 8)
        self.c.drawString(x_si + 14, self.y, self.etiqueta_si)
        self.c.drawString(x_no + 14, self.y, self.etiqueta_no)
        self.form.radio(name=grupo, value="si", x=x_si, y=self.y - 2, size=10,
                         buttonStyle="check", borderColor=HexColor("#888888"), fillColor=HexColor("#f4f6f8"))
        self.form.radio(name=grupo, value="no", x=x_no, y=self.y - 2, size=10,
                         buttonStyle="check", borderColor=HexColor("#888888"), fillColor=HexColor("#f4f6f8"))
        self.y -= 13 * (len(lineas) - 1) + 20

    def opciones(self, etiqueta, opciones_lista):
        self.salto_si_necesario(18 + 14 * len(opciones_lista))
        self.c.setFont("Helvetica", 9)
        self.c.drawString(MARGEN, self.y, etiqueta)
        self.y -= 15
        grupo = self._siguiente_nombre("opt")
        for op in opciones_lista:
            self.form.radio(name=grupo, value=op, x=MARGEN, y=self.y - 2, size=9,
                             buttonStyle="circle", borderColor=HexColor("#888888"), fillColor=HexColor("#f4f6f8"))
            self.c.setFont("Helvetica", 9)
            self.c.drawString(MARGEN + 14, self.y, op)
            self.y -= 14

    def persona_block(self, titulo, con_parentesco=True):
        self.parrafo(titulo, size=10, color=AZUL, bold=True)
        self.parrafo("(Adjunte junto con este PDF una foto legible de la cédula o pasaporte de esta persona)",
                      size=8)
        self.campo_texto("Nombre completo (para relacionar con la foto de cédula adjunta):")
        if con_parentesco:
            self.dos_campos("Parentesco con el titular:", "Ocupación:")
            self.campo_texto("Peso y estatura:")
        else:
            self.dos_campos("Peso:", "Estatura:")


def construir(salida, num_dependientes=5):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c)

    # --- Portada / instrucciones ---
    b.nueva_pagina("Instrucciones")
    b.parrafo("Por favor complete todos los campos de este PDF y guárdelo antes de enviarlo de vuelta.", size=9)
    b.parrafo("Adjunte junto con este PDF una foto legible de la cédula o pasaporte de cada persona mencionada.",
              size=9)
    b.parrafo("IMPORTANTE: NO incluya los datos de su tarjeta de crédito en este documento — esos se los", size=9,
              bold=True)
    b.parrafo("solicitamos por separado, por un canal seguro.", size=9, bold=True)
    b.espacio(10)

    b.seccion("1. Asegurados")
    b.campo_texto("Titular (nombre completo):")
    b.campo_texto("Dependientes (cónyuge / hijos, nombres completos):")
    b.campo_texto("Pagador (si es distinto del titular):")

    # --- Titular: identidad + residencia ---
    b.seccion("2. Datos del titular")
    b.persona_block("Titular", con_parentesco=False)
    b.campo_texto("Dirección residencial completa (país, provincia, distrito, calle, edificio, apto):",
                   alto_campo=15, multilinea=True)
    b.dos_campos("Teléfono de residencia:", "Teléfono celular:")
    b.campo_texto("Correo electrónico personal:")
    b.opciones("Estado civil:", ["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Unido(a)"])

    # --- Titular: datos laborales ---
    b.seccion("Datos laborales del titular")
    b.dos_campos("Profesión:", "Ocupación / cargo:")
    b.campo_texto("Empresa donde labora:")
    b.campo_texto("Dirección de la empresa:")
    b.dos_campos("Teléfono de la oficina/empresa:", "Correo de la empresa:")
    b.campo_texto("Actividad económica de la empresa (a qué se dedica):")
    b.si_no("¿Es una empresa propia?")
    b.opciones("Tipo de ocupación:", ["Asalariado", "Independiente", "Jubilado"])
    b.campo_texto("Si es independiente, ¿a qué actividad se dedica?")
    b.campo_texto("¿Tiene otras ocupaciones o fuentes de ingreso? ¿Cuáles?")
    b.opciones("Ingreso anual aproximado (US$):",
               ["Menos de 10 mil", "10 mil a 30 mil", "30 mil a 50 mil", "Más de 50 mil"])
    b.dos_campos("País(es) donde tributa sus ingresos:", "Número de Identificación Tributario / RUC:")

    # --- PEP ---
    b.seccion("3. Persona Expuesta Políticamente (PEP)")
    b.parrafo("Obligatorio por regulación — no se puede omitir. Para el titular y cada adulto asegurado.", size=8)
    b.espacio(6)
    b.si_no("¿Es usted, o fue en los últimos dos años, una Persona Expuesta Políticamente?")
    b.campo_texto("Si respondió Sí: cargo actual o anterior:")
    b.si_no("¿Tiene un familiar directo (cónyuge, padres, hermanos, hijos) que sea PEP?")
    b.campo_texto("Si respondió Sí: nombre, cargo y parentesco del familiar PEP:")
    b.si_no("¿Es usted un colaborador cercano de una Persona Expuesta Políticamente?")
    b.campo_texto("Si respondió Sí: nombre, cargo y relación:")

    # --- Dependientes (cantidad configurable, ver --dependientes) ---
    b.seccion(f"4. Dependientes (cónyuge / hijos)")
    if num_dependientes > 0:
        b.parrafo("Complete un bloque por cada dependiente a asegurar. Deje en blanco si no aplica. Se asume que",
                  size=8)
        b.parrafo("viven en el mismo país que el titular, salvo que indique lo contrario en Comentarios.", size=8)
        b.parrafo(f"Si tiene más de {num_dependientes} dependientes, agregue los datos de los adicionales en la "
                  "sección de Comentarios, al final de este documento.", size=8)
        b.espacio(6)
        for i in range(1, num_dependientes + 1):
            b.persona_block(f"Dependiente {i}", con_parentesco=True)
            b.espacio(4)
    else:
        b.parrafo("No aplica para este caso (sin dependientes).", size=9)

    # --- Cuestionario medico ---
    b.seccion("5. Cuestionario médico")
    b.parrafo("Conteste para el titular y cada persona a asegurar. Si alguna respuesta es \"Sí\", detalle abajo.",
              size=8)
    b.espacio(6)
    b.si_no("¿Tiene alguna condición médica diagnosticada, o se la han diagnosticado en algún momento?")
    b.si_no("¿Cirugía previa?")
    b.si_no("¿Toma algún medicamento recurrente?")
    b.si_no("¿Alguno de sus padres o hermanos tuvo tuberculosis, diabetes, cáncer, presión alta, "
            "enfermedad del corazón o riñón?")
    b.espacio(4)
    b.campo_texto("Si contestó \"Sí\" a alguna: detalle (condición, cuándo, médico tratante, medicamentos):",
                   alto_campo=40, multilinea=True)
    b.campo_texto("Nombre de su médico de cabecera (y especialidad):")

    # --- Beneficiarios y otros ---
    b.seccion("6. Beneficiarios")
    b.parrafo("A quién(es) se le entrega el beneficio de vida si el titular fallece.", size=8)
    b.espacio(6)
    for i in range(1, 3):
        b.parrafo(f"Beneficiario {i}", size=10, color=AZUL, bold=True)
        b.parrafo("(Adjunte junto con este PDF una foto legible de su cédula o pasaporte)", size=8)
        b.campo_texto("Nombre completo (para relacionar con la foto adjunta):")
        b.dos_campos("Parentesco con el titular:", "Ocupación:")
        b.campo_texto("Porcentaje asignado (deben sumar 100%):")
        b.espacio(4)

    b.seccion("7. Otros")
    b.si_no("¿Tiene o tuvo otro seguro de gastos médicos?")
    b.campo_texto("Si Sí: ¿con qué compañía, número de póliza, sigue vigente?")
    b.opciones("Forma de pago preferida:", ["Anual", "Semestral", "Trimestral", "Mensual"])
    b.opciones("Plan de interés (si ya lo conversó con su corredor):",
               ["Optimum Plus", "Optimum", "Security", "Essence", "Exclusive Int.", "Exclusive Plus", "Aún no sé"])
    b.espacio(6)
    b.campo_texto("Comentarios adicionales (ej. dependientes adicionales, aclaraciones):",
                   alto_campo=50, multilinea=True)

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_cliente.pdf")
    parser.add_argument("--dependientes", type=int, default=5,
                         help="cantidad de bloques de dependiente a incluir (0 para ningun dependiente)")
    args = parser.parse_args()
    construir(args.salida, num_dependientes=args.dependientes)


if __name__ == "__main__":
    main()
