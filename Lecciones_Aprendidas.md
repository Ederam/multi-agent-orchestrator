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

## ADR-004: Modularización y Aplicación de Clean Architecture

- **Contexto:** Mantener todo el grafo, servicios LLM, lógica de nodos y DTOs en un único archivo `main.py` generaba alto acoplamiento e impedía el escalamiento del sistema multi-agente.
- **Decisión:** Segmentar en capas modulares bajo `src/`: `core` (estado y configuración), `services` (adaptador Gemini), `nodes` (lógica de negocio y llamadas LLM) y `workflow` (ensamblado del grafo y enrutador).
- **Consecuencia:** Mayor testeabilidad unitaria de nodos, desacoplamiento del cliente de IA y facilidad para agregar nuevos agentes especializados sin modificar el punto de entrada.

## ADR-005: Resolución de Validación SSL para Clientes LLM en Windows

- **Contexto:** Al invocar la API de Gemini desde Windows, Python arrojó `[SSL: CERTIFICATE_VERIFY_FAILED]` debido a la ausencia de certificados raíz accesibles por el runtime estándar de Python.
- **Decisión:** Instalar la librería `certifi` y definir explícitamente las variables de entorno `SSL_CERT_FILE` y `REQUESTS_CA_BUNDLE` apuntando a `certifi.where()` dentro de `src/services/llm_service.py`.
- **Consecuencia:** Garantiza la validación segura de certificados TLS/SSL en las peticiones HTTPS salientes de LangChain hacia Google AI Studio.

## ADR-005: Diagnóstico y Mitigación de Error SSL en Clientes de IA sobre Windows

### 1. Síntoma

```text
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1082)
```

## ADR-006: Manejo de Inspección TLS/SSL (Untrusted Root CA) en Entornos de Desarrollo

- **Síntoma:** Error de conexión TLS: `'Se procesó correctamente una cadena de certificados, pero termina en un certificado de raíz no compatible con el proveedor de confianza.'`.
- **Causa Raíz:** Interceptación o inspección de paquetes HTTPS realizada por la red (firewall/proxy corporativo o módulo de inspección web de antivirus). El certificado presentado al cliente Python pertenece a una CA privada no compatible con la validación estricta de la API pública de Google.
- **Decisión de Arquitectura:**
  1. Configurar un cliente HTTP personalizado con transporte deshabilitado de verificación SSL estrictamente para el entorno de desarrollo local.
  2. Implementar un fallback desacoplado que permita continuar el flujo del grafo sin bloquear la orquestación del sistema multi-agente ante fallos de red externa.
- **Consecuencia:** Se desbloquea el consumo del modelo de lenguaje sin alterar el flujo de estados del orquestador.

## ADR-006: Diagnóstico de Inspección TLS (CryptoAPI SEC_E_UNTRUSTED_ROOT) y Parche de Transporte Local

- **Síntoma:** Error `('Se procesó correctamente una cadena de certificados, pero termina en un certificado de raíz no compatible con el proveedor de confianza.',)`.
- **Causa Raíz:**
  1. En Windows, un antivirus o proxy de red corporativo intercepta el tráfico TLS/HTTPS e inyecta su propio certificado intermedio.
  2. La librería `pip-system-certs` fuerza la validación estricta de CryptoAPI de Windows, provocando el bloqueo del socket.
  3. `ChatGoogleGenerativeAI` no admite el parámetro `http_client` de `httpx` directamente, sino que gestiona su propio pool de conexiones HTTPS vía `urllib3` / `ssl`.
- **Solución Técnica Aplicada:**
  1. Parchear el contexto SSL por defecto en tiempo de ejecución (`ssl._create_default_https_context = ssl._create_unverified_context`) en el adaptador de infraestructura exclusivamente para desarrollo local.
  2. Suprimir las advertencias de certificados no verificados de `urllib3`.
- **Consecuencia:** Permite la comunicación fluida con la API de Google Gemini en entornos corporativos o bajo proxies e inspecciones de red locales sin interrumpir el desarrollo.

