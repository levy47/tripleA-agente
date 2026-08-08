"""
Extrae datos de un caso de seguro (una persona o una familia completa con
dependientes y beneficiarios) a partir de:
  - un mensaje de texto libre (WhatsApp/email), y/o
  - un PDF adjunto (cuestionario ya completado, formulario escaneado, etc.)

A diferencia de extract.py (pensado para un solo asegurado sin dependientes),
este modulo devuelve una estructura con asegurado principal + dependientes[]
+ beneficiarios[], y NUNCA inventa datos de cumplimiento (PEP) ni respuestas
medicas detalladas que el documento de origen no haya preguntado explicita-
mente -- esos campos quedan marcados para que un humano se los confirme al
cliente antes de enviar el tramite.

Nota tecnica: NO usamos el modo de salida estructurada estricta de la API
(`output_config.format` / `client.messages.parse(output_format=...)`) porque
un esquema con esta cantidad de personas/campos anidados supera el limite de
complejidad de grammar que la API impone a ese modo (error "compiled grammar
is too large" / "Schema is too complex"). En su lugar, describimos el JSON
esperado en el prompt y lo validamos nosotros con Pydantic al recibirlo --
mismo resultado, sin el limite de complejidad.

Requiere ANTHROPIC_API_KEY en el entorno.

Uso:
    python3 extract_family.py --texto mensaje.txt --salida datos.json
    python3 extract_family.py --pdf cuestionario.pdf --salida datos.json
    python3 extract_family.py --texto mensaje.txt --pdf cuestionario.pdf --salida datos.json
"""
import os
import sys
import re
import json
import base64
import argparse
import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ValidationError
import anthropic


class DatosPersonales(BaseModel):
    nombre_completo: Optional[str] = None
    primer_nombre: Optional[str] = None
    segundo_nombre: Optional[str] = None
    apellidos: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    sexo: Optional[str] = None
    cedula_o_pasaporte: Optional[str] = None
    nacionalidad: Optional[str] = None
    pais_nacimiento: Optional[str] = None
    peso: Optional[str] = None
    estatura: Optional[str] = None
    direccion_residencial: Optional[str] = None
    direccion_provincia: Optional[str] = Field(
        None, description="provincia de Panama de la direccion residencial, solo si el documento "
                           "pide este desglose especifico (provincia/distrito/corregimiento/urbanizacion)")
    direccion_distrito: Optional[str] = None
    direccion_corregimiento: Optional[str] = None
    direccion_urbanizacion: Optional[str] = Field(None, description="urbanizacion o barriada")
    pais_residencia: Optional[str] = None
    correo_personal: Optional[str] = None
    telefono_residencia: Optional[str] = None
    telefono_celular: Optional[str] = None


class DatosLaboralesFinancieros(BaseModel):
    profesion: Optional[str] = None
    ocupacion: Optional[str] = None
    empresa_donde_labora: Optional[str] = None
    direccion_laboral: Optional[str] = None
    email_empresa: Optional[str] = None
    tipo_ocupacion: Optional[str] = None
    ingreso_anual_aproximado: Optional[str] = None
    pais_donde_tributa: Optional[str] = None


class Cumplimiento(BaseModel):
    pep_fue_preguntado_en_el_documento: bool = False
    es_pep_segun_documento: Optional[bool] = None


class AseguradoPrincipal(BaseModel):
    identidad: DatosPersonales = Field(default_factory=DatosPersonales)
    laboral: DatosLaboralesFinancieros = Field(default_factory=DatosLaboralesFinancieros)
    cumplimiento: Cumplimiento = Field(default_factory=Cumplimiento)
    estado_civil: Optional[str] = None


class MiembroJuridico(BaseModel):
    nombre: Optional[str] = None
    identificacion: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    direccion: Optional[str] = None
    cargo: Optional[str] = None
    nacionalidad: Optional[str] = None
    porcentaje: Optional[str] = Field(None, description="solo para accionistas, % de participacion")


class PersonaJuridica(BaseModel):
    """Solo se completa si el documento de origen es un KYC/formulario de PERSONA JURIDICA
    (empresa/sociedad), no de persona natural."""
    razon_social: Optional[str] = None
    razon_comercial: Optional[str] = None
    ruc_empresa: Optional[str] = None
    direccion_fisica_empresa: Optional[str] = None
    pais_constitucion: Optional[str] = None
    fecha_constitucion: Optional[str] = None
    pais_donde_opera_empresa: Optional[str] = None
    actividad_empresa: Optional[str] = None
    telefono_empresa: Optional[str] = None
    correo_empresa: Optional[str] = None
    sitio_web_empresa: Optional[str] = None
    pais_tributa_empresa: Optional[str] = None
    nit_empresa: Optional[str] = None
    directores: List[MiembroJuridico] = Field(default_factory=list)
    accionistas: List[MiembroJuridico] = Field(default_factory=list)
    representante_legal: Optional[MiembroJuridico] = None
    agente_residente_nombre: Optional[str] = None
    agente_residente_direccion: Optional[str] = None
    pep_fue_preguntado: bool = False
    pep_respuesta: Optional[bool] = Field(
        None, description="respuesta a la pregunta combinada de PEP (alguno de los directores/"
                           "accionistas/representante es PEP, familiar de PEP, o colaborador de PEP)")
    pep_detalle: Optional[str] = None
    ingreso_anual_aproximado: Optional[str] = Field(
        None, description="uno de: menos_50mil,50mil_250mil,250mil_500mil,500mil_3mio,3mio_5mio,"
                           "5mio_10mio,mas_10mio")
    otras_actividades_detalle: Optional[str] = None
    otras_actividades_monto: Optional[str] = None
    firma_nombre: Optional[str] = None
    firma_fecha: Optional[str] = None


class Dependiente(BaseModel):
    nombre_completo: str
    documento_identidad: Optional[str] = None
    nacionalidad: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    sexo: Optional[str] = None
    peso: Optional[str] = None
    estatura: Optional[str] = None
    ocupacion: Optional[str] = None
    parentesco: Optional[str] = None


class BeneficiarioPrimario(BaseModel):
    nombre_completo: str
    fecha_nacimiento: Optional[str] = None
    documento_identidad: Optional[str] = None
    nacionalidad: Optional[str] = None
    ocupacion: Optional[str] = None
    parentesco: Optional[str] = None
    porcentaje: Optional[str] = None


class DatosTarjetaCredito(BaseModel):
    tipo_tarjeta: Optional[str] = Field(None, description="'american_express', 'visa', 'mastercard' u 'otro'")
    tipo_tarjeta_otro: Optional[str] = None
    tarjetahabiente_nombre: Optional[str] = None
    tarjetahabiente_apellido: Optional[str] = None
    numero_tarjeta: Optional[str] = None
    fecha_expiracion_mmaa: Optional[str] = Field(None, description="formato MM/AA")
    codigo_seguridad: Optional[str] = Field(None, description="CVV/CVC, 3 digitos (4 en American Express)")
    banco_emisor: Optional[str] = None


class PolizaACobrar(BaseModel):
    nombre_asegurado: Optional[str] = None
    numero_poliza: Optional[str] = None
    prima: Optional[str] = None
    cantidad_cuotas: Optional[str] = None
    frecuencia: Optional[str] = Field(None, description="'mensual','trimestral','semestral','anual'")
    dia_cobro: Optional[str] = None
    monto_descuento: Optional[str] = None
    numero_factura: Optional[str] = None
    numero_certificado: Optional[str] = None


class AutorizacionCobroTarjeta(BaseModel):
    """Solo se completa si el documento de origen es una autorizacion de debito/cobro recurrente
    de primas por tarjeta de credito (TCR), de cualquier aseguradora (Sura, WorldWide Medical,
    Internacional de Seguros, Optima, Mercantil, ASSA, etc). Los datos de LA TARJETA (numero, tipo,
    vencimiento, CVV, banco emisor, nombre del tarjetahabiente) NO van aca -- esos se extraen aparte
    con el flujo existente de --tarjeta/DatosTarjetaCredito a partir de una foto de la tarjeta, y se
    borran del servidor apenas se genera el PDF."""
    contratante: Optional[str] = None
    nombre_asegurado_si_distinto_de_tarjetahabiente: Optional[str] = None
    identificacion_asegurado_si_distinto_de_tarjetahabiente: Optional[str] = None
    correo_1: Optional[str] = None
    correo_2: Optional[str] = None
    telefono_residencial: Optional[str] = None
    telefono_celular: Optional[str] = None
    banco_acredita: Optional[str] = Field(
        None, description="nombre del banco al que se le pide acreditar/cargar (algunos formularios, "
                           "ej. Internacional de Seguros, piden 'autorizo al banco ___')")
    frecuencia_cobro: Optional[str] = Field(None, description="'mensual','trimestral','semestral','anual'")
    monto_o_suma_total: Optional[str] = None
    renovacion_automatica: Optional[bool] = None
    polizas: List[PolizaACobrar] = Field(default_factory=list)


