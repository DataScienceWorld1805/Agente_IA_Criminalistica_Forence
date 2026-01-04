"""
Validadores para metadata y respuestas del sistema RAG.
"""
import logging
from typing import Dict, Any, List, Optional
from config import settings

logger = logging.getLogger(__name__)


def validate_metadata(metadata: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Valida que la metadata tenga los campos requeridos.
    
    Args:
        metadata: Metadata a validar
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    required_fields = ["source"]
    
    for field in required_fields:
        if field not in metadata:
            return False, f"Campo requerido faltante: {field}"
    
    # Validar valores de campos específicos
    if "source_reliability" in metadata:
        if metadata["source_reliability"] not in settings.SOURCE_RELIABILITY_LEVELS:
            return False, f"source_reliability inválido: {metadata['source_reliability']}"
    
    if "document_authority" in metadata:
        if metadata["document_authority"] not in settings.DOCUMENT_AUTHORITIES:
            logger.warning(f"document_authority no estándar: {metadata['document_authority']}")
    
    return True, None


def validate_response(response: str, min_length: int = 10) -> tuple[bool, Optional[str]]:
    """
    Valida que la respuesta tenga calidad mínima.
    
    Args:
        response: Respuesta a validar
        min_length: Longitud mínima
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not response:
        return False, "Respuesta vacía"
    
    if len(response.strip()) < min_length:
        return False, f"Respuesta muy corta (mínimo {min_length} caracteres)"
    
    # Verificar que no sea solo un error
    error_indicators = ["error", "no se pudo", "falló", "failed"]
    response_lower = response.lower()
    
    if any(indicator in response_lower for indicator in error_indicators):
        if len(response) < 50:  # Si es muy corta y contiene error, probablemente es un error real
            return False, "Respuesta parece ser un mensaje de error"
    
    return True, None


def validate_documents(documents: List[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
    """
    Valida que los documentos tengan la estructura correcta.
    
    Args:
        documents: Lista de documentos
        
    Returns:
        Tupla (es_válido, mensaje_error)
    """
    if not documents:
        return False, "Lista de documentos vacía"
    
    required_fields = ["text", "metadata"]
    
    for i, doc in enumerate(documents):
        for field in required_fields:
            if field not in doc:
                return False, f"Documento {i} falta campo: {field}"
        
        # Validar metadata
        is_valid, error = validate_metadata(doc.get("metadata", {}))
        if not is_valid:
            return False, f"Documento {i}: {error}"
    
    return True, None
