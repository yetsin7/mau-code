import os
from pathlib import Path
import fnmatch

def search_code(folder: str, pattern: str) -> str:
    """
    Busca archivos por patrón de nombre (ej: *.py, test_*) recursivamente en la carpeta.
    """
    path = Path(folder)
    if not path.exists():
        return f"Error: La carpeta indicada no existe en {folder}"

    matches = []
    max_files = 100 # Evitamos volcar miles de archivos en terminal

    try:
        for root, _, files in os.walk(str(path)):
            for file in files:
                # Comparamos el nombre del archivo con el patrón (case-insensitive)
                if fnmatch.fnmatch(file.lower(), pattern.lower()) or pattern.lower() in file.lower():
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(path)
                    matches.append(str(relative_path))
                    if len(matches) >= max_files:
                        break
            if len(matches) >= max_files:
                break

        if not matches:
            return f"No se encontraron archivos que coincidan con '{pattern}'."

        result = "\n".join(matches)
        if len(matches) >= max_files:
            result += f"\n\n[Límite alcanzado de {max_files} archivos encontrados]."
        return result
    except Exception as error:
        return f"Error al buscar archivos: {str(error)}"
