# RUNBOOK - MVP Agente Conversacional de Logística

## Operación del Sistema

### Arquitectura de Servicios

El sistema consta de 3 servicios principales que deben ejecutarse simultáneamente:

1. **Ollama Server** (Puerto 11434) - Servidor LLM local
2. **Mock API Server** (Puerto 8000) - API de datos de envíos
3. **Streamlit App** (Puerto 8502) - Interfaz web de chat

## Inicio del Sistema

### Secuencia de Arranque Recomendada

#### 1. Iniciar Ollama
```bash
# Terminal 1
ollama serve
```
**Verificación**: `curl -s http://localhost:11434/api/tags`

#### 2. Iniciar Mock API
```bash
# Terminal 2
cd /path/to/santiago_vela_new_test
python -m uvicorn tools.mock_api_server:app --host 0.0.0.0 --port 8000
```
**Verificación**: `curl -s http://localhost:8000/health`

#### 3. Iniciar Interfaz Web
```bash
# Terminal 3
cd /path/to/santiago_vela_new_test
streamlit run app.py
```
**Verificación**: Abrir http://localhost:8502

### Script de Inicio Automático
```bash
#!/bin/bash
# start_system.sh

echo "🚀 Iniciando sistema completo..."

# Verificar que Ollama esté instalado
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama no está instalado. Ejecute: brew install ollama"
    exit 1
fi

# Iniciar Ollama en background
echo "📡 Iniciando Ollama..."
ollama serve &
OLLAMA_PID=$!

# Esperar a que Ollama esté listo
sleep 5

# Verificar modelo
if ! ollama list | grep -q "llama3.2"; then
    echo "📥 Descargando modelo llama3.2..."
    ollama pull llama3.2
fi

# Iniciar API
echo "🔧 Iniciando Mock API..."
python -m uvicorn tools.mock_api_server:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Esperar a que API esté lista
sleep 3

# Iniciar Streamlit
echo "🌐 Iniciando interfaz web..."
streamlit run app.py &
STREAMLIT_PID=$!

echo "✅ Sistema iniciado correctamente"
echo "🌐 Interfaz: http://localhost:8502"
echo "📋 API Docs: http://localhost:8000/docs"

# Guardar PIDs para poder detener después
echo $OLLAMA_PID > .ollama.pid
echo $API_PID > .api.pid
echo $STREAMLIT_PID > .streamlit.pid
```

## Detener el Sistema

### Detener Servicios Individualmente
```bash
# Detener Streamlit
pkill -f "streamlit run"

# Detener API
pkill -f "uvicorn tools.mock_api_server"

# Detener Ollama
pkill -f "ollama serve"
```

### Script de Detención
```bash
#!/bin/bash
# stop_system.sh

echo " Deteniendo sistema..."

if [ -f .streamlit.pid ]; then
    kill $(cat .streamlit.pid) 2>/dev/null
    rm .streamlit.pid
fi

if [ -f .api.pid ]; then
    kill $(cat .api.pid) 2>/dev/null
    rm .api.pid
fi

if [ -f .ollama.pid ]; then
    kill $(cat .ollama.pid) 2>/dev/null
    rm .ollama.pid
fi

echo "✅ Sistema detenido"
```

## Reinicio del Sistema

### Reinicio Completo
```bash
# Detener todo
./stop_system.sh

# Limpiar puertos si están ocupados
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8502 | xargs kill -9 2>/dev/null
lsof -ti:11434 | xargs kill -9 2>/dev/null

# Esperar un momento
sleep 2

# Iniciar todo
./start_system.sh
```

### Reinicio Individual de Servicios

#### Reiniciar Solo API
```bash
pkill -f "uvicorn tools.mock_api_server"
python -m uvicorn tools.mock_api_server:app --host 0.0.0.0 --port 8000 &
```

#### Reiniciar Solo Streamlit
```bash
pkill -f "streamlit run"
streamlit run app.py &
```

#### Reiniciar Solo Ollama
```bash
pkill -f "ollama serve"
ollama serve &
```

## Logs y Monitoreo

### Ubicación de Logs

#### Logs de Aplicación
- **Streamlit**: Salida estándar del terminal
- **Mock API**: Salida estándar del terminal con uvicorn
- **Ollama**: `~/.ollama/logs/server.log`

#### Logs del Sistema
```bash
# Ver logs en tiempo real
tail -f ~/.ollama/logs/server.log

# Logs de sistema macOS
log show --predicate 'process == "ollama"' --last 1h
```

### Comandos de Monitoreo

#### Estado de Servicios
```bash
# Verificar puertos activos
lsof -i :8000,8502,11434

# Estado de procesos
ps aux | grep -E "(ollama|uvicorn|streamlit)"

# Verificar conectividad
curl -s http://localhost:8000/health
curl -s http://localhost:11434/api/tags
curl -s http://localhost:8502/healthz
```

