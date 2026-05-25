# core

## ACTION_EXECUTOR.PY
core\action_executor.py

```python
import importlib
from core.json_parser import try_parse_json_actions
from core.permissions import ask_tool_permission
from shell.renderer import console

def handle_model_response(model_response: str, permission_session) -> None:
    """
    Decide si la respuesta del modelo es texto explicativo normal
    o una lista de instrucciones en JSON para ejecutar herramientas.
    """
    actions = try_parse_json_actions(model_response)

    # Si no hay acciones JSON, imprimimos la respuesta como conversación normal
    if actions is None:
        console.print("\n[bold green]MauCode: >[/bold green]")
        console.print(model_response)
        console.print()
        return

    # Ejecutar secuencialmente cada una de las acciones solicitadas
    for action in actions:
        execute_action(action, permission_session)

def execute_action(action: dict, permission_session) -> None:
    """
    Despachador unificado que resuelve y ejecuta dinámicamente las 18 herramientas disponibles.
    Pide autorización interactiva al usuario antes de proceder a la llamada.
    """
    action_name = action.get("action", "")
    if not action_name:
        console.print("\n[bold red]Error: Acción sin propiedad 'action' válida.[/bold red]\n")
        return

    # 1. Mostrar de forma elegante todos los parámetros de la herramienta
    console.print("\n[bold yellow]MauCode quiere ejecutar esta acción: >[/bold yellow]")
    console.print(f"[cyan]Herramienta / Tool:[/cyan] {action_name}")
    for key, val in action.items():
        if key != "action" and key != "content":
            console.print(f"[cyan]{key.capitalize()}:[/cyan] {val}")
        elif key == "content":
            # Truncamos visualmente el contenido si es excesivamente largo
            content_str = str(val)
            if len(content_str) > 80:
                content_str = content_str[:80] + "..."
            console.print(f"[cyan]Contenido / Content:[/cyan] {content_str}")

    # 2. Solicitar confirmación interactiva de seguridad
    has_permission = ask_tool_permission(permission_session)
    if not has_permission:
        console.print("\n[bold red]Acción cancelada por el usuario.[/bold red]\n")
        return

    # 3. Resolución y ejecución dinámica en caliente
    result = ""
    try:
        if action_name == "create_file":
            tool = importlib.import_module("tools.filesystem.create-file").create_file
            result = tool(action.get("folder", ""), action.get("file_name", ""), action.get("content", ""))
            
        elif action_name == "read_file":
            tool = importlib.import_module("tools.filesystem.read-file").read_file
            result = tool(action.get("folder", ""), action.get("file_name", ""))
            
        elif action_name == "edit_file":
            tool = importlib.import_module("tools.filesystem.edit-file").edit_file
            result = tool(action.get("folder", ""), action.get("file_name", ""), action.get("target_text", ""), action.get("replacement_text", ""))
            
        elif action_name == "delete_file":
            tool = importlib.import_module("tools.filesystem.delete-file").delete_file
            result = tool(action.get("folder", ""), action.get("file_name", ""))
            
        elif action_name == "move_file":
            tool = importlib.import_module("tools.filesystem.move-file").move_file
            result = tool(action.get("src_folder", ""), action.get("src_file_name", ""), action.get("dest_folder", ""), action.get("dest_file_name", ""))
            
        elif action_name == "copy_file":
            tool = importlib.import_module("tools.filesystem.copy-file").copy_file
            result = tool(action.get("src_folder", ""), action.get("src_file_name", ""), action.get("dest_folder", ""), action.get("dest_file_name", ""))
            
        elif action_name == "rename_file":
            tool = importlib.import_module("tools.filesystem.rename-file").rename_file
            result = tool(action.get("folder", ""), action.get("old_name", ""), action.get("new_name", ""))
            
        elif action_name == "create_folder":
            tool = importlib.import_module("tools.filesystem.create-folder").create_folder
            result = tool(action.get("parent_folder", ""), action.get("folder_name", ""))
            
        elif action_name == "delete_folder":
            tool = importlib.import_module("tools.filesystem.delete-folder").delete_folder
            result = tool(action.get("folder", ""))
            
        elif action_name == "list_files":
            tool = importlib.import_module("tools.filesystem.list-files").list_files
            result = tool(action.get("folder", ""))
            
        elif action_name == "read_json":
            tool = importlib.import_module("tools.data.read-json").read_json
            result = tool(action.get("folder", ""), action.get("file_name", ""))
            
        elif action_name == "write_json":
            tool = importlib.import_module("tools.data.write-json").write_json
            result = tool(action.get("folder", ""), action.get("file_name", ""), action.get("content", ""))
            
        elif action_name == "git_status":
            tool = importlib.import_module("tools.git.git-status").git_status
            result = tool(action.get("workspace_folder", ""))
            
        elif action_name == "git_diff":
            tool = importlib.import_module("tools.git.git-diff").git_diff
            result = tool(action.get("workspace_folder", ""), action.get("file_name", ""))
            
        elif action_name == "git_commit":
            tool = importlib.import_module("tools.git.git-commit").git_commit
            result = tool(action.get("workspace_folder", ""), action.get("message", ""), action.get("files", None))
            
        elif action_name == "git_branch":
            tool = importlib.import_module("tools.git.git-branch").git_branch
            result = tool(action.get("workspace_folder", ""), action.get("branch_action", ""), action.get("branch_name", ""))
            
        elif action_name == "search_code":
            tool = importlib.import_module("tools.search.search-code").search_code
            result = tool(action.get("folder", ""), action.get("pattern", ""))
            
        elif action_name == "search_text":
            tool = importlib.import_module("tools.search.search-text").search_text
            result = tool(action.get("folder", ""), action.get("query", ""), action.get("extension", ""))
            
        else:
            result = f"Error: La herramienta '{action_name}' no está registrada en el despachador de MauCode."
            
    except Exception as error:
        result = f"Error al ejecutar la herramienta: {str(error)}"

    # 4. Mostrar el resultado de la ejecución
    console.print("\n[bold green]Resultado: >[/bold green]")
    console.print(result)
    console.print()
```

