# Reporte de Incidencia

## Objetivo
Facilitar a los clientes el reporte de problemas, daños o incidencias relacionadas con sus envíos, creando tickets de seguimiento y asegurando resolución oportuna.

## Entradas Requeridas
- **shipment_id**: Número de identificación del envío afectado
- **issue_type**: Tipo de incidencia (daño, retraso, pérdida, otro)
- **description**: Descripción detallada del problema
- **severity**: Nivel de severidad (low, medium, high)
- **contact_info**: Información de contacto del cliente

## Herramientas Requeridas
- `tools/conversation_agent.py`
- `tools/llm_interface.py`
- `tools/mock_api_server.py`

## Pasos del Proceso

### 1. Detección de Intención y Extracción
- Detectar intención "reportar_incidencia"
- Extraer shipment_id y tipo de problema del mensaje
- Identificar descripción del problema
- Determinar severidad basada en el tipo de incidencia

### 2. Clasificación de Incidencia
```bash
# Tipos de incidencia soportados:
# - daño: Productos dañados o en mal estado
# - retraso: Entregas fuera de tiempo
# - pérdida: Envíos perdidos o no localizados
# - otro: Cualquier otro problema
```

### 3. Recolección de Información
- Solicitar datos faltantes de manera estructurada
- Adaptar preguntas según tipo de incidencia
- Mantener tono empático y profesional

### 4. Validación de Datos
```bash
# Validaciones automáticas:
# - shipment_id existe en el sistema
# - issue_type es válido
# - description tiene contenido suficiente
# - Información de contacto disponible
```

### 5. Creación de Ticket
```bash
POST /tickets
{
  "shipment_id": "string",
  "issue_type": "string",
  "description": "string", 
  "severity": "string",
  "contact_info": "string"
}
```

### 6. Confirmación y Seguimiento
- Proporcionar número de ticket generado
- Explicar próximos pasos y tiempos de respuesta
- Ofrecer información de contacto para seguimiento

## Salidas Esperadas
- Ticket de incidencia creado exitosamente
- Número de referencia del ticket
- Tiempo estimado de respuesta
- Instrucciones para seguimiento

## Manejo de Errores

### Información Incompleta
- **Síntoma**: Faltan datos requeridos (ID, tipo, descripción)
- **Acción**: Solicitar información específica faltante
- **Mensaje**: "Para crear el reporte necesito: {campos_faltantes}. ¿Podría proporcionarme esta información?"

### Envío No Encontrado
- **Síntoma**: shipment_id no existe en sistema
- **Acción**: Verificar número y ofrecer alternativas
- **Mensaje**: "No encontré el envío {id}. ¿Podría verificar el número o tiene otro número de referencia?"

### Tipo de Incidencia No Claro
- **Síntoma**: Problema no se clasifica claramente
- **Acción**: Ofrecer opciones específicas
- **Mensaje**: "¿Su problema se relaciona con: 1) Daño del producto, 2) Retraso en entrega, 3) Pérdida del envío, 4) Otro?"

### Error de Sistema
- **Síntoma**: No se puede crear ticket por error técnico
- **Acción**: Registro manual y escalamiento inmediato
- **Mensaje**: "Registraré su incidencia manualmente. Un especialista se contactará en las próximas 2 horas."

## Criterios de Éxito
- Información completa de incidencia recolectada
- Ticket creado exitosamente en el sistema
- Número de referencia proporcionado al cliente
- Expectativas de tiempo de respuesta comunicadas
- Escalamiento automático según severidad

## Escalamiento Automático

### Alta Severidad
- **Pérdida de envío**: Escalamiento inmediato
- **Daño significativo**: Notificación a supervisor
- **Múltiples incidencias del mismo cliente**: Revisión especial

### Escalamiento por Cliente
- **Cliente A**: Escalamiento conservador, proceso formal
- **Cliente B**: Escalamiento ágil, comunicación directa

## Ejemplos de Uso

### Cliente Formal (Cliente A)
```
Usuario: "Tengo un problema con el envío 14309635, llegó con la caja dañada"
Asistente: "Lamento mucho escuchar sobre el daño en su envío 14309635. Para procesar su reporte de incidencia de manera efectiva, necesito algunos detalles adicionales:

1. ¿Podría describir específicamente el tipo de daño observado?
2. ¿El contenido del envío también resultó afectado?
3. ¿Tiene fotografías del daño que pueda compartir?

Esta información nos permitirá procesar su caso de manera prioritaria."

Usuario: "La caja estaba aplastada y el contenido se dañó parcialmente"
Asistente: "Gracias por la información. He creado el ticket de incidencia TK20250304152030 para su envío 14309635.

Detalles del reporte:
• Tipo: Daño del producto
• Severidad: Media-Alta
• Tiempo estimado de respuesta: 24 horas

Un representante especializado se comunicará con usted dentro de las próximas 24 horas para coordinar la resolución. ¿Requiere alguna información adicional?"
```

### Cliente Amigable (Cliente B)
```
Usuario: "oye mi paquete 14309635 llegó todo aplastado 😞"
Asistente: "¡Oh no! 😔 Qué mal que tu paquete llegó dañado. Te voy a ayudar a resolver esto súper rápido.

¿Me puedes contar un poquito más?
📦 ¿Qué tan dañada está la caja?
📱 ¿El contenido también se dañó?

Con esa info creo tu reporte y lo ponemos en prioridad."

Usuario: "sí, la caja aplastada y lo de adentro también se dañó"
Asistente: "¡Listo! ✅ Ya creé tu ticket TK20250304152030 para el envío 14309635.

📋 Tipo: Daño del producto  
⚡ Prioridad: Alta
⏰ Te contactamos en: máximo 24 horas

¡Te van a resolver todo súper rápido! 🚀 ¿Necesitas algo más mientras tanto?"
```

## Notas
- Mantener tono empático, especialmente para incidencias de daño/pérdida
- Documentar todos los detalles para facilitar resolución
- Aplicar escalamiento según políticas del cliente
- Seguir up automático si no hay respuesta en tiempo esperado
- Registrar patrones de incidencias para mejora de procesos
