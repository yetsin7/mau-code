# shell

## COMMAND_REGISTRY.PY
shell\command_registry.py

```python
"""
Registro central de comandos internos de MauCode.

Este archivo existe para que el autocompletado y el ejecutor de comandos
usen la misma lista. Así evitamos que un comando aparezca en sugerencias
pero luego no exista al presionar Enter.
"""

INTERNAL_COMMANDS = {
    "/thinking": {
        "description": "Activar/desactivar thinking",
        "alias_of": None,
    },
    "/think": {
        "description": "Activar/desactivar thinking",
        "alias_of": "/thinking",
    },
    "/model": {
        "description": "Cambiar modelo",
        "alias_of": "/modelo",
    },
    "/modelo": {
        "description": "Cambiar modelo",
        "alias_of": None,
    },
    "/help": {
        "description": "Ayuda con atajos disponibles",
        "alias_of": "/ayuda",
    },
    "/ayuda": {
        "description": "Ayuda con atajos disponibles",
        "alias_of": None,
    },
    "/exit": {
        "description": "Cerrar MauCode",
        "alias_of": "/salir",
    },
    "/salir": {
        "description": "Cerrar MauCode",
        "alias_of": None,
    },
}



def get_command_names() -> list[str]:
    """
    Devuelve los comandos internos disponibles.

    El orden importa porque el primer comando compatible será el que
    se muestre como sugerencia principal.
    """

    return list(INTERNAL_COMMANDS.keys())



def get_command_entries() -> dict:
    """
    Devuelve el diccionario completo de comandos internos.

    Se usa para mostrar autocompletado con descripción,
    no solo el nombre del comando.
    """

    return INTERNAL_COMMANDS   



def normalize_command(command: str) -> str:
    """
    Normaliza alias de comandos.

    Ejemplo:
    /model se convierte internamente en /modelo.
    """  

    command = command.strip().lower()

    command_info = INTERNAL_COMMANDS.get(command)

    if command_info is None:
        return command
    
    alias_of = command_info.get("alias_of")

    if alias_of:
        return alias_of
    
    return command
```

## COMMANDS.PY
shell\commands.py

