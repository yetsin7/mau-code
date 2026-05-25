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
