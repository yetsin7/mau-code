import importlib
from pathlib import Path
from rich.table import Table
from shell.renderer import console
import os

# Carga dinámica del gestor i18n
i18n_manager = importlib.import_module("core.i18n-manager")
get_text = i18n_manager.get_text

SEPARATOR = "─" * 60


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

    console.print()
    console.print(f"[dim]{SEPARATOR}[/dim]")
    console.print()
    
    # Logo: MauCode compacto, limpio y profesional
    console.print("[bold #06B6D4]███╗   ███╗ █████╗ ██╗   ██╗[/bold #06B6D4]\t[bold #06B6D4] ██████╗ ██████╗ ██████╗ ███████╗[/bold #06B6D4]")
    console.print("[bold #0891B2]████╗ ████║██╔══██╗██║   ██║[/bold #0891B2]\t[bold #0891B2]██╔════╝██╔═══██╗██╔══██╗██╔════╝[/bold #0891B2]")
    console.print("[bold #0E7490]██╔████╔██║███████║██║   ██║[/bold #0E7490]\t[bold #0E7490]██║     ██║   ██║██║  ██║█████╗  [/bold #0E7490]")
    console.print("[bold #22D3EE]██║╚██╔╝██║██╔══██║╚██████╔╝[/bold #22D3EE]\t[bold #22D3EE]╚██████╗╚██████╔╝██████╔╝███████╗[/bold #22D3EE]")

    console.print("[dim italic]{subtitle}[/dim italic]".format(subtitle=get_text('startup_subtitle')))
    console.print("[dim]📂 {workspace}[/dim]".format(workspace=workspace_path))
    console.print(
        "[bold #34D399]Grow[/bold #34D399] "
        "[dim]→[/dim] "
        "[bold #22D3EE]Code[/bold #22D3EE] "
        "[dim]→[/dim] "
        "[bold #A78BFA]Ship[/bold #A78BFA]  "
        "[dim]{tip}[/dim]".format(tip=get_text('startup_shortcuts_tip'))
    )

    console.print()

    if is_model_ready:
        console.print(f"  [bold green]●[/bold green] {model_status}")
    else:
        console.print(f"  [bold red]○[/bold red] {model_status}")

    console.print()
    console.print(f"[dim]{SEPARATOR}[/dim]")
    render_compact_footer()
    console.print()



def render_compact_footer() -> None:
    """
    Muestra una línea corta de ayuda debajo del prompt.

    Más adelante podemos hacer que esta línea cambie según modo,
    modelo seleccionado, permisos o workspace activo.
    """
    console.print(
        "[dim]  ? atajos  ·  / comandos  ·  Ctrl+C salir"
        "                         [bold]MauCode[/bold][/dim]"
    )


def render_shortcuts_help() -> None:
    """
    Muestra la ayuda rápida cuando el usuario presiona '?'.

    Esta pantalla no envía nada al modelo. Solo informa atajos.
    """

    console.print(f"[dim]{SEPARATOR}[/dim]")

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
        "[bold]/APIs[/bold] gestionar claves",
        "[bold]Esc[/bold] cancelar generación",
    )

    table.add_row(
        "[bold]Ctrl+V[/bold] pegar texto",
        "[bold]↑/↓[/bold] historial",
        "[bold]Tab[/bold] autocompletar",
    )

    console.print(table)
    console.print(f"[dim]{SEPARATOR}[/dim]")