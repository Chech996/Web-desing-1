#!/usr/bin/env python3
"""Generador estático del sitio de GC Legal.

Uso:
    python3 scripts/build.py                # enlaces portables (…/index.html)
    python3 scripts/build.py --clean-urls   # enlaces limpios (…/carpeta/)

Escribe cada página como <ruta>/index.html en la raíz del repositorio.
Sin dependencias: solo la biblioteca estándar de Python.
"""
import json
import os
import sys
from html import escape
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import (  # noqa: E402
    CATEGORIES, FIRM, HOW_DETAILED, HOW_STEPS, PROCESS_FAQS, SERVICE_BY_SLUG,
    SERVICES, VALUE_PROPS, VALUES, WHY,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_URLS = "--clean-urls" in sys.argv
ASSET_VERSION = "1"

# --------------------------------------------------------------------------
# Íconos SVG (trazo 1.8, estilo lineal)
# --------------------------------------------------------------------------
_P = {
    "building": '<path d="M6 22V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v18"/><path d="M3 22h18"/><path d="M10 7h1M13 7h1M10 11h1M13 11h1M10 15h1M13 15h1"/><path d="M10 22v-3h4v3"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8M8 17h5"/>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/><path d="M2 13h20"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/><path d="M12 15v2"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="18" rx="2"/><path d="M9 4V3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1"/><path d="M9 11h6M9 15h6M9 19h3"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "scale": '<path d="M12 3v18"/><path d="M7 21h10"/><path d="M5 7h14"/><path d="m5 7-3 7a3 3 0 0 0 6 0z"/><path d="m19 7-3 7a3 3 0 0 0 6 0z"/>',
    "tag": '<path d="M20.59 13.41 13.42 20.58a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><circle cx="7" cy="7" r="1.5"/>',
    "laptop": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M2 20h20"/>',
    "chat": '<path d="M21 12a8 8 0 0 1-11.6 7.14L4 21l1.86-5.4A8 8 0 1 1 21 12z"/><path d="M8.5 12h.01M12 12h.01M15.5 12h.01"/>',
    "doc": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="m9 15 2 2 4-4"/>',
    "check-circle": '<circle cx="12" cy="12" r="10"/><path d="m8 12 3 3 5-6"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    "zap": '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
    "arrow": '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
    "chev": '<path d="m6 9 6 6 6-6"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>',
    "moon": '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
    "eye": '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "help": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "repeat": '<path d="m17 1 4 4-4 4"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><path d="m7 23-4-4 4-4"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/>',
}
_FILLED = {
    "whatsapp": '<path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.16-.17.2-.35.22-.64.08-.3-.15-1.26-.46-2.39-1.48-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.07c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.7.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.41.25-.7.25-1.29.18-1.41-.08-.13-.28-.2-.57-.35z"/><path d="M12 0C5.37 0 0 5.37 0 12c0 2.13.55 4.12 1.52 5.86L.05 23.52a.5.5 0 0 0 .61.6l5.47-1.4A11.94 11.94 0 0 0 12 24c6.63 0 12-5.37 12-12S18.63 0 12 0zm0 21.82a9.78 9.78 0 0 1-5.18-1.48l-.37-.22-3.24.83.87-3.17-.25-.38A9.77 9.77 0 0 1 2.18 12 9.82 9.82 0 1 1 12 21.82z"/>',
    "instagram": '<path d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.72 3.72 0 0 1-1.38-.9 3.72 3.72 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23C2.17 15.58 2.16 15.2 2.16 12s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41C8.42 2.17 8.8 2.16 12 2.16M12 0C8.74 0 8.33.01 7.05.07 5.78.13 4.9.33 4.14.63c-.79.3-1.46.72-2.13 1.38A5.88 5.88 0 0 0 .63 4.14C.33 4.9.13 5.78.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.27.26 2.15.56 2.91.3.79.72 1.46 1.38 2.13.67.66 1.34 1.08 2.13 1.38.76.3 1.64.5 2.91.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.27-.06 2.15-.26 2.91-.56a5.88 5.88 0 0 0 2.13-1.38 5.88 5.88 0 0 0 1.38-2.13c.3-.76.5-1.64.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.27-.26-2.15-.56-2.91a5.88 5.88 0 0 0-1.38-2.13A5.88 5.88 0 0 0 19.86.63C19.1.33 18.22.13 16.95.07 15.67.01 15.26 0 12 0zm0 5.84a6.16 6.16 0 1 0 0 12.32 6.16 6.16 0 0 0 0-12.32zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.4-11.85a1.44 1.44 0 1 0 0 2.88 1.44 1.44 0 0 0 0-2.88z"/>',
    "linkedin": '<path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"/>',
}


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    if name in _FILLED:
        return f'<svg{c} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false">{_FILLED[name]}</svg>'
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{_P[name]}</svg>')


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def e(s):
    return escape(s, quote=True)


def wa_link(topic=None):
    """Enlace de WhatsApp con mensaje prellenado."""
    if topic:
        text = f"Hola, quiero consultar sobre {topic}"
    else:
        text = "Hola, quiero consultar sobre los servicios de GC Legal"
    return f"https://wa.me/{FIRM['whatsapp']}?text={quote(text, safe=',')}"


class Page:
    def __init__(self, path):
        self.path = path.strip("/")
        self.depth = len(self.path.split("/")) if self.path else 0

    def url(self, to):
        """Ruta relativa desde esta página hacia otra (to = ruta de carpeta, '' = inicio)."""
        to = to.strip("/")
        anchor = ""
        if "#" in to:
            to, anchor = to.split("#", 1)
            anchor = "#" + anchor
        prefix = "../" * self.depth
        if CLEAN_URLS:
            if not to:
                return (prefix or "./") + anchor
            return f"{prefix}{to}/{anchor}"
        if not to:
            return f"{prefix}index.html{anchor}"
        return f"{prefix}{to}/index.html{anchor}"

    def asset(self, p):
        return "../" * self.depth + "assets/" + p

    def abs(self):
        return FIRM["site_url"] + ("/" + self.path + "/" if self.path else "/")


def svc_path(s):
    return f"servicios/{s['cat']}/{s['slug']}"


def wa_btn(label, topic=None, cls="btn btn-primary", size=""):
    return (f'<a class="{cls}{" " + size if size else ""}" href="{e(wa_link(topic))}" target="_blank" rel="noopener">'
            f'{icon("whatsapp")}<span>{label}</span></a>')


# --------------------------------------------------------------------------
# Componentes globales
# --------------------------------------------------------------------------
NAV_ITEMS = [
    ("como-funciona", "Cómo funciona"),
    ("nosotros", "Nosotros"),
]


def logo(pg):
    return (f'<a class="logo" href="{pg.url("")}" aria-label="GC Legal — Inicio">'
            '<span class="logo-mark" aria-hidden="true">GC</span>'
            '<span class="logo-text"><span class="logo-name">GC Legal</span>'
            '<span class="logo-sub">Gómez &amp; Cadena Abogados</span></span></a>')


def header(pg, section):
    def cur(key):
        return ' aria-current="page"' if section == key else ""

    def dd_col(cat):
        items = "".join(
            f'<li><a class="dropdown-item" href="{pg.url(svc_path(s))}"{cur(s["slug"])}>'
            f'<span class="ico">{icon(s["icon"])}</span>'
            f'<span><strong>{e(s["name"])}</strong><span>{e(s["nav_desc"])}</span></span></a></li>'
            for s in SERVICES if s["cat"] == cat)
        return (f'<div><p class="dropdown-title"><a href="{pg.url("servicios/" + cat)}">{CATEGORIES[cat]["short"]}</a></p>'
                f'<ul class="dropdown-list">{items}</ul></div>')

    svc_active = " is-active" if section in ("servicios",) or section in SERVICE_BY_SLUG else ""
    nav = f'''
      <nav class="main-nav" aria-label="Principal">
        <ul class="nav-list">
          <li class="has-dropdown">
            <button class="nav-link{svc_active}" type="button" aria-expanded="false" aria-controls="dd-servicios">
              Servicios {icon("chev", "chev")}
            </button>
            <div class="dropdown" id="dd-servicios">
              <div class="dropdown-cols">{dd_col("empresas")}{dd_col("personas")}</div>
              <div class="dropdown-foot">
                <p>Tarifas fijas · Respuesta en menos de 24 horas</p>
                <a class="link-arrow" href="{pg.url("servicios")}">Ver todos los servicios {icon("arrow")}</a>
              </div>
            </div>
          </li>
          {"".join(f'<li><a class="nav-link" href="{pg.url(k)}"{cur(k)}>{v}</a></li>' for k, v in NAV_ITEMS)}
          <li><span class="nav-link is-disabled" aria-disabled="true" title="Muy pronto">Recursos <span class="soon">Pronto</span></span></li>
          <li><a class="nav-link" href="{pg.url("contacto")}"{cur("contacto")}>Contacto</a></li>
        </ul>
      </nav>'''

    def drawer_links(cat):
        return "".join(f'<li><a href="{pg.url(svc_path(s))}"{cur(s["slug"])}>{e(s["name"])}</a></li>'
                       for s in SERVICES if s["cat"] == cat)

    drawer = f'''
  <div class="drawer-overlay" data-drawer-close></div>
  <aside class="drawer" id="drawer" aria-label="Menú" aria-hidden="true" inert>
    <div class="drawer-head">
      {logo(pg)}
      <button class="icon-btn" type="button" data-drawer-close aria-label="Cerrar menú">{icon("x")}</button>
    </div>
    <div class="drawer-body">
      <div class="drawer-section">
        <p class="drawer-label">Para empresas</p>
        <ul class="drawer-links sub">{drawer_links("empresas")}</ul>
      </div>
      <div class="drawer-section">
        <p class="drawer-label">Para personas</p>
        <ul class="drawer-links sub">{drawer_links("personas")}</ul>
      </div>
      <div class="drawer-section">
        <ul class="drawer-links">
          <li><a href="{pg.url("servicios")}"{cur("servicios")}>Todos los servicios {icon("arrow", "chev")}</a></li>
          <li><a href="{pg.url("como-funciona")}"{cur("como-funciona")}>Cómo funciona</a></li>
          <li><a href="{pg.url("nosotros")}"{cur("nosotros")}>Nosotros</a></li>
          <li><span class="is-disabled">Recursos <span class="soon">Pronto</span></span></li>
          <li><a href="{pg.url("contacto")}"{cur("contacto")}>Contacto</a></li>
        </ul>
      </div>
    </div>
    <div class="drawer-foot">
      {wa_btn("Consulta gratuita", cls="btn btn-primary btn-block")}
      <button class="btn btn-outline btn-block" type="button" data-theme-toggle>{icon("moon")}<span>Cambiar tema</span></button>
    </div>
  </aside>'''

    return f'''
  <a class="skip-link" href="#contenido">Saltar al contenido</a>
  <header class="site-header">
    <div class="container header-inner">
      {logo(pg)}
      {nav}
      <div class="header-actions">
        <button class="icon-btn theme-toggle" type="button" data-theme-toggle aria-label="Cambiar tema">{icon("moon", "icon-moon")}{icon("sun", "icon-sun")}</button>
        {wa_btn("Consulta gratuita", cls="btn btn-primary btn-sm header-cta")}
        <button class="icon-btn menu-toggle" type="button" aria-label="Abrir menú" aria-expanded="false" aria-controls="drawer">{icon("menu")}</button>
      </div>
    </div>
  </header>
  {drawer}'''


FOOTER_SERVICE_LABELS = {
    "constitucion-sas": "Constitución de SAS",
    "contratos": "Contratos comerciales",
    "asesoria-empresarial": "Asesoría empresarial",
    "propiedad-intelectual": "Propiedad intelectual",
    "proteccion-datos": "Protección de datos",
    "gobierno-corporativo": "Gobierno corporativo",
    "derecho-familia": "Derecho de familia",
    "acciones-constitucionales": "Acciones constitucionales",
}


def footer(pg):
    svc = "".join(f'<li><a href="{pg.url(svc_path(s))}">{FOOTER_SERVICE_LABELS[s["slug"]]}</a></li>' for s in SERVICES)
    return f'''
  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          {logo(pg)}
          <p class="slogan">«{FIRM["slogan"]}»</p>
          <p>Servicios jurídicos con tarifas fijas para empresas y personas, desde Rionegro para toda Colombia.</p>
          <div class="social">
            <a href="{FIRM["instagram"]}" target="_blank" rel="noopener" aria-label="Instagram de GC Legal">{icon("instagram")}</a>
            <a href="{FIRM["linkedin"]}" target="_blank" rel="noopener" aria-label="LinkedIn de GC Legal">{icon("linkedin")}</a>
          </div>
        </div>
        <div class="footer-col">
          <h2>Servicios</h2>
          <ul class="footer-links">{svc}</ul>
        </div>
        <div class="footer-col">
          <h2>Firma</h2>
          <ul class="footer-links">
            <li><a href="{pg.url("nosotros")}">Nosotros</a></li>
            <li><a href="{pg.url("como-funciona")}">Cómo funciona</a></li>
            <li><a href="{pg.url("servicios")}">Todos los servicios</a></li>
            <li><a href="{pg.url("contacto")}">Contacto</a></li>
            <li><a href="{pg.url("terminos")}">Términos y condiciones</a></li>
            <li><a href="{pg.url("privacidad")}">Política de privacidad</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h2>Contacto</h2>
          <ul class="footer-links footer-contact">
            <li>{icon("whatsapp")}<a href="{e(wa_link())}" target="_blank" rel="noopener">{FIRM["whatsapp_display"]}</a></li>
            <li>{icon("mail")}<a href="mailto:{FIRM["email"]}">{FIRM["email"]}</a></li>
            <li>{icon("pin")}<span>{FIRM["city"]}, {FIRM["region"]}, {FIRM["country"]}</span></li>
            <li>{icon("clock")}<span>{FIRM["hours"]}</span></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© <span data-year>2026</span> GC Legal — Gómez &amp; Cadena Abogados. Todos los derechos reservados.</p>
        <p><em>Derecho a la solución.</em></p>
      </div>
    </div>
  </footer>
  <a class="wa-float" href="{e(wa_link())}" target="_blank" rel="noopener" aria-label="Escríbenos por WhatsApp">
    {icon("whatsapp")}<span class="wa-tip" aria-hidden="true">¿Hablamos por WhatsApp?</span>
  </a>'''


FAVICON = ("data:image/svg+xml,"
           + quote('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#1a2744"/>'
                   '<rect y="56" width="64" height="8" fill="#b8862b"/><text x="32" y="41" font-family="Georgia,serif" font-size="26" '
                   'font-weight="700" fill="#fff" text-anchor="middle">GC</text></svg>'))

THEME_BOOT = ("(function(){try{var t=localStorage.getItem('gc-theme');"
              "if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();")


def layout(pg, title, desc, body, section="", schema=None):
    ld = ""
    for block in (schema or []):
        ld += f'\n  <script type="application/ld+json">{json.dumps(block, ensure_ascii=False)}</script>'
    return f'''<!doctype html>
<html lang="es-CO">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <link rel="canonical" href="{pg.abs()}">
  <meta name="theme-color" content="#1a2744">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="es_CO">
  <meta property="og:site_name" content="GC Legal — Gómez &amp; Cadena Abogados">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{pg.abs()}">
  <link rel="icon" href="{FAVICON}">
  <script>{THEME_BOOT}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300..700&amp;family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&amp;display=swap">
  <link rel="stylesheet" href="{pg.asset("css/styles.css")}?v={ASSET_VERSION}">{ld}
</head>
<body>
{header(pg, section)}
  <main id="contenido">
{body}
  </main>
{footer(pg)}
  <script src="{pg.asset("js/main.js")}?v={ASSET_VERSION}" defer></script>
</body>
</html>
'''


# --------------------------------------------------------------------------
# Bloques reutilizables
# --------------------------------------------------------------------------
def cat_badge(cat):
    return f'<span class="badge badge-{cat}">{CATEGORIES[cat]["name"]}</span>'


def service_card(pg, s, wide=False, heading="h3"):
    extra = ""
    if wide:
        pts = "".join(f'<li>{icon("check")}<span>{e(p)}</span></li>' for p in s["card_points"])
        extra = (f'<ul class="card-list">{pts}</ul>'
                 f'<p class="card-meta">{icon("clock")}<span>{e(s.get("delivery_label", "Entrega"))}: {e(s["delivery"])}</span></p>')
    desc = s["long"] if wide else s["short"]
    return f'''
        <article class="card service-card{" is-wide" if wide else ""}">
          <div class="card-top"><span class="card-icon">{icon(s["icon"])}</span>{cat_badge(s["cat"])}</div>
          <{heading}><a href="{pg.url(svc_path(s))}">{e(s.get("full_name", s["name"]) if wide else s["name"])}</a></{heading}>
          <p>{e(desc)}</p>
          {extra}
          <span class="link-arrow" aria-hidden="true">Conoce más {icon("arrow")}</span>
        </article>'''


def cta_card(pg, title="¿No encuentras tu caso?", text="Cuéntanos tu situación y te decimos cómo podemos ayudarte. La consulta inicial no tiene costo."):
    return f'''
        <article class="card card-cta">
          <div>
            <span class="card-icon">{icon("help")}</span>
            <h3>{title}</h3>
            <p>{text}</p>
          </div>
          {wa_btn("Escríbenos", cls="btn btn-light")}
        </article>'''


def cta_band(pg, title="¿Necesitas asesoría jurídica?",
             text="Cuéntanos tu caso y recibe una cotización gratuita en menos de 24 horas.", topic=None,
             eyebrow="Consulta gratuita"):
    return f'''
    <section class="cta-band" aria-labelledby="cta-title">
      <div class="container">
        <div class="cta-box">
          <p class="eyebrow">{eyebrow}</p>
          <h2 id="cta-title">{title}</h2>
          <p>{text}</p>
          <div class="hero-ctas">{wa_btn("Escríbenos por WhatsApp", topic, cls="btn btn-light", size="btn-lg")}</div>
          <p class="cta-alt">o escríbenos a <a href="mailto:{FIRM["email"]}">{FIRM["email"]}</a></p>
        </div>
      </div>
    </section>'''


def faq_block(faqs, title="Preguntas frecuentes", lead="Resolvemos las dudas más comunes. Si la tuya no está aquí, escríbenos.", pg=None, topic=None):
    items = ""
    for i, (q, ans) in enumerate(faqs):
        paras = "".join(f"<p>{a}</p>" for a in ans)
        items += f'''
            <details{" open" if i == 0 else ""}>
              <summary>{e(q)}<span class="plus" aria-hidden="true"></span></summary>
              <div class="answer">{paras}</div>
            </details>'''
    return f'''
    <section class="section" id="preguntas" aria-labelledby="faq-title">
      <div class="container faq-wrap">
        <div class="section-head">
          <p class="eyebrow">FAQ</p>
          <h2 id="faq-title">{title}</h2>
          <p>{lead}</p>
          <div class="hero-ctas" style="margin-top:24px">{wa_btn("Hacer una pregunta", topic, cls="btn btn-outline")}</div>
        </div>
        <div class="faq">{items}
        </div>
      </div>
    </section>'''


def faq_schema(faqs):
    import re
    strip = lambda s: re.sub(r"<[^>]+>", "", s)
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": " ".join(strip(a) for a in ans)}}
                       for q, ans in faqs],
    }


