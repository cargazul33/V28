import os
from pathlib import Path

APP_NAME = "Radar M&M"
APP_VERSION = "V29"

BASE_DIR = Path(__file__).resolve().parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
CACHE_DIR = BASE_DIR / "cache"
HISTORY_DIR = BASE_DIR / "history"
LOGS_DIR = BASE_DIR / "logs"
for folder in [DOWNLOADS_DIR, CACHE_DIR, HISTORY_DIR, LOGS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Modo V27: una corrida diaria profunda, Telegram ejecutivo.
TOP_LIMIT = int(os.getenv("TOP_LIMIT", "5"))                 # alertas Telegram máximas
DETAIL_LIMIT = int(os.getenv("DETAIL_LIMIT", "25"))           # licitaciones a abrir en detalle
MAX_CODI_PAGES = int(os.getenv("MAX_CODI_PAGES", "8"))         # páginas CODINEU a recorrer
MAX_ROWS_PER_PAGE = int(os.getenv("MAX_ROWS_PER_PAGE", "150"))
ADJUNTOS_POR_LICITACION = int(os.getenv("ADJUNTOS_POR_LICITACION", "4"))
ITEMS_POR_PDF = int(os.getenv("ITEMS_POR_PDF", "6"))           # renglones extraídos por licitación
PRICE_HUNTER_LIMIT = int(os.getenv("PRICE_HUNTER_LIMIT", "3")) # ítems con búsqueda de precio por alerta

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "25"))
CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))

TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN", "")).strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

GMAIL_USER = os.getenv("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()
SAFIPRO_EMAIL = os.getenv("SAFIPRO_EMAIL", "safipro_no_responder@neuquen.gov.ar").strip()

CODI_USER = os.getenv("CODI_USER", "").strip()
CODI_PASSWORD = (os.getenv("CODI_PASS") or os.getenv("CODI_PASSWORD", "")).strip()
CODI_LOGIN_URL = os.getenv(
    "CODI_LOGIN_URL",
    "https://codi.neuquen.gob.ar/PortalLicitaciones/servlet/com.portallicitaciones.seguridad.login",
).strip()

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "").strip()

# Supabase: memoria persistente del radar (dedup de licitaciones vistas).
# La clave va SOLO como secret en GitHub Actions, nunca en el repo.
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = (
    os.getenv("SUPABASE_KEY")
    or os.getenv("SUPABASE_SECRET_KEY")
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
).strip()
SUPABASE_TABLE_SEEN = os.getenv("SUPABASE_TABLE_SEEN", "seen_licitaciones").strip()

USD_TO_ARS = float(os.getenv("USD_TO_ARS", "1550"))
PYG_TO_ARS = float(os.getenv("PYG_TO_ARS", "0.22"))

INVALID_PRODUCT_WORDS = [
    "sin stock", "agotado", "no disponible", "consultar precio", "consultar stock",
    "consultar disponibilidad", "a pedido", "pausada", "publicación finalizada",
    "publicacion finalizada", "producto no encontrado", "no encontramos resultados",
    "out of stock", "sold out", "indisponível", "indisponivel",
]

# Para mantener runtime/costo controlados.
BRAVE_RESULTS_PER_QUERY = int(os.getenv("BRAVE_RESULTS_PER_QUERY", "5"))
BRAVE_MAX_QUERIES_PER_ITEM = int(os.getenv("BRAVE_MAX_QUERIES_PER_ITEM", "6"))
DIRECT_FETCH_LIMIT_PER_PROVIDER = int(os.getenv("DIRECT_FETCH_LIMIT_PER_PROVIDER", "5"))


def is_telegram_configured():
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)


def is_gmail_configured():
    return bool(GMAIL_USER and GMAIL_APP_PASSWORD)


def is_supabase_configured():
    return bool(SUPABASE_URL and SUPABASE_KEY)


def is_codi_configured():
    return bool(CODI_USER and CODI_PASSWORD)
