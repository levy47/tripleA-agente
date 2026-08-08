"""
English version of generar_cuestionario_vida_pdf.py -- Life Insurance client
questionnaire for WorldWide Medical, same layout engine (Constructor).

Usage:
    python3 src/generar_cuestionario_vida_pdf_en.py --salida cuestionario_vida_worldwide_en.pdf
"""
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from generar_cuestionario_pdf import Constructor, AZUL

MEDICAL_QUESTIONS = [
    "Chest pain, palpitations, high blood pressure, rheumatic fever, heart murmur, heart attack, "
    "or any other heart disease?",
    "Shortness of breath, hoarseness, persistent cough, blood-streaked sputum, bronchitis, "
    "pleurisy, asthma, emphysema, tuberculosis, or any other respiratory disorder?",
    "Dizziness, fainting, epilepsy, seizures, headaches, speech impairment, paralysis, or any "
    "other neurological disorder?",
    "Jaundice, intestinal bleeding, ulcer, hernia, appendicitis, colitis, diverticulitis, "
    "hemorrhoids, or any other digestive disorder?",
    "Diabetes, thyroid, or any other endocrine disorder?",
    "Neuritis, sciatica, rheumatism, arthritis, gout, or muscle/bone disorder, including the "
    "spine?",
    "Skin disease, swollen lymph nodes, cyst, tumor, cancer, night sweats, fatigue, or similar "
    "symptom?",
    "Albumin, sugar, blood or pus in the urine, venereal disease, kidney stones, or any other "
    "renal/reproductive disorder?",
    "Any problem with your eyes, ears, nose, or throat?",
    "Allergies, anemia, or any other blood disorder?",
    "Any deformity, illness, or congenital defect?",
    "In the last 10 years, any medical exam, consultation, illness, injury, or outpatient "
    "procedure?",
    "Have you been a patient in a hospital, clinic, sanatorium, or other medical institution?",
    "Have you had an EKG, X-ray, or other specialized test?",
    "Were you advised to have any diagnostic test, hospitalization, or surgery that has not "
    "been carried out?",
    "Have you taken any prescribed medication, or received medical treatment, in the last 12 "
    "months?",
    "Do you plan to get medical treatment or a medical opinion in the next 6 months?",
    "Have you had a positive HIV test, or been diagnosed with AIDS or a related condition?",
    "Is there a family history of deaths from coronary disease, stroke, cancer, or kidney "
    "disease before age 60 (or diabetes before age 50)?",
]

MEDICAL_QUESTIONS_WOMEN = [
    "Any disorder related to menstruation, pregnancy, reproductive organs, or breasts?",
    "Are you pregnant? Indicate how many weeks.",
]

ADDITIONAL_QUESTIONS = [
    "Have you smoked cigarettes/cigars/pipes or used tobacco/nicotine in the last 24 months?",
    "Do you drink alcoholic beverages? Indicate how much and how often.",
    "Have you ever been arrested for use/possession/sale/distribution of drugs, or any related "
    "offense?",
    "Has your driver's license ever been suspended/revoked, or do you have traffic convictions/"
    "accidents?",
    "Have you engaged in risky activities (motorcycling, scuba/diving, skydiving, or similar)?",
    "Do you intend to replace, discontinue, or change any existing life/accident coverage?",
]


