"""
Script para organizar PDFs desde una ruta fuente a los subdirectorios de data/.
"""
import shutil
import sys
from pathlib import Path
from typing import Dict, List

# Agregar raíz del proyecto al path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Definir rutas directamente sin importar settings completo
DATA_DIR = BASE_DIR / "data"


def classify_pdf(filename: str) -> str:
    """
    Clasifica un PDF basándose en palabras clave en su nombre.
    
    Args:
        filename: Nombre del archivo PDF
        
    Returns:
        Nombre del subdirectorio destino
    """
    filename_lower = filename.lower()
    
    # Palabras clave para cada categoría
    fbi_keywords = ['fbi', 'doj', 'unodc', 'federal', 'bureau', 'investigation']
    forensic_keywords = ['forensic', 'forense', 'balística', 'ballistic', 'escena', 'scene', 
                         'manual', 'guía', 'guide', 'procedimiento', 'procedure']
    academic_keywords = ['paper', 'artículo', 'article', 'study', 'estudio', 'theory', 'teoría',
                        'academic', 'académico', 'research', 'investigación']
    case_keywords = ['case', 'caso', 'study', 'estudio', 'analysis', 'análisis', 'report', 'informe']
    legislation_keywords = ['legislation', 'legislación', 'law', 'ley', 'code', 'código', 
                           'penal', 'criminal', 'sentencia', 'sentence']
    
    # Verificar en orden de prioridad
    if any(kw in filename_lower for kw in fbi_keywords):
        return "fbi_documents"
    elif any(kw in filename_lower for kw in legislation_keywords):
        return "legislation"
    elif any(kw in filename_lower for kw in academic_keywords):
        return "academic_papers"
    elif any(kw in filename_lower for kw in forensic_keywords):
        return "forensic_manual"
    elif any(kw in filename_lower for kw in case_keywords):
        return "case_studies"
    else:
        # Por defecto, usar forensic_cases
        return "forensic_manual"


def organize_pdfs(source_dir: Path, dry_run: bool = False) -> Dict[str, List[str]]:
    """
    Organiza PDFs desde el directorio fuente a los subdirectorios de data/.
    
    Args:
        source_dir: Directorio fuente con PDFs
        dry_run: Si True, solo muestra qué haría sin copiar
        
    Returns:
        Diccionario con PDFs organizados por categoría
    """
    if not source_dir.exists():
        print(f"Error: El directorio {source_dir} no existe")
        return {}
    
    # Buscar todos los PDFs
    pdf_files = list(source_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No se encontraron PDFs en {source_dir}")
        return {}
    
    print(f"Encontrados {len(pdf_files)} PDFs en {source_dir}")
    print(f"Modo: {'DRY RUN (solo mostraría)' if dry_run else 'COPIAR archivos'}\n")
    
    organized = {
        "fbi_documents": [],
        "forensic_manual": [],
        "academic_papers": [],
        "case_studies": [],
        "legislation": []
    }
    
    for pdf_file in pdf_files:
        category = classify_pdf(pdf_file.name)
        dest_dir = DATA_DIR / category
        
        # Asegurar que el directorio destino existe
        dest_dir.mkdir(exist_ok=True, parents=True)
        
        dest_path = dest_dir / pdf_file.name
        
        if dest_path.exists():
            print(f"[!] Ya existe: {pdf_file.name} -> {category}/ (saltado)")
            continue
        
        organized[category].append(pdf_file.name)
        
        if dry_run:
            print(f"[PDF] {pdf_file.name} -> {category}/")
        else:
            try:
                shutil.copy2(pdf_file, dest_path)
                print(f"[OK] Copiado: {pdf_file.name} -> {category}/")
            except Exception as e:
                print(f"[ERROR] Error copiando {pdf_file.name}: {e}")
    
    print("\n" + "="*60)
    print("Resumen:")
    print("="*60)
    for category, files in organized.items():
        if files:
            print(f"{category}: {len(files)} archivos")
    
    return organized


def main():
    """Función principal."""
    source_path = Path("C:\\Users\\martin\\Desktop\\PDF_ForenceyCriminal")
    
    print("="*60)
    print("ORGANIZADOR DE PDFs PARA RAG CRIMINOLOGICO")
    print("="*60)
    print(f"\nOrigen: {source_path}")
    print(f"Destino: {DATA_DIR}\n")
    
    # Primero hacer dry run
    print("[DRY RUN] Ejecutando previsualizacion...\n")
    organize_pdfs(source_path, dry_run=True)
    
    # Copiar automáticamente
    print("\n" + "="*60)
    print("[COPIANDO] Copiando archivos...\n")
    organize_pdfs(source_path, dry_run=False)
    print("\n[OK] ¡Organizacion completada!")


if __name__ == "__main__":
    main()
