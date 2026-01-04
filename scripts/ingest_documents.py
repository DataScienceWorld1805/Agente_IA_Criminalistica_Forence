"""
Script para ingerir documentos PDF al sistema RAG criminológico.
"""
import sys
import logging
from pathlib import Path

# Agregar raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingest import PDFLoader, DocumentPreprocessor, MetadataExtractor
from chunking import SemanticChunker
from embeddings import BGEM3Embedder
from vectorstore import ChromaManager
from utils import ForensicLogger
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ingest_directory(directory: Path, collection_name: str = None):
    """
    Ingesta todos los PDFs de un directorio.
    
    Args:
        directory: Directorio con PDFs
        collection_name: Nombre de la colección (se infiere si no se proporciona)
    """
    if not directory.exists():
        logger.warning(f"Directorio no existe: {directory}")
        return
    
    logger.info(f"Procesando directorio: {directory}")
    
    # Inicializar componentes
    pdf_loader = PDFLoader()
    preprocessor = DocumentPreprocessor()
    metadata_extractor = MetadataExtractor()
    chunker = SemanticChunker()
    embedder = BGEM3Embedder()
    chroma_manager = ChromaManager()
    forensic_logger = ForensicLogger()
    
    # Cargar PDFs
    documents = pdf_loader.load_directory(directory)
    
    if not documents:
        logger.warning(f"No se encontraron PDFs en {directory}")
        return
    
    logger.info(f"Encontrados {len(documents)} documentos PDF")
    
    total_chunks = 0
    
    for doc in documents:
        try:
            # Preprocesar
            preprocessed = preprocessor.preprocess(doc)
            
            # Extraer metadata
            metadata = metadata_extractor.extract(preprocessed)
            
            # Determinar colección
            if not collection_name:
                collection_name = chroma_manager.determine_collection(metadata)
            
            # Chunking
            chunks = chunker.chunk_document(preprocessed)
            
            if not chunks:
                logger.warning(f"No se generaron chunks para {metadata.get('filename', 'unknown')}")
                continue
            
            # Enriquecer metadata de chunks
            enriched_chunks = []
            for chunk in chunks:
                chunk_metadata = metadata_extractor.enrich_chunk_metadata(
                    chunk['text'],
                    chunk['metadata']
                )
                enriched_chunks.append({
                    'text': chunk['text'],
                    'metadata': chunk_metadata
                })
            
            # Generar embeddings
            texts = [chunk['text'] for chunk in enriched_chunks]
            embeddings = embedder.embed_documents(texts)
            
            # Preparar datos para ChromaDB
            metadatas = [chunk['metadata'] for chunk in enriched_chunks]
            ids = [chunk['metadata'].get('chunk_id', f"chunk_{i}") 
                   for i, chunk in enumerate(enriched_chunks)]
            
            # Agregar a ChromaDB
            chroma_manager.add_documents(
                collection_name=collection_name,
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            total_chunks += len(enriched_chunks)
            
            # Logging
            forensic_logger.log_ingestion(
                file_path=metadata.get('source', 'unknown'),
                chunks_created=len(enriched_chunks),
                collection=collection_name,
                metadata=metadata
            )
            
            logger.info(f"Procesado: {metadata.get('filename', 'unknown')} -> {len(enriched_chunks)} chunks en {collection_name}")
            
        except Exception as e:
            logger.error(f"Error procesando documento: {e}")
            continue
    
    logger.info(f"Ingesta completada: {total_chunks} chunks totales en colección '{collection_name}'")


def main():
    """Función principal."""
    logger.info("Iniciando ingesta de documentos...")
    
    # Procesar cada directorio de datos
    directories = {
        settings.FBI_DOCUMENTS_DIR: "forensic_cases",
        settings.FORENSIC_MANUAL_DIR: "forensic_cases",
        settings.ACADEMIC_PAPERS_DIR: "criminology_theory",
        settings.CASE_STUDIES_DIR: "forensic_cases",
        settings.LEGISLATION_DIR: "legislation"
    }
    
    for directory, default_collection in directories.items():
        if directory.exists() and any(directory.glob("*.pdf")):
            ingest_directory(directory, default_collection)
        else:
            logger.info(f"Directorio vacío o no existe: {directory}")
    
    # También procesar PDFs directamente en data/ (fallback)
    if settings.DATA_DIR.exists():
        pdf_files = list(settings.DATA_DIR.glob("*.pdf"))
        if pdf_files:
            logger.info(f"Encontrados {len(pdf_files)} PDFs directamente en data/. Procesando...")
            # Usar colección por defecto para PDFs en la raíz
            ingest_directory(settings.DATA_DIR, "forensic_cases")
    
    logger.info("Ingesta completada")


if __name__ == "__main__":
    main()
