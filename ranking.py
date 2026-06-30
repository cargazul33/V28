from modules.engine.validator import validar_resultado
from modules.engine.matcher import calcular_match
from modules.engine.currency import convertir_a_ars


def score_precio(precio_ars, minimo):

    if precio_ars is None:
        return 0

    if minimo <= 0:
        return 40

    return round((minimo / precio_ars) * 40)


def score_match(match):

    tabla = {
        "EXACTO": 25,
        "CERCANO DEFENDIBLE": 18,
        "PARCIAL": 10,
        "NO MATCH": 0,
    }

    return tabla.get(match, 0)


def score_stock(resultado):

    if resultado.get("stock") is True:
        return 15

    estado = (
        str(resultado.get("estado", "")) +
        str(resultado.get("stock_texto", ""))
    ).lower()

    if "disponible" in estado:
        return 15

    return 0


def score_fuente(resultado):

    fuente = str(resultado.get("fuente", "")).lower()

    ranking = {
        "shopping china": 10,
        "nissei": 10,
        "cellshop": 9,
        "tupi": 9,
        "mercado libre argentina": 7,
        "fullh4rd": 9,
        "maximus": 9,
        "venex": 9,
        "compugarden": 8,
    }

    return ranking.get(fuente, 5)


def score_documentacion(resultado):

    ok, _ = validar_resultado(resultado)

    if ok:
        return 10

    return 0


def calcular_score(item, resultado, precio_minimo):

    match, _ = calcular_match(item, resultado)

    precio_ars = convertir_a_ars(resultado.get("precio"))

    total = 0

    total += score_precio(precio_ars, precio_minimo)
    total += score_match(match)
    total += score_stock(resultado)
    total += score_fuente(resultado)
    total += score_documentacion(resultado)

    resultado["precio_ars"] = precio_ars
    resultado["score_total"] = round(total)
    resultado["match"] = match

    return resultado


def elegir_ganador(item, resultados):

    if not resultados:
        return None

    precios = []

    for r in resultados:

        p = convertir_a_ars(r.get("precio"))

        if p:
            precios.append(p)

    minimo = min(precios) if precios else 1

    evaluados = []

    for r in resultados:

        evaluados.append(
            calcular_score(item, r, minimo)
        )

    evaluados.sort(
        key=lambda x: (
            x["score_total"],
            -(x.get("precio_ars") or 999999999)
        ),
        reverse=True,
    )

    return evaluados[0]
