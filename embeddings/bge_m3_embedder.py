"""
Embeddings multilingües usando BGE-M3 para el sistema RAG criminológico.
"""
import logging
from typing import List, Union
import numpy as np
from config import settings

logger = logging.getLogger(__name__)


class BGEM3Embedder:
    """Wrapper para embeddings BGE-M3 multilingües."""
    
    def __init__(self, model_name: str = None, device: str = None):
        """
        Inicializa el embedder BGE-M3.
        
        Args:
            model_name: Nombre del modelo (default: config)
            device: Dispositivo ('cpu' o 'cuda', default: config)
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.device = device or settings.EMBEDDING_DEVICE
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Carga el modelo BGE-M3."""
        try:
            logger.info(f"Cargando modelo BGE-M3: {self.model_name}")
            
            # Intentar con FlagEmbedding primero (recomendado para BGE-M3)
            try:
                from FlagEmbedding import FlagModel
                self.model = FlagModel(
                    self.model_name,
                    query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
                    use_fp16=False  # Usar FP32 para compatibilidad
                )
                logger.info("Modelo cargado con FlagEmbedding")
                self.backend = "flagembedding"
            except ImportError:
                # Fallback a sentence-transformers
                logger.info("FlagEmbedding no disponible, usando sentence-transformers")
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name, device=self.device)
                logger.info("Modelo cargado con sentence-transformers")
                self.backend = "sentence_transformers"
            
            logger.info(f"Modelo BGE-M3 cargado exitosamente en {self.device}")
            
        except Exception as e:
            logger.error(f"Error cargando modelo BGE-M3: {e}")
            raise
    
    def embed_documents(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Genera embeddings para una lista de documentos.
        
        Args:
            texts: Lista de textos a embedear
            batch_size: Tamaño del batch para procesamiento
            
        Returns:
            Lista de vectores de embeddings
        """
        if not texts:
            return []
        
        logger.info(f"Generando embeddings para {len(texts)} documentos")
        
        try:
            if self.backend == "flagembedding":
                # FlagEmbedding maneja batching internamente
                # FlagEmbedding normaliza automáticamente, no necesita el parámetro
                embeddings = self.model.encode(
                    texts,
                    batch_size=batch_size
                )
            else:
                # sentence-transformers
                embeddings = self.model.encode(
                    texts,
                    batch_size=batch_size,
                    normalize_embeddings=True,
                    show_progress_bar=len(texts) > 10
                )
            
            # Convertir a lista de listas
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()
            
            logger.info(f"Embeddings generados: {len(embeddings)} vectores de dimensión {len(embeddings[0]) if embeddings else 0}")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generando embeddings: {e}")
            raise
    
    def embed_query(self, query: str) -> List[float]:
        """
        Genera embedding para una consulta.
        
        Args:
            query: Texto de la consulta
            
        Returns:
            Vector de embedding
        """
        try:
            if self.backend == "flagembedding":
                # FlagEmbedding tiene método específico para queries
                embedding = self.model.encode_queries([query])
                if isinstance(embedding, np.ndarray):
                    embedding = embedding[0].tolist()
                else:
                    embedding = embedding[0]
            else:
                # sentence-transformers
                embedding = self.model.encode(
                    query,
                    normalize_embeddings=True
                )
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
            
            # Normalizar manualmente si es necesario (para FlagEmbedding)
            if self.backend == "flagembedding" and isinstance(embedding, (list, np.ndarray)):
                if isinstance(embedding, list):
                    embedding = np.array(embedding)
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = (embedding / norm).tolist()
                else:
                    embedding = embedding.tolist()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generando embedding de consulta: {e}")
            raise
    
    def embed(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Genera embeddings (método genérico).
        
        Args:
            text: Texto único o lista de textos
            
        Returns:
            Embedding único o lista de embeddings
        """
        if isinstance(text, str):
            return self.embed_query(text)
        else:
            return self.embed_documents(text)
    
    @property
    def dimension(self) -> int:
        """Retorna la dimensión de los embeddings."""
        return settings.EMBEDDING_DIMENSION  # BGE-M3 tiene 1024 dimensiones
