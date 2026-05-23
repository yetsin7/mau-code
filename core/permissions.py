# AQUÍ SE MANEJA EL TEMA DE PERMISOS PARA MauCode:
class PermissionSession:
    """
    Guarda permisos temporales para una sola respuesta del modelo.

    Importante:
    - No vive durante toda la ejecución de MauCode.
    - Se crea de nuevo cada vez que el usuario envía un mensaje.
    - Si el usuario elige "sí a todo", solo aplica a las acciones de
    esa respuesta específica del modelo.
    """

    def __init__(self):
        """
        Inicializa la sesión de permisos.
        
        allow_all empieza en False porque MauCode siempre debe preguntar 
        al inicio de cada nuevo mensaje del usuario.
        """

        self.allow_all = False


# Función para solicitar permisos:
def ask_tool_permission(permission_session: PermissionSession) -> bool:
    """
    Pregunta al usuario si quiere ejecutar una acción.

    Opciones:
    1. Sí: ejecuta solo esta acción.
    2. Sí a todo: ejecuta esta acción y las siguientes acciones
        de la misma respuesta del modelo.
    3. No, dime algo más: cancela esta acción.
    """

    if permission_session.allow_all:
        return True
    
    print("\n¿Qué quieres hacer?")
    print("1. Sí")
    print("2. Sí a todo")
    print("3. No, dime algo más")

    option = input("Elige una opción (1. Sí, 2. Sí a todo, 3. No, dime algo más): ").strip()

    if option == "1":
        return True
    
    if option == "2":
        permission_session.allow_all = True
        return True
    
    return False



