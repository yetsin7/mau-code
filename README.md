# MauCode

MauCode es un asistente local de programación que corre desde la terminal, conversa con un modelo de Ollama y ejecuta tools bajo confirmación del usuario. El proyecto cuenta con una separación clara de responsabilidades, estructurada en módulos de terminal, cliente de modelo, seguridad/permisos y un catálogo de herramientas.

## Estado actual

Actualmente MauCode puede:

- Iniciar una sesión de chat desde `main.py`;
- Consultar dinámicamente qué modelos están instalados localmente y permitir al usuario alternar entre ellos interactivamente con el comando `/modelo`;
- Enviar mensajes a Ollama usando preferentemente el modelo `qwen3:8b` (o el primero que esté disponible localmente);
- Cargar y precalentar el modelo local en memoria al inicio o cambio de modelo;
- Renderizar respuestas con formato enriquecido mediante Rich;
- Leer entrada interactiva enriquecida con autocompletado usando Prompt Toolkit;
- Guardar historial local en `.maucode_history`;
- Compactar pegados multilínea en placeholders visuales antes de enviarlos al modelo para conservar la legibilidad en pantalla;
- Detectar una o varias acciones JSON devueltas por el modelo en su respuesta;
- Pedir confirmación estructurada (Sí, Sí a todo, No) antes de ejecutar cualquier acción sensible;
- Crear archivos de texto o código mediante la herramienta `tools/filesystem/create_file.py`.

La única tool funcional conectada al flujo principal es `create_file`. Las demás herramientas existen como estructura preparada para futuras expansiones.

## Requisitos

MauCode depende de Python y de librerías externas usadas directamente por el código:

- Python 3.13 o compatible;
- Ollama instalado y ejecutándose localmente;
- Modelo recomendado: `qwen3:8b` disponible en Ollama;
- Paquetes de Python: `ollama`, `rich` y `prompt_toolkit`.

Instalación manual de dependencias:

```bash
pip install ollama rich prompt_toolkit
```

## Ejecución

Desde la raíz del proyecto:

```bash
python main.py
```

Para cambiar de modelo de forma interactiva durante la sesión, escribe:

```txt
/modelo
```

Para salir de la sesión escribe:

```txt
salir
```

## Estructura real del proyecto

```txt
mau-code/
├── .maucode_history
├── Estructura.md
├── README.md
├── main.py
├── core/
│   ├── action_executor.py
│   ├── action_guard.py
│   ├── json_parser.py
│   ├── model_client.py
│   └── permissions.py
├── prompts/
│   └── system_prompt.py
├── shell/
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
    │   ├── read_json.py
    │   └── write_json.py
    ├── filesystem/
    │   ├── copy_file.py
    │   ├── create_file.py
    │   ├── create_folder.py
    │   ├── delete_file.py
    │   ├── delete_folder.py
    │   ├── edit_file.py
    │   ├── list_files.py
    │   ├── move_file.py
    │   ├── read_file.py
    │   └── rename_file.py
    ├── git/
    │   ├── git_branch.py
    │   ├── git_commit.py
    │   ├── git_diff.py
    │   └── git_status.py
    └── search/
        ├── search_code.py
        └── search_text.py
```

Los directorios `__pycache__/` son artefactos generados por Python y no forman parte de la arquitectura fuente del proyecto.

## Flujo principal

```txt
Usuario
↓
shell.input_handler.read_user_input()
↓
(Si es comando interno /modelo, se maneja mediante shell.commands)
↓
core.model_client.ask_ollama()
↓
Ollama responde (texto u objetos JSON)
↓
core.action_executor.handle_model_response()
↓
(Si hay acciones, core.permissions.ask_tool_permission solicita confirmación)
↓
tools.filesystem.create_file.create_file() (ejecución tras confirmar)
↓
Resultado renderizado en la terminal con shell.renderer.console
```

## Módulos principales

### `main.py`
Punto de entrada ultra-limpio que importa e inicializa la sesión interactiva en la terminal, pasando las dependencias correspondientes de Ollama y del despachador de acciones.

### Módulos en `core/`

- **`core/model_client.py`**: Gestiona la interacción con Ollama, la lectura de modelos locales instalados, y la carga y puesta a punto de los modelos.
- **`core/action_executor.py`**: Determina si el texto de la respuesta del modelo contiene comandos ejecutables JSON, gestiona el flujo de permisos de usuario y despacha a las herramientas correspondientes.
- **`core/json_parser.py`**: Parsea robustamente bloques de JSON contenidos en texto o formato markdown de manera tolerante a comentarios extras del modelo.
- **`core/permissions.py`**: Controla el estado y la lógica de aprobación de herramientas por mensaje de usuario (permitiendo "Sí", "Sí a todo", o "Cancelar").

### Módulos en `prompts/`

- **`prompts/system_prompt.py`**: Contiene la definición de `SYSTEM_PROMPT` con las directrices de personalidad del asistente y el formato estricto de las acciones en JSON.

### Módulos en `shell/`

- **`shell/session.py`**: Inicia y mantiene el loop interactivo.
- **`shell/input_handler.py`**: Maneja la interacción en terminal con Prompt Toolkit, la base de historial y la compresión visual de grandes bloques de texto pegados.
- **`shell/commands.py`**: Administra el selector dialog interactivo para alternar modelos localmente instalados en Ollama.
- **`shell/command_registry.py`**: Diccionario central de comandos y alias.
- **`shell/renderer.py`**: Expone la consola compartida de Rich para el renderizado bonito.

### Módulos en `tools/`

- **`tools/filesystem/create_file.py`**: Crea archivos validando de forma segura rutas locales relativas, nombres de archivos, y permitiendo únicamente extensiones válidas de texto/código.

## Seguridad actual

MauCode no ejecuta acciones automáticamente. El modelo propone acciones estructuradas, pero el usuario siempre tiene la última palabra mediante la confirmación manual:

1. **Sí**: ejecuta solo esta acción.
2. **Sí a todo**: aprueba todas las acciones sugeridas en este turno del modelo.
3. **No, dime algo más**: deniega la acción propuesta.

## Carpeta de Pruebas Dedicada

Para realizar las simulaciones y pruebas de creación, edición o lectura de archivos por parte de los modelos mediante APIs o localmente, se debe utilizar siempre esta carpeta:
`C:\Users\Yetsin\Documents\Programacion\Ejercicios\Test-Mau-Code`

## Persistencia de Sesión

MauCode recuerda y restaura automáticamente el último modelo seleccionado de la sesión anterior (tanto de Ollama local como de APIs configuradas), guardando este estado localmente de forma segura en `api-config.json`.

## Catálogo Completo de Herramientas (18 Tools Funcionales)

Todas las 18 herramientas del catálogo están plenamente implementadas, conectadas al despachador general `core/action_executor.py` y descritas en el system prompt del modelo:
- **Herramientas de Archivo (Filesystem):** `create_file`, `read_file`, `edit_file`, `delete_file`, `move_file`, `copy_file`, `rename_file`, `create_folder`, `delete_folder`, `list_files`.
- **Herramientas de Estructura (Data):** `read_json`, `write_json`.
- **Herramientas de Control de Versiones (Git):** `git_status`, `git_diff`, `git_commit`, `git_branch`.
- **Herramientas de Búsqueda (Search):** `search_code`, `search_text`.

