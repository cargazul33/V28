from urllib.parse import quote_plus

BASE_URL = "https://www.shoppingchina.com.py"


def buscar(producto: str):
    producto = producto or ""
    return {
        "proveedor": "Shopping China",
        "fuente": "Shopping China",
        "pais": "PY",
        "query": producto,
        "titulo": producto,
        "precio": "",
        "stock": False,
        "stock_texto": "revisar manualmente",
        "estado": "REFERENCIA_REVISAR",
        "url": f"{BASE_URL}/catalogsearch/result/?q={quote_plus(producto)}",
    }
