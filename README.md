# MVP Agente Conversacional de Logística - Mysavant.AI

Sistema conversacional inteligente para operaciones logísticas usando el framework WAT (Workflows, Agents, Tools) con LLM local Ollama.

## 🚀 Características

- **3 Intenciones Principales**: Consulta de estado, reprogramación de entregas, reporte de incidencias
- **LLM Local**: Integración con Ollama (completamente gratuito)
- **Configuración por Cliente**: Tono y comportamiento personalizable
- **Mock API**: Servidor FastAPI con datos reales de envíos
- **Interfaz Web**: Chat interactivo con Streamlit
- **Framework WAT**: Separación clara entre workflows, agente y herramientas

## 📋 Requisitos del Sistema

### Versiones Requeridas
- **Python**: 3.8+ (recomendado 3.11)
- **Sistema Operativo**: macOS, Linux, Windows
- **Memoria RAM**: Mínimo 8GB (recomendado 16GB para LLM)
- **Espacio en Disco**: 5GB libres (modelos LLM)
- **Ollama**: Versión 0.17.6+

### Dependencias Python (requirements.txt)
```
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
streamlit>=1.28.0
pandas>=2.1.0
requests>=2.31.0
pydantic>=2.5.0
python-dotenv>=1.0.0
```

### Instalación de Ollama
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Descargar desde https://ollama.ai
```

### Instalar Modelo LLM
```bash
ollama pull llama3.2
# o alternativamente:
ollama pull mistral
```

## ⚡ Instalación Rápida (≤ 10 minutos)

### 1. Clonar Repositorio desde GitHub
```bash
# Clonar el repositorio
git clone https://github.com/svela11/santiago-vela_my_savant_test.git

# Navegar al directorio del proyecto
cd santiago-vela_my_savant_test

# Verificar que los archivos se clonaron correctamente
ls -la
```

**Archivos esperados después del clonado:**
```
├── .gitignore
├── Listado Ordenes.json     # Datos de envíos
├── data/                    # Datos procesados
├── .env                     # Variables de entorno (si existe)
└── README.md               # Este archivo
```

### 2. Instalar Dependencias Python
```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

**Si no existe requirements.txt, instalar manualmente:**
```bash
pip install fastapi uvicorn streamlit pandas requests pydantic python-dotenv
```

### 3. Iniciar Ollama
```bash
ollama serve
```

### 4. Verificar Estructura del Proyecto
```bash
# Verificar que tienes los archivos necesarios
ls -la

# Deberías ver al menos:
# - Listado Ordenes.json (archivo de datos)
# - data/ (carpeta con datos procesados)
```

**⚠️ IMPORTANTE**: Si faltan archivos del código fuente (tools/, config/, app.py, etc.), necesitarás:
1. Recrear los archivos faltantes siguiendo la documentación
2. O contactar al desarrollador para obtener el código completo

### 5. Ejecutar el Sistema (3 Terminales)

#### Terminal 1: Iniciar Ollama
```bash
# Iniciar servidor Ollama
ollama serve

# Verificar que funciona
ollama list
```

#### Terminal 2: Iniciar Mock API (si existe)
```bash
# Navegar al directorio del proyecto
cd santiago-vela_my_savant_test

# Iniciar servidor API (si existe el archivo)
python -m uvicorn tools.mock_api_server:app --host 0.0.0.0 --port 8000

# Verificar funcionamiento
curl http://localhost:8000/health
```

#### Terminal 3: Iniciar Interfaz Web (si existe)
```bash
# Navegar al directorio del proyecto
cd santiago-vela_my_savant_test

# Iniciar interfaz web (si existe app.py)
streamlit run app.py

# La aplicación se abrirá automáticamente en el navegador
```

### 6. Acceder a la Aplicación
- **Interfaz Web**: http://localhost:8502
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🏗️ Arquitectura del Sistema

### Framework WAT
```
workflows/          # Procedimientos en Markdown
├── consulta_estado_envio.md
├── reprogramar_entrega.md
└── reporte_incidencia.md

tools/              # Scripts Python determinísticos
├── mock_api_server.py      # Servidor FastAPI
├── conversation_agent.py   # Orquestador principal
├── llm_interface.py       # Integración Ollama
└── ...

config/             # Configuraciones por cliente
├── cliente_a_config.json  # Tono formal
├── cliente_b_config.json  # Tono amigable
└── default_config.json
```

### Componentes Principales
1. **Mock API Server** - Sirve datos de envíos desde JSON
2. **Conversation Agent** - Orquesta interacciones y detecta intenciones
3. **LLM Interface** - Maneja comunicación con Ollama
4. **Streamlit App** - Interfaz web de chat
5. **Client Configs** - Personalización por cliente

