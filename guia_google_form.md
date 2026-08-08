# Guía para armar el Google Form — Solicitud de Seguro (caso de una sola persona)

Esto es para el caso más simple: **una sola persona asegurada, sin dependientes**. Para
familias (cónyuge + hijos), seguí usando el cuestionario de WhatsApp — Google Forms no
maneja bien "repetir esta sección N veces".

Cómo armarlo: andá a forms.google.com → Formulario en blanco. Usá **"Agregar sección"**
(ícono de las dos líneas horizontales en la barra de herramientas de la derecha) para separar
cada bloque de abajo.

---

## Configuración general del formulario

- Título: **Solicitud de Seguro — Triple A Seguros**
- Descripción (debajo del título): *"Por favor completá todos los campos. NO incluyas los
  datos de tu tarjeta de crédito en este formulario — esos te los pedimos por separado, por
  un canal seguro."*
- En Configuración (ícono de engranaje) → **"Recopilar direcciones de correo"**: activalo, así
  sabés quién respondió.
- En Configuración → **"Respuestas"** → activá **"Recibir notificación por correo de nuevas
  respuestas"**, así te llega un aviso a tu email cada vez que alguien completa el form.

---

## Sección 1 — Datos personales

| Pregunta | Tipo de pregunta | Opciones |
|---|---|---|
| Nombre completo | Respuesta corta | — |
| Fecha de nacimiento | Fecha | — |
| Sexo | Opción múltiple | F, M |
| Nacionalidad | Respuesta corta | — |
| País de nacimiento | Respuesta corta | — |
| País de residencia | Respuesta corta | — |
| Cédula o pasaporte (número) | Respuesta corta | — |
| Adjuntar copia de cédula/pasaporte | **Subir archivo** | — |
| Peso | Respuesta corta | — |
| Estatura | Respuesta corta | — |
| Dirección de residencia completa | Párrafo | — |
| Teléfono de residencia | Respuesta corta | — |
| Teléfono celular | Respuesta corta | — |
| Correo electrónico personal | Respuesta corta (validar como email) | — |
| Estado civil | Opción múltiple | Soltero/a, Casado/a, Divorciado/a, Viudo/a, Unido/a |
| Profesión | Respuesta corta | — |
| Ocupación / cargo | Respuesta corta | — |
| Empresa donde labora | Respuesta corta | — |
| Dirección de la empresa | Párrafo | — |
| Teléfono de la oficina/empresa | Respuesta corta | — |
| Correo de la empresa | Respuesta corta | — |
| Actividad económica de la empresa | Respuesta corta | — |
| ¿Es una empresa propia? | Opción múltiple | Sí, No |
| Tipo de ocupación | Opción múltiple | Asalariado, Independiente, Jubilado |
| Si es independiente, ¿a qué actividad se dedica? | Respuesta corta | — |
| ¿Tiene otras ocupaciones o fuentes de ingreso? ¿Cuáles? | Párrafo | — |
| Ingreso anual aproximado (US$) | Opción múltiple | Menos de 10 mil, 10 a 30 mil, 30 a 50 mil, Más de 50 mil |
| País(es) donde tributa sus ingresos | Respuesta corta | — |
| Número de Identificación Tributario / RUC (si es distinto de su cédula) | Respuesta corta | — |

---

## Sección 2 — Persona Expuesta Políticamente (PEP)

*(Obligatorio por regulación — marcá las 3 preguntas como "Obligatorias")*

| Pregunta | Tipo | Opciones |
|---|---|---|
| ¿Es usted, o fue en los últimos dos años, una Persona Expuesta Políticamente? (jefe de estado/gobierno, político de alta jerarquía, funcionario gubernamental/judicial/militar de alta jerarquía, alto ejecutivo de empresa estatal, funcionario de partido político) | Opción múltiple | Sí, No |
| Si respondió Sí arriba: indique cargo actual o anterior | Respuesta corta | — |
| ¿Tiene un familiar directo (cónyuge, padres, hermanos, hijos) que sea PEP? | Opción múltiple | Sí, No |
| Si respondió Sí arriba: nombre, cargo y parentesco | Respuesta corta | — |
| ¿Es usted un colaborador cercano de una Persona Expuesta Políticamente? | Opción múltiple | Sí, No |
| Si respondió Sí arriba: nombre, cargo y relación | Respuesta corta | — |

Tip: podés usar **"Ir a la sección según la respuesta"** en las preguntas Sí/No para que solo
se muestre el campo de detalle cuando contestan "Sí" — no es obligatorio, pero queda más
prolijo.

---

## Sección 3 — Cuestionario médico (las 27 preguntas oficiales)

**Truco clave de Google Forms para esto:** usá el tipo de pregunta **"Cuadrícula de opción
múltiple"** (Multiple choice grid). Con eso metés las 27 preguntas como filas y "Sí"/"No"
como las dos columnas, todo en una sola pregunta — mucho más rápido de responder que 27
preguntas separadas.

- Filas (una por cada una de las 27 preguntas — copiá el texto tal cual del archivo
  `cuestionario_cliente_recomendado.md`, sección "4. Cuestionario médico", preguntas 1 a 27).
- Columnas: `Sí`, `No`
- Marcá "Requerir una respuesta por fila".

Después de la cuadrícula, agregá:

| Pregunta | Tipo |
|---|---|
| Si contestó "Sí" en alguna, detalle: condición, cuándo ocurrió, médico tratante, medicamentos | Párrafo |
| Nombre de su médico de cabecera (y especialidad) | Respuesta corta |

---

## Sección 4 — Beneficiarios

*(A quién(es) se le entrega el beneficio de vida si el titular fallece — hasta 2 beneficiarios)*

**Beneficiario 1** (marcar como obligatorio):
- Nombre completo — Respuesta corta
- Cédula o pasaporte — Respuesta corta
- Fecha de nacimiento — Fecha
- Nacionalidad — Respuesta corta
- Parentesco con el titular — Respuesta corta
- Porcentaje asignado — Respuesta corta

**Beneficiario 2** (opcional, aclarar "dejar en blanco si solo hay un beneficiario"):
- mismos 6 campos que arriba

---

## Sección 5 — Otros

| Pregunta | Tipo | Opciones |
|---|---|---|
| ¿Tiene o tuvo otro seguro de gastos médicos? | Opción múltiple | Sí, No |
| Si Sí: compañía, número de póliza, ¿sigue vigente? | Párrafo | — |
| Forma de pago preferida | Opción múltiple | Anual, Semestral, Otra (consultar con el corredor) |
| Plan de interés (si ya lo conversó con su corredor) | Opción múltiple | Optimum Plus, Optimum, Security, Essence, Exclusive Int., Aún no sé |

---

## Cómo llega la respuesta a vos

Con "Recibir notificación por correo" activado, cada respuesta te manda un email. Desde ahí
podés copiar el contenido del correo y pegarlo directo en el campo de mensaje del agente web
(agente-formularios-worldwide-medical.onrender.com), o descargar las respuestas como hoja de
cálculo desde la pestaña "Respuestas" del formulario (ícono de Sheets) si preferís procesar
varias juntas.
