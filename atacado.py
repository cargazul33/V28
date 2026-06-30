from urllib.parse import quote_plus


BASE_URL = "https://www.atacadogames.com"


def buscar(producto: str):
    producto = producto or ""

    return {
        "proveedor": "Atacado Games",
        "pais": "PY",
        "query": producto,
        "url": f"{BASE_URL}/buscar?q={quote_plus(producto)}",
    }
