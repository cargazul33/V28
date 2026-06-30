from urllib.parse import quote_plus


BASE_URL = "https://www.mega.com.py"


def buscar(producto: str):
    producto = producto or ""

    return {
        "proveedor": "Mega Electrónicos",
        "pais": "PY",
        "query": producto,
        "url": f"{BASE_URL}/search?controller=search&s={quote_plus(producto)}",
    }
