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

