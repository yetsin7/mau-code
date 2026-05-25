import importlib
from core.json_parser import try_parse_json_actions
from core.permissions import ask_tool_permission
from shell.renderer import console

def handle_model_response(model_response: str, permission_session) -> None:
    """
    Decide si la respuesta del modelo es texto explicativo normal
    o una lista de instrucciones en JSON para ejecutar herramientas.
    """
    actions = try_parse_json_actions(model_response)

    # Si no hay acciones JSON, imprimimos la respuesta como conversación normal
    if actions is None:
        console.print("\n[bold green]MauCode: >[/bold green]")
        console.print(model_response)
        console.print()
        return

    # Ejecutar secuencialmente cada una de las acciones solicitadas
    for action in actions:
        execute_action(action, permission_session)

def execute_action(action: dict, permission_session) -> None:
    """
    Despachador unificado que resuelve y ejecuta dinámicamente las 18 herramientas disponibles.
    Pide autorización interactiva al usuario antes de proceder a la llamada.
    """
    action_name = action.get("action", "")
    if not action_name:
        console.print("\n[bold red]Error: Acción sin propiedad 'action' válida.[/bold red]\n")
        return

    # 1. Mostrar de forma elegante todos los parámetros de la herramienta
    console.print("\n[bold yellow]MauCode quiere ejecutar esta acción: >[/bold yellow]")
    console.print(f"[cyan]Herramienta / Tool:[/cyan] {action_name}")
    for key, val in action.items():
        if key != "action" and key != "content":
            console.print(f"[cyan]{key.capitalize()}:[/cyan] {val}")
        elif key == "content":
            # Truncamos visualmente el contenido si es excesivamente largo
            content_str = str(val)
            if len(content_str) > 80:
                content_str = content_str[:80] + "..."
            console.print(f"[cyan]Contenido / Content:[/cyan] {content_str}")

    # 2. Solicitar confirmación interactiva de seguridad
    has_permission = ask_tool_permission(permission_session)
    if not has_permission:
        console.print("\n[bold red]Acción cancelada por el usuario.[/bold red]\n")
        return

    # 3. Resolución y ejecución dinámica en caliente
    result = ""
    try:
        if action_name == "create_file":
            tool = importlib.import_module("tools.filesystem.create-file").create_file
            result = tool(action.get("folder", ""), action.get("file_name", ""), action.get("content", ""))
            
        elif action_name == "read_file":
            tool = importlib.import_module("tools.filesystem.read-file").read_file
            result = tool(action.get("folder", ""), action.get("file_name", ""))
            
        elif action_name == "edit_file":
            tool = importlib.import_module("tools.filesystem.edit-file").edit_file
            result = tool(action.get("folder", ""), action.get("file_name", ""), action.get("target_text", ""), action.get("replacement_text", ""))
            
        elif action_name == "delete_file":
            tool = importlib.import_module("tools.filesystem.delete-file").delete_file
            result = tool(action.get("folder", ""), action.get("file_name", ""))
            
        elif action_name == "move_file":
            tool = importlib.import_module("tools.filesystem.move-file").move_file
            result = tool(action.get("src_folder", ""), action.get("src_file_name", ""), action.get("dest_folder", ""), action.get("dest_file_name", ""))
            
        elif action_name == "copy_file":
            tool = importlib.import_module("tools.filesystem.copy-file").copy_file
            result = tool(action.get("src_folder", ""), action.get("src_file_name", ""), action.get("dest_folder", ""), action.get("dest_file_name", ""))
            
        elif action_name == "rename_file":
            tool = importlib.import_module("tools.filesystem.rename-file").rename_file
            result = tool(action.get("folder", ""), action.get("old_name", ""), action.get("new_name", ""))
            
        elif action_name == "create_folder":
            tool = importlib.import_module("tools.filesystem.create-folder").create_folder
            result = tool(action.get("parent_folder", ""), action.get("folder_name", ""))
            
        elif action_name == "delete_folder":
            tool = importlib.import_module("tools.filesystem.delete-folder").delete_folder
            result = tool(action.get("folder", ""))
            
        elif action_name == "list_files":
            tool = importlib.import_module("tools.filesystem.list-files").list_files
            result = tool(action.get("folder", ""))
            
        elif action_name == "read_json":
            tool = importlib.import_module("tools.data.read-json").read_json
            result = tool(action.get("folder", ""), action.get("file_name", ""))
            
        elif action_name == "write_json":
            tool = importlib.import_module("tools.data.write-json").write_json
            result = tool(action.get("folder", ""), action.get("file_name", ""), action.get("content", ""))
            
        elif action_name == "git_status":
            tool = importlib.import_module("tools.git.git-status").git_status
            result = tool(action.get("workspace_folder", ""))
            
        elif action_name == "git_diff":
            tool = importlib.import_module("tools.git.git-diff").git_diff
            result = tool(action.get("workspace_folder", ""), action.get("file_name", ""))
            
        elif action_name == "git_commit":
            tool = importlib.import_module("tools.git.git-commit").git_commit
            result = tool(action.get("workspace_folder", ""), action.get("message", ""), action.get("files", None))
            
        elif action_name == "git_branch":
            tool = importlib.import_module("tools.git.git-branch").git_branch
            result = tool(action.get("workspace_folder", ""), action.get("branch_action", ""), action.get("branch_name", ""))
            
        elif action_name == "search_code":
            tool = importlib.import_module("tools.search.search-code").search_code
            result = tool(action.get("folder", ""), action.get("pattern", ""))
            
        elif action_name == "search_text":
            tool = importlib.import_module("tools.search.search-text").search_text
            result = tool(action.get("folder", ""), action.get("query", ""), action.get("extension", ""))
            
        else:
            result = f"Error: La herramienta '{action_name}' no está registrada en el despachador de MauCode."
            
    except Exception as error:
        result = f"Error al ejecutar la herramienta: {str(error)}"

    # 4. Mostrar el resultado de la ejecución
    console.print("\n[bold green]Resultado: >[/bold green]")
    console.print(result)
    console.print()
