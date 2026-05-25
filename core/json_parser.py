import json  # Para leer órdenes del modelo en formato JSON.
import re # Para extraer bloques JSON aunque vengan dentro de markdown.


def try_parse_json_actions(text: str):
    """
    Intenta convertir la respuesta del modelo en una lista de acciones JSON.

    Este parser es tolerante porque los modelos locales a veces responden con:
    - texto antes del JSON;
    - bloques markdown ```json;
    - varios objetos JSON consecutivos;
    - texto después del JSON.
    """

    text = text.strip()

    # Primero buscamos bloques markdown con JSON.
    fence_blocks = extract_fenced_json_blocks(text)

    if fence_blocks:
        combined_text = "\n".join(fence_blocks)
        return parse_multiple_json_objects(combined_text)

    # Si no hay bloques markdown, intentamos buscar objetos JSON en el texto plano:
    return parse_multiple_json_objects(text)



def extract_fenced_json_blocks(text: str) -> list[str]:

    """
    Extrae el contenido dentro de bloques markdown JSON.

    Ejemplo:
    ```json
    { ... }
    ```
    """

    pattern = r"```(?:json)?\s*(.*?)```"

    return re.findall(
        pattern,
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )



def parse_multiple_json_objects(text: str):
    """
    Lee uno o varios objetos JSON desde un texto.

    Si encuentra texto antes del primer JSON, avanza hasta el siguiente "{"
    para no fallar cuando el modelo agregue frases innecesarias.
    """

    decoder = json.JSONDecoder()
    actions = []
    index = 0

    text = text.strip()

    while index < len(text):

        # Saltamos espacios y saltos de línea:
        while index < len(text) and text[index].isspace():
            index += 1

        # Si hay texto antes de un JSON, buscamos el siguiente objeto.
        if index < len(text) and text[index] != "{":
            next_object_start = text.find("{", index)

            if next_object_start == -1:
                break

            index = next_object_start

        try:
            action, next_index = decoder.raw_decode(text[index:])
            actions.append(action)
            index += next_index

        except json.JSONDecodeError:
            return None
        
    if not actions:
        return None

    return actions