class DevolucionPrimaACH(BaseModel):
    """Solo se completa si el documento de origen es un formulario de pagos/devolucion de prima via
    ACH local o transferencia internacional -- el cliente RECIBE dinero (reembolso), no paga con
    tarjeta. No confundir con AutorizacionCobroTarjeta."""
    tipo_cuenta: Optional[str] = Field(None, description="'corriente' o 'ahorro'")
    numero_cuenta: Optional[str] = None
    entidad_bancaria: Optional[str] = None
    titular_cuenta: Optional[str] = None
    cedula_o_ruc: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    intl_titular_cuenta: Optional[str] = None
    intl_direccion: Optional[str] = Field(None, description="incluye pais y ciudad")
    intl_banco_beneficiario: Optional[str] = None
    intl_numero_cuenta_iban: Optional[str] = None
    intl_swift: Optional[str] = None
    intl_aba: Optional[str] = None
    intl_banco_intermediario: Optional[str] = None
    intl_banco_intermediario_swift: Optional[str] = None
    intl_banco_intermediario_aba: Optional[str] = None


class DatosVehiculo(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    tipo_traccion: Optional[str] = Field(None, description="'automatica' o 'manual'")
    anio: Optional[str] = None
    color: Optional[str] = None
    placa: Optional[str] = None
    num_pasajeros: Optional[str] = None
    numero_motor: Optional[str] = None
    numero_chasis: Optional[str] = None
    uso_vehiculo: Optional[str] = Field(None, description="'particular','comercial','autobuses','otro'")
    uso_vehiculo_otro: Optional[str] = None
    tipo_vehiculo: Optional[str] = Field(
        None, description="segun el formulario de origen: 'turismo' o '4x4' (La Regional), o "
                           "'sedan','camioneta','4x4','4x2','pick_up' (Optima) -- usa exactamente la "
                           "opcion marcada/mencionada en el documento")
    grupo_vehiculo: Optional[str] = Field(None, description="'2_a_4_ton' o '4_ton_en_adelante'")
    dispositivos_seguridad: List[str] = Field(
        default_factory=list, description="lista, valores posibles: 'inmobilizer','baston','alarma','otro'")
    dispositivos_seguridad_otro: Optional[str] = None


class DatosIncendio(BaseModel):
    """Solo se completa si el documento de origen es una Solicitud de Seguro de Incendio (ej. Optima)
    o el cuestionario de Triple A para ese producto. Datos del bien a asegurar, no de la persona
    (esos van en asegurado_principal/persona_juridica de siempre)."""
    tipo_poliza: Optional[str] = Field(None, description="'fija','declarativa','edificio_construccion'")
    bien_cubierto: Optional[str] = Field(None, description="'edificio','contenido', o ambos separados por coma")
    bien_cubierto_contenido_detalle: Optional[str] = None
    vigencia_desde: Optional[str] = None
    vigencia_hasta: Optional[str] = None
    acreedor_hipotecario: Optional[str] = None
    suma_asegurada_edificio: Optional[str] = None
    suma_asegurada_contenido: Optional[str] = None
    ocupacion_edificio: Optional[str] = Field(None, description="uso que se le da al edificio (ej. vivienda, oficina, comercio)")
    construccion_paredes: Optional[str] = Field(None, description="'concreto','metal','madera','otro'")
    construccion_paredes_otro: Optional[str] = None
    construccion_pisos: Optional[str] = Field(None, description="'concreto','metal','madera','otro'")
    construccion_pisos_otro: Optional[str] = None
    construccion_techo: Optional[str] = Field(None, description="'concreto','metal','madera','otro'")
    construccion_techo_otro: Optional[str] = None
    tiene_alarma_incendio: bool = False
    tiene_extintores: bool = False
    tiene_rociadores: bool = False
    tiene_detector_humo: bool = False
    estacion_bomberos_cercana: Optional[str] = None
    coberturas_detalle: Optional[str] = Field(None, description="texto libre: coberturas solicitadas (ej. lucro cesante) si el cliente las menciona")
    lucro_cesante_detalle: Optional[str] = None
    tiene_otros_seguros_mismos_bienes: Optional[bool] = None
    frecuencia_pago: Optional[str] = Field(None, description="'mensual','trimestral','semestral','anual'")


class DatosAutoPoliza(BaseModel):
    """Solo se completa si el documento de origen es una Solicitud de Seguro de Automovil (ej.
    Optima) o el cuestionario de Triple A para ese producto -- datos de la POLIZA/cobertura, no del
    vehiculo en si (eso va en vehiculo/DatosVehiculo)."""
    vigencia_desde: Optional[str] = None
    vigencia_hasta: Optional[str] = None
    acreedor_hipotecario: Optional[str] = None
    valor_auto: Optional[str] = None
    conductor_adicional_nombre: Optional[str] = None
    conductor_adicional_fecha_nacimiento: Optional[str] = None
    experiencia_manejo: Optional[str] = Field(None, description="'menos_2_anos','3_a_5_anos','mas_6_anos'")
    tuvo_siniestros_ultimos_5_anos: Optional[bool] = None
    frecuencia_pago: Optional[str] = Field(None, description="'mensual','trimestral','semestral','anual'")


class RespuestaMedica(BaseModel):
    numero: str = Field(..., description="ej. 'A1'..'A22' para Seccion A, 'B1'..'B5' para Seccion B")
    respuesta: str = Field(..., description="'si' o 'no'")
    detalle: Optional[str] = None


class Revision(BaseModel):
    campos_faltantes: List[str] = Field(default_factory=list)
    requiere_cuestionario_medico_detallado: bool = True
    quien_es_asegurado_principal_es_ambiguo: bool = False
    notas_para_el_corredor: Optional[str] = None


class PreferenciasPoliza(BaseModel):
    persona_que_completa_formulario: Optional[str] = Field(
        None, description="quien completa/firma el formulario KYC, uno de: 'contratante','asegurado',"
                           "'corredor','pagador','cia_seguros','beneficiario'. Solo si el documento tiene "
                           "una pregunta/checkbox explicito de este tipo (ej. '¿Quien completa este "
                           "formulario?') -- fijate MUY bien cual casilla especifica esta marcada, no "
                           "asumas 'asegurado' por defecto.")
    forma_pago: Optional[str] = Field(None, description="'anual', 'semestral', 'trimestral', 'mensual', u 'otra'")
    forma_pago_otra_texto: Optional[str] = Field(
        None, description="texto libre cuando forma_pago es 'otra' (ej. 'mensual')")
    plan_seleccionado: Optional[str] = Field(
        None, description="uno de: 'optimum_plus','optimum','security','essence','exclusive_int'. "
                           "Si el cliente pide un plan que no es ninguno de estos (ej. 'Exclusive Plus', que "
                           "no existe como casilla en el PDF actual), dejar este campo en null y describir lo "
                           "pedido en plan_no_reconocido en vez de inventar una casilla.")
    plan_no_reconocido: Optional[str] = None
    deducible_seleccionado: Optional[str] = Field(
        None, description="uno de: 'opcion_I','opcion_II','opcion_III','opcion_IV','otro'")
    tiene_seguro_previo: Optional[bool] = None
    seguro_previo_detalle: Optional[str] = None


class ExtraccionFamiliar(BaseModel):
    asegurado_principal: AseguradoPrincipal = Field(default_factory=AseguradoPrincipal)
    contratante_es_igual_al_asegurado: bool = True
    dependientes: List[Dependiente] = Field(default_factory=list)
    respuestas_medicas_detalladas: List[RespuestaMedica] = Field(default_factory=list)
    beneficiarios_primarios: List[BeneficiarioPrimario] = Field(default_factory=list)
    preferencias: PreferenciasPoliza = Field(default_factory=PreferenciasPoliza)
    persona_juridica: Optional[PersonaJuridica] = Field(
        None, description="completar SOLO si el documento de origen es un KYC/formulario de "
                           "persona juridica (empresa/sociedad); dejar null para casos de persona natural")
    datos_incendio: Optional[DatosIncendio] = Field(
        None, description="completar SOLO si el documento de origen es una Solicitud de Seguro de "
                           "Incendio o su cuestionario; dejar null en cualquier otro caso")
    datos_auto_poliza: Optional[DatosAutoPoliza] = Field(
        None, description="completar SOLO si el documento de origen es una Solicitud de Seguro de "
                           "Automovil o su cuestionario (datos de poliza/cobertura, no del vehiculo); "
                           "dejar null en cualquier otro caso")
    autorizacion_cobro: Optional[AutorizacionCobroTarjeta] = Field(
        None, description="completar SOLO si el documento de origen es una autorizacion de debito/"
                           "cobro recurrente de primas por tarjeta de credito (TCR); dejar null en "
                           "cualquier otro caso")
    devolucion_prima_ach: Optional[DevolucionPrimaACH] = Field(
        None, description="completar SOLO si el documento de origen es un formulario de pagos/"
                           "devolucion de prima via ACH o transferencia internacional; dejar null en "
                           "cualquier otro caso")
    tarjeta_desde_texto: Optional[DatosTarjetaCredito] = Field(
        None, description="completar SOLO si el CLIENTE escribio los datos de su tarjeta de credito "
                           "directamente como texto en el mensaje (numero, vencimiento y/o codigo de "
                           "seguridad tipeados) -- NUNCA si esos datos vienen de una foto de la "
                           "tarjeta, que se procesa por un canal separado y mas confiable. Si hay "
                           "tanto una foto de la tarjeta como texto con los mismos datos, dejar este "
                           "campo en null (la foto tiene prioridad). Nunca inventes ni completes "
                           "digitos faltantes.")
    revision: Revision = Field(default_factory=Revision)


ESQUEMA_JSON = json.dumps(ExtraccionFamiliar.model_json_schema(), ensure_ascii=False, indent=2)

PREGUNTAS_MEDICAS_OFICIALES = """
Seccion A (una fila por persona nombrada en la solicitud; numero -> tema):
A1. Artritis, neuritis, reumatismo, osteoporosis, lumbago, hernia discal, escoliosis u otros padecimientos de columna/musculo-esqueleticos
A2. Embolia, trombosis, migraña, dolores de cabeza u otros padecimientos cerebro-vasculares
A3. Epilepsia, desmayos, mareos, crisis nerviosa, ansiedad, depresion, convulsiones u otros padecimientos del cerebro o sistema nervioso
A4. Vision defectuosa, glaucoma, cataratas, otitis, laberintitis, mala audicion u otros padecimientos de vista/oido
A5. Presion arterial alta, problemas del corazon, soplos, valvulopatias, angina, infarto, varices, flebitis u otros padecimientos cardiovasculares
A6. Tuberculosis, enfisema, bronquitis, rinitis, sinusitis, amigdalitis, asma, alergias u otros padecimientos respiratorios
A7. Hernia hiatal, reflujo, gastritis, ulceras, colitis, hepatitis, diverticulosis, hemorroides, higado, vesicula, pancreas u otros padecimientos digestivos
A8. Calculos renales, nefritis, infecciones urinarias, sangre en la orina u otros padecimientos urinarios
A9. Padecimientos de prostata, testiculos, varicocele u otros organos reproductivos masculinos
A10. Anemia, hemofilia, trastornos de la coagulacion u otros padecimientos sanguineos
A11. Diabetes, colesterol/trigliceridos altos, tiroides, gota o trastornos endocrinos
A12. Cancer, tumor, quistes, ganglios, leucemia, quimioterapia o radioterapia
A13. Protesis, implantes, amputacion, secuelas de limitacion funcional
A14. Deformidad, enfermedad o defecto congenito, perdida de audicion/vista/algun miembro
A15. Transfusion de sangre
A16. Uso de sustancias psicoactivas/estimulantes o dependencia alcoholica
A17. Fuma o fumo tabaco/nicotina en cualquier forma
A18. Enfermedades de transmision sexual
A19. Cualquier otra enfermedad, padecimiento o accidente no mencionado arriba
A20. Practica deporte motorizado, de alto impacto o riesgo
A21. Esta embarazada (solo mujeres)
A22. Abortos, dolor pelvico, endometriosis, tumores/quistes, trastornos menstruales u otros padecimientos reproductivos femeninos (solo mujeres)

Seccion B (una fila por persona):
B1. Consulto un medico por algo no mencionado en la Seccion A
B2. Alguna alteracion de salud no mencionada arriba
B3. Examen fisico, estudios diagnosticos o pruebas especializadas recientes
B4. Antecedentes familiares (padres/hermanos) de tuberculosis, diabetes, cancer, presion alta, corazon o riñon
B5. Algun seguro de vida/accidente/salud previo fue declinado, aplazado, recargado, o tuvo reclamaciones
"""

SYSTEM_PROMPT = f"""Sos un asistente que extrae datos de solicitudes de seguro de salud (WorldWide Medical, Panama) \
a partir de un cuestionario que el cliente ya respondio (por WhatsApp, email, o un documento/PDF adjunto), y \
opcionalmente fotos o escaneos de cedula/pasaporte de una o mas personas. \
El caso puede ser una sola persona o una familia completa con dependientes y beneficiarios.

Reglas estrictas:
- Extrae unicamente lo que el documento dice explicita o inequivocamente. Nunca inventes ni asumas valores.
- Cedulas/pasaportes adjuntos (fotos o PDF escaneado): si hay una o mas imagenes de documentos de identidad, leelas \
y usa el nombre completo EXACTO tal como esta impreso, la fecha de nacimiento, el numero de cedula/pasaporte, la \
nacionalidad y el sexo que figuran ahi -- estos datos impresos en el documento oficial son mas confiables que lo que \
el cliente haya escrito a mano, asi que si hay diferencia, priorizá el dato del documento de identidad y anotá la \
discrepancia en notas_para_el_corredor. Si hay varias personas en el caso (familia) y varias fotos de identidad, \
emparejá cada foto con la persona correcta comparando el nombre impreso contra los nombres mencionados en el \
mensaje/cuestionario -- si no podés emparejar una foto con certeza, decilo en notas_para_el_corredor en vez de \
adivinar a quien pertenece.
- Determina quien es el "asegurado principal" (titular) usando las señales explicitas del documento (ej. "Primary \
Applicant", "Contratante", "Titular", a quien pertenece el email/telefono de contacto principal, quien figura como \
pagador). Si el documento simplemente numera "Applicant 1, 2, 3..." sin indicar cual es el principal, NO asumas que \
es el primero de la lista -- marca quien_es_asegurado_principal_es_ambiguo=true y explica la ambiguedad en \
notas_para_el_corredor, pero de todas formas completa tu mejor estimacion basada en el contexto.
- Las demas personas del grupo familiar van en "dependientes" (cónyuge/hijos que no sean el titular).
- PEP: nunca marques es_pep_segun_documento salvo que el documento haya preguntado EXPLICITAMENTE sobre Personas \
Expuestas Politicamente. Si no fue preguntado, dejar pep_fue_preguntado_en_el_documento=false y \
es_pep_segun_documento=null -- esto SIEMPRE debe confirmarse despues directamente con el cliente, es un dato de \
cumplimiento regulatorio que no se puede inferir.
- PERSONA JURIDICA (empresa/sociedad): si el documento de origen es un formulario "Conoce a su Cliente -- Persona \
Juridica" o similar (identificas esto porque pregunta Razon Social, RUC de una empresa, Directores/Dignatarios, \
Accionistas, Representante Legal, Agente Residente -- NO datos de una persona individual como asegurado), llena el \
objeto persona_juridica en vez de asegurado_principal. Reglas: \
(a) razon_social, ruc_empresa, direccion_fisica_empresa, etc. -- solo lo que el documento diga explicitamente. \
(b) directores y accionistas: un item por cada fila que el cliente haya completado (puede venir como texto libre \
tipo "nombre, cedula, cargo, nacionalidad" en una sola linea -- separalo en los campos correspondientes de \
MiembroJuridico). No inventes filas vacias ni completes con datos ficticios si el cliente no lleno esa fila. \
(c) PEP: igual que con personas naturales, nunca marques pep_respuesta salvo que el documento haya preguntado \
EXPLICITAMENTE. Si el cuestionario usa la pregunta combinada corta de Triple A ("¿alguno de los directores/"\
"accionistas/representante es PEP, familiar de PEP, o colaborador de PEP?"), fijate bien cual opcion (Si/No) esta \
marcada y volcala en pep_respuesta (true si Si, false si No) mas pep_fue_preguntado=true; si no fue preguntado, \
dejar pep_fue_preguntado=false y pep_respuesta=null. \
(d) ingreso_anual_aproximado: usa uno de los 7 rangos documentados en el esquema, solo si el documento lo indica.
- DIRECCION DESGLOSADA (provincia/distrito/corregimiento/urbanizacion): algunos formularios de Panama (ej. Optima \
Incendio/Auto) piden la direccion residencial partida en estos 4 campos en vez de un texto libre. Si el documento \
pide este desglose especifico, llena direccion_provincia/direccion_distrito/direccion_corregimiento/\
direccion_urbanizacion en asegurado_principal.identidad (ademas de direccion_residencial si tambien esta disponible \
como texto libre). Si el documento solo da una direccion en texto libre sin ese desglose, dejalos en null -- no \
inventes la provincia/distrito a partir de una direccion de texto libre.
- SEGURO DE INCENDIO (Optima u otra aseguradora): si el documento de origen es una Solicitud de Seguro de Incendio \
o el cuestionario de Triple A para ese producto, llena el objeto datos_incendio con los datos del BIEN a asegurar \
(tipo de poliza, construccion, medidas de seguridad, coberturas, etc.) -- solo lo que el documento diga \
explicitamente, no inventes ni asumas construccion de concreto por defecto. Las medidas de seguridad \
(tiene_alarma_incendio, tiene_extintores, tiene_rociadores, tiene_detector_humo) son booleanos independientes: \
marca true solo la(s) que el cliente marco explicitamente, las demas quedan false.
- SEGURO DE AUTOMOVIL (Optima u otra aseguradora): si el documento de origen es una Solicitud de Seguro de \
Automovil o el cuestionario de Triple A para ese producto, llena datos_auto_poliza con los datos de LA POLIZA \
(vigencia, valor del auto, conductor adicional, experiencia de manejo, siniestros) -- los datos FISICOS del \
vehiculo (marca, modelo, placa, motor, chasis, tipo, uso) NO van aca, esos se extraen aparte con el flujo de \
vehiculo/DatosVehiculo si el cliente adjunto el registro vehicular o proforma.
- AUTORIZACION DE COBRO POR TARJETA (TCR, cualquier aseguradora): llena el objeto autorizacion_cobro \
tanto si el cliente completo un documento/cuestionario de autorizacion de debito/cobro recurrente de \
primas, COMO si simplemente escribio un mensaje de texto libre (ej. WhatsApp) pidiendo autorizar el \
cobro de una o mas polizas por tarjeta -- no hace falta que sea un documento escaneado, con que el \
mensaje mencione poliza(s) y/o monto/frecuencia alcanza para llenar lo que el cliente haya dicho. Los \
datos de LA TARJETA (numero, tipo, vencimiento, CVV, banco emisor, nombre del tarjetahabiente) NUNCA \
van en este objeto -- esos vienen de una foto de la tarjeta procesada por separado. En "polizas" agrega \
un item por cada poliza que el cliente haya mencionado (puede venir como texto libre en una sola linea \
o como fila de tabla -- separalo en los campos de PolizaACobrar); no inventes filas vacias ni datos que \
el cliente no haya dado.
- DEVOLUCION DE PRIMA / FORMULARIO DE PAGOS ACH (ej. Sura "Formulario de Pagos ACH Local y \
Transferencias Internacionales"): si el documento pide una cuenta bancaria para que el CLIENTE reciba \
dinero (reembolso), no para cobrarle con tarjeta, llena devolucion_prima_ach en vez de \
autorizacion_cobro -- son cosas distintas, no las mezcles. Completa solo la seccion (ACH local o \
transferencia internacional) que el documento efectivamente tenga llena.
- TARJETA DE CREDITO ESCRITA EN TEXTO (no en foto): si en el mensaje de texto el cliente escribio los \
datos de su tarjeta de credito directamente (numero, vencimiento, codigo de seguridad), llena \
tarjeta_desde_texto con exactamente esos datos -- nunca inventes digitos ni completes lo que falte. Si \
el caso tambien incluye una FOTO de la tarjeta (procesada por separado), dejar tarjeta_desde_texto en \
null y confiar solo en la foto, que es mas confiable y es el canal recomendado.
- Historial medico detallado: el formulario oficial de WorldWide Medical tiene 22 preguntas de Seccion A + 5 de \
Seccion B, listadas abajo con su numero exacto (A1..A22, B1..B5). Si el cliente contesto el cuestionario NUEVO que \
incluye estas preguntas especificas una por una (aunque sea con su propia redaccion, siempre que quede claro a cual \
de las 27 corresponde cada respuesta), llena respuestas_medicas_detalladas con un item por cada pregunta contestada \
(numero, respuesta 'si'/'no', y detalle si el cliente dio informacion adicional), y en ese caso poné \
requiere_cuestionario_medico_detallado=false.
- Excepcion especifica (cuestionario corto de Triple A Seguros): si el documento contesta estas 4 preguntas de \
filtro -- (1) ¿tiene alguna condicion medica diagnosticada o se la han diagnosticado en algun momento?, \
(2) ¿cirugia previa?, (3) ¿toma algun medicamento recurrente?, (4) ¿algun padre/hermano tuvo tuberculosis, \
diabetes, cancer, presion alta, enfermedad del corazon o riñon? -- y las 4 respuestas son explicitamente 'No', \
ENTONCES SI podes llenar respuestas_medicas_detalladas con las 27 preguntas (A1..A22, B1..B5) todas en 'no', y \
requiere_cuestionario_medico_detallado=false. Esto aplica UNICAMENTE si las 4 preguntas de filtro fueron \
contestadas explicitamente con 'No' -- si falta alguna, o alguna es 'Si', o el documento no usa este cuestionario \
de 4 preguntas especifico, NO apliques esta excepcion.
- Para cualquier otro caso (el documento SOLO contesto una pregunta generica del tipo "¿tiene alguna condicion \
medica?" sin desglosar por las 27 preguntas especificas ni usar el cuestionario corto de 4 preguntas de arriba, o \
alguna de esas 4 preguntas fue 'Si'), NO inventes respuesta por pregunta: dejá respuestas_medicas_detalladas vacio \
y requiere_cuestionario_medico_detallado=true.

Preguntas oficiales de Seccion A y B (para que puedas identificar a cual corresponde cada respuesta del cliente):
{PREGUNTAS_MEDICAS_OFICIALES}

- Beneficiarios: si el documento menciona explicitamente a alguien como "beneficiario" (aunque tambien conteste su \
propio cuestionario y por ende tambien sea dependiente/asegurado), incluilo en beneficiarios_primarios ademas de en \
dependientes si corresponde.
- Normaliza fechas a formato dd/mm/aaaa. Para estado_civil usa uno de: soltero, casado, divorciado, viudo, unido. \
Para tipo_ocupacion usa uno de: asalariado, independiente, jubilado. Para ingreso_anual_aproximado usa uno de: \
menos_10mil, 10mil_30mil, 30mil_50mil, mas_50mil.
- Preferencias de poliza: para forma_pago usa uno de 'anual','semestral','trimestral'; si el cliente pidio otra \
frecuencia (ej. "mensual"), poné forma_pago='otra' y el texto exacto en forma_pago_otra_texto. Para \
plan_seleccionado usa EXACTAMENTE uno de: 'optimum_plus','optimum','security','essence','exclusive_int' -- estos \
son los unicos 5 planes que existen como casilla en el PDF de Solicitud. Si el cliente pide un plan con otro \
nombre (por ejemplo "Exclusive Plus", que no es ninguno de los anteriores), NO lo fuerces a ninguna de las 5 \
casillas: dejá plan_seleccionado en null y anotá el nombre exacto que pidio el cliente en plan_no_reconocido, para \
que el corredor lo revise a mano (puede ser un plan nuevo que el PDF todavia no tiene). Para deducible_seleccionado \
usa uno de: 'opcion_I','opcion_II','opcion_III','opcion_IV','otro'.
- Cualquier dato incompleto, contradictorio, o que requiera confirmacion, anotalo en campos_faltantes o en \
notas_para_el_corredor en vez de completarlo con un valor supuesto.

Respondé EXCLUSIVAMENTE con un objeto JSON valido que siga exactamente este JSON Schema (sin texto antes ni \
despues, sin bloque de codigo markdown, solo el JSON crudo):

{ESQUEMA_JSON}"""


EXTENSIONES_IMAGEN = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".webp": "image/webp", ".gif": "image/gif",
}