```python
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from shell.command_registry import normalize_command
from shell.renderer import console


from shell.terminal_ui import (
    SEPARATOR, 
    render_shortcuts_help, 
    clear_terminal,
)
from core.model_client import (
    detect_thinking_support_for_all_models,
    get_current_model,
    get_thinking_enabled,
    list_installed_ollama_models,
    model_supports_thinking,
    set_current_model,
    set_thinking_enabled,
    warm_up_model,
)



def handle_internal_command(message: str) -> bool:
    """
    Detecta y ejecuta comandos internos de MauCode.

    Retorna:
    - True si el mensaje fue un comando interno.
    - False si el mensaje debe enviarse normalmente al modelo.
    """

    command = normalize_command(message)

    if command == "/thinking":
        toggle_thinking()
        return True

    if command == "/modelo":
        open_model_selector()
        return True
    
    if command == "/ayuda":
        render_shortcuts_help()
        return True
    
    return False




def toggle_thinking() -> None:
    """
    Activa o desactiva thinking para modelos compatibles.
    """
    current_model = get_current_model()

    if not model_supports_thinking(current_model):
        set_thinking_enabled(False)

        console.print(
            f"[bold yellow]Este modelo no acepta thinking:[/bold yellow] "
            f"[cyan]{current_model}[/cyan]"
        )
        console.print("[dim]El chat continuará normalmente sin pensamiento.[/dim]")
        return

    new_value = not get_thinking_enabled()
    set_thinking_enabled(new_value)

    if new_value:
        console.print(
            f"[bold cyan]Thinking activado para: [/bold cyan]{current_model}"
        )
    else:
        console.print(
            "[bold yellow]Thinking desactivado.[/bold yellow]"
        )



def select_model_with_arrows(
    installed_models: list[str],
    current_model: str,
    thinking_support_by_model: dict[str, bool],
) -> str | None:
    """
    Muestra un selector interactivo de modelos.

    Controles:
    - Flecha arriba: modelo anterior.
    - Flecha abajo: modelo siguiente.
    - Enter: confirmar selección.
    - Esc/Ctrl+C: cancelar.
    """

    selected_index = 0

    if current_model in installed_models:
        selected_index = installed_models.index(current_model)

    key_bindings = KeyBindings()

    def move_selection_up() -> None:
        nonlocal selected_index
        selected_index = (selected_index -1) % len(installed_models)

    def move_selection_down() -> None:
        nonlocal selected_index
        selected_index = (selected_index +1) % len(installed_models)

    @key_bindings.add("up")
    def handle_up(event):
        move_selection_up()
        event.app.invalidate()
    
    @key_bindings.add("down")
    def handle_down(event):
        move_selection_down()
        event.app.invalidate()

    @key_bindings.add("enter")
    def handle_enter(event):        
        event.app.exit(result = installed_models[selected_index])

    @key_bindings.add("escape")
    def handle_escape(event):        
        event.app.exit(result = None)

    @key_bindings.add("c-c")
    def handle_ctrl_c(event):
        event.app.exit(result = None)

    def get_screen_text():
        fragments = []

        fragments.append(("class:separator", f"{SEPARATOR}\n"))
        fragments.append(("class:title", "Seleccionar modelo:\n\n"))

        for index, model_name in enumerate(installed_models):
            is_selected = index == selected_index
            is_current = model_name == current_model

            pointer = "❯" if is_selected else " "
            thinking_label = "  [thinking]" if thinking_support_by_model.get(model_name, False) else ""
            current_label = "   (actual)" if is_current else ""

            if is_selected:
                fragments.append(
                    (
                        "class:selected",
                        f"{pointer} {index + 1}. {model_name}{thinking_label}{current_label}\n", 
                    )
                )
            elif is_current:
                fragments.append(
                    (
                        "class:current",
                        f"{pointer} {index + 1}. {model_name}{thinking_label}{current_label}\n",
                    )
                )
            else:
                fragments.append(
                    (
                        "",
                        f"{pointer} {index + 1}. {model_name}{thinking_label}\n",
                    )
                )
        fragments.append(("", "\n"))
        fragments.append(
            (
                "class:help",
                "↑/↓ mover - Enter confirmar - Esc/Ctrl+C cancelar\n",
            )
        )
        fragments.append(("class:separator", SEPARATOR))

        return fragments
    
    style = Style.from_dict(
        {
            "title": "bold",
            "selected": "bold cyan",
            "current": "green",
            "help": "ansibrightblack",
            "separator": "ansibrightblack",
        }
    )

    control = FormattedTextControl(get_screen_text)

    application = Application(
        layout = Layout(
            HSplit(
                [
                    Window(
                        content = control,
                        always_hide_cursor = True,
                    )
                ]
            )
        ),
        key_bindings = key_bindings,
        style = style,
        full_screen = True,
        mouse_support = False,
    )

    return application.run()




def open_model_selector() -> None:
    """
    Abre un selector interactivo para elegir un modelo instalado.

    Usa flechas para moverse y Enter para confirmar.
    Al terminar, limpia la terminal y vuelve a mostrar la interfaz principal.
    """

    installed_models = list_installed_ollama_models()

    if not installed_models:
        console.print("[bold red]No hay modelos instalados en Ollama.[/bold red]")
        console.print("[yellow]Puedes instalar uno con:[/yellow] ollama pull qwen3:8b")
        return
    
    current_model = get_current_model()

    with console.status(
        "[bold cyan]Detectando modelos con thinking...[/bold cyan]",
        spinner = "dots",
    ):
        thinking_support_by_model = detect_thinking_support_for_all_models(installed_models)

    clear_terminal()

    selected_model = select_model_with_arrows(
        installed_models = installed_models,
        current_model = current_model,
        thinking_support_by_model = thinking_support_by_model,
    )

    if selected_model is None:
        clear_terminal()
        console.print("[bold yellow]Selección de modelo cancelada.[/bold yellow]")
        return
    
    if selected_model == current_model:
        clear_terminal()
        console.print(f"[dim]Modelo actual: {current_model}[/dim]")
        return    

    set_current_model(selected_model)

    with console.status(
        f"[bold cyan]Iniciando modelo {selected_model}...[/bold cyan]",
        spinner = "dots",
    ):
        is_ready, message = warm_up_model(selected_model)

    if is_ready:
        if thinking_support_by_model.get(selected_model, False):
            console.print(f"[bold green]✓[/bold green] {message}   .   [cyan]thinking[/cyan]")
        else:
            console.print(f"[bold green]✓[/bold green] {message}")
    else:
        console.print(f"[bold red]✗[/bold red] {message}")
```

