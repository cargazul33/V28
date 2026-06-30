from pathlib import Path
import re
from datetime import datetime

from modules.engine.currency import convertir_a_ars, precio_legible


SEPARADOR = "━━━━━━━━━━━━━━━━━━━━"


def limpiar(texto):
    texto = str(texto or "")
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def recortar(texto, limite=240):
    texto = limpiar(texto)
    return texto[:limite] + ("..." if len(texto) > limite else "")


def nombre_archivo(path):
    return Path(path or "").name


def etiqueta_prioridad(puntaje):
    try:
        puntaje = int(puntaje or 0)
    except Exception:
        puntaje = 0

    if puntaje >= 85:
        return "🟢 COTIZAR YA"
    if puntaje >= 60:
        return "🟡 REVISAR"
    return "🔴 DESCARTAR"


def rentabilidad_estimada(puntaje, items=None):
    items = items or []
    categorias = " ".join([str(i.get("categoria", "")) for i in items]).upper()

    base = int(puntaje or 0)
    if any(x in categorias for x in ["HARDWARE", "TONER", "UPS", "ILUMINACIÓN", "ILUMINACION"]):
        base += 5
    if any(x in categorias for x in ["SIN CLASIFICAR", "CLIMATIZACIÓN", "CLIMATIZACION"]):
        base -= 8

    if base >= 90:
        return "⭐⭐⭐⭐⭐ ALTA"
    if base >= 78:
        return "⭐⭐⭐⭐ BUENA"
    if base >= 65:
        return "⭐⭐⭐ MEDIA"
    return "⭐⭐ BAJA"


def tiempo_estimado(items=None, puntaje=0):
    cantidad = len(items or [])
    if cantidad <= 2 and puntaje >= 85:
        return "10-20 min"
    if cantidad <= 4:
        return "20-35 min"
    return "35+ min"


def accion_sugerida(puntaje):
    puntaje = int(puntaje or 0)
    if puntaje >= 85:
        return "✅ Cotizar primero. Revisar pliego y validar stock."
    if puntaje >= 60:
        return "🟡 Revisar rápido. Cotizar solo si los ítems son simples."
    return "🔴 Baja prioridad. No perder tiempo salvo pedido puntual."


def link_es_busqueda(url):
    """Detecta links que NO son ficha directa de producto.

    Regla Prompt Maestro: catalogsearch/listados/búsquedas/categorías nunca
    pueden mostrarse como precio base ganador, aunque tengan precio visible.
    """
    url = str(url or "").lower()
    fragmentos_invalidos = [
        "catalogsearch", "listado", "/search", "search?", "?q=", "&q=",
        "buscar", "resultado", "result/?q=", "category", "categoria", "termo=",
    ]
    return any(x in url for x in fragmentos_invalidos)


def ref_tiene_precio(ref):
    return bool(convertir_a_ars((ref or {}).get("precio")))


def ref_link_directo(ref):
    return bool(ref and ref.get("url") and not link_es_busqueda(ref.get("url")))


def ref_publicacion_limpia(ref):
    """Solo es ganador si tiene precio + link directo + no fue marcado inválido."""
    if not ref or not ref_tiene_precio(ref) or not ref_link_directo(ref):
        return False
    errores = [str(e).lower() for e in (ref.get("errores_validacion") or [])]
    errores_bloqueantes = [
        "link no directo", "sin precio", "sin enlace", "publicación no activa",
        "publicacion no activa", "sin producto identificable",
    ]
    return not any(any(b in e for b in errores_bloqueantes) for e in errores)


