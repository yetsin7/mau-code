# core

## ACTION_EXECUTOR.PY
core\action_executor.py

```python
from core.json_parser import try_parse_json_actions
from core.permissions import ask_tool_permission
from shell.renderer import console
from tools.filesystem.create_file import create_file



def handle_model_response(model_response: str, permission_session):
    """
    Decide si la respuesta del modelo es texto normal
    o una lista de instrucciones para ejecutar tools.
    """

    actions = try_parse_json_actions(model_response)

    # Si no se pudo interpretar como JSON, es una respuesta normal.
    if actions is None:
        console.print("\n[bold green]MauCode: >[/bold green]")
        console.print(model_response)
        console.print()
        return

    # Recorremos todas las acciones que el modelo haya solicitado.
    for action in actions:
        execute_action(action, permission_session)



def execute_action(action: dict, permission_session):
    """
    Ejecuta una acción individual devuelta por el modelo.

    Por ahora solo soporta create_file.
    En el futuro aquí podremos conectar read_file, edit_file,
    list_files, terminal, git, etc.
    """

    # Tool: create_file
    if action.get("action") == "create_file":
        execute_create_file(action, permission_session)
        return
    
    console.print("\n[bold red]La acción solicitada aún no existe. >[/bold red]")
    console.print(action)
    console.print()



def execute_create_file(action: dict, permission_session):
    """
    Ejecuta la tool create_file después de pedir permiso al usuario.
    """
         
    folder = action.get("folder", "")
    file_name = action.get("file_name", "")
    content = action.get("content", "")

    console.print(
        "\n[bold yellow]MauCode quiere ejecutar esta acción: >[/bold yellow]"
    )
    console.print("[cyan]Tool:[/cyan] create_file")
    console.print(f"[cyan]Carpeta:[/cyan] {folder}")
    console.print(f"[cyan]Nombre del archivo:[/cyan] {file_name}")

    has_permission = ask_tool_permission(permission_session)

    if not has_permission:
        console.print("\n[bold red]Acción cancelada por el usuario.[/bold red]\n")
        return

    result = create_file(
        folder=folder,
        file_name=file_name,
        content=content,
    )

    console.print("\n[bold green]Resultado: >[/bold green]")
    console.print(result)
    console.print()
```

## ACTION_GUARD.PY
core\action_guard.py

