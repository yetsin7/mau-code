from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from shell.renderer import console  # Consola visual con Rich.
from shell.command_registry import get_command_names, get_command_entries
from shell.terminal_ui import render_shortcuts_help

import re


# Cuenta cuántas veces el usuario ha pegado texto multilínea.
pasted_text_counter = 0

# Guarda los textos pegados reales.
# La clave es el ID del paste y el valor es el texto completo.
paste_storage = {}

# Genera IDs únicos para cada bloque pegado.
paste_id_counter = 0


# Contenedor de atajos/eventos personalizados de Prompt Toolkit.
key_bindings = KeyBindings()


@key_bindings.add(Keys.BracketedPaste)
def handle_paste(event):
    """
    Detecta cuando el usuario pega texto con CTRL+V.

    Si el texto pegado tiene varias líneas:
    - guarda el contenido real en paste_storage
    - muestra solo un placeholder corto en el input

    Si el texto pegado tiene una sola línea:
    - lo inserta normalmente en el input
    """

    global pasted_text_counter
    global paste_storage
    global paste_id_counter

    # Normalizamos saltos de línea para evitar problemas en Windows.
    pasted_text = (
        event.data
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    # Calculamos cuántas líneas tiene el texto pegado.
    line_count = pasted_text.count("\n") + 1

    # Si solo es una línea, se comporta como un paste normal.
    if line_count <= 1:
        event.current_buffer.insert_text(pasted_text)
        return

    # Registramos un nuevo bloque pegado.
    pasted_text_counter += 1
    paste_id_counter += 1

    paste_id = paste_id_counter

    # Guardamos el texto real para enviarlo después al modelo.
    paste_storage[paste_id] = pasted_text

    # Esto es lo único que el usuario verá en el input.
    placeholder = f"[Paste #{paste_id} · {line_count} líneas]"

    # Insertamos el placeholder visual, no el texto real completo.
    event.current_buffer.insert_text(placeholder)



@key_bindings.add("?")
def handle_shortcuts_help(event):
    """
    Muestra la ayuda rápida cuando el usuario presiona '?'.

    Si el usuario ya escribió algo, insertamos el signo normalmente.
    Si el input está vacío, mostramos la pantalla de atajos.
    """

    if event.current_buffer.text:
        event.current_buffer.insert_text("?")
        return
    
    run_in_terminal(render_shortcuts_help)


# Estado para rastrear si el usuario ya presionó Ctrl+C una vez en el prompt vacío
ctrl_c_pressed_once = False


@key_bindings.add("c-c")
def handle_ctrl_c(event):
    """
    Controla el evento Ctrl+C en el prompt de MauCode.

    - Si hay texto en el input: borra la entrada para que el usuario pueda escribir de nuevo.
    - Si el input está vacío: la primera vez lanza una alerta pidiendo confirmación.
      La segunda vez consecutiva cierra la sesión de MauCode.
    """
    global ctrl_c_pressed_once

    import importlib
    i18n_manager = importlib.import_module("core.i18n-manager")
    get_text = i18n_manager.get_text

    # Si hay algún texto en el buffer, simplemente lo borramos
    if event.current_buffer.text.strip() or event.current_buffer.text:
        event.current_buffer.text = ""
        ctrl_c_pressed_once = False
    else:
        # Si está vacío, revisamos si es la segunda vez consecutiva
        if ctrl_c_pressed_once:
            event.app.exit(exception=KeyboardInterrupt)
        else:
            ctrl_c_pressed_once = True
            
            # Mostramos la alerta temporal abajo
            def print_alert():
                console.print(f"\n[bold yellow]{get_text('double_ctrl_c_alert')}[/bold yellow]")
                
            run_in_terminal(print_alert)


class CommandAutoSuggest(AutoSuggest):
    """
    Muestra sugerencias fantasma para comandos internos.

    Ejemplo:
    si el usuario escribe "/mod", MauCode puede sugerir "el"
    para completar "/model".
    """

    def get_suggestion(self, buffer, document):
        """
        Devuelve la parte restante del comando sugerido.

        Solo funciona cuando el usuario está escribiendo un comando,
        es decir, cuando el texto empieza con "/".
        """
          
        text = document.text_before_cursor
    
        if not text.startswith("/"):
            return None
                
        # Si ya hay espacios, asumimos que no es un comando simple:
        if " " in text:
            return None
        
        for command in get_command_names():
            if command.startswith(text) and command != text:
                remaining_text = command[len(text):]
                return Suggestion(remaining_text)
            
        return None
        

    
# Autocompletador de comandos internos:
class CommandCompleter(Completer):
    """
    Muestra comandos internos con descripción.

    Esto permite que al escribir '/' aparezca una lista tipo Claude Code,
    usando el registro central de comandos.
    """

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        if not text.startswith("/"):
            return
        
        if " " in text:
            return
        
        for command, command_info in get_command_entries().items():
            if not command.startswith(text):
                continue

            yield Completion(
                command,
                start_position = -len(text),
                display = command,
                display_meta = command_info.get("description", ""),
            )

    


# Sesión reutilizable de Prompt Toolkit.
# Incluye historial con flechas arriba/abajo y soporte para paste custom.
session = PromptSession(
    history = FileHistory(".maucode_history"),
    key_bindings = key_bindings,
    completer = CommandCompleter(),
    auto_suggest = CommandAutoSuggest(),
    complete_while_typing = True,
)




def read_user_input() -> str:
    """
    Lee el mensaje del usuario.

    Si el mensaje contiene placeholders como:

        [Paste #1 · 245 líneas]

    los reemplaza internamente por el texto real que fue pegado.

    Esto permite que el usuario vea un input limpio, pero que MauCode
    reciba el contenido completo.
    """

    global paste_storage, ctrl_c_pressed_once
    ctrl_c_pressed_once = False

    # Leemos el mensaje final del usuario.
    message = session.prompt("Tú: > ")

    # Busca placeholders generados por handle_paste().
    pattern = r"\[Paste #(\d+) · \d+ líneas\]"
    matches = re.findall(pattern, message)

    # Si no hay placeholders, devolvemos el mensaje normal.
    if not matches:
        return message

    real_message = message

    # Reemplazamos cada placeholder por su texto pegado real.
    for match in matches:
        paste_id = int(match)

        # Si por alguna razón no existe el paste, lo ignoramos.
        if paste_id not in paste_storage:
            continue

        # Regex específica para este placeholder.
        placeholder_pattern = rf"\[Paste #{paste_id} · \d+ líneas\]"

        real_message = re.sub(
            placeholder_pattern,
            lambda match: paste_storage[paste_id],        
            real_message,
            count=1,
        )

    # Limpiamos los bloques pegados después de enviar el mensaje.
    paste_storage.clear()

    return real_message