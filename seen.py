"""Memoria de licitaciones vistas.

Backend principal: Supabase (Postgres vía REST/PostgREST), para que el estado
sobreviva entre corridas en el runner efímero de GitHub Actions.
Fallback: archivo local JSON, para que el radar siga corriendo si Supabase no
está configurado o falla la red (nunca frena la corrida por esto).
"""

import json
from pathlib import Path

import requests

from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE_SEEN, is_supabase_configured

SEEN_FILE = Path("history") / "seen_licitaciones.json"
TIMEOUT = 15


def id_oportunidad(op):
    texto = op.get("texto", "")
    url = op.get("visualizar_url", "")
    return f"{texto[:220]}|{url}".strip()


# --------------------------------------------------------------------------- #
# Backend Supabase (REST). La secret key va SOLO en el header apikey.
# --------------------------------------------------------------------------- #
def _headers(extra=None):
    h = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    if extra:
        h.update(extra)
    return h


def _rest_url():
    return f"{SUPABASE_URL.rstrip('/')}/rest/v1/{SUPABASE_TABLE_SEEN}"


def _cargar_supabase():
    r = requests.get(
        _rest_url(), headers=_headers(), params={"select": "id"}, timeout=TIMEOUT
    )
    r.raise_for_status()
    return {row["id"] for row in r.json()}


def _guardar_supabase(filas):
    if not filas:
        return
    r = requests.post(
        _rest_url(),
        headers=_headers({"Prefer": "resolution=ignore-duplicates,return=minimal"}),
        json=filas,
        timeout=TIMEOUT,
    )
    r.raise_for_status()


# --------------------------------------------------------------------------- #
# Backend local (fallback)
# --------------------------------------------------------------------------- #
def _cargar_local():
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not SEEN_FILE.exists():
        return set()
    try:
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    except Exception:
        return set()


def _guardar_local(vistos):
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(
        json.dumps(sorted(vistos), ensure_ascii=False, indent=2), encoding="utf-8"
    )


# --------------------------------------------------------------------------- #
# API pública
# --------------------------------------------------------------------------- #
def cargar_vistos():
    if is_supabase_configured():
        try:
            return _cargar_supabase()
        except Exception:
            return _cargar_local()
    return _cargar_local()


def filtrar_nuevas(oportunidades):
    """Devuelve solo las licitaciones no vistas antes y registra las nuevas."""
    vistos = cargar_vistos()
    nuevas = []
    nuevos_ids = set()
    filas = []

    for op in oportunidades or []:
        oid = id_oportunidad(op)
        if not oid or oid in vistos or oid in nuevos_ids:
            continue
        nuevas.append(op)
        nuevos_ids.add(oid)
        filas.append({
            "id": oid,
            "texto": (op.get("texto", "") or "")[:500],
            "url": op.get("visualizar_url", "") or "",
        })

    if is_supabase_configured():
        try:
            _guardar_supabase(filas)
        except Exception:
            _guardar_local(vistos | nuevos_ids)
    else:
        _guardar_local(vistos | nuevos_ids)

    return nuevas
