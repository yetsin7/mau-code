import json  # Para leer órdenes del modelo en formato JSON.

import ollama  # Cliente para comunicarnos con Ollama.

from terminal.input_handler import read_user_input  # Entrada del usuario con Prompt Toolkit.
from terminal.renderer import console  # Consola visual con Rich.
from tools.filesystem.create_file import create_file  # Tool para crear archivos.
from terminal.session import start_terminal_session  # Loop principal de la sesión.


# Nombre exacto del modelo instalado en Ollama.
MODEL_NAME = "qwen2.5-coder:7b"


# Prompt principal del sistema.
SYSTEM_PROMPT = """
Eres MauCode, un asistente útil y amigable de programación senior.

Puedes conversar normalmente.

Si el usuario te pide crear uno o varios archivos, scripts o archivos de código, debes responder SOLO con uno o varios objetos JSON válidos, uno por archivo.
Herramientas disponibles:

{
    "action": "create_file",
    "folder": "RUTA_EXACTA_DE_LA_CARPETA",
    "file_name": "NOMBRE_DEL_ARCHIVO_CON_EXTENSION",
    "content": "TEXTO_QUE_SE_GUARDARÁ"
}

Reglas:

- No inventes la carpeta.
- Usa exactamente la carpeta que el usuario indique.
- Si el usuario no indica carpeta, pregunta cuál carpeta debe usar.
- No uses markdown cuando respondas con JSON.
- No expliques nada cuando respondas con JSON.
- Si el usuario pide código Python, usa extensión .py.
- Si el usuario pide HTML, CSS o JavaScript, usa la extensión correcta.
- Cuando el contenido sea código, conserva saltos de línea e indentación usando \\n correctamente.
- Nunca minifiques código.
- Siempre usa formato legible y profesional.
- Conserva líneas vacías entre funciones, clases y bloques.
- Usa indentación correcta de 4 espacios en Python.
- Devuelve el contenido exactamente como debería verse dentro del archivo real.
- No comprimas múltiples instrucciones en una sola línea.
- Si el usuario pide crear varios archivos, debes devolver un JSON por cada archivo.
- No omitas archivos solicitados.
- No crees solo el primer archivo.
- Cada JSON debe ser independiente.
- Si el usuario pide 4 archivos, debes responder exactamente 4 objetos JSON.
- El contenido de cada archivo debe ser completo, legible y no minificado.
- Nunca reduzcas el contenido solicitado a un ejemplo corto.
- Si el usuario proporciona contenido exacto para un archivo, debes conservarlo completo.
- No resumas, no acortes y no simplifiques el contenido del archivo.
"""


def ask_ollama(user_message: str) -> str:
    """
    Envía un mensaje del usuario al modelo de Ollama
    y devuelve únicamente el contenido textual de la respuesta.
    """

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
    )

    return response["message"]["content"]


def try_parse_json_actions(text: str):
    """
    Intenta convertir la respuesta del modelo en una lista de acciones JSON.

    Soporta:
    - un solo JSON
    - varios JSON seguidos
    - JSON envuelto en ```json ... ```
    """

    text = text.strip()

    # Algunos modelos responden con bloques markdown.
    # Quitamos el inicio ```json si existe.
    if text.startswith("```json"):
        text = text.replace("```json", "", 1).strip()

    # Quitamos el cierre ``` si existe.
    if text.endswith("```"):
        text = text[:-3].strip()

    decoder = json.JSONDecoder()
    actions = []
    index = 0

    while index < len(text):
        try:
            action, next_index = decoder.raw_decode(text[index:])
            actions.append(action)
            index += next_index

            # Saltamos espacios y saltos de línea entre varios JSON.
            while index < len(text) and text[index].isspace():
                index += 1

        except json.JSONDecodeError:
            return None

    return actions


def handle_model_response(model_response: str):
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

        # Tool: create_file
        if action.get("action") == "create_file":
            folder = action.get("folder", "")
            file_name = action.get("file_name", "")
            content = action.get("content", "")

            console.print(
                "\n[bold yellow]MauCode quiere ejecutar esta acción: >[/bold yellow]"
            )
            console.print("[cyan]Tool:[/cyan] create_file")
            console.print(f"[cyan]Carpeta:[/cyan] {folder}")
            console.print(f"[cyan]Nombre del archivo:[/cyan] {file_name}")

            confirm = input("\n¿Quieres ejecutar esta acción? (si/no): ")

            if confirm.lower() != "si":
                console.print(
                    "\n[bold red]Acción cancelada por el usuario.[/bold red]\n"
                )
                continue

            result = create_file(
                folder=folder,
                file_name=file_name,
                content=content,
            )

            console.print("\n[bold green]Resultado: >[/bold green]")
            console.print(result)
            console.print()

            continue

        # Si la acción todavía no está implementada.
        console.print("\n[bold red]La acción solicitada aún no existe. >[/bold red]")
        console.print(action)
        console.print()


if __name__ == "__main__":
    start_terminal_session(
        ask_ollama = ask_ollama, 
        handle_model_response = handle_model_response,)