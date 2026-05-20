# Esta tool es la que trabaja con rutas, carpetas y archivos.
from pathlib import Path

def crear_archivo_texto(carpeta: str, nombre_archivo: str, contenido: str) -> str:
    """
    Crea un archivo de texto .txt
    en la carpeta indicada por el usuario.
    """

    ruta_carpeta = Path(carpeta)

    # Si la carpeta no existe, la creamos.
    ruta_carpeta.mkdir(parents=True, exist_ok=True)

    # Creamos la ruta completa del archivo:
    ruta_archivo = ruta_carpeta / nombre_archivo

    # Por seguridad, por ahora solo permitimos archivos .txt.
    if ruta_archivo.suffix.lower() != ".txt":
        return "Error: Por ahora, solo puedo crear archivos de texto .txt"

    # Guardamos el archivo con el contenido.
    ruta_archivo.write_text(contenido, encoding="utf-8")

    return f"Archivo creado correctamente en {ruta_archivo}"

