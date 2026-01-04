"""
Estado tipado para el grafo LangGraph del sistema RAG criminológico.
"""
from typing import List, Dict, Optional, Any, TypedDict


class RAGState(TypedDict):
    """
    Estado del grafo RAG criminológico.
    
    Campos:
        query: Consulta del usuario
        documents: Documentos recuperados del vector store
        reranked_docs: Documentos después del reranking (opcional)
        context: Contexto formateado para el LLM
        response: Respuesta generada por el LLM
        sources: Fuentes citadas en la respuesta
        metadata: Metadata adicional del proceso
        error: Error si ocurre alguno
    """
    query: str
    documents: List[Dict[str, Any]]
    reranked_docs: Optional[List[Dict[str, Any]]]
    context: Optional[str]
    response: Optional[str]
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    error: Optional[str]
