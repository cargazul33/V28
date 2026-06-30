import re


def limpiar(texto):
    texto = texto or ""
    texto = texto.replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def normalizar_clave(campo):
    return (
        campo.lower()
        .replace(" ", "_")
        .replace("ó", "o")
        .replace("í", "i")
        .replace("é", "e")
        .replace("á", "a")
        .replace("ú", "u")
        .replace("ñ", "n")
    )


def limpiar_prefijo_producto(texto):
    texto = limpiar(texto)
    texto = re.sub(r"^(M|W|MM|CM|UN|U)\s+", "", texto, flags=re.I)
    return limpiar(texto)


def extraer_codigo(texto):
    t = (texto or "").upper()

    m = re.search(r"C[ÓO]DIGO\s+([A-Z]{1,4}\d{2,5}[A-Z]?)", t)
    if m:
        return m.group(1)

    codigos_validos = re.findall(
        r"\b(CE\d{3,4}A|CF\d{3,4}A|MP\d{3,4}|TN\d{3,5}|DR\d{3,5}|CRG\d{3,5})\b",
        t
    )
    return codigos_validos[0] if codigos_validos else ""


def extraer_marca_sugerida(texto):
    m = re.search(r"Marca Sugerida:\s*(.*?)(?:\s+-\s+|$)", texto or "", flags=re.I)
    if not m:
        return ""
    return limpiar(m.group(1)).replace("//", "/")


def extraer_cantidad(texto):
    patrones = [
        r"Cantidad\s*[:\-]?\s*(\d+)",
        r"Cant\s+Sol\s+(\d+)",
        r"cant:\s*(\d+)",
        r"\bItem\s+\d+\s+(\d+)\b",
    ]

    for p in patrones:
        m = re.search(p, texto or "", flags=re.I)
        if m:
            return int(m.group(1))

    return None


def extraer_tipo_producto(texto):
    texto = limpiar_prefijo_producto(texto)

    if ";" in texto:
        return limpiar_prefijo_producto(texto.split(";")[0]).upper()

    conocidos = [
        "CARTUCHO DE TONER",
        "COMPUTADORA",
        "MONITOR DE VIDEO",
        "MONITOR PLANO/CURVO",
        "DISCO RIGIDO",
        "ESTABILIZADOR DE TENSION",
        "CABLE CONECTOR",
        "ESCRITORIO",
        "IMPRESORA",
        "AIRE ACONDICIONADO",
        "LAMPARA BAJO CONSUMO",
        "LÁMPARA BAJO CONSUMO",
        "LISTON DE CHAPA",
        "LISTÓN DE CHAPA",
        "TUBO LED",
    ]

    t = texto.upper()
    for k in conocidos:
        if k in t:
            return k

    return limpiar_prefijo_producto(texto[:60]).upper()


def extraer_valor(campo, texto):
    patron = rf"{re.escape(campo)}\s+(.+?)(?:\s+-\s+|$)"
    m = re.search(patron, texto or "", flags=re.I)
    return limpiar(m.group(1)) if m else ""


def limpiar_specs(specs):
    specs = dict(specs or {})

    if "memoria" in specs:
        specs["ram"] = specs["memoria"].replace("DDR4320", "DDR4 3200")
        specs.pop("memoria", None)

    if "microprocesador" in specs:
        specs["cpu"] = specs["microprocesador"]
        specs.pop("microprocesador", None)

    if "disco" in specs:
        disco = specs["disco"]
        if "SSD" in disco.upper():
            specs["almacenamiento"] = disco
        specs.pop("disco", None)

    return specs


def extraer_especificaciones(texto):
    campos = [
        "Tipo",
        "Color",
        "Descripción",
        "Descripcion",
        "Uso",
        "Memoria",
        "Disco",
        "Microprocesador",
        "Tamaño",
        "Tecnología",
        "Tecnologia",
        "Resolución",
        "Resolucion",
        "Interfaz",
        "Potencia",
        "Tensión De Entrada",
        "Tension De Entrada",
        "Tensión De Salida",
        "Tension De Salida",
        "Accesorio",
        "Medidas",
        "Material",
        "Cantidad de cajones",
        "Capacidad",
        "Controlador Disco",
    ]

    specs = {}
    for campo in campos:
        valor = extraer_valor(campo, texto)
        if valor:
            specs[normalizar_clave(campo)] = valor

    return limpiar_specs(specs)


def detectar_categoria(tipo, texto):
    t = f"{tipo} {texto}".lower()

    if any(x in t for x in ["toner", "tóner", "cartucho"]):
        return "TONER / INSUMOS IMPRESIÓN"

    if any(x in t for x in ["computadora", "monitor", "disco", "ssd", "hdmi", "vga", "notebook"]):
        return "HARDWARE"

    if any(x in t for x in ["estabilizador", "ups", "tension", "tensión", "fuente", "220 v", "1000 va"]):
        return "ELECTRICIDAD / UPS"

    if any(x in t for x in ["lampara", "lámpara", "led", "liston", "listón", "tubo led"]):
        return "ELECTRICIDAD / ILUMINACIÓN"

    if any(x in t for x in ["escritorio", "silla", "melamina", "mobiliario"]):
        return "MUEBLES / OFICINA"

    if any(x in t for x in ["herramienta", "taladro", "amoladora"]):
        return "HERRAMIENTAS"

    if any(x in t for x in ["aire acondicionado", "split", "climatización", "climatizacion"]):
        return "CLIMATIZACIÓN"

    return "SIN CLASIFICAR"


