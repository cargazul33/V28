from modules.engine.validator import marcar_validacion
from modules.engine.matcher import marcar_match
from modules.utils.logger import get_logger
from modules.providers import buscar_en_paraguay
from modules.engine.decision import decidir

logger = get_logger("orchestrator")


def normalizar_resultados(item, resultados):
    salida = []

    for r in resultados or []:
        r = dict(r)

        r.setdefault("titulo", r.get("query", ""))
        r.setdefault("descripcion", r.get("query", ""))
        r.setdefault("precio", "")
        r.setdefault("stock", False)
        r.setdefault("stock_texto", "revisar manualmente")
        r.setdefault("estado", "REFERENCIA_REVISAR")

        r = marcar_match(item, r)
        r = marcar_validacion(r)

        salida.append(r)

    return salida


def ordenar_referencias(resultados):
    def score(r):
        puntos = 0

        if r.get("precio"):
            puntos += 40
        if r.get("url"):
            puntos += 30
        if r.get("match") == "EXACTO":
            puntos += 20
        elif r.get("match") == "CERCANO DEFENDIBLE":
            puntos += 15
        elif r.get("match") == "PARCIAL":
            puntos += 8
        if r.get("pais") == "PY":
            puntos += 5

        return puntos

    return sorted(resultados, key=score, reverse=True)


def resolver_item(item, usar_cache=False):
    query = item.get("buscar_py") or item.get("busqueda_sugerida") or ""

    auditoria = {
        "item": item,
        "paraguay": [],
        "argentina": [],
        "referencias": [],
        "ganador": None,
        "referencia": None,
        "estado": "SIN_REFERENCIAS",
        "motivo": "",
    }

    try:
        crudos_py = buscar_en_paraguay(query)
        resultados_py = normalizar_resultados(item, crudos_py)
        auditoria["paraguay"] = resultados_py

        referencias = [r for r in resultados_py if r.get("url")]
        referencias = ordenar_referencias(referencias)

        auditoria["referencias"] = referencias[:3]

        if referencias:
            auditoria["referencia"] = referencias[0]
            auditoria["estado"] = "REFERENCIAS_PARA_REVISAR"
            auditoria["motivo"] = "Se encontraron referencias útiles para revisión manual."
        else:
            auditoria["motivo"] = "Sin referencias útiles."

        # Prompt Maestro Definitivo: decision determinística sobre la auditoría.
        try:
            auditoria["decision"] = decidir(auditoria).to_dict()
        except Exception as e:
            auditoria["decision"] = None
            logger.error(f"decidir() falló: {e}")

        return auditoria

    except Exception as e:
        logger.error(f"Error proveedores Paraguay: {e}")
        auditoria["motivo"] = str(e)
        return auditoria


def resolver_items(items, limite=3):
    resultados = []

    for item in items[:limite]:
        try:
            resultados.append(resolver_item(item, usar_cache=False))
        except Exception as e:
            resultados.append({
                "item": item,
                "paraguay": [],
                "argentina": [],
                "referencias": [],
                "ganador": None,
                "referencia": None,
                "estado": "ERROR",
                "motivo": str(e),
            })

    return resultados
