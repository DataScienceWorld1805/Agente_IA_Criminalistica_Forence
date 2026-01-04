"""
Interfaz Gradio profesional tipo ChatGPT para el sistema RAG criminológico.
Versión simplificada y funcional.
"""
import logging
import gradio as gr
from typing import Tuple, List, Optional
from ui.cli import RAGCLI
from graph.state import RAGState
from prompts import format_prompt_with_context

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar el sistema RAG (se inicializa una vez al cargar el módulo)
_rag_system: Optional[RAGCLI] = None


def get_rag_system() -> RAGCLI:
    """Obtiene o inicializa el sistema RAG (singleton)."""
    global _rag_system
    if _rag_system is None:
        logger.info("Inicializando sistema RAG para Gradio...")
        _rag_system = RAGCLI()
        logger.info("Sistema RAG inicializado")
    return _rag_system


def format_response_with_citations(response: str, sources: list) -> str:
    """
    Formatea la respuesta con citas profesionales integradas.
    
    Args:
        response: Respuesta del LLM
        sources: Lista de fuentes
        
    Returns:
        Respuesta formateada con citas profesionales y legibles
    """
    if not sources:
        return response
    
    # Agregar sección de referencias profesional
    citations_section = "\n\n---\n\n"
    citations_section += "## 📚 Referencias Consultadas\n\n"
    
    for i, source in enumerate(sources, 1):
        source_name = source.get('source', 'Fuente desconocida')
        # Limpiar nombres de archivo largos
        if len(source_name) > 60:
            parts = source_name.replace('\\', '/').split('/')
            if len(parts) > 1:
                source_name = "..." + "/".join(parts[-2:])
            else:
                source_name = source_name[:57] + "..."
        
        authority = source.get('document_authority', '')
        year = source.get('year', '')
        reliability = source.get('source_reliability', '')
        
        # Formato profesional de cita
        citation = f"**[{i}]** {source_name}"
        
        if authority and authority != 'otro':
            citation += f" - *{authority}*"
        
        if year:
            citation += f" ({year})"
        
        if reliability:
            reliability_text = f"Confiabilidad: {reliability.upper()}"
            citation += f" - {reliability_text}"
        
        citations_section += f"{citation}\n\n"
    
    return response + citations_section