def mejor_referencia(referencias):
    """Devuelve ganador limpio si existe; si no, referencia cercana para revisar.

    Importante: una referencia con link de búsqueda puede volver como
    'cercana', pero formatear_referencia la mostrará como SIN MATCH EXACTO
    LIMPIO y nunca como precio base ganador.
    """
    refs = [dict(r) for r in (referencias or []) if r.get("url")]
    if not refs:
        return None

    con_precio = []
    for ref in refs:
        ars = convertir_a_ars(ref.get("precio"))
        if ars:
            ref["_ars"] = ars
            con_precio.append(ref)

    def match_score(ref):
        tabla = {
            "EXACTO": 4,
            "CERCANO DEFENDIBLE": 3,
            "PARCIAL": 2,
            "NO MATCH": 0,
        }
        return tabla.get(ref.get("match"), 1)

    # 1) Ganador real: precio publicado + link directo útil.
    limpias = [r for r in con_precio if ref_publicacion_limpia(r)]
    if limpias:
        limpias.sort(key=lambda r: (-match_score(r), r.get("_ars", 10**18)))
        limpias[0]["_estado_mm"] = "GANADOR_LIMPIO"
        return limpias[0]

    # 2) No hay ganador: devolver la más cercana para revisión, no como ganadora.
    if con_precio:
        con_precio.sort(key=lambda r: (-match_score(r), r.get("_ars", 10**18)))
        con_precio[0]["_estado_mm"] = "SIN_MATCH_EXACTO_LIMPIO"
        return con_precio[0]

    cercana = refs[0]
    cercana["_estado_mm"] = "SIN_HALLAZGO_VERIFICABLE"
    return cercana


def formatear_referencia(ref):
    if not ref:
        return [
            "🎯 Estado:",
            "SIN HALLAZGO VERIFICABLE CON PRECIO PUBLICADO",
        ]

    precio = ref.get("precio") or ""
    ars = precio_legible(precio) if precio else "-"
    fuente = ref.get("fuente") or ref.get("proveedor") or "-"
    pais = ref.get("pais") or "-"
    match = ref.get("match") or "REVISAR"
    url = ref.get("url") or "-"
    estado_mm = ref.get("_estado_mm") or ""

    # Candado final: link de búsqueda/listado NO puede ser ganador.
    if not ref_publicacion_limpia(ref):
        lineas = [
            "🔎 SIN MATCH EXACTO LIMPIO",
        ]
        if precio:
            lineas.append(f"Precio observado no ganador: {precio} ≈ {ars}")
        lineas.extend([
            f"🏪 {fuente} / {pais}",
            f"🎯 Match declarado: {match} (pendiente de ficha directa)",
            f"🔗 ENLACE MÁS CERCANO: {url}",
            "⚠️ NO TOMAR COMO PRECIO BASE GANADOR: falta ficha directa útil con precio publicado.",
        ])
        if link_es_busqueda(url):
            lineas.append("⚠️ Link de búsqueda/listado/categoría. Abrir y validar producto exacto antes de ofertar.")
        errores = ref.get("errores_validacion") or []
        if errores:
            lineas.append("⚠️ " + "; ".join([str(e) for e in errores[:2]]))
        return lineas

    lineas = [
        "🥇 Precio base verificado:",
        f"{precio} ≈ {ars}",
        f"🏪 {fuente} / {pais}",
        f"🎯 Match: {match}",
        f"🔗 {url}",
        "⚠️ PRECIO BASE VERIFICADO. Validar admisibilidad documental, comercial y técnica antes de ofertar.",
    ]

    errores = ref.get("errores_validacion") or []
    if errores:
        lineas.append("⚠️ " + "; ".join([str(e) for e in errores[:2]]))

    return lineas


def formatear_items(items_resueltos, max_items=3):
    if not items_resueltos:
        return ["📦 Ítems: sin renglones cotizables claros."]

    salida = ["📦 Ítems clave"]

    for idx, res in enumerate(items_resueltos[:max_items], start=1):
        item = res.get("item", {})
        ref = mejor_referencia(res.get("referencias", []))

        producto = item.get("producto") or "Ítem sin nombre"
        categoria = item.get("categoria") or "-"
        estado = item.get("estado_renglon") or "-"
        cantidad = item.get("cantidad")
        codigo = item.get("codigo")

        salida.append("")
        salida.append(f"{idx}) {producto}")
        salida.append(f"   Categoría: {categoria}")
        salida.append(f"   Renglón: {estado}")
        if cantidad:
            salida.append(f"   Cantidad: {cantidad}")
        if codigo:
            salida.append(f"   Código: {codigo}")

        for linea in formatear_referencia(ref):
            salida.append("   " + linea)

    return salida


