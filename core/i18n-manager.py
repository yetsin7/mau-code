import locale

# Diccionario de traducciones centralizado para soporte bilingüe
TRANSLATIONS = {
    "es": {
        "select_provider_title": "Configurar Clave de API",
        "select_provider_prompt": "Selecciona el proveedor de la API:",
        "enter_key_prompt": "Ingresa la clave de API para {provider}: ",
        "empty_key_error": "[bold red]Error: La clave de API no puede estar vacía.[/bold red]",
        "testing_connection": "[bold cyan]Probando conexión con {provider}...[/bold cyan]",
        "connection_success": "[bold green]✓ ¡Conexión exitosa! Se detectaron {count} modelos en {provider}.[/bold green]",
        "connection_failed": "[bold red]✗ Error al conectar con {provider}: {error}[/bold red]",
        "invalid_key_try_again": "[yellow]La clave no es válida o falló el test de conexión. Por favor, intenta de nuevo.[/yellow]",
        "cancel_api_setup": "[bold yellow]Configuración de API cancelada.[/bold yellow]",
        "no_models_found": "[yellow]No se encontraron modelos disponibles en {provider}.[/yellow]",
        "model_selector_title": "Seleccionar modelo:",
        "model_selector_help": "↑/↓ mover - Enter confirmar - Esc/Ctrl+C cancelar",
        "model_selector_current": "(actual)",
        "model_selection_canceled": "[bold yellow]Selección de modelo cancelada.[/bold yellow]",
        "model_actual_label": "[dim]Modelo actual: {model}[/dim]",
        "warming_up": "[bold cyan]Iniciando modelo {model}...[/bold cyan]",
        "model_ready": "Modelo listo: {model}",
        "model_warm_up_error": "No se pudo iniciar el modelo: {error}",
        "provider_options": "Opciones de proveedores de API",
        "option_exit": "Volver al chat",
        
        # Nuevas traducciones para el selector visual y nombres personalizados de APIs
        "api_selector_title": "Gestión de APIs de Modelos:",
        "api_selector_help": "↑/↓ mover - Enter confirmar - Esc/Ctrl+C cancelar",
        "add_new_api_option": "[+ Agregar nueva API / Add new API]",
        "api_action_title": "Configuración de API",
        "api_action_prompt": "¿Qué deseas hacer con la API de '{name}'?",
        "api_action_delete": "Eliminar API / Delete API",
        "api_action_cancel": "Regresar / Back",
        "enter_custom_provider_prompt": "Ingresa un nombre personalizado para el proveedor de la API (ej. mi-openai): ",
        "empty_provider_error": "[bold red]Error: El nombre del proveedor no puede estar vacío.[/bold red]",
        "detect_protocol_failed": "[bold red]Error: No se pudo detectar un protocolo de comunicación válido (OpenAI, Anthropic, Gemini, Groq) para esta API key.[/bold red]",
        "api_deleted_success": "[bold green]✓ API '{name}' eliminada con éxito.[/bold green]",
    },
    "en": {
        "select_provider_title": "Configure API Key",
        "select_provider_prompt": "Select the API provider:",
        "enter_key_prompt": "Enter the API key for {provider}: ",
        "empty_key_error": "[bold red]Error: The API key cannot be empty.[/bold red]",
        "testing_connection": "[bold cyan]Testing connection to {provider}...[/bold cyan]",
        "connection_success": "[bold green]✓ Connection successful! Detected {count} models in {provider}.[/bold green]",
        "connection_failed": "[bold red]✗ Error connecting to {provider}: {error}[/bold red]",
        "invalid_key_try_again": "[yellow]The key is invalid or connection test failed. Please try again.[/yellow]",
        "cancel_api_setup": "[bold yellow]API configuration canceled.[/bold yellow]",
        "no_models_found": "[yellow]No models found in {provider}.[/yellow]",
        "model_selector_title": "Select model:",
        "model_selector_help": "↑/↓ move - Enter confirm - Esc/Ctrl+C cancel",
        "model_selector_current": "(current)",
        "model_selection_canceled": "[bold yellow]Model selection canceled.[/bold yellow]",
        "model_actual_label": "[dim]Current model: {model}[/dim]",
        "warming_up": "[bold cyan]Initializing model {model}...[/bold cyan]",
        "model_ready": "Model ready: {model}",
        "model_warm_up_error": "Could not initialize model: {error}",
        "provider_options": "API provider options",
        "option_exit": "Back to chat",
        
        # New translations for custom API selector and custom naming
        "api_selector_title": "Model API Management:",
        "api_selector_help": "↑/↓ move - Enter confirm - Esc/Ctrl+C cancel",
        "add_new_api_option": "[+ Add new API / Agregar nueva API]",
        "api_action_title": "API Configuration",
        "api_action_prompt": "What do you want to do with '{name}''s API?",
        "api_action_delete": "Delete API / Eliminar API",
        "api_action_cancel": "Back / Regresar",
        "enter_custom_provider_prompt": "Enter a custom name for the API provider (e.g. my-openai): ",
        "empty_provider_error": "[bold red]Error: Provider name cannot be empty.[/bold red]",
        "detect_protocol_failed": "[bold red]Error: Could not detect a valid communication protocol (OpenAI, Anthropic, Gemini, Groq) for this API key.[/bold red]",
        "api_deleted_success": "[bold green]✓ API '{name}' deleted successfully.[/bold green]",
    }
}

# Idioma predeterminado del sistema
default_language = "es"

def detect_system_language() -> str:
    """
    Detecta el idioma del sistema operativo.
    Si empieza con 'es', se establece español. De lo contrario, inglés.
    """
    global default_language
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.startswith("es"):
            default_language = "es"
        else:
            default_language = "en"
    except Exception:
        default_language = "es"
    return default_language

# Ejecutar la detección al cargar el módulo
detect_system_language()

def get_text(key: str, **kwargs) -> str:
    """
    Devuelve la cadena de texto traducida según el idioma del sistema.
    Permite formatear variables en el texto devuelto.
    """
    translations_dict = TRANSLATIONS.get(default_language, TRANSLATIONS["es"])
    text_template = translations_dict.get(key, TRANSLATIONS["es"].get(key, key))
    if kwargs:
        return text_template.format(**kwargs)
    return text_template

def set_language(lang_code: str) -> None:
    """
    Permite cambiar manualmente el idioma a usar en tiempo de ejecución.
    """
    global default_language
    if lang_code in TRANSLATIONS:
        default_language = lang_code
