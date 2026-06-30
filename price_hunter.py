import re
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SITIOS_PARAGUAY = [
    {
        "nombre": "Shopping China",
        "pais": "PY",
        "search_url": "https://www.shoppingchina.com.py/catalogsearch/result/?q={q}",
    },
    {
        "nombre": "Nissei",
        "pais": "PY",
        "search_url": "https://nissei.com/py/catalogsearch/result/?q={q}",
    },
    {
        "nombre": "Cellshop",
        "pais": "PY",
        "search_url": "https://www.cellshop.com/py/catalogsearch/result/?q={q}",
    },
]

SITIOS_ARGENTINA = [
    {
        "nombre": "Mercado Libre Argentina",
        "pais": "AR",
        "search_url": "https://listado.mercadolibre.com.ar/{q}",
    }
]


def limpiar(texto):
    texto = texto or ""
    return re.sub(r"\s+", " ", texto).strip()


def preparar_query(query):
    query = limpiar(query)
    return query.replace(" ", "+")


def extraer_precio(texto):
    texto = texto or ""

    patrones = [
        r"U\$S\s?[\d\.,]+",
        r"USD\s?[\d\.,]+",
        r"\$\s?[\d\.,]+",
        r"Gs\.?\s?[\d\.,]+",
    ]

    for patron in patrones:
        m = re.search(patron, texto, flags=re.I)
        if m:
            return limpiar(m.group(0))

    return ""


def pagina_valida(texto):
    t = (texto or "").lower()

    invalidos = [
        "sin stock",
        "agotado",
        "no disponible",
        "consultar precio",
        "consultar stock",
        "a pedido",
        "pausada",
        "producto no encontrado",
        "no encontramos resultados",
    ]

    return not any(x in t for x in invalidos)


def buscar_en_sitio(query, sitio):
    url = sitio["search_url"].format(q=preparar_query(query))

    try:
        r = requests.get(url, headers=HEADERS, timeout=20)

        if not r.ok:
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        texto = limpiar(soup.get_text(" "))

        if not pagina_valida(texto):
            return None

        precio = extraer_precio(texto)

        if not precio:
            return None

        return {
            "pais": sitio["pais"],
            "fuente": sitio["nombre"],
            "query": query,
            "precio": precio,
            "url": url,
            "estado": "PRECIO_VISIBLE",
            "match": "PARCIAL",
        }

    except Exception:
        return None


def buscar_paraguay(query):
    resultados = []

    for sitio in SITIOS_PARAGUAY:
        resultado = buscar_en_sitio(query, sitio)
        if resultado:
            resultados.append(resultado)

    return resultados


def buscar_argentina(query):
    resultados = []

    for sitio in SITIOS_ARGENTINA:
        resultado = buscar_en_sitio(query, sitio)
        if resultado:
            resultados.append(resultado)

    return resultados


def elegir_ganador(resultados):
    if not resultados:
        return None

    return resultados[0]


def buscar_precio_item(item):
    query_py = item.get("buscar_py") or item.get("busqueda_sugerida") or ""
    query_ar = item.get("buscar_ar") or query_py

    if not query_py:
        return {
            "pais": "-",
            "fuente": "-",
            "query": "",
            "precio": "SIN QUERY",
            "url": "",
            "estado": "SIN_QUERY",
            "match": "NO MATCH",
        }

    resultados_py = buscar_paraguay(query_py)
    ganador_py = elegir_ganador(resultados_py)

    if ganador_py:
        return ganador_py

    resultados_ar = buscar_argentina(query_ar)
    ganador_ar = elegir_ganador(resultados_ar)

    if ganador_ar:
        return ganador_ar

    return {
        "pais": "-",
        "fuente": "-",
        "query": query_py,
        "precio": "SIN HALLAZGO VERIFICABLE CON PRECIO PUBLICADO",
        "url": "",
        "estado": "SIN_MATCH",
        "match": "NO MATCH",
    }


def buscar_precios_items(items, limite=3):
    salida = []

    for item in items[:limite]:
        resultado = buscar_precio_item(item)

        salida.append({
            "item": item,
            "precio": resultado,
        })

    return salida


def resumen_price_hunter(resultados):
    if not resultados:
        return "\n💰 <b>Price Hunter V19:</b> sin ítems para buscar.\n"

    mensaje = "\n💰 <b>Price Hunter V19 — Primeros precios base:</b>\n"

    for i, r in enumerate(resultados, start=1):
        item = r["item"]
        precio = r["precio"]

        mensaje += (
            f"\nÍtem {i}\n"
            f"Producto: {item.get('producto')}\n"
            f"Buscar: {precio.get('query')}\n"
            f"Precio: {precio.get('precio')}\n"
            f"Fuente: {precio.get('fuente')}\n"
            f"País: {precio.get('pais')}\n"
            f"Match: {precio.get('match')}\n"
        )

        if precio.get("url"):
            mensaje += f"Link: {precio.get('url')}\n"

    return mensaje
