import os
import re
from pathlib import Path


# Carpeta raíz del proyecto.
# Si este script está en C:\Dev\mau-code, esta será esa carpeta.
ROOT_DIR = Path(__file__).resolve().parent

# Carpeta donde se generarán los archivos .md separados.
OUTPUT_DIR = ROOT_DIR / "ESTRUCTURA"

# Carpetas que no deben analizarse.
IGNORED_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    "ESTRUCTURA",
}

# Archivos que no deben incluirse.
IGNORED_FILES = {
    "all_files.md",
    "create-structure.py",
    "create_estructure.py",
    ".maucode_history",
}

# Extensiones permitidas.
ALLOWED_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".gitignore",
}


def get_file_extension(file_path: Path) -> str:
    """
    Devuelve la extensión lógica del archivo.

    Importante:
    pathlib y os.path.splitext no tratan .gitignore como extensión,
    por eso manejamos ese caso manualmente.
    """

    if file_path.name == ".gitignore":
        return ".gitignore"

    return file_path.suffix.lower()


def should_process(file_path: Path) -> bool:
    """
    Determina si un archivo debe incluirse en la documentación.
    """

    if file_path.name in IGNORED_FILES:
        return False

    if any(part in IGNORED_DIRS for part in file_path.parts):
        return False

    return get_file_extension(file_path) in ALLOWED_EXTENSIONS


def get_markdown_language(file_path: Path) -> str:
    """
    Devuelve el lenguaje correcto para el bloque markdown.
    """

    extension = get_file_extension(file_path)

    lang_map = {
        ".py": "python",
        ".md": "markdown",
        ".txt": "text",
        ".json": "json",
        ".toml": "toml",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".gitignore": "gitignore",
    }

    return lang_map.get(extension, "")


def make_output_file_name(relative_folder: Path) -> str:
    """
    Crea el nombre del archivo .md según la carpeta.

    Ejemplos:
    - prompts        -> prompts-structure.md
    - shell          -> shell-structure.md
    - tools/search   -> tools-search-structure.md
    - raíz del repo  -> root-structure.md
    """

    if str(relative_folder) == ".":
        return "root-structure.md"

    folder_name = "-".join(relative_folder.parts)
    folder_name = re.sub(r"[^a-zA-Z0-9_-]+", "-", folder_name)

    return f"{folder_name}-structure.md"


def collect_files_by_folder() -> dict[Path, list[Path]]:
    """
    Recorre el proyecto y agrupa los archivos por carpeta.
    """

    files_by_folder = {}

    for root, dirs, files in os.walk(ROOT_DIR):
        root_path = Path(root)

        # Evitamos recorrer carpetas ignoradas.
        dirs[:] = [
            directory
            for directory in dirs
            if directory not in IGNORED_DIRS
        ]

        for file_name in files:
            file_path = root_path / file_name

            if not should_process(file_path):
                continue

            relative_folder = file_path.parent.relative_to(ROOT_DIR)
            files_by_folder.setdefault(relative_folder, []).append(file_path)

    for folder_files in files_by_folder.values():
        folder_files.sort(key=lambda path: path.name.lower())

    return dict(
        sorted(
            files_by_folder.items(),
            key=lambda item: str(item[0]).lower(),
        )
    )


def clean_old_structure_files() -> None:
    """
    Borra archivos *-structure.md antiguos para evitar documentación vieja.
    """

    if not OUTPUT_DIR.exists():
        return

    for file_path in OUTPUT_DIR.glob("*-structure.md"):
        file_path.unlink()


def write_folder_structure_file(relative_folder: Path, files: list[Path]) -> None:
    """
    Crea un archivo markdown para una carpeta específica.
    """

    output_file_name = make_output_file_name(relative_folder)
    output_file_path = OUTPUT_DIR / output_file_name

    title = "ROOT" if str(relative_folder) == "." else str(relative_folder)

    with output_file_path.open("w", encoding="utf-8") as out:
        out.write(f"# {title}\n\n")

        for file_path in files:
            relative_path = file_path.relative_to(ROOT_DIR)
            lang = get_markdown_language(file_path)

            out.write(f"## {file_path.name.upper()}\n")
            out.write(f"{relative_path}\n\n")

            try:
                content = file_path.read_text(encoding="utf-8")

                out.write(f"```{lang}\n")
                out.write(content.rstrip())
                out.write("\n```\n\n")

            except Exception as error:
                out.write(f"*Error al leer el archivo: {error}*\n\n")



def main() -> None:
    """
    Genera una carpeta ESTRUCTURA con un archivo .md por cada carpeta del proyecto.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    clean_old_structure_files()

    files_by_folder = collect_files_by_folder()

    for relative_folder, files in files_by_folder.items():
        write_folder_structure_file(relative_folder, files)

    print(f"Éxito: ESTRUCTURA generada en {OUTPUT_DIR}")


if __name__ == "__main__":
    main()