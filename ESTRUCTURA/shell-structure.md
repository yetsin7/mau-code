# shell

## API-COMMANDS.PY
shell\api-commands.py

```python
import importlib
from prompt_toolkit import PromptSession
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from shell.renderer import console
from shell.terminal_ui import SEPARATOR, clear_terminal

# Carga dinámica de módulos en kebab-case
i18n_manager = importlib.import_module("core.i18n-manager")
get_text = i18n_manager.get_text

api_manager = importlib.import_module("core.api-manager")
add_api_provider = api_manager.add_api_provider
get_configured_providers = api_manager.get_configured_providers
delete_api_provider = api_manager.delete_api_provider

# Estilo compartido idéntico al de selector de modelos (fondo oscuro del terminal)
SHARED_STYLE = Style.from_dict(
    {
        "title": "bold",
        "selected": "bold cyan",
        "help": "ansibrightblack",
        "separator": "ansibrightblack",
    }
)

def select_api_with_arrows(configured_apis: list[str]) -> str | None:
    """
    Muestra el selector interactivo de APIs usando las flechas del teclado.
    Idéntico al selector de modelos de MauCode.
    """
    options = ["ADD_NEW_API"] + configured_apis
    selected_index = 0

    key_bindings = KeyBindings()

    def move_selection_up() -> None:
        nonlocal selected_index
        selected_index = (selected_index - 1) % len(options)

    def move_selection_down() -> None:
        nonlocal selected_index
        selected_index = (selected_index + 1) % len(options)

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
        event.app.exit(result=options[selected_index])

    @key_bindings.add("escape")
    def handle_escape(event):        
        event.app.exit(result=None)

    @key_bindings.add("c-c")
    def handle_ctrl_c(event):
        event.app.exit(result=None)

    def get_screen_text():
        fragments = []
        fragments.append(("class:separator", f"{SEPARATOR}\n"))
        fragments.append(("class:title", f"{get_text('api_selector_title')}\n\n"))

        for index, opt in enumerate(options):
            is_selected = index == selected_index
            pointer = "❯" if is_selected else " "

            if opt == "ADD_NEW_API":
                display_name = get_text("add_new_api_option")
            else:
                display_name = f"{opt}  [API]"

            if is_selected:
                fragments.append(
                    (
                        "class:selected",
                        f"{pointer} {index + 1}. {display_name}\n", 
                    )
                )
            else:
                fragments.append(
                    (
                        "",
                        f"{pointer} {index + 1}. {display_name}\n",
                    )
                )
        fragments.append(("", "\n"))
        fragments.append(
            (
                "class:help",
                f"{get_text('api_selector_help')}\n",
            )
        )
        fragments.append(("class:separator", SEPARATOR))
        return fragments

    control = FormattedTextControl(get_screen_text)

    application = Application(
        layout=Layout(
            HSplit(
                [
                    Window(
                        content=control,
                        always_hide_cursor=True,
                    )
                ]
            )
        ),
        key_bindings=key_bindings,
        style=SHARED_STYLE,
        full_screen=True,
        mouse_support=False,
    )

    return application.run()

def select_api_action_with_arrows(api_name: str) -> str | None:
    """
    Muestra un selector interactivo por flechas para gestionar una API guardada.
    """
    options = ["EDIT", "DELETE", "BACK"]
    selected_index = 0

    key_bindings = KeyBindings()

    def move_selection_up() -> None:
        nonlocal selected_index
        selected_index = (selected_index - 1) % len(options)

    def move_selection_down() -> None:
        nonlocal selected_index
        selected_index = (selected_index + 1) % len(options)

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
        event.app.exit(result=options[selected_index])

    @key_bindings.add("escape")
    def handle_escape(event):        
        event.app.exit(result=None)

    @key_bindings.add("c-c")
    def handle_ctrl_c(event):
        event.app.exit(result=None)

    def get_screen_text():
        fragments = []
        fragments.append(("class:separator", f"{SEPARATOR}\n"))
        fragments.append(("class:title", f"{get_text('api_action_prompt', name=api_name)}\n\n"))

        for index, opt in enumerate(options):
            is_selected = index == selected_index
            pointer = "❯" if is_selected else " "

            if opt == "EDIT":
                display_name = get_text("api_action_title") + " (Editar API Key / Edit API Key)"
            elif opt == "DELETE":
                display_name = get_text("api_action_delete")
            else:
                display_name = get_text("api_action_cancel")

            if is_selected:
                fragments.append(
                    (
                        "class:selected",
                        f"{pointer} {index + 1}. {display_name}\n", 
                    )
                )
            else:
                fragments.append(
                    (
                        "",
                        f"{pointer} {index + 1}. {display_name}\n",
                    )
                )
        fragments.append(("", "\n"))
        fragments.append(
            (
                "class:help",
                f"{get_text('api_selector_help')}\n",
            )
        )
        fragments.append(("class:separator", SEPARATOR))
        return fragments

    control = FormattedTextControl(get_screen_text)

    application = Application(
        layout=Layout(
            HSplit(
                [
                    Window(
                        content=control,
                        always_hide_cursor=True,
                    )
                ]
            )
        ),
        key_bindings=key_bindings,
        style=SHARED_STYLE,
        full_screen=True,
        mouse_support=False,
    )

    return application.run()

def configure_apis() -> None:
    """
    Función de control interactivo principal para la gestión de APIs mediante menú visual.
    Utiliza PromptSession ligero e integrado en terminal para lecturas libres (sin cuadros blancos).
    """
    prompt_session = PromptSession()

    while True:
        clear_terminal()
        apis = get_configured_providers()
        
        # Muestra el selector visual controlado por flechas
        selected_choice = select_api_with_arrows(apis)
        
        if selected_choice is None:
            clear_terminal()
            console.print(get_text("cancel_api_setup"))
            return

        if selected_choice == "ADD_NEW_API":
            # Flujo de creación de una nueva API con nombre personalizado
            clear_terminal()
            console.print(SEPARATOR)
            console.print(f"[bold cyan]=== AGREGAR NUEVA API / ADD NEW API ===[/bold cyan]")
            console.print()
            
            # 1. Solicitar el nombre de la plataforma (ej. OpenAI)
            console.print(f" {get_text('enter_custom_provider_prompt')}")
            try:
                custom_name = prompt_session.prompt("Nombre de la plataforma / Platform Name: > ").strip()
            except (KeyboardInterrupt, EOFError):
                continue

            if not custom_name:
                console.print()
                console.print(get_text("empty_provider_error"))
                console.print("[dim]Presiona ENTER para continuar...[/dim]")
                try:
                    prompt_session.prompt()
                except Exception:
                    pass
                continue
            
            custom_name_clean = custom_name

            # 2. Solicitar la API key (enmascarada con asteriscos)
            console.print()
            console.print(f" {get_text('enter_key_prompt', provider=custom_name_clean)}")
            try:
                api_key = prompt_session.prompt("API Key: > ", is_password=True).strip()
            except (KeyboardInterrupt, EOFError):
                continue

            if not api_key:
                console.print()
                console.print(get_text("empty_key_error"))
                console.print("[dim]Presiona ENTER para continuar...[/dim]")
                try:
                    prompt_session.prompt()
                except Exception:
                    pass
                continue

            clear_terminal()
            
            # Spinner interactivo de carga durante la comprobación de red nativa
            with console.status(
                get_text("testing_connection", provider=custom_name_clean),
                spinner="dots",
            ):
                success, result = add_api_provider(custom_name_clean, api_key)

            if success:
                console.print()
                console.print(get_text("connection_success", provider=custom_name_clean, count=len(result)))
                console.print()
                console.print("[dim]Presiona ENTER para regresar...[/dim]")
                try:
                    prompt_session.prompt()
                except Exception:
                    pass
            else:
                # Si falló, mostramos el error
                console.print()
                console.print(get_text("connection_failed", provider=custom_name_clean, error=result))
                console.print()
                console.print("[dim]Presiona ENTER para continuar...[/dim]")
                try:
                    prompt_session.prompt()
                except Exception:
                    pass

        else:
            # Submenú visual controlado por flechas para gestionar la API seleccionada
            clear_terminal()
            action = select_api_action_with_arrows(selected_choice)

            if action == "EDIT":
                clear_terminal()
                console.print(SEPARATOR)
                console.print(f"[bold cyan]=== EDITAR API KEY: {selected_choice} ===[/bold cyan]")
                console.print()
                console.print(f" {get_text('enter_key_prompt', provider=selected_choice)}")
                try:
                    api_key = prompt_session.prompt("API Key: > ", is_password=True).strip()
                except (KeyboardInterrupt, EOFError):
                    continue

                if not api_key:
                    console.print()
                    console.print(get_text("empty_key_error"))
                    console.print("[dim]Presiona ENTER para continuar...[/dim]")
                    try:
                        prompt_session.prompt()
                    except Exception:
                        pass
                    continue

                clear_terminal()
                
                # Probar en caliente la nueva clave de API
                with console.status(
                    get_text("testing_connection", provider=selected_choice),
                    spinner="dots",
                ):
                    success, result = add_api_provider(selected_choice, api_key)

                if success:
                    console.print()
                    console.print(get_text("connection_success", provider=selected_choice, count=len(result)))
                    console.print()
                    console.print("[dim]Presiona ENTER para regresar...[/dim]")
                    try:
                        prompt_session.prompt()
                    except Exception:
                        pass
                else:
                    console.print()
                    console.print(get_text("connection_failed", provider=selected_choice, error=result))
                    console.print()
                    console.print("[dim]Presiona ENTER para continuar...[/dim]")
                    try:
                        prompt_session.prompt()
                    except Exception:
                        pass

            elif action == "DELETE":
                # Eliminar la API guardada
                if delete_api_provider(selected_choice):
                    clear_terminal()
                    console.print()
                    console.print(get_text("api_deleted_success", name=selected_choice))
                    console.print()
                    console.print("[dim]Presiona ENTER para continuar...[/dim]")
                    try:
                        prompt_session.prompt()
                    except Exception:
                        pass
```

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
    "/apis": {
        "description": "Configurar APIs de modelos",
        "alias_of": "/APIs",
    },
    "/APIs": {
        "description": "Configurar APIs de modelos",
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
import importlib
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

# Carga dinámica del gestor i18n con nombre kebab-case
i18n_manager = importlib.import_module("core.i18n-manager")
get_text = i18n_manager.get_text


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
    
    if command == "/apis":
        open_api_config()
        return True

    if command == "/APIs":
        open_api_config()
        return True
    
    if command == "/ayuda":
        render_shortcuts_help()
        return True
    
    return False


def open_api_config() -> None:
    """
    Importa y ejecuta la configuración interactiva de APIs de LLMs.

    - El usuario puede agregar cualquier plataforma API con el nombre/apodo que desee y su propia API key.
    - No existen plataformas predefinidas: todo lo que aparece fue creado por el usuario.
    - La gestión es 100% personalizada y flexible.
    """
    api_commands = importlib.import_module("shell.api-commands")
    api_commands.configure_apis()


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

    - Todos los modelos (locales y API) muestran si soportan thinking (True/False) mediante la etiqueta [thinking].
    - No existen modelos ni plataformas predefinidas: todo lo que aparece fue agregado por el usuario.
    - El usuario puede distinguir fácilmente entre modelos locales y de API, y ver si tienen acceso a razonamiento avanzado.

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
        selected_index = (selected_index - 1) % len(installed_models)

    def move_selection_down() -> None:
        nonlocal selected_index
        selected_index = (selected_index + 1) % len(installed_models)

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
        fragments.append(("class:title", f"{get_text('model_selector_title')}\n\n"))

        for index, model_name in enumerate(installed_models):
            is_selected = index == selected_index
            is_current = model_name == current_model

            pointer = "❯" if is_selected else " "
            thinking_label = "  [thinking]" if thinking_support_by_model.get(model_name, False) else ""
            current_label = f"   {get_text('model_selector_current')}" if is_current else ""

            # Etiquetado visual elegante y premium de modelos API vs Locales
            if "/" in model_name:
                provider_part, real_model_part = model_name.split("/", 1)
                display_name = f"{real_model_part}   [API: {provider_part.upper()}]"
            else:
                display_name = f"{model_name}   [LOCAL]"

            if is_selected:
                fragments.append(
                    (
                        "class:selected",
                        f"{pointer} {index + 1}. {display_name}{thinking_label}{current_label}\n", 
                    )
                )
            elif is_current:
                fragments.append(
                    (
                        "class:current",
                        f"{pointer} {index + 1}. {display_name}{thinking_label}{current_label}\n",
                    )
                )
            else:
                fragments.append(
                    (
                        "",
                        f"{pointer} {index + 1}. {display_name}{thinking_label}\n",
                    )
                )
        fragments.append(("", "\n"))
        fragments.append(
            (
                "class:help",
                f"{get_text('model_selector_help')}\n",
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
    Abre un selector interactivo para elegir un modelo instalado (local o de API).

    Usa flechas para moverse y Enter para confirmar.
    Al terminar, limpia la terminal y vuelve a mostrar la interfaz principal.
    """

    installed_models = list_installed_ollama_models()

    if not installed_models:
        console.print("[bold red]No hay modelos locales instalados en Ollama ni APIs configuradas.[/bold red]")
        console.print("[yellow]Puedes configurar una API escribiendo:[/yellow] /APIs")
        return
    
    current_model = get_current_model()

    with console.status(
        "[bold cyan]Detectando modelos compatibles...[/bold cyan]",
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
        console.print(get_text("model_selection_canceled"))
        return
    
    if selected_model == current_model:
        clear_terminal()
        console.print(get_text("model_actual_label", model=current_model))
        return    

    set_current_model(selected_model)

    with console.status(
        get_text("warming_up", model=selected_model),
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


# Estado para rastrear si el usuario ya presionó Ctrl+C una vez en el prompt vacío
ctrl_c_pressed_once = False


@key_bindings.add("c-c")
def handle_ctrl_c(event):
    """
    Controla el evento Ctrl+C en el prompt de MauCode.

    - Si hay texto en el input: borra la entrada para que el usuario pueda escribir de nuevo.
    - Si el input está vacío: la primera vez lanza una alerta pidiendo confirmación.
      La segunda vez consecutiva cierra la sesión de MauCode.
    """
    global ctrl_c_pressed_once

    import importlib
    i18n_manager = importlib.import_module("core.i18n-manager")
    get_text = i18n_manager.get_text

    # Si hay algún texto en el buffer, simplemente lo borramos
    if event.current_buffer.text.strip() or event.current_buffer.text:
        event.current_buffer.text = ""
        ctrl_c_pressed_once = False
    else:
        # Si está vacío, revisamos si es la segunda vez consecutiva
        if ctrl_c_pressed_once:
            event.app.exit(exception=KeyboardInterrupt)
        else:
            ctrl_c_pressed_once = True
            
            # Mostramos la alerta temporal abajo
            def print_alert():
                console.print(f"\n[bold yellow]{get_text('double_ctrl_c_alert')}[/bold yellow]")
                
            run_in_terminal(print_alert)


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

    global paste_storage, ctrl_c_pressed_once
    ctrl_c_pressed_once = False

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
import threading
import time
import msvcrt
from shell.commands import handle_internal_command
from shell.renderer import console  # Consola visual con Rich.
from shell.input_handler import read_user_input  # Función para leer entrada del usuario.
from shell.terminal_ui import clear_terminal, render_startup_header 
from shell.workspace import ask_workspace_trust, get_current_workspace
from core.permissions import PermissionSession


def ask_model_with_esc_cancel(ask_ollama_func, conversation_history) -> dict:
    """
    Ejecuta la consulta al modelo en un hilo de fondo y escucha la tecla Esc en Windows
    para cancelar la generación en caliente de forma inmediata sin bloquear el terminal.
    """
    model_result = {}
    exception_raised = None
    
    def run_query():
        nonlocal model_result, exception_raised
        try:
            model_result = ask_ollama_func(conversation_history)
        except Exception as e:
            exception_raised = e

    thread = threading.Thread(target=run_query)
    thread.daemon = True
    thread.start()

    # Bucle de espera no bloqueante
    while thread.is_alive():
        # En Windows, detectamos si se pulsó una tecla sin detener el flujo principal
        if msvcrt.kbhit():
            key = msvcrt.getch()
            # Esc en Windows se representa por el byte b'\x1b'
            if key == b'\x1b':
                # Consumimos cualquier otra tecla en cola del búfer
                while msvcrt.kbhit():
                    msvcrt.getch()
                return {"content": "", "thinking": "", "canceled": True}
        
        time.sleep(0.05)

    if exception_raised:
        raise exception_raised

    return model_result



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
                model_result = ask_model_with_esc_cancel(ask_ollama, conversation_history)

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
        canceled = model_result.get("canceled", False)

        if canceled:
            conversation_history.pop()
            console.print()
            console.print("[bold yellow]Generación cancelada por el usuario con Esc.[/bold yellow]")
            console.print()
            continue

        if not response.strip():
            conversation_history.pop()
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
import json
import urllib.request
import urllib.error
from shell.renderer import console


def stream_openai_response(url: str, headers: dict, body: dict) -> str:
    """
    Realiza una petición de streaming (SSE) a una API compatible con OpenAI.
    Imprime los tokens en tiempo real y retorna el contenido completo acumulado.

    Parámetros:
        url: Endpoint de chat completions
        headers: Headers HTTP incluyendo Authorization
        body: Cuerpo JSON de la petición (se le agrega stream=True)

    Retorna:
        El texto completo generado por el modelo.
    """
    body["stream"] = True

    req = urllib.request.Request(url, method="POST")
    req.data = json.dumps(body).encode("utf-8")
    req.add_header("Content-Type", "application/json")
    for key, value in headers.items():
        req.add_header(key, value)

    accumulated_content = ""

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            buffer = ""

            for raw_chunk in response:
                chunk = raw_chunk.decode("utf-8")
                buffer += chunk

                # Procesamos líneas SSE completas del buffer
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()

                    if not line:
                        continue

                    # Fin del stream según la especificación SSE de OpenAI
                    if line == "data: [DONE]":
                        break

                    if not line.startswith("data: "):
                        continue

                    json_str = line[6:]  # Removemos el prefijo "data: "

                    try:
                        data = json.loads(json_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        token = delta.get("content", "")

                        if token:
                            console.print(token, end="")
                            accumulated_content += token

                    except json.JSONDecodeError:
                        continue

    except urllib.error.HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
            parsed_error = json.loads(error_body)
            error_message = parsed_error.get("error", {}).get("message", error.reason)
        except Exception:
            error_message = str(error.reason)
        raise RuntimeError(f"Error de API durante streaming: {error_message}")

    except urllib.error.URLError as error:
        raise RuntimeError(f"Error de red/conexión durante streaming: {error.reason}")

    # Salto de línea final después del stream
    console.print()

    return accumulated_content


def stream_api_response(provider: str, url: str, headers: dict, body: dict) -> str:
    """
    Selecciona la estrategia de streaming correcta según el proveedor.
    Actualmente soporta streaming para APIs compatibles con OpenAI (OpenAI, Groq).

    Parámetros:
        provider: Protocolo del proveedor (openai, groq, anthropic, gemini)
        url: URL del endpoint de chat
        headers: Headers HTTP
        body: Cuerpo de la petición

    Retorna:
        El texto completo generado.
    """
    # OpenAI y Groq usan el mismo protocolo SSE
    if provider in ("openai", "groq"):
        return stream_openai_response(url, headers, body)

    # Anthropic y Gemini no soportan streaming con urllib por ahora
    # Se retorna None para que el caller use la petición normal
    return None
```

## TERMINAL_UI.PY
shell\terminal_ui.py

```python
import importlib
from pathlib import Path
from rich.table import Table
from shell.renderer import console
import os

# Carga dinámica del gestor i18n
i18n_manager = importlib.import_module("core.i18n-manager")
get_text = i18n_manager.get_text

SEPARATOR = "─" * 60


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

    console.print()
    console.print(f"[dim]{SEPARATOR}[/dim]")
    console.print()
    
    # Logo: MauCode compacto, limpio y profesional
    console.print("[bold #06B6D4]███╗   ███╗ █████╗ ██╗   ██╗[/bold #06B6D4]\t[bold #06B6D4] ██████╗ ██████╗ ██████╗ ███████╗[/bold #06B6D4]")
    console.print("[bold #0891B2]████╗ ████║██╔══██╗██║   ██║[/bold #0891B2]\t[bold #0891B2]██╔════╝██╔═══██╗██╔══██╗██╔════╝[/bold #0891B2]")
    console.print("[bold #0E7490]██╔████╔██║███████║██║   ██║[/bold #0E7490]\t[bold #0E7490]██║     ██║   ██║██║  ██║█████╗  [/bold #0E7490]")
    console.print("[bold #22D3EE]██║╚██╔╝██║██╔══██║╚██████╔╝[/bold #22D3EE]\t[bold #22D3EE]╚██████╗╚██████╔╝██████╔╝███████╗[/bold #22D3EE]")

    console.print("[dim italic]{subtitle}[/dim italic]".format(subtitle=get_text('startup_subtitle')))
    console.print("[dim]📂 {workspace}[/dim]".format(workspace=workspace_path))
    console.print(
        "[bold #34D399]Grow[/bold #34D399] "
        "[dim]→[/dim] "
        "[bold #22D3EE]Code[/bold #22D3EE] "
        "[dim]→[/dim] "
        "[bold #A78BFA]Ship[/bold #A78BFA]  "
        "[dim]{tip}[/dim]".format(tip=get_text('startup_shortcuts_tip'))
    )

    console.print()

    if is_model_ready:
        console.print(f"  [bold green]●[/bold green] {model_status}")
    else:
        console.print(f"  [bold red]○[/bold red] {model_status}")

    console.print()
    console.print(f"[dim]{SEPARATOR}[/dim]")
    render_compact_footer()
    console.print()



def render_compact_footer() -> None:
    """
    Muestra una línea corta de ayuda debajo del prompt.

    Más adelante podemos hacer que esta línea cambie según modo,
    modelo seleccionado, permisos o workspace activo.
    """
    console.print(
        "[dim]  ? atajos  ·  / comandos  ·  Ctrl+C salir"
        "                         [bold]MauCode[/bold][/dim]"
    )


def render_shortcuts_help() -> None:
    """
    Muestra la ayuda rápida cuando el usuario presiona '?'.

    Esta pantalla no envía nada al modelo. Solo informa atajos.
    """

    console.print(f"[dim]{SEPARATOR}[/dim]")

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
        "[bold]/APIs[/bold] gestionar claves",
        "[bold]Esc[/bold] cancelar generación",
    )

    table.add_row(
        "[bold]Ctrl+V[/bold] pegar texto",
        "[bold]↑/↓[/bold] historial",
        "[bold]Tab[/bold] autocompletar",
    )

    console.print(table)
    console.print(f"[dim]{SEPARATOR}[/dim]")
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

