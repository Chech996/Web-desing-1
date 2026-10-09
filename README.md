# GC Legal — Gómez & Cadena Abogados

Sitio web estático multipágina de GC Legal («Derecho a la solución»). HTML, CSS y JS vanilla; la única dependencia externa es Google Fonts.

## Estructura

```
index.html                         Inicio
servicios/                         Directorio con filtro (Todos / Empresas / Personas)
servicios/empresas/                Hub empresarial + 6 servicios
servicios/personas/                Hub personal + 2 servicios
como-funciona/  nosotros/  contacto/  terminos/  privacidad/
assets/css/styles.css              Sistema de diseño (tokens, claro/oscuro, componentes)
assets/js/main.js                  Tema, menú, menú móvil, filtro, formulario
scripts/content.py                 TODO el contenido (servicios, FAQ, datos de contacto)
scripts/build.py                   Generador de las páginas
```

## Editar contenido

1. Edita `scripts/content.py` (textos) o `scripts/build.py` (plantillas).
2. Regenera: `python3 scripts/build.py`
3. Para publicar con URLs limpias (`/servicios/empresas/contratos/`) usa `python3 scripts/build.py --clean-urls`. Sin el flag, los enlaces apuntan a `…/index.html` y el sitio funciona también abriendo los archivos localmente.

## Antes de publicar — reemplazar placeholders (en `scripts/content.py` → `FIRM`)

- `whatsapp` / `whatsapp_display`: número real (hoy `573000000000`)
- `email`, `instagram`, `linkedin`: confirmar
- `site_url`: dominio definitivo (canonical, Open Graph, schema.org y `sitemap.xml`)
- Revisar con el equipo los textos de Términos y Política de privacidad.

## Notas

- El formulario de contacto no requiere servidor: valida los datos y abre WhatsApp (o el correo) con el mensaje prellenado.
- Los testimonios tienen un espacio reservado (comentario HTML en `index.html`); solo agregar testimonios reales autorizados.
- Schema.org: `LegalService` en inicio/nosotros/contacto; `Service`, `FAQPage` y `BreadcrumbList` en cada servicio.
