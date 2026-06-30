import re
from urllib.parse import urljoin

BASE = "https://codi.neuquen.gob.ar/PortalLicitaciones/servlet/"


def normalizar_url(url):
    if not url:
        return ""
    if url.startswith("http"):
        return url
    return urljoin(BASE, url)


def limpiar(texto):
    texto = texto or ""
    return re.sub(r"\s+", " ", texto).strip()


def leer_detalle(page, url):
    url = normalizar_url(url)

    page.goto(url, wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(2500)

    texto = page.locator("body").inner_text(timeout=30000)
    html = page.content()

    descargas = []
    vistos = set()

    patrones = re.findall(
        r'com\.portallicitaciones\.adescargaradj\?[^"\\<>\s]+',
        html
    )

    nombres = re.findall(
        r'[^"\\<>]+?\.(?:pdf|xls|xlsx|doc|docx|zip)',
        html,
        flags=re.I
    )

    for i, link in enumerate(patrones):
        if link in vistos:
            continue

        vistos.add(link)

        descargas.append({
            "texto": limpiar(nombres[i]) if i < len(nombres) else "Descargar Archivo",
            "href": normalizar_url(link),
            "origen": "html_regex"
        })

    return {
        "url": url,
        "texto": texto,
        "descargas": descargas
    }