def breadcrumb(pg, trail):
    """trail: lista de (ruta|None, etiqueta). El último es la página actual."""
    items = []
    for i, (path, label) in enumerate(trail):
        if i == len(trail) - 1:
            items.append(f'<li><span aria-current="page">{e(label)}</span></li>')
        else:
            items.append(f'<li><a href="{pg.url(path)}">{e(label)}</a></li>')
    return f'<nav class="breadcrumb" aria-label="Ruta de navegación"><ol>{"".join(items)}</ol></nav>'


def breadcrumb_schema(trail):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": label,
                             "item": FIRM["site_url"] + ("/" + path + "/" if path else "/")}
                            for i, (path, label) in enumerate(trail)],
    }


def org_schema():
    return {
        "@context": "https://schema.org",
        "@type": ["LegalService", "LocalBusiness"],
        "@id": FIRM["site_url"] + "/#firma",
        "name": "GC Legal — Gómez & Cadena Abogados",
        "alternateName": "GC Legal",
        "slogan": FIRM["slogan"],
        "description": "Firma colombiana de servicios jurídicos para empresas y personas con tarifas fijas, atención digital y presencial.",
        "url": FIRM["site_url"] + "/",
        "email": FIRM["email"],
        "telephone": "+" + FIRM["whatsapp"],
        "address": {"@type": "PostalAddress", "addressLocality": FIRM["city"],
                    "addressRegion": FIRM["region"], "addressCountry": "CO"},
        "areaServed": {"@type": "Country", "name": "Colombia"},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                       "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                                       "opens": "08:00", "closes": "18:00"}],
        "sameAs": [FIRM["instagram"], FIRM["linkedin"]],
        "knowsLanguage": "es",
    }


