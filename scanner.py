import re
from urllib.parse import urljoin

URL_LICITACIONES = "https://codi.neuquen.gob.ar/PortalLicitaciones/servlet/com.portallicitaciones.wwlicitacion"
BASE = "https://codi.neuquen.gob.ar/PortalLicitaciones/servlet/"

EXCLUIR = [
    "MINISTERIO DE SALUD",
    "POLICIA",
    "POLICÍA",
    "CONSEJO PROVINCIAL DE EDUCACION",
    "CONSEJO PROVINCIAL DE EDUCACIÓN",
    "C.P.E",
    "CPE",
]

CLAVES_COTIZAR = [
    "DISCOS EXTERNOS",
    "DISCO EXTERNO",
    "IMPRESORA",
    "MONITORES",
    "MONITOR",
    "INSUMOS INFORMÁTICOS",
    "INSUMOS INFORMATICOS",
    "EQUIPAMIENTO INFORMÁTICO",
    "EQUIPAMIENTO INFORMATICO",
    "HARDWARE",
    "EQUIPO DE COMPUTACIÓN",
    "EQUIPO DE COMPUTACION",
    "CONECTIVIDAD",
    "RED",
    "ROUTER",
    "SWITCH",
    "VIDEOSEGURIDAD",
    "VIDEOVIGILANCIA",
    "ELECTRICIDAD Y TELEFONÍA",
    "ELECTRICIDAD Y TELEFONIA",
    "LIBRERÍA",
    "LIBRERIA",
    "PAPELERÍA",
    "PAPELERIA",
    "ÚTILES DE OFICINA",
    "UTILES DE OFICINA",
]

CLAVES_REVISAR = [
    "ESCRITORIO",
    "MOBILIARIO",
    "SILLA",
    "SILLAS",
    "ARMARIO",
    "ARMARIOS",
    "AIRE ACONDICIONADO",
    "SPLIT",
    "MATERIALES ELÉCTRICOS",
    "MATERIALES ELECTRICOS",
    "FERRETERÍA",
    "FERRETERIA",
]


def limpiar(texto):
    texto = texto or ""
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def normalizar_url(url):
    if not url:
        return ""
    if url.startswith("http"):
        return url
    return urljoin(BASE, url)


def clasificar(texto):
    t = texto.upper()

    if any(x in t for x in EXCLUIR):
        return "DESCARTAR", 0

    if any(x in t for x in CLAVES_COTIZAR):
        return "COTIZAR", 90

    if any(x in t for x in CLAVES_REVISAR):
        return "REVISAR", 65

    return "DESCARTAR", 10


def aplicar_filtros(page):
    # Estado = Publicado
    try:
        page.select_option("select[name='vLCTESTA']", label="Publicado")
        page.wait_for_timeout(1000)
    except Exception:
        pass

    # 100 registros por página
    try:
        selects = page.locator("select")
        for i in range(selects.count()):
            try:
                selects.nth(i).select_option(label="100 registros por página")
                page.wait_for_timeout(1000)
                break
            except Exception:
                continue
    except Exception:
        pass

    page.wait_for_timeout(3000)


def scan_licitaciones(page):
    page.goto(URL_LICITACIONES, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)

    aplicar_filtros(page)

    filas = page.locator("tr").count()
    resultados = []

    for i in range(min(filas, 150)):
        try:
            fila = page.locator("tr").nth(i)
            texto = limpiar(fila.inner_text(timeout=3000))

            if len(texto) < 40:
                continue

            decision, puntaje = clasificar(texto)

            if decision == "DESCARTAR":
                continue

            visualizar_url = ""
            onclick = ""

            links = fila.locator("a").count()

            for j in range(links):
                try:
                    link = fila.locator("a").nth(j)
                    link_text = limpiar(link.inner_text(timeout=1000))
                    href = link.get_attribute("href") or ""
                    oc = link.get_attribute("onclick") or ""

                    combinado = f"{link_text} {href} {oc}"

                    if "Visualizar" in combinado or "wpverdetalleprove" in combinado:
                        visualizar_url = normalizar_url(href)
                        onclick = oc
                        break
                except Exception:
                    pass

            resultados.append({
                "decision": decision,
                "puntaje": puntaje,
                "texto": texto[:1000],
                "visualizar_url": visualizar_url,
                "onclick": onclick,
            })

        except Exception as e:
            print("Error leyendo fila", i, e)

    return resultados
