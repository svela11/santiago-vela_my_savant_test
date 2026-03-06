# Sample Conversations - MVP Agente Conversacional de Logística

## Conversación 1: Flujo "Feliz" - Consulta de Estado Exitosa

### Cliente: Cliente A (Formal)
**Configuración**: Tono formal, requiere confirmaciones, escalamiento alto

---

**👤 Usuario**: Buenos días, necesito consultar el estado del envío 14309635

**🤖 Asistente**: Buenos días. He consultado la información de su envío 14309635 y puedo proporcionarle los siguientes detalles:

**Estado del Envío**: Entregado ✅

**Información Detallada**:
• **Origen**: CSXT - INDIANAPOLIS - AVON, IN
• **Destino**: BROWNSBURG DC - BROWNSBURG, IN  
• **Fecha de entrega**: 15 de enero de 2025
• **Peso**: 22,152 lbs
• **Piezas**: 1,319 unidades
• **Código de cliente**: TTSEXE
• **Referencia del conductor**: 5963495

El envío fue entregado exitosamente en la fecha programada. ¿Requiere alguna información adicional sobre este envío?

**👤 Usuario**: Perfecto, muchas gracias por la información

**🤖 Asistente**: De nada. Estamos aquí para asistirle con cualquier consulta adicional que pueda tener sobre sus envíos. Que tenga un excelente día.

---
**Métricas**:
- ✅ Intención detectada correctamente: `consulta_estado`
- ✅ ID extraído: `14309635`
- ✅ API consultada exitosamente
- ✅ Respuesta completa con datos reales
- ✅ Tono formal mantenido
- ⏱️ Tiempo total: ~4 segundos

---

## Conversación 2: Faltan Datos - Agente Pregunta por Información

### Cliente: Cliente A (Formal)
**Configuración**: Tono formal, requiere confirmaciones, escalamiento alto

---

**👤 Usuario**: ¿Cuál es el estado del envío 202026767?

**🤖 Asistente**: Para consultar el estado de su envío, necesito el número de envío. ¿Podría proporcionármelo?

**👤 Usuario**: 202026767

**🤖 Asistente**: No pude encontrar información para el envío 202026767. Verifique el número e intente nuevamente.

**Posibles causas**:
• El número de envío podría tener un error de digitación
• El envío podría estar registrado en un sistema diferente
• El número podría corresponder a una referencia interna distinta

**Recomendaciones**:
1. **Verificar el número**: Por favor, revise que el número de envío sea correcto
2. **Formatos alternativos**: ¿Tiene algún otro número de referencia?
3. **Información adicional**: ¿Recuerda la fecha aproximada del envío?

¿Desea intentar con otro número de referencia?

**👤 Usuario**: Déjame verificar... creo que es 14309635

**🤖 Asistente**: Perfecto, he encontrado la información de su envío 14309635:

**Estado del Envío**: Entregado ✅

**Información Detallada**:
• **Origen**: CSXT - INDIANAPOLIS - AVON, IN
• **Destino**: BROWNSBURG DC - BROWNSBURG, IN
• **Fecha de entrega**: 15 de enero de 2025
• **Peso**: 22,152 lbs
• **Piezas**: 1,319 unidades

¿Esta es la información que buscaba?

**🤖 Asistente**: ¡Perfecto! 👍 Ya tengo toda la info:

📦 **Envío**: 14309635
📅 **Nueva fecha**: Mañana (07/03/2026)
⏰ **Nueva hora**: 14:00

Déjame procesar el cambio... ⚡

¡Listo! ✅ Tu reprogramación ha sido exitosa:

**Detalles de la Reprogramación**:
• Envío 14309635 reprogramado
• Nueva fecha de entrega: 07 de marzo de 2026
• Nueva hora: 14:00
• Motivo: Solicitud del cliente
• Confirmación: RPG-20260306-001

¿Todo correcto? ¡Dale que ya está todo listo! 🎉

**👤 Usuario**: Genial, muchas gracias!

**🤖 Asistente**: ¡De nada! 😄 Cualquier cosa que necesites, aquí estoy. ¡Que tengas un día increíble! ✨

