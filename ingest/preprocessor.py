"""
Preprocesamiento y normalización de documentos para el sistema RAG criminológico.
"""
import re
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentPreprocessor:
    """Preprocesa y normaliza documentos extraídos de PDFs."""
    
    def __init__(self):
        """Inicializa el preprocesador."""
        # Patrones para headers/footers comunes
        self.header_footer_patterns = [
            r'^\d+\s*$',  # Solo números (páginas)
            r'^Página\s+\d+',  # "Página X"
            r'^Page\s+\d+',  # "Page X"
            r'^\d+\s+de\s+\d+',  # "X de Y"
            r'^Confidential|^CONFIDENTIAL',
            r'^©\s*\d{4}',
            r'^Documento\s+confidencial',
        ]
        
        # Patrones para normalización de fechas
        self.date_patterns = [
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', r'\3-\d{2}-\d{2}'),  # DD/MM/YYYY
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', r'\1-\2-\3'),  # YYYY-MM-DD
        ]
    
    def preprocess(self, document: Dict[str, any]) -> Dict[str, any]:
        """
        Preprocesa un documento completo.
        
        Args:
            document: Documento con 'text', 'metadata', 'pages'
            
        Returns:
            Documento preprocesado
        """
        logger.info(f"Preprocesando documento: {document['metadata'].get('filename', 'unknown')}")
        
        # Preprocesar texto completo
        cleaned_text = self.clean_text(document['text'])
        
        # Preprocesar páginas individuales
        cleaned_pages = []
        for page in document.get('pages', []):
            cleaned_page = page.copy()
            if 'text' in cleaned_page:
                cleaned_page['text'] = self.clean_text(cleaned_page['text'])
            cleaned_pages.append(cleaned_page)
        
        # Normalizar metadata
        normalized_metadata = self.normalize_metadata(document['metadata'])
        
        return {
            "text": cleaned_text,
            "metadata": normalized_metadata,
            "pages": cleaned_pages,
            "original_length": len(document['text']),
            "cleaned_length": len(cleaned_text)
        }
    
    def clean_text(self, text: str) -> str:
        """
        Limpia y normaliza el texto.
        
        Args:
            text: Texto a limpiar
            
        Returns:
            Texto limpio
        """
        if not text:
            return ""
        
        # Eliminar headers/footers
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Verificar si es header/footer
            is_header_footer = False
            for pattern in self.header_footer_patterns:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    is_header_footer = True
                    break
            
            if not is_header_footer:
                cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        # Normalizar espacios en blanco
        text = re.sub(r'\s+', ' ', text)  # Múltiples espacios a uno
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Múltiples saltos de línea
        
        # Eliminar caracteres de control (excepto \n, \t)
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Normalizar comillas y guiones
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        text = text.replace('–', '-').replace('—', '-')
        
        # Limpiar ruido legal/administrativo común
        text = self._remove_legal_noise(text)
        
        return text.strip()
    
    def _remove_legal_noise(self, text: str) -> str:
        """Elimina ruido legal o administrativo común."""
        # Patrones de ruido común (ajustar según necesidad)
        noise_patterns = [
            r'^Este documento es confidencial.*?$',
            r'^Documento clasificado.*?$',
            r'^Para uso interno únicamente.*?$',
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            is_noise = False
            for pattern in noise_patterns:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    is_noise = True
                    break
            
            if not is_noise:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def normalize_metadata(self, metadata: Dict[str, any]) -> Dict[str, any]:
        """
        Normaliza la metadata del documento.
        
        Args:
            metadata: Metadata original
            
        Returns:
            Metadata normalizada
        """
        normalized = metadata.copy()
        
        # Normalizar fechas si existen
        if 'date' in normalized:
            normalized['date'] = self._normalize_date(normalized['date'])
        
        # Agregar timestamp de procesamiento
        normalized['processed_at'] = datetime.now().isoformat()
        
        # Normalizar nombres de archivo
        if 'filename' in normalized:
            normalized['filename'] = normalized['filename'].strip()
        
        return normalized
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normaliza una fecha a formato estándar."""
        if not date_str:
            return None
        
        # Intentar parsear diferentes formatos
        try:
            # Formato común: DD/MM/YYYY
            match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
            if match:
                day, month, year = match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # Formato: YYYY-MM-DD
            match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
            if match:
                return date_str
            
            # Intentar parsear con datetime
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        except Exception as e:
            logger.warning(f"Error normalizando fecha '{date_str}': {e}")
        
        return date_str
    
    def extract_sections(self, text: str) -> List[Dict[str, str]]:
        """
        Extrae secciones del documento basándose en títulos.
        
        Args:
            text: Texto del documento
            
        Returns:
            Lista de secciones con 'title' y 'content'
        """
        sections = []
        
        # Patrón para detectar títulos (líneas en mayúsculas, numeradas, etc.)
        title_pattern = r'^(?:[A-Z][A-Z\s]{3,}|(?:\d+\.?\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)$'
        
        lines = text.split('\n')
        current_section = {"title": "Introducción", "content": []}
        
        for line in lines:
            line_stripped = line.strip()
            
            # Verificar si es un título
            if line_stripped and (
                re.match(title_pattern, line_stripped) or
                line_stripped.isupper() and len(line_stripped) > 5
            ):
                # Guardar sección anterior
                if current_section["content"]:
                    sections.append({
                        "title": current_section["title"],
                        "content": "\n".join(current_section["content"])
                    })
                
                # Nueva sección
                current_section = {
                    "title": line_stripped,
                    "content": []
                }
            else:
                current_section["content"].append(line)
        
        # Agregar última sección
        if current_section["content"]:
            sections.append({
                "title": current_section["title"],
                "content": "\n".join(current_section["content"])
            })
        
        return sections
