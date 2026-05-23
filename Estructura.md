# MauCode - Estructura real del proyecto

Este documento describe la estructura que existe actualmente en `C:\Dev\mau-code`.
No es una estructura deseada ni un roadmap: es el mapa real del working tree
fuente que MauCode usa hoy.

## Arbol fuente actual

```txt
mau-code/
├── .maucode_history
├── Estructura.md
├── README.md
├── main.py
├── shell/
│   ├── input_handler.py
│   ├── paste_handler.py
│   ├── renderer.py
│   ├── run_python.py
│   ├── run_terminal.py
│   ├── session.py
│   └── streaming.py
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

## Archivos generados

Python tambien genera carpetas `__pycache__/` con archivos `.pyc`. Esos archivos
no son parte de la arquitectura fuente y no deben usarse para entender el diseno
del proyecto.

## Responsabilidades por modulo

### `main.py`

Responsabilidad actual:

- define `MODEL_NAME`;
- mantiene `SYSTEM_PROMPT`;
- envia mensajes a Ollama en `ask_ollama()`;
- detecta acciones JSON en `try_parse_json_actions()`;
- procesa respuestas normales o acciones en `handle_model_response()`;
- conecta el loop de terminal con `start_terminal_session()`.

Riesgo principal:

- concentra prompt, comunicacion con el modelo, parsing JSON y despacho de tools
  en un solo archivo. Sigue funcionando, pero sera el primer candidato natural
  para refactor cuando crezca el numero de tools.

### `shell/input_handler.py`

Responsabilidad actual:

- crea una sesion reutilizable de Prompt Toolkit;
- guarda historial en `.maucode_history`;
- detecta pegados multilínea con `Keys.BracketedPaste`;
- reemplaza pegados grandes por placeholders visibles;
- reconstruye el mensaje completo antes de enviarlo al modelo.

Detalle importante:

- el usuario ve un input limpio, pero MauCode recibe el texto completo pegado.

### `shell/session.py`

Responsabilidad actual:

- imprime el saludo inicial;
- mantiene el loop interactivo;
- lee el mensaje del usuario;
- corta la sesion con `salir`;
- delega la llamada al modelo y el manejo de la respuesta.

### `shell/renderer.py`

Responsabilidad actual:

- expone una instancia compartida de `Console` de Rich.

### `shell/paste_handler.py`

Estado actual:

- archivo vacio.

Uso esperado:

- puede recibir en el futuro la logica de paste que hoy vive dentro de
  `shell/input_handler.py`, si se decide separar esa responsabilidad.

### `shell/run_python.py`

Estado actual:

- archivo vacio.

Uso esperado:

- punto de extension para ejecucion controlada de scripts Python.

### `shell/run_terminal.py`

Estado actual:

- archivo vacio.

Uso esperado:

- punto de extension para ejecucion controlada de comandos de terminal.

### `shell/streaming.py`

Estado actual:

- archivo vacio.

Uso esperado:

- punto de extension para streaming de respuestas del modelo.

## Tools actuales

### `tools/filesystem/create_file.py`

Estado actual:

- implementado.

Responsabilidad:

- crear carpetas cuando sea necesario;
- crear archivos de texto o codigo;
- validar que `file_name` no incluya rutas embebidas;
- restringir extensiones permitidas;
- escribir el contenido con UTF-8.

Accion conectada al flujo principal:

```json
{
  "action": "create_file",
  "folder": "RUTA_EXACTA_DE_LA_CARPETA",
  "file_name": "NOMBRE_DEL_ARCHIVO_CON_EXTENSION",
  "content": "TEXTO_QUE_SE_GUARDARA"
}
```

### `tools/filesystem/*.py`

Archivos existentes:

- `copy_file.py`
- `create_folder.py`
- `delete_file.py`
- `delete_folder.py`
- `edit_file.py`
- `list_files.py`
- `move_file.py`
- `read_file.py`
- `rename_file.py`

Estado actual:

- existen como modulos, pero estan vacios.

### `tools/git/*.py`

Archivos existentes:

- `git_branch.py`
- `git_commit.py`
- `git_diff.py`
- `git_status.py`

Estado actual:

- existen como modulos, pero estan vacios.

### `tools/search/*.py`

Archivos existentes:

- `search_code.py`
- `search_text.py`

Estado actual:

- existen como modulos, pero estan vacios.

### `tools/data/*.py`

Archivos existentes:

- `read_json.py`
- `write_json.py`

Estado actual:

- existen como modulos, pero estan vacios.

## Flujo de ejecucion actual

```txt
python main.py
↓
main.start_terminal_session()
↓
shell.session.start_terminal_session()
↓
shell.input_handler.read_user_input()
↓
main.ask_ollama()
↓
Ollama responde texto o acciones JSON
↓
main.handle_model_response()
↓
si hay accion create_file, MauCode pide confirmacion
↓
tools.filesystem.create_file.create_file()
↓
resultado renderizado en terminal con Rich
```

## Estructura que no existe actualmente

La estructura anterior mencionaba carpetas que todavia no estan presentes en el
repo. Actualmente no existen:

- `core/`
- `prompts/`
- `storage/`
- `docs/`
- `tests/`
- `scripts/`
- `requirements.txt`
- `maucode.bat`

Esos nombres pueden seguir siendo ideas validas para el futuro, pero no deben
presentarse como estructura real del proyecto mientras no existan en el repo.

## Reglas de mantenimiento de estructura

- Documentar solo carpetas y archivos reales.
- Marcar claramente los modulos vacios como pendientes.
- No presentar herramientas no conectadas como funcionales.
- Mantener una tool por archivo.
- Mantener `main.py` como punto de entrada hasta que exista un modulo `core/`.
- Crear pruebas antes de ampliar acciones sensibles como terminal, Git o borrado.
- Actualizar este archivo cada vez que se cree, elimine o mueva un modulo fuente.
