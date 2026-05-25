from pathlib import Path

def delete_file(folder: str, file_name: str) -> str:
    """
    Elimina un archivo dentro de la carpeta indicada.
    """
    # Seguridad: Bloquear escapes de directorios
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        return "Error: Nombre de archivo no permitido o contiene rutas relativas."

    file_path = Path(folder) / file_name

    if not file_path.exists():
        return f"Error: El archivo no existe en {file_path}"

    if not file_path.is_file():
        return f"Error: {file_path} no es un archivo (puede ser una carpeta)."

    try:
        # Eliminar el archivo
        file_path.unlink()
        return f"Archivo eliminado correctamente de {file_path}"
    except Exception as error:
        return f"Error al eliminar el archivo: {str(error)}"
