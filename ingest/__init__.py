"""
Módulo de ingesta de documentos PDF para el sistema RAG criminológico.
"""

from .pdf_loader import PDFLoader
from .preprocessor import DocumentPreprocessor
from .metadata_extractor import MetadataExtractor

__all__ = ["PDFLoader", "DocumentPreprocessor", "MetadataExtractor"]
