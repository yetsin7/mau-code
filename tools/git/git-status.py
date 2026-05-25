import subprocess
from pathlib import Path

def git_status(workspace_folder: str) -> str:
    """
    Ejecuta 'git status' de forma segura dentro del directorio del workspace indicado.
    """
    path = Path(workspace_folder)
    if not path.exists():
        return f"Error: La carpeta de trabajo no existe: {workspace_folder}"

    try:
        # Ejecutar el comando git status localmente
        result = subprocess.run(
            ["git", "status"],
            capture_output=True,
            text=True,
            cwd=str(path),
            check=True
        )
        return result.stdout or "Sin cambios en el repositorio."
    except subprocess.CalledProcessError as error:
        return f"Error al ejecutar git status: {error.stderr or str(error)}"
    except Exception as error:
        return f"Error inesperado: {str(error)}"
