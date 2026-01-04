"""
Gestión de ChromaDB para almacenamiento vectorial con múltiples colecciones.
"""
import logging
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from config import settings

logger = logging.getLogger(__name__)


class ChromaManager:
    """Gestor de ChromaDB con múltiples colecciones para diferentes dominios."""
    
    def __init__(self, persist_directory: str = None):
        """
        Inicializa el gestor de ChromaDB.
        
        Args:
            persist_directory: Directorio para persistencia (default: config)
        """
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIRECTORY
        self.client = None
        self.collections = {}
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa el cliente de ChromaDB."""
        try:
            logger.info(f"Inicializando ChromaDB en {self.persist_directory}")
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            logger.info("Cliente ChromaDB inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando ChromaDB: {e}")
            raise
    
    def get_or_create_collection(
        self,
        collection_name: str,
        embedding_function=None
    ) -> chromadb.Collection:
        """
        Obtiene o crea una colección en ChromaDB.
        
        Args:
            collection_name: Nombre de la colección
            embedding_function: Función de embedding (opcional, se usa la default)
            
        Returns:
            Colección de ChromaDB
        """
        if collection_name in self.collections:
            return self.collections[collection_name]
        
        try:
            # Intentar obtener colección existente
            collection = self.client.get_collection(name=collection_name)
            logger.info(f"Colección '{collection_name}' recuperada")
        except Exception:
            # Crear nueva colección
            if embedding_function is None:
                # Usar función de embedding por defecto (se reemplazará con embeddings externos)
                embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=embedding_function,
                metadata={"description": settings.CHROMA_COLLECTIONS.get(collection_name, "")}
            )
            logger.info(f"Colección '{collection_name}' creada")
        
        self.collections[collection_name] = collection
        return collection
    
    def add_documents(
        self,
        collection_name: str,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ):
        """
        Agrega documentos a una colección.
        
        Args:
            collection_name: Nombre de la colección
            texts: Lista de textos
            embeddings: Lista de embeddings
            metadatas: Lista de metadata
            ids: IDs opcionales (se generan si no se proporcionan)
        """
        collection = self.get_or_create_collection(collection_name)
        
        if ids is None:
            ids = [f"{collection_name}_doc_{i}" for i in range(len(texts))]
        
        # Validar que todos los arrays tengan la misma longitud
        if not (len(texts) == len(embeddings) == len(metadatas) == len(ids)):
            raise ValueError("Todos los arrays deben tener la misma longitud")
        
        try:
            # ChromaDB espera embeddings como lista de listas
            collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Agregados {len(texts)} documentos a colección '{collection_name}'")
            
        except Exception as e:
            logger.error(f"Error agregando documentos a '{collection_name}': {e}")
            raise
    
    def query(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Consulta documentos en una colección.
        
        Args:
            collection_name: Nombre de la colección
            query_embeddings: Embeddings de la consulta
            n_results: Número de resultados
            where: Filtros de metadata
            where_document: Filtros de contenido del documento
            
        Returns:
            Resultados de la consulta
        """
        collection = self.get_or_create_collection(collection_name)
        
        try:
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error consultando colección '{collection_name}': {e}")
            raise
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Obtiene información sobre una colección.
        
        Args:
            collection_name: Nombre de la colección
            
        Returns:
            Información de la colección
        """
        collection = self.get_or_create_collection(collection_name)
        
        count = collection.count()
        
        return {
            "name": collection_name,
            "count": count,
            "description": settings.CHROMA_COLLECTIONS.get(collection_name, "")
        }
    
    def list_collections(self) -> List[str]:
        """Lista todas las colecciones disponibles."""
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"Error listando colecciones: {e}")
            return []
    
    def delete_collection(self, collection_name: str):
        """Elimina una colección."""
        try:
            self.client.delete_collection(name=collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            logger.info(f"Colección '{collection_name}' eliminada")
        except Exception as e:
            logger.error(f"Error eliminando colección '{collection_name}': {e}")
            raise
    
    def determine_collection(self, metadata: Dict[str, Any]) -> str:
        """
        Determina la colección apropiada basándose en metadata.
        
        Args:
            metadata: Metadata del documento
            
        Returns:
            Nombre de la colección
        """
        # Lógica para determinar colección basada en metadata
        document_type = metadata.get('document_type', '').lower()
        crime_type = metadata.get('crime_type', '').lower()
        authority = metadata.get('document_authority', '').lower()
        
        # Mapeo de tipos de documento a colecciones
        if 'teoría' in document_type or 'theory' in document_type:
            return "criminology_theory"
        elif 'caso' in document_type or 'case' in document_type:
            if 'serial' in crime_type:
                return "serial_killers"
            else:
                return "forensic_cases"
        elif 'legislación' in document_type or 'legislation' in document_type:
            return "legislation"
        elif 'técnica' in document_type or 'technique' in document_type:
            return "investigation_techniques"
        else:
            # Default basado en tipo de crimen
            if 'serial' in crime_type:
                return "serial_killers"
            else:
                return "forensic_cases"
    
    def reset_collection(self, collection_name: str):
        """Resetea una colección (elimina todos los documentos)."""
        try:
            self.delete_collection(collection_name)
            # Recrear colección vacía
            self.get_or_create_collection(collection_name)
            logger.info(f"Colección '{collection_name}' reseteada")
        except Exception as e:
            logger.error(f"Error reseteando colección '{collection_name}': {e}")
            raise
