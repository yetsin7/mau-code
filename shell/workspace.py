from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings
from shell.renderer import console
from shell.terminal_ui import SEPARATOR


def get_current_workspace() -> Path:
    """
    Devuelve la carpeta desde donde se ejecutó MauCode.

    Si el usuario abre PowerShell en C:\\Dev\\mi-proyecto y ejecuta MauCode,
    esa carpeta será el workspace activo.
    """

    return Path.cwd().resolve()



def ask_workspace_trust(workspace_path: Path) -> bool:
    """
    Pregunta si el usuario confía en la carpeta actual.

    Enter confirma.
    N cancela.
    Ctrl+C o Esc cancelan sin traceback.
    """

    key_bindings = KeyBindings()

    @key_bindings.add(Keys.Escape)
    def cancel_with_escape(event):
        """
        Permite cancelar la pantalla incial con Esc.
        """

        event.app.exit(exception = KeyboardInterrupt)

    prompt_session = PromptSession(key_bindings = key_bindings)

    console.print(SEPARATOR)
    console.print("[bold]Acceso al espacio de trabajo:[/bold]")
    console.print()

    console.print(f"    [cyan]{workspace_path}[/cyan]")
    console.print()

    console.print("[bold]Verificación rápida de seguridad:[/bold] ¿Usted creó éste proyecto? Confía en él?")
    console.print("[dim]De lo contrario, por favor revise antes el contenido de ésta carpeta.[/dim]")
    console.print()


    console.print(
        "[dim]MauCode podrá leer, editar y ejecutar archivos aquí: "
        "solo después de tu aprovación.[/dim]"
    )
    console.print()

    console.print("[bold green]Enter[/bold green] para confirmar - [bold yellow]N[/bold yellow] para salir - [bold red]Esc/Ctrl+C[/bold red] para cancelar")
    console.print(SEPARATOR)
    

    try:
        answer = prompt_session.prompt("❯ ").strip().lower()    
        
    except (KeyboardInterrupt, EOFError):
        console.print()
        console.print("[bold yellow]Inicio cancelado.[/bold yellow]")
        return False
    
    if answer == "":
        return True
    
    if answer in {"y", "yes", "s", "si", "sí"}:
        return True
    
    console.print()
    console.print("\n[bold yellow]Inicio cancelado. No se dieron permios para este espacio de trabajo.[/bold yellow]")
    return False
