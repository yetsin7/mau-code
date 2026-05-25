import shutil
from pathlib import Path

# Extensiones permitidas por seguridad
ALLOWED_TEXT_EXTENSIONS = {
    ".bat", ".css", ".csv", ".dockerfile", ".env", ".gitignore",
    ".html", ".js", ".json", ".jsx", ".md", ".ps1", ".py", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml"
}

def copy_file(src_folder: str, src_file_name: str, dest_folder: str, dest_file_name: str) -> str:
    """
    Copia un archivo desde una carpeta origen hacia una carpeta destino.
    """
    src_path = Path(src_folder) / src_file_name
    dest_path = Path(dest_folder) / dest_file_name

    # Seguridad: Evitar escapes de directorios
    if ".." in src_file_name or ".." in dest_file_name:
        return "Error: No se permiten rutas relativas que contengan '..' por seguridad."

    # Seguridad: Comprobar extensión de destino
    dest_extension = dest_path.suffix.lower() or dest_path.name.lower()
    if dest_extension not in ALLOWED_TEXT_EXTENSIONS:
        return f"Error: La extensión '{dest_extension}' no está permitida para copia de texto."

    if not src_path.exists():
        return f"Error: El archivo origen no existe en {src_path}"

    try:
        # Asegurar directorio de destino
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copiar archivo
        shutil.copy2(str(src_path), str(dest_path))
        return f"Archivo copiado correctamente desde {src_path} hacia {dest_path}"
    except Exception as error:
        return f"Error al copiar el archivo: {str(error)}"