## INPUT_HANDLER.PY
shell\input_handler.py

```python
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from shell.renderer import console  # Consola visual con Rich.
from shell.command_registry import get_command_names, get_command_entries
from shell.terminal_ui import render_shortcuts_help

import re


# Cuenta cuántas veces el usuario ha pegado texto multilínea.
pasted_text_counter = 0

# Guarda los textos pegados reales.
# La clave es el ID del paste y el valor es el texto completo.
paste_storage = {}

# Genera IDs únicos para cada bloque pegado.
paste_id_counter = 0


# Contenedor de atajos/eventos personalizados de Prompt Toolkit.
key_bindings = KeyBindings()


@key_bindings.add(Keys.BracketedPaste)
def handle_paste(event):
    """
    Detecta cuando el usuario pega texto con CTRL+V.

    Si el texto pegado tiene varias líneas:
    - guarda el contenido real en paste_storage
    - muestra solo un placeholder corto en el input

    Si el texto pegado tiene una sola línea:
    - lo inserta normalmente en el input
    """

    global pasted_text_counter
    global paste_storage
    global paste_id_counter

    # Normalizamos saltos de línea para evitar problemas en Windows.
    pasted_text = (
        event.data
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    # Calculamos cuántas líneas tiene el texto pegado.
    line_count = pasted_text.count("\n") + 1

    # Si solo es una línea, se comporta como un paste normal.
    if line_count <= 1:
        event.current_buffer.insert_text(pasted_text)
        return

    # Registramos un nuevo bloque pegado.
    pasted_text_counter += 1
    paste_id_counter += 1

    paste_id = paste_id_counter

    # Guardamos el texto real para enviarlo después al modelo.
    paste_storage[paste_id] = pasted_text

    # Esto es lo único que el usuario verá en el input.
    placeholder = f"[Paste #{paste_id} · {line_count} líneas]"

    # Insertamos el placeholder visual, no el texto real completo.
    event.current_buffer.insert_text(placeholder)



@key_bindings.add("?")
def handle_shortcuts_help(event):
    """
    Muestra la ayuda rápida cuando el usuario presiona '?'.

    Si el usuario ya escribió algo, insertamos el signo normalmente.
    Si el input está vacío, mostramos la pantalla de atajos.
    """

    if event.current_buffer.text:
        event.current_buffer.insert_text("?")
        return
    
    run_in_terminal(render_shortcuts_help)



class CommandAutoSuggest(AutoSuggest):
    """
    Muestra sugerencias fantasma para comandos internos.

    Ejemplo:
    si el usuario escribe "/mod", MauCode puede sugerir "el"
    para completar "/model".
    """

    def get_suggestion(self, buffer, document):
        """
        Devuelve la parte restante del comando sugerido.

        Solo funciona cuando el usuario está escribiendo un comando,
        es decir, cuando el texto empieza con "/".
        """
          
        text = document.text_before_cursor
    
        if not text.startswith("/"):
            return None
                
        # Si ya hay espacios, asumimos que no es un comando simple:
        if " " in text:
            return None
        
        for command in get_command_names():
            if command.startswith(text) and command != text:
                remaining_text = command[len(text):]
                return Suggestion(remaining_text)
            
        return None
        

    
# Autocompletador de comandos internos:
class CommandCompleter(Completer):
    """
    Muestra comandos internos con descripción.

    Esto permite que al escribir '/' aparezca una lista tipo Claude Code,
    usando el registro central de comandos.
    """

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        if not text.startswith("/"):
            return
        
        if " " in text:
            return
        
        for command, command_info in get_command_entries().items():
            if not command.startswith(text):
                continue

            yield Completion(
                command,
                start_position = -len(text),
                display = command,
                display_meta = command_info.get("description", ""),
            )

    


# Sesión reutilizable de Prompt Toolkit.
# Incluye historial con flechas arriba/abajo y soporte para paste custom.
session = PromptSession(
    history = FileHistory(".maucode_history"),
    key_bindings = key_bindings,
    completer = CommandCompleter(),
    auto_suggest = CommandAutoSuggest(),
    complete_while_typing = True,
)




def read_user_input() -> str:
    """
    Lee el mensaje del usuario.

    Si el mensaje contiene placeholders como:

        [Paste #1 · 245 líneas]

    los reemplaza internamente por el texto real que fue pegado.

    Esto permite que el usuario vea un input limpio, pero que MauCode
    reciba el contenido completo.
    """

    global paste_storage

    # Leemos el mensaje final del usuario.
    message = session.prompt("Tú: > ")

    # Busca placeholders generados por handle_paste().
    pattern = r"\[Paste #(\d+) · \d+ líneas\]"
    matches = re.findall(pattern, message)

    # Si no hay placeholders, devolvemos el mensaje normal.
    if not matches:
        return message

    real_message = message

    # Reemplazamos cada placeholder por su texto pegado real.
    for match in matches:
        paste_id = int(match)

        # Si por alguna razón no existe el paste, lo ignoramos.
        if paste_id not in paste_storage:
            continue

        # Regex específica para este placeholder.
        placeholder_pattern = rf"\[Paste #{paste_id} · \d+ líneas\]"

        real_message = re.sub(
            placeholder_pattern,
            lambda match: paste_storage[paste_id],        
            real_message,
            count=1,
        )

    # Limpiamos los bloques pegados después de enviar el mensaje.
    paste_storage.clear()

    return real_message
```

