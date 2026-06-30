import os
import re
from urllib.parse import unquote

DOWNLOAD_DIR = "downloads"


def limpiar_nombre(nombre):
    nombre = nombre or "archivo.pdf"
    nombre = unquote(nombre)
    nombre = re.sub(r'[\\/*?:"<>|]', "_", nombre)
    nombre = re.sub(r"\s+", " ", nombre).strip()

    if "." not in nombre:
        nombre += ".pdf"

    return nombre


def descargar_descargas(page, descargas):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    archivos = []

    for d in descargas or []:
        nombre = limpiar_nombre(d.get("nombre") or d.get("texto") or "archivo.pdf")
        link = d.get("link") or d.get("href") or ""

        if not link or "adescargaradj" not in link:
            continue

        try:
            # Buscar cualquier elemento real de descarga en la página actual
            selector = f"a[href*='adescargaradj'], img[src*='Descarga'], input[value*='Descargar']"

            with page.expect_download(timeout=60000) as download_info:
                page.locator(selector).first.click(timeout=30000)

            download = download_info.value
            destino = os.path.join(DOWNLOAD_DIR, nombre)
            download.save_as(destino)
            archivos.append(destino)

        except Exception as e:
            print(f"Error descargando por click {nombre}: {e}")

    return archivos
