"""
English version of generar_cuestionario_pdf.py -- same fillable PDF questionnaire,
same layout engine (Constructor), translated content for English-speaking clients.

Usage:
    python3 src/generar_cuestionario_pdf_en.py --salida cuestionario_cliente_en.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL


def construir(salida, num_dependientes=5):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Health Insurance Application Questionnaire",
                     subtitulo_banner="Triple A Seguros — WorldWide Medical",
                     etiqueta_si="Yes", etiqueta_no="No")

    # --- Cover / instructions ---
    b.nueva_pagina("Instructions")
    b.parrafo("Please complete every field in this PDF and save it before sending it back.", size=9)
    b.parrafo("Attach along with this PDF a clear photo of the ID/passport of each person mentioned.",
              size=9)
    b.parrafo("IMPORTANT: Do NOT include your credit card details in this document -- we will request", size=9,
              bold=True)
    b.parrafo("that separately, through a secure channel.", size=9, bold=True)
    b.espacio(10)

    b.seccion("1. Insured Persons")
    b.campo_texto("Policyholder (full name):")
    b.campo_texto("Dependents (spouse / children, full names):")
    b.campo_texto("Payer (if different from the policyholder):")

    # --- Policyholder: identity + residence ---
    b.seccion("2. Policyholder Information")
    b.parrafo("Policyholder", size=10, color=AZUL, bold=True)
    b.parrafo("(Attach along with this PDF a clear photo of this person's ID/passport)", size=8)
    b.campo_texto("Full name (to match with the attached ID photo):")
    b.dos_campos("Weight:", "Height:")
    b.campo_texto("Full home address (country, province/state, city, street, building, apt.):",
                   alto_campo=15, multilinea=True)
    b.dos_campos("Home phone:", "Cell phone:")
    b.campo_texto("Personal email:")
    b.opciones("Marital status:", ["Single", "Married", "Divorced", "Widowed", "Domestic Partnership"])

    # --- Policyholder: employment ---
    b.seccion("Policyholder's Employment Information")
    b.dos_campos("Profession:", "Occupation / title:")
    b.campo_texto("Employer:")
    b.campo_texto("Employer's address:")
    b.dos_campos("Work phone:", "Work email:")
    b.campo_texto("Employer's line of business:")
    b.si_no("Is this your own business?")
    b.opciones("Employment type:", ["Employed", "Self-employed", "Retired"])
    b.campo_texto("If self-employed, what is your line of business?")
    b.campo_texto("Do you have other jobs or sources of income? Which ones?")
    b.opciones("Approximate annual income (US$):",
               ["Under 10,000", "10,000 to 30,000", "30,000 to 50,000", "Over 50,000"])
    b.dos_campos("Country/countries where you pay taxes:", "Tax ID Number:")

    # --- PEP ---
    b.seccion("3. Politically Exposed Person (PEP)")
    b.parrafo("Required by regulation -- cannot be skipped. For the policyholder and each adult insured.",
              size=8)
    b.espacio(6)
    b.si_no("Are you, or have you been in the last two years, a Politically Exposed Person?")
    b.campo_texto("If Yes: current or former position:")
    b.si_no("Do you have a direct family member (spouse, parents, siblings, children) who is a PEP?")
    b.campo_texto("If Yes: name, position, and relationship of the PEP family member:")
    b.si_no("Are you a close associate of a Politically Exposed Person?")
    b.campo_texto("If Yes: name, position, and relationship:")

    # --- Dependents (configurable count) ---
    b.seccion("4. Dependents (spouse / children)")
    if num_dependientes > 0:
        b.parrafo("Complete one block per dependent to be insured. Leave blank if not applicable. Dependents "
                  "are", size=8)
        b.parrafo("assumed to live in the same country as the policyholder unless stated otherwise below.",
                  size=8)
        b.parrafo(f"If you have more than {num_dependientes} dependents, add the extra ones in the Comments "
                  "section at the end of this document.", size=8)
        b.espacio(6)
        for i in range(1, num_dependientes + 1):
            b.parrafo(f"Dependent {i}", size=10, color=AZUL, bold=True)
            b.parrafo("(Attach along with this PDF a clear photo of this person's ID/passport)", size=8)
            b.campo_texto("Full name (to match with the attached ID photo):")
            b.dos_campos("Relationship to policyholder:", "Occupation:")
            b.campo_texto("Weight and height:")
            b.espacio(4)
    else:
        b.parrafo("Not applicable for this case (no dependents).", size=9)

    # --- Medical questionnaire ---
    b.seccion("5. Medical Questionnaire")
    b.parrafo("Answer for the policyholder and every person to be insured. If any answer is \"Yes\", "
              "give details below.", size=8)
    b.espacio(6)
    b.si_no("Do you have any medical condition that has ever been diagnosed?")
    b.si_no("Any prior surgery?")
    b.si_no("Do you take any recurring medication?")
    b.si_no("Have any of your parents or siblings had tuberculosis, diabetes, cancer, high blood pressure, "
            "or heart or kidney disease?")
    b.espacio(4)
    b.campo_texto("If you answered \"Yes\" to any: details (condition, when, treating physician, medications):",
                   alto_campo=40, multilinea=True)
    b.campo_texto("Name of your primary care physician (and specialty):")

    # --- Beneficiaries and other ---
    b.seccion("6. Beneficiaries")
    b.parrafo("Who will receive the life benefit if the policyholder passes away.", size=8)
    b.espacio(6)
    for i in range(1, 3):
        b.parrafo(f"Beneficiary {i}", size=10, color=AZUL, bold=True)
        b.parrafo("(Attach along with this PDF a clear photo of their ID/passport)", size=8)
        b.campo_texto("Full name (to match with the attached photo):")
        b.dos_campos("Relationship to policyholder:", "Occupation:")
        b.campo_texto("Assigned percentage (must add up to 100%):")
        b.espacio(4)

    b.seccion("7. Other")
    b.si_no("Do you have, or have you had, any other health insurance?")
    b.campo_texto("If Yes: which company, policy number, is it still active?")
    b.opciones("Preferred payment frequency:", ["Annual", "Semiannual", "Quarterly", "Monthly"])
    b.opciones("Plan of interest (if already discussed with your broker):",
               ["Optimum Plus", "Optimum", "Security", "Essence", "Exclusive Int.", "Exclusive Plus",
                "Not sure yet"])
    b.espacio(6)
    b.campo_texto("Additional comments (e.g. extra dependents, clarifications):",
                   alto_campo=50, multilinea=True)

    c.save()
    print(f"PDF generated: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_cliente_en.pdf")
    parser.add_argument("--dependientes", type=int, default=5,
                         help="number of dependent blocks to include (0 for none)")
    args = parser.parse_args()
    construir(args.salida, num_dependientes=args.dependientes)


if __name__ == "__main__":
    main()