## PASTE_HANDLER.PY
shell\paste_handler.py

```python

```

## RENDERER.PY
shell\renderer.py

```python
from rich.console import Console  # Llamamos a Rich para hacer la terminal más bonita.


# Creamos una instancia de la consola de Rich.
console = Console()
```

## RUN_PYTHON.PY
shell\run_python.py

```python

```

## RUN_TERMINAL.PY
shell\run_terminal.py

```python

```

## SESSION.PY
shell\session.py

```python
from shell.commands import handle_internal_command
from shell.renderer import console  # Consola visual con Rich.
from shell.input_handler import read_user_input  # Función para leer entrada del usuario.
from shell.terminal_ui import clear_terminal, render_startup_header 
from shell.workspace import ask_workspace_trust, get_current_workspace
from core.permissions import PermissionSession


# Loop princial de la sesión:
def start_terminal_session(
    ask_ollama,
    handle_model_response,
    warm_up_model = None,
):

    """
    Inicia la sesión principal de MauCode, dentro de la terminal.
    """

    workspace_path = get_current_workspace()

    if not ask_workspace_trust(workspace_path):
        return
    
    # Limpiamos la consola después de confirmar:
    clear_terminal()

    is_ready = True
    model_status = "Modelo no inicializado."

    if warm_up_model is not None:
        with console.status(
            "[bold cyan]Iniciando modelo local...[/bold cyan]",
            spinner = "dots",
        ):
            is_ready, model_status = warm_up_model()

    clear_terminal()
    
    render_startup_header(
        workspace_path = workspace_path,
        model_status = model_status,
        is_model_ready = is_ready,
    )

    conversation_history = []

    while True: 

        # Leer mensaje del usuario:
        try:
            message = read_user_input()

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Sesión cerrada con Ctrl+C.[/bold yellow]")
            break

        except EOFError:
            console.print("[bold yellow]Sesión cerrada.[/bold yellow]")
            break


        # Mensajes para salir de MauCode:
        normalized_message = message.strip().lower()

        if not normalized_message:
            continue

        if normalized_message in {"salir", "exit", "quit", "/salir", "/exit", "/quit"}:            
            console.print("[bold red]¡Hasta luego![/bold red]")
            break

        # Detectamos comandos internos como /modelo.
        # Si se ejecuta un comando interno, no enviamos nada a Ollama.
        if handle_internal_command(message):
            continue

        # Guardamos el mensaje del usuario en el historial conversacional:
        conversation_history.append(
            {
                "role": "user",
                "content": message,
            }
        )

        # Enviar conversación completa al modelo:
        try:
            with console.status(
                "[bold cyan]MauCode está pensando...[/bold cyan]",
                spinner = "dots",
            ):
                model_result = ask_ollama(conversation_history)

        except KeyboardInterrupt:
            conversation_history.pop()
            console.print("\n[bold yellow]Respuesta cancelada con Ctrl+C:[/bold yellow]")
            continue

        except Exception as error:
            conversation_history.pop()
            console.print()
            console.print("[bold red]Error al consultar el modelo:[/bold red]")
            console.print(f"[red]{error}[/red]")
            console.print()
            continue

        response = model_result.get("content", "")
        thinking = model_result.get("thinking", "")

        if not response.strip():
            console.print()
            console.print("[bold yellow]El modelo respondió vacío.[/bold yellow]")
            console.print()
            continue

        if thinking:
            console.print("[dim]Thinking capturado del modelo.[/dim]")

        # Creamos permisos temporales para esta respuesta del modelo:
        permission_session = PermissionSession()

        # Procesar respuesta del modelo:
        handle_model_response(response, permission_session)

        # Guardamos la respuesta final en el historial conversacional:
        conversation_history.append(
            {
                "role": "assistant",
                "content": response,
            }
        )
```

