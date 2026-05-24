from pathlib import Path
from rich.table import Table
from shell.renderer import console
import os


SEPARATOR = "-" * 70


def clear_terminal() -> None:
    """
    Limpia la pantalla visible de la terminal.

    Usamos cls/clear porque console.clear() no siempre limpia bien
    después de interfaces interactivas de prompt_toolkit en Windows.
    """

    command = "cls" if os.name == "nt" else "clear"
    os.system(command)

    # Limpieza extra para terminales compatibles con ANSI:
    # 2J limpia pantalla, 3J limpia scrollback, H mueve cursor al inicio.
    console.file.write("\033[2J\033[3J\033[H")
    console.file.flush()
    


def render_startup_header(
    workspace_path: Path,
    model_status: str,
    is_model_ready: bool,
) -> None:
    
    """
    Muestra la cabecera principal de MauCode al iniciar la sesión.

    Esta función solo se encarga de pintar la interfaz.
    No decide permisos, no llama al modelo y no ejecuta tools.
    """

    console.print(SEPARATOR)
    console.print("[bold]Accessing workspace:[/bold]")
    console.print()

    console.print("[bold cyan] ▐▛███▜▌[/bold cyan]   [bold]MauCode[/bold]")
    console.print("[bold cyan]▝▜█████▛▘[/bold cyan]  Local coding agent · Ollama")
    console.print(f"[bold cyan]  ▘▘ ▝▝[/bold cyan]    {workspace_path}")

    console.print()

    if is_model_ready:
        console.print(f"[bold green]✓[/bold green] {model_status}")
    else:
        console.print(f"[bold red]✗[/bold red] {model_status}")

    console.print(SEPARATOR)
    render_compact_footer()
    console.print()



def render_compact_footer() -> None:
    """
    Muestra una línea corta de ayuda debajo del prompt.

    Más adelante podemos hacer que esta línea cambie según modo,
    modelo seleccionado, permisos o workspace activo.
    """
    console.print(
        "[dim] ? for shortcuts | / for commands"
        "                 MauCode | local[/dim]"
    )


def render_shortcuts_help() -> None:
    """
    Muestra la ayuda rápida cuando el usuario presiona '?'.

    Esta pantalla no envía nada al modelo. Solo informa atajos.
    """

    console.print(SEPARATOR)

    table = Table.grid(expand = True)
    table.add_column(ratio = 1)
    table.add_column(ratio = 1)
    table.add_column(ratio = 1)

    table.add_row(
        "[bold]?[/bold] para atajos",
        "[bold]/[/bold] para comandos",
        "[bold]Ctrl+C[/bold] para salir",
    )

    table.add_row(
        "[bold]/model[/bold] cambiar modelo",
        "[bold]/help[/bold] mostrar atajos",
        "[bold]salir[/bold] cerrar MauCode",
    )

    table.add_row(
        "[bold]Ctrl+V[/bold] pegar texto",
        "[bold]↑/↓[/bold] Navegar",
        "[bold]Tab[/bold] Aceptar",
    )

    console.print(table)
    console.print(SEPARATOR)
   