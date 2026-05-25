# tools\filesystem

## COPY-FILE.PY
tools\filesystem\copy-file.py

```python
import shutil
from pathlib import Path

# Extensiones permitidas por seguridad
ALLOWED_TEXT_EXTENSIONS = {
    ".bat", ".css", ".csv", ".dockerfile", ".env", ".gitignore",
    ".html", ".js", ".json", ".jsx", ".md", ".ps1", ".py", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml"
}

def copy_file(src_folder: str, src_file_name: str, dest_folder: str, dest_file_name: str) -> str:
    """
    Copia un archivo desde una carpeta origen hacia una carpeta destino.
    """
    src_path = Path(src_folder) / src_file_name
    dest_path = Path(dest_folder) / dest_file_name

    # Seguridad: Evitar escapes de directorios
    if ".." in src_file_name or ".." in dest_file_name:
        return "Error: No se permiten rutas relativas que contengan '..' por seguridad."

    # Seguridad: Comprobar extensión de destino
    dest_extension = dest_path.suffix.lower() or dest_path.name.lower()
    if dest_extension not in ALLOWED_TEXT_EXTENSIONS:
        return f"Error: La extensión '{dest_extension}' no está permitida para copia de texto."

    if not src_path.exists():
        return f"Error: El archivo origen no existe en {src_path}"

    try:
        # Asegurar directorio de destino
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copiar archivo
        shutil.copy2(str(src_path), str(dest_path))
        return f"Archivo copiado correctamente desde {src_path} hacia {dest_path}"
    except Exception as error:
        return f"Error al copiar el archivo: {str(error)}"
```

## CREATE-FILE.PY
tools\filesystem\create-file.py

```python
from pathlib import Path

# Extensiones de texto y código permitidas por seguridad
ALLOWED_TEXT_EXTENSIONS = {
    ".bat", ".css", ".csv", ".dockerfile", ".env", ".gitignore",
    ".html", ".js", ".json", ".jsx", ".md", ".ps1", ".py", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml"
}

def create_file(folder: str, file_name: str, content: str) -> str:
    """
    Crea archivos de texto o código dentro de la carpeta indicada por el usuario.
    """
    folder_path = Path(folder)

    # Si la carpeta no existe, la creamos recursivamente
    folder_path.mkdir(parents=True, exist_ok=True)

    # Ruta completa del archivo
    file_path = folder_path / file_name

    # SEGURIDAD: Bloquear archivos peligrosos o con escapes de directorios
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        return "Error: El nombre del archivo contiene rutas no permitidas."

    # Comprobación de extensión por seguridad
    file_extension = file_path.suffix.lower() or file_path.name.lower()
    if file_extension not in ALLOWED_TEXT_EXTENSIONS:
        return f"Error: La extensión '{file_extension}' no está permitida. Solo se permiten archivos de texto o código estándar."

    try:
        # Escribimos el contenido codificado en UTF-8
        file_path.write_text(content, encoding="utf-8")
        return f"Archivo creado correctamente en {file_path}"
    except Exception as error:
        return f"Error al crear el archivo: {str(error)}"
```

## CREATE-FOLDER.PY
tools\filesystem\create-folder.py

```python
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
```

## DELETE-FILE.PY
tools\filesystem\delete-file.py

```python
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
```

## DELETE-FOLDER.PY
tools\filesystem\delete-folder.py

```python
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
```

## EDIT-FILE.PY
tools\filesystem\edit-file.py