## STREAMING.PY
shell\streaming.py

```python

```

## TERMINAL_UI.PY
shell\terminal_ui.py

```python
from pathlib import Path
from rich.table import Table
from shell.renderer import console
import os


SEPARATOR = "-" * 70


def clear_terminal() -> None:
    """
    Limpia la pantalla visible de la terminal.

    Usamos cls/clear porque console.clear() no siempre limpia bien
    después de interfaces interactivas de prompt_toolkit en Windows.
    """

    command = "cls" if os.name == "nt" else "clear"
    os.system(command)

    # Limpieza extra para terminales compatibles con ANSI:
    # 2J limpia pantalla, 3J limpia scrollback, H mueve cursor al inicio.
    console.file.write("\033[2J\033[3J\033[H")
    console.file.flush()
    


def render_startup_header(
    workspace_path: Path,
    model_status: str,
    is_model_ready: bool,
) -> None:
    
    """
    Muestra la cabecera principal de MauCode al iniciar la sesión.

    Esta función solo se encarga de pintar la interfaz.
    No decide permisos, no llama al modelo y no ejecuta tools.
    """

    console.print(SEPARATOR)
    console.print("[bold]Accessing workspace:[/bold]")
    console.print()

    console.print("[bold cyan] ▐▛███▜▌[/bold cyan]   [bold]MauCode[/bold]")
    console.print("[bold cyan]▝▜█████▛▘[/bold cyan]  Local coding agent · Ollama")
    console.print(f"[bold cyan]  ▘▘ ▝▝[/bold cyan]    {workspace_path}")

    console.print()

    if is_model_ready:
        console.print(f"[bold green]✓[/bold green] {model_status}")
    else:
        console.print(f"[bold red]✗[/bold red] {model_status}")

    console.print(SEPARATOR)
    render_compact_footer()
    console.print()



def render_compact_footer() -> None:
    """
    Muestra una línea corta de ayuda debajo del prompt.

    Más adelante podemos hacer que esta línea cambie según modo,
    modelo seleccionado, permisos o workspace activo.
    """
    console.print(
        "[dim] ? for shortcuts | / for commands"
        "                 MauCode | local[/dim]"
    )


def render_shortcuts_help() -> None:
    """
    Muestra la ayuda rápida cuando el usuario presiona '?'.

    Esta pantalla no envía nada al modelo. Solo informa atajos.
    """

    console.print(SEPARATOR)

    table = Table.grid(expand = True)
    table.add_column(ratio = 1)
    table.add_column(ratio = 1)
    table.add_column(ratio = 1)

    table.add_row(
        "[bold]?[/bold] para atajos",
        "[bold]/[/bold] para comandos",
        "[bold]Ctrl+C[/bold] para salir",
    )

    table.add_row(
        "[bold]/model[/bold] cambiar modelo",
        "[bold]/help[/bold] mostrar atajos",
        "[bold]salir[/bold] cerrar MauCode",
    )

    table.add_row(
        "[bold]Ctrl+V[/bold] pegar texto",
        "[bold]↑/↓[/bold] Navegar",
        "[bold]Tab[/bold] Aceptar",
    )

    console.print(table)
    console.print(SEPARATOR)
```

