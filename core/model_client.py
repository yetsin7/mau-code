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