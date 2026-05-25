# tools\git

## GIT-BRANCH.PY
tools\git\git-branch.py

```python
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
```

## GIT-COMMIT.PY
tools\git\git-commit.py

```python
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
```

## GIT-DIFF.PY
tools\git\git-diff.py

```python
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
```

## GIT-STATUS.PY
tools\git\git-status.py

```python
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
```