def _bloque_para_archivo(path: str) -> dict:
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as fh:
        b64 = base64.standard_b64encode(fh.read()).decode("utf-8")
    if ext == ".pdf":
        return {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}}
    media_type = EXTENSIONES_IMAGEN.get(ext)
    if media_type:
        return {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}}
    raise ValueError(f"Tipo de archivo no soportado: {path} (usar PDF, JPG, PNG o WEBP)")


def build_content_blocks(texto: Optional[str], adjuntos: Optional[List[str]]) -> list:
    adjuntos = adjuntos or []
    blocks = [_bloque_para_archivo(p) for p in adjuntos]

    texto_final = texto.strip() if texto else ""
    if not texto_final and not adjuntos:
        texto_final = " "
    if texto_final:
        blocks.append({"type": "text", "text": texto_final})
    elif adjuntos:
        blocks.append({"type": "text", "text": "Extrae los datos de estos documentos/imagenes."})
    return blocks


def _extraer_json(texto_respuesta: str) -> dict:
    texto_respuesta = texto_respuesta.strip()
    # por si Claude igual envuelve en ```json ... ```
    m = re.search(r"\{.*\}", texto_respuesta, re.DOTALL)
    if not m:
        raise ValueError(f"La respuesta no contenia JSON: {texto_respuesta[:500]}")
    return json.loads(m.group(0))


