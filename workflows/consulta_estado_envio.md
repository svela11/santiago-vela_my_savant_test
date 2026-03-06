# Consulta de Estado de Envío

## Objetivo
Proporcionar información actualizada y precisa sobre el estado de envíos a los clientes de manera eficiente y clara.

## Entradas Requeridas
- **shipment_id**: Número de identificación del envío
- **client_config**: Configuración específica del cliente (tono, idioma, políticas)

## Herramientas Requeridas
- `tools/conversation_agent.py`
- `tools/llm_interface.py`
- `tools/mock_api_server.py`

## Pasos del Proceso

### 1. Detección de Intención
- El agente conversacional detecta la intención "consulta_estado"
- Extrae el ID del envío del mensaje del usuario
- Valida que el ID esté presente y sea válido

### 2. Validación de Entrada
```bash
# El agente verifica automáticamente:
# - Presencia del shipment_id
# - Formato válido del ID
# - Configuración del cliente cargada
```

### 3. Consulta a la API
```bash
# Llamada automática del agente:
GET /shipments/{shipment_id}
```

### 4. Procesamiento de Respuesta
- Si el envío existe: generar respuesta informativa
- Si no existe: mensaje de error claro
- Aplicar configuración de tono según cliente

### 5. Generación de Respuesta
- Usar plantillas del cliente específico
- Incluir información relevante: origen, destino, ETA, estado
- Mantener tono consistente (formal/amigable)

## Salidas Esperadas
- Información completa del estado del envío
- Mensaje formateado según configuración del cliente
- Datos estructurados para seguimiento

## Manejo de Errores

### ID de Envío Faltante
- **Síntoma**: Usuario no proporciona número de envío
- **Acción**: Solicitar el ID de manera clara y específica
- **Mensaje**: "Para consultar el estado de su envío, necesito el número de envío. ¿Podría proporcionármelo?"

### Envío No Encontrado
- **Síntoma**: API retorna 404 para el shipment_id
- **Acción**: Verificar número y sugerir alternativas
- **Mensaje**: "No pude encontrar información para el envío {id}. Verifique el número e intente nuevamente."

### Error de API
- **Síntoma**: API no responde o retorna error 500
- **Acción**: Mensaje de error técnico y escalamiento
- **Mensaje**: "Hay un problema técnico temporal. Por favor, intente en unos minutos o contacte a soporte."

### Formato de ID Inválido
- **Síntoma**: ID no tiene formato esperado
- **Acción**: Solicitar formato correcto
- **Mensaje**: "El número de envío debe tener entre 6-8 dígitos. ¿Podría verificar el número?"

## Criterios de Éxito
- ID de envío extraído correctamente del mensaje
- Información recuperada de la API exitosamente
- Respuesta generada según configuración del cliente
- Tono y formato apropiados aplicados
- Información completa y útil proporcionada

## Escalamiento
- **Múltiples intentos fallidos**: Derivar a soporte humano
- **Problemas técnicos persistentes**: Escalamiento automático
- **Cliente insatisfecho**: Según configuración del cliente

## Ejemplos de Uso

### Cliente Formal (Cliente A)
```
Usuario: "¿Cuál es el estado del envío 14309635?"
Asistente: "Estimado cliente, el estado actual de su envío 14309635 es: en_transito.

Detalles:
• Origen: CSXT - INDIANAPOLIS - AVON, IN
• Destino: BROWNSBURG DC - BROWNSBURG, IN  
• Fecha estimada de entrega: 2025-01-15
• Peso: 22152
• Piezas: 1319

¿Requiere información adicional?"
```

### Cliente Amigable (Cliente B)
```
Usuario: "hola, como va mi envío 14309635?"
Asistente: "¡Perfecto! Aquí tienes la info de tu envío 14309635:

📦 Estado: en_transito
📍 Desde: CSXT - INDIANAPOLIS - AVON, IN
🎯 Hacia: BROWNSBURG DC - BROWNSBURG, IN
⏰ Llegada estimada: 2025-01-15

¿Todo bien o necesitas algo más?"
```

## Notas
- Siempre usar datos reales de la API, nunca inventar información
- Mantener consistencia en el tono según configuración del cliente
- Registrar todas las consultas para análisis posterior
- Aplicar políticas de escalamiento según configuración
