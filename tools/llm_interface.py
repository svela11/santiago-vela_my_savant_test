#!/usr/bin/env python3
"""
Interfaz LLM para integración con Ollama en el framework WAT.
Maneja comunicación con modelos locales y procesamiento de respuestas.
"""

import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class OllamaInterface:
    def __init__(self, model_name: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.session = requests.Session()
        self.conversation_history = []
        
    def check_ollama_status(self) -> bool:
        """Verificar si Ollama está ejecutándose."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_available_models(self) -> List[str]:
        """Listar modelos disponibles en Ollama."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except:
            return []
    
    def generate_response(self, prompt: str, system_prompt: str = None, context: Dict = None) -> Dict[str, Any]:
        """Generar respuesta usando Ollama."""
        if not self.check_ollama_status():
            return {
                "success": False,
                "error": "Ollama no está disponible. Asegúrese de que esté ejecutándose.",
                "fallback_message": "Lo siento, el sistema de IA no está disponible en este momento. Por favor, contacte a soporte."
            }
        
        # Construir prompt completo
        full_prompt = self._build_prompt(prompt, system_prompt, context)
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Respuestas más consistentes
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '').strip()
                
                # Agregar a historial
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "prompt": prompt,
                    "response": generated_text,
                    "model": self.model_name
                })
                
                return {
                    "success": True,
                    "response": generated_text,
                    "model_used": self.model_name,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Error del modelo: {response.status_code}",
                    "fallback_message": "Hubo un problema procesando su solicitud. Por favor, intente nuevamente."
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Timeout del modelo",
                "fallback_message": "La respuesta está tomando más tiempo del esperado. Por favor, intente nuevamente."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_message": "Ocurrió un error inesperado. Por favor, contacte a soporte."
            }
    
    def _build_prompt(self, user_prompt: str, system_prompt: str = None, context: Dict = None) -> str:
        """Construir prompt completo con contexto."""
        parts = []
        
        # Sistema
        if system_prompt:
            parts.append(f"SISTEMA: {system_prompt}")
        
        # Contexto adicional
        if context:
            if context.get('client_config'):
                config = context['client_config']
                parts.append(f"CONFIGURACIÓN CLIENTE: Tono={config.get('tone', 'formal')}, Idioma={config.get('language', 'es')}")
            
            if context.get('shipment_data'):
                parts.append(f"DATOS ENVÍO: {json.dumps(context['shipment_data'], ensure_ascii=False)}")
            
            if context.get('conversation_context'):
                parts.append(f"CONTEXTO: {context['conversation_context']}")
        
        # Prompt del usuario
        parts.append(f"USUARIO: {user_prompt}")
        parts.append("ASISTENTE:")
        
        return "\n\n".join(parts)
    
    def detect_intent(self, user_message: str, client_config: Dict = None) -> Dict[str, Any]:
        """Detectar intención del usuario."""
        system_prompt = """Eres un clasificador de intenciones para un sistema de logística. 
        Clasifica el mensaje del usuario en una de estas categorías:
        1. consulta_estado - Preguntas sobre el estado de un envío
        2. reprogramar_entrega - Solicitudes para cambiar fecha/hora de entrega  
        3. reportar_incidencia - Reportes de problemas (daño, retraso, pérdida)
        4. saludo - Saludos o inicio de conversación
        5. otro - Cualquier otra cosa
        
        Responde SOLO con el nombre de la categoría, nada más."""
        
        context = {"client_config": client_config} if client_config else None
        
        result = self.generate_response(user_message, system_prompt, context)
        
        if result["success"]:
            intent = result["response"].lower().strip()
            # Validar que sea una intención válida
            valid_intents = ["consulta_estado", "reprogramar_entrega", "reportar_incidencia", "saludo", "otro"]
            if intent in valid_intents:
                return {"intent": intent, "confidence": 0.8}
            else:
                return {"intent": "otro", "confidence": 0.5}
        else:
            return {"intent": "otro", "confidence": 0.0, "error": result.get("error")}
    
    def extract_entities(self, user_message: str, intent: str) -> Dict[str, Any]:
        """Extraer entidades del mensaje del usuario."""
        if intent == "consulta_estado":
            system_prompt = """Extrae el ID de envío del mensaje. 
            Busca números que podrían ser IDs de envío (típicamente 6-8 dígitos).
            Responde SOLO con el ID encontrado, o 'NO_ENCONTRADO' si no hay ninguno."""
            
        elif intent == "reprogramar_entrega":
            system_prompt = """Extrae información de reprogramación del mensaje.
            Busca: ID de envío, nueva fecha, nueva hora, motivo.
            Responde en formato JSON: {"shipment_id": "...", "new_date": "...", "new_time": "...", "reason": "..."}
            Usa 'NO_ENCONTRADO' para campos no encontrados."""
            
        elif intent == "reportar_incidencia":
            system_prompt = """Extrae información de incidencia del mensaje.
            Busca: ID de envío, tipo de problema, descripción.
            Responde en formato JSON: {"shipment_id": "...", "issue_type": "...", "description": "..."}
            Usa 'NO_ENCONTRADO' para campos no encontrados."""
            
        else:
            return {}
        
        result = self.generate_response(user_message, system_prompt)
        
        if result["success"]:
            try:
                # Intentar parsear como JSON si es necesario
                response_text = result["response"].strip()
                if response_text.startswith("{"):
                    return json.loads(response_text)
                else:
                    return {"extracted_value": response_text}
            except:
                return {"extracted_value": result["response"]}
        else:
            return {}
    
    def generate_contextual_response(self, user_message: str, intent: str, 
                                   entities: Dict, api_data: Dict = None, 
                                   client_config: Dict = None) -> str:
        """Generar respuesta contextual basada en intención y datos."""
        
        # Construir prompt base según configuración del cliente
        tone = client_config.get('tone', 'formal') if client_config else 'formal'
        language = client_config.get('language', 'es') if client_config else 'es'
        
        if tone == 'formal':
            base_prompt = "Responde de manera profesional y formal."
        else:
            base_prompt = "Responde de manera amigable y cercana."
        
        if language == 'en':
            base_prompt += " Respond in English."
        else:
            base_prompt += " Responde en español."
        
        # Agregar contexto específico por intención
        if intent == "consulta_estado" and api_data:
            context_prompt = f"""
            {base_prompt}
            
            REGLAS ESTRICTAS ANTI-ALUCINACIÓN:
            1. SOLO usa los datos proporcionados a continuación
            2. NO inventes, asumas o agregues información
            3. Si un dato no está disponible, NO lo menciones
            4. NUNCA uses información de otros envíos
            
            El usuario pregunta sobre el estado del envío. Información VERIFICADA:
            {json.dumps(api_data, ensure_ascii=False, indent=2)}
            
            Responde ÚNICAMENTE con estos datos exactos. NO agregues información adicional.
            """
            
        elif intent == "reprogramar_entrega" and api_data:
            if api_data.get("success"):
                context_prompt = f"""
                {base_prompt}
                
                La reprogramación fue exitosa. Confirma los detalles:
                {json.dumps(api_data, ensure_ascii=False, indent=2)}
                
                Confirma la nueva fecha y hora, y proporciona cualquier información adicional relevante.
                """
            else:
                context_prompt = f"""
                {base_prompt}
                
                Hubo un problema con la reprogramación:
                {api_data.get('detail', 'Error desconocido')}
                
                Explica el problema y sugiere alternativas o próximos pasos.
                """
                
        elif intent == "reportar_incidencia" and api_data:
            if api_data.get("success"):
                context_prompt = f"""
                {base_prompt}
                
                El ticket de incidencia fue creado exitosamente:
                {json.dumps(api_data, ensure_ascii=False, indent=2)}
                
                Confirma la creación del ticket y explica los próximos pasos.
                """
            else:
                context_prompt = f"""
                {base_prompt}
                
                Hubo un problema creando el ticket:
                {api_data.get('detail', 'Error desconocido')}
                
                Explica el problema y sugiere alternativas.
                """
        else:
            context_prompt = f"""
            {base_prompt}
            
            Responde al mensaje del usuario de manera útil. Si no tienes información 
            suficiente, pide los datos necesarios de manera clara.
            """
        
        context = {
            "client_config": client_config,
            "conversation_context": f"Intención: {intent}, Entidades: {entities}"
        }
        
        result = self.generate_response(user_message, context_prompt, context)
        
        if result["success"]:
            return result["response"]
        else:
            return result.get("fallback_message", "Lo siento, no puedo procesar su solicitud en este momento.")
    
    def clear_history(self):
        """Limpiar historial de conversación."""
        self.conversation_history = []
    
    def get_conversation_summary(self) -> str:
        """Obtener resumen de la conversación."""
        if not self.conversation_history:
            return "No hay conversación previa."
        
        last_interactions = self.conversation_history[-3:]  # Últimas 3 interacciones
        summary_parts = []
        
        for interaction in last_interactions:
            summary_parts.append(f"Usuario: {interaction['prompt'][:100]}...")
            summary_parts.append(f"Asistente: {interaction['response'][:100]}...")
        
        return "\n".join(summary_parts)

def main():
    """Función de prueba."""
    llm = OllamaInterface()
    
    print("🤖 Probando interfaz Ollama...")
    
    # Verificar estado
    if llm.check_ollama_status():
        print("✅ Ollama está ejecutándose")
        
        # Listar modelos
        models = llm.list_available_models()
        print(f"📋 Modelos disponibles: {models}")
        
        # Prueba básica
        result = llm.generate_response("Hola, ¿cómo estás?")
        print(f"🗣️ Respuesta de prueba: {result}")
        
    else:
        print("❌ Ollama no está disponible")
        print("💡 Ejecute: ollama serve")

if __name__ == "__main__":
    main()