```python

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

    
    # Si no hay bloques markdown, intentamos buscar objetos JSON en el texto:
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
import ollama  # Cliente para comunicarnos con Ollama.
import re
from prompts.system_prompt import SYSTEM_PROMPT


# Modelo preferido con thinking:
PREFERRED_MODEL_NAME = "qwen3:8b"

# Tiempo que Ollama mantendrá el modelo cargado en memoria
# después de usarlo
MODEL_KEEP_ALIVE = "5m"

# Modelo actualmente seleccionado durante MauCode.
# Empieza vacío porque MauCode debe detectar los modelos instalados, y debe dar instrucciones en caso que no: 
current_model_name = None

thinking_enabled = False

# Caché de capacidades por modelo.
# True = el modelo acepta el parámetro think.
# False = el modelo no acepta thinking:
model_thinking_support_cache = {}



def list_installed_ollama_models() -> list[str]:
    """
    Lee los modelos instalados localmente en Ollama.

    MauCode no debe depender de una lista fija escrita en código.
    En su lugar, consulta Ollama y obtiene la lista real de modelos
    disponibles en la computadora del usuario.
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



def select_default_model() -> str:

    """
    Selecciona automáticamente el mejor modelo disponible.

    Regla actual:
    - Si qwen3:8b está instalado, se usa por defecto.
    - Si qwen3:8b no está instalado, se usa el primer modelo instalado.
    - Si no hay modelos instalados, se lanza un error claro.
    """

    installed_models = list_installed_ollama_models()

    if not installed_models:
        raise RuntimeError(
            "No hay modelos instalados en Ollama. Instala uno con: ollama pull qwen3:8b"
        )
    
    if PREFERRED_MODEL_NAME in installed_models:
        return PREFERRED_MODEL_NAME
    
    return installed_models[0]



def initialize_model() -> str:
    """
    Inicializa el modelo activo de MauCode.

    Esta función se llama al inicio del programa para que MauCode elija
    automáticamente un modelo antes de que el usuario mande su primer mensaje.
    """

    global current_model_name

    current_model_name = select_default_model()

    return current_model_name



def get_current_model() -> str:
    """
    Devuelve el modelo actualmente activo.

    Si todavía no hay modelo seleccionado, lo inicializa automáticamente.
    Esto evita que ask_ollama falle por no tener modelo configurado.
    """

    global current_model_name

    if current_model_name is None:
        current_model_name = select_default_model()

    return current_model_name




def unload_model(model_name: str) -> tuple[bool, str]:
    """
    Descarga un modelo de la memoria de Ollama usando keep_alive=0.

    Esto ayuda a que al cambiar de modelo no quede el anterior activo
    consumiendo memoria.
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

        return True, f"Modelo descargado: {model_name}"

    except Exception as error:
        return False, f"No se pudo descargar el modelo {model_name}: {error}"



def set_current_model(model_name: str) -> None:

    """
    Cambia el modelo activo de MauCode durante la sesión actual.

    Si había un modelo anterior distinto, intenta descargarlo de memoria.
    Si el nuevo modelo no soporta thinking, se desactiva la preferencia
    de thinking para evitar errores al chatear.
    """

    global current_model_name
    global thinking_enabled

    old_model = current_model_name

    if old_model and old_model != model_name:
        unload_model(old_model)

    current_model_name = model_name

    if not model_supports_thinking(model_name):
        thinking_enabled = False



def get_thinking_enabled() -> bool:
    """
    Devuelve si MauCode debe pedir thinking a los modelos compatibles.
    """

    return thinking_enabled



def set_thinking_enabled(value: bool) -> None:
    """
    Activa o desactiva el uso de thinking en modelos compatibles.
    """
    global thinking_enabled

    thinking_enabled = value   



def is_thinking_not_supported_error(error: Exception) -> bool:
    """
    Detecta errores de Ollama cuando un modelo no soporta thinking.

    Algunos modelos devuelven HTTP 400 si se les envía think=True.
    MauCode debe detectar eso, guardar la capacidad del modelo y seguir
    chateando normalmente sin thinking.
    """
    error_text = str (error).lower()

    return  (
        "does not support thinking" in error_text
        or "thinking is not supported" in error_text
        or "think is not supported" in error_text
    )

def detect_thinking_support_for_one_model(
        model_name: str, 
        force: bool = False,
    ) -> bool:

    """
    Detecta si un modelo específico acepta el parámetro think de Ollama.

    La prueba se guarda en caché para no repetirla innecesariamente.
    Usamos keep_alive=0 para no dejar cargados en memoria todos los
    modelos que se revisan en el selector.
    """

    if not force and model_name in model_thinking_support_cache:
        return model_thinking_support_cache[model_name]
    
    try:
        ollama.chat(
            model = model_name,
            messages = [
                {
                    "role": "user",
                    "content": "Responde solo: OK", 
                }
                
            ],
            think = True,
            options = {
                "num_predict": 1,
            },
            keep_alive = 0,
        )

        model_thinking_support_cache[model_name] = True
        return True
    
    except TypeError:
        # La versión instalada de ollama-python no acepta el parámetro think:
        model_thinking_support_cache[model_name] = False
        return False
    
    except Exception as error:
        if is_thinking_not_supported_error(error):
            model_thinking_support_cache[model_name] = False
            return False
        
        # Si el error es otro, no fingimos que el modelo no soporta thinking.
        # Dejamos que el error real suba para poder verlo:
        raise



def detect_thinking_support_for_all_models(
    model_name: list[str],
) -> dict[str, bool]:

    """
    Detecta qué modelos de una lista soportan thinking.

    Retorna un diccionario como:

    {
        "qwen3:8b": True,
        "opencoder:8b": False,
    }
    """

    thinking_support_by_model = {}

    for model_name in model_name:
        try:
            thinking_support_by_model[model_name] = detect_thinking_support_for_one_model(
                model_name
            )
            
        except Exception as error:
            # En el selector solo mostramos la etiqueta [thinking]
            # Cuando la capacidad fue confirmada correctamente:
            thinking_support_by_model[model_name] = False
        
    return thinking_support_by_model



def model_supports_thinking(model_name: str | None = None) -> bool:
    """
    Devuelve si el modelo indicado, o el modelo actual, soporta thinking.
    """
    selected_model = model_name or get_current_model()

    return detect_thinking_support_for_one_model(selected_model)

   

def get_model_thinking_label(model_name: str) -> str:
    """
    Devuelve la etiqueta visual para el selector de modelos.
    """

    if model_supports_thinking(model_name):
        return "    [thinking]"
    
    return ""


def should_use_thinking_for_chat(model_name: str | None = None) -> bool:

    """
    Devuelve True solo si:
    - el usuario activó thinking;
    - el modelo actual soporta thinking.
    """

    selected_model = model_name or get_current_model()

    return get_thinking_enabled() and model_supports_thinking(selected_model)



def split_inline_thinking(content: str) -> tuple[str, str]:
    """
    Extrae bloques <think>...</think> cuando un modelo viejo
    devuelve el razonamiento dentro del contenido principal.

    Retorna:
    - thinking
    - final_content
    """

    import os

    pattern = r"<think>(.*?)</think>"
    matches = re.findall(pattern, content, flags = re.DOTALL | re.IGNORECASE)    

    if not matches:
        return "", content
    
    thinking = "\n\n".join(match.strip() for match in matches)
    final_content = re.sub(
        pattern,
        "",
        content,
        flags = re.DOTALL | re.IGNORECASE,
    ).strip()

    return thinking, final_content



def ask_ollama(conversation_messages: list[dict]) -> dict:
    """
    Envía la conversación completa al modelo local de Ollama.

    Retorna:
    - content: respuesta final del modelo.
    - thinking: razonamiento separado, si el modelo lo soporta y está activo.
    """

    selected_model = get_current_model()

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
                model = selected_model,
                messages = messages,
                think = get_thinking_enabled(),
                keep_alive = MODEL_KEEP_ALIVE,
            )
        else:
            response = ollama.chat(
                model = selected_model,
                messages = messages,
                keep_alive = MODEL_KEEP_ALIVE,
            )

    except TypeError:
        # Compatibilidad con versiones viejas de oolama-python
        # que todavía no acepten el parámetro thinkL
        response = ollama.chat(
            model = selected_model,
            messages = messages,
            keep_alive = MODEL_KEEP_ALIVE,
        )

    except Exception as error:
        if supports_thinking and is_thinking_not_supported_error(error):
            model_thinking_support_cache[selected_model] = False
            set_thinking_enabled(False)

            response = ollama.chat(
                model = selected_model,
                messages = messages,
                keep_alive = MODEL_KEEP_ALIVE,
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

    return  {
        "content": content.strip(),
        "thinking": thinking.strip(),
    }



def warm_up_model(model_name: str | None = None) -> tuple[bool, str]:
    """
    Carga el modelo en memoria al iniciar MauCode o al cambiar de modelo.

    Si model_name viene vacío:
    - MauCode usa el modelo activo.
    - Si no hay modelo activo, selecciona automáticamente uno.
    """

    try:

        selected_model = model_name or get_current_model()

        ollama.chat(
            model = selected_model,
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
            keep_alive = MODEL_KEEP_ALIVE,
        )

        return True, f"Modelo listo: {selected_model}"
    
    except Exception as error:
        return False, f"No se pudeo iniciar el modelo: { error }"
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

