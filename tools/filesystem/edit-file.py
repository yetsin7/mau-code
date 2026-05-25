from pathlib import Path

# Extensiones de texto permitidas por seguridad
ALLOWED_TEXT_EXTENSIONS = {
    ".bat", ".css", ".csv", ".dockerfile", ".env", ".gitignore",
    ".html", ".js", ".json", ".jsx", ".md", ".ps1", ".py", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml"
}

def edit_file(folder: str, file_name: str, target_text: str, replacement_text: str) -> str:
    """
    Edita un archivo reemplazando un fragmento de texto exacto (target_text)
    por uno nuevo (replacement_text).
    """
    file_path = Path(folder) / file_name

    # Seguridad: Bloquear escapes de directorios
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        return "Error: Nombre de archivo no permitido o contiene rutas relativas."

    # Seguridad: Comprobar extensión
    file_extension = file_path.suffix.lower() or file_path.name.lower()
    if file_extension not in ALLOWED_TEXT_EXTENSIONS:
        return f"Error: La extensión '{file_extension}' no está permitida para edición de texto."

    if not file_path.exists():
        return f"Error: El archivo no existe en {file_path}"

    try:
        # Leer el contenido original
        content = file_path.read_text(encoding="utf-8")

        if target_text not in content:
            return "Error: No se encontró el bloque de texto exacto a reemplazar. Verifica mayúsculas, minúsculas y espacios."

        # Reemplazar la coincidencia
        new_content = content.replace(target_text, replacement_text, 1) # Solo reemplazamos la primera coincidencia por seguridad
        
        # Guardar los cambios
        file_path.write_text(new_content, encoding="utf-8")
        return f"Archivo editado correctamente en {file_path}"
    except Exception as error:
        return f"Error al editar el archivo: {str(error)}"
