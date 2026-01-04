"""
Script para crear el archivo .env con todas las variables necesarias.
"""
from pathlib import Path

env_content = """# ============================================
# CONFIGURACIÓN DEL SISTEMA RAG CRIMINOLÓGICO
# ============================================

# ============================================
# GROQ API Configuration
# ============================================
# Obtén tu API key en: https://console.groq.com/
# Reemplaza 'your_groq_api_key_here' con tu API key real
GROQ_API_KEY=your_groq_api_key_here

# Modelo de Groq a usar
# Opciones disponibles:
# - llama-3.3-70b-versatile (mejor calidad, límite 100k tokens/día)
# - llama-3.1-70b-versatile (alta calidad, límite 100k tokens/día)
# - llama-3.1-8b-instant (rápido, límite más alto)
# - mixtral-8x7b-32768 (buena calidad, límite más alto)
GROQ_MODEL=llama-3.3-70b-versatile

# ============================================
# ChromaDB Configuration
# ============================================
# Ruta donde se almacena la base de datos vectorial
CHROMA_DB_PATH=./chroma_db
CHROMA_PERSIST_DIRECTORY=./chroma_db

# ============================================
# Embeddings Configuration
# ============================================
# Modelo de embeddings multilingües (BGE-M3)
EMBEDDING_MODEL=BAAI/bge-m3
# Dispositivo: 'cpu' o 'cuda' (si tienes GPU NVIDIA)
EMBEDDING_DEVICE=cpu

# ============================================
# Chunking Configuration
# ============================================
# Tamaño de chunk en tokens (500-800 recomendado)
CHUNK_SIZE=600
# Overlap entre chunks en tokens (10-20% recomendado)
CHUNK_OVERLAP=100
# Tamaño mínimo de chunk en tokens
MIN_CHUNK_SIZE=200

# ============================================
# Retrieval Configuration
# ============================================
# Número default de documentos a recuperar
DEFAULT_K=5
# Número máximo de documentos a recuperar
MAX_K=10
# Factor de diversidad para MMR (0.0-1.0)
# Valores más altos = más diversidad, menos relevancia
MMR_DIVERSITY=0.5

# ============================================
# Reranking Configuration
# ============================================
# Activar reranking (true/false)
# El reranking mejora la relevancia pero es más lento
USE_RERANKER=false
# Modelo de reranking cross-encoder
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2

# ============================================
# Logging Configuration
# ============================================
# Directorio para logs forenses
LOG_DIR=./logs
# Nivel de logging: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO
"""

def main():
    """Crea el archivo .env."""
    base_dir = Path(__file__).parent.parent
    env_file = base_dir / ".env"
    
    if env_file.exists():
        print(f"[!] El archivo .env ya existe en {env_file}")
        response = input("¿Deseas sobrescribirlo? (s/n): ").strip().lower()
        if response not in ['s', 'si', 'sí', 'y', 'yes']:
            print("[CANCELADO] Operacion cancelada")
            return
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"[OK] Archivo .env creado exitosamente en: {env_file}")
        print("\n[IMPORTANTE] Edita el archivo .env y configura tu GROQ_API_KEY")
        print("   Puedes obtener tu API key en: https://console.groq.com/")
        
    except Exception as e:
        print(f"[ERROR] Error creando archivo .env: {e}")

if __name__ == "__main__":
    main()
