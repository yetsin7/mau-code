import ollama  # Cliente para comunicarnos con Ollama.

from prompts.system_prompt import SYSTEM_PROMPT

# Nombre exacto del modelo instalado en Ollama.
MODEL_NAME = "qwen2.5-coder:7b"


def ask_ollama(user_message: str) -> str:
    """
    Envía el mensaje del usuario al modelo local de Ollama.

    Esta función mantiene aislada la comunicación con el modelo para que
    main.py no tenga que saber cómo se llama Ollama internamente.
    """

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
    )

    return response["message"]["content"]