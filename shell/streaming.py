import json
import urllib.request
import urllib.error
from shell.renderer import console


def stream_openai_response(url: str, headers: dict, body: dict) -> str:
    """
    Realiza una petición de streaming (SSE) a una API compatible con OpenAI.
    Imprime los tokens en tiempo real y retorna el contenido completo acumulado.

    Parámetros:
        url: Endpoint de chat completions
        headers: Headers HTTP incluyendo Authorization
        body: Cuerpo JSON de la petición (se le agrega stream=True)

    Retorna:
        El texto completo generado por el modelo.
    """
    body["stream"] = True

    req = urllib.request.Request(url, method="POST")
    req.data = json.dumps(body).encode("utf-8")
    req.add_header("Content-Type", "application/json")
    for key, value in headers.items():
        req.add_header(key, value)

    accumulated_content = ""

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            buffer = ""

            for raw_chunk in response:
                chunk = raw_chunk.decode("utf-8")
                buffer += chunk

                # Procesamos líneas SSE completas del buffer
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()

                    if not line:
                        continue

                    # Fin del stream según la especificación SSE de OpenAI
                    if line == "data: [DONE]":
                        break

                    if not line.startswith("data: "):
                        continue

                    json_str = line[6:]  # Removemos el prefijo "data: "

                    try:
                        data = json.loads(json_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        token = delta.get("content", "")

                        if token:
                            console.print(token, end="")
                            accumulated_content += token

                    except json.JSONDecodeError:
                        continue

    except urllib.error.HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
            parsed_error = json.loads(error_body)
            error_message = parsed_error.get("error", {}).get("message", error.reason)
        except Exception:
            error_message = str(error.reason)
        raise RuntimeError(f"Error de API durante streaming: {error_message}")

    except urllib.error.URLError as error:
        raise RuntimeError(f"Error de red/conexión durante streaming: {error.reason}")

    # Salto de línea final después del stream
    console.print()

    return accumulated_content


def stream_api_response(provider: str, url: str, headers: dict, body: dict) -> str:
    """
    Selecciona la estrategia de streaming correcta según el proveedor.
    Actualmente soporta streaming para APIs compatibles con OpenAI (OpenAI, Groq).

    Parámetros:
        provider: Protocolo del proveedor (openai, groq, anthropic, gemini)
        url: URL del endpoint de chat
        headers: Headers HTTP
        body: Cuerpo de la petición

    Retorna:
        El texto completo generado.
    """
    # OpenAI y Groq usan el mismo protocolo SSE
    if provider in ("openai", "groq"):
        return stream_openai_response(url, headers, body)

    # Anthropic y Gemini no soportan streaming con urllib por ahora
    # Se retorna None para que el caller use la petición normal
    return None