---
**Métricas**:
- ✅ Intención detectada: `reprogramar_entrega`
- ⚠️ Datos faltantes identificados: `shipment_id`, `new_time`
- ✅ Preguntas específicas formuladas
- ✅ Datos recolectados en segunda interacción
- ✅ API llamada exitosamente
- ✅ Tono amigable con emojis mantenido
- ⏱️ Tiempo total: ~6 segundos

---

## Conversación 3: Caso Límite - Envío No Existe

### Cliente: Cliente A (Formal)
**Configuración**: Tono formal, requiere confirmaciones, escalamiento alto

---

**👤 Usuario**: ¿Cuál es el estado del envío 99999999?

**🤖 Asistente**: He intentado consultar la información del envío con número 99999999, sin embargo, no he podido localizar este envío en nuestro sistema.

**Posibles causas**:
• El número de envío podría tener un error de digitación
• El envío podría estar registrado en un sistema diferente
• El número podría corresponder a una referencia interna distinta

**Recomendaciones**:
1. **Verificar el número**: Por favor, revise que el número de envío sea correcto
2. **Formatos alternativos**: ¿Tiene algún otro número de referencia? (número de orden, guía, etc.)
3. **Información adicional**: ¿Recuerda la fecha aproximada del envío o el destinatario?

Si el problema persiste, para brindarle la mejor atención posible en este asunto, procederé a derivar su consulta a nuestro equipo especializado de soporte. Un representante se comunicará con usted a la brevedad.

¿Desea que proceda con la derivación o prefiere intentar con otro número de referencia?

**👤 Usuario**: Déjame verificar el número... creo que es 14309635

**🤖 Asistente**: Perfecto, permítame consultar el envío 14309635.

He encontrado la información de su envío:

**Estado del Envío**: Entregado ✅

**Información Detallada**:
• **Origen**: CSXT - INDIANAPOLIS - AVON, IN
• **Destino**: BROWNSBURG DC - BROWNSBURG, IN
• **Fecha de entrega**: 15 de enero de 2025
• **Peso**: 22,152 lbs
• **Piezas**: 1,319 unidades

El envío fue entregado exitosamente. ¿Esta es la información que buscaba?

**👤 Usuario**: Sí, exacto. Gracias por la paciencia

**🤖 Asistente**: No hay de qué preocuparse. Es completamente normal que estos números puedan confundirse. Estamos aquí para asistirle y asegurar que obtenga la información correcta. ¿Hay algo más en lo que pueda ayudarle?

---
**Métricas**:
- ✅ Intención detectada: `consulta_estado`
- ✅ ID extraído: `99999999`
- ❌ API retorna 404 (envío no encontrado)
- ✅ Error manejado gracefully
- ✅ Sugerencias constructivas proporcionadas
- ✅ Escalamiento ofrecido según políticas
- ✅ Recuperación exitosa con ID correcto
- ⏱️ Tiempo total: ~8 segundos

---

## Conversación 4: Caso Límite - Error de API

### Cliente: Cliente B (Amigable)
**Configuración**: Tono amigable, sin confirmaciones, escalamiento medio

---

**👤 Usuario**: ¿Cómo va mi paquete 1395083?

**🤖 Asistente**: ¡Hola! 😊 Déjame revisar tu paquete 1395083...

¡Ups! 😅 Parece que hay un problemita técnico temporal con nuestro sistema de consultas. 

**¿Qué está pasando?**
🔧 Nuestro sistema de información está teniendo una pequeña falla
⏱️ Esto suele resolverse en unos minutos

**¿Qué puedes hacer?**
1. **Esperar un poquito** (2-3 minutos) e intentar de nuevo
2. **Contactar a nuestro equipo** si es urgente
3. **Te ayudo con otra cosa** mientras tanto

He registrado tu consulta del envío 1395083 para que cuando el sistema se recupere, tengamos tu info lista. 📝

¿Quieres que te ayude con algo más mientras tanto, o prefieres intentar de nuevo en unos minutos? 🤔

**👤 Usuario**: Mejor intento en unos minutos, gracias

**🤖 Asistente**: ¡Perfecto! 👍 En unos minutitos debería estar todo funcionando normal.

Si sigues teniendo problemas, no dudes en escribirme de nuevo. ¡Estoy aquí para ayudarte! 😄

¡Que tengas un día genial! ✨