def format_sources_panel(sources: list) -> str:
    """
    Formatea las fuentes para el panel lateral de manera clara y legible.
    
    Args:
        sources: Lista de fuentes
        
    Returns:
        HTML formateado con las fuentes
    """
    if not sources:
        return """
        <div style='text-align: center; padding: 80px 20px; color: #6c757d; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'>
            <div style='font-size: 64px; margin-bottom: 20px; opacity: 0.2;'>📚</div>
            <p style='font-size: 16px; font-weight: 500; margin: 0; color: #495057;'>Fuentes consultadas</p>
            <p style='font-size: 14px; margin-top: 8px; color: #868e96;'>Aparecerán aquí después de realizar una consulta</p>
        </div>
        """
    
    html = """
    <style>
        .sources-wrapper {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }
        .sources-header {
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid #dee2e6;
        }
        .sources-title {
            font-size: 20px;
            font-weight: 700;
            color: #212529;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .sources-count {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }
        .source-card {
            background: #ffffff;
            border: 1px solid #dee2e6;
            border-left: 4px solid #667eea;
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 16px;
            transition: all 0.2s ease;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .source-card:hover {
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
            transform: translateY(-2px);
            border-left-color: #764ba2;
        }
        .source-number {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            text-align: center;
            line-height: 28px;
            font-weight: 700;
            font-size: 13px;
            margin-right: 12px;
            vertical-align: middle;
        }
        .source-name {
            font-size: 15px;
            font-weight: 600;
            color: #1a202c;
            margin-bottom: 12px;
            line-height: 1.5;
            word-break: break-word;
        }
        .source-details {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        .detail-badge {
            display: inline-flex;
            align-items: center;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-authority {
            background: #e7f5ff;
            color: #1971c2;
            border: 1px solid #a5d8ff;
        }
        .badge-high {
            background: #d3f9d8;
            color: #2b8a3e;
            border: 1px solid #8ce99a;
        }
        .badge-medium {
            background: #fff3bf;
            color: #f59f00;
            border: 1px solid #ffd43b;
        }
        .badge-low {
            background: #ffe3e3;
            color: #c92a2a;
            border: 1px solid #ffa8a8;
        }
        .badge-year {
            background: #f8f9fa;
            color: #495057;
            border: 1px solid #dee2e6;
        }
    </style>
    """
    
    html += "<div class='sources-wrapper'>"
    html += "<div class='sources-header'>"
    html += "<div class='sources-title'>"
    html += "<span>📚</span>"
    html += "<span>Fuentes Consultadas</span>"
    html += f"<span class='sources-count'>{len(sources)}</span>"
    html += "</div>"
    html += "</div>"
    
    for i, source in enumerate(sources, 1):
        source_name = source.get('source', 'Fuente desconocida')
        # Limpiar nombres de archivo largos para mejor legibilidad
        if len(source_name) > 50:
            parts = source_name.replace('\\', '/').split('/')
            if len(parts) > 1:
                source_name = ".../" + "/".join(parts[-2:])
            else:
                source_name = source_name[:47] + "..."
        
        html += "<div class='source-card'>"
        html += f"<div class='source-name'><span class='source-number'>{i}</span>{source_name}</div>"
        html += "<div class='source-details'>"
        
        if source.get('document_authority') and source.get('document_authority') != 'otro':
            html += f"<span class='detail-badge badge-authority'>{source['document_authority']}</span>"
        
        if source.get('source_reliability'):
            reliability = source['source_reliability']
            badge_class = f"badge-{reliability}"
            html += f"<span class='detail-badge {badge_class}'>{reliability.upper()}</span>"
        
        if source.get('year'):
            html += f"<span class='detail-badge badge-year'>{source['year']}</span>"
        
        html += "</div>"
        html += "</div>"
    
    html += "</div>"
    return html


