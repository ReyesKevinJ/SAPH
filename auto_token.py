from playwright.sync_api import sync_playwright
import json
import time

def renovar_credenciales():
    print("🔄 Iniciando navegador automático para obtener nuevos tokens del SMN...")
    
    with sync_playwright() as p:
        # Se lanza con ventana visible temporalmente porque Cloudflare bloquea navegadores 100% invisibles
        browser = p.chromium.launch(headless=False)
        
        # Simulamos tu User-Agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        credenciales = {"token": None, "cookie": None}
        
        # Interceptamos las peticiones de red buscando la autorización de la API
        def interceptar_peticion(request):
            if "ws1.smn.gob.ar/v1/images/radar" in request.url:
                if "authorization" in request.headers:
                    # Capturamos el token completo (incluyendo la palabra "JWT ")
                    credenciales["token"] = "JWT " + request.headers["authorization"].replace("JWT ", "")
                    
        page.on("request", interceptar_peticion)
        
        try:
            print("🌐 Entrando a smn.gob.ar/radar...")
            page.goto("https://www.smn.gob.ar/radar", timeout=45000)
            
            # Esperamos 10 segundos para darle tiempo a Cloudflare y a la carga del mapa
            time.sleep(10)
        except Exception as e:
            print(f"⚠️ Aviso de carga (puede ser ignorado si los tokens se obtienen): {e}")
            
        # Extraemos la cookie cf_clearance directamente del navegador
        cookies = context.cookies()
        for c in cookies:
            if c['name'] == 'cf_clearance':
                credenciales["cookie"] = f"has_js=1; cf_clearance={c['value']}"
                
        browser.close()
        
        if credenciales["token"] and credenciales["cookie"]:
            with open("credenciales_smn.json", "w", encoding="utf-8") as f:
                json.dump(credenciales, f, indent=4)
            print(f"✅ ¡Éxito! Token y Cookie guardados en credenciales_smn.json")
            return True
        else:
            print("❌ Falló la extracción. Cloudflare podría estar bloqueando el acceso.")
            return False

if __name__ == "__main__":
    renovar_credenciales()