## ACTION_GUARD.PY
core\action_guard.py

```python

```

## API-CHAT.PY
core\api-chat.py

```python
import re
import importlib
from prompts.system_prompt import SYSTEM_PROMPT

# Carga dinámica de módulos con nombres kebab-case
api_manager = importlib.import_module("core.api-manager")
get_api_key_for_model = api_manager.get_api_key_for_model
make_http_request = api_manager.make_http_request


def split_inline_thinking(content: str) -> tuple[str, str]:
    """
    Extrae bloques <think>...</think> de las respuestas de los modelos.
    Retorna una tupla (thinking, contenido_limpio).
    """
    pattern = r"<think>(.*?)</think>"
    matches = re.findall(pattern, content, flags=re.DOTALL | re.IGNORECASE)    

    if not matches:
        return "", content
    
    thinking = "\n\n".join(match.strip() for match in matches)
    final_content = re.sub(
        pattern,
        "",
        content,
        flags=re.DOTALL | re.IGNORECASE,
    ).strip()

    return thinking, final_content


def ask_api_model(model_name: str, conversation_messages: list[dict]) -> dict:
    """
    Realiza la llamada de chat completion para los proveedores de API externos.
    - El usuario puede definir cualquier nombre/apodo para la plataforma API y asociar su propia API key.
    - No existen plataformas predefinidas: todo lo que aparece fue creado por el usuario.
    - Usa streaming en tiempo real para OpenAI y Groq cuando es posible.

    Parámetros:
        model_name: Nombre del modelo en formato "proveedor/modelo" (personalizado por el usuario)
        conversation_messages: Historial de mensajes de la conversación

    Retorna:
        Diccionario con 'content' y 'thinking'.
        Nota: Solo los modelos Ollama locales soportan razonamiento real (thinking=True). Los de API pueden devolver bloques <think>...</think> si el proveedor lo soporta, pero no es nativo.
    """
    provider, real_model, api_key = get_api_key_for_model(model_name)
    if not provider or not api_key:
        raise RuntimeError(f"No se encontró clave de API configurada para el modelo: {model_name}")

    # Estructuramos el historial con el prompt de sistema
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *conversation_messages
    ]

    content = ""
    
    if provider == "openai":
        content = _ask_openai_compatible(provider, real_model, api_key, messages,
                                          "https://api.openai.com/v1/chat/completions")

    elif provider == "anthropic":
        content = _ask_anthropic(real_model, api_key, conversation_messages)

    elif provider == "gemini":
        content = _ask_gemini(real_model, api_key, conversation_messages)

    elif provider == "groq":
        content = _ask_openai_compatible(provider, real_model, api_key, messages,
                                          "https://api.groq.com/openai/v1/chat/completions")

    else:
        raise RuntimeError(f"Proveedor de API no soportado: {provider}")

    # Extraemos bloques de pensamiento si existen en el contenido devuelto
    thinking, final_content = split_inline_thinking(content)
    
    return {
        "content": final_content.strip(),
        "thinking": thinking.strip(),
    }


def _ask_openai_compatible(provider: str, model: str, api_key: str,
                            messages: list[dict], url: str) -> str:
    """
    Envía la petición a una API compatible con OpenAI (OpenAI, Groq).
    Intenta streaming primero, fallback a petición estándar.
    """
    headers = {"Authorization": f"Bearer {api_key}"}
    body = {"model": model, "messages": messages}

    # Intentamos streaming primero para respuesta en tiempo real
    try:
        streaming = importlib.import_module("shell.streaming")
        streamed = streaming.stream_api_response(provider, url, headers, body)
        if streamed is not None:
            return streamed
    except Exception:
        pass

    # Fallback: petición estándar sin streaming
    _, response = make_http_request(url, headers=headers, method="POST", body_data=body)
    return response.get("choices", [{}])[0].get("message", {}).get("content", "")


def _ask_anthropic(model: str, api_key: str, conversation_messages: list[dict]) -> str:
    """
    Envía la petición a la API de Anthropic (Claude).
    Requiere extraer el system prompt a un campo raíz independiente.
    """
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    anthropic_messages = []
    system_text = SYSTEM_PROMPT
    
    for msg in conversation_messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        else:
            anthropic_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
            
    body = {
        "model": model,
        "system": system_text,
        "messages": anthropic_messages,
        "max_tokens": 4096
    }
    _, response = make_http_request(url, headers=headers, method="POST", body_data=body)
    return response.get("content", [{}])[0].get("text", "")


def _ask_gemini(model: str, api_key: str, conversation_messages: list[dict]) -> str:
    """
    Envía la petición a la API de Gemini (Google).
    Mapea los mensajes al formato de contenido esperado por Gemini.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    contents = []
    for msg in conversation_messages:
        if msg["role"] == "system":
            continue
        role = "user" if msg["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })
        
    body = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        }
    }
    _, response = make_http_request(url, method="POST", body_data=body)
    return response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
```

