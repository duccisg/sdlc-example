# Plataforma de ciclo de vida de desarrollo de software

Esta solución define una plataforma de orquestación multi-agente para cubrir todo el ciclo de vida de desarrollo de software (SDLC) desde la captura de requerimientos hasta la retrospectiva. La arquitectura se construye sobre **LangChain**, **LangGraph** y **LangFuse** (interpretado a partir de la solicitud original que mencionaba "languse").

## Componentes principales

- `backend/`: API basada en FastAPI que encapsula los agentes, el grafo de orquestación (LangGraph) y la integración con LangFuse para trazas/observabilidad.
- `frontend/`: Aplicación React (Vite) agnóstica al backend que permite iniciar flujos, revisar el trabajo de los agentes y confirmar cada fase antes de continuar.

## Flujo de trabajo SDLC

1. **Captura de requerimientos** – agente de negocio analiza la entrada inicial.
2. **Análisis** – agente de arquitectura define dominio y riesgos.
3. **Diseño** – agente de diseño genera blueprint de la solución.
4. **Implementación** – agente técnico propone guías y scaffolding.
5. **Pruebas** – agente QA diseña planes y estrategias de testing.
6. **Despliegue** – agente DevOps planifica pipeline, infra y observabilidad.
7. **Retrospectiva** – agente agile resume aprendizajes; cierre sin confirmación adicional.

Cada etapa espera confirmación del usuario antes de avanzar, y permite adjuntar contexto adicional previo a ejecutar el siguiente agente.

## Configuración del backend

1. Crear y activar un entorno virtual.
2. Instalar dependencias:

   ```bash
   cd backend
   pip install -e .
   ```

3. Variables de entorno relevantes (opcional según el proveedor en uso):

   - `OPENAI_API_KEY` – habilita respuestas reales con ChatGPT.
   - `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` – para trazas.
   - `REDIS_URL`, `DATABASE_URL` – ganchos listos si se requiere persistencia externa.

4. Ejecutar la API:

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   Sin llave de OpenAI se usa un modelo stub determinístico que devuelve mensajes de marcador de posición.

## Configuración del frontend

1. Instalar dependencias:

   ```bash
   cd frontend
   npm install
   ```

2. Servir en desarrollo:

   ```bash
   npm run dev
   ```

   Vite queda disponible en `http://localhost:5173` con proxy preparado para `http://localhost:8000/api`.

## Integración y extensión

- Los agentes se registran en `app/services/agent_manager.py`; es posible reemplazar cualquier fase inyectando una implementación personalizada.
- El grafo de orquestación (`app/workflows/sdlc_graph.py`) usa LangGraph para manejar estados y confirmaciones.
- `WorkflowOrchestrator` mantiene el estado en memoria; para producción se sugiere persistir en Redis o base de datos aprovechando los hooks ya previstos en configuración.
- LangFuse es opcional pero listo para usar si se proporcionan credenciales válidas.

## Próximos pasos sugeridos

- Añadir soporte para adjuntos (voz, archivos) transformándolos a texto antes de invocar el primer agente.
- Persistir estados en una base de datos o caché para resiliencia y colaboración multiusuario.
- Incorporar tests automatizados para cada agente y para el flujo end-to-end.
- Extender el frontend con visualizaciones de dependencias, métricas o paneles de LangFuse.
