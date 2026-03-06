#!/usr/bin/env python3
"""
Interfaz web Streamlit para el agente conversacional de logística WAT Framework.
Proporciona chat interactivo con selección de cliente y configuración.
"""

import streamlit as st
import sys
import os
from pathlib import Path
import json
import requests
import subprocess
import time

# Agregar directorio tools al path
sys.path.append(str(Path(__file__).parent / "tools"))

from conversation_agent import ConversationAgent

# Configuración de página
st.set_page_config(
    page_title="Asistente de Logística",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1f4e79, #2e86ab);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f1f8e9;
        border-left: 4px solid #4caf50;
    }
    .error-message {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-online { background-color: #4caf50; }
    .status-offline { background-color: #f44336; }
</style>
""", unsafe_allow_html=True)

def check_api_status():
    """Verificar estado de la API."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_ollama_status():
    """Verificar estado de Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_api_server():
    """Iniciar servidor API en background."""
    try:
        # Verificar si ya está ejecutándose
        if check_api_status():
            return True
        
        # Iniciar servidor
        subprocess.Popen([
            sys.executable, "tools/mock_api_server.py"
        ], cwd=Path(__file__).parent)
        
        # Esperar a que inicie
        for _ in range(10):
            time.sleep(1)
            if check_api_status():
                return True
        
        return False
    except:
        return False

def load_client_configs():
    """Cargar configuraciones de cliente disponibles."""
    config_dir = Path("config")
    configs = {}
    
    for config_file in config_dir.glob("*_config.json"):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                client_id = config.get('client_id', config_file.stem.replace('_config', ''))
                configs[client_id] = config
        except:
            continue
    
    return configs

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🚚 Asistente de Logística Mysavant.AI</h1>
        <p>Sistema conversacional inteligente para consultas de envíos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Estado de servicios
        st.subheader("Estado de Servicios")
        
        api_status = check_api_status()
        ollama_status = check_ollama_status()
        
        col1, col2 = st.columns(2)
        with col1:
            status_class = "status-online" if api_status else "status-offline"
            status_text = "Online" if api_status else "Offline"
            st.markdown(f'<span class="status-indicator {status_class}"></span>API: {status_text}', 
                       unsafe_allow_html=True)
        
        with col2:
            status_class = "status-online" if ollama_status else "status-offline"
            status_text = "Online" if ollama_status else "Offline"
            st.markdown(f'<span class="status-indicator {status_class}"></span>Ollama: {status_text}', 
                       unsafe_allow_html=True)
        
        # Botón para iniciar API si no está disponible
        if not api_status:
            if st.button("🚀 Iniciar API Server"):
                with st.spinner("Iniciando servidor API..."):
                    if start_api_server():
                        st.success("✅ API iniciada correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error iniciando API")
        
        # Instrucciones para Ollama
        if not ollama_status:
            st.warning("⚠️ Ollama no está disponible")
            st.markdown("""
            **Para iniciar Ollama:**
            ```bash
            ollama serve
            ```
            
            **Para instalar un modelo:**
            ```bash
            ollama pull llama3.2
            ```
            """)
        
        st.divider()
        
        # Selección de cliente
        st.subheader("👤 Configuración de Cliente")
        
        client_configs = load_client_configs()
        client_options = list(client_configs.keys())
        
        if client_options:
            selected_client = st.selectbox(
                "Seleccionar Cliente:",
                client_options,
                index=0
            )
            
            # Mostrar configuración del cliente
            if selected_client in client_configs:
                config = client_configs[selected_client]
                st.write(f"**Tono:** {config.get('tone', 'N/A')}")
                st.write(f"**Idioma:** {config.get('language', 'N/A')}")
                
                # Mostrar políticas
                policies = config.get('policies', {})
                st.write("**Políticas:**")
                for policy, value in policies.items():
                    st.write(f"- {policy}: {'✅' if value else '❌'}")
        else:
            selected_client = "default"
            st.warning("No se encontraron configuraciones de cliente")
        
        st.divider()
        
        # Información del sistema
        st.subheader("ℹ️ Información")
        st.markdown("""
        **Intenciones soportadas:**
        - 🔍 Consulta de estado de envíos
        - 📅 Reprogramación de entregas
        - ⚠️ Reporte de incidencias
        - 👋 Saludos y conversación general
        """)
    
    # Área principal de chat
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("💬 Chat")
        
        # Verificar que los servicios estén disponibles
        if not api_status:
            st.error("❌ API no disponible. Inicie el servidor API desde la barra lateral.")
            return
        
        if not ollama_status:
            st.warning("⚠️ Ollama no disponible. El sistema funcionará con respuestas limitadas.")
        
        # Inicializar agente si no existe
        if 'agent' not in st.session_state or st.session_state.get('current_client') != selected_client:
            st.session_state.agent = ConversationAgent(client_id=selected_client)
            st.session_state.current_client = selected_client
            st.session_state.messages = []
        
        # Mostrar historial de mensajes
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 Usuario:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                message_class = "error-message" if message.get("error") else "assistant-message"
                st.markdown(f"""
                <div class="chat-message {message_class}">
                    <strong>🤖 Asistente:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        # Input para nuevo mensaje
        user_input = st.chat_input("Escriba su mensaje aquí...")
        
        if user_input:
            # Agregar mensaje del usuario
            st.session_state.messages.append({
                "role": "user", 
                "content": user_input
            })
            
            # Procesar mensaje con el agente
            with st.spinner("Procesando..."):
                try:
                    response = st.session_state.agent.process_message(user_input)
                    
                    # Agregar respuesta del asistente
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["message"],
                        "intent": response.get("intent"),
                        "success": response.get("success", True),
                        "error": not response.get("success", True)
                    })
                    
                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error procesando mensaje: {str(e)}",
                        "error": True
                    })
            
            st.rerun()
    
    with col2:
        st.header("📊 Estado")
        
        if 'agent' in st.session_state:
            # Mostrar estado de conversación
            conversation_state = st.session_state.agent.conversation_state
            
            st.subheader("🎯 Intención Actual")
            current_intent = conversation_state.get("current_intent", "Ninguna")
            st.write(current_intent)
            
            st.subheader("📝 Entidades Recolectadas")
            entities = conversation_state.get("collected_entities", {})
            if entities:
                for key, value in entities.items():
                    st.write(f"**{key}:** {value}")
            else:
                st.write("Ninguna")
            
            st.subheader("💬 Mensajes")
            message_count = len(st.session_state.messages)
            st.write(f"Total: {message_count}")
            
            # Botón para limpiar conversación
            if st.button("🗑️ Limpiar Chat"):
                st.session_state.messages = []
                st.session_state.agent.reset_conversation()
                st.rerun()
        
        st.divider()
        
        # Ejemplos de uso
        st.subheader("💡 Ejemplos")
        st.markdown("""
        **Consultar estado:**
        - "¿Cuál es el estado del envío 14309635?"
        - "Estado de mi paquete 1395083"
        
        **Reprogramar entrega:**
        - "Necesito cambiar la entrega del 14309635 para mañana"
        - "Reprogramar envío 1395083 para el 25/01"
        
        **Reportar problema:**
        - "Mi paquete 14309635 llegó dañado"
        - "El envío 1395083 no ha llegado"
        """)

if __name__ == "__main__":
    main()
