import subprocess
from pathlib import Path

def git_branch(workspace_folder: str, action: str, branch_name: str = "") -> str:
    """
    Gestiona ramas de Git (listar, crear o borrar) dentro del workspace indicado.
    Las acciones permitidas son: 'list', 'create', 'delete'.
    """
    path = Path(workspace_folder)
    if not path.exists():
        return f"Error: La carpeta de trabajo no existe: {workspace_folder}"

    action = action.lower().strip()

    try:
        if action == "list":
            result = subprocess.run(
                ["git", "branch"],
                capture_output=True,
                text=True,
                cwd=str(path),
                check=True
            )
            return result.stdout or "No hay ramas locales configuradas."

        elif action == "create":
            if not branch_name or not branch_name.strip():
                return "Error: Debes proveer un nombre de rama válido para crear."
            subprocess.run(
                ["git", "branch", branch_name.strip()],
                capture_output=True,
                text=True,
                cwd=str(path),
                check=True
            )
            return f"Rama '{branch_name.strip()}' creada correctamente."

        elif action == "delete":
            if not branch_name or not branch_name.strip():
                return "Error: Debes proveer un nombre de rama válido para borrar."
            result = subprocess.run(
                ["git", "branch", "-d", branch_name.strip()],
                capture_output=True,
                text=True,
                cwd=str(path),
                check=True
            )
            return result.stdout or f"Rama '{branch_name.strip()}' eliminada correctamente."

        else:
            return f"Error: Acción '{action}' no válida. Solo se permite: list, create, delete."

    except subprocess.CalledProcessError as error:
        return f"Error al gestionar ramas de git: {error.stderr or str(error)}"
    except Exception as error:
        return f"Error inesperado: {str(error)}"