ESQUEMA_JSON_TARJETA = json.dumps(DatosTarjetaCredito.model_json_schema(), ensure_ascii=False, indent=2)

SYSTEM_PROMPT_TARJETA = f"""Sos un asistente que lee UNA foto de una tarjeta de credito/debito \
para completar el formulario de autorizacion de cobro recurrente de una aseguradora.

Extrae UNICAMENTE lo que este visible en la imagen:
- tipo_tarjeta: por el logo de la red ('american_express', 'visa', 'mastercard'), o 'otro' si es \
otra red (en ese caso completa tipo_tarjeta_otro con el nombre).
- tarjetahabiente_nombre y tarjetahabiente_apellido: el nombre impreso en la tarjeta, separado en \
nombre(s) y apellido(s) lo mejor que puedas.
- numero_tarjeta: el numero completo, solo digitos.
- fecha_expiracion_mmaa: formato MM/AA.
- codigo_seguridad: el CVV/CVC (3 digitos al dorso, o 4 digitos al frente en American Express), \
SOLO si esa parte de la tarjeta es visible en la imagen. Si la imagen no muestra el codigo de \
seguridad, dejalo en null -- NUNCA lo inventes ni lo derives del numero de tarjeta.
- banco_emisor: el nombre del banco, si aparece impreso en la tarjeta.

Si algun dato no es legible o no esta en la imagen, dejalo en null. No inventes ningun dato.

Respondes UNICAMENTE con un JSON que siga este esquema (sin texto adicional, sin markdown):

{ESQUEMA_JSON_TARJETA}"""


