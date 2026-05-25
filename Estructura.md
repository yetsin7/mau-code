# MauCode - Estructura real del proyecto

Este documento describe la estructura que existe actualmente en `C:\Dev\mau-code`.
No es una estructura deseada ni un roadmap: es el mapa real del working tree
fuente que MauCode usa hoy.

## Árbol fuente actual

```txt
mau-code/
├── .maucode_history
├── Estructura.md
├── README.md
├── main.py
├── core/
│   ├── action_executor.py
│   ├── action_guard.py
│   ├── api-manager.py
│   ├── i18n-manager.py
│   ├── json_parser.py
│   ├── model_client.py
│   ├── ollama-service.py
│   └── permissions.py
├── prompts/
│   └── system_prompt.py
├── shell/
│   ├── api-commands.py
│   ├── commands.py
│   ├── command_registry.py
│   ├── input_handler.py
│   ├── paste_handler.py
│   ├── renderer.py
│   ├── run_python.py
│   ├── run_terminal.py
│   ├── session.py
│   ├── streaming.py
│   └── workspace.py
└── tools/
    ├── data/
    │   ├── read-json.py
    │   └── write-json.py
    ├── filesystem/
    │   ├── copy-file.py
    │   ├── create-file.py
    │   ├── create-folder.py
    │   ├── delete-file.py
    │   ├── delete-folder.py
    │   ├── edit-file.py
    │   ├── list-files.py
    │   ├── move-file.py
    │   ├── read-file.py
    │   └── rename-file.py
    ├── git/
    │   ├── git-branch.py
    │   ├── git-commit.py
    │   ├── git-diff.py
    │   └── git-status.py
    └── search/
        ├── search-code.py
        └── search-text.py
```

## Archivos generados

Python también genera carpetas `__pycache__/` con archivos `.pyc`. Estos archivos
no son parte de la arquitectura fuente y no deben usarse para entender el diseño
del proyecto.

## Responsabilidades por módulo

### `main.py`

Responsabilidad actual:

- Importa e inicializa el flujo principal.
- Delega el loop interactivo a `shell/session.py`.
- Pasa `ask_ollama`, `handle_model_response` y `warm_up_model` a la sesión.

### Módulos en `core/`

#### `core/action_executor.py`

Responsabilidad actual:

- Decide si la respuesta del modelo es texto normal o una lista de acciones JSON (`handle_model_response`).
- Ejecuta acciones individuales devueltas por el modelo (`execute_action`). Actualmente, solo soporta `create_file`.
- Solicita confirmación al usuario antes de ejecutar acciones a través de `core/permissions.py`.

#### `core/action_guard.py`

Estado actual:

- Archivo vacío. Pensado para futuras validaciones de seguridad de acciones.

#### `core/json_parser.py`

Responsabilidad actual:

- Intenta convertir respuestas del modelo en una lista de acciones JSON (`try_parse_json_actions`).
- Parser tolerante que extrae bloques markdown de tipo JSON (`extract_fenced_json_blocks`) o decodifica múltiples objetos JSON sueltos dentro del texto (`parse_multiple_json_objects`).

#### `core/model_client.py`

Responsabilidad actual:

- Conexión directa con la librería `ollama` para el chat con el modelo.
- Detecta dinámicamente qué modelos están instalados localmente en Ollama (`list_installed_ollama_models`).
- Selecciona el mejor modelo por defecto (prefiere `qwen3:8b`, o el primero disponible si no está).
- Permite cambiar y calentar/cargar en memoria el modelo seleccionado (`warm_up_model`).

#### `core/permissions.py`

Responsabilidad actual:

- Gestiona permisos para ejecutar herramientas con la clase `PermissionSession`.
- `ask_tool_permission` le ofrece al usuario tres opciones ante una acción propuesta: 1. Sí (solo esta acción), 2. Sí a todo (para esta respuesta del modelo), 3. No, dime algo más (cancelar).

### Módulos en `prompts/`

#### `prompts/system_prompt.py`

Responsabilidad actual:

