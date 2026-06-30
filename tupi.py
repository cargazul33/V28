from urllib.parse import quote_plus

BASE_URL = "https://www.tupi.com.py"


def buscar(producto: str):
    producto = producto or ""
    return {
        "proveedor": "Tupi",
        "fuente": "Tupi",
        "pais": "PY",
        "query": producto,
        "titulo": producto,
        "precio": "",
        "stock": False,
        "stock_texto": "revisar manualmente",
        "estado": "REFERENCIA_REVISAR",
        "url": f"{BASE_URL}/buscar?q={quote_plus(producto)}",
    }
