"""
Chunking semántico estratégico para documentos criminológicos.
"""
import logging
import tiktoken
from typing import List, Dict, Optional
from config import settings

logger = logging.getLogger(__name__)


class SemanticChunker:
    """Chunking semántico que respeta límites de significado."""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        min_chunk_size: int = None
    ):
        """
        Inicializa el chunker semántico.
        
        Args:
            chunk_size: Tamaño objetivo del chunk en tokens (default: config)
            chunk_overlap: Overlap entre chunks en tokens (default: config)
            min_chunk_size: Tamaño mínimo del chunk en tokens (default: config)
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.min_chunk_size = min_chunk_size or settings.MIN_CHUNK_SIZE
        
        # Inicializar tokenizer (usando cl100k_base que es compatible con muchos modelos)
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Error cargando tokenizer: {e}. Usando método alternativo.")
            self.tokenizer = None
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict[str, any]]:
        """
        Divide el texto en chunks semánticos.
        
        Args:
            text: Texto a dividir
            metadata: Metadata del documento original
            
        Returns:
            Lista de chunks con metadata
        """
        if not text or not text.strip():
            return []
        
        logger.info(f"Chunking texto de {len(text)} caracteres")
        
        # Dividir en párrafos primero (límites semánticos naturales)
        paragraphs = self._split_into_paragraphs(text)
        
        # Agrupar párrafos en chunks
        chunks = self._create_chunks_from_paragraphs(paragraphs, metadata or {})
        
        logger.info(f"Creados {len(chunks)} chunks")
        
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Divide el texto en párrafos."""
        # Dividir por doble salto de línea (párrafos)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Si no hay párrafos claros, dividir por saltos de línea simples
        if len(paragraphs) == 1:
            paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        return paragraphs
    
    def _create_chunks_from_paragraphs(
        self,
        paragraphs: List[str],
        base_metadata: Dict
    ) -> List[Dict[str, any]]:
        """Crea chunks agrupando párrafos respetando límites semánticos."""
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para_idx, paragraph in enumerate(paragraphs):
            para_tokens = self._count_tokens(paragraph)
            
            # Si el párrafo solo excede el tamaño máximo, dividirlo
            if para_tokens > self.chunk_size:
                # Guardar chunk actual si existe
                if current_chunk:
                    chunk = self._create_chunk_dict(current_chunk, base_metadata, len(chunks))
                    chunks.append(chunk)
                    current_chunk = []
                    current_size = 0
                
                # Dividir párrafo grande
                sub_chunks = self._split_large_paragraph(paragraph)
                for sub_chunk in sub_chunks:
                    chunks.append(self._create_chunk_dict(
                        [sub_chunk], base_metadata, len(chunks)
                    ))
                continue
            
            # Si agregar este párrafo excedería el tamaño, guardar chunk actual
            if current_size + para_tokens > self.chunk_size and current_chunk:
                chunk = self._create_chunk_dict(current_chunk, base_metadata, len(chunks))
                chunks.append(chunk)
                
                # Iniciar nuevo chunk con overlap
                current_chunk, current_size = self._create_overlap_chunk(chunks[-1])
            
            # Agregar párrafo al chunk actual
            current_chunk.append(paragraph)
            current_size += para_tokens
        
        # Agregar último chunk si existe y cumple tamaño mínimo
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            if self._count_tokens(chunk_text) >= self.min_chunk_size:
                chunk = self._create_chunk_dict(current_chunk, base_metadata, len(chunks))
                chunks.append(chunk)
        
        return chunks
    
    def _split_large_paragraph(self, paragraph: str) -> List[str]:
        """Divide un párrafo grande en sub-chunks."""
        # Dividir por oraciones primero
        sentences = self._split_into_sentences(paragraph)
        
        sub_chunks = []
        current_sub = []
        current_size = 0
        
        for sentence in sentences:
            sent_tokens = self._count_tokens(sentence)
            
            if current_size + sent_tokens > self.chunk_size and current_sub:
                sub_chunks.append(' '.join(current_sub))
                current_sub = []
                current_size = 0
            
            current_sub.append(sentence)
            current_size += sent_tokens
        
        if current_sub:
            sub_chunks.append(' '.join(current_sub))
        
        return sub_chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divide texto en oraciones."""
        # Patrón simple para oraciones (puede mejorarse con NLTK/spaCy)
        import re
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _create_overlap_chunk(self, previous_chunk: Dict) -> tuple:
        """Crea un nuevo chunk con overlap del anterior."""
        prev_text = previous_chunk['text']
        prev_paragraphs = self._split_into_paragraphs(prev_text)
        
        # Tomar los últimos párrafos que quepan en el overlap
        overlap_paras = []
        overlap_size = 0
        
        for para in reversed(prev_paragraphs):
            para_tokens = self._count_tokens(para)
            if overlap_size + para_tokens <= self.chunk_overlap:
                overlap_paras.insert(0, para)
                overlap_size += para_tokens
            else:
                break
        
        return overlap_paras, overlap_size
    
    def _create_chunk_dict(
        self,
        paragraphs: List[str],
        base_metadata: Dict,
        chunk_index: int
    ) -> Dict[str, any]:
        """Crea el diccionario de metadata para un chunk."""
        chunk_text = '\n\n'.join(paragraphs)
        
        chunk_metadata = base_metadata.copy()
        chunk_metadata.update({
            'chunk_id': f"{base_metadata.get('source', 'doc')}_chunk_{chunk_index}",
            'chunk_index': chunk_index,
            'chunk_size_tokens': self._count_tokens(chunk_text),
            'chunk_size_chars': len(chunk_text),
        })
        
        return {
            'text': chunk_text,
            'metadata': chunk_metadata
        }
    
    def _count_tokens(self, text: str) -> int:
        """Cuenta tokens en el texto."""
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception:
                pass
        
        # Fallback: aproximación (1 token ≈ 4 caracteres)
        return len(text) // 4
    
    def chunk_document(self, document: Dict[str, any]) -> List[Dict[str, any]]:
        """
        Chunking completo de un documento preprocesado.
        
        Args:
            document: Documento con 'text' y 'metadata'
            
        Returns:
            Lista de chunks con metadata enriquecida
        """
        text = document.get('text', '')
        metadata = document.get('metadata', {})
        
        chunks = self.chunk_text(text, metadata)
        
        # Enriquecer metadata de cada chunk si hay extractor disponible
        # (esto se hará en el pipeline principal)
        
        return chunks
