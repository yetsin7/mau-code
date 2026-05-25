from pathlib import Path

def create_folder(parent_folder: str, folder_name: str) -> str:
    """
    Crea una carpeta (directorio) de forma recursiva dentro de la carpeta padre indicada.
    """
    # Seguridad: Bloquear escapes de directorios
    if ".." in folder_name:
        return "Error: No se permiten rutas relativas que contengan '..' por seguridad."

    target_path = Path(parent_folder) / folder_name

    try:
        # Crear la carpeta y sus padres si no existen
        target_path.mkdir(parents=True, exist_ok=True)
        return f"Carpeta creada correctamente en {target_path}"
    except Exception as error:
        return f"Error al crear la carpeta: {str(error)}"