def detectar_subcategoria(tipo, texto):
    t = f"{tipo} {texto}".lower()

    if any(x in t for x in ["ce340a", "ce341a", "ce342a", "ce343a", "cf237a"]):
        return "Tóner HP"

    if "mp305" in t or "ricoh" in t:
        return "Tóner Ricoh"

    if "computadora" in t:
        return "PC Escritorio"

    if "monitor" in t:
        return "Monitor"

    if "disco" in t:
        return "Disco Externo"

    if "estabilizador" in t:
        return "Estabilizador"

    if "cable" in t:
        return "Cable / Adaptador"

    if any(x in t for x in ["lampara", "lámpara"]):
        return "Lámpara LED"

    if any(x in t for x in ["liston", "listón", "tubo led"]):
        return "Listón / Accesorio LED"

    if "escritorio" in t:
        return "Escritorio"

    return ""


def detectar_servicios(texto):
    t = (texto or "").lower()

    return {
        "requiere_instalacion": any(x in t for x in ["instalación", "instalacion", "puesta en marcha"]),
        "requiere_service": any(x in t for x in ["service", "mantenimiento"]),
        "requiere_garantia": "garantía" in t or "garantia" in t,
    }


def detectar_estado_renglon(texto):
    servicios = detectar_servicios(texto)

    if servicios["requiere_instalacion"] or servicios["requiere_service"]:
        return "MIXTO O INDIVISIBLE"

    if "marca sugerida" in (texto or "").lower():
        return "SEMI-CERRADO"

    return "ABIERTO"


def construir_busqueda(tipo, texto, pais="PY"):
    codigo = extraer_codigo(texto)
    marca = extraer_marca_sugerida(texto)
    specs = extraer_especificaciones(texto)
    tipo_upper = tipo.upper()

    if codigo:
        base = f"{marca} {codigo}".strip() if marca else codigo

    elif "COMPUTADORA" in tipo_upper:
        partes = [
            "PC escritorio",
            specs.get("cpu", ""),
            specs.get("ram", ""),
            specs.get("almacenamiento", ""),
            "H510M-F" if "H510M-F" in texto.upper() else "",
        ]
        base = " ".join([p for p in partes if p])

    elif "DISCO" in tipo_upper:
        base = "disco externo 2TB"

    elif "MONITOR" in tipo_upper:
        partes = [
            "monitor",
            specs.get("tamano", ""),
            specs.get("tecnologia", ""),
            specs.get("resolucion", ""),
            specs.get("interfaz", ""),
        ]
        base = " ".join([p for p in partes if p])

    elif "ESTABILIZADOR" in tipo_upper:
        base = f"estabilizador automatico {specs.get('potencia', '')} 6 tomas"

    elif "CABLE" in tipo_upper:
        base = "cable adaptador VGA a HDMI"

    elif "LAMPARA" in tipo_upper or "LÁMPARA" in tipo_upper:
        base = f"lampara led bajo consumo {specs.get('potencia', '')}".strip()

    elif "LISTON" in tipo_upper or "LISTÓN" in tipo_upper:
        base = "liston chapa tubo led"

    else:
        base = tipo

    base = limpiar(base)

    if pais == "AR":
        return limpiar(f"{base} Argentina")

    return limpiar(f"{base} Paraguay Ciudad del Este")


def calcular_confianza(item):
    score = 50

    if item.get("producto"):
        score += 10
    if item.get("categoria") != "SIN CLASIFICAR":
        score += 10
    if item.get("subcategoria"):
        score += 5
    if item.get("codigo"):
        score += 15
    if item.get("marca_sugerida"):
        score += 5
    if item.get("especificaciones"):
        score += 10
    if item.get("cantidad"):
        score += 10

    return min(score, 99)


def estructurar_renglon(texto, archivo=None):
    texto = limpiar(texto)
    tipo = extraer_tipo_producto(texto)
    specs = extraer_especificaciones(texto)
    servicios = detectar_servicios(texto)

    item = {
        "archivo": archivo,
        "texto_original": texto,
        "producto": tipo,
        "codigo": extraer_codigo(texto),
        "cantidad": extraer_cantidad(texto),
        "marca_sugerida": extraer_marca_sugerida(texto),
        "categoria": detectar_categoria(tipo, texto),
        "subcategoria": detectar_subcategoria(tipo, texto),
        "estado_renglon": detectar_estado_renglon(texto),
        "especificaciones": specs,
        "requiere_instalacion": servicios["requiere_instalacion"],
        "requiere_service": servicios["requiere_service"],
        "requiere_garantia": servicios["requiere_garantia"],
    }

    item["compatible_mm"] = item["categoria"] not in ["SIN CLASIFICAR", "CLIMATIZACIÓN"]
    item["buscar_py"] = construir_busqueda(tipo, texto, "PY")
    item["buscar_ar"] = construir_busqueda(tipo, texto, "AR")
    item["busqueda_sugerida"] = item["buscar_py"]
    item["confianza"] = calcular_confianza(item)

    return item


def estructurar_renglones(renglones, archivo=None):
    salida = []
    vistos = set()

    for r in renglones or []:
        item = estructurar_renglon(r, archivo=archivo)
        clave = f"{item['producto']}|{item['codigo']}|{item['buscar_py']}".lower()

        if clave in vistos:
            continue

        vistos.add(clave)
        salida.append(item)

    return salida
