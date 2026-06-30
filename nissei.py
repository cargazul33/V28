import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from config import REQUEST_TIMEOUT


BASE_URL = "https://nissei.com"
SEARCH_URL = "https://nissei.com/py/catalogsearch/result/?q={q}"

HEADERS = {"User-Agent": "Mozilla/5.0"}


def limpiar(texto):
    texto = texto or ""
    return re.sub(r"\s+", " ", texto).strip()


def extraer_precio(texto):
    patrones = [
        r"Gs\.?\s?[\d\.,]+",
        r"U\$S\s?[\d\.,]+",
        r"USD\s?[\d\.,]+",
        r"\$\s?[\d\.,]+",
    ]

    for p in patrones:
        m = re.search(p, texto or "", flags=re.I)
        if m:
            return limpiar(m.group(0))

    return ""


def buscar(producto: str):
    producto = producto or ""
    url = SEARCH_URL.format(q=quote_plus(producto))

    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)

        if not r.ok:
            return {
                "proveedor": "Nissei",
                "fuente": "Nissei",
                "pais": "PY",
                "query": producto,
                "titulo": producto,
                "precio": "",
                "url": url,
                "estado": "ERROR_HTTP",
                "stock": False,
                "stock_texto": "no verificado",
            }

        soup = BeautifulSoup(r.text, "html.parser")
        texto = limpiar(soup.get_text(" "))

        precio = extraer_precio(texto)

        return {
            "proveedor": "Nissei",
            "fuente": "Nissei",
            "pais": "PY",
            "query": producto,
            "titulo": producto,
            "descripcion": texto[:800],
            "precio": precio,
            "moneda": "PYG" if "Gs" in precio else "",
            "stock": False,
            "stock_texto": "revisar manualmente",
            "estado": "REFERENCIA_REVISAR",
            "url": url,
        }

    except Exception as e:
        return {
            "proveedor": "Nissei",
            "fuente": "Nissei",
            "pais": "PY",
            "query": producto,
            "titulo": producto,
            "precio": "",
            "url": url,
            "estado": f"ERROR: {str(e)[:80]}",
            "stock": False,
            "stock_texto": "no verificado",
        }
