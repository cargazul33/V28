import re
from config import USD_TO_ARS, PYG_TO_ARS


def limpiar_numero(valor):
    valor = re.sub(r"[^\d,\.]", "", str(valor or ""))
    if not valor:
        return None
    if "." in valor and "," in valor:
        valor = valor.replace(".", "").replace(",", ".")
    elif "." in valor:
        valor = valor.replace(".", "")
    elif "," in valor:
        valor = valor.replace(",", ".")
    try:
        return float(valor)
    except Exception:
        return None


def detectar_moneda(texto):
    t = str(texto or "").upper()
    if "GS" in t or "PYG" in t or "GUARANI" in t or "GUARANÍ" in t:
        return "PYG"
    if "USD" in t or "U$S" in t or "US$" in t:
        return "USD"
    return "ARS"


def convertir_a_ars(precio):
    numero = limpiar_numero(precio)
    if numero is None:
        return None

    moneda = detectar_moneda(precio)

    if moneda == "PYG":
        return round(numero * PYG_TO_ARS)
    if moneda == "USD":
        return round(numero * USD_TO_ARS)

    return round(numero)


def precio_legible(precio):
    ars = convertir_a_ars(precio)
    if ars is None:
        return "-"
    return f"${ars:,.0f}".replace(",", ".")