## 🎯 Casos de Uso

### 1. Consulta de Estado
```
Usuario: "¿Cuál es el estado del envío 14309635?"
Sistema: Consulta API → Genera respuesta contextual
```

### 2. Reprogramación de Entrega
```
Usuario: "Necesito cambiar la entrega del 14309635 para mañana"
Sistema: Extrae datos → Valida → Actualiza → Confirma
```

### 3. Reporte de Incidencia
```
Usuario: "Mi paquete 14309635 llegó dañado"
Sistema: Crea ticket → Asigna prioridad → Programa seguimiento
```

## 🔧 Configuración por Cliente

### Cliente A (Formal)
```json
{
  "tone": "formal",
  "language": "es",
  "require_confirmation": true,
  "escalation_threshold": "high"
}
```

### Cliente B (Amigable)
```json
{
  "tone": "amigable", 
  "language": "es",
  "require_confirmation": false,
  "escalation_threshold": "medium"
}
```

## 📡 API Endpoints

### Consulta de Envíos
```bash
GET /shipments/{id}
# Ejemplo: GET /shipments/14309635
```

### Reprogramación
```bash
POST /shipments/{id}/reschedule
{
  "new_date": "2025-01-20",
  "new_time": "14:00",
  "reason": "Solicitud del cliente"
}
```

### Crear Ticket
```bash
POST /tickets
{
  "shipment_id": "14309635",
  "issue_type": "daño",
  "description": "Caja aplastada",
  "severity": "medium"
}
```

## 🧪 Cómo Probar el Sistema

### Ejemplos de Prompts y Resultados Esperados

#### 1. Consulta de Estado (Flujo Exitoso)
**Prompt**: `"¿Cuál es el estado del envío 14309635?"`

**Resultado Esperado**:
```
Estado del Envío: Entregado ✅
• Origen: CSXT - INDIANAPOLIS - AVON, IN
• Destino: BROWNSBURG DC - BROWNSBURG, IN  
• Fecha de entrega: 15 de enero de 2025
• Peso: 22,152 lbs
• Piezas: 1,319 unidades
```

#### 2. Reprogramación de Entrega
**Prompt**: `"Necesito cambiar la entrega del 14309635 para el 25/01/2025 a las 14:00"`

**Resultado Esperado**:
```
Reprogramación exitosa:
• Envío: 14309635
• Nueva fecha: 25 de enero de 2025
• Nueva hora: 14:00
• Confirmación: RPG-20260306-001
```

#### 3. Reporte de Incidencia
**Prompt**: `"Mi paquete 14309635 llegó dañado"`

**Resultado Esperado**:
```
Ticket creado: TK20260306152030
• Tipo: Daño del producto
• Severidad: Media-Alta
• Tiempo de respuesta: 24 horas
```

#### 4. Caso con Datos Faltantes
**Prompt**: `"Quiero reprogramar mi entrega"`

**Resultado Esperado**:
```
Para reprogramar necesito:
• Número de envío
• Nueva fecha
• Nueva hora
¿Podrías proporcionarme esta información?
```

#### 5. Envío No Encontrado
**Prompt**: `"Estado del envío 99999999"`

**Resultado Esperado**:
```
No encontré información para el envío 99999999.
Verifica el número e intenta nuevamente.
¿Tienes otro número de referencia?
```

### IDs de Prueba Disponibles
- `14309635` - Envío entregado (DE)
- `1395083` - Envío pickup (PU)
- `32491741` - Envío Costco
- `500795617` - Envío Miami

### Diferencias por Cliente
- **Cliente A (Formal)**: Lenguaje profesional, confirmaciones requeridas
- **Cliente B (Amigable)**: Emojis, lenguaje casual, respuestas directas

## 🛠️ Troubleshooting Rápido

### Problema: Error al Clonar Repositorio
**Síntomas**: `git clone` falla o archivos incompletos
```bash
# Verificar conexión a GitHub
ping github.com

# Clonar con HTTPS si SSH falla
git clone https://github.com/svela11/santiago-vela_my_savant_test.git

# Si el repositorio es privado, autenticarse
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"

# Descargar como ZIP si git falla
# Ir a: https://github.com/svela11/santiago-vela_my_savant_test
# Click en "Code" > "Download ZIP"
```

### Problema: Archivos Faltantes Después del Clonado
**Síntomas**: Solo aparecen README.md, .gitignore y datos
```bash
# Verificar qué archivos están en el repositorio remoto
git ls-tree -r HEAD --name-only

# Si faltan archivos de código, contactar al desarrollador
# Los archivos principales que deberían estar:
# - tools/mock_api_server.py
# - tools/conversation_agent.py  
# - tools/llm_interface.py
# - app.py
# - config/
# - requirements.txt
```