def extraer_tarjeta(ruta_imagen: str) -> DatosTarjetaCredito:
    client = anthropic.Anthropic()
    content = [
        _bloque_para_archivo(ruta_imagen),
        {"type": "text", "text": "Extrae los datos de esta tarjeta."},
    ]

    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT_TARJETA,
        messages=[{"role": "user", "content": content}],
    )

    texto_respuesta = "".join(b.text for b in response.content if b.type == "text")
    datos_dict = _extraer_json(texto_respuesta)

    try:
        return DatosTarjetaCredito.model_validate(datos_dict)
    except ValidationError as e:
        raise ValueError(f"La respuesta de Claude no siguio el esquema de tarjeta: {e}\n\nJSON recibido:\n{texto_respuesta[:1000]}")


def aplanar_tarjeta(t: DatosTarjetaCredito) -> dict:
    plano = {}
    if t.tipo_tarjeta:
        plano["tarjeta_tipo"] = t.tipo_tarjeta
    plano["tarjeta_tipo_otro"] = _v(t.tipo_tarjeta_otro)
    plano["tarjetahabiente_nombre"] = _v(t.tarjetahabiente_nombre)
    plano["tarjetahabiente_apellido"] = _v(t.tarjetahabiente_apellido)
    nombre_completo = " ".join(p for p in [t.tarjetahabiente_nombre, t.tarjetahabiente_apellido] if p)
    plano["tarjetahabiente_nombre_completo"] = nombre_completo
    plano["numero_tarjeta"] = _v(t.numero_tarjeta)
    plano["tarjeta_fecha_exp_mmaa"] = _v(t.fecha_expiracion_mmaa)
    plano["tarjeta_codigo_seguridad"] = _v(t.codigo_seguridad)
    plano["banco_emisor"] = _v(t.banco_emisor)
    return plano


ESQUEMA_JSON_VEHICULO = json.dumps(DatosVehiculo.model_json_schema(), ensure_ascii=False, indent=2)

SYSTEM_PROMPT_VEHICULO = f"""Sos un asistente que lee un documento (registro vehicular, tarjeta de \
circulacion, o proforma/factura de compra de un vehiculo) para completar una solicitud de seguro \
de automovil.

Extrae UNICAMENTE lo que este visible/impreso en el documento:
- marca, modelo, anio, color: tal como aparecen.
- placa: el numero de placa (si el vehiculo es nuevo/proforma, puede no tener placa aun -- en ese \
caso dejalo en null).
- numero_motor, numero_chasis (VIN): tal como aparecen.
- num_pasajeros: capacidad de pasajeros, si el documento lo indica.
- tipo_traccion: 'automatica' o 'manual', SOLO si el documento lo indica explicitamente -- no lo \
adivines por el modelo.

Estos otros datos casi nunca vienen en un registro vehicular o proforma -- dejalos en null salvo \
que el documento los mencione explicitamente (no los inventes en base al tipo de auto):
- uso_vehiculo, tipo_vehiculo, grupo_vehiculo, dispositivos_seguridad.

Si algun dato no es legible o no esta en el documento, dejalo en null. No inventes ningun dato.

Respondes UNICAMENTE con un JSON que siga este esquema (sin texto adicional, sin markdown):

{ESQUEMA_JSON_VEHICULO}"""


def extraer_vehiculo(ruta_documento: str) -> DatosVehiculo:
    client = anthropic.Anthropic()
    content = [
        _bloque_para_archivo(ruta_documento),
        {"type": "text", "text": "Extrae los datos del vehiculo de este documento."},
    ]

    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT_VEHICULO,
        messages=[{"role": "user", "content": content}],
    )

    texto_respuesta = "".join(b.text for b in response.content if b.type == "text")
    datos_dict = _extraer_json(texto_respuesta)

    try:
        return DatosVehiculo.model_validate(datos_dict)
    except ValidationError as e:
        raise ValueError(f"La respuesta de Claude no siguio el esquema de vehiculo: {e}\n\nJSON recibido:\n{texto_respuesta[:1000]}")


def aplanar_vehiculo(v: DatosVehiculo) -> dict:
    plano = {
        "vehiculo_marca": _v(v.marca),
        "vehiculo_modelo": _v(v.modelo),
        "vehiculo_anio": _v(v.anio),
        "vehiculo_color": _v(v.color),
        "vehiculo_placa": _v(v.placa),
        "vehiculo_num_pasajeros": _v(v.num_pasajeros),
        "vehiculo_numero_motor": _v(v.numero_motor),
        "vehiculo_numero_chasis": _v(v.numero_chasis),
        "vehiculo_uso_otro": _v(v.uso_vehiculo_otro),
        "vehiculo_dispositivos_seguridad_otro": _v(v.dispositivos_seguridad_otro),
    }
    if v.tipo_traccion:
        plano["vehiculo_tipo_traccion"] = v.tipo_traccion
    if v.uso_vehiculo:
        plano["vehiculo_uso"] = v.uso_vehiculo
    if v.tipo_vehiculo:
        plano["vehiculo_tipo"] = v.tipo_vehiculo
    if v.grupo_vehiculo:
        plano["vehiculo_grupo"] = v.grupo_vehiculo
    if v.dispositivos_seguridad:
        plano["vehiculo_dispositivos_seguridad"] = v.dispositivos_seguridad
    return plano


def extraer(texto: Optional[str], adjuntos: Optional[List[str]] = None) -> ExtraccionFamiliar:
    client = anthropic.Anthropic()
    content = build_content_blocks(texto, adjuntos)

    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )

    texto_respuesta = "".join(b.text for b in response.content if b.type == "text")
    datos_dict = _extraer_json(texto_respuesta)

    try:
        return ExtraccionFamiliar.model_validate(datos_dict)
    except ValidationError as e:
        raise ValueError(f"La respuesta de Claude no siguio el esquema esperado: {e}\n\nJSON recibido:\n{texto_respuesta[:2000]}")


def _calcular_edad(fecha_str: Optional[str]) -> Optional[str]:
    if not fecha_str:
        return None
    try:
        d, m, y = [int(p) for p in fecha_str.strip().split("/")]
        nacimiento = datetime.date(y, m, d)
    except Exception:
        return None
    hoy = datetime.date.today()
    edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
    return str(edad)


def _v(x):
    return x if x not in (None, "") else ""


