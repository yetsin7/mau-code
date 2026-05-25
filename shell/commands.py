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
    Importa dinámicamente y ejecuta la configuración interactiva de APIs de LLMs.
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



