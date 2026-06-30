import re


def extraer_codigo(texto):
    t = (texto or "").upper()

    codigos = re.findall(r"\b[A-Z]{1,4}\d{2,5}[A-Z]?\b", t)
    if codigos:
        return codigos[0]

    return ""


def tipo_base(texto):
    t = (texto or "").upper()

    if ";" in t:
        return t.split(";")[0].strip()

    palabras = [
        "ESCRITORIO",
        "CARTUCHO DE TONER",
        "COMPUTADORA",
        "MONITOR",
        "DISCO RIGIDO",
        "ESTABILIZADOR",
        "CABLE CONECTOR",
    ]

    for p in palabras:
        if p in t:
            return p

    return t[:60]


def clave_dedupe(texto):
    codigo = extraer_codigo(texto)
    tipo = tipo_base(texto)

    if codigo:
        return f"{tipo}|{codigo}"

    t = (texto or "").lower()
    t = re.sub(r"marca sugerida:.*", "", t, flags=re.I)
    t = re.sub(r"especificacion adicional:.*", "", t, flags=re.I)
    t = re.sub(r"especificación adicional:.*", "", t, flags=re.I)
    t = re.sub(r"[^a-z0-9áéíóúñ]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()

    return f"{tipo}|{t[:140]}"


def clasificar_renglon(texto):
    t = (texto or "").lower()

    if any(x in t for x in ["cartucho", "toner", "tóner", "ce340a", "ce341a", "ce342a", "ce343a", "mp305", "ricoh"]):
        return {"rubro": "TONER / INSUMOS IMPRESIÓN", "decision": "COTIZAR", "puntaje": 95}

    if any(x in t for x in ["computadora", "monitor", "disco rigido", "disco rígido", "ssd", "hdmi", "vga", "notebook"]):
        return {"rubro": "HARDWARE", "decision": "COTIZAR", "puntaje": 95}

    if any(x in t for x in ["estabilizador", "ups", "tension", "tensión", "fuente", "220 v", "1000 va"]):
        return {"rubro": "ELECTRICIDAD / UPS", "decision": "COTIZAR", "puntaje": 85}

    if any(x in t for x in ["impresora", "alquiler de impresoras"]):
        return {"rubro": "IMPRESIÓN", "decision": "COTIZAR", "puntaje": 90}

    if any(x in t for x in ["escritorio", "silla", "mobiliario", "armario", "melamina"]):
        return {"rubro": "MUEBLES / OFICINA", "decision": "REVISAR", "puntaje": 70}

    if any(x in t for x in ["herramienta", "taladro", "amoladora", "llave", "destornillador"]):
        return {"rubro": "HERRAMIENTAS", "decision": "REVISAR", "puntaje": 70}

    if any(x in t for x in ["aire acondicionado", "split", "climatización", "climatizacion"]):
        if any(x in t for x in ["service", "mantenimiento", "certificado", "carrier network manager"]):
            return {"rubro": "CLIMATIZACIÓN / SERVICIO", "decision": "DESCARTAR", "puntaje": 35}
        return {"rubro": "CLIMATIZACIÓN / EQUIPO", "decision": "REVISAR", "puntaje": 65}

    if any(x in t for x in ["servicio", "mantenimiento", "mano de obra", "instalación", "instalacion", "capacitación"]):
        return {"rubro": "SERVICIO", "decision": "DESCARTAR", "puntaje": 30}

    return {"rubro": "SIN CLASIFICAR", "decision": "REVISAR", "puntaje": 50}


def clasificar_renglones(renglones):
    salida = []
    vistos = set()

    for r in renglones or []:
        clave = clave_dedupe(r)

        if clave in vistos:
            continue

        vistos.add(clave)
        c = clasificar_renglon(r)

        salida.append({
            "texto": r,
            "rubro": c["rubro"],
            "decision": c["decision"],
            "puntaje": c["puntaje"],
            "codigo": extraer_codigo(r)
        })

    return salida
