from urllib.parse import quote_plus

BASE_URL = "https://listado.mercadolibre.com.ar"


def buscar(producto: str):
    producto = producto or ""
    return {
        "proveedor": "Mercado Libre Argentina",
        "fuente": "Mercado Libre Argentina",
        "pais": "AR",
        "query": producto,
        "titulo": producto,
        "precio": "",
        "stock": False,
        "stock_texto": "revisar manualmente",
        "estado": "REFERENCIA_REVISAR",
        "url": f"{BASE_URL}/{quote_plus(producto)}",
    }
