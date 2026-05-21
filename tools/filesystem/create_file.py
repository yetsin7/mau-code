# Esta tool es la que trabaja con rutas, carpetas y archivos.
from pathlib import Path

ALLOWED_TEXT_EXTENSIONS = {
    ".bat", 
    ".css", 
    ".csv",
    ".dockerfile",
    ".env",
    ".gitignore",
    ".html",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".sql",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
    }

# Función para crear archivo.
def create_file(folder: str, file_name: str, content: str) -> str:
    """
    Crea archivos de texto o código
    dentro de la carpeta indicada por el usuario.
    """

    folder_path = Path(folder)

    # Si la carpeta no existe, la creamos.
    folder_path.mkdir(parents=True, exist_ok=True)

    # Creamos la ruta completa del archivo:
    file_path = folder_path / file_name

    # SEGURIDAD: Bloquear archivos peligrosos o con extensiones no permitidas:
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        return "Error: El nombre del archivo contiene rutas no permitidas."

    # Aquí es para las extensiones de texto, por seguridad. Si no es una extensión permitida, no lo creamos.
    file_extension = file_path.suffix.lower() or file_path.name.lower()  # Si no tiene extensión, usamos el nombre completo para verificar.

    # Por seguridad, por ahora solo permitimos archivos .txt.
    if file_extension not in ALLOWED_TEXT_EXTENSIONS:
        return f"Error: La extensión '{file_extension}' no está permitida. Solo se permiten los siguientes tipos de archivo: {', '.join(ALLOWED_TEXT_EXTENSIONS)}"


    # Guardamos el archivo con el contenido.
    file_path.write_text(content, encoding="utf-8")

    return f"Archivo creado correctamente en {file_path}"

