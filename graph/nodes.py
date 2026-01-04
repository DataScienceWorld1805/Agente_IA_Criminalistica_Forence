"""
Nodos del grafo LangGraph para el sistema RAG criminológico.
"""
import logging
from typing import Dict, Any
from graph.state import RAGState
from retriever import AdvancedRetriever, Reranker
from llm import GroqClient
from prompts import format_prompt_with_context
from config import settings

logger = logging.getLogger(__name__)


def retrieve_node(state: RAGState, retriever: AdvancedRetriever) -> Dict[str, Any]:
    """
    Nodo de recuperación: busca documentos relevantes en ChromaDB.
    
    Args:
        state: Estado actual del grafo
        retriever: Retriever avanzado
        
    Returns:
        Actualización del estado con documentos recuperados
    """
    query = state.get("query", "")
    
    if not query:
        logger.error("Query vacía en nodo de recuperación")
        return {
            "documents": [],
            "error": "Query vacía"
        }
    
    logger.info(f"Recuperando documentos para: '{query[:50]}...'")
    
    try:
        # Recuperar documentos
        # OPTIMIZACIÓN: MMR deshabilitado por defecto para mejor rendimiento
        documents = retriever.retrieve(
            query=query,
            k=settings.DEFAULT_K,
            use_mmr=False  # Deshabilitado para mejor rendimiento
        )
        
        logger.info(f"Recuperados {len(documents)} documentos")
        
        # Crear contexto desde los documentos recuperados
        context = _format_context(documents) if documents else ""
        
        return {
            "documents": documents,
            "context": context,
            "metadata": {
                **state.get("metadata", {}),
                "retrieved_count": len(documents)
            }
        }
        
    except Exception as e:
        logger.error(f"Error en recuperación: {e}")
        return {
            "documents": [],
            "error": str(e)
        }


def rerank_node(state: RAGState, reranker: Reranker) -> Dict[str, Any]:
    """
    Nodo de reranking: mejora la relevancia de documentos recuperados.
    
    Args:
        state: Estado actual del grafo
        reranker: Reranker opcional
        
    Returns:
        Actualización del estado con documentos rerankeados
    """
    query = state.get("query", "")
    documents = state.get("documents", [])
    
    if not documents:
        logger.warning("No hay documentos para rerankear")
        return {
            "reranked_docs": [],
            "context": ""
        }
    
    if not reranker.is_available():
        logger.info("Reranker no disponible, usando documentos originales")
        return {
            "reranked_docs": documents,
            "context": _format_context(documents)
        }
    
    logger.info(f"Rerankeando {len(documents)} documentos")
    
    try:
        reranked_docs = reranker.rerank(
            query=query,
            documents=documents,
            top_k=settings.DEFAULT_K
        )
        
        logger.info(f"Reranking completado: {len(reranked_docs)} documentos")
        
        return {
            "reranked_docs": reranked_docs,
            "context": _format_context(reranked_docs),
            "metadata": {
                **state.get("metadata", {}),
                "reranked_count": len(reranked_docs)
            }
        }
        
    except Exception as e:
        logger.error(f"Error en reranking: {e}")
        # Usar documentos originales en caso de error
        return {
            "reranked_docs": documents,
            "context": _format_context(documents)
        }


def generate_node(state: RAGState, llm_client: GroqClient) -> Dict[str, Any]:
    """
    Nodo de generación: genera respuesta usando Groq LLM.
    
    Args:
        state: Estado actual del grafo
        llm_client: Cliente Groq
        
    Returns:
        Actualización del estado con respuesta generada
    """
    query = state.get("query", "")
    context = state.get("context", "")
    
    if not query:
        logger.error("Query vacía en nodo de generación")
        return {
            "response": "",
            "error": "Query vacía"
        }
    
    if not context:
        logger.warning("Contexto vacío, generando respuesta sin contexto")
    
    logger.info("Generando respuesta con Groq LLM")
    
    try:
        # Formatear prompt con contexto
        prompt = format_prompt_with_context(query, context)
        
        # Generar respuesta con max_tokens reducido para mejor rendimiento
        response = llm_client.generate(prompt, max_tokens=1200)
        
        logger.info(f"Respuesta generada: {len(response)} caracteres")
        
        return {
            "response": response,
            "metadata": {
                **state.get("metadata", {}),
                "response_length": len(response)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generando respuesta: {e}")
        return {
            "response": "",
            "error": str(e)
        }


def format_response_node(state: RAGState) -> Dict[str, Any]:
    """
    Nodo de formateo: formatea la respuesta final con citas y fuentes.
    
    Args:
        state: Estado actual del grafo
        
    Returns:
        Actualización del estado con respuesta formateada y fuentes
    """
    response = state.get("response", "")
    reranked_docs = state.get("reranked_docs") or state.get("documents", [])
    
    if not response:
        logger.warning("No hay respuesta para formatear")
        return {
            "response": "",
            "sources": []
        }
    
    logger.info("Formateando respuesta con citas")
    
    # Extraer fuentes de los documentos usados
    sources = []
    seen_sources = set()
    
    for doc in reranked_docs[:5]:  # Top 5 documentos
        metadata = doc.get("metadata", {})
        source_info = {
            "text": doc.get("text", "")[:200] + "...",  # Preview
            "source": metadata.get("source", "Desconocido"),
            "document_authority": metadata.get("document_authority", "otro"),
            "source_reliability": metadata.get("source_reliability", "media"),
            "year": metadata.get("year"),
            "crime_type": metadata.get("crime_type"),
        }
        
        # Evitar duplicados
        source_key = metadata.get("source", "")
        if source_key and source_key not in seen_sources:
            sources.append(source_info)
            seen_sources.add(source_key)
    
    # Formatear respuesta con citas
    formatted_response = _add_citations(response, sources)
    
    return {
        "response": formatted_response,
        "sources": sources,
        "metadata": {
            **state.get("metadata", {}),
            "sources_count": len(sources)
        }
    }


def _format_context(documents: list) -> str:
    """
    Formatea documentos como contexto para el LLM.
    
    Args:
        documents: Lista de documentos
        
    Returns:
        Contexto formateado
    """
    if not documents:
        return ""
    
    context_parts = []
    
    for i, doc in enumerate(documents, 1):
        text = doc.get("text", "")
        metadata = doc.get("metadata", {})
        source = metadata.get("source", "Fuente desconocida")
        
        context_part = f"[Documento {i} - Fuente: {source}]\n{text}\n"
        context_parts.append(context_part)
    
    return "\n---\n\n".join(context_parts)


def _add_citations(response: str, sources: list) -> str:
    """
    Agrega citas a la respuesta.
    
    Args:
        response: Respuesta original
        sources: Lista de fuentes
        
    Returns:
        Respuesta con citas
    """
    if not sources:
        return response
    
    # Agregar sección de fuentes al final
    citations_section = "\n\n---\n\n**Fuentes consultadas:**\n\n"
    
    for i, source in enumerate(sources, 1):
        source_name = source.get("source", "Fuente desconocida")
        authority = source.get("document_authority", "")
        year = source.get("year", "")
        
        citation = f"{i}. {source_name}"
        if authority:
            citation += f" ({authority})"
        if year:
            citation += f" - {year}"
        
        citations_section += f"- {citation}\n"
    
    return response + citations_section
