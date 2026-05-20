# MauCode — Estructura Deseada del Proyecto

Este documento define la arquitectura deseada de MauCode.

La idea es construir un agente tipo Claude Code
utilizando Ollama y herramientas locales.

---

# Objetivos del Proyecto

MauCode deberá poder:

- Conversar con modelos locales usando Ollama.
- Ejecutar tools de forma segura.
- Pedir confirmación antes de ejecutar acciones.
- Leer y escribir archivos.
- Ejecutar comandos de terminal.
- Trabajar dentro de proyectos de programación.
- Tener memoria y contexto.
- Funcionar desde CMD usando:

```bash
maucode
```

---

# Estructura General Deseada

```txt
MauCode/
│
├── main.py
│
├── core/
│   ├── agent.py
│   ├── chat.py
│   ├── permissions.py
│   ├── memory.py
│   ├── json_parser.py
│   └── tool_router.py
│
├── tools/
│   ├── crear_archivo.py
│   ├── leer_archivo.py
│   ├── escribir_archivo.py
│   ├── ejecutar_terminal.py
│   ├── buscar_codigo.py
│   └── listar_archivos.py
│
├── prompts/
│   ├── system_prompt.txt
│   ├── tool_prompt.txt
│   └── personality_prompt.txt
│
├── storage/
│   ├── chats/
│   ├── memory/
│   ├── logs/
│   └── cache/
│
├── docs/
│   ├── arquitectura.md
│   ├── ideas.md
│   ├── roadmap.md
│   └── seguridad.md
│
├── tests/
│   ├── test_tools.py
│   ├── test_permissions.py
│   └── test_memory.py
│
├── scripts/
│   ├── install.bat
│   ├── setup.ps1
│   └── start.bat
│
├── .venv/
│
├── maucode.bat
│
├── requirements.txt
│
├── README.md
│
└── ESTRUCTURA_DESEADA.md
```

---

# Explicación de Carpetas

## core/

Contendrá la lógica principal del agente.

Aquí vivirá:

- manejo del chat
- memoria
- permisos
- parsing de JSON
- routing de tools
- agent loop
- historial de conversación

---

## tools/

Cada tool estará separada en su propio archivo.

Ejemplo:

```txt
crear_archivo.py
```

Ventajas:

- código limpio
- más fácil mantener
- fácil agregar nuevas tools
- más parecido a Claude Code

Cada tool deberá tener:

- validación
- permisos
- logs
- manejo de errores

---

## prompts/

Aquí vivirán los prompts grandes del sistema.

Ventajas:

- evitar prompts gigantes dentro de Python
- editar prompts sin tocar código
- separar lógica y comportamiento

Ejemplos:

```txt
system_prompt.txt
tool_prompt.txt
```

---

## storage/

Guardará:

- historial de chats
- memoria
- logs
- cache
- configuraciones

---

## docs/

Documentación técnica del proyecto.

Aquí iremos escribiendo:

- arquitectura
- ideas futuras
- decisiones técnicas
- notas de seguridad

---

## tests/

Pruebas automáticas del sistema.

Ejemplos:

- verificar tools
- probar permisos
- evitar bugs

---

## scripts/

Scripts para instalación y automatización.

Ejemplos:

```txt
install.bat
start.bat
```

---

# Flujo Correcto del Sistema

MauCode NO ejecuta cosas automáticamente.

Flujo correcto:

```txt
Usuario
↓
Modelo propone acción
↓
MauCode valida
↓
Usuario confirma
↓
Python ejecuta
↓
Resultado vuelve al modelo
```

---

# Filosofía del Proyecto

La idea NO es hacer un simple chatbot.

La idea es crear:

```txt
un agente de terminal real
```

capaz de:

- trabajar con código
- editar proyectos
- usar tools
- entender contexto
- automatizar tareas

---

# Objetivo Final

Poder abrir cualquier terminal y ejecutar:

```bash
maucode
```

y que automáticamente:

- se inicie el agente
- cargue el modelo de Ollama
- tenga acceso a tools
- recuerde el contexto
- funcione como Claude Code

---

# Stack Tecnológico Inicial

## Lenguaje principal

```txt
Python
```

Porque:

- rápido para prototipar
- excelente para IA
- muy compatible con Ollama
- fácil crear tools locales

---

## Modelos

Usaremos Ollama.

Ejemplo:

```txt
qwen2.5-coder:7b
```

---

## Terminal UI

Usaremos:

```txt
Rich
```

y posiblemente después:

```txt
Textual
```

---

# Posibles Mejoras Futuras

## Sistema de memoria

Guardar conversaciones y contexto.

---

## RAG local

Buscar información dentro de proyectos.

---

## Multiagentes

Sub-agentes especializados.

---

## Integración VSCode

Extensión personalizada.

---

## MCP (Model Context Protocol)

Compatibilidad con herramientas externas.

---

## Plugin System

Sistema de extensiones.

---

## Tool Marketplace

Instalar tools externas.

---

# Reglas de Desarrollo

- Mantener código modular.
- Una tool por archivo.
- Explicar el código paso a paso.
- Evitar archivos gigantes.
- Refactorizar constantemente.
- Separar prompts del código.
- Mantener permisos seguros.

---

# Estado Actual del Proyecto

Actualmente MauCode puede:

- conversar con Ollama
- detectar JSON
- preparar tool calling
- pedir confirmación antes de ejecutar acciones

Próximo objetivo:

```txt
mover tools a carpeta tools/
```

y crear el primer router de herramientas.