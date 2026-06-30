from pathlib import Path

from modules.login import crear_sesion
from modules.scanner import scan_licitaciones
from modules.detail import leer_detalle
from modules.downloader import descargar_descargas
from modules.document_reader import extraer_renglones_archivos
from modules.structured_extractor import estructurar_renglones
from modules.engine.orchestrator import resolver_items
from modules.telegram_bot import enviar_telegram
from modules.telegram_report import construir_alerta_licitacion, construir_resumen_corrida
from modules.utils.logger import log_start, log_end, log_error
from modules.storage.seen import filtrar_nuevas
from config import (
    APP_VERSION,
    TOP_LIMIT,
    DETAIL_LIMIT,
    ITEMS_POR_PDF,
    PRICE_HUNTER_LIMIT,
    ADJUNTOS_POR_LICITACION,
)


def limpiar_descargas(descargas):
    limpias = []
    vistos = set()
    for d in descargas or []:
        nombre = d.get("texto") or d.get("nombre") or "Archivo"
        link = d.get("href") or d.get("link") or ""
        if not link or "adescargaradj" not in link:
            continue
        if link in vistos:
            continue
        vistos.add(link)
        limpias.append({"nombre": nombre, "link": link})
    return limpias


def estructurar_archivos(archivos):
    renglones_doc = extraer_renglones_archivos(archivos)
    renglones = [r["renglon"] for r in renglones_doc]
    archivo = ", ".join(sorted({Path(r.get("archivo", "")).name for r in renglones_doc if r.get("archivo")}))
    items = estructurar_renglones(renglones, archivo=archivo or None)
    # Evita gastar búsquedas en renglones débiles o no compatibles.
    items = [i for i in items if i.get("confianza", 0) >= 62 and i.get("compatible_mm", True)]
    # Ordena: primero códigos, hardware/toner, renglones puros, confianza alta.
    def score(i):
        categoria = str(i.get("categoria", "")).upper()
        return (
            1 if i.get("codigo") else 0,
            1 if any(x in categoria for x in ["TONER", "HARDWARE", "UPS", "ILUMINACIÓN", "ILUMINACION"]) else 0,
            0 if i.get("estado_renglon") == "MIXTO O INDIVISIBLE" else 1,
            i.get("confianza", 0),
        )
    return sorted(items, key=score, reverse=True)[:ITEMS_POR_PDF]


def resolver_items_licitacion(items):
    if not items:
        return []
    try:
        return resolver_items(items, limite=min(PRICE_HUNTER_LIMIT, len(items)))
    except Exception as e:
        return [{
            "item": items[0],
            "referencias": [],
            "estado": "ERROR",
            "motivo": str(e)[:180],
        }]


def procesar_oportunidad(page, op, con_precios=True):
    detalle = None
    archivos = []
    link_pliego = ""
    items_resueltos = []
    items = []

    try:
        if op.get("visualizar_url"):
            detalle = leer_detalle(page, op["visualizar_url"])
            descargas = limpiar_descargas(detalle.get("descargas"))
            if descargas:
                link_pliego = descargas[0]["link"]
                archivos = descargar_descargas(page, descargas[:ADJUNTOS_POR_LICITACION])
                items = estructurar_archivos(archivos)
                if con_precios:
                    items_resueltos = resolver_items_licitacion(items)
                else:
                    items_resueltos = [{"item": item, "referencias": [], "estado": "SIN_PRECIO"} for item in items[:3]]
    except Exception as e:
        op = dict(op)
        op["texto"] = f"{op.get('texto', '')} | Error detalle/documentos: {str(e)[:160]}"

    alerta = construir_alerta_licitacion(
        op,
        detalle=detalle,
        archivo_pdf=", ".join([Path(a).name for a in archivos[:3]]) if archivos else None,
        link_pliego=link_pliego,
        items_resueltos=items_resueltos,
    )

    return {
        "op": op,
        "detalle": detalle,
        "archivos": archivos,
        "items": items,
        "items_resueltos": items_resueltos,
        "alerta": alerta,
    }


def seleccionar_para_detalle(oportunidades):
    ordenadas = sorted(oportunidades, key=lambda o: int(o.get("puntaje", 0) or 0), reverse=True)
    return ordenadas[:DETAIL_LIMIT]


def seleccionar_para_alerta(procesadas):
    def score(p):
        op = p.get("op", {})
        items = p.get("items", [])
        resueltos = p.get("items_resueltos", [])
        tiene_codigo = any(i.get("codigo") for i in items)
        tiene_ref = any((r.get("referencias") or r.get("referencia")) for r in resueltos)
        return (
            int(op.get("puntaje", 0) or 0),
            1 if tiene_codigo else 0,
            1 if tiene_ref else 0,
            len(items),
        )
    procesadas = sorted(procesadas, key=score, reverse=True)
    return procesadas[:TOP_LIMIT]


def main():
    p = browser = None
    log_start()
    try:
        p, browser, context, page = crear_sesion()
        oportunidades = scan_licitaciones(page)
        total_detectadas = len(oportunidades)
        # Dedup persistente (Supabase): solo seguimos con las NO vistas antes.
        oportunidades = filtrar_nuevas(oportunidades)
        candidatas = seleccionar_para_detalle(oportunidades)

        if not candidatas:
            enviar_telegram(
                f"✅ Radar M&M {APP_VERSION}\n\n"
                f"Corrida OK\n"
                f"Oportunidades detectadas: {total_detectadas}\n"
                f"Nuevas (no vistas antes): {len(oportunidades)}\n"
                f"Sin oportunidades nuevas para enviar."
            )
            return

        # Escaneo profundo: abre más licitaciones que las que finalmente manda.
        procesadas = []
        for idx, op in enumerate(candidatas, start=1):
            # Para no quemar tiempo/API, solo las mejores llevan cazador de precio.
            con_precios = idx <= max(TOP_LIMIT, PRICE_HUNTER_LIMIT)
            procesadas.append(procesar_oportunidad(page, op, con_precios=con_precios))

        alertas = seleccionar_para_alerta(procesadas)
        enviadas = 0
        for p_op in alertas:
            enviar_telegram(p_op["alerta"])
            enviadas += 1

        total_docs = sum(len(p.get("archivos", [])) for p in procesadas)
        total_items = sum(len(p.get("items", [])) for p in procesadas)
        enviar_telegram(
            construir_resumen_corrida(
                total_detectadas,
                enviadas,
                oportunidades,
                detalle_revisadas=len(procesadas),
                documentos=total_docs,
                items=total_items,
            )
        )

    except Exception as e:
        log_error("Radar principal", e)
        enviar_telegram(f"❌ Error Radar M&M {APP_VERSION}:\n{str(e)[:400]}")
    finally:
        if browser:
            browser.close()
        if p:
            p.stop()
        log_end()


if __name__ == "__main__":
    main()
