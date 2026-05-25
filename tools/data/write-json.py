import json
from pathlib import Path

def write_json(folder: str, file_name: str, content: str) -> str:
    """
    Codifica y escribe datos estructurados en formato JSON.
    El parámetro content debe ser una cadena JSON válida.
    """
    # Seguridad: Bloquear escapes de directorios
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        return "Error: Nombre de archivo no permitido o contiene rutas relativas."

    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)

    file_path = folder_path / file_name

    if not file_path.suffix.lower() == ".json":
        return "Error: Solo se permite escribir archivos con extensión .json."

    try:
        # Validamos que el contenido sea JSON decodificable
        parsed_data = json.loads(content)
        
        # Guardamos el JSON formateado de forma legible en UTF-8
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=4, ensure_ascii=False)
            
        return f"Archivo JSON creado correctamente en {file_path}"
    except json.JSONDecodeError:
        return "Error: El contenido provisto no es una cadena JSON válida."
    except Exception as error:
        return f"Error al escribir el archivo JSON: {str(error)}"
