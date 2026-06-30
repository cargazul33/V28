# Radar M&M — V28

Monitor diario de licitaciones de **CODINEU** (Neuquén) con foco en arbitraje
**Paraguay → Argentina** para M&M Insumos. Una sola corrida profunda por día,
alerta ejecutiva por Telegram.

## Qué hace, en orden

1. **Login** en el portal CODINEU (Playwright).
2. **Scan** de licitaciones (multi-página).
3. **Detalle + descarga** de pliegos y adjuntos.
4. **Lectura de documentos** (PDF / DOCX / XLSX) y extracción de renglones.
5. **Estructura** los renglones y filtra los compatibles con el modelo M&M.
6. **Cazador de precios** Paraguay (proveedores + Brave) por ítem.
7. **Motor de decisión** (`modules/engine/decision.py`) — aplica el
   *Prompt Maestro Definitivo* de forma determinística: Paraguay primero,
   jerarquía del ganador, precio publicado + link directo + publicación activa,
   fusibles/advertencias. Salida en pesos.
8. **Telegram**: alerta por licitación + resumen de la corrida.

## Arquitectura (una sola, sin capas fósiles)

Todo el runtime vive en el paquete `modules/`. El punto de entrada es `app.py`.
No hay ZIP intermedio: el workflow corre el repo directo.

```
app.py                      # orquestación de la corrida diaria
config.py                   # versión, límites, secretos (con alias)
modules/
  login.py  scanner.py  detail.py  downloader.py
  document_reader.py  structured_extractor.py
  price_hunter.py  classifier.py  database.py
  telegram_bot.py  telegram_report.py  gmail_watcher.py  pdf_reader.py
  engine/
    orchestrator.py         # arma la auditoría por ítem y llama a decidir()
    decision.py             # Prompt Maestro Definitivo (determinístico)
    currency.py  validator.py  matcher.py  ranking.py
  providers/                # nissei, cellshop, mega, atacado, tupi, visaovip...
  storage/seen.py
  utils/  cache.py  logger.py
tests/                      # tests offline del motor de decisión y currency
```

## Correr local

```bash
pip install -r requirements.txt
python -m playwright install chromium
python -m unittest discover -s tests -p "test_*.py" -v   # tests offline
python app.py                                            # corrida completa
```

## Secretos (GitHub Actions → Settings → Secrets)

`CODI_USER`, `CODI_PASS`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, `BRAVE_API_KEY`.
Opcionales (Gmail/SAFIPRO): `GMAIL_USER`, `GMAIL_APP_PASSWORD`.

`config.py` acepta alias (`TELEGRAM_TOKEN`/`TELEGRAM_BOT_TOKEN`,
`CODI_PASS`/`CODI_PASSWORD`), así que no hay desajuste de nombres.