CHECK_TRUST = ["Tarifas fijas", "Respuesta en 24h", "Atención 100% digital o presencial"]


def trust_pills(items):
    return '<div class="pill-row">' + "".join(f'<span class="pill">{icon("check-circle")}{e(t)}</span>' for t in items) + "</div>"


# --------------------------------------------------------------------------
# Páginas
# --------------------------------------------------------------------------
def page_home():
    pg = Page("")
    cards = "".join(service_card(pg, s) for s in SERVICES) + cta_card(pg)
    values = "".join(f'''
          <div class="card feature feature-card">
            <span class="card-icon">{icon(i)}</span>
            <h3>{t}</h3>
            <p>{d}</p>
          </div>''' for i, t, d in VALUE_PROPS)
    steps = "".join(f'''
          <li class="step">
            <div class="step-num"><span class="card-icon">{icon(i)}</span></div>
            <h3>{t}</h3>
            <p>{d}</p>
          </li>''' for i, t, d in HOW_STEPS)
    why = "".join(f'''
          <div class="why-item">
            <span class="card-icon">{icon(i)}</span>
            <div><h3>{t}</h3><p>{d}</p></div>
          </div>''' for i, t, d in WHY)

    body = f'''
    <section class="hero" aria-labelledby="hero-title">
      <div class="container hero-grid">
        <div>
          <p class="eyebrow">GC Legal · Gómez &amp; Cadena Abogados</p>
          <h1 id="hero-title">Derecho a la <em>solución</em></h1>
          <p class="hero-sub">Servicios jurídicos con tarifas fijas, procesos claros y la asesoría de abogados expertos. Sin sorpresas, sin letra pequeña.</p>
          <div class="hero-ctas">
            {wa_btn("Consulta gratuita", size="btn-lg")}
            <a class="btn btn-outline btn-lg" href="#servicios">Conoce nuestros servicios</a>
          </div>
          <div class="hero-trust">{trust_pills(CHECK_TRUST)}</div>
        </div>
        <aside class="proposal-card" aria-label="Ejemplo de propuesta de servicio">
          <div class="proposal-top">{cat_badge("empresas")}<small>Propuesta · ejemplo</small></div>
          <h2>Constitución de SAS</h2>
          <ul class="proposal-rows">
            <li><span>Alcance</span><span>Definido por escrito</span></li>
            <li><span>Entrega</span><span>5–10 días hábiles</span></li>
            <li><span>Modalidad</span><span>Digital o presencial</span></li>
            <li><span>Honorarios</span><span>Tarifa fija</span></li>
          </ul>
          <ul class="proposal-checks">
            <li>{icon("check")}Estatutos personalizados</li>
            <li>{icon("check")}Registro en Cámara de Comercio</li>
            <li>{icon("check")}NIT y RUT de la sociedad</li>
          </ul>
          <p class="proposal-stamp">{icon("shield")}Conoces el valor total antes de empezar</p>
        </aside>
      </div>
    </section>

    <section class="section section-alt" aria-labelledby="valor-title">
      <div class="container">
        <div class="section-head center">
          <p class="eyebrow">Nuestra propuesta</p>
          <h2 id="valor-title">Asesoría jurídica como debería ser</h2>
          <p>Combinamos la experiencia de una firma con la claridad y agilidad que esperas de un servicio moderno.</p>
        </div>
        <div class="grid grid-3">{values}
        </div>
      </div>
    </section>

    <section class="section" id="servicios" aria-labelledby="servicios-title">
      <div class="container">
        <div class="section-head center">
          <p class="eyebrow">Servicios</p>
          <h2 id="servicios-title">Nuestros servicios</h2>
          <p>Soluciones jurídicas diseñadas para empresas y personas. Tarifas fijas, procesos claros.</p>
        </div>
        <div class="grid grid-cards">{cards}
        </div>
        <div class="section-foot"><a class="btn btn-outline btn-lg" href="{pg.url("servicios")}">Ver todos los servicios {icon("arrow")}</a></div>
      </div>
    </section>

    <section class="section section-alt" aria-labelledby="como-title">
      <div class="container">
        <div class="section-head center">
          <p class="eyebrow">Cómo funciona</p>
          <h2 id="como-title">¿Cómo funciona?</h2>
          <p>Tres pasos simples para resolver tu necesidad jurídica.</p>
        </div>
        <ol class="steps">{steps}
        </ol>
        <div class="section-foot"><a class="link-arrow" href="{pg.url("como-funciona")}">Conoce cómo trabajamos {icon("arrow")}</a></div>
      </div>
    </section>

    <section class="section" aria-labelledby="why-title">
      <div class="container">
        <div class="section-head center">
          <p class="eyebrow">¿Por qué GC Legal?</p>
          <h2 id="why-title">¿Por qué elegirnos?</h2>
        </div>
        <div class="why-grid">{why}
        </div>
      </div>
    </section>

    <!--
      TESTIMONIOS: espacio reservado para testimonios reales de clientes
      (con su autorización). No publicar testimonios inventados.
    -->
{cta_band(pg)}'''
    return pg, layout(pg, "GC Legal — Gómez & Cadena Abogados | Derecho a la solución",
                      "Firma de abogados en Rionegro, Antioquia, con tarifas fijas para empresas y personas: constitución de SAS, contratos, marcas, protección de datos, familia y tutelas. Atención digital en toda Colombia.",
                      body, "inicio", [org_schema()])