def process_chat_message(message: str, history) -> Tuple:
    """
    Procesa un mensaje del chat y retorna el historial actualizado.
    
    Args:
        message: Mensaje del usuario
        history: Historial de conversación (formato Gradio 6.x: lista de diccionarios con 'role' y 'content')
        
    Returns:
        Tupla con (historial_actualizado, fuentes_html) - las fuentes se incluyen en las citas de la respuesta
    """
    if not message or not message.strip():
        return history if history else [], ""
    
    # Normalizar historial a formato Gradio 6.x (lista de diccionarios)
    # Formato: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    normalized_history = []
    if history:
        for msg in history:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                # Ya es un diccionario válido
                normalized_history.append({"role": str(msg["role"]), "content": str(msg["content"])})
            elif isinstance(msg, (list, tuple)) and len(msg) >= 2:
                # Convertir formato antiguo (tupla) a diccionario
                normalized_history.append({"role": "user", "content": str(msg[0])})
                normalized_history.append({"role": "assistant", "content": str(msg[1])})
            elif hasattr(msg, "role") and hasattr(msg, "content"):
                # Objeto tipo ChatMessage, convertir a diccionario
                normalized_history.append({"role": str(msg.role), "content": str(msg.content)})
    
    history = normalized_history
    
    try:
        rag_system = get_rag_system()
        
        # Estado inicial
        initial_state: RAGState = {
            "query": message,
            "documents": [],
            "reranked_docs": None,
            "context": None,
            "response": None,
            "sources": [],
            "metadata": {},
            "error": None
        }
        
        # Ejecutar grafo
        final_state = rag_system.graph.invoke(initial_state)
        
        # Verificar errores
        if final_state.get("error"):
            error_msg = final_state['error']
            # Mejorar mensaje de error para rate limits
            if "Límite diario de tokens" in error_msg or "rate_limit" in error_msg.lower():
                error_response = f"""**⚠️ Límite de Tokens Alcanzado**

{error_msg}

**Soluciones:**
1. **Esperar**: El límite se reinicia cada 24 horas
2. **Cambiar de modelo**: Edita tu archivo `.env` y cambia `GROQ_MODEL` a:
   - `llama-3.1-8b-instant` (más rápido, límite más alto)
   - `mixtral-8x7b-32768` (buena calidad, límite más alto)
3. **Upgrade**: Considera actualizar tu plan en [Groq Console](https://console.groq.com/settings/billing)

Después de cambiar el modelo, reinicia la aplicación."""
            else:
                error_response = f"**Error:** {error_msg}"
            
            # Usar formato Gradio 6.x: diccionarios con role y content
            history.append({"role": "user", "content": str(message)})
            history.append({"role": "assistant", "content": str(error_response)})
            return history, ""
        
        response = final_state.get("response", "No se generó respuesta")
        sources = final_state.get("sources", [])
        
        # Logging forense
        rag_system.forensic_logger.log_query(
            query=message,
            documents_used=final_state.get("reranked_docs") or final_state.get("documents", []),
            prompt_final=format_prompt_with_context(message, final_state.get("context", "")),
            response=response,
            sources=sources,
            metadata=final_state.get("metadata", {}),
            error=final_state.get("error")
        )
        
        # Formatear respuesta con citas profesionales
        formatted_response = format_response_with_citations(response, sources)
        
        # Formatear fuentes para el panel
        sources_html = format_sources_panel(sources)
        
        # Agregar al historial usando formato Gradio 6.x: diccionarios con role y content
        history.append({"role": "user", "content": str(message)})
        history.append({"role": "assistant", "content": str(formatted_response)})
        
        return history, sources_html
        
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}", exc_info=True)
        error_response = f"**Error procesando consulta:**\n\n{str(e)}"
        history.append({"role": "user", "content": str(message)})
        history.append({"role": "assistant", "content": str(error_response)})
        return history, ""


# Ejemplos de consultas
EXAMPLE_QUERIES = [
    "¿Qué es la medicina forense?",
    "¿Cuál es el modus operandi típico de homicidas seriales organizados?",
    "¿Qué técnicas forenses se usan en análisis de balística?",
    "¿Cómo se analiza una escena de crimen?",
    "¿Qué es la perfilación criminal?",
]


