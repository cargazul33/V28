import os
import re
from pypdf import PdfReader


def limpiar(texto):
    texto = texto or ""
    texto = texto.replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def leer_pdf(path):
    try:
        reader = PdfReader(path)
        partes = []
        for page in reader.pages:
            partes.append(page.extract_text() or "")
        return limpiar(" ".join(partes))
    except Exception as e:
        return f"ERROR_LEYENDO_PDF: {e}"


def normalizar_item(t):
    t = limpiar(t)

    basura_inicio = [
        r"^VER ANEXO\s+",
        r"^HP ORIGINAL\s+",
        r"^ORIGINAL\s+",
        r"^0\s*-\s*plazo\s*:\s*0\s*",
        r"^Cant Sol\s*",
    ]

    for b in basura_inicio:
        t = re.sub(b, "", t, flags=re.I)

    cortes = [
        "tracto sucesivo",
        "fch. ini",
        "prorrogable",
        "actuación contable",
        "actuacion contable",
        "expediente electrónico",
        "expediente electronico",
        "item cant ofr",
        "precio unitario",
        "precio total",
        "mantenimiento de oferta",
        "lugar de entrega",
    ]

    low = t.lower()
    posiciones = [low.find(c) for c in cortes if low.find(c) != -1]

    if posiciones:
        t = t[:min(posiciones)]

    t = re.sub(r"\s*-\s*Especificacion Adicional:\s*$", "", t, flags=re.I)
    t = re.sub(r"\s*-\s*Especificación Adicional:\s*$", "", t, flags=re.I)

    return limpiar(t)


def clave_item(t):
    t = t.lower()
    t = re.sub(r"[^a-z0-9áéíóúñ]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:180]


def detectar_renglones(texto):
    texto = limpiar(texto)
    encontrados = []
    vistos = set()

    patron_productos = (
        r"([A-ZÁÉÍÓÚÑ0-9 /().-]{4,80};\s*.{20,520}?)"
        r"(?=\s+[A-ZÁÉÍÓÚÑ0-9 /().-]{4,80};|\s+Mantenimiento de oferta|\s+Lugar de entrega|$)"
    )

    for m in re.findall(patron_productos, texto, flags=re.S):
        item = normalizar_item(m)

        if len(item) < 20:
            continue

        if any(x in item.lower() for x in [
            "pliego de bases",
            "artículo",
            "articulo",
            "decreto",
            "reglamento",
            "garantía",
            "presentación de ofertas",
            "firma digital",
        ]):
            continue

        k = clave_item(item)
        if k in vistos:
            continue

        vistos.add(k)
        encontrados.append(item)

    return encontrados[:30]


def leer_pdfs_descargados(carpeta="downloads"):
    resultados = []

    if not os.path.exists(carpeta):
        return resultados

    for nombre in os.listdir(carpeta):
        if not nombre.lower().endswith(".pdf"):
            continue

        path = os.path.join(carpeta, nombre)
        texto = leer_pdf(path)
        renglones = detectar_renglones(texto)

        resultados.append({
            "archivo": path,
            "texto": texto,
            "renglones": renglones
        })

    return resultados
