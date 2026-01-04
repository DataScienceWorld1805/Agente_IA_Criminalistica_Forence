"""
Configuración centralizada del sistema RAG criminológico.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CHROMA_DB_PATH = BASE_DIR / os.getenv("CHROMA_DB_PATH", "./chroma_db")

# Crear directorios si no existen
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
CHROMA_DB_PATH.mkdir(exist_ok=True, parents=True)

# Subdirectorios de datos
FBI_DOCUMENTS_DIR = DATA_DIR / "fbi_documents"
FORENSIC_MANUAL_DIR = DATA_DIR / "forensic_manual"
ACADEMIC_PAPERS_DIR = DATA_DIR / "academic_papers"
CASE_STUDIES_DIR = DATA_DIR / "case_studies"
LEGISLATION_DIR = DATA_DIR / "legislation"

# Crear subdirectorios
for dir_path in [FBI_DOCUMENTS_DIR, FORENSIC_MANUAL_DIR, ACADEMIC_PAPERS_DIR, 
                 CASE_STUDIES_DIR, LEGISLATION_DIR]:
    dir_path.mkdir(exist_ok=True, parents=True)

# Groq Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Modelo de Groq a usar (opciones: llama-3.3-70b-versatile, llama-3.1-8b-instant, llama-3.1-70b-versatile, mixtral-8x7b-32768)
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
# No lanzar error aquí, se validará cuando se use el cliente Groq

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY = str(CHROMA_DB_PATH)
CHROMA_COLLECTIONS = {
    "criminology_theory": "Teorías criminológicas generales",
    "forensic_cases": "Casos forenses y medicina forense",
    "serial_killers": "Estudios de asesinos seriales",
    "legislation": "Legislación penal comparada",
    "investigation_techniques": "Técnicas de investigación criminal"
}

# Embeddings Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")
EMBEDDING_DIMENSION = 1024  # BGE-M3 tiene 1024 dimensiones

# Chunking Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "600"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
MIN_CHUNK_SIZE = int(os.getenv("MIN_CHUNK_SIZE", "200"))
CHUNK_OVERLAP_PERCENT = CHUNK_OVERLAP / CHUNK_SIZE if CHUNK_SIZE > 0 else 0.1

# Retrieval Configuration
DEFAULT_K = int(os.getenv("DEFAULT_K", "2"))  # Reducido a 2 para máximo rendimiento
MAX_K = int(os.getenv("MAX_K", "10"))
MMR_DIVERSITY = float(os.getenv("MMR_DIVERSITY", "0.5"))

# Reranking Configuration
USE_RERANKER = os.getenv("USE_RERANKER", "false").lower() == "true"
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# Logging Configuration
LOG_DIR = LOGS_DIR
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Metadata Fields para documentos criminológicos
METADATA_FIELDS = [
    "crime_type",
    "offender_type",
    "victimology",
    "modus_operandi",
    "signature_behavior",
    "geography",
    "time_period",
    "source_reliability",  # alta / media / baja
    "document_authority",  # FBI, académico, judicial
    "document_type",
    "year",
    "country",
    "case",
    "section",
    "confidence_level"
]

# Tipos de chunk
CHUNK_TYPES = ["Teoría", "Hechos", "Análisis", "Conclusiones"]

# Niveles de confiabilidad de fuentes
SOURCE_RELIABILITY_LEVELS = ["alta", "media", "baja"]

# Autoridades documentales
DOCUMENT_AUTHORITIES = ["FBI", "DOJ", "UNODC", "académico", "judicial", "policial", "otro"]
