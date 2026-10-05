### Archivo: `Lecciones_Aprendidas.md`

```markdown
# Lecciones Aprendidas y Registros de Decisiones de Arquitectura (ADR)

## ADR-001: Configuración del Entorno Virtual y Launcher en Windows

- **Contexto:** Al ejecutar `python -m venv .venv` en PowerShell, el sistema respondió con un error de acceso directo a Microsoft Store debido a que `python.exe` no estaba mapeado prioritariamente en las variables de entorno (`PATH`).
- **Decisión:** Utilizar el ejecutable `py` (Python Launcher oficial para Windows) para instanciar el entorno virtual.
- **Consecuencia:** Garantiza la invocación correcta del intérprete sin alterar las políticas globales del SO.

## ADR-002: Ejecución de Scripts y Alias de Shell en PowerShell

- **Diferencias de Shell:** El comando `source` es nativo de entornos POSIX (Linux/macOS). En Windows PowerShell la activación se realiza mediante la ruta directa `.\.venv\Scripts\Activate.ps1`.
- **Politica de Ejecución:** Para permitir scripts `.ps1` locales no firmados, se requirió elevar la política a nivel de usuario:
  `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.
```

## ADR-003: Implementación de Enrutamiento Dinámico con Aristas Condicionales

- **Contexto:** Se requiere que el flujo del sistema no sea puramente secuencial, sino que tome decisiones de ramificación basadas en la inspección del estado (`AgentState`).
- **Decisión:** Implementar funciones puras de enrutamiento (_Router_) y enlazarlas mediante `workflow.add_conditional_edges()`.
- **Consecuencia:**
  1. Permite bifurcar la ejecución hacia nodos especializados (`tech_support` vs `general_info`).
  2. La función del router mapea cadenas de caracteres a los identificadores exactos de los nodos de destino registrados en el grafo.
