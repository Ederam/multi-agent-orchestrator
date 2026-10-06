# Hoja de Ruta del Proyecto: Sistema Multi-Agente con IA (AI-MultiAgent-Core)

## 1. Visión General

Construir una plataforma autónoma multi-agente basada en grafos de estado (StateGraph) utilizando Python y LangGraph, aplicando Clean Architecture, observabilidad y patrones de ejecución deterministas para incidentes de infraestructura backend.

---

## 2. Fases de Desarrollo y Estado de Entrega

### Fase 1: Fundamentos de Orquestación y Grafos de Estado [COMPLETADA]

- [x] Modelado de estado inmutable (`AgentState`) con tipado estricto y reducers (`Annotated[List, operator.add]`).
- [x] Implementación de nodos deterministas (normalización, validación, autocorrección).
- [x] Enrutamiento condicional (`conditional_edges`) para bucles de autocorrección (_Self-Correction Loop_).
- [x] Modularización bajo Clean Architecture (`core`, `services`, `nodes`, `workflow`).
- [x] Adaptador de infraestructura desacoplado con modo Sandbox seguro para entornos corporativos.
- [x] Repositorio Git inicializado y vinculado con GitHub remoto.

### Fase 2: Construcción del Primer Sistema Multi-Agente Autónomo [COMPLETADA]

- [x] **Agente Router / Clasificador:** Analiza la intención semántica del mensaje.
- [x] **Agente Consultor (Tool Executor):** Implementación de Tool Calling con invocación de `query_service_metrics`.
- [x] **Agente Analista / Sintetizador (Incident Reporter):** Transforma el payload crudo de telemetría en un reporte estructurado.
- [x] **Agente Notificador:** Formatea y despacha la alerta automática hacia canales externos.

### Fase 3: Evaluación, Supervisión y Human-in-the-loop (HITL) [PENDIENTE]

- [ ] **Persistencia y Checkpointers:** Implementación de memoria de estado con `MemorySaver` / SQLite.
- [ ] **Human-in-the-loop (HITL):** Puntos de interrupción (_interrupt_before_) para aprobación humana antes de acciones críticas (ej. reiniciar servicios o reiniciar pods).
- [ ] **Observabilidad y Trazabilidad:** Monitoreo de latencias, auditoría y métricas de ejecución.
