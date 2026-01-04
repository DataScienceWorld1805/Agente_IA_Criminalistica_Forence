"""
Script para probar el sistema RAG sin necesidad de API key de Groq.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Prueba que todos los imports funcionen."""
    print("="*60)
    print("PRUEBA DE IMPORTS")
    print("="*60)
    
    errors = []
    
    try:
        from config import settings
        print("[OK] config.settings")
    except Exception as e:
        errors.append(f"config.settings: {e}")
        print(f"[ERROR] config.settings: {e}")
    
    try:
        from ingest import PDFLoader, DocumentPreprocessor, MetadataExtractor
        print("[OK] ingest")
    except Exception as e:
        errors.append(f"ingest: {e}")
        print(f"[ERROR] ingest: {e}")
    
    try:
        from chunking import SemanticChunker
        print("[OK] chunking")
    except Exception as e:
        errors.append(f"chunking: {e}")
        print(f"[ERROR] chunking: {e}")
    
    try:
        from embeddings import BGEM3Embedder
        print("[OK] embeddings")
    except Exception as e:
        errors.append(f"embeddings: {e}")
        print(f"[ERROR] embeddings: {e}")
    
    try:
        from vectorstore import ChromaManager
        print("[OK] vectorstore")
    except Exception as e:
        errors.append(f"vectorstore: {e}")
        print(f"[ERROR] vectorstore: {e}")
    
    try:
        from retriever import AdvancedRetriever, Reranker
        print("[OK] retriever")
    except Exception as e:
        errors.append(f"retriever: {e}")
        print(f"[ERROR] retriever: {e}")
    
    try:
        from graph import create_rag_graph, RAGState
        print("[OK] graph")
    except Exception as e:
        errors.append(f"graph: {e}")
        print(f"[ERROR] graph: {e}")
    
    try:
        from prompts import get_system_prompt, format_prompt_with_context
        print("[OK] prompts")
    except Exception as e:
        errors.append(f"prompts: {e}")
        print(f"[ERROR] prompts: {e}")
    
    try:
        from utils import ForensicLogger
        print("[OK] utils")
    except Exception as e:
        errors.append(f"utils: {e}")
        print(f"[ERROR] utils: {e}")
    
    return errors


def test_chromadb():
    """Prueba que ChromaDB esté funcionando."""
    print("\n" + "="*60)
    print("PRUEBA DE CHROMADB")
    print("="*60)
    
    try:
        from vectorstore import ChromaManager
        chroma_manager = ChromaManager()
        
        collections = chroma_manager.list_collections()
        print(f"[OK] ChromaDB conectado")
        print(f"[INFO] Colecciones encontradas: {len(collections)}")
        
        for collection in collections:
            info = chroma_manager.get_collection_info(collection)
            print(f"  - {collection}: {info['count']} documentos")
        
        return True
    except Exception as e:
        print(f"[ERROR] ChromaDB: {e}")
        return False


def test_retrieval():
    """Prueba el sistema de recuperación."""
    print("\n" + "="*60)
    print("PRUEBA DE RETRIEVAL")
    print("="*60)
    
    try:
        from vectorstore import ChromaManager
        from embeddings import BGEM3Embedder
        from retriever import AdvancedRetriever
        
        print("[INFO] Inicializando componentes...")
        chroma_manager = ChromaManager()
        embedder = BGEM3Embedder()
        retriever = AdvancedRetriever(chroma_manager, embedder)
        
        print("[INFO] Probando recuperación...")
        query = "medicina forense"
        results = retriever.retrieve(query, k=3)
        
        print(f"[OK] Recuperación exitosa: {len(results)} documentos")
        if results:
            print(f"[INFO] Primer documento: {results[0].get('metadata', {}).get('source', 'N/A')[:50]}...")
        
        return True
    except Exception as e:
        print(f"[ERROR] Retrieval: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecuta todas las pruebas."""
    print("\n" + "="*60)
    print("ANALISIS Y PRUEBA DEL SISTEMA RAG CRIMINOLOGICO")
    print("="*60 + "\n")
    
    # Prueba imports
    import_errors = test_imports()
    
    if import_errors:
        print(f"\n[ERROR] Se encontraron {len(import_errors)} errores en imports")
        return
    
    # Prueba ChromaDB
    chroma_ok = test_chromadb()
    
    # Prueba retrieval
    if chroma_ok:
        retrieval_ok = test_retrieval()
    else:
        retrieval_ok = False
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    print(f"Imports: {'OK' if not import_errors else 'ERROR'}")
    print(f"ChromaDB: {'OK' if chroma_ok else 'ERROR'}")
    print(f"Retrieval: {'OK' if retrieval_ok else 'ERROR'}")
    
    if not import_errors and chroma_ok and retrieval_ok:
        print("\n[OK] Sistema listo para usar!")
        print("\nNOTA: Para usar el sistema completo, configura GROQ_API_KEY en .env")
    else:
        print("\n[ERROR] Hay problemas que deben resolverse antes de usar el sistema")


if __name__ == "__main__":
    main()
