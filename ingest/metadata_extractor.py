"""
Extractor de metadata criminológica de documentos.
"""
import re
import logging
from typing import Dict, List, Optional
from pathlib import Path
from config import settings

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extrae metadata criminológica de documentos."""
    
    def __init__(self):
        """Inicializa el extractor de metadata."""
        # Patrones para detectar tipos de crimen
        self.crime_patterns = {
            "homicidio": r'\b(homicidio|asesinato|murder|homicide)\b',
            "homicidio_serial": r'\b(asesino\s+serial|serial\s+killer|homicidio\s+serial)\b',
            "violencia_domestica": r'\b(violencia\s+doméstica|domestic\s+violence)\b',
            "crimen_organizado": r'\b(crimen\s+organizado|organized\s+crime|mafia)\b',
            "terrorismo": r'\b(terrorismo|terrorism|terrorista)\b',
            "trata_personas": r'\b(trata\s+de\s+personas|human\s+trafficking)\b',
        }
        
        # Patrones para autoridades documentales
        self.authority_patterns = {
            "FBI": r'\b(FBI|Federal\s+Bureau\s+of\s+Investigation)\b',
            "DOJ": r'\b(DOJ|Department\s+of\s+Justice|Departamento\s+de\s+Justicia)\b',
            "UNODC": r'\b(UNODC|United\s+Nations\s+Office\s+on\s+Drugs\s+and\s+Crime)\b',
            "académico": r'\b(universidad|university|académico|academic|paper|artículo)\b',
            "judicial": r'\b(sentencia|sentence|tribunal|court|judicial)\b',
            "policial": r'\b(policía|police|investigación\s+policial)\b',
        }
        
        # Patrones para geografía
        self.geography_patterns = {
            "USA": r'\b(USA|United\s+States|Estados\s+Unidos|EE\.UU\.)\b',
            "México": r'\b(México|Mexico)\b',
            "Colombia": r'\b(Colombia)\b',
            "España": r'\b(España|Spain)\b',
        }
        
        # Patrones para años
        self.year_pattern = r'\b(19|20)\d{2}\b'
    
    def extract(self, document: Dict[str, any]) -> Dict[str, any]:
        """
        Extrae metadata criminológica de un documento.
        
        Args:
            document: Documento con 'text' y 'metadata'
            
        Returns:
            Metadata enriquecida
        """
        text = document.get('text', '').lower()
        metadata = document.get('metadata', {}).copy()
        
        logger.info(f"Extrayendo metadata de: {metadata.get('filename', 'unknown')}")
        
        # Extraer tipo de crimen
        crime_type = self._extract_crime_type(text)
        if crime_type:
            metadata['crime_type'] = crime_type
        
        # Extraer autoridad documental
        document_authority = self._extract_document_authority(text, metadata)
        if document_authority:
            metadata['document_authority'] = document_authority
        
        # Extraer geografía
        geography = self._extract_geography(text)
        if geography:
            metadata['geography'] = geography
        
        # Extraer año
        year = self._extract_year(text, metadata)
        if year:
            metadata['year'] = year
        
        # Inferir tipo de documento primero (necesario para determinar confiabilidad)
        document_type = self._infer_document_type(text, metadata)
        if document_type:
            metadata['document_type'] = document_type
        
        # Determinar confiabilidad de fuente (usando tipo de documento también)
        source_reliability = self._determine_reliability(document_authority, document_type)
        if source_reliability:
            metadata['source_reliability'] = source_reliability
        
        # Extraer casos mencionados
        cases = self._extract_cases(text)
        if cases:
            metadata['case'] = cases[0]  # Primer caso encontrado
        
        return metadata
    
    def _extract_crime_type(self, text: str) -> Optional[str]:
        """Extrae el tipo de crimen del texto."""
        text_lower = text.lower()
        
        for crime_type, pattern in self.crime_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return crime_type
        
        return None
    
    def _extract_document_authority(self, text: str, metadata: Dict) -> Optional[str]:
        """Extrae la autoridad documental."""
        text_lower = text.lower()
        filename_lower = metadata.get('filename', '').lower()
        combined = f"{text_lower} {filename_lower}"
        
        for authority, pattern in self.authority_patterns.items():
            if re.search(pattern, combined, re.IGNORECASE):
                return authority
        
        return "otro"
    
    def _extract_geography(self, text: str) -> Optional[str]:
        """Extrae información geográfica."""
        text_lower = text.lower()
        
        for geo, pattern in self.geography_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                return geo
        
        return None
    
    def _extract_year(self, text: str, metadata: Dict) -> Optional[int]:
        """Extrae el año del documento."""
        # Buscar en metadata primero
        if 'year' in metadata:
            try:
                return int(metadata['year'])
            except (ValueError, TypeError):
                pass
        
        # Buscar en el texto
        years = re.findall(self.year_pattern, text)
        if years:
            # Tomar el año más reciente entre 1900-2099
            valid_years = [int(y) for y in years if 1900 <= int(y) <= 2099]
            if valid_years:
                return max(valid_years)
        
        return None
    
    def _determine_reliability(self, authority: Optional[str], document_type: Optional[str] = None) -> str:
        """
        Determina el nivel de confiabilidad basándose en la autoridad y tipo de documento.
        
        Args:
            authority: Autoridad del documento
            document_type: Tipo de documento (Manual, Paper académico, etc.)
        """
        # Autoridades de alta confiabilidad
        high_reliability_authorities = ["FBI", "DOJ", "UNODC", "judicial"]
        
        # Tipos de documentos de alta confiabilidad
        high_reliability_types = ["Manual", "Paper académico", "Investigación oficial", 
                                  "Sentencia judicial", "Estudio de caso"]
        
        # Si es una autoridad de alta confiabilidad
        if authority and authority in high_reliability_authorities:
            return "alta"
        
        # Si es un tipo de documento de alta confiabilidad
        if document_type and document_type in high_reliability_types:
            return "alta"
        
        # Autoridades de confiabilidad media
        medium_reliability_authorities = ["académico", "policial"]
        if authority and authority in medium_reliability_authorities:
            return "media"
        
        # Por defecto, para documentos técnicos/forenses: alta confiabilidad
        # Esto es porque son documentos especializados y técnicos de criminología/forense
        # Los documentos en este sistema son principalmente manuales y papers especializados
        if not authority or authority == "otro":
            # Si no hay autoridad específica, asumir alta confiabilidad
            # porque son documentos técnicos especializados en criminología/forense
            return "alta"
        
        # Si llegamos aquí y no es alta ni media, darle alta por defecto
        # (mejor que baja para documentos técnicos)
        return "alta"
    
    def _infer_document_type(self, text: str, metadata: Dict) -> Optional[str]:
        """Infiere el tipo de documento."""
        text_lower = text.lower()
        filename_lower = metadata.get('filename', '').lower()
        combined = f"{text_lower} {filename_lower}"
        
        # Patrones más específicos para detectar tipos de documentos
        if re.search(r'\b(investigación|investigation|report|informe)\b', combined, re.IGNORECASE):
            return "Investigación oficial"
        elif re.search(r'\b(manual|guide|guía|handbook)\b', combined, re.IGNORECASE):
            return "Manual"
        elif re.search(r'\b(paper|artículo|article|study|estudio|research)\b', combined, re.IGNORECASE):
            return "Paper académico"
        elif re.search(r'\b(sentencia|sentence|case|judicial)\b', combined, re.IGNORECASE):
            return "Sentencia judicial"
        elif re.search(r'\b(caso|case\s+study|estudio\s+de\s+caso)\b', combined, re.IGNORECASE):
            return "Estudio de caso"
        # Detectar documentos forenses por palabras clave
        elif re.search(r'\b(forense|forensic|medicina\s+forense|criminalística|criminalistica|balística|ballistic)\b', combined, re.IGNORECASE):
            return "Manual"  # Tratar documentos forenses como manuales (alta confiabilidad)
        
        return None
    
    def _extract_cases(self, text: str) -> List[str]:
        """Extrae nombres de casos mencionados."""
        # Patrones comunes para casos (nombres en mayúsculas, códigos, etc.)
        case_patterns = [
            r'\b([A-Z]{2,10}\s+[A-Z]{2,10})\b',  # Iniciales como "BTK", "FBI"
            r'Caso\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "Caso XYZ"
            r'Case\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "Case XYZ"
        ]
        
        cases = []
        for pattern in case_patterns:
            matches = re.findall(pattern, text)
            cases.extend(matches)
        
        # Filtrar casos comunes que no son casos reales
        exclude = ['FBI', 'DOJ', 'UNODC', 'USA', 'EE UU']
        cases = [c for c in cases if c not in exclude and len(c) > 2]
        
        return list(set(cases))[:5]  # Máximo 5 casos únicos
    
    def enrich_chunk_metadata(self, chunk_text: str, document_metadata: Dict) -> Dict[str, any]:
        """
        Enriquece la metadata de un chunk individual.
        
        Args:
            chunk_text: Texto del chunk
            document_metadata: Metadata del documento padre
            
        Returns:
            Metadata enriquecida para el chunk
        """
        chunk_metadata = document_metadata.copy()
        
        # Determinar tipo de chunk
        chunk_type = self._classify_chunk_type(chunk_text)
        if chunk_type:
            chunk_metadata['chunk_type'] = chunk_type
        
        # Extraer sección si es posible
        section = self._extract_section(chunk_text)
        if section:
            chunk_metadata['section'] = section
        
        return chunk_metadata
    
    def _classify_chunk_type(self, text: str) -> Optional[str]:
        """Clasifica el tipo de chunk (Teoría, Hechos, Análisis, Conclusiones)."""
        text_lower = text.lower()
        
        # Patrones para cada tipo
        if re.search(r'\b(teoría|theory|modelo|model|framework)\b', text_lower):
            return "Teoría"
        elif re.search(r'\b(hecho|fact|evidencia|evidence|ocurrió|happened)\b', text_lower):
            return "Hechos"
        elif re.search(r'\b(análisis|analysis|analizar|examinar|evaluar)\b', text_lower):
            return "Análisis"
        elif re.search(r'\b(conclusión|conclusion|resumen|summary|en\s+resumen)\b', text_lower):
            return "Conclusiones"
        
        return None
    
    def _extract_section(self, text: str) -> Optional[str]:
        """Extrae el nombre de la sección del chunk."""
        # Buscar títulos al inicio del chunk
        lines = text.split('\n')[:3]  # Primeras 3 líneas
        
        for line in lines:
            line_stripped = line.strip()
            # Si la línea es corta y parece un título
            if len(line_stripped) < 100 and (
                line_stripped.isupper() or
                re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', line_stripped)
            ):
                return line_stripped
        
        return None
