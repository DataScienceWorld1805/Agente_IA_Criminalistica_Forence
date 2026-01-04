"""
Reranker opcional usando cross-encoder para mejorar relevancia.
"""
import logging
from typing import List, Dict, Optional, Any
import numpy as np
from config import settings

logger = logging.getLogger(__name__)


class Reranker:
    """Reranker semántico usando cross-encoder."""
    
    def __init__(self, model_name: str = None, use_reranker: bool = None):
        """
        Inicializa el reranker.
        
        Args:
            model_name: Nombre del modelo cross-encoder (default: config)
            use_reranker: Si usar reranking (default: config)
        """
        self.model_name = model_name or settings.RERANKER_MODEL
        self.use_reranker = use_reranker if use_reranker is not None else settings.USE_RERANKER
        self.model = None
        
        if self.use_reranker:
            self._load_model()
    
    def _load_model(self):
        """Carga el modelo cross-encoder."""
        try:
            logger.info(f"Cargando reranker: {self.model_name}")
            
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(self.model_name)
            
            logger.info("Reranker cargado exitosamente")
            
        except ImportError:
            logger.warning("sentence-transformers no disponible para reranking. Deshabilitando reranker.")
            self.use_reranker = False
            self.model = None
        except Exception as e:
            logger.error(f"Error cargando reranker: {e}")
            self.use_reranker = False
            self.model = None
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerankea documentos basándose en relevancia semántica.
        
        Args:
            query: Texto de la consulta
            documents: Lista de documentos a rerankear
            top_k: Número de documentos a retornar (None = todos)
            
        Returns:
            Documentos rerankeados ordenados por relevancia
        """
        if not self.use_reranker or not self.model or not documents:
            return documents
        
        if len(documents) == 1:
            return documents
        
        logger.info(f"Rerankeando {len(documents)} documentos")
        
        try:
            # Preparar pares (query, document) para el cross-encoder
            pairs = [(query, doc['text']) for doc in documents]
            
            # Calcular scores
            scores = self.model.predict(pairs)
            
            # Si scores es un array 1D, convertir a lista
            if isinstance(scores, np.ndarray):
                scores = scores.tolist()
            
            # Agregar scores a documentos
            for doc, score in zip(documents, scores):
                doc['rerank_score'] = float(score)
            
            # Ordenar por score descendente
            reranked = sorted(documents, key=lambda x: x.get('rerank_score', 0.0), reverse=True)
            
            # Priorizar fuentes oficiales
            reranked = self._prioritize_official_sources(reranked)
            
            # Retornar top_k si se especifica
            if top_k:
                reranked = reranked[:top_k]
            
            logger.info(f"Reranking completado. Top score: {reranked[0].get('rerank_score', 0.0):.4f}")
            
            return reranked
            
        except Exception as e:
            logger.error(f"Error en reranking: {e}")
            return documents  # Retornar documentos originales en caso de error
    
    def _prioritize_official_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioriza documentos por confiabilidad: alta > media > baja.
        
        Args:
            documents: Documentos ya ordenados por score
            
        Returns:
            Documentos reordenados con prioridad a alta confiabilidad
        """
        high_reliability_docs = []
        medium_reliability_docs = []
        low_reliability_docs = []
        
        for doc in documents:
            reliability = doc.get('metadata', {}).get('source_reliability', 'media')
            
            if reliability == 'alta':
                high_reliability_docs.append(doc)
            elif reliability == 'media':
                medium_reliability_docs.append(doc)
            else:
                low_reliability_docs.append(doc)
        
        # Combinar: primero alta confiabilidad, luego media, luego baja
        # (cada grupo mantiene su orden por score)
        return high_reliability_docs + medium_reliability_docs + low_reliability_docs
    
    def is_available(self) -> bool:
        """Verifica si el reranker está disponible."""
        return self.use_reranker and self.model is not None