## API-MANAGER.PY
core\api-manager.py

```python
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
```

## I18N-MANAGER.PY
core\i18n-manager.py

```python
import locale

# Diccionario de traducciones centralizado para soporte bilingüe
TRANSLATIONS = {
    "es": {
        "select_provider_title": "Configurar Clave de API",
        "select_provider_prompt": "Selecciona el proveedor de la API:",
        "enter_key_prompt": "Ingresa la clave de API para {provider}: ",
        "empty_key_error": "[bold red]Error: La clave de API no puede estar vacía.[/bold red]",
        "testing_connection": "[bold cyan]Probando conexión con {provider}...[/bold cyan]",
        "connection_success": "[bold green]✓ ¡Conexión exitosa! Se detectaron {count} modelos en {provider}.[/bold green]",
        "connection_failed": "[bold red]✗ Error al conectar con {provider}: {error}[/bold red]",
        "invalid_key_try_again": "[yellow]La clave no es válida o falló el test de conexión. Por favor, intenta de nuevo.[/yellow]",
        "cancel_api_setup": "[bold yellow]Configuración de API cancelada.[/bold yellow]",
        "no_models_found": "[yellow]No se encontraron modelos disponibles en {provider}.[/yellow]",
        "model_selector_title": "Seleccionar modelo:",
        "model_selector_help": "↑/↓ mover - Enter confirmar - Esc/Ctrl+C cancelar",
        "model_selector_current": "(actual)",
        "model_selection_canceled": "[bold yellow]Selección de modelo cancelada.[/bold yellow]",
        "model_actual_label": "[dim]Modelo actual: {model}[/dim]",
        "warming_up": "[bold cyan]Iniciando modelo {model}...[/bold cyan]",
        "model_ready": "Modelo listo: {model}",
        "model_warm_up_error": "No se pudo iniciar el modelo: {error}",
        "provider_options": "Opciones de proveedores de API",
        "option_exit": "Volver al chat",
        
        # Nuevas traducciones para el selector visual y nombres personalizados de APIs
        "api_selector_title": "Gestión de APIs de Modelos:",
        "api_selector_help": "↑/↓ mover - Enter confirmar - Esc/Ctrl+C cancelar",
        "add_new_api_option": "[+ Agregar nueva API / Add new API]",
        "api_action_title": "Configuración de API",
        "api_action_prompt": "¿Qué deseas hacer con la API de '{name}'?",
        "api_action_delete": "Eliminar API / Delete API",
        "api_action_cancel": "Regresar / Back",
        "enter_custom_provider_prompt": "Ingresa un nombre personalizado para el proveedor de la API (ej. mi-openai): ",
        "empty_provider_error": "[bold red]Error: El nombre del proveedor no puede estar vacío.[/bold red]",
        "detect_protocol_failed": "[bold red]Error: No se pudo detectar un protocolo de comunicación válido (OpenAI, Anthropic, Gemini, Groq) para esta API key.[/bold red]",
        "api_deleted_success": "[bold green]✓ API '{name}' eliminada con éxito.[/bold green]",
        "double_ctrl_c_alert": "Presiona otra vez Ctrl+C para salir",
        "startup_subtitle": "Tu copiloto de desarrollo local",
        "startup_shortcuts_tip": "Escribe ? para atajos | / para comandos",
    },
    "en": {
        "select_provider_title": "Configure API Key",
        "select_provider_prompt": "Select the API provider:",
        "enter_key_prompt": "Enter the API key for {provider}: ",
        "empty_key_error": "[bold red]Error: The API key cannot be empty.[/bold red]",
        "testing_connection": "[bold cyan]Testing connection to {provider}...[/bold cyan]",
        "connection_success": "[bold green]✓ Connection successful! Detected {count} models in {provider}.[/bold green]",
        "connection_failed": "[bold red]✗ Error connecting to {provider}: {error}[/bold red]",
        "invalid_key_try_again": "[yellow]The key is invalid or connection test failed. Please try again.[/yellow]",
        "cancel_api_setup": "[bold yellow]API configuration canceled.[/bold yellow]",
        "no_models_found": "[yellow]No models found in {provider}.[/yellow]",
        "model_selector_title": "Select model:",
        "model_selector_help": "↑/↓ move - Enter confirm - Esc/Ctrl+C cancel",
        "model_selector_current": "(current)",
        "model_selection_canceled": "[bold yellow]Model selection canceled.[/bold yellow]",
        "model_actual_label": "[dim]Current model: {model}[/dim]",
        "warming_up": "[bold cyan]Initializing model {model}...[/bold cyan]",
        "model_ready": "Model ready: {model}",
        "model_warm_up_error": "Could not initialize model: {error}",
        "provider_options": "API provider options",
        "option_exit": "Back to chat",
        
        # New translations for custom API selector and custom naming
        "api_selector_title": "Model API Management:",
        "api_selector_help": "↑/↓ move - Enter confirm - Esc/Ctrl+C cancel",
        "add_new_api_option": "[+ Add new API / Agregar nueva API]",
        "api_action_title": "API Configuration",
        "api_action_prompt": "What do you want to do with '{name}''s API?",
        "api_action_delete": "Delete API / Eliminar API",
        "api_action_cancel": "Back / Regresar",
        "enter_custom_provider_prompt": "Enter a custom name for the API provider (e.g. my-openai): ",
        "empty_provider_error": "[bold red]Error: Provider name cannot be empty.[/bold red]",
        "detect_protocol_failed": "[bold red]Error: Could not detect a valid communication protocol (OpenAI, Anthropic, Gemini, Groq) for this API key.[/bold red]",
        "api_deleted_success": "[bold green]✓ API '{name}' deleted successfully.[/bold green]",
        "double_ctrl_c_alert": "Press Ctrl+C again to exit",
        "startup_subtitle": "Your local development copilot",
        "startup_shortcuts_tip": "Type ? for shortcuts | / for commands",
    }
}

# Idioma predeterminado del sistema
default_language = "es"

def detect_system_language() -> str:
    """
    Detecta el idioma del sistema operativo.
    Si empieza con 'es', se establece español. De lo contrario, inglés.
    """
    global default_language
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.startswith("es"):
            default_language = "es"
        else:
            default_language = "en"
    except Exception:
        default_language = "es"
    return default_language

# Ejecutar la detección al cargar el módulo
detect_system_language()

def get_text(key: str, **kwargs) -> str:
    """
    Devuelve la cadena de texto traducida según el idioma del sistema.
    Permite formatear variables en el texto devuelto.
    """
    translations_dict = TRANSLATIONS.get(default_language, TRANSLATIONS["es"])
    text_template = translations_dict.get(key, TRANSLATIONS["es"].get(key, key))
    if kwargs:
        return text_template.format(**kwargs)
    return text_template

def set_language(lang_code: str) -> None:
    """
    Permite cambiar manualmente el idioma a usar en tiempo de ejecución.
    """
    global default_language
    if lang_code in TRANSLATIONS:
        default_language = lang_code
```

