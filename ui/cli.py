"""
Interfaz CLI para el sistema RAG criminológico.
"""
import sys
import logging
from typing import Optional
from graph import create_rag_graph, RAGState
from retriever import AdvancedRetriever, Reranker
from llm import GroqClient
from embeddings import BGEM3Embedder
from vectorstore import ChromaManager
from prompts import get_system_prompt, format_prompt_with_context
from utils import ForensicLogger
from config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RAGCLI:
    """Interfaz de línea de comandos para el sistema RAG."""
    
    def __init__(self):
        """Inicializa el CLI y todos los componentes necesarios."""
        logger.info("Inicializando sistema RAG criminológico...")
        
        # Inicializar componentes
        self.chroma_manager = ChromaManager()
        self.embedder = BGEM3Embedder()
        self.retriever = AdvancedRetriever(self.chroma_manager, self.embedder)
        self.reranker = Reranker()
        self.llm_client = GroqClient()
        self.forensic_logger = ForensicLogger()
        
        # Crear grafo LangGraph
        self.graph = create_rag_graph(self.retriever, self.reranker, self.llm_client)
        
        logger.info("Sistema RAG inicializado exitosamente")
    
    def query(self, query: str, show_sources: bool = True) -> str:
        """
        Ejecuta una consulta en el sistema RAG.
        
        Args:
            query: Consulta del usuario
            show_sources: Si mostrar fuentes en la salida
            
        Returns:
            Respuesta generada
        """
        if not query or not query.strip():
            return "Error: Consulta vacía"
        
        logger.info(f"Procesando consulta: '{query[:50]}...'")
        
        try:
            # Estado inicial
            initial_state: RAGState = {
                "query": query,
                "documents": [],
                "reranked_docs": None,
                "context": None,
                "response": None,
                "sources": [],
                "metadata": {},
                "error": None
            }
            
            # Ejecutar grafo
            final_state = self.graph.invoke(initial_state)
            
            # Verificar errores
            if final_state.get("error"):
                return f"Error: {final_state['error']}"
            
            response = final_state.get("response", "No se generó respuesta")
            sources = final_state.get("sources", [])
            
            # Logging forense
            self.forensic_logger.log_query(
                query=query,
                documents_used=final_state.get("reranked_docs") or final_state.get("documents", []),
                prompt_final=format_prompt_with_context(query, final_state.get("context", "")),
                response=response,
                sources=sources,
                metadata=final_state.get("metadata", {}),
                error=final_state.get("error")
            )
            
            # Formatear respuesta con fuentes si se solicita
            if show_sources and sources:
                response += self._format_sources_display(sources)
            
            return response
            
        except Exception as e:
            logger.error(f"Error procesando consulta: {e}")
            return f"Error procesando consulta: {str(e)}"
    
    def _format_sources_display(self, sources: list) -> str:
        """Formatea las fuentes para visualización."""
        if not sources:
            return ""
        
        formatted = "\n\n" + "="*60 + "\n"
        formatted += "FUENTES CONSULTADAS:\n"
        formatted += "="*60 + "\n\n"
        
        for i, source in enumerate(sources, 1):
            formatted += f"{i}. {source.get('source', 'Fuente desconocida')}\n"
            if source.get('document_authority'):
                formatted += f"   Autoridad: {source['document_authority']}\n"
            if source.get('source_reliability'):
                formatted += f"   Confiabilidad: {source['source_reliability']}\n"
            if source.get('year'):
                formatted += f"   Año: {source['year']}\n"
            formatted += "\n"
        
        return formatted
    
    def interactive_mode(self):
        """Modo interactivo para consultas múltiples."""
        # Verificar si stdin está disponible
        if not sys.stdin.isatty():
            print("Error: El modo interactivo requiere una terminal con entrada disponible.")
            print("Por favor, proporciona una consulta como argumento:")
            print("  python main.py 'tu consulta aquí'")
            return
        
        print("\n" + "="*60)
        print("SISTEMA RAG CRIMINOLÓGICO")
        print("="*60)
        print("\nEscribe tus consultas sobre criminología, medicina forense,")
        print("balística y escenas de crimen.")
        print("\nComandos especiales:")
        print("  /quit o /exit - Salir")
        print("  /help - Mostrar ayuda")
        print("  /sources on/off - Activar/desactivar visualización de fuentes")
        print("="*60 + "\n")
        
        show_sources = True
        
        while True:
            try:
                query = input("\n> ").strip()
                
                if not query:
                    continue
                
                # Comandos especiales
                if query.lower() in ["/quit", "/exit"]:
                    print("\n¡Hasta luego!")
                    break
                
                if query.lower() == "/help":
                    print("\nEste sistema RAG está especializado en:")
                    print("- Criminología general y teorías")
                    print("- Medicina forense")
                    print("- Balística")
                    print("- Análisis de escenas de crimen")
                    print("- Psicología criminal")
                    print("- Modus Operandi y Signature")
                    print("- Perfilación criminal")
                    continue
                
                if query.lower().startswith("/sources"):
                    parts = query.split()
                    if len(parts) > 1:
                        if parts[1].lower() == "on":
                            show_sources = True
                            print("Visualización de fuentes activada")
                        elif parts[1].lower() == "off":
                            show_sources = False
                            print("Visualización de fuentes desactivada")
                    continue
                
                # Procesar consulta
                print("\nProcesando...")
                response = self.query(query, show_sources=show_sources)
                print("\n" + "-"*60)
                print(response)
                print("-"*60)
                
            except (EOFError, KeyboardInterrupt):
                print("\n\n¡Hasta luego!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                logger.error(f"Error en modo interactivo: {e}")


def main():
    """Función principal del CLI."""
    try:
        cli = RAGCLI()
        
        # Verificar si hay argumentos de línea de comandos
        if len(sys.argv) > 1:
            # Modo de consulta única
            query = " ".join(sys.argv[1:])
            response = cli.query(query)
            print(response)
        else:
            # Verificar si stdin está disponible para modo interactivo
            if sys.stdin.isatty():
                # Modo interactivo
                cli.interactive_mode()
            else:
                # No hay entrada disponible, mostrar mensaje de ayuda
                print("Sistema RAG Criminológico")
                print("="*60)
                print("\nUso:")
                print("  python main.py 'tu consulta aquí'")
                print("\nEjemplo:")
                print("  python main.py '¿Qué es la medicina forense?'")
                print("\nPara modo interactivo, ejecuta desde una terminal:")
                print("  python main.py")
                print("="*60)
            
    except Exception as e:
        logger.error(f"Error inicializando CLI: {e}")
        print(f"Error: {e}")
        sys.exit(1)


def query_rag(query: str) -> str:
    """
    Función de conveniencia para consultar el RAG desde código.
    
    Args:
        query: Consulta del usuario
        
    Returns:
        Respuesta generada
    """
    cli = RAGCLI()
    return cli.query(query, show_sources=False)


if __name__ == "__main__":
    main()
