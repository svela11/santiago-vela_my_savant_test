#!/usr/bin/env python3
"""
Agente conversacional principal para el sistema de logística WAT Framework.
Orquesta interacciones entre LLM, API y configuraciones de cliente.
"""

import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

try:
    from .llm_interface import OllamaInterface
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from llm_interface import OllamaInterface
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ConversationAgent:
    def __init__(self, api_base_url: str = "http://localhost:8000", client_id: str = "default"):
        self.api_base_url = api_base_url
        self.client_id = client_id
        self.llm = OllamaInterface()
        self.client_config = self.load_client_config(client_id)
        self.conversation_state = {
            "current_intent": None,
            "collected_entities": {},
            "pending_confirmation": None,
            "conversation_history": []
        }
        
    def load_client_config(self, client_id: str) -> Dict:
        """Cargar configuración específica del cliente."""
        config_file = Path(f"config/{client_id}_config.json")
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Cargar configuración por defecto
            default_config = Path("config/default_config.json")
            if default_config.exists():
                with open(default_config, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Configuración mínima por defecto
                return {
                    "client_id": client_id,
                    "tone": "formal",
                    "language": "es",
                    "policies": {
                        "no_hallucination": True,
                        "require_confirmation": True,
                        "escalation_threshold": "medium"
                    },
                    "required_fields": {
                        "consulta_estado": ["shipment_id"],
                        "reprogramar_entrega": ["shipment_id", "new_date", "new_time"],
                        "reportar_incidencia": ["shipment_id", "issue_type", "description"]
                    }
                }
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Procesar mensaje del usuario y generar respuesta."""
        try:
            # 1. Detectar intención usando reglas simples primero
            intent = self._detect_intent_simple(user_message)
            
            # 2. Extraer entidades usando reglas simples
            entities = self._extract_entities_simple(user_message, intent)
            
            # 3. Actualizar estado de conversación
            self.conversation_state["current_intent"] = intent
            self.conversation_state["collected_entities"].update(entities)
            
            # 4. Procesar según intención
            if intent == "saludo":
                response = self._handle_greeting(user_message)
                
            elif intent == "consulta_estado":
                response = self._handle_status_query(user_message, entities)
                
            elif intent == "reprogramar_entrega":
                response = self._handle_reschedule_request(user_message, entities)
                
            elif intent == "reportar_incidencia":
                response = self._handle_incident_report(user_message, entities)
                
            else:
                response = self._handle_other(user_message)
            
            # 5. Agregar a historial
            self.conversation_state["conversation_history"].append({
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "intent": intent,
                "entities": entities,
                "response": response["message"]
            })
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "message": self._get_error_message(),
                "intent": "error",
                "error": str(e)
            }
    
    def _detect_intent_simple(self, user_message: str) -> str:
        """Detectar intención usando reglas simples con prioridades."""
        message_lower = user_message.lower().strip()
        
        # Normalizar errores ortográficos comunes
        message_lower = self._normalize_spelling(message_lower)
        
        # PRIORIDAD 0: Detectar reprogramación PRIMERO (tiene máxima precedencia)
        import re
        reprog_words = [
            "reprogramar", "repgrogramar", "cambiar", "mover", "nueva fecha", "reschedule",
            "se puede reprogramar", "puedo cambiar", "modificar entrega", "quiero mover",
            "reagenda", "reagendar", "para mañana", "para el viernes", "para el lunes",
            "para el sábado", "para el jueves", "en la tarde", "por la mañana", "en la noche",
            "kiero mover", "quiero que llegue"
        ]
        if any(word in message_lower for word in reprog_words):
            return "reprogramar_entrega"
        
        # PRIORIDAD 0.5: Detectar incidencias ANTES que consultas (crítico)
        incident_words = [
            "dañado", "problema", "incidencia", "perdido", "retraso", "ticket", "abierto", "roto",
            "mal estado", "defectuoso", "averiado", "llegó mal", "llegó abierto", "llegó dañado",
            "no llegó", "tardó", "demora", "llegó tarde", "llegó incompleto", "nunca llegó",
            "se perdió", "llegó mal", "retrasado", "debía llegar", "debería haber llegado",
            "sigue en tránsito", "dice entregado pero no lo recibí", "no lo recibí", "no llego"
        ]
        if any(word in message_lower for word in incident_words):
            return "reportar_incidencia"
        
        # PRIORIDAD 0.7: Detectar intenciones no soportadas ANTES que consultas
        unsupported_words = [
            "cancelar", "cancela", "devolver", "devolución", "dirección", "direccion", 
            "costo", "costó", "precio", "repartidor", "conductor", "eliminar"
        ]
        if any(word in message_lower for word in unsupported_words):
            return "no_soportado"
        
        # PRIORIDAD 1: Si contiene ID de envío + palabras de consulta = consulta_estado
        has_shipment_id = re.search(r'\b\d{4,8}\b', user_message)  # Ampliado para IDs de 4-8 dígitos
        has_query_words = any(word in message_lower for word in [
            "estado", "status", "cuál es", "como va", "información", "consultar", "necesito",
            "donde esta", "dónde está", "ahora mismo", "ya salió", "cuándo llegará", "cuando llegara",
            "ya fue entregado", "está en tránsito", "esta en transito", "plis", "please"
        ])
        
        if has_shipment_id and has_query_words:
            return "consulta_estado"
        
        # PRIORIDAD 2: Solo ID de envío (mensaje que es principalmente números) = consulta_estado
        if has_shipment_id:
            # Si el mensaje es principalmente el ID (con pocas palabras adicionales)
            words = message_lower.split()
            if len(words) <= 3 or any(re.match(r'\d{4,8}', word) for word in words):
                return "consulta_estado"
        
        # PRIORIDAD 3: Si la conversación anterior pidió un ID y ahora hay un ID = consulta_estado
        if has_shipment_id and self.conversation_state.get("current_intent") == "consulta_estado":
            return "consulta_estado"
        
        # (Incidencias ya detectadas en PRIORIDAD 0.5)
        
        # PRIORIDAD 6: Palabras de consulta sin ID = pedir ID
        query_words = [
            "estado", "status", "cuál es", "como va", "información", "consultar",
            "donde esta", "dónde está", "mi envío", "mi paquete", "pakete"
        ]
        if any(word in message_lower for word in query_words):
            return "consulta_estado"
        
        # PRIORIDAD 7: Solo saludos sin otra intención
        greeting_words = ["hola", "buenos días", "buenas tardes", "hi", "hello", "necesito ayuda", "tengo un problema"]
        if any(word in message_lower for word in greeting_words) and not has_query_words:
            return "saludo"
        
        return "otro"
    
    def _normalize_spelling(self, text: str) -> str:
        """Normalizar errores ortográficos comunes."""
        corrections = {
            "pakete": "paquete",
            "kiero": "quiero",
            "plis": "por favor",
            "donde": "dónde",
            "esta": "está",
            "llego": "llegó",
            "entrego": "entregó"
        }
        
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        
        return text
    
    def _extract_entities_simple(self, user_message: str, intent: str) -> Dict[str, Any]:
        """Extraer entidades usando reglas simples."""
        import re
        entities = {}
        
        # Buscar ID de envío (4-8 dígitos, pero validar formato)
        shipment_match = re.search(r'\b(\d{4,8})\b', user_message)
        if shipment_match:
            shipment_id = shipment_match.group(1)
            # Validar que no sea un ID obviamente inválido
            if self._is_valid_shipment_id(shipment_id):
                entities["shipment_id"] = shipment_id
                entities["extracted_value"] = shipment_id
            else:
                entities["shipment_id"] = "INVALID_FORMAT"
                entities["extracted_value"] = "INVALID_FORMAT"
        
        # Para reprogramación, buscar fechas
        if intent == "reprogramar_entrega":
            # Buscar fechas en formato DD/MM/YYYY o similar
            date_match = re.search(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b', user_message)
            if date_match:
                entities["new_date"] = date_match.group(1)
            
            # Buscar horas
            time_match = re.search(r'\b(\d{1,2}:\d{2})\b', user_message)
            if time_match:
                entities["new_time"] = time_match.group(1)
            
            # Detectar fechas relativas SOLO si no hay fecha absoluta
            message_lower = user_message.lower()
            if "new_date" not in entities:  # Solo si no se detectó fecha absoluta
                if "mañana" in message_lower:
                    entities["new_date"] = "mañana"
                elif "viernes" in message_lower:
                    entities["new_date"] = "viernes"
                elif "lunes" in message_lower:
                    entities["new_date"] = "lunes"
                elif "sábado" in message_lower or "sabado" in message_lower:
                    entities["new_date"] = "sábado"
                elif "jueves" in message_lower:
                    entities["new_date"] = "jueves"
                elif "ayer" in message_lower:
                    entities["new_date"] = "ayer"  # Fecha inválida - será manejada en validación
            
            # Detectar horarios relativos
            if "en la tarde" in message_lower or "tarde" in message_lower:
                entities["new_time"] = "tarde"
            elif "por la mañana" in message_lower or "mañana" in message_lower:
                entities["new_time"] = "mañana"
            elif "en la noche" in message_lower or "noche" in message_lower:
                entities["new_time"] = "noche"
            elif "3pm" in message_lower or "15:00" in message_lower:
                entities["new_time"] = "15:00"
        
        # Para incidencias, detectar tipo de problema
        if intent == "reportar_incidencia":
            message_lower = user_message.lower()
            if any(word in message_lower for word in ["dañado", "roto", "abierto", "mal estado", "defectuoso", "averiado", "llegó mal", "llegó abierto", "llegó dañado"]):
                entities["issue_type"] = "daño"
            elif any(word in message_lower for word in ["perdido", "no llegó", "no recibí", "extraviado"]):
                entities["issue_type"] = "pérdida"
            elif any(word in message_lower for word in ["retraso", "tarde", "tardó", "demora", "no ha llegado"]):
                entities["issue_type"] = "retraso"
            else:
                entities["issue_type"] = "otro"
            
            entities["description"] = user_message
        
        return entities
    
    def _convert_date_format(self, date_str: str) -> str:
        """Convertir fecha de DD/MM/YYYY a YYYY-MM-DD para la API."""
        import re
        from datetime import datetime
        
        # Si es una fecha relativa, devolverla tal como está
        if date_str in ["mañana", "viernes", "lunes", "sábado", "jueves", "ayer"]:
            return date_str
        
        # Intentar convertir DD/MM/YYYY a YYYY-MM-DD
        try:
            # Detectar formato DD/MM/YYYY o DD-MM-YYYY
            if re.match(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', date_str):
                # Separar por / o -
                parts = re.split(r'[/-]', date_str)
                if len(parts) == 3:
                    day, month, year = parts
                    # Validar que sea una fecha válida
                    datetime.strptime(f"{year}-{month.zfill(2)}-{day.zfill(2)}", '%Y-%m-%d')
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # Si ya está en formato YYYY-MM-DD, devolverla tal como está
            if re.match(r'\d{4}-\d{1,2}-\d{1,2}', date_str):
                return date_str
                
        except ValueError:
            pass
        
        # Si no se puede convertir, devolver la fecha original
        return date_str
    
    def _is_valid_shipment_id(self, shipment_id: str) -> bool:
        """Validar si un ID de envío tiene formato válido."""
        # Rechazar IDs obviamente inválidos
        if shipment_id in ["12345", "98765", "54321", "11111", "22222", "33333", "44444", "77777", "88888", "99999", "99999999"]:
            return False
        
        # Rechazar IDs que son solo repetición de un dígito
        if len(set(shipment_id)) == 1:
            return False
        
        # Rechazar IDs alfanuméricos como ABCD123
        if not shipment_id.isdigit():
            return False
        
        # Aceptar IDs de 6-8 dígitos que parecen reales
        if len(shipment_id) >= 6:
            return True
        
        # IDs de 4-5 dígitos solo si no son secuenciales obvios
        if shipment_id in ["1234", "2345", "3456", "4567", "5678", "6789", "7890"]:
            return False
        
        return True
    
    def _handle_greeting(self, user_message: str) -> Dict[str, Any]:
        """Manejar saludos y mensajes de bienvenida."""
        greeting_template = self.client_config.get("message_templates", {}).get("greeting")
        
        if greeting_template:
            message = greeting_template
        else:
            if self.client_config.get("tone") == "amigable":
                message = "¡Hola! 😊 Soy tu asistente de logística. ¿En qué puedo ayudarte hoy? Puedo ayudarte con:\n\n• Consultar el estado de tus envíos\n• Reprogramar entregas\n• Reportar incidencias\n\n¿Qué necesitas?"
            else:
                message = "Buenos días. Soy el asistente de logística. Estoy aquí para ayudarle con:\n\n• Consultas de estado de envíos\n• Reprogramación de entregas\n• Reporte de incidencias\n\n¿En qué puedo asistirle?"
        
        return {
            "success": True,
            "message": message,
            "intent": "saludo",
            "next_actions": ["consulta_estado", "reprogramar_entrega", "reportar_incidencia"]
        }
    
    def _handle_status_query(self, user_message: str, entities: Dict) -> Dict[str, Any]:
        """Manejar consultas de estado de envío."""
        shipment_id = entities.get("extracted_value") or entities.get("shipment_id")
        
        # Si no hay ID en el mensaje actual, verificar si hay uno en el contexto previo
        if not shipment_id or shipment_id == "NO_ENCONTRADO":
            # Buscar en mensajes previos de la conversación
            for prev_msg in reversed(self.conversation_state.get("conversation_history", [])):
                if prev_msg.get("entities", {}).get("shipment_id"):
                    shipment_id = prev_msg["entities"]["shipment_id"]
                    break
        
        if not shipment_id or shipment_id == "NO_ENCONTRADO":
            return {
                "success": False,
                "message": "Para consultar el estado de su envío, necesito el número de envío. ¿Podría proporcionármelo?",
                "intent": "consulta_estado",
                "missing_fields": ["shipment_id"]
            }
        
        # Manejar IDs con formato inválido
        if shipment_id == "INVALID_FORMAT":
            if self.client_config.get("tone") == "amigable":
                message = "¡Ups! 😅 Parece que el número de envío que me diste no tiene el formato correcto. Los números de envío suelen tener entre 6 y 8 dígitos.\n\n¿Podrías verificar el número e intentar de nuevo? 📦"
            else:
                message = "El número de envío proporcionado no tiene un formato válido. Los números de envío deben tener entre 6 y 8 dígitos.\n\nPor favor, verifique el número e intente nuevamente."
            
            return {
                "success": False,
                "message": message,
                "intent": "consulta_estado",
                "error": "invalid_format"
            }
        
        # Consultar API
        api_response = self._call_api("GET", f"/shipments/{shipment_id}")
        
        if api_response["success"] and api_response.get("data"):
            # Validar que los datos sean del ID correcto
            returned_id = api_response["data"].get("shipment_id", "")
            if returned_id != shipment_id:
                error_msg = f"No pude encontrar información para el envío {shipment_id}. Verifique el número e intente nuevamente."
                return {
                    "success": False,
                    "message": error_msg,
                    "intent": "consulta_estado",
                    "error": "ID mismatch"
                }
            
            # Generar respuesta contextual solo con datos validados
            response_message = self.llm.generate_contextual_response(
                user_message, "consulta_estado", entities, 
                api_response["data"], self.client_config
            )
            
            return {
                "success": True,
                "message": response_message,
                "intent": "consulta_estado",
                "shipment_data": api_response["data"]
            }
        else:
            error_msg = f"No pude encontrar información para el envío {shipment_id}. Verifique el número e intente nuevamente."
            return {
                "success": False,
                "message": error_msg,
                "intent": "consulta_estado",
                "error": api_response.get("error", "Envío no encontrado")
            }
    
    def _handle_reschedule_request(self, user_message: str, entities: Dict) -> Dict[str, Any]:
        """Manejar solicitudes de reprogramación."""
        # Si es una pregunta sobre si se puede reprogramar
        if any(phrase in user_message.lower() for phrase in ["se puede", "puedo", "es posible", "ya no se puede"]):
            return self._handle_reschedule_inquiry(user_message, entities)
        
        required_fields = self.client_config["required_fields"]["reprogramar_entrega"]
        missing_fields = []
        
        # Verificar campos requeridos
        shipment_id = entities.get("shipment_id")
        new_date = entities.get("new_date")
        new_time = entities.get("new_time")
        reason = entities.get("reason", "Solicitud del cliente")
        
        if not shipment_id or shipment_id == "NO_ENCONTRADO":
            missing_fields.append("shipment_id")
        if not new_date or new_date == "NO_ENCONTRADO" or new_date == "":
            missing_fields.append("new_date")
        if not new_time or new_time == "NO_ENCONTRADO" or new_time == "":
            missing_fields.append("new_time")
        
        # Validar fecha pasada antes de procesar
        if new_date == "ayer":
            if self.client_config.get("tone") == "amigable":
                message = "¡Ups! 😅 No puedo reprogramar una entrega para ayer porque ya pasó. ¿Te gustaría cambiarla para una fecha futura? Por ejemplo, mañana, el viernes, etc. 📅"
            else:
                message = "No es posible reprogramar una entrega para una fecha pasada. Por favor, proporcione una fecha futura para la reprogramación."
            
            return {
                "success": False,
                "message": message,
                "intent": "reprogramar_entrega",
                "error": "invalid_past_date"
            }
        
        if missing_fields:
            missing_text = ", ".join(missing_fields)
            return {
                "success": False,
                "message": f"Para reprogramar la entrega necesito: {missing_text}. ¿Podría proporcionarme esta información?",
                "intent": "reprogramar_entrega",
                "missing_fields": missing_fields
            }
        
        # Convertir fecha DD/MM/YYYY a YYYY-MM-DD para la API
        converted_date = self._convert_date_format(new_date)
        
        # Llamar API para reprogramar
        reschedule_data = {
            "new_date": converted_date,
            "new_time": new_time,
            "reason": reason
        }
        
        api_response = self._call_api("POST", f"/shipments/{shipment_id}/reschedule", reschedule_data)
        
        # Generar respuesta contextual
        response_message = self.llm.generate_contextual_response(
            user_message, "reprogramar_entrega", entities,
            api_response.get("data", api_response), self.client_config
        )
        
        return {
            "success": api_response["success"],
            "message": response_message,
            "intent": "reprogramar_entrega",
            "api_response": api_response
        }
    
    def _handle_reschedule_inquiry(self, user_message: str, entities: Dict) -> Dict[str, Any]:
        """Manejar preguntas sobre si se puede reprogramar un envío."""
        # Buscar ID de envío en el contexto de la conversación
        shipment_id = entities.get("shipment_id")
        if not shipment_id:
            # Buscar en mensajes previos
            for prev_msg in reversed(self.conversation_state.get("conversation_history", [])):
                if prev_msg.get("entities", {}).get("shipment_id"):
                    shipment_id = prev_msg["entities"]["shipment_id"]
                    break
        
        if shipment_id:
            # Consultar estado actual del envío
            api_response = self._call_api("GET", f"/shipments/{shipment_id}")
            
            if api_response["success"] and api_response.get("data"):
                shipment_data = api_response["data"]
                status = shipment_data.get("status", "").lower()
                
                # Determinar si se puede reprogramar según el estado
                if status == "entregado":
                    if self.client_config.get("tone") == "amigable":
                        message = f"Lo siento, pero el envío {shipment_id} ya fue entregado el {shipment_data.get('delivery_date', 'fecha no disponible')} 📦✅\n\nUna vez entregado, no es posible reprogramarlo. ¿Necesitas ayuda con algo más? 😊"
                    else:
                        message = f"El envío {shipment_id} tiene estado 'entregado' con fecha {shipment_data.get('delivery_date', 'no disponible')}. Los envíos entregados no pueden ser reprogramados.\n\n¿Requiere asistencia con algún otro asunto?"
                    
                    return {
                        "success": False,
                        "message": message,
                        "intent": "reprogramar_entrega",
                        "reason": "already_delivered"
                    }
                
                elif status in ["en_transito", "pendiente", "programado"]:
                    if self.client_config.get("tone") == "amigable":
                        message = f"¡Sí! Tu envío {shipment_id} está {status} y sí se puede reprogramar 📅✨\n\n¿Para qué fecha y hora te gustaría cambiarlo? Solo necesito:\n📅 Nueva fecha (DD/MM/YYYY)\n⏰ Nueva hora (HH:MM)"
                    else:
                        message = f"Sí, el envío {shipment_id} con estado '{status}' puede ser reprogramado.\n\nPara proceder necesito:\n• Nueva fecha de entrega (formato DD/MM/YYYY)\n• Nueva hora de entrega (formato HH:MM)\n\n¿Podría proporcionarme esta información?"
                    
                    return {
                        "success": True,
                        "message": message,
                        "intent": "reprogramar_entrega",
                        "can_reschedule": True,
                        "current_status": status
                    }
                
                else:
                    message = f"El envío {shipment_id} tiene estado '{status}'. Para determinar si se puede reprogramar, le recomiendo contactar a nuestro equipo de soporte especializado."
                    return {
                        "success": False,
                        "message": message,
                        "intent": "reprogramar_entrega",
                        "reason": "status_unclear"
                    }
            else:
                message = f"No pude verificar el estado del envío {shipment_id}. Para consultas sobre reprogramación, por favor contacte a nuestro equipo de soporte."
                return {
                    "success": False,
                    "message": message,
                    "intent": "reprogramar_entrega",
                    "error": "shipment_not_found"
                }
        else:
            # No hay ID de envío en contexto
            if self.client_config.get("tone") == "amigable":
                message = "Para saber si puedes reprogramar tu entrega, necesito el número de envío 📦\n\n¿Me puedes decir cuál es el ID de tu envío?"
            else:
                message = "Para verificar si su envío puede ser reprogramado, necesito el número de envío. ¿Podría proporcionármelo?"
            
            return {
                "success": False,
                "message": message,
                "intent": "reprogramar_entrega",
                "missing_fields": ["shipment_id"]
            }
    
    def _handle_incident_report(self, user_message: str, entities: Dict) -> Dict[str, Any]:
        """Manejar reportes de incidencias."""
        required_fields = self.client_config["required_fields"]["reportar_incidencia"]
        missing_fields = []
        
        # Verificar campos requeridos
        shipment_id = entities.get("shipment_id")
        issue_type = entities.get("issue_type")
        description = entities.get("description")
        
        # Si no hay ID en el mensaje actual, buscar en el contexto de la conversación
        if not shipment_id or shipment_id == "NO_ENCONTRADO":
            # Buscar en mensajes previos de la conversación
            for prev_msg in reversed(self.conversation_state.get("conversation_history", [])):
                if prev_msg.get("entities", {}).get("shipment_id"):
                    shipment_id = prev_msg["entities"]["shipment_id"]
                    entities["shipment_id"] = shipment_id  # Actualizar entidades
                    break
        
        if not shipment_id or shipment_id == "NO_ENCONTRADO":
            missing_fields.append("shipment_id")
        if not issue_type or issue_type == "NO_ENCONTRADO":
            missing_fields.append("issue_type")
        if not description or description == "NO_ENCONTRADO":
            missing_fields.append("description")
        
        if missing_fields:
            missing_text = ", ".join(missing_fields)
            return {
                "success": False,
                "message": f"Para crear el reporte de incidencia necesito: {missing_text}. ¿Podría proporcionarme esta información?",
                "intent": "reportar_incidencia",
                "missing_fields": missing_fields
            }
        
        # Crear ticket
        ticket_data = {
            "shipment_id": shipment_id,
            "issue_type": issue_type,
            "description": description,
            "severity": "medium",
            "contact_info": "Por definir"
        }
        
        api_response = self._call_api("POST", "/tickets", ticket_data)
        
        # Generar respuesta contextual
        response_message = self.llm.generate_contextual_response(
            user_message, "reportar_incidencia", entities,
            api_response.get("data", api_response), self.client_config
        )
        
        return {
            "success": api_response["success"],
            "message": response_message,
            "intent": "reportar_incidencia",
            "api_response": api_response
        }
    
    def _handle_other(self, user_message: str) -> Dict[str, Any]:
        """Manejar otros tipos de mensajes."""
        message_lower = user_message.lower()
        
        # Detectar intenciones no soportadas pero relacionadas con logística
        if any(word in message_lower for word in ["cancelar", "cancela", "devolver", "devolución", "dirección", "direccion", "costo", "costó", "precio", "repartidor", "conductor"]):
            if self.client_config.get("tone") == "amigable":
                message = "¡Hola! 😊 Entiendo que necesitas ayuda con eso, pero por ahora solo puedo ayudarte con:\n\n📦 **Consultar estado** de envíos\n📅 **Reprogramar entregas**\n🎫 **Reportar incidencias**\n\nPara otros temas como cancelaciones, devoluciones o cambios de dirección, te recomiendo contactar a nuestro equipo de soporte especializado. ¿Hay algo de lo que sí puedo ayudarte? 😄"
            else:
                message = "Comprendo su consulta, sin embargo, mi capacidad se limita a:\n\n• Consultas de estado de envíos\n• Reprogramación de entregas\n• Reporte de incidencias\n\nPara asuntos como cancelaciones, devoluciones, cambios de dirección o información de costos, le recomiendo contactar directamente a nuestro equipo de soporte especializado.\n\n¿Puedo asistirle con alguna de las funciones disponibles?"
            
            return {
                "success": False,
                "message": message,
                "intent": "no_soportado",
                "available_actions": ["consulta_estado", "reprogramar_entrega", "reportar_incidencia"]
            }
        
        # Generar respuesta usando LLM con políticas de no alucinación
        system_prompt = """Eres un asistente de logística. Si no sabes algo o no tienes información específica, 
        di claramente que no lo sabes y sugiere contactar a soporte. No inventes información.
        
        Puedes ayudar con:
        - Consultas de estado de envíos
        - Reprogramación de entregas  
        - Reporte de incidencias
        
        Para cualquier otra cosa, deriva a soporte humano."""
        
        response = self.llm.generate_response(user_message, system_prompt, {"client_config": self.client_config})
        
        if response["success"]:
            message = response["response"]
        else:
            message = "Lo siento, no puedo procesar su solicitud en este momento. Por favor, contacte a nuestro equipo de soporte."
        
        return {
            "success": True,
            "message": message,
            "intent": "otro",
            "escalation_suggested": True
        }
    
    def _call_api(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Realizar llamada a la API."""
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                return {"success": False, "error": f"Método {method} no soportado"}
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {"detail": response.text}
                return {"success": False, "error": f"API Error {response.status_code}", "data": error_data}
                
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Timeout de API"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "No se pudo conectar a la API"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_error_message(self) -> str:
        """Obtener mensaje de error según configuración del cliente."""
        error_template = self.client_config.get("message_templates", {}).get("error_message")
        
        if error_template:
            return error_template
        else:
            if self.client_config.get("tone") == "amigable":
                return "¡Ups! Algo salió mal. Por favor, intenta nuevamente o contacta a nuestro equipo de soporte. 😅"
            else:
                return "Se ha producido un error. Por favor, intente nuevamente o contacte al servicio de soporte técnico."
    
    def get_conversation_summary(self) -> str:
        """Obtener resumen de la conversación actual."""
        history = self.conversation_state["conversation_history"]
        if not history:
            return "No hay conversación previa."
        
        summary = f"Cliente: {self.client_id}\n"
        summary += f"Intención actual: {self.conversation_state['current_intent']}\n"
        summary += f"Entidades recolectadas: {self.conversation_state['collected_entities']}\n"
        summary += f"Mensajes intercambiados: {len(history)}\n"
        
        return summary
    
    def reset_conversation(self):
        """Reiniciar estado de conversación."""
        self.conversation_state = {
            "current_intent": None,
            "collected_entities": {},
            "pending_confirmation": None,
            "conversation_history": []
        }
        self.llm.clear_history()

def main():
    """Función de prueba."""
    agent = ConversationAgent(client_id="cliente_a")
    
    print("🤖 Agente conversacional iniciado")
    print("💬 Escriba 'salir' para terminar")
    
    while True:
        user_input = input("\nUsuario: ")
        if user_input.lower() in ['salir', 'exit', 'quit']:
            break
        
        response = agent.process_message(user_input)
        print(f"Asistente: {response['message']}")
        
        if response.get("intent"):
            print(f"[Intención detectada: {response['intent']}]")

if __name__ == "__main__":
    main()
