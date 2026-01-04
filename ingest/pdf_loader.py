"""
Cargador de documentos PDF para el sistema RAG criminológico.
"""
import logging
from pathlib import Path
from typing import List, Dict, Optional
import pdfplumber
import PyPDF2

logger = logging.getLogger(__name__)


class PDFLoader:
    """Carga y extrae texto de archivos PDF."""
    
    def __init__(self, use_pdfplumber: bool = True):
        """
        Inicializa el cargador de PDFs.
        
        Args:
            use_pdfplumber: Si True, usa pdfplumber (mejor para tablas).
                           Si False, usa PyPDF2 (más rápido).
        """
        self.use_pdfplumber = use_pdfplumber
    
    def load_pdf(self, file_path: Path) -> Dict[str, any]:
        """
        Carga un archivo PDF y extrae su contenido.
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con 'text', 'metadata' y 'pages'
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        logger.info(f"Cargando PDF: {file_path}")
        
        try:
            if self.use_pdfplumber:
                return self._load_with_pdfplumber(file_path)
            else:
                return self._load_with_pypdf2(file_path)
        except Exception as e:
            logger.error(f"Error cargando PDF {file_path}: {e}")
            raise
    
    def _load_with_pdfplumber(self, file_path: Path) -> Dict[str, any]:
        """Carga PDF usando pdfplumber (mejor para documentos complejos)."""
        text_parts = []
        pages = []
        
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                    pages.append({
                        "page_number": page_num,
                        "text": page_text,
                        "bbox": page.bbox if hasattr(page, 'bbox') else None
                    })
        
        full_text = "\n\n".join(text_parts)
        
        return {
            "text": full_text,
            "metadata": {
                "source": str(file_path),
                "filename": file_path.name,
                "total_pages": total_pages,
                "loader": "pdfplumber"
            },
            "pages": pages
        }
    
    def _load_with_pypdf2(self, file_path: Path) -> Dict[str, any]:
        """Carga PDF usando PyPDF2 (más rápido, menos preciso)."""
        text_parts = []
        pages = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                    pages.append({
                        "page_number": page_num,
                        "text": page_text
                    })
        
        full_text = "\n\n".join(text_parts)
        
        return {
            "text": full_text,
            "metadata": {
                "source": str(file_path),
                "filename": file_path.name,
                "total_pages": total_pages,
                "loader": "PyPDF2"
            },
            "pages": pages
        }
    
    def load_directory(self, directory: Path, pattern: str = "*.pdf") -> List[Dict[str, any]]:
        """
        Carga todos los PDFs de un directorio.
        
        Args:
            directory: Directorio con PDFs
            pattern: Patrón de búsqueda (default: "*.pdf")
            
        Returns:
            Lista de documentos cargados
        """
        documents = []
        pdf_files = list(directory.glob(pattern))
        
        logger.info(f"Encontrados {len(pdf_files)} archivos PDF en {directory}")
        
        for pdf_file in pdf_files:
            try:
                doc = self.load_pdf(pdf_file)
                documents.append(doc)
            except Exception as e:
                logger.warning(f"Error cargando {pdf_file}: {e}")
                continue
        
        return documents
