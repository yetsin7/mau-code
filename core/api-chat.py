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
