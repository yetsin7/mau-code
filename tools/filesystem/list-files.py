from pathlib import Path

def list_files(folder: str) -> str:
    """
    Enúmera todos los archivos y carpetas dentro de la carpeta indicada por el usuario.
    """
    folder_path = Path(folder)

    if not folder_path.exists():
        return f"Error: La carpeta no existe en {folder_path}"

    if not folder_path.is_dir():
        return f"Error: {folder_path} no es un directorio válido."

    try:
        entries = []
        # Listamos los elementos del directorio
        for path in folder_path.iterdir():
            entry_type = "[DIR] " if path.is_dir() else "[FILE]"
            entries.append(f"{entry_type} {path.name}")
        
        if not entries:
            return f"La carpeta en {folder_path} está vacía."

        entries.sort()
        return "\n".join(entries)
    except Exception as error:
        return f"Error al listar archivos: {str(error)}"
