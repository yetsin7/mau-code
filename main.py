# Importar el modelo de Ollama
import ollama

# Llamamos a Rich para hacer la terminal más bonita
from rich.console import Console

# Creamos una instancia de la consola de Rich
console = Console()

# Nombre EXACTO del modelo de Ollama que queremos usar:
MODELO = "qwen2.5-coder:7b"


# Creamos una función para enviar mensajes al modelo de Ollama: 
def preguntar_a_ollama(mensaje_usuario = str) -> str:
    
    """Envía un mensaje al modelo y devuelve la respuesta."""

    respuesta = ollama.chat(
        model = MODELO,
          messages=[
            {
                "role": "system", 
                "content": (
                    "Eres Cara de Loco, un asistente útil y amigable en programación sennior."
                ),

            },
            {
                "role": "user", 
                "content": mensaje_usuario,
            },
        ],
    )

    # Extraemos solamente el texto de respuesta.
    return respuesta['message']['content']


# Función principal del programa
def iniciar_chat():
    console.print("[bold green]¡Hola! Soy MauCode, tu asistente de programación sennior. ¿En qué puedo ayudarte hoy?[/bold green]")
    console.print("[bold yellow]Escribe 'salir' para terminar el chat.[/bold yellow]")
    
    while True:
        # Esperamos la entrada del usuario:
        mensaje = input("[bold cyan]Tú:[/bold cyan] ")

        # Comando para salir del chat:
        if mensaje.lower() == "salir":
            console.print("[bold red]¡Hasta luego![/bold red]")
            break

        # Mandamos el mensaje al modelo:
        respuesta = preguntar_a_ollama(mensaje)

        # Imprimimos la respuesta del modelo:
        console.print("\n[bold green]MauCode: >[/bold green]") 
        console.print(respuesta)
        console.print()

     # Punto de inicio del programa.
if __name__ == "__main__":
    iniciar_chat()   
            