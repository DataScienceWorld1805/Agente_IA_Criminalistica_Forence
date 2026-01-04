"""
Sistema de logging forense con trazabilidad completa.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)


class ForensicLogger:
    """Logger forense con trazabilidad completa de consultas y respuestas."""
    
    def __init__(self, log_dir: Path = None):
        """
        Inicializa el logger forense.
        
        Args:
            log_dir: Directorio para logs (default: config)
        """
        self.log_dir = Path(log_dir or settings.LOG_DIR)
        self.log_dir.mkdir(exist_ok=True, parents=True)
        
        # Configurar logging estándar
        self._setup_standard_logging()
    
    def _setup_standard_logging(self):
        """Configura logging estándar de Python."""
        log_file = self.log_dir / "rag_system.log"
        
        logging.basicConfig(
            level=getattr(logging, settings.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def log_query(
        self,
        query: str,
        documents_used: list,
        prompt_final: str,
        response: str,
        sources: list,
        metadata: Dict[str, Any] = None,
        error: Optional[str] = None
    ) -> str:
        """
        Registra una consulta completa con trazabilidad forense.
        
        Args:
            query: Pregunta original
            documents_used: Documentos recuperados y usados
            prompt_final: Prompt final enviado al LLM
            response: Respuesta generada
            sources: Fuentes citadas
            metadata: Metadata adicional
            error: Error si ocurrió alguno
            
        Returns:
            ID del log generado
        """
        timestamp = datetime.now()
        log_id = f"query_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
        
        log_entry = {
            "log_id": log_id,
            "timestamp": timestamp.isoformat(),
            "query": {
                "original": query,
                "length": len(query)
            },
            "documents": {
                "count": len(documents_used),
                "documents": [
                    {
                        "id": doc.get("id", "unknown"),
                        "source": doc.get("metadata", {}).get("source", "unknown"),
                        "collection": doc.get("collection", "unknown"),
                        "distance": doc.get("distance"),
                        "rerank_score": doc.get("rerank_score"),
                        "preview": doc.get("text", "")[:200] + "..." if doc.get("text") else ""
                    }
                    for doc in documents_used[:10]  # Top 10
                ]
            },
            "prompt": {
                "system_prompt_length": len(prompt_final.split("---")[0]) if "---" in prompt_final else 0,
                "user_prompt_length": len(prompt_final),
                "full_prompt": prompt_final  # Guardar prompt completo para auditoría
            },
            "response": {
                "text": response,
                "length": len(response),
                "sources_count": len(sources)
            },
            "sources": sources,
            "metadata": metadata or {},
            "error": error,
            "system_info": {
                "embedding_model": settings.EMBEDDING_MODEL,
                "llm_model": "groq-llama-3.1-70b",
                "chunk_size": settings.CHUNK_SIZE,
                "reranker_used": settings.USE_RERANKER
            }
        }
        
        # Guardar en archivo JSON
        log_file = self.log_dir / f"{log_id}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)
        
        # También guardar en log diario
        daily_log_file = self.log_dir / f"queries_{timestamp.strftime('%Y%m%d')}.jsonl"
        with open(daily_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        logger.info(f"Query registrada: {log_id}")
        
        return log_id
    
    def log_ingestion(
        self,
        file_path: str,
        chunks_created: int,
        collection: str,
        metadata: Dict[str, Any] = None
    ):
        """
        Registra la ingesta de un documento.
        
        Args:
            file_path: Ruta del archivo procesado
            chunks_created: Número de chunks creados
            collection: Colección donde se almacenó
            metadata: Metadata adicional
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "ingestion",
            "file_path": file_path,
            "chunks_created": chunks_created,
            "collection": collection,
            "metadata": metadata or {}
        }
        
        ingestion_log = self.log_dir / "ingestion.log"
        with open(ingestion_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        logger.info(f"Ingesta registrada: {file_path} -> {chunks_created} chunks en {collection}")
    
    def get_query_log(self, log_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un log de consulta por ID.
        
        Args:
            log_id: ID del log
            
        Returns:
            Entrada del log o None
        """
        log_file = self.log_dir / f"{log_id}.json"
        
        if not log_file.exists():
            return None
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo log {log_id}: {e}")
            return None
    
    def list_recent_queries(self, limit: int = 10) -> list:
        """
        Lista las consultas recientes.
        
        Args:
            limit: Número máximo de consultas
            
        Returns:
            Lista de IDs de logs recientes
        """
        log_files = sorted(
            self.log_dir.glob("query_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        return [f.stem for f in log_files[:limit]]
