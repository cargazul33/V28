import re


def limpiar(texto):
    texto = texto or ""
    texto = str(texto).lower()
    texto = texto.replace("á", "a")
    texto = texto.replace("é", "e")
    texto = texto.replace("í", "i")
    texto = texto.replace("ó", "o")
    texto = texto.replace("ú", "u")
    texto = texto.replace("ñ", "n")
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def tokens(texto):
    return set(limpiar(texto).split())


def contiene_codigo(item, resultado):
    codigo = item.get("codigo") or item.get("part_number") or ""
    if not codigo:
        return False

    texto_resultado = limpiar(
        f"{resultado.get('titulo', '')} {resultado.get('descripcion', '')}"
    )

    return limpiar(codigo) in texto_resultado


def calcular_match(item, resultado):
    producto = item.get("producto", "")
    busqueda = item.get("buscar_py") or item.get("buscar_ar") or item.get("busqueda_sugerida") or ""
    specs = item.get("especificaciones") or {}

    texto_item = " ".join([
        producto,
        busqueda,
        " ".join([str(v) for v in specs.values()]),
    ])

    texto_resultado = " ".join([
        resultado.get("titulo", ""),
        resultado.get("descripcion", ""),
        resultado.get("fuente", ""),
    ])

    t_item = tokens(texto_item)
    t_res = tokens(texto_resultado)

    if not t_item or not t_res:
        return "NO MATCH", 0

    if contiene_codigo(item, resultado):
        return "EXACTO", 100

    inter = t_item.intersection(t_res)
    ratio = len(inter) / max(len(t_item), 1)

    if ratio >= 0.55:
        return "CERCANO DEFENDIBLE", round(ratio * 100)

    if ratio >= 0.25:
        return "PARCIAL", round(ratio * 100)

    return "NO MATCH", round(ratio * 100)


def marcar_match(item, resultado):
    match, score = calcular_match(item, resultado)

    resultado["match"] = match
    resultado["match_score"] = score

    return resultado
