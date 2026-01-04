"""
Retriever avanzado con MMR y filtros de metadata para el sistema RAG criminológico.
"""
import logging
from typing import List, Dict, Optional, Any
import numpy as np
from vectorstore import ChromaManager
from embeddings import BGEM3Embedder
from config import settings

logger = logging.getLogger(__name__)


class AdvancedRetriever:
    """Retriever avanzado con similarity search, metadata filters y MMR."""
    
    def __init__(
        self,
        chroma_manager: ChromaManager,
        embedder: BGEM3Embedder,
        default_k: int = None,
        max_k: int = None,
        mmr_diversity: float = None
    ):
        """
        Inicializa el retriever avanzado.
        
        Args:
            chroma_manager: Gestor de ChromaDB
            embedder: Embedder para consultas
            default_k: Número default de resultados (default: config)
            max_k: Número máximo de resultados (default: config)
            mmr_diversity: Factor de diversidad para MMR (default: config)
        """
        self.chroma_manager = chroma_manager
        self.embedder = embedder
        self.default_k = default_k or settings.DEFAULT_K
        self.max_k = max_k or settings.MAX_K
        self.mmr_diversity = mmr_diversity or settings.MMR_DIVERSITY
    
    def retrieve(
        self,
        query: str,
        collection_names: Optional[List[str]] = None,
        k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        use_mmr: bool = False  # Deshabilitado por defecto para mejor rendimiento
    ) -> List[Dict[str, Any]]:
        """
        Recupera documentos relevantes para una consulta.
        
        Args:
            query: Texto de la consulta
            collection_names: Lista de colecciones a consultar (None = todas, limitado a 3)
            k: Número de resultados (default: default_k)
            filters: Filtros de metadata
            use_mmr: Si usar Max Marginal Relevance (deshabilitado por defecto)
            
        Returns:
            Lista de documentos recuperados con metadata
        """
        k = k or self.default_k
        k = min(k, self.max_k)
        
        logger.info(f"Recuperando documentos para consulta: '{query[:50]}...' (k={k}, mmr={use_mmr})")
        
        # Generar embedding de la consulta
        query_embedding = self.embedder.embed_query(query)
        
        # Determinar colecciones a consultar
        if collection_names is None:
            all_collections = self.chroma_manager.list_collections()
            # OPTIMIZACIÓN: Limitar a 1 colección para máximo rendimiento
            # Priorizar colecciones más relevantes (forensic_cases, criminology_theory)
            priority_collections = ["forensic_cases", "criminology_theory", "investigation_techniques"]
            collection_names = []
            
            # Agregar solo la primera colección prioritaria disponible
            for col in priority_collections:
                if col in all_collections and len(collection_names) < 1:
                    collection_names.append(col)
                    break
            
            # Si no hay colecciones prioritarias, tomar la primera disponible
            if not collection_names and all_collections:
                collection_names = [all_collections[0]]
        
        if not collection_names:
            logger.warning("No hay colecciones disponibles")
            return []
        
        logger.info(f"Consultando {len(collection_names)} colecciones: {collection_names}")
        
        # OPTIMIZACIÓN: Reducir documentos candidatos
        # Si MMR está deshabilitado, obtener solo k documentos por colección
        # Si MMR está habilitado, obtener k + 2 (no k * 2)
        candidates_per_collection = k if not use_mmr else min(k + 2, k * 2)
        
        # Consultar cada colección
        all_results = []
        for collection_name in collection_names:
            try:
                results = self._query_collection(
                    collection_name,
                    query_embedding,
                    candidates_per_collection,
                    filters
                )
                all_results.extend(results)
            except Exception as e:
                logger.warning(f"Error consultando colección '{collection_name}': {e}")
                continue
        
        # Aplicar MMR solo si está habilitado Y hay suficientes resultados
        if use_mmr and len(all_results) > k:
            results = self._apply_mmr(query_embedding, all_results, k)
        else:
            # Ordenar por relevancia y tomar top k
            results = sorted(all_results, key=lambda x: x.get('distance', float('inf')))[:k]
        
        # Priorizar documentos de alta confiabilidad
        results = self._prioritize_by_reliability(results)
        
        logger.info(f"Recuperados {len(results)} documentos")
        
        return results
    
    def _query_collection(
        self,
        collection_name: str,
        query_embedding: List[float],
        k: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Consulta una colección específica."""
        # Construir filtros where para ChromaDB
        where_clause = self._build_where_clause(filters) if filters else None
        
        # Consultar ChromaDB
        results = self.chroma_manager.query(
            collection_name=collection_name,
            query_embeddings=[query_embedding],
            n_results=k,
            where=where_clause
        )
        
        # Formatear resultados
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            documents = results['documents'][0]
            metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(documents)
            distances = results['distances'][0] if results['distances'] else [0.0] * len(documents)
            ids = results['ids'][0] if results['ids'] else [None] * len(documents)
            
            for doc, metadata, distance, doc_id in zip(documents, metadatas, distances, ids):
                formatted_results.append({
                    'text': doc,
                    'metadata': metadata or {},
                    'distance': distance,
                    'id': doc_id,
                    'collection': collection_name
                })
        
        return formatted_results
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construye la cláusula where para ChromaDB.
        
        ChromaDB usa operadores específicos:
        - $eq: igual
        - $ne: no igual
        - $in: en lista
        - $gt, $gte, $lt, $lte: comparaciones
        """
        where_clause = {}
        
        for key, value in filters.items():
            if value is None:
                continue
            
            # Si es una lista, usar $in
            if isinstance(value, list):
                where_clause[key] = {"$in": value}
            # Si es un string, usar $eq
            elif isinstance(value, str):
                where_clause[key] = {"$eq": value}
            # Si es un número, usar $eq
            elif isinstance(value, (int, float)):
                where_clause[key] = {"$eq": value}
            else:
                where_clause[key] = value
        
        return where_clause
    
    def _apply_mmr(
        self,
        query_embedding: List[float],
        candidates: List[Dict[str, Any]],
        k: int
    ) -> List[Dict[str, Any]]:
        """
        Aplica Max Marginal Relevance para diversificar resultados (OPTIMIZADO).
        
        MMR selecciona documentos que son relevantes pero diversos entre sí.
        Versión optimizada que limita el número de comparaciones.
        """
        if not candidates or k <= 0:
            return []
        
        # OPTIMIZACIÓN: Si hay pocos candidatos, usar solo similarity search
        if len(candidates) <= k + 2:
            return sorted(candidates, key=lambda x: x.get('distance', float('inf')))[:k]
        
        # Calcular similitudes con la consulta
        similarities = []
        for candidate in candidates:
            # Usar distancia inversa como similitud
            distance = candidate.get('distance', 1.0)
            similarity = 1.0 / (1.0 + distance)  # Convertir distancia a similitud
            similarities.append(similarity)
        
        # Seleccionar primer documento (más relevante)
        selected = [0]
        selected_indices = set(selected)
        
        # OPTIMIZACIÓN: Pre-calcular similitudes entre candidatos (solo top 20 para velocidad)
        # Limitar a los top candidatos para reducir complejidad
        top_candidates = min(20, len(candidates))
        candidate_similarities = {}
        
        # Iterativamente seleccionar documentos que maximizan MMR
        # OPTIMIZACIÓN: Limitar iteraciones a k + 5 para mejor rendimiento
        max_iterations = min(k + 5, len(candidates))
        
        while len(selected) < k and len(selected) < max_iterations:
            best_score = -float('inf')
            best_idx = None
            
            # OPTIMIZACIÓN: Solo considerar candidatos no seleccionados
            for idx in range(min(top_candidates, len(candidates))):
                if idx in selected_indices:
                    continue
                
                # Relevancia con la consulta
                relevance = similarities[idx]
                
                # Diversidad con documentos ya seleccionados
                # OPTIMIZACIÓN: Solo comparar con los últimos 3 seleccionados
                max_similarity_to_selected = 0.0
                recent_selected = selected[-3:] if len(selected) > 3 else selected
                
                for sel_idx in recent_selected:
                    # Usar distancia aproximada entre candidatos
                    # Si ambos tienen distancia similar, asumir alta similitud
                    sel_distance = candidates[sel_idx].get('distance', 1.0)
                    curr_distance = candidates[idx].get('distance', 1.0)
                    
                    # Similitud aproximada basada en diferencia de distancias
                    distance_diff = abs(sel_distance - curr_distance)
                    similarity = 1.0 / (1.0 + distance_diff)
                    max_similarity_to_selected = max(max_similarity_to_selected, similarity)
                
                # Score MMR: lambda * relevance - (1 - lambda) * max_similarity
                mmr_score = (
                    self.mmr_diversity * relevance -
                    (1 - self.mmr_diversity) * max_similarity_to_selected
                )
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx
            
            if best_idx is not None:
                selected.append(best_idx)
                selected_indices.add(best_idx)
            else:
                break
        
        # Retornar documentos seleccionados en orden
        return [candidates[i] for i in selected]
    
    def retrieve_by_collection(
        self,
        query: str,
        collection_name: str,
        k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recupera documentos de una colección específica.
        
        Args:
            query: Texto de la consulta
            collection_name: Nombre de la colección
            k: Número de resultados
            filters: Filtros de metadata
            
        Returns:
            Lista de documentos recuperados
        """
        return self.retrieve(
            query=query,
            collection_names=[collection_name],
            k=k,
            filters=filters
        )
    
    def filter_by_metadata(
        self,
        documents: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Filtra documentos por metadata (post-retrieval).
        
        Args:
            documents: Lista de documentos
            filters: Filtros a aplicar
            
        Returns:
            Documentos filtrados
        """
        filtered = []
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            matches = True
            
            for key, value in filters.items():
                if key not in metadata:
                    matches = False
                    break
                
                if isinstance(value, list):
                    if metadata[key] not in value:
                        matches = False
                        break
                elif metadata[key] != value:
                    matches = False
                    break
            
            if matches:
                filtered.append(doc)
        
        return filtered
    
    def _prioritize_by_reliability(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioriza documentos por confiabilidad manteniendo el orden de relevancia dentro de cada nivel.
        
        Args:
            documents: Lista de documentos ordenados por relevancia
            
        Returns:
            Documentos reordenados: alta confiabilidad primero, luego media, luego baja
        """
        high_reliability = []
        medium_reliability = []
        low_reliability = []
        
        for doc in documents:
            reliability = doc.get('metadata', {}).get('source_reliability', 'media')
            
            if reliability == 'alta':
                high_reliability.append(doc)
            elif reliability == 'media':
                medium_reliability.append(doc)
            else:
                low_reliability.append(doc)
        
        # Combinar manteniendo el orden de relevancia dentro de cada grupo
        return high_reliability + medium_reliability + low_reliability
    