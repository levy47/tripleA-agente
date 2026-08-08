# Cómo publicar esta app en Render

## 1. Subir el código a GitHub (una sola vez)

1. Entrar a github.com y crear una cuenta si no tenés.
2. Crear un repositorio nuevo **privado** (botón "New repository"). Nombre sugerido:
   `agente-formularios-worldwide-medical`. No marcar ninguna opción de "agregar README".
3. GitHub te va a mostrar unos comandos para "push an existing repository" — copiar la URL que
   termina en `.git` (por ejemplo `https://github.com/tu-usuario/agente-formularios-worldwide-medical.git`).

## 2. Crear la cuenta en Render

1. Entrar a render.com y crear una cuenta (podés usar la misma cuenta de GitHub para entrar, es más
   rápido).
2. En el panel, click en **New +** → **Web Service**.
3. Conectar tu cuenta de GitHub y elegir el repositorio que creaste en el paso 1.

## 3. Configurar el servicio

Render debería detectar Python automáticamente. Si te pide completar algo a mano:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`
- **Plan:** el gratis ("Free") alcanza para probar. Si más adelante lo usan todos los días de forma
  seria, conviene pasar a un plan pago para que no se "duerma" por inactividad.

## 4. Variables de entorno (acá van las claves, nunca en el código)

En la sección **Environment** del servicio, agregar:

| Variable | Valor |
|---|---|
| `ANTHROPIC_API_KEY` | tu clave de Anthropic (empieza con `sk-ant-`) |
| `ACCESS_PASSWORD` | la clave de acceso que van a usar tus socios/equipo para entrar a la página |

Render las guarda de forma segura y no quedan visibles en el código ni en GitHub.

## 5. Deploy

Click en **Create Web Service** (o **Deploy**). Después de unos minutos, Render te da una URL
como `https://agente-formularios-worldwide-medical.onrender.com` — ese es el link para mandarle
a tus socios.

## Nota sobre el plan gratis

En el plan gratis, el servicio "se duerme" después de un rato sin uso y tarda unos 30-60 segundos
en despertar la primera vez que alguien entra después de la inactividad. Los archivos generados
durante una sesión (los PDFs) se guardan mientras el servicio está despierto; si se duerme y se
reinicia, esos archivos temporales se pierden (hay que volver a generarlos, no es un problema de
los datos del cliente, que ya fueron descargados). Si esto molesta en el uso diario, conviene
pasar a un plan pago.
