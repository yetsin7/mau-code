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