### Problema: "API: Offline" en Interfaz
**Síntomas**: Chat no funciona, error "API no disponible"
```bash
# Verificar puerto
lsof -i :8000

# Si está ocupado, matar proceso
lsof -ti:8000 | xargs kill -9

# Reiniciar API (si existe el archivo)
cd santiago-vela_my_savant_test
python -m uvicorn tools.mock_api_server:app --host 0.0.0.0 --port 8000
```

### Problema: "Ollama: Offline" en Interfaz
**Síntomas**: Respuestas genéricas, sin contexto
```bash
# Verificar estado
ollama list

# Reiniciar servicio
ollama serve

# Verificar modelo
ollama pull llama3.2
```

### Problema: Chat Se Queda Cargando
**Síntomas**: Spinner infinito, sin respuesta
```bash
# Verificar memoria disponible
vm_stat  # macOS

# Reiniciar Ollama con menos memoria
export OLLAMA_MAX_LOADED_MODELS=1
ollama serve
```

### Problema: ModuleNotFoundError
**Síntomas**: Error al importar módulos
```bash
# Verificar entorno virtual activo
which python

# Reinstalar dependencias
pip install -r requirements.txt

# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Problema: Puerto Ya En Uso
**Síntomas**: "Address already in use"
```bash
# Encontrar y matar proceso
lsof -i :8000
kill -9 <PID>

# O matar todos los procesos del puerto
lsof -ti:8000,8502,11434 | xargs kill -9
```

### Problema: Repositorio Vacío o Solo con Datos
**Síntomas**: Solo tienes README.md, .gitignore, Listado Ordenes.json
```bash
# Verificar el contenido del repositorio remoto
git ls-remote --heads origin

# Verificar si hay otras ramas
git branch -r

# Si el código está en otra rama
git checkout develop
# o
git checkout main

# Si no hay código fuente, necesitarás:
# 1. Contactar al desarrollador (Santiago Vela)
# 2. O recrear los archivos siguiendo la documentación
```

### Problema: No Tienes Git Instalado
**Síntomas**: `git: command not found`
```bash
# macOS
xcode-select --install
# o
brew install git

# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install git

# Linux (CentOS/RHEL)
sudo yum install git

# Windows: Descargar desde https://git-scm.com/
```

## 📊 Monitoreo y Logs

### Logs del Sistema
- API: Logs automáticos en consola
- Conversaciones: Guardadas en memoria del agente
- Errores: Capturados y mostrados en interfaz

### Métricas Disponibles
- Intenciones detectadas
- Tiempo de respuesta
- Éxito/fallo de operaciones
- Escalamientos activados

## 🔒 Seguridad y Políticas

### No Alucinación
- El sistema nunca inventa datos de envíos
- Respuestas explícitas "No sé" cuando no hay información
- Validación de todos los datos antes de mostrar

### Escalamiento Automático
- Errores técnicos → Soporte inmediato
- Múltiples fallos → Agente humano
- Alta severidad → Notificación prioritaria

## 🚀 Despliegue en Producción

### Consideraciones
1. **Base de Datos**: Reemplazar JSON con PostgreSQL/MySQL
2. **Autenticación**: Implementar JWT/OAuth
3. **Monitoreo**: Agregar Prometheus/Grafana
4. **Escalabilidad**: Usar Docker/Kubernetes
5. **Seguridad**: HTTPS, rate limiting, validación

### Variables de Entorno Producción
```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
LOG_LEVEL=INFO
ENVIRONMENT=production
```

## 📚 Documentación Adicional

### Workflows
- Cada workflow en `workflows/` documenta procedimientos específicos
- Incluye manejo de errores y criterios de éxito
- Ejemplos de conversaciones por cliente

### Configuración Avanzada
- Personalización de plantillas de mensajes
- Reglas de escalamiento por cliente
- Horarios de negocio y zonas horarias

## 🤝 Contribución

### Agregar Nueva Intención
1. Crear workflow en `workflows/nueva_intencion.md`
2. Actualizar `conversation_agent.py`
3. Agregar endpoint en `mock_api_server.py` si necesario
4. Probar con ambos clientes

### Nuevo Cliente
1. Crear `config/nuevo_cliente_config.json`
2. Definir tono, políticas y plantillas
3. Probar flujos principales
4. Documentar casos especiales

## 📄 Licencia

Proyecto de demostración para evaluación técnica. Uso interno únicamente.

---

**Tiempo estimado de setup**: ≤ 10 minutos  
**Herramientas**: 100% gratuitas  
**Soporte**: Documentación completa incluida
