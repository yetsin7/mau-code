import re

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

from terminal.renderer import console  # Consola visual con Rich.


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


# Sesión reutilizable de Prompt Toolkit.
# Incluye historial con flechas arriba/abajo y soporte para paste custom.
session = PromptSession(
    history=FileHistory(".maucode_history"),
    key_bindings=key_bindings,
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

    global paste_storage

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