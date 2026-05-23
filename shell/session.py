from shell.renderer import console  # Consola visual con Rich.
from shell.input_handler import read_user_input  # Función para leer entrada del usuario.
from core.permissions import PermissionSession

# Loop princial de la sesión:
def start_terminal_session(
    ask_ollama,
    handle_model_response,
):

    """
    Inicia la sesión principal de MauCode, dentro de la terminal.
    """

    console.print(
        "[bold green]¡Hola! Soy MauCode, tu asistente de programación senior. ¿En qué puedo ayudarte hoy?[/bold green]" 
    )

    console.print(
        "[bold yellow]Escribe 'salir' para terminar el chat.[/bold yellow]"
    )

    while True: 

        # Leer mensaje del usuario:
        message = read_user_input()

        if message.lower() == "salir":
            console.print("[bold red]¡Hasta luego![/bold red]")
            break

        # Enviar mensaje al modelo:
        response = ask_ollama(message)

        # Creamos permisos temporales para esta respuesta del modelo:
        permission_session = PermissionSession()

        # Procesar respuesta del modelo:
        handle_model_response(response, permission_session)