def page_service(s):
    path = svc_path(s)
    pg = Page(path)
    cat = CATEGORIES[s["cat"]]
    trail = [("", "Inicio"), ("servicios", "Servicios"), ("servicios/" + s["cat"], cat["name"]), (path, s["name"])]

    pills_items = [p for p in [
        "Tarifa fija" if s["cat"] == "empresas" or s.get("badge2") == "Tarifa fija" else None,
        (f"Entrega en {s['delivery']}" if "delivery_label" not in s else s["delivery"]),
        s.get("badge2") if s.get("badge2") != "Tarifa fija" else None,
    ] if p]

    what = "".join(f"<p>{p}</p>" for p in s["what"])
    extra = ""
    if s.get("extra"):
        chips = "".join(f'<span class="chip">{e(c)}</span>' for c in s["extra"]["chips"])
        extra = f'<h3 style="margin-top:36px">{e(s["extra"]["title"])}</h3><div class="chips">{chips}</div>'

    includes = "".join(
        f'<li><span class="check">{icon("check")}</span><span>{e(t)}<small>{e(d)}</small></span></li>'
        for t, d in s["includes"])
    steps = "".join(f'''
          <li class="step">
            <div class="step-num"></div>
            <h3>{e(t)}</h3>
            <p>{e(d)}</p>
          </li>''' for t, d in s["steps"])

    plans = ""
    if s.get("plans"):
        cards = ""
        for p in s["plans"]:
            pts = "".join(f'<li><span class="check">{icon("check")}</span><span>{e(x)}</span></li>' for x in p["points"])
            badge = '<span class="badge badge-empresas">Más elegido</span>' if p.get("featured") else '<span class="badge badge-personas">Plan</span>'
            cards += f'''
          <article class="card plan{" is-featured" if p.get("featured") else ""}">
            {badge}
            <h3>{e(p["name"])}</h3>
            <p class="plan-for">{e(p["for"])}</p>
            <p class="plan-price"><strong>Tarifa mensual fija</strong>Cotizada según el tamaño de tu empresa</p>
            <ul class="checklist plain">{pts}</ul>
            <div class="plan-actions">{wa_btn("Cotizar plan " + p["name"], "el plan " + p["name"] + " de asesoría empresarial", cls="btn " + ("btn-primary" if p.get("featured") else "btn-outline") + " btn-block")}</div>
          </article>'''
        plans = f'''
    <section class="section section-alt" aria-labelledby="planes-title">
      <div class="container">
        <div class="section-head center">
          <p class="eyebrow">Planes</p>
          <h2 id="planes-title">Un plan para cada etapa de tu empresa</h2>
          <p>Todos los planes tienen tarifa mensual fija. Te ayudamos a elegir el adecuado en el diagnóstico inicial, sin costo.</p>
        </div>
        <div class="plans">{cards}
        </div>
      </div>
    </section>'''

    related = [SERVICE_BY_SLUG[r] for r in s["related"]]
    rel_cards = "".join(service_card(pg, r) for r in related)
    if len(related) < 3:
        rel_cards += cta_card(pg)
    alt_a = "section-alt" if not plans else ""
    alt_b = "" if not plans else "section-alt"

    body = f'''
    <section class="page-hero">
      <div class="container">
        {breadcrumb(pg, trail)}
        <div class="service-hero-grid">
          <div>
            {cat_badge(s["cat"])}
            <h1>{e(s["h1"])} <span class="h1-sub">— {e(s["h1_sub"])}</span></h1>
            <p class="lead">{e(s["intro"])}</p>
            {trust_pills(pills_items)}
            <div class="hero-ctas">
              {wa_btn("Solicitar cotización", s["wa"], size="btn-lg")}
              <a class="btn btn-outline btn-lg" href="#incluye">Qué incluye</a>
            </div>
            <p class="trust-line">{icon("shield")}Atención de un abogado experto. Sin costos ocultos.</p>
          </div>
          <aside class="summary-card" aria-labelledby="resumen-title">
            <h2 id="resumen-title">En resumen</h2>
            <ul class="summary-list">
              <li>{icon("tag")}<div><strong>Honorarios</strong><span>Tarifa fija, cotizada antes de empezar</span></div></li>
              <li>{icon("clock")}<div><strong>{e(s.get("delivery_label", "Entrega estimada"))}</strong><span>{e(s["delivery"])}</span></div></li>
              <li>{icon("laptop")}<div><strong>Modalidad</strong><span>100 % digital o presencial en Rionegro</span></div></li>
              <li>{icon("target")}<div><strong>Ideal para</strong><span>{e(s["ideal"])}</span></div></li>
            </ul>
            {wa_btn("Cotizar por WhatsApp", s["wa"], cls="btn btn-primary btn-block")}
            <p class="fine">Respuesta en menos de 24 horas hábiles</p>
          </aside>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="que-es-title">
      <div class="container split split-wide">
        <div class="prose">
          <p class="eyebrow">El servicio</p>
          <h2 id="que-es-title" style="margin-top:14px">{e(s["what_title"])}</h2>
          {what}
          {extra}
        </div>
        <aside class="aside-box">
          <span class="card-icon">{icon(s["icon"])}</span>
          <h3 style="margin-top:18px">¿Tienes dudas sobre tu caso?</h3>
          <p>Escríbenos y un abogado te orienta sin costo. Te decimos con franqueza si este es el servicio que necesitas.</p>
          <div style="margin-top:20px;display:grid;gap:10px">
            {wa_btn("Hablar con un abogado", s["wa"], cls="btn btn-primary btn-block")}
            <a class="btn btn-outline btn-block" href="{pg.url("contacto")}?servicio={s["slug"]}">Usar el formulario</a>
          </div>
        </aside>
      </div>
    </section>

    <section class="section {alt_a}" id="incluye" aria-labelledby="incluye-title">
      <div class="container">
        <div class="section-head">
          <p class="eyebrow">Entregables</p>
          <h2 id="incluye-title">¿Qué incluye?</h2>
          <p>Todo lo que recibes, por escrito y sin sorpresas.</p>
        </div>
        <ul class="checklist cols">{includes}</ul>
        <p class="note">{icon("info")}<span>{e(s["includes_note"])}</span></p>
      </div>
    </section>
{plans}
    <section class="section {alt_b}" aria-labelledby="proceso-title">
      <div class="container">
        <div class="section-head">
          <p class="eyebrow">Proceso</p>
          <h2 id="proceso-title">¿Cómo funciona?</h2>
          <p>Un proceso claro, con un abogado responsable de principio a fin.</p>
        </div>
        <ol class="steps steps-4">{steps}
        </ol>
        <div class="callout">{icon("clock")}<p><strong>Tiempo estimado:</strong> {e(s["timing"])}</p></div>
      </div>
    </section>
{faq_block(s["faqs"], lead=f"Lo que más nos preguntan sobre {s.get('full_name', s['name']).lower() if s['slug'] != 'propiedad-intelectual' else 'el registro de marcas'} en Colombia.", pg=pg, topic=s["wa"])}
    <section class="section section-alt" aria-labelledby="rel-title">
      <div class="container">
        <div class="section-head">
          <p class="eyebrow">También te puede interesar</p>
          <h2 id="rel-title">Servicios relacionados</h2>
        </div>
        <div class="grid grid-cards">{rel_cards}
        </div>
      </div>
    </section>
{cta_band(pg, s["cta_title"], s["cta_text"], s["wa"], eyebrow="Cotización gratuita")}'''

    schema = [
        {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": s.get("full_name", s["name"]),
            "serviceType": s.get("full_name", s["name"]),
            "description": s["meta_desc"],
            "url": pg.abs(),
            "areaServed": {"@type": "Country", "name": "Colombia"},
            "provider": {"@id": FIRM["site_url"] + "/#firma", "@type": "LegalService", "name": "GC Legal — Gómez & Cadena Abogados"},
        },
        faq_schema(s["faqs"]),
        breadcrumb_schema(trail),
    ]
    return pg, layout(pg, s["meta_title"], s["meta_desc"], body, s["slug"], schema)


