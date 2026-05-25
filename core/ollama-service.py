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
