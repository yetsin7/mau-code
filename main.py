import ollama # Importar el modelo de Ollama
import json # Para leer órdenes del modelo en formato JSON.
from tools.crear_archivo import crear_archivo_texto # Importar Tools Calling.
from rich.console import Console # Llamamos a Rich para hacer la terminal más bonita.


# Creamos una instancia de la consola de Rich.
console = Console()

# Nombre EXACTO del modelo de Ollama que queremos usar.
MODELO = "qwen2.5-coder:7b"


# PROMPT DE HERRAMIENTAS (Tool Calling).
SYSTEM_PROMPT = """
Eres Mau Code, un asistente útil y amigable de programación senior.

Puedes conversar normalmente.

Si el usuario te pide crear un archivo de texto, debes responder SOLO con JSON válido.

Herramientas disponibles:

{
    "accion": "crear_archivo_texto",
    "carpeta": "RUTA_EXACTA_DE_LA_CARPETA",
    "nombre_archivo": "NOMBRE_DEL_ARCHIVO.txt",
    "contenido": "TEXTO_QUE_SE_GUARDARÁ"
}

Reglas:

- No inventes la carpeta.
- Usa exactamente la carpeta que el usuario indique.
- Si el usuario no indica carpeta, pregunta cuál carpeta debe usar.
- No uses markdown cuando respondas con JSON.
- No expliques nada cuando respondas con JSON.
"""


# Creamos una función para enviar mensajes al modelo de Ollama.
def preguntar_a_ollama(mensaje_usuario: str) -> str:
    """
    Envía un mensaje al modelo de Ollama
    y devuelve únicamente el contenido de la respuesta.
    """

    respuesta = ollama.chat(
        model=MODELO,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": mensaje_usuario,
            },
        ],
    )

    # Extraemos solamente el texto de respuesta.
    return respuesta['message']['content']


# Función para leer JSON.
def intentar_leer_json(texto: str):
    """
    Intenta convertir un texto JSON
    en datos válidos de Python.

    Si no puede convertirlo, devuelve None.
    """

    try:
        return json.loads(texto)

    except json.JSONDecodeError:
        return None



# Ejecutor de Tool Calling.
def manejar_respuesta_del_modelo(respuesta_modelo: str):
    """
    Decide si la respuesta del modelo
    es texto normal o una instrucción
    para ejecutar una tool.
    """

    datos = intentar_leer_json(respuesta_modelo)

    # Si no es JSON, lo mostramos como texto normal.
    if datos is None:

        console.print("\n[bold green]MauCode: >[/bold green]")
        console.print(respuesta_modelo)
        console.print()

        return
    
    # Si es JSON, verificamos la acción.
    accion = datos.get("accion")

    if accion == "crear_archivo_texto":        

        carpeta = datos.get("carpeta", "")
        nombre_archivo = datos.get("nombre_archivo", "")
        contenido = datos.get("contenido", "")

        console.print("\n[bold yellow]MauCode quiere ejecutar esta acción:  >[/bold yellow]")

        console.print(f"[cyan]Tool:[/cyan] crear_archivo_texto")
        console.print(f"[cyan]Carpeta:[/cyan] {carpeta}")
        console.print(f"[cyan]Nombre del archivo:[/cyan] {nombre_archivo}")

        confirmar = input("\n¿Quieres ejecutar esta acción? (si/no): ")
        
        if confirmar.lower() != "si":

            console.print("\n[bold red]Acción cancelada por el usuario.[/bold red]\n")
            return
        
        resultado = crear_archivo_texto(
            carpeta = carpeta,
            nombre_archivo = nombre_archivo,
            contenido = contenido
        )

        console.print(f"\n[bold green]Resultado: >[/bold green]")
        console.print(resultado)
        console.print()

        return

    console.print("\n[bold red]La acción solicitada aún no existe. >[/bold red]")
    console.print(datos)



# Función principal del programa.
def iniciar_chat():
    """
    Inicia el chat principal de MauCode
    dentro de la terminal.
    """

    console.print(
        "[bold green]¡Hola! Soy MauCode, tu asistente de programación senior. ¿En qué puedo ayudarte hoy?[/bold green]"
    )

    console.print(
        "[bold yellow]Escribe 'salir' para terminar el chat.[/bold yellow]"
    )

    while True:

        # Esperamos la entrada del usuario.
        mensaje = input("[bold cyan]Tú:[/bold cyan] ")

        # Comando para salir del chat.
        if mensaje.lower() == "salir":

            console.print("[bold red]¡Hasta luego![/bold red]")
            break

        # Mandamos el mensaje al modelo.
        respuesta = preguntar_a_ollama(mensaje)

        # Revisamos si respondió texto normal o pidió ejecutar una tool.
        manejar_respuesta_del_modelo(respuesta)


# Punto de inicio del programa.
if __name__ == "__main__":
    iniciar_chat()

