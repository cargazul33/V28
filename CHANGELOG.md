# Changelog

## V28 — Consolidación (una sola arquitectura, ejecutable)

Esta versión no agrega features: arregla que el sistema **corra el código real**.

### Arreglado (crítico)
- **El CI corría un fósil.** El workflow descomprimía `mm-radar-v2-v21-telegram.zip`
  y ejecutaba el `app.py` de adentro (V21 congelado). Ahora corre el repo directo.
- **El `app.py` V27 no importaba.** Importaba `modules.document_reader` y
  `modules.telegram_report`, que vivían sueltos en la raíz. Movidos a `modules/`.
- **Motor de decisión apuntaba a un paquete fantasma.** `decision.py` importaba
  `radar.pricing.*` (carpeta inexistente). Plegado a `modules/engine/decision.py`
  con imports al paquete real, y **conectado al orquestador** (antes ni se llamaba).
- **Bug de import latente:** `decision` importaba `link_directo`, pero la función
  se llama `contiene_link_directo`. Corregido con alias.
- **Tests no colectaban:** apuntaban a `radar.*`. Portados los offline
  (`test_decision`, `test_currency`) a `tests/` sobre `modules.engine.*`.

### Eliminado
- ZIPs anidados (incluido `Radar_MM_V1_Base.zip` adentro del de V21).
- 45 `.pyc` versionados, `radar.log`, pliegos demo.
- Directorio basura `modules/utils/mkdir -p modules/` (comando de shell mal
  redirigido que quedó como carpeta).
- Generación paralela `radar.*` de la raíz (codebase A, no ejecutable como estaba).
  Su único valor —el motor de decisión— fue plegado a `modules/engine/`.

### Pendiente para vos (no verificable acá sin el portal)
- El camino Playwright/red (login, scan, providers) compila pero no se ejecutó
  en este entorno. Validá una corrida real con `workflow_dispatch`.
- Si querés que la alerta de Telegram muestre el veredicto del motor de decisión
  (hoy se adjunta en `auditoria["decision"]` pero el render sigue usando las
  referencias), es un cambio chico en `telegram_report.formatear_items`.
