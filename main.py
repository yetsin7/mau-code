from core.action_executor import handle_model_response
from core.model_client import ask_ollama, warm_up_model
from shell.session import start_terminal_session  # Loop principal de la sesión.


if __name__ == "__main__":
    start_terminal_session(
        ask_ollama = ask_ollama, 
        handle_model_response = handle_model_response,
        warm_up_model = warm_up_model,
    )