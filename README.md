Estado Actual del Proyecto

Esta es la primera versión funcional de MauCode.

Actualmente, el sistema permite:

Mantener conversaciones desde la terminal.
Enviar prompts al modelo y recibir respuestas en tiempo real.
Utilizar modelos locales mediante Ollama.
Detectar respuestas en formato JSON.
Ejecutar el primer sistema básico de Tool Calling.
Crear archivos .txt desde instrucciones conversacionales.
Solicitar confirmación del usuario antes de ejecutar acciones.
Trabajar con una arquitectura modular inicial basada en tools.
Tool Calling Actual

MauCode ya cuenta con un primer sistema de tools inspirado en agentes tipo Claude Code.

Flujo actual:

Usuario
↓
Modelo propone acción en JSON
↓
MauCode valida la respuesta
↓
Usuario confirma ejecución
↓
Python ejecuta la tool

Actualmente existe la siguiente tool:

crear_archivo_texto
Arquitectura Actual
mau-code/
│
├── main.py
│
├── tools/
│   └── crear_archivo.py
│
└── ESTRUCTURA_DESEADA.md
Objetivo del Proyecto

El objetivo de MauCode es evolucionar desde un simple chat CLI hacia un agente local completo capaz de:

utilizar herramientas
manipular archivos
ejecutar comandos
trabajar con proyectos reales
comprender contexto
automatizar tareas
extender capacidades mediante plugins/tools

La meta final es tener un entorno similar a:

Claude Code

pero completamente local y personalizable.

Roadmap Inicial

Próximas metas del proyecto:

Refactorizar el sistema de tools.
Crear un router de herramientas.
Separar prompts del código Python.
Agregar memoria conversacional.
Agregar lectura y escritura de archivos.
Ejecutar comandos de terminal.
Crear sistema de permisos más avanzado.
Implementar streaming de respuestas.
Crear comando global:
maucode
Tecnologías Utilizadas
Backend
Python
Modelos
Ollama
Qwen2.5-Coder:7B
Terminal UI
Rich
Filosofía del Proyecto

MauCode NO ejecuta acciones automáticamente.

Toda acción sensible debe seguir este flujo:

Modelo propone acción
↓
Usuario confirma
↓
MauCode ejecuta

La seguridad y el control del usuario son prioridad.

Estado

🚧 Proyecto en desarrollo temprano.

Actualmente el enfoque principal es construir una arquitectura sólida, modular y escalable antes de agregar funcionalidades avanzadas.