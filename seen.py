import json
from pathlib import Path


SEEN_FILE = Path("history") / "seen_licitaciones.json"


def cargar_vistos():
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not SEEN_FILE.exists():
        return set()

    try:
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    except Exception:
        return set()


def guardar_vistos(vistos):
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(
        json.dumps(sorted(list(vistos)), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def id_oportunidad(op):
    texto = op.get("texto", "")
    url = op.get("visualizar_url", "")
    return f"{texto[:220]}|{url}".strip()


def filtrar_nuevas(oportunidades):
    vistos = cargar_vistos()
    nuevas = []

    for op in oportunidades:
        oid = id_oportunidad(op)
        if oid in vistos:
            continue
        nuevas.append(op)
        vistos.add(oid)

    guardar_vistos(vistos)
    return nuevas