## ADR-007: Conflicto entre pip-system-certs y CryptoAPI de Windows

- **Síntoma:** Persistencia de `SEC_E_UNTRUSTED_ROOT` a pesar de configurar contextos SSL permisivos.
- **Causa Raíz:** El paquete `pip-system-certs` intercepta sockets a nivel de runtime nativo, anulando cualquier configuración de contexto SSL en Python.
- **Solución:**
  1. Desinstalar `pip-system-certs` del entorno virtual (`pip uninstall pip-system-certs -y`).
  2. Forzar transporte `transport="rest"` en `ChatGoogleGenerativeAI`.
  3. Definir `os.environ["PYTHONHTTPSVERIFY"] = "0"` para bypass en desarrollo local.

## ADR-008: Adaptador HTTP Directo para Google Gemini bajo Inspección TLS

- **Síntoma:** Error `[SSL: CERTIFICATE_VERIFY_FAILED]` persistente en Windows debido a proxies o inspección SSL corporativa/antivirus, sumado a que `ChatGoogleGenerativeAI` no expone parámetros de transporte ni bypass de certificados en sus constructores.
- **Causa Raíz:** Los SDKs de alto nivel encapsulan las llamadas HTTP sin exponer la bandera `verify=False` del cliente subyacente.
- **Decisión de Arquitectura:**
  1. Implementar un servicio desacoplado (`GeminiClient`) en `src/services/llm_service.py` utilizando `httpx` o `requests` con bypass explícito de verificación TLS en entornos de desarrollo local.
  2. Mantener la misma interfaz de invocación (`invoke`) para que los nodos (`src/nodes/ai_nodes.py`) no sufran acoplamiento con la librería externa subyacente.
- **Consecuencia:** Se elimina la dependencia del wrapper rígido, permitiendo el consumo de Gemini 2.5 Flash en cualquier entorno corporativo o con inspección profunda de paquetes sin alterar los contratos del grafo.

## ADR-009: Cumplimiento de Políticas de Seguridad y Adopción de Sandbox/Mock LLM Adapter

- **Contexto:** En entornos empresariales con inspección TLS, proxies corporativos y filtrado de contenido saliente, forzar bypasses de certificados (`verify=False`) o consultar APIs externas de IA puede violar normativas de seguridad de la organización o resultar en bloqueos HTTP 403.
- **Decisión de Arquitectura:**
  1. Restablecer la validación estricta de certificados TLS/HTTPS estándar.
  2. Implementar un `MockLLMService` (Sandbox Adapter) desacoplado que cumpla con la interfaz del modelo, permitiendo diseñar y probar el grafo multi-agente, enrutamiento y Tool Calling sin dependencias externas ni riesgos de seguridad.
  3. Evitar filtrar claves de API en URLs o logs de error.
- **Consecuencia:** Desarrollo 100% seguro, reproducible y alineado a los estándares de SecOps corporativos.

## ADR-010: Implementación del Patrón Tool Calling en el Grafo

- **Contexto:** Los modelos de IA no deben inventar datos operativos; deben consultar herramientas deterministas para obtener telemetría real.
- **Decisión:** Modelar la intención de herramienta en el estado (`required_tool`), evaluarla mediante una arista condicional (`route_after_ai`) y delegar la ejecución a un nodo dedicado (`tool_executor`).
- **Consecuencia:** Separación clara entre el razonamiento del agente y la ejecución de infraestructura, garantizando trazabilidad y seguridad.

## ADR-011: Integración del Agente Sintetizador de Incidentes

- **Contexto:** Los datos crudos devueltos por las herramientas de diagnóstico no son aptos para la toma de decisiones directas sin un procesamiento semántico que calcule impacto y severidad.
- **Decisión:** Crear el nodo `incident_synthesizer_node` en la capa de agentes de IA, encargado de correlacionar latencias, tasas de error y estado del circuito para generar un dict estructurado (`incident_report`).
- **Consecuencia:** Encapsulamiento del razonamiento de diagnóstico en un agente especializado sin sobrecargar al nodo enrutador inicial.