def create_interface():
    """Crea y configura la interfaz Gradio profesional tipo ChatGPT."""
    
    with gr.Blocks(title="Sistema RAG Criminológico - Chat") as app:
        # Header profesional y moderno
        header_html = """
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 32px 24px; 
                    border-radius: 12px; 
                    margin-bottom: 24px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <div style="max-width: 1200px; margin: 0 auto;">
                <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                    <div style="font-size: 36px;">🔬</div>
                    <div>
                        <h1 style="color: #ffffff; 
                                   font-size: 28px; 
                                   font-weight: 700; 
                                   margin: 0; 
                                   font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                                   letter-spacing: -0.5px;">
                            Sistema RAG Criminológico
                        </h1>
                        <p style="color: rgba(255, 255, 255, 0.9); 
                                  font-size: 14px; 
                                  margin: 4px 0 0 0;
                                  font-weight: 500;">
                            Asistente Inteligente de Investigación Forense
                        </p>
                    </div>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255, 255, 255, 0.2);">
                    <div style="background: rgba(255, 255, 255, 0.15); 
                                backdrop-filter: blur(10px);
                                padding: 8px 16px; 
                                border-radius: 20px; 
                                color: #ffffff; 
                                font-size: 13px; 
                                font-weight: 500;">
                        🧬 Medicina Forense
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.15); 
                                backdrop-filter: blur(10px);
                                padding: 8px 16px; 
                                border-radius: 20px; 
                                color: #ffffff; 
                                font-size: 13px; 
                                font-weight: 500;">
                        🔍 Criminología
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.15); 
                                backdrop-filter: blur(10px);
                                padding: 8px 16px; 
                                border-radius: 20px; 
                                color: #ffffff; 
                                font-size: 13px; 
                                font-weight: 500;">
                        🎯 Balística
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.15); 
                                backdrop-filter: blur(10px);
                                padding: 8px 16px; 
                                border-radius: 20px; 
                                color: #ffffff; 
                                font-size: 13px; 
                                font-weight: 500;">
                        📋 Análisis de Escenas
                    </div>
                </div>
                <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.2);">
                    <p style="color: rgba(255, 255, 255, 0.85); 
                              font-size: 12px; 
                              margin: 0;
                              font-weight: 400;
                              display: flex; 
                              align-items: center; 
                              gap: 8px;">
                        <span>⚡</span>
                        <span>Powered by <strong>LangGraph</strong>, <strong>Groq LLM</strong>, y <strong>ChromaDB</strong></span>
                        <span style="margin-left: auto; opacity: 0.7;">v2.0</span>
                    </p>
                </div>
            </div>
        </div>
        """
        gr.HTML(header_html)
        
        # Contenido principal - Chat a ancho completo
        chatbot = gr.Chatbot(
            label="",
            value=[],
            height=650,
            show_label=False,
            container=True
        )
        
        with gr.Row():
            msg = gr.Textbox(
                label="",
                placeholder="Escribe tu consulta aquí...",
                show_label=False,
                container=False,
                scale=4
            )
            submit_btn = gr.Button("Enviar", variant="primary", scale=1)
        
        with gr.Row():
            clear_btn = gr.Button("Limpiar Conversación", variant="secondary")
        
        # Ejemplos
        gr.Markdown("### 💡 Ejemplos de Consultas")
        examples = gr.Examples(
            examples=EXAMPLE_QUERIES,
            inputs=msg,
            label=""
        )
        
        # Footer
        gr.Markdown("""
        ---
        **⚠️ Uso académico y de investigación únicamente**
        """)
        
        # Event handlers
        def respond(message, history):
            """Procesa el mensaje y actualiza el chat."""
            # Asegurarse de que history sea una lista
            if history is None:
                history = []
            elif not isinstance(history, list):
                history = []
            
            # Procesar mensaje (retorna lista de diccionarios formato Gradio 6.x)
            new_history, _ = process_chat_message(message, history)
            
            # Asegurarse de que new_history sea una lista válida de diccionarios
            if not isinstance(new_history, list):
                new_history = []
            else:
                # Validar que todos los elementos sean diccionarios válidos
                validated_history = []
                for msg in new_history:
                    if isinstance(msg, dict) and "role" in msg and "content" in msg:
                        validated_history.append({"role": str(msg["role"]), "content": str(msg["content"])})
                new_history = validated_history
            
            return new_history, ""
        
        msg.submit(respond, [msg, chatbot], [chatbot, msg])
        submit_btn.click(respond, [msg, chatbot], [chatbot, msg])
        
        clear_btn.click(
            lambda: ([]),
            outputs=[chatbot]
        )
    
    return app


def launch_app(server_name: str = "0.0.0.0", server_port: int = 7860, share: bool = False):
    """
    Lanza la aplicación Gradio.
    
    Args:
        server_name: Dirección del servidor
        server_port: Puerto del servidor
        share: Si crear un enlace público compartido
    """
    # Tema personalizado
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="gray",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "-apple-system", "sans-serif"]
    )
    
    # CSS mínimo pero efectivo
    custom_css = """
    .gradio-container {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    """
    
    app = create_interface()
    app.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        show_error=True,
        theme=theme,
        css=custom_css
    )


if __name__ == "__main__":
    launch_app()
