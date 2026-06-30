from urllib.parse import quote_plus


BASE_URL = "https://visaovip.com"


def buscar(producto: str):
    producto = producto or ""

    return {
        "proveedor": "Visao VIP",
        "pais": "PY",
        "query": producto,
        "url": f"{BASE_URL}/busca?termo={quote_plus(producto)}",
    }