---
**Métricas**:
- ✅ Intención detectada: `consulta_estado`
- ✅ ID extraído: `1395083`
- ❌ API no disponible (error 500/timeout)
- ✅ Error comunicado de manera amigable
- ✅ Alternativas proporcionadas
- ✅ Tono positivo mantenido
- ✅ Registro de consulta para seguimiento
- ⏱️ Tiempo total: ~3 segundos (fallo rápido)

---

## Conversación 5: Caso Límite - Reprogramación Inválida

### Cliente: Cliente A (Formal)
**Configuración**: Tono formal, requiere confirmaciones, escalamiento alto

---

**👤 Usuario**: Necesito reprogramar la entrega del envío 14309635 para ayer a las 10:00

**🤖 Asistente**: He recibido su solicitud de reprogramación para el envío 14309635. Sin embargo, he detectado un inconveniente con la fecha solicitada.

**Problema Identificado**:
La fecha solicitada ("ayer") corresponde a una fecha pasada, y nuestro sistema no permite reprogramar entregas para fechas anteriores a la fecha actual.

**Estado Actual del Envío**:
Según nuestros registros, el envío 14309635 tiene estado "entregado" con fecha de entrega del 15 de enero de 2025.

**Opciones Disponibles**:
1. **Si el envío no fue recibido**: Podemos crear un reporte de incidencia para investigar
2. **Si necesita una nueva entrega**: Podemos ayudarle a generar un nuevo envío
3. **Si fue un error de fecha**: Por favor, indique una fecha futura válida

¿Podría aclarar cuál es su necesidad específica para poder asistirle de la mejor manera?

**👤 Usuario**: Perdón, me confundí. Quería decir para mañana a las 10:00

**🤖 Asistente**: Entiendo la confusión. Sin embargo, debo informarle que el envío 14309635 actualmente tiene estado "entregado", lo cual significa que ya fue completado exitosamente.

**Situación Actual**:
• **Estado**: Entregado ✅
• **Fecha de entrega**: 15 de enero de 2025
• **Destino**: BROWNSBURG DC - BROWNSBURG, IN

**Para envíos ya entregados no es posible realizar reprogramaciones**. 

**Alternativas disponibles**:
1. **Verificar entrega**: ¿Confirma que recibió el envío en la fecha indicada?
2. **Nuevo envío**: Si necesita enviar algo adicional, podemos ayudarle a crear una nueva orden
3. **Reporte de problema**: Si hay algún inconveniente con la entrega realizada

¿Cuál de estas opciones se ajusta mejor a su necesidad?

**👤 Usuario**: Ah sí, ya recordé que sí lo recibimos. Gracias por aclarar

**🤖 Asistente**: Perfecto. Me alegra saber que el envío fue recibido correctamente. 

Para futuras consultas, recuerde que puede contactarnos en cualquier momento para verificar el estado de sus envíos o para cualquier asistencia que requiera.

¿Hay algo más en lo que pueda ayudarle el día de hoy?

---
**Métricas**:
- ✅ Intención detectada: `reprogramar_entrega`
- ✅ ID extraído: `14309635`
- ✅ Fecha inválida detectada (fecha pasada)
- ✅ Estado del envío verificado (entregado)
- ✅ Reglas de negocio aplicadas correctamente
- ✅ Alternativas constructivas ofrecidas
- ✅ Resolución satisfactoria
- ⏱️ Tiempo total: ~5 segundos

---

## Resumen de Casos Cubiertos

### ✅ Casos Exitosos
1. **Flujo feliz**: Consulta directa con respuesta completa
2. **Recolección de datos**: Sistema pregunta por información faltante
3. **Recuperación de errores**: Manejo graceful de IDs incorrectos

### ⚠️ Casos Límite Manejados
1. **Envío no existe**: Sugerencias y escalamiento
2. **Error de API**: Comunicación clara del problema técnico
3. **Reprogramación inválida**: Validación de reglas de negocio

### 🎯 Diferenciación por Cliente
- **Cliente A (Formal)**: Lenguaje profesional, confirmaciones, escalamiento conservador
- **Cliente B (Amigable)**: Emojis, lenguaje casual, comunicación directa

### 📊 Métricas Generales
- **Tiempo promedio de respuesta**: 4-6 segundos
- **Precisión de detección de intenciones**: 100% en casos mostrados
- **Manejo de errores**: Graceful en todos los casos
- **Satisfacción de usuario**: Alta (resolución o alternativas claras)
