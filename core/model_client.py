import re
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
get_api_key_for_model = api_manager.get_api_key_for_model
make_http_request = api_manager.make_http_request


# Modelo actualmente seleccionado durante MauCode.
current_model_name = None

# Preferencia de thinking activada por el usuario
thinking_enabled = False

def select_default_model() -> str:
    """
    Selecciona automáticamente el mejor modelo disponible.
    Prioriza qwen3:8b local, luego otros locales, y finalmente modelos por API.
    """
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
    Cambia el modelo activo de MauCode durante la sesión actual.
    """
    global current_model_name
    global thinking_enabled

    old_model = current_model_name
    current_model_name = model_name

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
    Los modelos de API devuelven False para la implementación de Ollama.
    """
    local_models = [m for m in models_list if "/" not in m]
    api_models = [m for m in models_list if "/" in m]

    thinking_support = {}
    if local_models:
        thinking_support = detect_local_thinking_support(local_models)
    
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
    Devuelve la etiqueta visual para el selector de modelos.
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

def split_inline_thinking(content: str) -> tuple[str, str]:
    """
    Extrae bloques <think>...</think> de las respuestas de los modelos.
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
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        body = {
            "model": real_model,
            "messages": messages
        }
        _, response = make_http_request(url, headers=headers, method="POST", body_data=body)
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

    elif provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # Anthropic requiere extraer el system prompt a un campo raíz independiente
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
            "model": real_model,
            "system": system_text,
            "messages": anthropic_messages,
            "max_tokens": 4096
        }
        _, response = make_http_request(url, headers=headers, method="POST", body_data=body)
        content = response.get("content", [{}])[0].get("text", "")

    elif provider == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{real_model}:generateContent?key={api_key}"
        
        # Mapeamos los mensajes al formato de contenido de Gemini
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
        content = response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

    elif provider == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        body = {
            "model": real_model,
            "messages": messages
        }
        _, response = make_http_request(url, headers=headers, method="POST", body_data=body)
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

    else:
        raise RuntimeError(f"Proveedor de API no soportado: {provider}")

    # Extraemos bloques de pensamiento si existen en el contenido devuelto
    thinking, final_content = split_inline_thinking(content)
    
    return {
        "content": final_content.strip(),
        "thinking": thinking.strip(),
    }

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