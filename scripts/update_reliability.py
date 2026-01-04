"""
Script para actualizar la confiabilidad de documentos existentes en ChromaDB.
Esto actualiza los documentos ya indexados para que tengan 'alta' confiabilidad.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from vectorstore import ChromaManager
from ingest import MetadataExtractor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_reliability():
    """Actualiza la confiabilidad de todos los documentos a 'alta'."""
    logger.info("Actualizando confiabilidad de documentos en ChromaDB...")
    
    chroma_manager = ChromaManager()
    metadata_extractor = MetadataExtractor()
    
    collections = chroma_manager.list_collections()
    
    total_updated = 0
    
    for collection_name in collections:
        logger.info(f"Procesando colección: {collection_name}")
        
        try:
            collection = chroma_manager.get_or_create_collection(collection_name)
            count = collection.count()
            
            if count == 0:
                logger.info(f"  Colección vacía, saltando...")
                continue
            
            logger.info(f"  Documentos en colección: {count}")
            
            # Obtener todos los documentos (en lotes)
            batch_size = 100
            updated = 0
            
            for offset in range(0, count, batch_size):
                # Obtener batch de documentos
                results = collection.get(
                    limit=batch_size,
                    offset=offset
                )
                
                if not results['ids']:
                    break
                
                # Actualizar metadata
                new_metadatas = []
                ids_to_update = []
                
                for i, metadata in enumerate(results['metadatas']):
                    if metadata:
                        # Actualizar confiabilidad a 'alta' si no es ya alta
                        current_reliability = metadata.get('source_reliability', 'media')
                        
                        if current_reliability != 'alta':
                            new_metadata = metadata.copy()
                            new_metadata['source_reliability'] = 'alta'
                            new_metadatas.append(new_metadata)
                            ids_to_update.append(results['ids'][i])
                
                # Actualizar en ChromaDB
                if ids_to_update:
                    collection.update(
                        ids=ids_to_update,
                        metadatas=new_metadatas
                    )
                    updated += len(ids_to_update)
                    logger.info(f"  Actualizados {updated}/{count} documentos...")
            
            total_updated += updated
            logger.info(f"  Colección {collection_name}: {updated} documentos actualizados")
            
        except Exception as e:
            logger.error(f"Error procesando colección {collection_name}: {e}")
            continue
    
    logger.info(f"\nTotal de documentos actualizados: {total_updated}")
    logger.info("Actualización completada!")


if __name__ == "__main__":
    update_reliability()