## JSON_PARSER.PY
core\json_parser.py

```python
import json  # Para leer órdenes del modelo en formato JSON.
import re # Para extraer bloques JSON aunque vengan dentro de markdown.


def try_parse_json_actions(text: str):
    """
    Intenta convertir la respuesta del modelo en una lista de acciones JSON.

    Este parser es tolerante porque los modelos locales a veces responden con:
    - texto antes del JSON;
    - bloques markdown ```json;
    - varios objetos JSON consecutivos;
    - texto después del JSON.
    """

    text = text.strip()

    # Primero buscamos bloques markdown con JSON.
    fence_blocks = extract_fenced_json_blocks(text)

    if fence_blocks:
        combined_text = "\n".join(fence_blocks)
        return parse_multiple_json_objects(combined_text)

    # Si no hay bloques markdown, intentamos buscar objetos JSON en el texto plano:
    return parse_multiple_json_objects(text)



def extract_fenced_json_blocks(text: str) -> list[str]:

    """
    Extrae el contenido dentro de bloques markdown JSON.

    Ejemplo:
    ```json
    { ... }
    ```
    """

    pattern = r"```(?:json)?\s*(.*?)```"

    return re.findall(
        pattern,
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )



def parse_multiple_json_objects(text: str):
    """
    Lee uno o varios objetos JSON desde un texto.

    Si encuentra texto antes del primer JSON, avanza hasta el siguiente "{"
    para no fallar cuando el modelo agregue frases innecesarias.
    """

    decoder = json.JSONDecoder()
    actions = []
    index = 0

    text = text.strip()

    while index < len(text):

        # Saltamos espacios y saltos de línea:
        while index < len(text) and text[index].isspace():
            index += 1

        # Si hay texto antes de un JSON, buscamos el siguiente objeto.
        if index < len(text) and text[index] != "{":
            next_object_start = text.find("{", index)

            if next_object_start == -1:
                break

            index = next_object_start

        try:
            action, next_index = decoder.raw_decode(text[index:])
            actions.append(action)
            index += next_index

        except json.JSONDecodeError:
            return None
        
    if not actions:
        return None

    return actions
```

## MODEL_CLIENT.PY
core\model_client.py

```python
import ollama
import importlib
from prompts.system_prompt import SYSTEM_PROMPT

# Carga dinámica de módulos con nombres kebab-case (obligatorios por reglas del proyecto)
ollama_service = importlib.import_module("core.ollama-service")
PREFERRED_MODEL_NAME = ollama_service.PREFERRED_MODEL_NAME
MODEL_KEEP_ALIVE = ollama_service.MODEL_KEEP_ALIVE
list_local_ollama_models = ollama_service.list_installed_ollama_models
unload_local_model = ollama_service.unload_model
detect_thinking_support_for_one_model = ollama_service.detect_thinking_support_for_one_model
detect_local_thinking_support = ollama_service.detect_thinking_support_for_all_models
warm_up_local_model = ollama_service.warm_up_local_model

api_manager = importlib.import_module("core.api-manager")
get_api_models = api_manager.get_api_models
load_api_config = api_manager.load_api_config
save_api_config = api_manager.save_api_config


# Modelo actualmente seleccionado durante MauCode.
current_model_name = None

# Preferencia de thinking activada por el usuario
thinking_enabled = False

def select_default_model() -> str:
    """
    Selecciona automáticamente el mejor modelo disponible.
    Prioriza el último modelo seleccionado de la sesión anterior si está configurado y es válido.
    """
    try:
        config = load_api_config()
        settings = config.get("settings", {})
        last_model = settings.get("last_selected_model")
        if last_model:
            if "/" in last_model:
                api_models = get_api_models()
                if last_model in api_models:
                    return last_model
            else:
                installed_models = list_local_ollama_models()
                if last_model in installed_models:
                    return last_model
    except Exception:
        pass

    try:
        installed_models = list_local_ollama_models()
        if PREFERRED_MODEL_NAME in installed_models:
            return PREFERRED_MODEL_NAME
        if installed_models:
            return installed_models[0]
    except Exception:
        pass

    api_models = get_api_models()
    if api_models:
        return api_models[0]

    raise RuntimeError(
        "No hay modelos locales instalados en Ollama ni APIs configuradas.\n"
        "Instala un modelo local ('ollama pull qwen3:8b') o configura una API con '/APIs'."
    )

def initialize_model() -> str:
    """
    Inicializa el modelo activo de MauCode.
    """
    global current_model_name
    current_model_name = select_default_model()
    return current_model_name

def get_current_model() -> str:
    """
    Devuelve el modelo actualmente activo.
    """
    global current_model_name
    if current_model_name is None:
        current_model_name = select_default_model()
    return current_model_name

def set_current_model(model_name: str) -> None:
    """
    Cambia el modelo activo de MauCode durante la sesión actual y lo persiste.
    """
    global current_model_name
    global thinking_enabled

    old_model = current_model_name
    current_model_name = model_name

    # Guardamos el modelo seleccionado como el último usado de forma persistente
    try:
        config = load_api_config()
        settings = config.get("settings", {})
        settings["last_selected_model"] = model_name
        config["settings"] = settings
        save_api_config(config)
    except Exception:
        pass

    # Si cambiamos de un modelo local de Ollama a otro, descargamos el anterior
    if old_model and old_model != model_name and "/" not in old_model:
        try:
            unload_local_model(old_model)
        except Exception:
            pass

    if not model_supports_thinking(model_name):
        thinking_enabled = False


def get_thinking_enabled() -> bool:
    """
    Devuelve si el usuario activó la opción de thinking.
    """
    return thinking_enabled

def set_thinking_enabled(value: bool) -> None:
    """
    Activa o desactiva el uso de thinking en modelos compatibles.
    """
    global thinking_enabled
    thinking_enabled = value

def list_installed_ollama_models() -> list[str]:
    """
    Retorna una lista combinada de los modelos locales de Ollama y los configurados por API.
    """
    local_models = []
    try:
        local_models = list_local_ollama_models()
    except Exception:
        pass
    api_models = get_api_models()
    return local_models + api_models

def detect_thinking_support_for_all_models(models_list: list[str]) -> dict[str, bool]:
    """
    Detecta el soporte de thinking para una lista de modelos (locales y de API).
    
    - Para modelos locales de Ollama, detecta si soportan thinking realmente.
    - Para modelos de API (cualquier modelo con "/" en el nombre), siempre retorna False (ningún API soporta thinking local).
    - Esta función es usada para mostrar en la UI/CLI si cada modelo tiene acceso a thinking (True/False), independientemente de su origen.
    """
    local_models = [m for m in models_list if "/" not in m]
    api_models = [m for m in models_list if "/" in m]

    thinking_support = {}
    if local_models:
        thinking_support = detect_local_thinking_support(local_models)
    # Para todos los modelos API, explicitamente False
    for m in api_models:
        thinking_support[m] = False

    return thinking_support

def model_supports_thinking(model_name: str | None = None) -> bool:
    """
    Devuelve si el modelo indicado, o el modelo actual, soporta thinking local.
    """
    selected_model = model_name or get_current_model()
    if "/" in selected_model:
        return False
    try:
        return detect_thinking_support_for_one_model(selected_model)
    except Exception:
        return False

def get_model_thinking_label(model_name: str) -> str:
    """
    Devuelve la etiqueta visual para el selector de modelos, indicando si soporta thinking.
    
    - Si el modelo soporta thinking (solo Ollama local), muestra "[thinking]".
    - Si no, retorna cadena vacía.
    - Esto se usa para que el usuario vea claramente qué modelos tienen acceso a razonamiento avanzado.
    """
    if model_supports_thinking(model_name):
        return "    [thinking]"
    return ""

def should_use_thinking_for_chat(model_name: str | None = None) -> bool:
    """
    Devuelve True si el usuario activó thinking y el modelo lo soporta.
    """
    selected_model = model_name or get_current_model()
    return get_thinking_enabled() and model_supports_thinking(selected_model)

# Carga dinámica del módulo de chat con APIs externas (extraído por límite de 400 líneas)
api_chat = importlib.import_module("core.api-chat")
ask_api_model = api_chat.ask_api_model
split_inline_thinking = api_chat.split_inline_thinking


def ask_ollama(conversation_messages: list[dict]) -> dict:
    """
    Envía la conversación al modelo activo, redirigiendo a la API o a Ollama local.
    """
    selected_model = get_current_model()

    # Si es un modelo configurado por API, lo redirigimos
    if "/" in selected_model:
        return ask_api_model(selected_model, conversation_messages)

    # Si es local, lo procesamos con el cliente de Ollama estándar
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        *conversation_messages,
    ]

    supports_thinking = model_supports_thinking(selected_model)

    try:
        if supports_thinking:
            response = ollama.chat(
                model=selected_model,
                messages=messages,
                think=get_thinking_enabled(),
                keep_alive=MODEL_KEEP_ALIVE,
            )
        else:
            response = ollama.chat(
                model=selected_model,
                messages=messages,
                keep_alive=MODEL_KEEP_ALIVE,
            )
    except TypeError:
        response = ollama.chat(
            model=selected_model,
            messages=messages,
            keep_alive=MODEL_KEEP_ALIVE,
        )
    except Exception as error:
        if supports_thinking and "does not support thinking" in str(error).lower():
            set_thinking_enabled(False)
            response = ollama.chat(
                model=selected_model,
                messages=messages,
                keep_alive=MODEL_KEEP_ALIVE,
            )
        else:
            raise
    
    if isinstance(response, dict):
        response_message = response.get("message", {})
    else:
        response_message = getattr(response, "message", {})

    if isinstance(response_message, dict):
        content = response_message.get("content", "") or ""
        thinking = response_message.get("thinking", "") or ""
    else:
        content = getattr(response_message, "content", "") or ""
        thinking = getattr(response_message, "thinking", "") or ""

    if not thinking:
        thinking, content = split_inline_thinking(content)

    return {
        "content": content.strip(),
        "thinking": thinking.strip(),
    }

def warm_up_model(model_name: str | None = None) -> tuple[bool, str]:
    """
    Carga el modelo en memoria local si es local, o valida su disponibilidad si es de API.
    """
    selected_model = model_name or get_current_model()
    if "/" in selected_model:
        return True, f"Modelo de API listo: {selected_model}"
    
    return warm_up_local_model(selected_model)
```

## OLLAMA-SERVICE.PY
core\ollama-service.py

```python
import ollama
import re

# Nombre del modelo local preferido para thinking
PREFERRED_MODEL_NAME = "qwen3:8b"

# Tiempo que Ollama mantendrá el modelo cargado en memoria RAM/VRAM
MODEL_KEEP_ALIVE = "5m"

# Caché local para evitar volver a consultar el soporte de thinking de los modelos
model_thinking_support_cache = {}

def list_installed_ollama_models() -> list[str]:
    """
    Lee e identifica los modelos instalados localmente en la instancia de Ollama.
    """
    response = ollama.list()

    if isinstance(response, dict):
        raw_models = response.get("models", [])
    else:
        raw_models = getattr(response, "models", [])

    installed_models = []
    for model in raw_models:
        if isinstance(model, dict):
            model_name = model.get("model") or model.get("name")
        else:
            model_name = getattr(model, "model", None) or getattr(model, "name", None)

        if model_name:
            installed_models.append(model_name)

    return installed_models

def unload_model(model_name: str) -> tuple[bool, str]:
    """
    Descarga un modelo específico de la memoria de Ollama para liberar recursos.
    """
    try:
        ollama.generate(
            model=model_name,
            prompt="",
            keep_alive=0,
            options={
                "num_predict": 0,
            },
        )
        return True, f"Modelo local descargado: {model_name}"
    except Exception as error:
        return False, f"No se pudo descargar el modelo local {model_name}: {error}"

def is_thinking_not_supported_error(error: Exception) -> bool:
    """
    Detecta si el error devuelto por Ollama indica falta de soporte para thinking.
    """
    error_text = str(error).lower()
    return (
        "does not support thinking" in error_text
        or "thinking is not supported" in error_text
        or "think is not supported" in error_text
    )

def detect_thinking_support_for_one_model(model_name: str, force: bool = False) -> bool:
    """
    Detecta si un modelo local soporta el parámetro think de Ollama.
    """
    if not force and model_name in model_thinking_support_cache:
        return model_thinking_support_cache[model_name]

    try:
        ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": "Responde solo: OK",
                }
            ],
            think=True,
            options={
                "num_predict": 1,
            },
            keep_alive=0,
        )
        model_thinking_support_cache[model_name] = True
        return True
    except TypeError:
        model_thinking_support_cache[model_name] = False
        return False
    except Exception as error:
        if is_thinking_not_supported_error(error):
            model_thinking_support_cache[model_name] = False
            return False
        raise

def detect_thinking_support_for_all_models(models_list: list[str]) -> dict[str, bool]:
    """
    Detecta el soporte de thinking para un conjunto de modelos.
    """
    thinking_support_by_model = {}
    for model_name in models_list:
        try:
            thinking_support_by_model[model_name] = detect_thinking_support_for_one_model(model_name)
        except Exception:
            thinking_support_by_model[model_name] = False
    return thinking_support_by_model

def warm_up_local_model(model_name: str) -> tuple[bool, str]:
    """
    Calienta y carga en memoria RAM/VRAM un modelo local de Ollama.
    """
    try:
        ollama.chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "Responde únicamente con ¡Hola, estoy listo!",
                },
                {
                    "role": "user",
                    "content": "OK",
                },
            ],
            options={
                "num_predict": 1,
            },
            keep_alive=MODEL_KEEP_ALIVE,
        )
        return True, f"Modelo local listo: {model_name}"
    except Exception as error:
        return False, f"No se pudo iniciar el modelo local: {error}"
```

## PERMISSIONS.PY
core\permissions.py

```python
# AQUÍ SE MANEJA EL TEMA DE PERMISOS PARA MauCode:
class PermissionSession:
    """
    Guarda permisos temporales para una sola respuesta del modelo.

    Importante:
    - No vive durante toda la ejecución de MauCode.
    - Se crea de nuevo cada vez que el usuario envía un mensaje.
    - Si el usuario elige "sí a todo", solo aplica a las acciones de
    esa respuesta específica del modelo.
    """

    def __init__(self):
        """
        Inicializa la sesión de permisos.
        
        allow_all empieza en False porque MauCode siempre debe preguntar 
        al inicio de cada nuevo mensaje del usuario.
        """

        self.allow_all = False


# Función para solicitar permisos:
def ask_tool_permission(permission_session: PermissionSession) -> bool:
    """
    Pregunta al usuario si quiere ejecutar una acción.

    Opciones:
    1. Sí: ejecuta solo esta acción.
    2. Sí a todo: ejecuta esta acción y las siguientes acciones
        de la misma respuesta del modelo.
    3. No, dime algo más: cancela esta acción.
    """

    if permission_session.allow_all:
        return True
    
    print("\n¿Qué quieres hacer?")
    print("1. Sí")
    print("2. Sí a todo")
    print("3. No, dime algo más")

    option = input("Elige una opción (1. Sí, 2. Sí a todo, 3. No, dime algo más): ").strip()

    if option == "1":
        return True
    
    if option == "2":
        permission_session.allow_all = True
        return True
    
    return False
```

