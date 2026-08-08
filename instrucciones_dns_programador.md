Hola! Necesito que agregues un registro DNS en el dominio aaa.com.pa para conectar un
subdominio nuevo a una app que tenemos hosteada en Render.

**Registro a crear:**

| Campo | Valor |
|---|---|
| Tipo | CNAME |
| Host / Nombre | `formulario` |
| Apunta a / Valor / Target | `agente-formularios-worldwide-medical.onrender.com` |
| TTL | El que esté por defecto (o 3600) |

Esto hace que `formulario.aaa.com.pa` apunte a nuestra app en Render.

Una vez que lo agregues, avisame para verificarlo del lado de Render (Render detecta el
registro automáticamente y genera el certificado SSL solo — puede tardar unos minutos hasta
24 horas en propagar, dependiendo del proveedor de DNS).

Gracias!