def page_hub(cat_key):
    pg = Page("servicios/" + cat_key)
    cat = CATEGORIES[cat_key]
    trail = [("", "Inicio"), ("servicios", "Servicios"), ("servicios/" + cat_key, cat["name"])]
    items = [s for s in SERVICES if s["cat"] == cat_key]
    cards = "".join(service_card(pg, s, wide=True, heading="h2") for s in items)
    other = "personas" if cat_key == "empresas" else "empresas"
    if len(items) % 3 or len(items) < 3:
        cards += cta_card(pg)
    intro = "".join(f"<p>{p}</p>" for p in cat["intro"])
    body = f'''
    <section class="page-hero">
      <div class="container">
        {breadcrumb(pg, trail)}
        <p class="eyebrow" style="margin-top:28px">{cat["short"]}</p>
        <h1>{e(cat["title"])}</h1>
        <p class="lead">{e(cat["lead"])}</p>
        {trust_pills(CHECK_TRUST)}
        <div class="hero-ctas">{wa_btn("Consulta gratuita", "servicios para " + cat_key, size="btn-lg")}</div>
      </div>
    </section>

    <section class="section" aria-labelledby="hub-list">
      <div class="container">
        <div class="split" style="margin-bottom:clamp(40px,5vw,64px)">
          <div><p class="eyebrow">Servicios</p><h2 id="hub-list" style="margin-top:14px">{"Todo lo que tu empresa necesita, en un solo lugar" if cat_key == "empresas" else "Te acompañamos cuando más lo necesitas"}</h2></div>
          <div class="prose" style="color:var(--fg-muted)">{intro}</div>
        </div>
        <div class="grid grid-cards">{cards}
        </div>
        <div class="callout">{icon("info")}<p>¿Buscas servicios {CATEGORIES[other]["short"].lower()}? <a class="text-link" href="{pg.url("servicios/" + other)}">Ver servicios {CATEGORIES[other]["short"].lower()}</a> o consulta el <a class="text-link" href="{pg.url("servicios")}">directorio completo</a>.</p></div>
      </div>
    </section>
{cta_band(pg, "¿No sabes por dónde empezar?", "Cuéntanos tu situación y te recomendamos el servicio adecuado. Cotización gratuita en menos de 24 horas.")}'''
    schema = [breadcrumb_schema(trail), {
        "@context": "https://schema.org", "@type": "ItemList", "name": cat["title"],
        "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": s.get("full_name", s["name"]),
                             "url": FIRM["site_url"] + "/" + svc_path(s) + "/"} for i, s in enumerate(items)]}]
    return pg, layout(pg, cat["meta_title"], cat["meta_desc"], body, "servicios", schema)


def page_directory():
    pg = Page("servicios")
    trail = [("", "Inicio"), ("servicios", "Servicios")]
    groups = ""
    for key in ("empresas", "personas"):
        cat = CATEGORIES[key]
        items = [s for s in SERVICES if s["cat"] == key]
        cards = "".join(service_card(pg, s, wide=True) for s in items)
        if len(items) % 3:
            cards += cta_card(pg)
        groups += f'''
        <div class="directory-group" id="grupo-{key}" data-group="{key}" role="tabpanel" aria-labelledby="tab-{key}">
          <div class="group-head">
            <div><p class="eyebrow">{len(items)} servicios</p><h2>{cat["short"]}</h2></div>
            <p>{e(cat["lead"])}</p>
          </div>
          <div class="grid grid-cards">{cards}
          </div>
          <div class="section-foot" style="justify-content:flex-start;margin-top:28px"><a class="link-arrow" href="{pg.url("servicios/" + key)}">Ver servicios {cat["short"].lower()} {icon("arrow")}</a></div>
        </div>'''
    body = f'''
    <section class="page-hero">
      <div class="container">
        {breadcrumb(pg, trail)}
        <p class="eyebrow" style="margin-top:28px">Servicios</p>
        <h1>Todos nuestros servicios</h1>
        <p class="lead">Soluciones jurídicas con tarifas fijas para empresas y personas.</p>
        <div class="tabs" role="tablist" aria-label="Filtrar servicios" data-filter-tabs>
          <button class="tab" role="tab" id="tab-todos" data-filter="todos" aria-selected="true">Todos</button>
          <button class="tab" role="tab" id="tab-empresas" data-filter="empresas" aria-selected="false" tabindex="-1" aria-controls="grupo-empresas">Empresas</button>
          <button class="tab" role="tab" id="tab-personas" data-filter="personas" aria-selected="false" tabindex="-1" aria-controls="grupo-personas">Personas</button>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">{groups}
      </div>
    </section>
{cta_band(pg, "¿No encuentras lo que buscas?", "Atendemos muchos otros asuntos jurídicos. Cuéntanos tu caso y te decimos cómo podemos ayudarte.")}'''
    return pg, layout(pg, "Todos los servicios jurídicos | GC Legal",
                      "Directorio de servicios jurídicos de GC Legal para empresas y personas: SAS, contratos, marcas, protección de datos, gobierno corporativo, familia y tutelas. Tarifas fijas.",
                      body, "servicios", [breadcrumb_schema(trail)])


