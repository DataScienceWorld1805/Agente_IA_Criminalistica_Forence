"""
Script para probar una consulta al sistema RAG.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_query():
    """Prueba una consulta al sistema."""
    print("="*60)
    print("PRUEBA DE CONSULTA AL SISTEMA RAG")
    print("="*60 + "\n")
    
    try:
        from vectorstore import ChromaManager
        from embeddings import BGEM3Embedder
        from retriever import AdvancedRetriever
        
        print("[1/3] Inicializando componentes...")
        chroma_manager = ChromaManager()
        embedder = BGEM3Embedder()
        retriever = AdvancedRetriever(chroma_manager, embedder)
        
        print("[2/3] Realizando consulta de prueba...")
        query = "¿Qué es la medicina forense?"
        print(f"Consulta: '{query}'\n")
        
        results = retriever.retrieve(query, k=5)
        
        print(f"[3/3] Resultados encontrados: {len(results)}\n")
        
        if results:
            print("Documentos recuperados:")
            print("-" * 60)
            for i, doc in enumerate(results[:3], 1):
                metadata = doc.get('metadata', {})
                source = metadata.get('source', 'Desconocido')
                text_preview = doc.get('text', '')[:150] + "..."
                
                print(f"\n[{i}] Fuente: {Path(source).name}")
                print(f"    Distancia: {doc.get('distance', 'N/A'):.4f}")
                print(f"    Preview: {text_preview}")
        
        print("\n" + "="*60)
        print("[OK] Sistema de recuperación funcionando correctamente")
        print("="*60)
        
        # Verificar si hay API key para probar el LLM
        from dotenv import load_dotenv
        import os
        load_dotenv()
        api_key = os.getenv('GROQ_API_KEY', '')
        
        if api_key and api_key != 'your_groq_api_key_here':
            print("\n[INFO] GROQ_API_KEY configurada - El sistema completo está listo")
            print("       Ejecuta: python main.py")
        else:
            print("\n[INFO] GROQ_API_KEY no configurada")
            print("       Configura tu API key en .env para usar el LLM")
            print("       Obtén tu key en: https://console.groq.com/")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_query()
