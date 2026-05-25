import subprocess
from pathlib import Path

def git_diff(workspace_folder: str, file_name: str = "") -> str:
    """
    Muestra la diferencia de cambios (git diff) en el workspace.
    Si se provee un file_name, solo muestra los cambios de ese archivo.
    """
    path = Path(workspace_folder)
    if not path.exists():
        return f"Error: La carpeta de trabajo no existe: {workspace_folder}"

    # Argumentos del comando git diff
    cmd = ["git", "diff"]
    if file_name and file_name.strip():
        clean_file = file_name.strip()
        if ".." in clean_file:
            return "Error: No se permite navegar fuera del workspace."
        cmd.append(clean_file)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(path),
            check=True
        )
        return result.stdout or "No hay diferencias de cambios en el repositorio."
    except subprocess.CalledProcessError as error:
        return f"Error al ejecutar git diff: {error.stderr or str(error)}"
    except Exception as error:
        return f"Error inesperado: {str(error)}"
