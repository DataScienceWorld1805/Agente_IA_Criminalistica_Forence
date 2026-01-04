"""
Definición del grafo LangGraph para el sistema RAG criminológico.
"""
import logging
from langgraph.graph import StateGraph, END
from graph.state import RAGState
from graph.nodes import retrieve_node, rerank_node, generate_node, format_response_node
from retriever import AdvancedRetriever, Reranker
from llm import GroqClient
from config import settings

logger = logging.getLogger(__name__)


def create_rag_graph(
    retriever: AdvancedRetriever,
    reranker: Reranker,
    llm_client: GroqClient
) -> StateGraph:
    """
    Crea el grafo LangGraph para el sistema RAG.
    
    Args:
        retriever: Retriever avanzado
        reranker: Reranker opcional
        llm_client: Cliente Groq
        
    Returns:
        Grafo LangGraph configurado
    """
    logger.info("Creando grafo LangGraph para RAG criminológico")
    
    # Crear grafo
    workflow = StateGraph(RAGState)
    
    # Agregar nodos
    workflow.add_node(
        "retrieve",
        lambda state: retrieve_node(state, retriever)
    )
    
    workflow.add_node(
        "rerank",
        lambda state: rerank_node(state, reranker)
    )
    
    workflow.add_node(
        "generate",
        lambda state: generate_node(state, llm_client)
    )
    
    workflow.add_node(
        "format_response",
        lambda state: format_response_node(state)
    )
    
    # Definir flujo
    workflow.set_entry_point("retrieve")
    
    # Flujo condicional: rerank solo si está habilitado
    workflow.add_conditional_edges(
        "retrieve",
        lambda state: "rerank" if settings.USE_RERANKER and reranker.is_available() else "generate",
        {
            "rerank": "rerank",
            "generate": "generate"
        }
    )
    
    # Después de rerank, ir a generate
    workflow.add_edge("rerank", "generate")
    
    # Después de generate, formatear respuesta
    workflow.add_edge("generate", "format_response")
    
    # Finalizar
    workflow.add_edge("format_response", END)
    
    # Compilar grafo
    app = workflow.compile()
    
    logger.info("Grafo LangGraph creado exitosamente")
    
    return app
