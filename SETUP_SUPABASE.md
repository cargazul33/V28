# Setup Supabase — V29 (memoria del radar)

Objetivo de esta versión: **matar el bug de re-alertar lo mismo todos los días.**
Una sola tabla, `seen_licitaciones`. Nada más por ahora.

## 1. Crear el proyecto (si no lo tenés)

En https://supabase.com → New project. Anotá la región más cercana (São Paulo).

## 2. Crear la tabla

Dashboard → **SQL Editor** → pegá esto y dale Run:

```sql
create table if not exists public.seen_licitaciones (
    id          text primary key,           -- identificador único de la licitación
    texto       text,                        -- título/descripción (para auditar)
    url         text,                        -- link "ver licitación"
    primera_vez timestamptz not null default now()
);

-- Índice por fecha, para consultas de historial más adelante.
create index if not exists seen_licitaciones_primera_vez_idx
    on public.seen_licitaciones (primera_vez desc);

-- RLS: la tabla NO se expone a clientes públicos todavía. Solo la toca el
-- backend con la secret key (que igual saltea RLS). La activamos para que el
-- Security Advisor no la marque; sin políticas, nadie con anon/publishable entra.
alter table public.seen_licitaciones enable row level security;
```

## 3. Conseguir las claves

Dashboard → **Settings → API Keys**.

- **Project URL** (`https://xxxx.supabase.co`) → va al secret `SUPABASE_URL`.
- **Secret key** (`sb_secret_…`, pestaña *API Keys*). Si tu proyecto es viejo y
  solo ves *Legacy*, usá la **service_role** key (`eyJ…`). Cualquiera de las dos
  sirve → va al secret `SUPABASE_KEY`.

> La secret/service_role key tiene acceso total y saltea RLS. **Nunca** en el
> repo, frontend ni logs. Solo como secret de GitHub Actions.

## 4. Cargar los secrets en GitHub

Repo → Settings → Secrets and variables → Actions → New repository secret:

- `SUPABASE_URL` = el Project URL
- `SUPABASE_KEY` = la secret key (`sb_secret_…`) o la service_role

(El código también acepta `SUPABASE_SECRET_KEY` o `SUPABASE_SERVICE_ROLE_KEY`
como nombre de secret, por si preferís ser explícito.)

## 5. Listo

Con eso, en la próxima corrida `app.py` llama a `filtrar_nuevas`, que lee los
IDs ya vistos de Supabase, deja pasar solo las nuevas, y registra las nuevas.
Si Supabase no responde, cae a archivo local y la corrida no se frena.

## Cómo verificar que funciona

1. Corré el radar una vez → en Supabase, Table Editor → `seen_licitaciones`
   debería llenarse con las licitaciones de hoy.
2. Corré de nuevo (mismo día) → no debería mandarte las mismas alertas, y la
   tabla no debería crecer (salvo licitaciones realmente nuevas).

## Lo que NO está en esta versión (a propósito)

Tablas de `precios`, `renglones`, `runs`, `alertas`, dashboard. Eso es V30+,
cuando el dedup esté probado y andando. No tiene sentido crear el esquema de un
dashboard que todavía no existe.