#### Métricas de Sistema
```bash
# Uso de memoria
ps -o pid,ppid,%mem,%cpu,comm -p $(pgrep -f "ollama|uvicorn|streamlit")

# Uso de disco
du -sh ~/.ollama/models/

# Conexiones de red
netstat -an | grep -E ":8000|:8502|:11434"
```

## Errores Comunes y Soluciones

### 1. "API: Offline" en Interfaz

**Síntomas**: 
- Interfaz muestra "API: Offline"
- Chat no funciona

**Diagnóstico**:
```bash
curl -s http://localhost:8000/health
lsof -i :8000
```

**Solución**:
```bash
# Si puerto ocupado
lsof -ti:8000 | xargs kill -9

# Reiniciar API
python -m uvicorn tools.mock_api_server:app --host 0.0.0.0 --port 8000
```

### 2. "Ollama: Offline" en Interfaz

**Síntomas**:
- Interfaz muestra "Ollama: Offline"
- Respuestas genéricas sin contexto

**Diagnóstico**:
```bash
curl -s http://localhost:11434/api/tags
ollama list
```

**Solución**:
```bash
# Reiniciar Ollama
pkill -f "ollama serve"
ollama serve

# Verificar modelo
ollama pull llama3.2
```

### 3. Chat Se Queda "Cargando"

**Síntomas**:
- Mensaje enviado pero sin respuesta
- Spinner infinito

**Diagnóstico**:
```bash
# Verificar logs de Ollama
tail -f ~/.ollama/logs/server.log

# Verificar memoria disponible
free -h  # Linux
vm_stat  # macOS
```

**Solución**:
```bash
# Reiniciar Ollama con más memoria
export OLLAMA_MAX_LOADED_MODELS=1
ollama serve

# O usar modelo más pequeño
ollama pull llama3.2:1b
```

### 4. Error "ModuleNotFoundError"

**Síntomas**:
- Error al iniciar cualquier componente
- Imports fallan

**Solución**:
```bash
# Verificar entorno virtual
which python
pip list

# Reinstalar dependencias
pip install -r requirements.txt

# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 5. Puerto Ya En Uso

**Síntomas**:
- "Address already in use"
- Servicios no inician

**Solución**:
```bash
# Encontrar proceso usando puerto
lsof -i :8000

# Matar proceso específico
kill -9 <PID>

# O matar todos los procesos del puerto
lsof -ti:8000 | xargs kill -9
```

### 6. Modelo LLM No Responde

**Síntomas**:
- Ollama online pero respuestas vacías
- Timeouts en requests

**Diagnóstico**:
```bash
# Probar modelo directamente
ollama run llama3.2 "Hola, ¿cómo estás?"

# Verificar recursos
top -p $(pgrep ollama)
```

**Solución**:
```bash
# Reiniciar modelo
ollama stop llama3.2
ollama run llama3.2

# O cambiar modelo
ollama pull mistral:7b
# Actualizar config en tools/llm_interface.py
```

## Mantenimiento

### Limpieza Periódica

#### Limpiar Logs
```bash
# Rotar logs de Ollama
mv ~/.ollama/logs/server.log ~/.ollama/logs/server.log.old
touch ~/.ollama/logs/server.log
```

#### Limpiar Modelos No Usados
```bash
# Ver modelos instalados
ollama list

# Eliminar modelos no necesarios
ollama rm <model_name>
```

### Actualizaciones

#### Actualizar Ollama
```bash
brew upgrade ollama
```

#### Actualizar Dependencias Python
```bash
pip install -r requirements.txt --upgrade
```

#### Actualizar Modelos LLM
```bash
ollama pull llama3.2  # Descarga versión más reciente
```

### Backup y Restauración

#### Backup de Configuraciones
```bash
# Crear backup
tar -czf backup_$(date +%Y%m%d).tar.gz config/ data/ workflows/

# Restaurar
tar -xzf backup_YYYYMMDD.tar.gz
```

#### Backup de Modelos
```bash
# Los modelos están en ~/.ollama/models/
cp -r ~/.ollama/models/ ./backup_models/
```

## Contacto y Escalamiento

### Información de Soporte
- **Desarrollador**: Santiago Vela
- **Repositorio**: GitHub (URL del repositorio)
- **Documentación**: README.md y carpeta docs/

### Escalamiento de Problemas
1. **Nivel 1**: Consultar este RUNBOOK
2. **Nivel 2**: Revisar logs y aplicar soluciones comunes
3. **Nivel 3**: Contactar desarrollador con logs específicos
4. **Nivel 4**: Crear issue en repositorio GitHub

### Información para Reportes
Al reportar problemas, incluir:
- Versión del sistema operativo
- Salida de `ollama --version`
- Logs relevantes (últimas 50 líneas)
- Pasos para reproducir el problema
- Configuración de cliente utilizada
/Users/santiago/Desktop/santiago_vela_new_test/docs/RUNBOOK.md
/Users/santiago/Desktop/santiago_vela_new_test/santiago-vela_my_savant_test