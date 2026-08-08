"""
English version of generar_kyc_juridico_pdf.py -- Know Your Customer (Legal
Entity) questionnaire, same layout engine (Constructor).

Usage:
    python3 src/generar_kyc_juridico_pdf_en.py --salida cuestionario_kyc_juridico_en.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL


def construir(salida):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Know Your Customer (KYC) Questionnaire — Legal Entity",
                     subtitulo_banner="Triple A Seguros",
                     etiqueta_si="Yes", etiqueta_no="No")

    b.nueva_pagina("Instructions")
    b.parrafo("Complete and save this PDF before sending it back. Do NOT include credit card details.",
              size=9, bold=True)
    b.espacio(6)

    b.seccion("1. Role / Company information")
    b.opciones("Who is completing this form?",
               ["Policyholder", "Insured", "Broker", "Payer", "Insurance Company", "Beneficiary"])
    b.dos_campos("Legal name:", "Trade name (if different):")
    b.dos_campos("Tax Registration Number (RUC):", "Tax ID Number (NIT, if different):")
    b.campo_texto("Full physical address:")
    b.dos_campos("Country of incorporation:", "Date of incorporation:")
    b.dos_campos("Country of operation:", "Line of business:")
    b.dos_campos("Phone:", "Email:")
    b.campo_texto("Country/countries where it pays taxes:")

    b.seccion("2. Directors, officers, and shareholders (10%+)")
    b.parrafo("Attach a copy of each person's ID/passport.", size=8)
    b.parrafo("Directors and officers — list each one on its own line with these 6 items: full "
              "name, ID/passport, date of birth, address, position, nationality.", size=8)
    b.campo_texto("Directors and officers:", alto_campo=45, multilinea=True)
    b.parrafo("Shareholders / ultimate beneficial owners — list each one on its own line with "
              "these 5 items: full name, ID/passport, date of birth, ownership %, nationality.",
              size=8)
    b.campo_texto("Shareholders / ultimate beneficial owners:", alto_campo=45, multilinea=True)

    b.seccion("3. Legal representative and resident agent")
    b.campo_texto("Legal representative / attorney-in-fact: full name, ID number, date of "
                   "birth, and address (attach a copy of their ID/passport):")
    b.campo_texto("Resident agent: name and address:")

    b.seccion("4. Politically Exposed Person (PEP)")
    b.parrafo("Is any director, shareholder, legal representative, or attorney-in-fact a PEP, "
              "a direct family member of one, or a close associate of one?", size=8)
    b.si_no("Answer:")
    b.campo_texto("If Yes: who, position, and relationship:")

    b.seccion("5. Financial profile and signature")
    b.opciones("Company's approximate annual income (balboas):",
               ["Under 50,000", "50,000 to 250,000", "250,000 to 500,000",
                "500,000 to 3 million", "3 to 5 million", "5 to 10 million", "Over 10 million"])
    b.campo_texto("Documents to attach: Legal Representative's ID/passport, Public Registry "
                   "Certificate, Operation Notice (if applicable).")
    b.dos_campos("Name of signer:", "Date:")

    c.save()
    print(f"PDF generated: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_kyc_juridico_en.pdf")
    args = parser.parse_args()
    construir(args.salida)


if __name__ == "__main__":
    main()
