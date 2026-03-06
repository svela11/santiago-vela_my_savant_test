# Statement of Work (SOW) - MVP Agente Conversacional de Logística

## Alcance del Proyecto

### Objetivo Principal
Desarrollar un MVP (Minimum Viable Product) de un agente conversacional para operaciones logísticas que permita a los clientes consultar estados de envíos, reprogramar entregas y reportar incidencias a través de una interfaz de chat inteligente.

### Funcionalidades Incluidas

#### 1. Agente Conversacional
- **Detección de intenciones**: Clasificación automática de mensajes en 4 categorías principales
  - Saludos y conversación general
  - Consulta de estado de envíos
  - Reprogramación de entregas
  - Reporte de incidencias
- **Extracción de entidades**: Identificación automática de IDs de envío, fechas, horas y tipos de problemas
- **Configuración por cliente**: Personalización de tono, idioma y políticas según cliente específico

#### 2. Mock API Server
- **Endpoints RESTful**: 
  - `GET /shipments/{id}` - Consulta de información de envíos
  - `POST /shipments/{id}/reschedule` - Reprogramación de entregas
  - `POST /tickets` - Creación de tickets de incidencia
  - `GET /tickets/{id}` - Consulta de tickets
  - `GET /health` - Health check del sistema
- **Datos reales**: Procesamiento de 74+ envíos desde archivo JSON proporcionado
- **Validación**: Esquemas Pydantic para validación de entrada y salida

#### 3. Interfaz de Usuario
- **Chat web**: Interfaz Streamlit con chat interactivo
- **Monitoreo**: Estado en tiempo real de servicios (API + Ollama)
- **Configuración**: Selector de cliente con diferentes configuraciones
- **Ejemplos**: Casos de uso integrados para facilitar pruebas

#### 4. Integración LLM Local
- **Ollama**: Integración con LLM local completamente gratuito
- **Modelos soportados**: llama3.2, mistral y otros modelos compatibles
- **Políticas anti-alucinación**: Respuestas basadas únicamente en datos verificados

### Arquitectura WAT Framework

#### Workflows (Procedimientos)
- Documentación detallada en Markdown para cada flujo de trabajo
- Manejo de errores específico por tipo de operación
- Criterios de éxito y escalamiento definidos

#### Agents (Orquestación)
- Agente principal que coordina LLM, API y configuraciones
- Estado de conversación persistente durante la sesión
- Manejo inteligente de datos faltantes

#### Tools (Herramientas)
- Scripts Python modulares y reutilizables
- Separación clara de responsabilidades
- Interfaces bien definidas entre componentes

## Supuestos del Proyecto

### Técnicos
1. **Entorno de desarrollo**: macOS con Python 3.8+
2. **Conectividad**: Acceso a localhost para servicios (puertos 8000, 8502, 11434)
3. **Recursos**: Suficiente memoria RAM para ejecutar modelo LLM local (mínimo 8GB recomendado)
4. **Datos**: Archivo JSON de envíos proporcionado contiene datos válidos y representativos

### Operacionales
1. **Usuarios**: Personal técnico capaz de ejecutar comandos básicos de terminal
2. **Tiempo de setup**: Máximo 10 minutos para instalación completa
3. **Disponibilidad**: Sistema diseñado para demostración, no para producción 24/7
4. **Escalabilidad**: MVP diseñado para validar concepto, no para carga masiva

### De Negocio
1. **Clientes**: Al menos 2 configuraciones de cliente diferentes (formal/amigable)
2. **Idioma**: Soporte principal en español
3. **Intenciones**: Limitado a 3 intenciones principales de logística
4. **Datos**: Información de envíos es mock/demo, no datos de producción reales

## Fuera de Alcance

### Funcionalidades No Incluidas
1. **Autenticación y autorización**: Sin sistema de login/usuarios
2. **Base de datos persistente**: Datos en memoria/archivos JSON únicamente
3. **Integración con sistemas reales**: Solo Mock API, no ERP/WMS reales
4. **Notificaciones**: Sin email, SMS o push notifications
5. **Reportes y analytics**: Sin dashboards o métricas de negocio
6. **Multi-idioma**: Solo español, sin internacionalización
7. **Integración con servicios de terceros**: Sin APIs externas (transportistas, etc.)

### Aspectos Técnicos Excluidos
1. **Seguridad avanzada**: Sin encriptación, rate limiting o protección DDoS
2. **Monitoreo de producción**: Sin logging centralizado, métricas o alertas
3. **CI/CD**: Sin pipelines de despliegue automatizado
4. **Testing automatizado**: Sin suite completa de pruebas unitarias/integración
5. **Documentación de API**: Más allá de FastAPI docs automáticas
6. **Optimización de performance**: Sin caching, CDN o optimizaciones avanzadas

### Limitaciones de Datos
1. **Volumen**: Optimizado para dataset de prueba (~100 envíos máximo)
2. **Tiempo real**: Sin sincronización con sistemas de tracking reales
3. **Historiales**: Sin persistencia de conversaciones entre sesiones
4. **Backup/Recovery**: Sin estrategias de respaldo de datos

## Criterios de Éxito

### Funcionales
- ✅ Detección correcta de las 3 intenciones principales (>90% precisión)
- ✅ Consulta exitosa de información de envíos desde Mock API
- ✅ Reprogramación de entregas con validación de datos
- ✅ Creación de tickets de incidencia con información completa
- ✅ Diferenciación clara entre configuraciones de cliente

### Técnicos
- ✅ Setup completo en ≤10 minutos
- ✅ Uso exclusivo de herramientas gratuitas
- ✅ Respuesta del sistema en <5 segundos para consultas normales
- ✅ Manejo graceful de errores sin crashes del sistema
- ✅ Documentación completa y ejecutable

### De Experiencia
- ✅ Interfaz intuitiva sin necesidad de entrenamiento
- ✅ Respuestas naturales y contextualmente apropiadas
- ✅ Manejo claro de casos donde faltan datos
- ✅ Escalamiento apropiado para casos no manejables

## Entregables

### Código
- Agente conversacional (`tools/conversation_agent.py`)
- Mock API Server (`tools/mock_api_server.py`)
- Interfaz LLM (`tools/llm_interface.py`)
- Aplicación Streamlit (`app.py`)

### Configuración
- Templates de cliente (`config/*.json`)
- Variables de entorno (`.env.example`)
- Dependencias (`requirements.txt`)

### Documentación
- README.md con instrucciones completas
- Workflows en Markdown (`workflows/*.md`)
- Documentación técnica (`docs/*.md`)
- Ejemplos de conversaciones

### Evidencias
- Conversaciones de prueba documentadas
- Screenshots de la interfaz funcionando
- Logs de ejemplo del sistema

## Timeline y Recursos

### Fases de Desarrollo
1. **Fase 1**: Arquitectura y Mock API (Completado)
2. **Fase 2**: Agente conversacional e integración LLM (Completado)
3. **Fase 3**: Interfaz de usuario y configuraciones (Completado)
4. **Fase 4**: Documentación y evidencias (En progreso)

### Recursos Utilizados
- **Desarrollo**: 1 desarrollador senior
- **Tiempo total**: ~8 horas de desarrollo efectivo
- **Herramientas**: Python, FastAPI, Streamlit, Ollama
- **Infraestructura**: Desarrollo local únicamente