# Mapea "A1".."A22" / "B1".."B5" a las claves exactas del mapping del Solicitud
# (mappings/schema_solicitud_extra.json).
CLAVES_MEDICAS = {
    "A1": "medico_seccionA_1_columna_musculoesqueletico",
    "A2": "medico_seccionA_2_cerebro_vascular",
    "A3": "medico_seccionA_3_neurologico_psiquiatrico",
    "A4": "medico_seccionA_4_vista_oido",
    "A5": "medico_seccionA_5_cardiovascular",
    "A6": "medico_seccionA_6_respiratorio",
    "A7": "medico_seccionA_7_digestivo",
    "A8": "medico_seccionA_8_urinario",
    "A9": "medico_seccionA_9_reproductivo_masculino",
    "A10": "medico_seccionA_10_sangre",
    "A11": "medico_seccionA_11_endocrino_diabetes",
    "A12": "medico_seccionA_12_cancer_tumor",
    "A13": "medico_seccionA_13_protesis_amputacion",
    "A14": "medico_seccionA_14_deformidad_congenita",
    "A15": "medico_seccionA_15_transfusion_sangre",
    "A16": "medico_seccionA_16_sustancias_alcohol",
    "A17": "medico_seccionA_17_fuma_tabaco",
    "A18": "medico_seccionA_18_ets",
    "A19": "medico_seccionA_19_otra_enfermedad_no_mencionada",
    "A20": "medico_seccionA_20_deporte_riesgo",
    "A21": "medico_seccionA_21_embarazo",
    "A22": "medico_seccionA_22_reproductivo_femenino",
    "B1": "medico_seccionB_1_consulta_medica_no_mencionada",
    "B2": "medico_seccionB_2_alteracion_salud_no_mencionada",
    "B3": "medico_seccionB_3_examen_fisico_estudios",
    "B4": "medico_seccionB_4_antecedentes_familiares",
    "B5": "medico_seccionB_5_seguro_declinado_aplazado",
}


def aplanar_familia(ext: ExtraccionFamiliar) -> dict:
    """Convierte la extraccion anidada en el dict plano que fill_pdf.py y
    fill_pdf_overlay.py esperan, siguiendo las mismas claves usadas en
    mappings/schema_cliente.json, schema_kyc_extra.json y
    schema_solicitud_extra.json."""
    ap = ext.asegurado_principal
    idn = ap.identidad
    lab = ap.laboral

    plano = {
        # --- reusados entre KYC y Solicitud (schema_cliente.json) ---
        "nombre_completo": _v(idn.nombre_completo),
        "fecha_nacimiento": _v(idn.fecha_nacimiento),
        "cedula_o_pasaporte": _v(idn.cedula_o_pasaporte),
        "peso": _v(idn.peso),
        "estatura": _v(idn.estatura),
        "direccion_residencial": _v(idn.direccion_residencial),
        "direccion_provincia": _v(idn.direccion_provincia),
        "direccion_distrito": _v(idn.direccion_distrito),
        "direccion_corregimiento": _v(idn.direccion_corregimiento),
        "direccion_urbanizacion": _v(idn.direccion_urbanizacion),
        "telefono_residencia": _v(idn.telefono_residencia),
        "telefono_celular": _v(idn.telefono_celular),
        "correo_personal": _v(idn.correo_personal),
        "profesion": _v(lab.profesion),
        "ocupacion": _v(lab.ocupacion),
        "empresa_donde_labora": _v(lab.empresa_donde_labora),
        "direccion_laboral": _v(lab.direccion_laboral),
        "estado_civil": _v(ap.estado_civil),
        "ingreso_anual_aproximado": _v(lab.ingreso_anual_aproximado),
        "pais_donde_tributa": _v(lab.pais_donde_tributa),

        # --- especificos del KYC ---
        "persona_que_completa": "asegurado",
        "apellido_1": _v(idn.apellidos),
        "apellido_2": "",
        "nombre_1": _v(idn.primer_nombre),
        "nombre_2": _v(idn.segundo_nombre),
        "pais_nacimiento": _v(idn.pais_nacimiento),
        "nacionalidad": _v(idn.nacionalidad),
        "pais_residencia": _v(idn.pais_residencia),
        "genero": (idn.sexo or "").strip().upper()[:1],
        "pasaporte": "",
        "numero_identificacion_tributario": "",
        "otras_ocupaciones_detalle": "",
        "otras_ocupaciones_monto": "",
        "ocupacion_descripcion_exacta": "",
        "firma_fecha": "",

        # --- especificos del Solicitud (operativos, los completa el corredor) ---
        "tipo_solicitud": "poliza_nueva",
        "plan_seleccionado": "",
        "deducible_seleccionado": "",
        "forma_pago": "",
        "forma_pago_otra_texto": "",
        "persona_completa_formulario": "asegurado",

        "asegurado_primer_nombre": _v(idn.primer_nombre),
        "asegurado_segundo_nombre": _v(idn.segundo_nombre),
        "asegurado_apellidos": _v(idn.apellidos),
        "asegurado_sexo": (idn.sexo or "").strip().lower()[:1],
        "asegurado_nacionalidad": _v(idn.nacionalidad),
        "asegurado_edad": _calcular_edad(idn.fecha_nacimiento) or "",
        "asegurado_pais_nacimiento": _v(idn.pais_nacimiento),
        "asegurado_pais_residencia": _v(idn.pais_residencia),
        "asegurado_tel_oficina": "",
        "asegurado_fax": "",
        "asegurado_actividad_economica_empresa": "",
        "asegurado_empresa_propia": "",
        "asegurado_email_empresa": _v(lab.email_empresa),
        "asegurado_tipo_ocupacion": _v(lab.tipo_ocupacion),
        "asegurado_actividad_independiente_detalle": "",

        "ingreso_anual_otras_actividades": "",
        "hijos_19_24_estudiantes_tiempo_completo": "",
        "historial_medico_detalle_tabla": "",
        "tiene_seguro_gastos_medicos_previo": "",
    }

    # --- Respuestas medicas detalladas (Seccion A/B), solo si el cliente las contesto una por una ---
    detalles_si = []
    for r in ext.respuestas_medicas_detalladas:
        clave = CLAVES_MEDICAS.get(r.numero.strip().upper())
        if not clave:
            continue
        respuesta_norm = (r.respuesta or "").strip().lower()
        plano[clave] = "si" if respuesta_norm in ("si", "sí", "yes", "true") else "no"
        if plano[clave] == "si" and r.detalle:
            detalles_si.append(f"{r.numero}: {r.detalle}")
    if detalles_si:
        plano["historial_medico_detalle_tabla"] = " || ".join(detalles_si)

    # --- Dependientes: tabla es un solo campo de texto libre en el PDF ---
    filas_dependientes = []
    for d in ext.dependientes:
        fila = " | ".join([
            _v(d.nombre_completo) or "(nombre no indicado)",
            _v(d.documento_identidad) or "(documento no indicado)",
            _v(d.nacionalidad) or "(nacionalidad no indicada)",
            _v(d.fecha_nacimiento) or "(fecha no indicada)",
            _v(d.sexo) or "(sexo no indicado)",
            _v(d.peso) or "-",
            _v(d.estatura) or "-",
            _v(d.ocupacion) or "-",
            _v(d.parentesco) or "(parentesco no indicado)",
        ])
        filas_dependientes.append(fila)
    plano["dependientes_tabla_texto"] = " || ".join(filas_dependientes)

    # --- Beneficiarios primarios: el PDF solo tiene 3 filas reales ---
    beneficiarios = ext.beneficiarios_primarios[:3]
    porcentaje_default = "100" if len(beneficiarios) == 1 else ""
    for i, b in enumerate(beneficiarios, start=1):
        plano[f"beneficiario_primario_{i}_nombre"] = _v(b.nombre_completo)
        plano[f"beneficiario_primario_{i}_fecha_nacimiento"] = _v(b.fecha_nacimiento)
        plano[f"beneficiario_primario_{i}_documento_identidad"] = _v(b.documento_identidad)
        plano[f"beneficiario_primario_{i}_nacionalidad"] = _v(b.nacionalidad)
        plano[f"beneficiario_primario_{i}_ocupacion"] = _v(b.ocupacion)
        plano[f"beneficiario_primario_{i}_parentesco"] = _v(b.parentesco)
        plano[f"beneficiario_primario_{i}_porcentaje"] = _v(b.porcentaje) or porcentaje_default

    # --- Preferencias de poliza ---
    pref = ext.preferencias
    plano["forma_pago"] = _v(pref.forma_pago)
    plano["forma_pago_otra_texto"] = _v(pref.forma_pago_otra_texto)
    plano["plan_seleccionado"] = _v(pref.plan_seleccionado)
    plano["deducible_seleccionado"] = _v(pref.deducible_seleccionado)
    if pref.persona_que_completa_formulario:
        plano["persona_que_completa"] = pref.persona_que_completa_formulario
        plano["persona_completa_formulario"] = pref.persona_que_completa_formulario

    # --- PEP: solo se completa si el documento pregunto EXPLICITAMENTE (ap.cumplimiento ya
    # garantiza esto -- ver instruccion del prompt). Un "No" a la pregunta combinada de nuestro
    # propio cuestionario cubre las 3 categorias oficiales del KYC (PEP propio/familiar/colaborador)
    # de forma segura. Un "Si" NO se reparte entre las 3 categorias -- eso requiere que el corredor
    # confirme cual aplica, asi que se deja en blanco pero se registra el detalle para que no se
    # pierda la respuesta.
    avisos = []
    pep_preguntado = ap.cumplimiento.pep_fue_preguntado_en_el_documento
    pep_valor = ap.cumplimiento.es_pep_segun_documento
    if pep_preguntado and pep_valor is False:
        plano["pep_titular"] = "no"
        plano["pep_contratante"] = "no"
        plano["es_pep"] = "no"
        plano["es_familiar_pep"] = "no"
        plano["es_colaborador_pep"] = "no"
    elif pep_preguntado and pep_valor is True:
        avisos.append("cliente contesto SI a PEP -- confirmar con el corredor cual categoria "
                       "aplica (PEP propio / familiar / colaborador cercano) antes de marcar el KYC")
    else:
        avisos.append("falta preguntar PEP")

    if ext.revision.quien_es_asegurado_principal_es_ambiguo:
        avisos.append("confirmar quien es el asegurado principal")
    if ext.revision.requiere_cuestionario_medico_detallado:
        avisos.append("falta cuestionario medico detallado (Seccion A/B)")
    if pref.plan_no_reconocido:
        avisos.append(f"plan pedido por el cliente no esta en el PDF: '{pref.plan_no_reconocido}'")

    if ext.persona_juridica:
        pj = ext.persona_juridica
        plano.update(aplanar_persona_juridica(pj))
        # Caso de empresa: los avisos de persona natural armados arriba (medico, PEP
        # individual, asegurado principal ambiguo) no aplican -- se reemplazan por completo.
        avisos = []
        if not pj.pep_fue_preguntado:
            avisos.append("falta preguntar PEP")
        elif pj.pep_respuesta is True:
            avisos.append("cliente contesto SI a PEP (empresa) -- confirmar con el corredor cual "
                           "categoria aplica (propio/familiar/colaborador) antes de marcar el KYC")
        if not pj.directores and not pj.accionistas:
            avisos.append("no se completaron directores ni accionistas")
        if pref.plan_no_reconocido:
            avisos.append(f"plan pedido por el cliente no esta en el PDF: '{pref.plan_no_reconocido}'")

    if ext.datos_incendio:
        plano.update(aplanar_incendio(ext.datos_incendio))

    if ext.datos_auto_poliza:
        plano.update(aplanar_auto_poliza(ext.datos_auto_poliza))

    if ext.autorizacion_cobro:
        plano.update(aplanar_autorizacion_cobro(ext.autorizacion_cobro))
        if not plano.get("forma_pago") and ext.autorizacion_cobro.frecuencia_cobro:
            plano["forma_pago"] = ext.autorizacion_cobro.frecuencia_cobro

    if ext.devolucion_prima_ach:
        plano.update(aplanar_devolucion_ach(ext.devolucion_prima_ach))

    if ext.tarjeta_desde_texto:
        plano.update(aplanar_tarjeta(ext.tarjeta_desde_texto))

    if avisos:
        plano["comentarios_adicionales_1"] = "PENDIENTE DE REVISAR: " + "; ".join(avisos) + "."

    return plano


