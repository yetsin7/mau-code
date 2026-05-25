from pathlib import Path

# Extensiones de texto y código permitidas por seguridad
ALLOWED_TEXT_EXTENSIONS = {
    ".bat", ".css", ".csv", ".dockerfile", ".env", ".gitignore",
    ".html", ".js", ".json", ".jsx", ".md", ".ps1", ".py", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml"
}

def create_file(folder: str, file_name: str, content: str) -> str:
    """
    Crea archivos de texto o código dentro de la carpeta indicada por el usuario.
    """
    folder_path = Path(folder)

    # Si la carpeta no existe, la creamos recursivamente
    folder_path.mkdir(parents=True, exist_ok=True)

    # Ruta completa del archivo
    file_path = folder_path / file_name

    # SEGURIDAD: Bloquear archivos peligrosos o con escapes de directorios
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        return "Error: El nombre del archivo contiene rutas no permitidas."

    # Comprobación de extensión por seguridad
    file_extension = file_path.suffix.lower() or file_path.name.lower()
    if file_extension not in ALLOWED_TEXT_EXTENSIONS:
        return f"Error: La extensión '{file_extension}' no está permitida. Solo se permiten archivos de texto o código estándar."

    try:
        # Escribimos el contenido codificado en UTF-8
        file_path.write_text(content, encoding="utf-8")
        return f"Archivo creado correctamente en {file_path}"
    except Exception as error:
        return f"Error al crear el archivo: {str(error)}"
