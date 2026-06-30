import os
import re
from imap_tools import MailBox, AND

SAFIPRO_EMAIL = "safipro_no_responder@neuquen.gov.ar"


def limpiar(texto):
    texto = texto or ""
    texto = texto.replace("\r", " ").replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def extraer_datos_licitacion(texto):
    texto = limpiar(texto)

    titulo = ""
    patrones = [
        r"participar en la Licitación:\s*(.*?)(?:\.|,|\n|$)",
        r"participar en la Licitacion:\s*(.*?)(?:\.|,|\n|$)",
        r"(Contratación Directa.*?\d+)",
        r"(Contratacion Directa.*?\d+)",
        r"(Concurso de precios.*?\d+)",
        r"(Concurso de Precios.*?\d+)",
        r"(Licitación Pública.*?\d+)",
        r"(Licitacion Publica.*?\d+)",
    ]

    for p in patrones:
        m = re.search(p, texto, flags=re.I)
        if m:
            titulo = limpiar(m.group(1))
            break

    numero = ""
    m_num = re.search(r"(?:Nro\.?|N°|número|numero)?\s*[-:]?\s*(\d{2,5})", titulo, flags=re.I)
    if m_num:
        numero = m_num.group(1)

    organismo = ""
    m_org = re.search(
        r"(MINISTERIO|ENTE|INSTITUTO|POLICIA|POLICÍA|SUBSECRETARIA|SUBSECRETARÍA|FONDO|DIRECCION|DIRECCIÓN).*?(?=,|\.| - |$)",
        texto,
        flags=re.I,
    )
    if m_org:
        organismo = limpiar(m_org.group(0))

    return {
        "titulo": titulo or texto[:180],
        "numero": numero,
        "organismo": organismo,
        "texto": texto,
    }


def leer_alertas_safipro(max_emails=20):
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")

    if not user or not password:
        return []

    alertas = []

    with MailBox("imap.gmail.com").login(user, password, "INBOX") as mailbox:
        mensajes = mailbox.fetch(
            AND(from_=SAFIPRO_EMAIL),
            reverse=True,
            limit=max_emails,
            mark_seen=False,
        )

        for msg in mensajes:
            subject = msg.subject or ""

            if "Nueva Licitacion" not in subject and "Nueva Licitación" not in subject:
                continue

            cuerpo = msg.text or msg.html or ""
            datos = extraer_datos_licitacion(cuerpo)

            alertas.append({
                "id": msg.uid,
                "fecha": msg.date.strftime("%Y-%m-%d %H:%M"),
                "subject": subject,
                "titulo": datos["titulo"],
                "numero": datos["numero"],
                "organismo": datos["organismo"],
                "texto": datos["texto"],
            })

    return alertas


def filtrar_alertas_no_vistas(alertas, oportunidades):
    vistos = set()

    for op in oportunidades or []:
        texto = limpiar(op.get("texto", "")).lower()
        vistos.add(texto)

    nuevas = []

    for alerta in alertas or []:
        titulo = limpiar(alerta.get("titulo", "")).lower()
        numero = alerta.get("numero", "")

        duplicada = False

        for v in vistos:
            if numero and numero in v:
                duplicada = True
                break
            if titulo and titulo[:60] in v:
                duplicada = True
                break

        if not duplicada:
            nuevas.append(alerta)

    return nuevas


def crear_resumen_gmail(alertas, max_items=5):
    if not alertas:
        return "\n📧 <b>Gmail SAFIPRO:</b> sin alertas nuevas fuera del radar.\n"

    mensaje = "\n📧 <b>Gmail SAFIPRO — Alertas nuevas:</b>\n"

    for i, a in enumerate(alertas[:max_items], start=1):
        mensaje += (
            f"\n#{i}\n"
            f"🕒 {a['fecha']}\n"
            f"📌 {a['titulo']}\n"
        )

        if a.get("organismo"):
            mensaje += f"🏢 {a['organismo']}\n"

    return mensaje
