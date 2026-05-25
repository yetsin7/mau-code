import subprocess
from pathlib import Path

def git_commit(workspace_folder: str, message: str, files: list = None) -> str:
    """
    Agrega archivos a revisión ('git add') y realiza el commit correspondiente en el workspace.
    Si files es None o vacío, agrega todos los cambios pendientes ('git add .').
    """
    path = Path(workspace_folder)
    if not path.exists():
        return f"Error: La carpeta de trabajo no existe: {workspace_folder}"

    if not message or not message.strip():
        return "Error: El mensaje de commit no puede estar vacío."

    try:
        # 1. Agregar archivos (git add)
        if files:
            # Limpiamos nombres de archivos para seguridad
            files_clean = [f.strip() for f in files if f and f.strip() and ".." not in f]
            if not files_clean:
                return "Error: No se indicaron archivos válidos para agregar."
            subprocess.run(
                ["git", "add"] + files_clean,
                capture_output=True,
                text=True,
                cwd=str(path),
                check=True
            )
            add_result = f"Archivos agregados: {', '.join(files_clean)}"
        else:
            subprocess.run(
                ["git", "add", "."],
                capture_output=True,
                text=True,
                cwd=str(path),
                check=True
            )
            add_result = "Todos los archivos agregados."

        # 2. Hacer commit (git commit)
        commit_result = subprocess.run(
            ["git", "commit", "-m", message.strip()],
            capture_output=True,
            text=True,
            cwd=str(path),
            check=True
        )

        return f"{add_result}\nCommit exitoso:\n{commit_result.stdout}"

    except subprocess.CalledProcessError as error:
        return f"Error en git: {error.stderr or str(error)}"
    except Exception as error:
        return f"Error inesperado al hacer commit: {str(error)}"
