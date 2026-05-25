from pathlib import Path

# Extensiones de texto permitidas por seguridad
ALLOWED_TEXT_EXTENSIONS = {
    ".bat", ".css", ".csv", ".dockerfile", ".env", ".gitignore",
    ".html", ".js", ".json", ".jsx", ".md", ".ps1", ".py", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml"
}

def read_file(folder: str, file_name: str) -> str:
    """
    Lee el contenido de un archivo de texto o código dentro de la carpeta indicada.
    Retorna el contenido en formato texto en UTF-8.
    """
    file_path = Path(folder) / file_name

    # Seguridad: Bloquear escapes de directorios
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        return "Error: Nombre de archivo no permitido o contiene rutas relativas."

    # Seguridad: Verificar que la extensión sea de texto
    file_extension = file_path.suffix.lower() or file_path.name.lower()
    if file_extension not in ALLOWED_TEXT_EXTENSIONS:
        return f"Error: La extensión '{file_extension}' no está permitida para lectura de texto."

    if not file_path.exists():
        return f"Error: El archivo no existe en {file_path}"

    try:
        # Leer el archivo codificado en UTF-8
        content = file_path.read_text(encoding="utf-8")
        return content
    except Exception as error:
        return f"Error al leer el archivo: {str(error)}"
