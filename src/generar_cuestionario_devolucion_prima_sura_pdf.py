"""
PDF llenable (AcroForm) del cuestionario de cliente para el Formulario de Pagos
(ACH Local y Transferencias Internacionales) / Devolucion de Prima de Sura
(Seguros Suramericana), mismo motor que generar_cuestionario_pdf.py.

Uso:
    python3 src/generar_cuestionario_devolucion_prima_sura_pdf.py --salida cuestionario_devolucion_prima_sura.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Cuestionario para Devolución de Prima / "
                     "Formulario de Pagos ACH — Sura",
                     subtitulo_banner="Triple A Seguros — Sura")

    b.nueva_pagina("Instrucciones")
    b.parrafo("Este formulario es para que USTED RECIBA un reembolso/devolución de prima de "
              "Seguros Suramericana, S.A. — no es para pagar con tarjeta de crédito.", size=9,
              bold=True)
    b.parrafo("Complete solo UNA de las dos secciones siguientes, según cómo vaya a recibir el "
              "pago: \"Pago local (ACH Panamá)\" si tiene cuenta bancaria en Panamá, o "
              "\"Transferencia internacional\" si la cuenta está en el extranjero.", size=9)
    b.parrafo("Guarde este PDF antes de enviarlo de vuelta.", size=9)
    b.espacio(6)

    b.seccion("1. Pago local (ACH Panamá)")
    b.parrafo("Complete esta sección si va a recibir el reembolso en una cuenta bancaria en "
              "Panamá.", size=8)
    b.espacio(4)
    b.opciones("Tipo de cuenta:", ["Corriente", "Ahorro"])
    b.campo_texto("Número de cuenta:")
    b.campo_texto("Entidad bancaria:")
    b.campo_texto("Titular de la cuenta:")
    b.dos_campos("Cédula o RUC:", "Correo electrónico:")
    b.campo_texto("Teléfono:")

    b.seccion("2. Transferencia internacional (si aplica)")
    b.parrafo("Complete esta sección solo si la cuenta donde recibirá el reembolso está fuera de "
              "Panamá.", size=8)
    b.espacio(4)
    b.campo_texto("Titular de la cuenta:")
    b.campo_texto("Dirección completa (incluya país y ciudad):")
    b.campo_texto("Banco beneficiario:")
    b.campo_texto("Número de cuenta (IBAN/CLABE):")
    b.dos_campos("Swift:", "ABA:")
    b.campo_texto("Banco intermediario (si aplica):")
    b.dos_campos("Swift del banco intermediario:", "ABA del banco intermediario:")

    c.save()
    print(f"PDF generado: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_devolucion_prima_sura.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
