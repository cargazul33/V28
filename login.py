import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

URL_LOGIN = "https://codi.neuquen.gob.ar/PortalLicitaciones/servlet/com.portallicitaciones.seguridad.login"


def crear_sesion():
    user = os.getenv("CODI_USER")
    password = os.getenv("CODI_PASS")

    if not user or not password:
        raise RuntimeError("Faltan CODI_USER o CODI_PASS en GitHub Secrets")

    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    ultimo_error = None

    for intento in range(1, 4):
        try:
            page.goto(URL_LOGIN, wait_until="commit", timeout=60000)
            page.wait_for_timeout(4000)

            if page.locator("#vUSUARIOUSERNAME").count() == 0:
                page.reload(wait_until="commit", timeout=60000)
                page.wait_for_timeout(4000)

            page.wait_for_selector("#vUSUARIOUSERNAME", timeout=60000)

            page.fill("#vUSUARIOUSERNAME", user)
            page.fill("#vUSUARIOPASSWORD", password)
            page.click("#LOGIN")

            page.wait_for_timeout(6000)

            texto = page.locator("body").inner_text(timeout=30000)

            if "Error de usuario o contraseña" in texto or "Invitado" in texto:
                raise RuntimeError("Falló login CODINEU")

            if "Licitaciones de la Provincia del Neuquén" in texto or "Presa, Magali" in texto:
                return p, browser, context, page

            return p, browser, context, page

        except Exception as e:
            ultimo_error = e
            print(f"Intento login {intento} falló: {e}")
            page.wait_for_timeout(5000)

    browser.close()
    p.stop()
    raise RuntimeError(f"No se pudo iniciar sesión CODINEU luego de 3 intentos: {ultimo_error}")
