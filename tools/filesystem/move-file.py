import shutil
from pathlib import Path

def move_file(src_folder: str, src_file_name: str, dest_folder: str, dest_file_name: str) -> str:
    """
    Mueve un archivo desde una carpeta de origen a una de destino,
    permitiendo opcionalmente renombrarlo en el proceso.
    """
    src_path = Path(src_folder) / src_file_name
    dest_path = Path(dest_folder) / dest_file_name

    # Seguridad: Bloquear escapes de rutas relativas peligrosas
    if ".." in src_file_name or ".." in dest_file_name:
        return "Error: No se permiten rutas con '..' por motivos de seguridad."

    if not src_path.exists():
        return f"Error: El archivo de origen no existe en {src_path}"

    try:
        # Asegurar que el directorio de destino exista
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Mover el archivo utilizando shutil
        shutil.move(str(src_path), str(dest_path))
        return f"Archivo movido correctamente desde {src_path} hacia {dest_path}"
    except Exception as error:
        return f"Error al mover el archivo: {str(error)}"
