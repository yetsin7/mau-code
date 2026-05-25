from pathlib import Path

# Extensiones permitidas por seguridad
ALLOWED_TEXT_EXTENSIONS = {
    ".bat", ".css", ".csv", ".dockerfile", ".env", ".gitignore",
    ".html", ".js", ".json", ".jsx", ".md", ".ps1", ".py", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml"
}

def rename_file(folder: str, old_name: str, new_name: str) -> str:
    """
    Renombra un archivo dentro de la carpeta indicada.
    """
    folder_path = Path(folder)
    old_path = folder_path / old_name
    new_path = folder_path / new_name

    # Seguridad: Bloquear escapes de directorios
    if ".." in old_name or ".." in new_name or "/" in new_name or "\\" in new_name:
        return "Error: Nombre de archivo no permitido o contiene rutas relativas."

    # Seguridad: Verificar extensión del archivo de destino
    new_extension = new_path.suffix.lower() or new_path.name.lower()
    if new_extension not in ALLOWED_TEXT_EXTENSIONS:
        return f"Error: La extensión de destino '{new_extension}' no está permitida."

    if not old_path.exists():
        return f"Error: El archivo de origen '{old_name}' no existe en {old_path}"

    if new_path.exists():
        return f"Error: El archivo de destino '{new_name}' ya existe en {new_path}"

    try:
        # Renombrar/mover localmente
        old_path.rename(new_path)
        return f"Archivo renombrado correctamente de {old_name} a {new_name}"
    except Exception as error:
        return f"Error al renombrar el archivo: {str(error)}"