## WORKSPACE.PY
shell\workspace.py

```python
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings
from shell.renderer import console
from shell.terminal_ui import SEPARATOR


def get_current_workspace() -> Path:
    """
    Devuelve la carpeta desde donde se ejecutó MauCode.

    Si el usuario abre PowerShell en C:\\Dev\\mi-proyecto y ejecuta MauCode,
    esa carpeta será el workspace activo.
    """

    return Path.cwd().resolve()



def ask_workspace_trust(workspace_path: Path) -> bool:
    """
    Pregunta si el usuario confía en la carpeta actual.

    Enter confirma.
    N cancela.
    Ctrl+C o Esc cancelan sin traceback.
    """

    key_bindings = KeyBindings()

    @key_bindings.add(Keys.Escape)
    def cancel_with_escape(event):
        """
        Permite cancelar la pantalla incial con Esc.
        """

        event.app.exit(exception = KeyboardInterrupt)

    prompt_session = PromptSession(key_bindings = key_bindings)

    console.print(SEPARATOR)
    console.print("[bold]Acceso al espacio de trabajo:[/bold]")
    console.print()

    console.print(f"    [cyan]{workspace_path}[/cyan]")
    console.print()

    console.print("[bold]Verificación rápida de seguridad:[/bold] ¿Usted creó éste proyecto? Confía en él?")
    console.print("[dim]De lo contrario, por favor revise antes el contenido de ésta carpeta.[/dim]")
    console.print()


    console.print(
        "[dim]MauCode podrá leer, editar y ejecutar archivos aquí: "
        "solo después de tu aprovación.[/dim]"
    )
    console.print()

    console.print("[bold green]Enter[/bold green] para confirmar - [bold yellow]N[/bold yellow] para salir - [bold red]Esc/Ctrl+C[/bold red] para cancelar")
    console.print(SEPARATOR)
    

    try:
        answer = prompt_session.prompt("❯ ").strip().lower()    
        
    except (KeyboardInterrupt, EOFError):
        console.print()
        console.print("[bold yellow]Inicio cancelado.[/bold yellow]")
        return False
    
    if answer == "":
        return True
    
    if answer in {"y", "yes", "s", "si", "sí"}:
        return True
    
    console.print()
    console.print("\n[bold yellow]Inicio cancelado. No se dieron permios para este espacio de trabajo.[/bold yellow]")
    return False
```

