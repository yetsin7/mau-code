import os
import json
import urllib.request
import urllib.error

# Nombre del archivo de configuración local
CONFIG_FILE_NAME = "api-config.json"

def get_config_path() -> str:
    """
    Retorna la ruta absoluta del archivo api-config.json en la raíz del proyecto.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return os.path.join(project_root, CONFIG_FILE_NAME)

def load_api_config() -> dict:
    """
    Carga la configuración desde el archivo JSON local.
    """
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_api_config(config: dict) -> bool:
    """
    Guarda la configuración en el archivo JSON local.
    """
    config_path = get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False

def make_http_request(url: str, headers: dict = None, method: str = "GET", body_data: dict = None) -> tuple[int, dict]:
    """
    Realiza una petición HTTP utilizando urllib estándar.
    """
    headers = headers or {}
    req = urllib.request.Request(url, headers=headers, method=method)
    
    if body_data is not None:
        req.data = json.dumps(body_data).encode("utf-8")
        if "Content-Type" not in req.headers:
            req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            status = response.status
            body = response.read().decode("utf-8")
            return status, json.loads(body)
    except urllib.error.HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
            parsed_error = json.loads(error_body)
        except Exception:
            parsed_error = {"error": {"message": error.reason}}
        raise RuntimeError(parsed_error.get("error", {}).get("message", error.reason) or str(error))
    except urllib.error.URLError as error:
        raise RuntimeError(f"Error de red/conexión: {error.reason}")
    except Exception as error:
        raise RuntimeError(f"Error inesperado de comunicación: {str(error)}")

def detect_provider_protocol(custom_name: str, api_key: str) -> str | None:
    """
    Infiere de forma inteligente el protocolo de comunicación LLM a utilizar.
    Analiza primero los prefijos inequívocos de las claves API y luego palabras clave del nombre.
    """
    key_clean = api_key.strip()
    name_lower = custom_name.lower().strip()

    # 1. Validación estricta por prefijo de clave API
    if key_clean.startswith("gsk_"):
        return "groq"
    if key_clean.startswith("sk-ant-"):
        return "anthropic"
    if key_clean.startswith("sk-"):
        return "openai"
    if key_clean.startswith("AIzaSy"):
        return "gemini"

    # 2. Validación por coincidencia de subcadenas en el nombre personalizado
    if "groq" in name_lower:
        return "groq"
    if "anthropic" in name_lower or "claude" in name_lower:
        return "anthropic"
    if "gemini" in name_lower or "google" in name_lower:
        return "gemini"
    if "openai" in name_lower or "gpt" in name_lower:
        return "openai"

    return None

def test_and_fetch_models(protocol: str, api_key: str) -> list[str]:
    """
    Prueba la conexión HTTP con el protocolo inferido y obtiene los modelos disponibles.
    """
    if not api_key or not api_key.strip():
        raise RuntimeError("La clave de API no puede estar vacía.")

    protocol = protocol.lower().strip()
    models = []

    if protocol == "openai":
        url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        _, data = make_http_request(url, headers=headers)
        raw_models = data.get("data", [])
        for model in raw_models:
            model_id = model.get("id", "")
            if model_id.startswith(("gpt-", "o1-", "o3-")):
                models.append(model_id)
        if not models:
            models = [m.get("id") for m in raw_models if m.get("id")]
            
    elif protocol == "anthropic":
        url = "https://api.anthropic.com/v1/models"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
        try:
            _, data = make_http_request(url, headers=headers)
            raw_models = data.get("data", [])
            models = [m.get("id") for m in raw_models if m.get("id")]
        except Exception:
            # Fallback si falla el endpoint de listar modelos
            test_url = "https://api.anthropic.com/v1/messages"
            test_body = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "Ping"}]
            }
            make_http_request(test_url, headers=headers, method="POST", body_data=test_body)
            models = [
                "claude-3-5-sonnet-latest",
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-latest",
                "claude-3-5-haiku-20241022",
                "claude-3-opus-latest",
                "claude-3-opus-20240229",
                "claude-3-haiku-20240307"
            ]

    elif protocol == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        _, data = make_http_request(url)
        raw_models = data.get("models", [])
        for model in raw_models:
            model_name = model.get("name", "")
            if model_name.startswith("models/"):
                model_name = model_name[7:]
            if "gemini" in model_name:
                models.append(model_name)
                
    elif protocol == "groq":
        url = "https://api.groq.com/openai/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        _, data = make_http_request(url, headers=headers)
        raw_models = data.get("data", [])
        models = [m.get("id") for m in raw_models if m.get("id")]
        
    else:
        raise RuntimeError(f"Protocolo no soportado o no reconocido.")

    if not models:
        raise RuntimeError("No se detectaron modelos disponibles para esta clave.")

    models.sort()
    return models

def add_api_provider(custom_name: str, api_key: str) -> tuple[bool, list[str] | str]:
    """
    Infiere el protocolo, prueba la conexión y almacena la API de forma persistente con nombre libre.
    """
    clean_name = custom_name.strip()
    if not clean_name:
        return False, "El nombre del proveedor no puede estar vacío."

    protocol = detect_provider_protocol(clean_name, api_key)
    if not protocol:
        return False, "No se pudo inferir el protocolo del proveedor (se requiere clave de OpenAI, Anthropic, Gemini o Groq)."

    try:
        models = test_and_fetch_models(protocol, api_key)
        config = load_api_config()
        providers = config.get("providers", {})
        
        # Guardamos en minúsculas en el diccionario para uniformidad en búsquedas
        providers[clean_name.lower()] = {
            "name": clean_name,
            "api_key": api_key.strip(),
            "protocol": protocol,
            "models": models
        }
        config["providers"] = providers
        
        if save_api_config(config):
            return True, models
        else:
            return False, "Error al escribir la configuración."
    except Exception as error:
        return False, str(error)

def delete_api_provider(custom_name: str) -> bool:
    """
    Elimina un proveedor de API guardado por su nombre.
    """
    config = load_api_config()
    providers = config.get("providers", {})
    clean_key = custom_name.lower().strip()
    if clean_key in providers:
        del providers[clean_key]
        config["providers"] = providers
        return save_api_config(config)
    return False

def get_configured_providers() -> list[str]:
    """
    Retorna la lista de los nombres de los proveedores configurados por el usuario.
    
    IMPORTANTE:
    - No existen plataformas API predefinidas en el sistema.
    - El usuario puede agregar cualquier plataforma con el nombre/apodo que desee y su propia API key.
    - El sistema nunca agrega proveedores por defecto ni sugiere nombres: todo es personalizado.
    """
    config = load_api_config()
    providers = config.get("providers", {})
    return [details.get("name", key) for key, details in providers.items()]

def get_api_models() -> list[str]:
    """
    Retorna los modelos disponibles, cada uno prefijado con el nombre personalizado del proveedor.
    
    Ejemplo: Si el usuario agregó un proveedor llamado "OpenHandles" y otro "MiAPI", los modelos se listarán como:
        - OpenHandles/gpt-4
        - MiAPI/claude-3-haiku
    
    No existen modelos ni plataformas predefinidas: todo lo que aparece aquí fue agregado por el usuario.
    """
    config = load_api_config()
    providers = config.get("providers", {})
    all_models = []
    for key, details in providers.items():
        name_prefix = details.get("name", key)
        provider_models = details.get("models", [])
        for model in provider_models:
            all_models.append(f"{name_prefix}/{model}")
    return all_models

def get_api_key_for_model(model_name: str) -> tuple[str | None, str | None, str | None]:
    """
    Resuelve el nombre del modelo personalizado en (protocolo, modelo_real, api_key).
    Retorna el protocolo real para que model_client sepa cómo invocar la API transparente.
    """
    if "/" not in model_name:
        return None, None, None
        
    parts = model_name.split("/", 1)
    custom_name = parts[0].lower()
    real_model = parts[1]
    
    config = load_api_config()
    providers = config.get("providers", {})
    provider_details = providers.get(custom_name)
    if not provider_details:
        return None, None, None
        
    return provider_details.get("protocol"), real_model, provider_details.get("api_key")
