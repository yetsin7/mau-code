# MauCode

MauCode es un asistente local de programacion que corre desde la terminal,
conversa con un modelo de Ollama y ejecuta tools bajo confirmacion del usuario.
El proyecto esta en una etapa temprana, pero ya tiene una separacion inicial
entre la sesion de terminal, el renderizado, la entrada del usuario y el
catalogo de tools.

## Estado actual

Actualmente MauCode puede:

- iniciar una sesion de chat desde `main.py`;
- enviar mensajes a Ollama usando el modelo `qwen2.5-coder:7b`;
- renderizar respuestas con Rich;
- leer entrada interactiva con Prompt Toolkit;
- guardar historial local en `.maucode_history`;
- compactar pegados multilínea en placeholders visuales antes de enviarlos al modelo;
- detectar una o varias acciones JSON devueltas por el modelo;
- pedir confirmacion antes de ejecutar una accion sensible;
- crear archivos de texto o codigo mediante `tools/filesystem/create_file.py`.

La unica tool funcional conectada al flujo principal es `create_file`. Las demas
carpetas y archivos de `tools/` existen como estructura preparada para futuras
tools, pero varios modulos todavia estan vacios.

## Requisitos

MauCode depende de Python y de librerias usadas directamente por el codigo
actual:

- Python 3.13 o compatible;
- Ollama instalado y ejecutandose localmente;
- modelo `qwen2.5-coder:7b` disponible en Ollama;
- paquetes de Python: `ollama`, `rich` y `prompt_toolkit`.

Instalacion manual de dependencias:

```bash
pip install ollama rich prompt_toolkit
```

## Ejecucion

Desde la raiz del proyecto:

```bash
python main.py
```

Para salir de la sesion escribe:

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

Los directorios `__pycache__/` son artefactos generados por Python y no forman
parte de la arquitectura fuente del proyecto.

## Flujo principal

```txt
Usuario
↓
shell.input_handler.read_user_input()
↓
main.ask_ollama()
↓
Ollama responde texto o JSON
↓
main.handle_model_response()
↓
MauCode pide confirmacion si hay accion
↓
tools.filesystem.create_file.create_file()
↓
Resultado vuelve a la terminal
```

## Modulos principales

### `main.py`

Contiene el prompt del sistema, la comunicacion con Ollama, el parser de
acciones JSON y el despacho inicial de tools. Actualmente solo despacha la
accion `create_file`.

### `shell/session.py`

Inicia y mantiene el loop principal de la sesion interactiva. Lee mensajes,
detecta el comando `salir`, envia prompts al modelo y delega el manejo de la
respuesta.

### `shell/input_handler.py`

Centraliza la entrada del usuario con Prompt Toolkit. Mantiene historial local
en `.maucode_history` y reemplaza pegados multilínea por placeholders visibles
para que la terminal siga siendo legible.

### `shell/renderer.py`

Expone una instancia compartida de `rich.console.Console` para renderizar la
salida de MauCode.

### `tools/filesystem/create_file.py`

Crea archivos de texto o codigo en la carpeta indicada por el usuario. Valida
el nombre del archivo, bloquea rutas embebidas en `file_name` y permite solo
extensiones de texto/codigo incluidas en `ALLOWED_TEXT_EXTENSIONS`.

## Seguridad actual

MauCode no ejecuta acciones automaticamente. El modelo puede proponer una
accion JSON, pero el usuario debe confirmarla antes de que Python ejecute la
tool.

La tool `create_file` aplica validaciones basicas:

- bloquea `..`, `/` y `\` dentro del nombre del archivo;
- restringe las extensiones permitidas;
- escribe contenido con codificacion UTF-8.

## Limites actuales

- No existe todavia un router general de tools.
- No hay memoria persistente mas alla del historial de terminal.
- No hay `requirements.txt`, instalador ni comando global `maucode`.
- No hay pruebas automatizadas.
- Varias tools declaradas en carpetas estan vacias y pendientes de implementar.
- El prompt del sistema todavia vive dentro de `main.py`.

## Direccion tecnica recomendada

Las siguientes mejoras deben hacerse manteniendo modulos pequenos y
responsabilidades separadas:

- extraer el prompt del sistema fuera de `main.py`;
- crear un router de tools con validacion por accion;
- implementar tools vacias una por una con permisos explicitos;
- agregar pruebas enfocadas para parser JSON, confirmaciones y filesystem;
- crear un archivo de dependencias;
- mantener la documentacion sincronizada con la estructura real del repo.
