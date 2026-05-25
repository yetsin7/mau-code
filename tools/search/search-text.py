import os
from pathlib import Path

def search_text(folder: str, query: str, extension: str = "") -> str:
    """
    Busca de forma recursiva una cadena de texto (query)
    dentro de todos los archivos de texto permitidos en la carpeta.
    """
    path = Path(folder)
    if not path.exists():
        return f"Error: La carpeta indicada no existe en {folder}"

    query_lower = query.lower()
    matches = []
    max_matches = 50 # Límite para evitar volcar outputs gigantescos en terminal
    
    # Extensiones de texto permitidas
    ALLOWED_EXTENSIONS = {
        ".bat", ".css", ".csv", ".dockerfile", ".env", ".gitignore",
        ".html", ".js", ".json", ".jsx", ".md", ".ps1", ".py", ".sh",
        ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml"
    }

    try:
        for root, _, files in os.walk(str(path)):
            for file in files:
                file_path = Path(root) / file
                
                # Filtrado por extensión si el usuario lo especifica
                if extension and not file.lower().endswith(extension.lower()):
                    continue
                
                # Por seguridad, solo leemos archivos de extensiones de texto conocidas
                if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                    continue

                try:
                    # Leer archivo en UTF-8 y buscar coincidencias
                    content = file_path.read_text(encoding="utf-8")
                    if query_lower in content.lower():
                        # Extraer líneas de coincidencias
                        lines = content.splitlines()
                        for i, line in enumerate(lines):
                            if query_lower in line.lower():
                                relative_path = file_path.relative_to(path)
                                matches.append(f"{relative_path}:{i+1}: {line.strip()}")
                                if len(matches) >= max_matches:
                                    break
                except Exception:
                    # Omitir archivos corruptos o ilegibles
                    pass

                if len(matches) >= max_matches:
                    break
            if len(matches) >= max_matches:
                break

        if not matches:
            return f"No se encontraron coincidencias para '{query}'."

        matches_count = len(matches)
        result = "\n".join(matches)
        if matches_count >= max_matches:
            result += f"\n\n[Límite alcanzado de {max_matches} coincidencias]."
        return result
    except Exception as error:
        return f"Error al buscar texto: {str(error)}"