```python
from pathlib import Path

# Extensiones de texto permitidas por seguridad
ALLOWED_TEXT_EXTENSIONS = {
    ".bat", ".css", ".csv", ".dockerfile", ".env", ".gitignore",
    ".html", ".js", ".json", ".jsx", ".md", ".ps1", ".py", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml"
}

def edit_file(folder: str, file_name: str, target_text: str, replacement_text: str) -> str:
    """
    Edita un archivo reemplazando un fragmento de texto exacto (target_text)
    por uno nuevo (replacement_text).
    """
    file_path = Path(folder) / file_name

    # Seguridad: Bloquear escapes de directorios
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        return "Error: Nombre de archivo no permitido o contiene rutas relativas."

    # Seguridad: Comprobar extensión
    file_extension = file_path.suffix.lower() or file_path.name.lower()
    if file_extension not in ALLOWED_TEXT_EXTENSIONS:
        return f"Error: La extensión '{file_extension}' no está permitida para edición de texto."

    if not file_path.exists():
        return f"Error: El archivo no existe en {file_path}"

    try:
        # Leer el contenido original
        content = file_path.read_text(encoding="utf-8")

        if target_text not in content:
            return "Error: No se encontró el bloque de texto exacto a reemplazar. Verifica mayúsculas, minúsculas y espacios."

        # Reemplazar la coincidencia
        new_content = content.replace(target_text, replacement_text, 1) # Solo reemplazamos la primera coincidencia por seguridad
        
        # Guardar los cambios
        file_path.write_text(new_content, encoding="utf-8")
        return f"Archivo editado correctamente en {file_path}"
    except Exception as error:
        return f"Error al editar el archivo: {str(error)}"
```

## LIST-FILES.PY
tools\filesystem\list-files.py

```python
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
```

## MOVE-FILE.PY
tools\filesystem\move-file.py

```python
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
```

## READ-FILE.PY
tools\filesystem\read-file.py

```python
from pathlib import Path

# Extensiones de texto permitidas por seguridad
ALLOWED_TEXT_EXTENSIONS = {
    ".bat", ".css", ".csv", ".dockerfile", ".env", ".gitignore",
    ".html", ".js", ".json", ".jsx", ".md", ".ps1", ".py", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml"
}

def read_file(folder: str, file_name: str) -> str:
    """
    Lee el contenido de un archivo de texto o código dentro de la carpeta indicada.
    Retorna el contenido en formato texto en UTF-8.
    """
    file_path = Path(folder) / file_name

    # Seguridad: Bloquear escapes de directorios
    if ".." in file_name or "/" in file_name or "\\" in file_name:
        return "Error: Nombre de archivo no permitido o contiene rutas relativas."

    # Seguridad: Verificar que la extensión sea de texto
    file_extension = file_path.suffix.lower() or file_path.name.lower()
    if file_extension not in ALLOWED_TEXT_EXTENSIONS:
        return f"Error: La extensión '{file_extension}' no está permitida para lectura de texto."

    if not file_path.exists():
        return f"Error: El archivo no existe en {file_path}"

    try:
        # Leer el archivo codificado en UTF-8
        content = file_path.read_text(encoding="utf-8")
        return content
    except Exception as error:
        return f"Error al leer el archivo: {str(error)}"
```

## RENAME-FILE.PY
tools\filesystem\rename-file.py

```python
from pathlib import Path

# Extensiones permitidas por seguridad
ALLOWED_TEXT_EXTENSIONS = {
    ".bat", ".css", ".csv", ".dockerfile", ".env", ".gitignore",
    ".html", ".js", ".json", ".jsx", ".md", ".ps1", ".py", ".sh",
    ".sql", ".toml", ".ts", ".tsx", ".txt", ".xml", ".yaml", ".yml"
}

def rename_file(folder: str, old_name: str, new_name: str) -> str:
    """
    Renombra un archivo dentro de la carpeta indicada.
    """
    folder_path = Path(folder)
    old_path = folder_path / old_name
    new_path = folder_path / new_name

    # Seguridad: Bloquear escapes de directorios
    if ".." in old_name or ".." in new_name or "/" in new_name or "\\" in new_name:
        return "Error: Nombre de archivo no permitido o contiene rutas relativas."

    # Seguridad: Verificar extensión del archivo de destino
    new_extension = new_path.suffix.lower() or new_path.name.lower()
    if new_extension not in ALLOWED_TEXT_EXTENSIONS:
        return f"Error: La extensión de destino '{new_extension}' no está permitida."

    if not old_path.exists():
        return f"Error: El archivo de origen '{old_name}' no existe en {old_path}"

    if new_path.exists():
        return f"Error: El archivo de destino '{new_name}' ya existe en {new_path}"

    try:
        # Renombrar/mover localmente
        old_path.rename(new_path)
        return f"Archivo renombrado correctamente de {old_name} a {new_name}"
    except Exception as error:
        return f"Error al renombrar el archivo: {str(error)}"
```