def aplanar_persona_juridica(pj: PersonaJuridica) -> dict:
    plano = {
        "razon_social": _v(pj.razon_social),
        "razon_comercial": _v(pj.razon_comercial),
        "ruc_empresa": _v(pj.ruc_empresa),
        "direccion_fisica_empresa": _v(pj.direccion_fisica_empresa),
        "pais_constitucion": _v(pj.pais_constitucion),
        "fecha_constitucion": _v(pj.fecha_constitucion),
        "pais_donde_opera_empresa": _v(pj.pais_donde_opera_empresa),
        "actividad_empresa": _v(pj.actividad_empresa),
        "telefono_empresa": _v(pj.telefono_empresa),
        "correo_empresa": _v(pj.correo_empresa),
        "sitio_web_empresa": _v(pj.sitio_web_empresa),
        "pais_tributa_empresa": _v(pj.pais_tributa_empresa),
        "nit_empresa": _v(pj.nit_empresa),
        "agente_residente_nombre": _v(pj.agente_residente_nombre),
        "agente_residente_direccion": _v(pj.agente_residente_direccion),
        "juridica_otras_actividades_detalle": _v(pj.otras_actividades_detalle),
        "juridica_otras_actividades_monto": _v(pj.otras_actividades_monto),
        "juridica_firma_nombre": _v(pj.firma_nombre),
        "juridica_firma_fecha": _v(pj.firma_fecha),
    }
    if pj.ingreso_anual_aproximado:
        plano["juridica_ingreso_anual"] = pj.ingreso_anual_aproximado

    for i in range(1, 5):
        d = pj.directores[i - 1] if i <= len(pj.directores) else None
        plano[f"director_{i}_nombre"] = _v(d.nombre) if d else ""
        plano[f"director_{i}_identificacion"] = _v(d.identificacion) if d else ""
        plano[f"director_{i}_fecha_nacimiento"] = _v(d.fecha_nacimiento) if d else ""
        plano[f"director_{i}_direccion"] = _v(d.direccion) if d else ""
        plano[f"director_{i}_cargo"] = _v(d.cargo) if d else ""
        plano[f"director_{i}_nacionalidad"] = _v(d.nacionalidad) if d else ""

    for i in range(1, 5):
        a = pj.accionistas[i - 1] if i <= len(pj.accionistas) else None
        plano[f"accionista_{i}_nombre"] = _v(a.nombre) if a else ""
        plano[f"accionista_{i}_identificacion"] = _v(a.identificacion) if a else ""
        plano[f"accionista_{i}_fecha_nacimiento"] = _v(a.fecha_nacimiento) if a else ""
        plano[f"accionista_{i}_porcentaje"] = _v(a.porcentaje) if a else ""
        plano[f"accionista_{i}_nacionalidad"] = _v(a.nacionalidad) if a else ""

    rl = pj.representante_legal
    plano["representante_legal_nombre"] = _v(rl.nombre) if rl else ""
    plano["representante_legal_identificacion"] = _v(rl.identificacion) if rl else ""
    plano["representante_legal_fecha_nacimiento"] = _v(rl.fecha_nacimiento) if rl else ""
    plano["representante_legal_direccion"] = _v(rl.direccion) if rl else ""
    plano["representante_legal_nacionalidad"] = _v(rl.nacionalidad) if rl else ""

    if pj.pep_fue_preguntado and pj.pep_respuesta is False:
        plano["juridica_pep_titular"] = "no"
        plano["juridica_pep_familiar"] = "no"
        plano["juridica_pep_colaborador"] = "no"
    if pj.pep_detalle:
        plano["juridica_pep_titular_cargo"] = _v(pj.pep_detalle)

    return plano


def aplanar_incendio(di: DatosIncendio) -> dict:
    plano = {
        "incendio_tipo_poliza": _v(di.tipo_poliza),
        "incendio_bien_cubierto": _v(di.bien_cubierto),
        "incendio_bien_cubierto_contenido_detalle": _v(di.bien_cubierto_contenido_detalle),
        "incendio_vigencia_desde": _v(di.vigencia_desde),
        "incendio_vigencia_hasta": _v(di.vigencia_hasta),
        "incendio_acreedor_hipotecario": _v(di.acreedor_hipotecario),
        "incendio_suma_asegurada_edificio": _v(di.suma_asegurada_edificio),
        "incendio_suma_asegurada_contenido": _v(di.suma_asegurada_contenido),
        "incendio_ocupacion_edificio": _v(di.ocupacion_edificio),
        "incendio_construccion_paredes": _v(di.construccion_paredes),
        "incendio_construccion_paredes_otro": _v(di.construccion_paredes_otro),
        "incendio_construccion_pisos": _v(di.construccion_pisos),
        "incendio_construccion_pisos_otro": _v(di.construccion_pisos_otro),
        "incendio_construccion_techo": _v(di.construccion_techo),
        "incendio_construccion_techo_otro": _v(di.construccion_techo_otro),
        "incendio_alarma_incendio": "si" if di.tiene_alarma_incendio else "",
        "incendio_extintores": "si" if di.tiene_extintores else "",
        "incendio_rociadores": "si" if di.tiene_rociadores else "",
        "incendio_detector_humo": "si" if di.tiene_detector_humo else "",
        "incendio_estacion_bomberos_cercana": _v(di.estacion_bomberos_cercana),
        "incendio_coberturas_detalle": _v(di.coberturas_detalle),
        "incendio_lucro_cesante_detalle": _v(di.lucro_cesante_detalle),
        "incendio_frecuencia_pago": _v(di.frecuencia_pago),
    }
    if di.tiene_otros_seguros_mismos_bienes is not None:
        plano["incendio_otros_seguros_mismos_bienes"] = "si" if di.tiene_otros_seguros_mismos_bienes else "no"
    return plano


