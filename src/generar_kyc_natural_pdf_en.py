"""
English version of generar_kyc_natural_pdf.py -- Know Your Customer (Natural
Person) questionnaire, same layout engine (Constructor).

Usage:
    python3 src/generar_kyc_natural_pdf_en.py --salida cuestionario_kyc_natural_en.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Know Your Customer (KYC) Questionnaire — Natural Person",
                     subtitulo_banner="Triple A Seguros",
                     etiqueta_si="Yes", etiqueta_no="No")

    b.nueva_pagina("Instructions")
    b.parrafo("Complete and save this PDF before sending it back. Do NOT include credit card details.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Personal information")
    b.opciones("Who is completing this form?",
               ["Policyholder", "Insured", "Broker", "Payer", "Insurance Company", "Beneficiary"])
    b.parrafo("(Attach along with this PDF a clear photo of your ID/passport)", size=8)
    b.dos_campos("Full name:", "Date of birth:")
    b.dos_campos("Sex (F/M):", "Nationality:")
    b.dos_campos("Country of birth:", "Country of residence:")
    b.campo_texto("Full home address:")
    b.dos_campos("Phone / cell phone:", "Email:")

    b.seccion("2. Employment information")
    b.dos_campos("Profession / occupation:", "Employer:")
    b.campo_texto("Employer's address:")
    b.campo_texto("If self-employed, what is your line of business?")
    b.opciones("Approximate annual income (US$):",
               ["Under 10,000", "10,000 to 30,000", "30,000 to 50,000", "Over 50,000"])
    b.dos_campos("Other income sources? Which, and how much?", "Country/countries you pay taxes / Tax ID:")

    b.seccion("3. Politically Exposed Person (PEP)")
    b.parrafo("Are you, do you have a direct family member who is, or are you a close associate "
              "of, a Politically Exposed Person? Required by regulation.", size=8)
    b.si_no("Answer:")
    b.campo_texto("If Yes: who, position, and relationship:")

    b.seccion("4. Signature")
    b.dos_campos("Name:", "Date:")

    c.save()
    print(f"PDF generated: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_kyc_natural_en.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
