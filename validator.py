from config import INVALID_PRODUCT_WORDS


def limpiar(texto):
    texto = texto or ""
    return " ".join(str(texto).replace("\n", " ").split()).strip()


def contiene_precio(resultado):
    precio = resultado.get("precio") if isinstance(resultado, dict) else None
    if not precio:
        return False

    precio_txt = str(precio).strip().lower()

    invalidos = [
        "",
        "-",
        "sin precio",
        "consultar",
        "consultar precio",
        "sin hallazgo verificable con precio publicado",
    ]

    return precio_txt not in invalidos


def contiene_link_directo(resultado):
    url = resultado.get("url") if isinstance(resultado, dict) else None
    if not url:
        return False

    url = str(url).strip().lower()

    invalidos = [
        "catalogsearch",
        "search",
        "buscar",
        "listado",
        "categoria",
        "category",
        "?q=",
    ]

    return not any(x in url for x in invalidos)


def publicacion_activa(resultado):
    texto = " ".join([
        str(resultado.get("titulo", "")),
        str(resultado.get("descripcion", "")),
        str(resultado.get("estado", "")),
        str(resultado.get("stock_texto", "")),
    ]).lower()

    for palabra in INVALID_PRODUCT_WORDS:
        if palabra.lower() in texto:
            return False

    return True


def disponibilidad_solida(resultado):
    if resultado.get("stock") is True:
        return True

    texto = " ".join([
        str(resultado.get("estado", "")),
        str(resultado.get("stock_texto", "")),
        str(resultado.get("descripcion", "")),
    ]).lower()

    positivos = [
        "disponible",
        "en stock",
        "stock disponible",
        "agregar al carrito",
        "comprar",
    ]

    return any(x in texto for x in positivos)


def validar_resultado(resultado):
    errores = []

    if not isinstance(resultado, dict):
        return False, ["resultado inválido"]

    if not contiene_precio(resultado):
        errores.append("sin precio publicado")

    if not resultado.get("titulo"):
        errores.append("sin producto identificable")

    if not resultado.get("url"):
        errores.append("sin enlace")

    if resultado.get("url") and not contiene_link_directo(resultado):
        errores.append("link no directo")

    if not publicacion_activa(resultado):
        errores.append("publicación no activa o inválida")

    if not disponibilidad_solida(resultado):
        errores.append("stock no confirmado")

    return len(errores) == 0, errores


def semaforo_resultado(resultado):
    valido, errores = validar_resultado(resultado)

    if valido:
        return "LIMPIO"

    if contiene_precio(resultado) and resultado.get("url"):
        return "OBSERVABLE"

    return "NO_RECOMENDADO"


def marcar_validacion(resultado):
    valido, errores = validar_resultado(resultado)

    resultado["valido"] = valido
    resultado["errores_validacion"] = errores
    resultado["semaforo"] = semaforo_resultado(resultado)

    return resultado
