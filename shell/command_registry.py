"""
Registro central de comandos internos de MauCode.

Este archivo existe para que el autocompletado y el ejecutor de comandos
usen la misma lista. Así evitamos que un comando aparezca en sugerencias
pero luego no exista al presionar Enter.
"""

INTERNAL_COMMANDS = {
    "/thinking": {
        "description": "Activar/desactivar thinking",
        "alias_of": None,
    },
    "/think": {
        "description": "Activar/desactivar thinking",
        "alias_of": "/thinking",
    },
    "/model": {
        "description": "Cambiar modelo",
        "alias_of": "/modelo",
    },
    "/modelo": {
        "description": "Cambiar modelo",
        "alias_of": None,
    },
    "/help": {
        "description": "Ayuda con atajos disponibles",
        "alias_of": "/ayuda",
    },
    "/ayuda": {
        "description": "Ayuda con atajos disponibles",
        "alias_of": None,
    },
    "/apis": {
        "description": "Configurar APIs de modelos",
        "alias_of": "/APIs",
    },
    "/APIs": {
        "description": "Configurar APIs de modelos",
        "alias_of": None,
    },
    "/exit": {
        "description": "Cerrar MauCode",
        "alias_of": "/salir",
    },
    "/salir": {
        "description": "Cerrar MauCode",
        "alias_of": None,
    },
}



def get_command_names() -> list[str]:
    """
    Devuelve los comandos internos disponibles.

    El orden importa porque el primer comando compatible será el que
    se muestre como sugerencia principal.
    """

    return list(INTERNAL_COMMANDS.keys())



def get_command_entries() -> dict:
    """
    Devuelve el diccionario completo de comandos internos.

    Se usa para mostrar autocompletado con descripción,
    no solo el nombre del comando.
    """

    return INTERNAL_COMMANDS   



def normalize_command(command: str) -> str:
    """
    Normaliza alias de comandos.

    Ejemplo:
    /model se convierte internamente en /modelo.
    """  

    command = command.strip().lower()

    command_info = INTERNAL_COMMANDS.get(command)

    if command_info is None:
        return command
    
    alias_of = command_info.get("alias_of")

    if alias_of:
        return alias_of
    
    return command