def page_how():
    pg = Page("como-funciona")
    trail = [("", "Inicio"), ("como-funciona", "Cómo funciona")]
    steps = ""
    for st in HOW_DETAILED:
        pts = "".join(f'<li>{icon("check")}<span><strong>{e(a)}:</strong> {e(b)}</span></li>' for a, b in st["points"])
        steps += f'''
          <li class="step">
            <div class="step-num"><span class="card-icon">{icon(st["icon"])}</span></div>
            <h3>{e(st["title"])}</h3>
            <p>{e(st["text"])}</p>
            <ul class="step-list">{pts}</ul>
          </li>'''
    rows = [
        ("Cuánto pagas", "Lo sabes hasta que llega la factura.", "Lo sabes antes de empezar, por escrito."),
        ("Comunicación", "Cada llamada o correo puede sumar horas.", "Consultas incluidas dentro del alcance."),
        ("Incentivos", "Más horas significan más ingresos para el abogado.", "La eficiencia nos beneficia a ambos."),
        ("Cambios de alcance", "Se cobran sin aviso previo.", "Se cotizan y aprueban antes de hacerlos."),
        ("Presupuesto", "Difícil de planear.", "Predecible, ideal para tu flujo de caja."),
    ]
    trs = "".join(f'<tr><td>{a}</td><td data-label="Por horas"><span>{b}</span></td><td class="is-us" data-label="Tarifa fija GC Legal">{c}</td></tr>' for a, b, c in rows)
    factors = [
        ("target", "Alcance", "Qué documentos, trámites y gestiones incluye el servicio."),
        ("layers", "Complejidad", "Número de partes, socios, clases o particularidades del caso."),
        ("clock", "Urgencia", "Si necesitas una entrega prioritaria, te lo decimos desde el principio."),
    ]
    _P.setdefault("layers", '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>')
    fac = "".join(f'<div class="card feature feature-card"><span class="card-icon">{icon(i)}</span><h3>{t}</h3><p>{d}</p></div>' for i, t, d in factors)
    asesoria = SERVICE_BY_SLUG["asesoria-empresarial"]
    plans = "".join(f'<li><span class="check">{icon("check")}</span><span>{e(p["name"])}<small>{e(p["for"])}</small></span></li>' for p in asesoria["plans"])

    body = f'''
    <section class="page-hero">
      <div class="container">
        {breadcrumb(pg, trail)}
        <p class="eyebrow" style="margin-top:28px">Cómo funciona</p>
        <h1>Así <em>trabajamos</em></h1>
        <p class="lead">Un proceso sencillo y transparente, pensado para que sepas en todo momento qué estamos haciendo, cuánto cuesta y cuándo lo recibes.</p>
        {trust_pills(CHECK_TRUST)}
      </div>
    </section>

    <section class="section" aria-labelledby="pasos-title">
      <div class="container">
        <div class="section-head">
          <p class="eyebrow">El proceso</p>
          <h2 id="pasos-title">Tres pasos, cero sorpresas</h2>
          <p>Desde el primer mensaje hasta la entrega final, siempre sabes en qué punto está tu caso.</p>
        </div>
        <ol class="steps">{steps}
        </ol>
      </div>
    </section>

    <section class="section section-alt" id="tarifas" aria-labelledby="tarifas-title">
      <div class="container">
        <div class="split">
          <div class="prose">
            <p class="eyebrow">Tarifas fijas</p>
            <h2 id="tarifas-title" style="margin-top:14px">Tarifas fijas, sin sorpresas</h2>
            <p>La facturación por horas pone todo el riesgo del lado del cliente: no sabes cuánto vas a pagar hasta que el trabajo termina, y cada llamada o correo puede aumentar la cuenta.</p>
            <p>Nosotros trabajamos al revés. Antes de empezar, te enviamos una propuesta con el <strong>alcance exacto</strong>, el <strong>plazo</strong> y una <strong>tarifa fija</strong>. Ese es el valor que pagas, aunque el trabajo nos tome más tiempo del previsto.</p>
            <p>No publicamos precios en la web porque cada caso es distinto; preferimos darte un valor exacto para tu situación en menos de 24 horas.</p>
          </div>
          <div class="table-wrap">
            <table class="compare">
              <caption class="sr-only">Comparación entre facturación por horas y tarifa fija</caption>
              <thead><tr><th scope="col">Aspecto</th><th scope="col">Por horas</th><th scope="col" class="is-us">Tarifa fija GC Legal</th></tr></thead>
              <tbody>{trs}</tbody>
            </table>
          </div>
        </div>
        <h3 style="margin-top:clamp(48px,6vw,72px);margin-bottom:24px">¿Cómo calculamos tu tarifa?</h3>
        <div class="grid grid-3">{fac}</div>
        <p class="note">{icon("info")}<span>Los costos de terceros —tasas de la SIC, derechos de la Cámara de Comercio, impuestos de registro o gastos notariales— se informan por separado en la propuesta, con su valor exacto o estimado.</span></p>
      </div>
    </section>

    <section class="section" id="asesoria-recurrente" aria-labelledby="rec-title">
      <div class="container split split-wide">
        <div class="prose">
          <p class="eyebrow">Para empresas</p>
          <h2 id="rec-title" style="margin-top:14px">Asesoría empresarial recurrente</h2>
          <p>Algunas empresas necesitan un abogado de forma permanente, pero no tienen el volumen para contratar uno de planta. Para ellas creamos los <strong>planes de asesoría mensual</strong>: una tarifa fija al mes que incluye consultas, revisión de documentos y alertas de cumplimiento.</p>
          <p>Es como tener un área legal propia sin salarios, prestaciones ni seguridad social. Y como conocemos tu empresa, cada consulta se resuelve más rápido.</p>
          <div class="hero-ctas" style="margin-top:28px">
            <a class="btn btn-primary" href="{pg.url(svc_path(asesoria))}">Ver planes de asesoría {icon("arrow")}</a>
          </div>
        </div>
        <aside class="aside-box">
          <span class="card-icon">{icon("repeat")}</span>
          <h3 style="margin-top:18px">Tres niveles, una tarifa mensual fija</h3>
          <ul class="checklist plain" style="margin-top:18px">{plans}</ul>
        </aside>
      </div>
    </section>
{faq_block(PROCESS_FAQS, title="Preguntas sobre el proceso", lead="Todo lo que debes saber antes de trabajar con nosotros.", pg=pg).replace('class="section"', 'class="section section-alt"', 1)}
{cta_band(pg, "¿Empezamos?", "Escríbenos por WhatsApp, cuéntanos tu caso y recibe tu propuesta con tarifa fija en menos de 24 horas.")}'''
    return pg, layout(pg, "Cómo funciona: proceso y tarifas fijas | GC Legal",
                      "Así trabajamos en GC Legal: consulta gratuita, propuesta con alcance, plazo y tarifa fija, y entrega de tu solución. Conoce nuestros planes de asesoría empresarial mensual.",
                      body, "como-funciona", [breadcrumb_schema(trail), faq_schema(PROCESS_FAQS)])