def construir(salida, num_beneficiarios_primarios=3, num_beneficiarios_contingentes=2,
              num_coberturas_previas=2):
    c = canvas.Canvas(salida, pagesize=letter)
    b = Constructor(c, titulo_banner="Life Insurance Application Questionnaire",
                     subtitulo_banner="Triple A Seguros — WorldWide Medical",
                     etiqueta_si="Yes", etiqueta_no="No")

    b.nueva_pagina("Instructions")
    b.parrafo("Please complete every field in this PDF and save it before sending it back.", size=9)
    b.parrafo("Attach along with this PDF a clear photo of the ID/passport of each person mentioned.",
              size=9)
    b.parrafo("IMPORTANT: Do NOT include your credit card details in this document -- we will "
              "request that separately, through a secure channel.", size=9, bold=True)
    b.espacio(10)

    b.seccion("1. Proposed Insured")
    b.campo_texto("Full name (to match with the attached ID photo):")
    b.parrafo("(Attach along with this PDF a clear photo of their ID/passport)", size=8)
    b.opciones("Sex:", ["F", "M"])
    b.campo_texto("Date of birth:")
    b.dos_campos("Country of birth:", "Nationality(ies):")
    b.campo_texto("Country of residence:")
    b.campo_texto("Full home address (country, province/state, city, street, building/house):",
                   alto_campo=15, multilinea=True)
    b.dos_campos("Home/cell phone:", "Email:")
    b.dos_campos("Profession:", "Occupation (if self-employed, indicate your line of business):")
    b.campo_texto("Employer, employer's address, and employer's line of business:")
    b.campo_texto("Years of employment at current company:")
    b.campo_texto("Duties/responsibilities at your job:")
    b.dos_campos("Annual income (amount and currency):", "Income from other activities (if any):")
    b.dos_campos("Primary care physician (name):", "Broker's name:")

    b.seccion("2. Policyholder (only if a different person than the Insured)")
    b.campo_texto("Full name, ID/passport, date of birth, sex:")
    b.campo_texto("Nationality(ies), country of birth, country of residence:")
    b.campo_texto("Relationship to the Insured:")
    b.campo_texto("Home and work address, phone numbers, email:")
    b.campo_texto("Occupation/title, employer, employer's line of business:")
    b.dos_campos("Country/countries where you pay taxes:", "Purpose of this insurance:")

    b.seccion("3. Politically Exposed Person (PEP)")
    b.parrafo("Required by regulation, for the Insured, Policyholder, and Payer if different "
              "people.", size=8)
    b.espacio(6)
    b.si_no("Are you, do you have a direct family member who is, or are you a close associate "
            "of, a Politically Exposed Person?")
    b.campo_texto("If Yes: position (and time in the position), or name/position/relationship "
                   "with the PEP:")

    b.seccion("4. Primary Beneficiaries")
    b.parrafo(f"Complete one block per primary beneficiary (up to {num_beneficiarios_primarios}). "
              "Percentages must add up to 100%.", size=8)
    b.espacio(6)
    for i in range(1, num_beneficiarios_primarios + 1):
        b.parrafo(f"Primary Beneficiary {i}", size=10, color=AZUL, bold=True)
        b.parrafo("(Attach along with this PDF a clear photo of their ID/passport)", size=8)
        b.campo_texto("Full name (to match with the attached photo):")
        b.dos_campos("Relationship to the Insured:", "Occupation:")
        b.campo_texto("Assigned percentage (must add up to 100%):")
        b.espacio(4)

    b.seccion("5. Contingent Beneficiaries (if applicable)")
    b.parrafo("Receive the benefit only if a primary beneficiary cannot.", size=8)
    b.espacio(6)
    for i in range(1, num_beneficiarios_contingentes + 1):
        b.parrafo(f"Contingent Beneficiary {i}", size=10, color=AZUL, bold=True)
        b.campo_texto("Full name:")
        b.dos_campos("Relationship to the Insured:", "Occupation:")
        b.campo_texto("Assigned percentage:")
        b.espacio(4)

    b.campo_texto("If any beneficiary is a minor: name and ID/passport of the person who will "
                   "receive the benefit on their behalf, and their relationship to the Insured:",
                   alto_campo=30, multilinea=True)

    b.seccion("6. Bank Assignment (only if applicable)")
    b.dos_campos("Bank product / bank contact:", "Assigned amount:")

    b.seccion("7. Existing Coverage or Pending Applications with Other Companies")
    b.parrafo("If you have or had other life/accident insurance.", size=8)
    b.espacio(6)
    for i in range(1, num_coberturas_previas + 1):
        b.parrafo(f"Prior Coverage {i}", size=10, color=AZUL, bold=True)
        b.dos_campos("Company name and address:", "Policy number:")
        b.dos_campos("Insured amount:", "Application date:")
        b.espacio(4)

    b.seccion("8. Medical Questionnaire")
    b.parrafo("Answer for the proposed Insured. If any answer is \"Yes\", give details below: "
              "condition, when, treating physician, treatment/medications, results, hospital "
              "name and address.", size=8)
    b.espacio(6)
    for question in MEDICAL_QUESTIONS:
        b.si_no(question)
    b.parrafo("For women only:", size=9, bold=True)
    for question in MEDICAL_QUESTIONS_WOMEN:
        b.si_no(question)
    b.parrafo("Additional:", size=9, bold=True)
    for question in ADDITIONAL_QUESTIONS:
        b.si_no(question)
    b.espacio(4)
    b.campo_texto("Details of \"Yes\" answers (indicate question number, condition, when, "
                   "treating physician, treatment/medications, results, hospital):",
                   alto_campo=50, multilinea=True)

    b.seccion("9. Financial Profile and Other")
    b.campo_texto("Annual income from activities other than your main occupation (if any):")
    b.opciones("Preferred payment frequency:", ["Annual", "Semiannual", "Quarterly", "Monthly"])

    c.save()
    print(f"PDF generated: {salida}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", default="cuestionario_vida_worldwide_en.pdf")
    parser.add_argument("--beneficiarios-primarios", type=int, default=3)
    parser.add_argument("--beneficiarios-contingentes", type=int, default=2)
    parser.add_argument("--coberturas-previas", type=int, default=2)
    args = parser.parse_args()
    construir(args.salida, num_beneficiarios_primarios=args.beneficiarios_primarios,
              num_beneficiarios_contingentes=args.beneficiarios_contingentes,
              num_coberturas_previas=args.coberturas_previas)


if __name__ == "__main__":
    main()
