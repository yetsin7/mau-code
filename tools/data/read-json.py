import json
from pathlib import Path

def read_json(folder: str, file_name: str) -> str:
    """
    Lee y decodifica un archivo estructurado en formato JSON.
    """
    # Seguridad: Bloquear escapes de directorios
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        return "Error: Nombre de archivo no permitido o contiene rutas relativas."

    file_path = Path(folder) / file_name

    if not file_path.suffix.lower() == ".json":
        return "Error: Solo se permite leer archivos con extensión .json."

    if not file_path.exists():
        return f"Error: El archivo no existe en {file_path}"

    try:
        # Leer y decodificar JSON en UTF-8
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=4, ensure_ascii=False)
    except Exception as error:
        return f"Error al leer el archivo JSON: {str(error)}"