- Contiene `SYSTEM_PROMPT`, la variable de texto que define la identidad de MauCode, sus instrucciones de formateo de código, reglas de creación de archivos JSON e independencia de objetos JSON.

### Módulos en `shell/`

#### `shell/session.py`

Responsabilidad actual:

- Inicia la terminal interactiva (`start_terminal_session`), mostrando saludo y cargando el modelo local.
- Mantiene el loop de conversación interactiva, detectando comandos internos y la palabra clave `salir`.

#### `shell/input_handler.py`

Responsabilidad actual:

- Maneja la lectura de la entrada del usuario usando `prompt_toolkit`.
- Soporta historial con persistencia en `.maucode_history`.
- Detecta pegados grandes de texto (`BracketedPaste`), reemplazándolos con placeholders visibles en la terminal para mantener el orden visual, pero conservando todo el texto original para el modelo.

#### `shell/commands.py`

Responsabilidad actual:

- Intercepta y procesa comandos internos como `/modelo` o `/model`.
- Ofrece una interfaz de diálogo visual en terminal (`radiolist_dialog`) para elegir qué modelo local de Ollama usar y lo carga en memoria de inmediato.

#### `shell/command_registry.py`

Responsabilidad actual:

- Mantiene el registro de comandos válidos (`INTERNAL_COMMANDS`) y maneja la normalización de alias (por ejemplo, de `/model` a `/modelo`).

#### `shell/renderer.py`

Responsabilidad actual:

- Expone una consola compartida de `rich.console.Console` para formatear los mensajes y colores en terminal.

#### `shell/paste_handler.py`, `shell/run_python.py`, `shell/run_terminal.py`, `shell/streaming.py`, `shell/workspace.py`

Estado actual:

- Archivos vacíos preparados como puntos de extensión futuros (gestión de pastes, ejecución de código, streaming de tokens y manejo del workspace).

## Tools actuales

### `tools/filesystem/create_file.py`

Estado actual:

- Implementado.

Responsabilidad:

- Crear carpetas recursivamente de ser necesario.
- Crear archivos validando que `file_name` no tenga rutas embebidas (`/`, `\`, `..`).
- Validar extensiones mediante un set de extensiones permitidas.
- Escribir contenido codificado en UTF-8.

### Resto de módulos en `tools/`

Archivos existentes en:
- `tools/data/` (`read_json.py`, `write_json.py`)
- `tools/filesystem/` (restantes `.py` como `copy_file.py`, `delete_file.py`, `edit_file.py`, etc.)
- `tools/git/` (`git_branch.py`, `git_commit.py`, etc.)
- `tools/search/` (`search_code.py`, `search_text.py`)

Estado actual:

- Creados como módulos vacíos. Pendientes de implementar y conectar al despachador de acciones.

## Flujo de ejecución actual

```txt
python main.py
↓
shell.session.start_terminal_session()
↓
(Opcional) core.model_client.warm_up_model() (Inicia el modelo seleccionado)
↓
shell.input_handler.read_user_input()
↓
(Si es comando interno /modelo, lo maneja shell.commands.handle_internal_command() y vuelve a pedir entrada)
↓
core.model_client.ask_ollama()
↓
Ollama responde (texto u objetos JSON)
↓
core.action_executor.handle_model_response()
↓
core.json_parser.try_parse_json_actions() (Parsea el texto buscando JSONs)
↓
Si hay acción (e.g. create_file), se pide confirmación mediante core.permissions.ask_tool_permission()
↓
Si el usuario autoriza (Opción 1 o 2), se ejecuta tools.filesystem.create_file.create_file()
↓
Resultado renderizado en terminal con shell.renderer.console
```

## Reglas de mantenimiento de estructura

- Documentar solo carpetas y archivos reales.
- Marcar claramente los módulos vacíos como pendientes.
- No presentar herramientas no conectadas como funcionales.
- Mantener una tool por archivo.
- Mantener `main.py` como punto de entrada limpio.
- Crear pruebas antes de ampliar acciones sensibles como terminal, Git o borrado.
- Actualizar este archivo cada vez que se cree, elimine o mueva un módulo fuente.
