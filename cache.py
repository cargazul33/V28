import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

from config import CACHE_DIR, CACHE_TTL_HOURS
from modules.utils.logger import get_logger


logger = get_logger("cache")


def _cache_key(key):
    raw = str(key).strip().lower()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cache_path(key):
    return Path(CACHE_DIR) / f"{_cache_key(key)}.json"


def set_cache(key, value, meta=None):
    path = _cache_path(key)

    payload = {
        "key": key,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=CACHE_TTL_HOURS)).isoformat(),
        "meta": meta or {},
        "value": value,
    }

    try:
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True
    except Exception as e:
        logger.error(f"No se pudo guardar cache {key}: {e}")
        return False


def get_cache(key):
    path = _cache_path(key)

    if not path.exists():
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        expires_at = datetime.fromisoformat(payload["expires_at"])

        if datetime.now() > expires_at:
            try:
                path.unlink()
            except Exception:
                pass
            return None

        return payload.get("value")

    except Exception as e:
        logger.error(f"No se pudo leer cache {key}: {e}")
        return None


def has_cache(key):
    return get_cache(key) is not None


def delete_cache(key):
    path = _cache_path(key)

    try:
        if path.exists():
            path.unlink()
        return True
    except Exception as e:
        logger.error(f"No se pudo borrar cache {key}: {e}")
        return False


def clear_expired_cache():
    removed = 0

    for path in Path(CACHE_DIR).glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            expires_at = datetime.fromisoformat(payload["expires_at"])

            if datetime.now() > expires_at:
                path.unlink()
                removed += 1

        except Exception:
            try:
                path.unlink()
                removed += 1
            except Exception:
                pass

    logger.info(f"Cache vencido limpiado: {removed} archivos")
    return removed
