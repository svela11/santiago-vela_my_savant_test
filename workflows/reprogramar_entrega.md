# Reprogramación de Entrega

## Objetivo
Permitir a los clientes reprogramar fechas y horarios de entrega de sus envíos de manera eficiente, validando disponibilidad y confirmando cambios.

## Entradas Requeridas
- **shipment_id**: Número de identificación del envío
- **new_date**: Nueva fecha de entrega (formato YYYY-MM-DD)
- **new_time**: Nueva hora de entrega (formato HH:MM)
- **reason**: Motivo de la reprogramación (opcional)

## Herramientas Requeridas
- `tools/conversation_agent.py`
- `tools/llm_interface.py`
- `tools/mock_api_server.py`

## Pasos del Proceso

### 1. Detección de Intención y Extracción
- Detectar intención "reprogramar_entrega"
- Extraer shipment_id, nueva fecha, nueva hora del mensaje
- Identificar motivo si se proporciona

### 2. Validación de Datos
```bash
# Validaciones automáticas:
# - shipment_id existe y es válido
# - new_date es fecha futura válida
# - new_time tiene formato correcto
# - Envío permite reprogramación (no entregado/cancelado)
```

### 3. Solicitud de Datos Faltantes
- Si faltan campos requeridos, solicitarlos específicamente
- Usar configuración del cliente para el tono del mensaje
- Mantener contexto de la conversación

### 4. Confirmación (si requerida)
```bash
# Según configuración del cliente:
# - Cliente A: Requiere confirmación explícita
# - Cliente B: Procede directamente
```

### 5. Llamada a API
```bash
POST /shipments/{shipment_id}/reschedule
{
  "new_date": "YYYY-MM-DD",
  "new_time": "HH:MM", 
  "reason": "motivo"
}
```

### 6. Procesamiento de Respuesta
- Confirmar reprogramación exitosa
- Informar nueva fecha y hora
- Proporcionar información adicional relevante

## Salidas Esperadas
- Confirmación de reprogramación exitosa
- Detalles de la nueva fecha/hora
- Número de referencia o confirmación
- Próximos pasos si aplican

## Manejo de Errores

### Datos Faltantes
- **Síntoma**: Faltan shipment_id, fecha o hora
- **Acción**: Solicitar datos específicos faltantes
- **Mensaje**: "Para reprogramar la entrega necesito: {campos_faltantes}. ¿Podría proporcionarme esta información?"

### Envío No Encontrado
- **Síntoma**: API retorna 404 para shipment_id
- **Acción**: Verificar número de envío
- **Mensaje**: "No encontré el envío {id}. ¿Podría verificar el número?"

### Fecha Inválida
- **Síntoma**: Fecha en el pasado o formato incorrecto
- **Acción**: Solicitar fecha válida futura
- **Mensaje**: "La fecha debe ser futura y en formato DD/MM/YYYY. ¿Podría proporcionar una fecha válida?"

### Envío No Reprogramable
- **Síntoma**: Envío ya entregado o cancelado
- **Acción**: Explicar estado actual
- **Mensaje**: "Este envío tiene estado '{estado}' y no puede ser reprogramado. ¿Necesita crear una incidencia?"

### Error de Sistema
- **Síntoma**: API retorna error 500
- **Acción**: Escalamiento a soporte
- **Mensaje**: "Hay un problema técnico. Su solicitud ha sido registrada y será procesada manualmente."

## Criterios de Éxito
- Todos los datos requeridos recolectados correctamente
- Validaciones de fecha/hora pasadas exitosamente
- API confirma reprogramación exitosa
- Cliente recibe confirmación clara con nuevos detalles
- Registro de cambio guardado para auditoría

## Escalamiento
- **Múltiples intentos fallidos**: Derivar a agente humano
- **Fechas no disponibles**: Ofrecer alternativas o escalamiento
- **Problemas técnicos**: Registro manual y seguimiento

## Ejemplos de Uso

### Cliente Formal (Cliente A)
```
Usuario: "Necesito reprogramar la entrega del envío 14309635 para el 20 de enero a las 2 PM"
Asistente: "Entiendo que desea reprogramar la entrega del envío 14309635 para el 20 de enero de 2025 a las 14:00 horas. 

Por favor, confirme si desea proceder con la acción solicitada. Esta confirmación es requerida por nuestras políticas de seguridad."

Usuario: "Sí, confirmo"
Asistente: "Perfecto. La reprogramación ha sido procesada exitosamente:

• Envío: 14309635
• Nueva fecha: 20 de enero de 2025
• Nueva hora: 14:00 horas
• Fecha anterior: 15 de enero de 2025

¿Requiere alguna información adicional?"
```

### Cliente Amigable (Cliente B)
```
Usuario: "oye puedo cambiar mi entrega 14309635 para mañana en la tarde?"
Asistente: "¡Claro! Te ayudo a reprogramar tu envío 14309635. 

Solo necesito que me confirmes:
📅 ¿Qué fecha específica? (formato DD/MM/YYYY)
⏰ ¿A qué hora exacta te conviene?"

Usuario: "20/01/2025 a las 3 PM"
Asistente: "¡Listo! ✅ Tu entrega ha sido reprogramada:

📦 Envío: 14309635  
📅 Nueva fecha: 20/01/2025
⏰ Nueva hora: 15:00
🔄 Cambio desde: 15/01/2025

¿Todo correcto? ¡Dale que procedemos! 👍"
```

## Notas
- Validar siempre que la nueva fecha sea futura
- Considerar horarios de negocio del cliente
- Registrar motivo de reprogramación para análisis
- Aplicar políticas de confirmación según cliente
- Mantener registro de cambios para auditoría
