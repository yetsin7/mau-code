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