def extraer_resumen_licitacion(texto):
    texto = limpiar(texto)
    apertura = ""
    m_fecha = re.search(r"\b(\d{2}/\d{2}/\d{2,4}\s+\d{1,2}:\d{2})\b", texto)
    if m_fecha:
        apertura = m_fecha.group(1)

    organismo = ""
    m_org = re.search(r"\b(MINISTERIO|SUBSECRETAR[IÍ]A|DIRECCI[ÓO]N|FONDO|EPAS|IPVU|VIALIDAD|JEFATURA)[^\n\r]{0,90}", texto, flags=re.I)
    if m_org:
        organismo = recortar(m_org.group(0), 110)

    return organismo, apertura


def construir_alerta_licitacion(op, detalle=None, archivo_pdf=None, link_pliego=None, items_resueltos=None):
    puntaje = int(op.get("puntaje", 0) or 0)
    texto = op.get("texto", "")
    organismo, apertura = extraer_resumen_licitacion(texto)
    items_resueltos = items_resueltos or []

    lineas = []
    lineas.append("🚨 RADAR M&M V27 — FULL CRAWLER DIARIO")
    lineas.append("")
    lineas.append(f"{etiqueta_prioridad(puntaje)} ({puntaje}/100)")
    lineas.append("")

    if organismo:
        lineas.append("🏛 Organismo")
        lineas.append(organismo)
        lineas.append("")

    lineas.append("📄 Licitación")
    lineas.append(recortar(texto, 280))
    lineas.append("")

    if apertura:
        lineas.append(f"📅 Apertura: {apertura}")

    lineas.append(f"💰 Rentabilidad: {rentabilidad_estimada(puntaje, [r.get('item', {}) for r in items_resueltos])}")
    lineas.append(f"⏱ Tiempo estimado: {tiempo_estimado(items_resueltos, puntaje)}")
    lineas.append("")

    if link_pliego:
        lineas.append("📥 Descargar pliego")
        lineas.append(link_pliego)
        lineas.append("")

    if op.get("visualizar_url"):
        lineas.append("🌐 Ver licitación")
        lineas.append(op.get("visualizar_url"))
        lineas.append("")

    if archivo_pdf:
        lineas.append(f"✅ PDF leído: {nombre_archivo(archivo_pdf)}")
        lineas.append("")

    lineas.append(SEPARADOR)
    lineas.extend(formatear_items(items_resueltos, max_items=3))
    lineas.append(SEPARADOR)
    lineas.append("")
    lineas.append("🤖 Recomendación")
    lineas.append(accion_sugerida(puntaje))
    lineas.append("")
    lineas.append(datetime.now().strftime("🕒 %d/%m/%Y %H:%M"))

    return "\n".join(lineas).strip()



def construir_resumen_corrida(total, enviadas, oportunidades, detalle_revisadas=0, documentos=0, items=0):
    cotizar = sum(1 for o in oportunidades if int(o.get("puntaje", 0) or 0) >= 85)
    revisar = sum(1 for o in oportunidades if 60 <= int(o.get("puntaje", 0) or 0) < 85)

    return (
        "✅ Radar M&M V27\n\n"
        "Corrida profunda OK\n"
        f"Licitaciones detectadas: {total}\n"
        f"Licitaciones abiertas en detalle: {detalle_revisadas}\n"
        f"Documentos descargados/leídos: {documentos}\n"
        f"Ítems extraídos: {items}\n"
        f"Alertas enviadas: {enviadas}\n"
        f"🟢 Cotizar: {cotizar}\n"
        f"🟡 Revisar: {revisar}\n\n"
        "Sin Excel. Sin artifacts. Solo Telegram.\n"
        "Modo V27: escaneo profundo diario + Paraguay primero + Brave + Argentina si Paraguay falla."
    )
