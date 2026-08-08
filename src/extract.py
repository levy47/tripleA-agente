"""
Extrae datos estructurados del mensaje de texto libre que manda el cliente
(WhatsApp/email) usando Claude, siguiendo el esquema en mappings/schema_cliente.json.

Requiere ANTHROPIC_API_KEY en el entorno (o un perfil vía `ant auth login`).

Uso:
    python3 extract.py <mensaje_cliente.txt> <salida_datos.json>
"""
import sys
import json
from typing import Optional, List
from pydantic import BaseModel, Field
import anthropic


class Beneficiario(BaseModel):
    nombre: str
    cedula: Optional[str] = None
    edad: Optional[int] = None
    parentesco: Optional[str] = None


# Nota: la API de Claude limita a 24 parametros opcionales por schema (evita
# ineficiencia al compilar la gramatica de la salida estructurada). Un solo
# modelo plano con los ~25 campos del cliente supera ese limite, asi que se
# agrupan en sub-modelos tematicos (cada uno bien por debajo del limite) y
# se aplanan de nuevo a un dict plano despues de parsear la respuesta.
class Identificacion(BaseModel):
    nombre_completo: Optional[str] = None
    fecha_nacimiento: Optional[str] = Field(None, description="formato dd/mm/aaaa")
    cedula_o_pasaporte: Optional[str] = None
    peso: Optional[str] = None
    estatura: Optional[str] = None
    estado_civil: Optional[str] = Field(
        None, description="uno de: soltero, casado, divorciado, viudo, unido"
    )


class Contacto(BaseModel):
    direccion_residencial: Optional[str] = None
    correo_personal: Optional[str] = None
    telefono_residencia: Optional[str] = None
    telefono_celular: Optional[str] = None


class Laboral(BaseModel):
    profesion: Optional[str] = None
    ocupacion: Optional[str] = None
    ocupacion_descripcion_exacta: Optional[str] = None
    empresa_donde_labora: Optional[str] = None
    telefono_empresa: Optional[str] = None
    direccion_laboral: Optional[str] = None
    tiene_otras_ocupaciones: Optional[bool] = None
    otras_ocupaciones_detalle: Optional[str] = None


class Financiero(BaseModel):
    ingreso_anual_aproximado: Optional[str] = Field(
        None, description="uno de: menos_10mil, 10mil_30mil, 30mil_50mil, mas_50mil"
    )
    pais_donde_tributa: Optional[str] = None


class Salud(BaseModel):
    tiene_padecimiento_medico: Optional[bool] = None
    padecimiento_detalle: Optional[str] = None
    medico_cabecera_nombre: Optional[str] = None


class DatosCliente(BaseModel):
    identificacion: Identificacion = Field(default_factory=Identificacion)
    contacto: Contacto = Field(default_factory=Contacto)
    laboral: Laboral = Field(default_factory=Laboral)
    financiero: Financiero = Field(default_factory=Financiero)
    salud: Salud = Field(default_factory=Salud)
    beneficiarios: List[Beneficiario] = Field(default_factory=list)
    campos_faltantes: List[str] = Field(
        default_factory=list,
        description="nombres de campos que el mensaje del cliente no mencionaba y quedaron sin dato",
    )

    def aplanado(self) -> dict:
        """Combina los sub-modelos en un unico dict plano, compatible con las
        claves de mappings/schema_cliente.json que usan fill_pdf.py / fill_pdf_overlay.py."""
        plano = {}
        for sub in (self.identificacion, self.contacto, self.laboral, self.financiero, self.salud):
            plano.update(sub.model_dump())
        plano["beneficiarios"] = [b.model_dump() for b in self.beneficiarios]
        plano["campos_faltantes"] = list(self.campos_faltantes)
        return plano


SYSTEM_PROMPT = """Sos un asistente que extrae datos de clientes de una aseguradora (WorldWide Medical, Panamá) \
a partir del mensaje de texto libre que el cliente envía por WhatsApp o email, respondiendo un cuestionario ya conocido.

Reglas:
- Extraé únicamente lo que el mensaje dice explícita o inequívocamente. No inventes ni asumas valores.
- Si un dato no está en el mensaje, dejalo vacío/null y agregá el nombre del campo a "campos_faltantes".
- Normalizá fechas a formato dd/mm/aaaa cuando sea posible.
- Para estado_civil e ingreso_anual_aproximado, usá exactamente uno de los valores permitidos indicados en la descripción del campo, mapeando la expresión libre del cliente (ej. "gano más de 50 mil al año" -> "mas_50mil").
- Para beneficiarios, extraé una entrada por cada persona mencionada como beneficiario."""


def main():
    input_path, output_path = sys.argv[1], sys.argv[2]

    with open(input_path, encoding="utf-8") as fh:
        mensaje_cliente = fh.read()

    client = anthropic.Anthropic()

    response = client.messages.parse(
        model="claude-opus-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": mensaje_cliente}],
        output_format=DatosCliente,
    )

    datos = response.parsed_output

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(datos.aplanado(), fh, ensure_ascii=False, indent=2)

    print(f"Datos extraidos -> {output_path}")
    if datos.campos_faltantes:
        print("Campos faltantes (revisar con el cliente):", ", ".join(datos.campos_faltantes))


if __name__ == "__main__":
    main()
