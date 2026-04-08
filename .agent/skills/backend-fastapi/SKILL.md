---
name: backend-fastapi-neocafe
description: Use this skill when creating or modifying FastAPI endpoints, services, or AI adapters for the NeoCafeIA chatbot project using hexagonal architecture, factory pattern, and Gemini or multi-provider AI integrations.
compatibility:
  - Python 3.12+
  - FastAPI
  - Pydantic v2
metadata:
  author: equipo-neocafe
  version: "1.0"
---

# Objetivo
Construir y mantener el backend del chatbot NeoCafeIA usando FastAPI,
arquitectura hexagonal, separación de capas y adaptadores de IA.

# Instrucciones
1. Separar el código en capas: domain, services, infrastructure.
2. Usar Pydantic para validación de datos.
3. Implementar servicios desacoplados en `services/`.
4. Usar factory pattern para seleccionar el proveedor de IA.
5. Cargar contexto dinámico desde archivos en `knowledge/`.
6. Mantener endpoints simples en `app.py`.

# Ejemplos

## Crear endpoint
Input:
"Crea un endpoint para listar productos"

Output:
- Endpoint en app.py
- Lógica en services/
- Schema en domain/

# Restricciones
- NUNCA hardcodear API keys
- NUNCA mezclar capas en un mismo archivo
- NO usar if/else para seleccionar modelos (usar factory)
- NO poner lógica de negocio en app.py