def page_about():
    pg = Page("nosotros")
    trail = [("", "Inicio"), ("nosotros", "Nosotros")]
    values = "".join(f'<div class="card value"><span class="card-icon">{icon(i)}</span><h3>{t}</h3><p>{d}</p></div>' for i, t, d in VALUES)
    areas = "".join(f'<li><a href="{pg.url(svc_path(s))}"><span class="card-icon">{icon(s["icon"])}</span>{e(s.get("full_name", s["name"]))}</a></li>' for s in SERVICES)
    diffs = [
        ("Precio antes que trabajo", "Recibes una propuesta con tarifa fija antes de comprometerte. Nunca una cuenta que no aprobaste."),
        ("Lenguaje claro", "Te explicamos tu situación en palabras sencillas para que decidas con información."),
        ("Servicios empaquetados", "Alcances definidos y entregables concretos, como un producto: sabes exactamente qué recibes."),
        ("Abogados que responden", "Respuesta en menos de 24 horas hábiles por el canal que prefieras."),
    ]
    diff_html = "".join(f'<li><span class="check">{icon("check")}</span><span>{t}<small>{d}</small></span></li>' for t, d in diffs)
    body = f'''
    <section class="page-hero">
      <div class="container">
        {breadcrumb(pg, trail)}
        <p class="eyebrow" style="margin-top:28px">Nosotros</p>
        <h1>Sobre GC Legal</h1>
        <p class="lead">Somos Gómez &amp; Cadena Abogados, una firma colombiana de servicios jurídicos con vocación empresarial, con sede en Rionegro, Antioquia, y clientes en todo el país.</p>
      </div>
    </section>

    <section class="section" aria-labelledby="historia-title">
      <div class="container split">
        <div>
          <p class="eyebrow">Nuestra historia</p>
          <h2 id="historia-title" style="margin-top:14px">Creemos que el derecho debe resolver, no complicar</h2>
        </div>
        <div class="prose" style="color:var(--fg-muted);font-size:1.06rem">
          <p>GC Legal nació de una convicción sencilla: muchas personas y empresas en Colombia evitan buscar un abogado porque no saben cuánto les va a costar, cuánto se va a demorar o si van a entender lo que les dicen. Esa incertidumbre termina saliendo cara.</p>
          <p>Nuestra misión es hacer que la asesoría jurídica de calidad sea <strong>clara, accesible y predecible</strong>. Por eso trabajamos con tarifas fijas, procesos definidos y herramientas digitales, sin renunciar al rigor y al criterio que exige cada caso. Así entendemos nuestro lema: <em>Derecho a la solución</em>.</p>
        </div>
      </div>
      <div class="container">
        <div class="stat-row">
          <div class="stat"><strong>Tarifa fija</strong><span>En todos nuestros servicios empaquetados</span></div>
          <div class="stat"><strong>&lt; 24 horas</strong><span>Tiempo de respuesta a tu consulta</span></div>
          <div class="stat"><strong>Toda Colombia</strong><span>Atención digital y presencial en Rionegro</span></div>
        </div>
      </div>
    </section>

    <section class="section section-alt" aria-labelledby="dif-title">
      <div class="container split split-wide">
        <div class="prose">
          <p class="eyebrow">Por qué somos diferentes</p>
          <h2 id="dif-title" style="margin-top:14px">Una firma pensada desde la experiencia del cliente</h2>
          <p>La forma tradicional de contratar un abogado —reuniones largas, cobros por hora y respuestas que tardan semanas— no responde a cómo funcionan hoy las empresas ni las personas.</p>
          <p>Tomamos lo mejor de las firmas modernas de servicios jurídicos y lo adaptamos al derecho colombiano y a nuestra región: servicios con alcance claro, comunicación directa por WhatsApp y la posibilidad de reunirte con nosotros en persona cuando lo necesites.</p>
        </div>
        <ul class="checklist">{diff_html}</ul>
      </div>
    </section>

    <section class="section" aria-labelledby="valores-title">
      <div class="container">
        <div class="section-head center">
          <p class="eyebrow">Valores</p>
          <h2 id="valores-title">Lo que guía nuestro trabajo</h2>
        </div>
        <div class="values">{values}</div>
      </div>
    </section>

    <section class="section section-alt" aria-labelledby="areas-title">
      <div class="container">
        <div class="section-head">
          <p class="eyebrow">Áreas de práctica</p>
          <h2 id="areas-title">En qué te podemos ayudar</h2>
          <p>Servicios jurídicos para empresas y personas, con tarifa fija y entregables claros.</p>
        </div>
        <ul class="areas">{areas}</ul>
      </div>
    </section>
{cta_band(pg, "Conversemos sobre tu caso", "La primera consulta es gratuita. Escríbenos y recibe una propuesta clara en menos de 24 horas.")}'''
    return pg, layout(pg, "Sobre GC Legal — Gómez & Cadena Abogados | Rionegro, Antioquia",
                      "Conoce GC Legal: firma colombiana de servicios jurídicos con vocación empresarial, tarifas fijas y atención digital y presencial desde Rionegro, Antioquia.",
                      body, "nosotros", [breadcrumb_schema(trail), org_schema()])


def page_contact():
    pg = Page("contacto")
    trail = [("", "Inicio"), ("contacto", "Contacto")]
    opts = '<option value="">Selecciona una opción</option>'
    for key in ("empresas", "personas"):
        opts += f'<optgroup label="{CATEGORIES[key]["short"]}">'
        opts += "".join(f'<option value="{s["slug"]}">{e(s.get("full_name", s["name"]))}</option>' for s in SERVICES if s["cat"] == key)
        opts += "</optgroup>"
    opts += '<option value="otro">Otro / no estoy seguro</option>'
    body = f'''
    <section class="page-hero">
      <div class="container">
        {breadcrumb(pg, trail)}
        <p class="eyebrow" style="margin-top:28px">Contacto</p>
        <h1>Contáctanos</h1>
        <p class="lead">Cuéntanos tu caso y te respondemos en menos de 24 horas hábiles con una orientación inicial y una cotización clara. La consulta no tiene costo.</p>
      </div>
    </section>

    <section class="section">
      <div class="container contact-grid">
        <div class="card form-card">
          <h2>Envíanos tu consulta</h2>
          <p>Completa el formulario y lo enviaremos a nuestro WhatsApp con tu mensaje listo. Si prefieres, también puedes enviarlo por correo.</p>
          <form id="contact-form" novalidate data-wa="{FIRM["whatsapp"]}" data-email="{FIRM["email"]}">
            <div class="form-grid">
              <div class="field">
                <label for="nombre">Nombre completo</label>
                <input id="nombre" name="nombre" type="text" autocomplete="name" required aria-describedby="err-nombre">
                <p class="error" id="err-nombre" aria-live="polite"></p>
              </div>
              <div class="field">
                <label for="email">Correo electrónico</label>
                <input id="email" name="email" type="email" autocomplete="email" required aria-describedby="err-email">
                <p class="error" id="err-email" aria-live="polite"></p>
              </div>
              <div class="field">
                <label for="telefono">Teléfono / WhatsApp <span class="opt">(opcional)</span></label>
                <input id="telefono" name="telefono" type="tel" autocomplete="tel" inputmode="tel" aria-describedby="err-telefono">
                <p class="error" id="err-telefono" aria-live="polite"></p>
              </div>
              <div class="field">
                <label for="servicio">Tipo de servicio</label>
                <select id="servicio" name="servicio" required aria-describedby="err-servicio">{opts}</select>
                <p class="error" id="err-servicio" aria-live="polite"></p>
              </div>
              <div class="field full">
                <label for="mensaje">Cuéntanos tu caso</label>
                <textarea id="mensaje" name="mensaje" required placeholder="Describe brevemente tu situación y qué necesitas." aria-describedby="err-mensaje"></textarea>
                <p class="error" id="err-mensaje" aria-live="polite"></p>
              </div>
              <div class="full">
                <label class="consent">
                  <input type="checkbox" name="consentimiento" required aria-describedby="err-consent">
                  <span>Autorizo a GC Legal a tratar mis datos personales para atender mi consulta, conforme a la <a href="{pg.url("privacidad")}">Política de privacidad</a> y la Ley 1581 de 2012.
                  <span class="error" id="err-consent" aria-live="polite" style="display:block;color:var(--danger)"></span></span>
                </label>
              </div>
              <div class="full form-actions">
                <button class="btn btn-primary btn-lg" type="submit">{icon("whatsapp")}<span>Enviar por WhatsApp</span></button>
                <button class="btn btn-outline btn-lg" type="button" id="send-email">{icon("mail")}<span>Enviar por correo</span></button>
              </div>
            </div>
            <div class="form-status" id="form-status" role="status" aria-live="polite">{icon("check-circle")}<span></span></div>
          </form>
        </div>

        <div class="info-stack">
          <div class="card info-item info-wa">
            <span class="card-icon">{icon("whatsapp")}</span>
            <div>
              <h3>WhatsApp</h3>
              <p>{FIRM["whatsapp_display"]}</p>
              <small>El canal más rápido para cotizar.</small>
              {wa_btn("Abrir WhatsApp", cls="btn btn-light btn-sm")}
            </div>
          </div>
          <div class="card info-item">
            <span class="card-icon">{icon("mail")}</span>
            <div><h3>Correo</h3><a class="val" href="mailto:{FIRM["email"]}">{FIRM["email"]}</a><small>Para enviar documentos o consultas detalladas.</small></div>
          </div>
          <div class="card info-item">
            <span class="card-icon">{icon("clock")}</span>
            <div><h3>Horario de atención</h3><p>{FIRM["hours"]}</p><small>Mensajes fuera de horario se responden el siguiente día hábil.</small></div>
          </div>
          <div class="card info-item">
            <span class="card-icon">{icon("pin")}</span>
            <div><h3>Ubicación</h3><p>{FIRM["city"]}, {FIRM["region"]}</p><small>Atención presencial con cita previa. Atención digital en toda Colombia.</small></div>
          </div>
        </div>
      </div>
    </section>
{cta_band(pg, "También puedes escribirnos directamente por WhatsApp", "Es la forma más rápida de recibir tu cotización. Te respondemos en menos de 24 horas hábiles.", eyebrow="Respuesta rápida")}'''
    return pg, layout(pg, "Contacto — Consulta gratuita | GC Legal",
                      "Contacta a GC Legal por WhatsApp, correo o formulario. Consulta gratuita y cotización con tarifa fija en menos de 24 horas. Rionegro, Antioquia, y toda Colombia.",
                      body, "contacto", [breadcrumb_schema(trail), org_schema()])