def aplanar_auto_poliza(dap: DatosAutoPoliza) -> dict:
    plano = {
        "auto_poliza_vigencia_desde": _v(dap.vigencia_desde),
        "auto_poliza_vigencia_hasta": _v(dap.vigencia_hasta),
        "auto_poliza_acreedor_hipotecario": _v(dap.acreedor_hipotecario),
        "auto_poliza_valor_auto": _v(dap.valor_auto),
        "auto_poliza_conductor_adicional_nombre": _v(dap.conductor_adicional_nombre),
        "auto_poliza_conductor_adicional_fecha_nacimiento": _v(dap.conductor_adicional_fecha_nacimiento),
        "auto_poliza_experiencia_manejo": _v(dap.experiencia_manejo),
        "auto_poliza_frecuencia_pago": _v(dap.frecuencia_pago),
    }
    if dap.tuvo_siniestros_ultimos_5_anos is not None:
        plano["auto_poliza_siniestros_ultimos_5_anos"] = "si" if dap.tuvo_siniestros_ultimos_5_anos else "no"
    return plano


MAX_POLIZAS_A_COBRAR = 6


def aplanar_autorizacion_cobro(ac: AutorizacionCobroTarjeta) -> dict:
    plano = {
        "cobro_contratante": _v(ac.contratante),
        "cobro_nombre_asegurado_si_distinto": _v(ac.nombre_asegurado_si_distinto_de_tarjetahabiente),
        "cobro_identificacion_asegurado_si_distinto": _v(ac.identificacion_asegurado_si_distinto_de_tarjetahabiente),
        "cobro_correo_1": _v(ac.correo_1),
        "cobro_correo_2": _v(ac.correo_2),
        "cobro_telefono_residencial": _v(ac.telefono_residencial),
        "cobro_telefono_celular": _v(ac.telefono_celular),
        "cobro_banco_acredita": _v(ac.banco_acredita),
        "cobro_frecuencia": _v(ac.frecuencia_cobro),
        "cobro_monto_o_suma_total": _v(ac.monto_o_suma_total),
    }
    if ac.renovacion_automatica is not None:
        plano["cobro_renovacion_automatica"] = "si" if ac.renovacion_automatica else "no"

    for i in range(1, MAX_POLIZAS_A_COBRAR + 1):
        p = ac.polizas[i - 1] if i <= len(ac.polizas) else None
        plano[f"poliza_{i}_nombre_asegurado"] = _v(p.nombre_asegurado) if p else ""
        plano[f"poliza_{i}_numero_poliza"] = _v(p.numero_poliza) if p else ""
        plano[f"poliza_{i}_prima"] = _v(p.prima) if p else ""
        plano[f"poliza_{i}_cantidad_cuotas"] = _v(p.cantidad_cuotas) if p else ""
        plano[f"poliza_{i}_frecuencia"] = _v(p.frecuencia) if p else ""
        plano[f"poliza_{i}_dia_cobro"] = _v(p.dia_cobro) if p else ""
        plano[f"poliza_{i}_monto_descuento"] = _v(p.monto_descuento) if p else ""
        plano[f"poliza_{i}_numero_factura"] = _v(p.numero_factura) if p else ""
        plano[f"poliza_{i}_numero_certificado"] = _v(p.numero_certificado) if p else ""

    return plano


def aplanar_devolucion_ach(da: DevolucionPrimaACH) -> dict:
    return {
        "ach_tipo_cuenta": _v(da.tipo_cuenta),
        "ach_numero_cuenta": _v(da.numero_cuenta),
        "ach_entidad_bancaria": _v(da.entidad_bancaria),
        "ach_titular_cuenta": _v(da.titular_cuenta),
        "ach_cedula_o_ruc": _v(da.cedula_o_ruc),
        "ach_correo": _v(da.correo),
        "ach_telefono": _v(da.telefono),
        "ach_intl_titular_cuenta": _v(da.intl_titular_cuenta),
        "ach_intl_direccion": _v(da.intl_direccion),
        "ach_intl_banco_beneficiario": _v(da.intl_banco_beneficiario),
        "ach_intl_numero_cuenta_iban": _v(da.intl_numero_cuenta_iban),
        "ach_intl_swift": _v(da.intl_swift),
        "ach_intl_aba": _v(da.intl_aba),
        "ach_intl_banco_intermediario": _v(da.intl_banco_intermediario),
        "ach_intl_banco_intermediario_swift": _v(da.intl_banco_intermediario_swift),
        "ach_intl_banco_intermediario_aba": _v(da.intl_banco_intermediario_aba),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--texto", default=None, help="ruta a un archivo de texto con el mensaje del cliente")
    parser.add_argument("--pdf", default=None, help="(alias de --adjunto, para compatibilidad)")
    parser.add_argument("--adjunto", action="append", default=[],
                         help="ruta a un PDF/imagen adjunto (cuestionario, cedula, pasaporte). Se puede repetir.")
    parser.add_argument("--tarjeta", default=None,
                         help="ruta a una foto de la tarjeta de credito, para el formulario de pago (opcional)")
    parser.add_argument("--vehiculo", default=None,
                         help="ruta al registro vehicular/tarjeta de circulacion o proforma del vehiculo (opcional)")
    parser.add_argument("--salida", required=True, help="ruta del JSON de salida (estructura anidada, sin aplanar)")
    parser.add_argument("--salida-plana", default=None, help="ruta opcional para el JSON ya aplanado, listo para fill_pdf.py")
    args = parser.parse_args()

    adjuntos = list(args.adjunto)
    if args.pdf:
        adjuntos.append(args.pdf)

    if not args.texto and not adjuntos and not args.tarjeta and not args.vehiculo:
        print("Hay que pasar --texto, --adjunto, --tarjeta y/o --vehiculo (uno o mas)", file=sys.stderr)
        sys.exit(1)

    texto = None
    if args.texto:
        with open(args.texto, encoding="utf-8") as fh:
            texto = fh.read()

    tarjeta = None
    if args.tarjeta:
        tarjeta = extraer_tarjeta(args.tarjeta)

    vehiculo = None
    if args.vehiculo:
        vehiculo = extraer_vehiculo(args.vehiculo)

    if texto or adjuntos:
        resultado = extraer(texto, adjuntos)
    else:
        resultado = ExtraccionFamiliar()

    salida_dict = resultado.model_dump()
    if tarjeta:
        salida_dict["pago_tarjeta"] = tarjeta.model_dump()
    if vehiculo:
        salida_dict["vehiculo"] = vehiculo.model_dump()

    with open(args.salida, "w", encoding="utf-8") as fh:
        json.dump(salida_dict, fh, ensure_ascii=False, indent=2)

    if args.salida_plana:
        plano = aplanar_familia(resultado)
        if tarjeta:
            plano.update(aplanar_tarjeta(tarjeta))
            mes, _, anio = (tarjeta.fecha_expiracion_mmaa or "").partition("/")
            plano["tarjeta_exp_mes"] = mes.strip()
            plano["tarjeta_exp_anio"] = anio.strip()
        if vehiculo:
            plano.update(aplanar_vehiculo(vehiculo))
        with open(args.salida_plana, "w", encoding="utf-8") as fh:
            json.dump(plano, fh, ensure_ascii=False, indent=2)

    print(f"Datos extraidos -> {args.salida}")
    if resultado.revision.quien_es_asegurado_principal_es_ambiguo:
        print("ATENCION: no quedo claro quien es el asegurado principal, revisar con el corredor.")
    if resultado.revision.requiere_cuestionario_medico_detallado:
        print("ATENCION: falta el cuestionario medico detallado (22 preguntas de Seccion A).")
    if not resultado.asegurado_principal.cumplimiento.pep_fue_preguntado_en_el_documento:
        print("ATENCION: falta preguntar PEP directamente al cliente.")
    if resultado.revision.campos_faltantes:
        print("Campos faltantes:", ", ".join(resultado.revision.campos_faltantes))
    if resultado.revision.notas_para_el_corredor:
        print("Notas:", resultado.revision.notas_para_el_corredor)


if __name__ == "__main__":
    main()
