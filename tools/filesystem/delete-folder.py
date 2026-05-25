import shutil
from pathlib import Path

def delete_folder(folder: str) -> str:
    """
    Elimina una carpeta completa (incluyendo todo su contenido de forma recursiva).
    """
    folder_path = Path(folder)

    if not folder_path.exists():
        return f"Error: La carpeta no existe en {folder_path}"

    if not folder_path.is_dir():
        return f"Error: {folder_path} no es una carpeta."

    try:
        # Eliminar carpeta y contenidos de forma recursiva
        shutil.rmtree(str(folder_path))
        return f"Carpeta y todo su contenido eliminados correctamente de {folder_path}"
    except Exception as error:
        return f"Error al eliminar la carpeta: {str(error)}"