def page_legal(kind):
    pg = Page(kind)
    if kind == "terminos":
        title, h1 = "Términos y condiciones | GC Legal", "Términos y condiciones"
        desc = "Términos y condiciones de uso del sitio web de GC Legal — Gómez & Cadena Abogados."
        content = f'''
          <h2>1. Información general</h2>
          <p>Este sitio web es operado por <strong>GC Legal — Gómez &amp; Cadena Abogados</strong>, con domicilio en {FIRM["city"]}, {FIRM["region"]}, Colombia. Al navegar en él aceptas estos términos.</p>
          <h2>2. Carácter informativo del contenido</h2>
          <p>La información publicada tiene fines exclusivamente informativos y generales. <strong>No constituye asesoría jurídica</strong> ni crea una relación abogado-cliente. Cada caso tiene particularidades que deben analizarse de forma individual.</p>
          <p>Procuramos mantener el contenido actualizado, pero las normas y la jurisprudencia cambian. Antes de tomar decisiones, consulta tu situación con un abogado.</p>
          <h2>3. Contratación de servicios</h2>
          <p>La relación profesional inicia únicamente cuando aceptas por escrito una propuesta de servicios. Esa propuesta define el alcance, el plazo, la tarifa fija, la forma de pago y las exclusiones del servicio.</p>
          <ul>
            <li>La consulta inicial y la cotización no tienen costo ni generan obligación.</li>
            <li>Los costos de terceros (tasas, derechos de registro, impuestos, gastos notariales) no hacen parte de los honorarios, salvo que la propuesta diga lo contrario.</li>
            <li>Cualquier trabajo adicional al alcance pactado se cotiza y aprueba antes de realizarse.</li>
          </ul>
          <h2>4. Tiempos estimados</h2>
          <p>Los plazos indicados en el sitio son estimados y dependen de que recibamos la información completa, y de los tiempos de entidades como la Cámara de Comercio, la DIAN, la SIC, notarías y despachos judiciales, que no controlamos.</p>
          <h2>5. Propiedad intelectual</h2>
          <p>Los textos, diseño, logotipos y demás elementos de este sitio son propiedad de GC Legal o se usan con autorización. No pueden reproducirse sin permiso previo y por escrito.</p>
          <h2>6. Enlaces a terceros</h2>
          <p>El sitio puede contener enlaces a plataformas de terceros, como WhatsApp, Instagram o LinkedIn. No somos responsables de sus contenidos ni de sus políticas de privacidad.</p>
          <h2>7. Ley aplicable</h2>
          <p>Estos términos se rigen por las leyes de la República de Colombia.</p>
          <h2>8. Contacto</h2>
          <p>Para cualquier inquietud sobre estos términos, escríbenos a <a class="text-link" href="mailto:{FIRM["email"]}">{FIRM["email"]}</a>.</p>'''
    else:
        title, h1 = "Política de privacidad y tratamiento de datos | GC Legal", "Política de privacidad"
        desc = "Política de tratamiento de datos personales de GC Legal conforme a la Ley 1581 de 2012: finalidades, derechos de los titulares y canales de atención."
        content = f'''
          <h2>1. Responsable del tratamiento</h2>
          <p><strong>GC Legal — Gómez &amp; Cadena Abogados</strong>, con domicilio en {FIRM["city"]}, {FIRM["region"]}, Colombia. Correo: <a class="text-link" href="mailto:{FIRM["email"]}">{FIRM["email"]}</a>. WhatsApp: {FIRM["whatsapp_display"]}.</p>
          <h2>2. Marco legal</h2>
          <p>Esta política se adopta en cumplimiento de la Ley 1581 de 2012, el Decreto 1377 de 2013 (compilado en el Decreto 1074 de 2015) y demás normas que los complementen o modifiquen.</p>
          <h2>3. Datos que recogemos</h2>
          <p>Recogemos los datos que nos entregas voluntariamente a través del formulario de contacto, WhatsApp, correo electrónico o reuniones: nombre, documento de identidad, correo, teléfono, información sobre tu caso y documentos de soporte.</p>
          <h2>4. Finalidades</h2>
          <ul>
            <li>Atender tu consulta y enviarte una cotización.</li>
            <li>Prestar los servicios jurídicos contratados y gestionar los trámites correspondientes.</li>
            <li>Facturar, cobrar y cumplir obligaciones legales, contables y tributarias.</li>
            <li>Enviarte información sobre tu caso o, si lo autorizas, sobre nuestros servicios.</li>
          </ul>
          <h2>5. Secreto profesional</h2>
          <p>La información de tu caso está protegida, además, por el secreto profesional del abogado. Solo la compartimos con autoridades o terceros cuando es necesario para prestar el servicio, con tu autorización o por mandato legal.</p>
          <h2>6. Derechos de los titulares</h2>
          <p>Como titular de los datos tienes derecho a:</p>
          <ul>
            <li>Conocer, actualizar y rectificar tus datos personales.</li>
            <li>Solicitar prueba de la autorización otorgada.</li>
            <li>Ser informado sobre el uso que se ha dado a tus datos.</li>
            <li>Presentar quejas ante la Superintendencia de Industria y Comercio.</li>
            <li>Revocar la autorización o solicitar la supresión de tus datos, cuando no exista un deber legal o contractual de conservarlos.</li>
            <li>Acceder gratuitamente a tus datos.</li>
          </ul>
          <h2>7. Procedimiento para consultas y reclamos</h2>
          <p>Puedes ejercer tus derechos escribiendo a <a class="text-link" href="mailto:{FIRM["email"]}">{FIRM["email"]}</a>. Las <strong>consultas</strong> se atienden en un máximo de diez (10) días hábiles y los <strong>reclamos</strong> en un máximo de quince (15) días hábiles, prorrogables en los términos de la ley.</p>
          <h2>8. Seguridad</h2>
          <p>Adoptamos medidas técnicas, humanas y administrativas razonables para proteger tus datos contra pérdida, consulta, uso o acceso no autorizado.</p>
          <h2>9. Vigencia</h2>
          <p>Esta política rige desde su publicación. Los datos se conservarán durante el tiempo necesario para cumplir las finalidades descritas y las obligaciones legales aplicables.</p>'''
    trail = [("", "Inicio"), (kind, h1)]
    body = f'''
    <section class="page-hero">
      <div class="container">
        {breadcrumb(pg, trail)}
        <p class="eyebrow" style="margin-top:28px">Legal</p>
        <h1>{h1}</h1>
        <p class="lead">Última actualización: octubre de 2026.</p>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <div class="legal">
          {content}
        </div>
      </div>
    </section>'''
    return pg, layout(pg, title, desc, body, kind, [breadcrumb_schema(trail)])


# --------------------------------------------------------------------------
# Construcción
# --------------------------------------------------------------------------
def write(pg, html):
    out_dir = os.path.join(ROOT, pg.path) if pg.path else ROOT
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return os.path.relpath(os.path.join(out_dir, "index.html"), ROOT)


def sitemap(pages):
    urls = "".join(f"  <url><loc>{p.abs()}</loc></url>\n" for p in pages)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {FIRM['site_url']}/sitemap.xml\n")


def main():
    builders = [page_home, page_directory, lambda: page_hub("empresas"), lambda: page_hub("personas")]
    builders += [lambda s=s: page_service(s) for s in SERVICES]
    builders += [page_how, page_about, page_contact, lambda: page_legal("terminos"), lambda: page_legal("privacidad")]
    pages = []
    for b in builders:
        pg, html = b()
        print("✓", write(pg, html))
        pages.append(pg)
    sitemap(pages)
    print(f"\n{len(pages)} páginas generadas ({'URLs limpias' if CLEAN_URLS else 'enlaces portables'}).")


if __name__ == "__main__":
    main()
