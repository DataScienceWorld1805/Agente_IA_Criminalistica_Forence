"""
Prompts especializados para el sistema RAG criminológico.
"""
from typing import List, Dict, Any


def get_system_prompt() -> str:
    """
    Retorna el prompt del sistema para el analista criminológico.
    
    Returns:
        Prompt del sistema
    """
    return """Eres un analista criminológico senior con experiencia en:
- Criminología general y teorías criminológicas
- Medicina forense y análisis de escenas de crimen
- Balística forense
- Psicología criminal
- Modus Operandi (MO) y Signature
- Perfilación criminal (criminal profiling)
- Técnicas de investigación criminal

REGLAS CRÍTICAS:
1. Respondes ÚNICAMENTE con base en los documentos proporcionados en el contexto.
2. NUNCA inventes datos, estadísticas, casos o información que no esté en el contexto.
3. SIEMPRE cita las fuentes de manera explícita cuando uses información específica.
4. Diferencia claramente entre:
   - Hechos documentados
   - Análisis e inferencias
   - Teorías y modelos
5. Si no tienes información suficiente en el contexto, indica claramente esta limitación.
6. Usa lenguaje técnico apropiado pero accesible.
7. Estructura tus respuestas de manera clara y organizada.

DISCLAIMER LEGAL Y ÉTICO:
- Este sistema es una herramienta de investigación y análisis académico.
- NO debe usarse para perfilado de personas reales contemporáneas.
- NO debe usarse para hacer inferencias acusatorias sobre individuos específicos.
- La información proporcionada es para fines educativos y de investigación únicamente.
- Siempre verifica la información con fuentes oficiales antes de tomar decisiones importantes.

FORMATO DE RESPUESTA:
- Proporciona respuestas estructuradas y bien organizadas.
- Incluye citas explícitas a las fuentes cuando uses información específica.
- Indica el nivel de certeza cuando sea apropiado (Alto/Medio/Bajo).
- Si mencionas casos específicos, incluye información contextual relevante."""


def get_user_prompt_template() -> str:
    """
    Retorna el template del prompt del usuario.
    
    Returns:
        Template del prompt
    """
    return """Contexto proporcionado (documentos relevantes):

{context}

---

Pregunta del usuario: {query}

Por favor, proporciona una respuesta completa y bien fundamentada basándote ÚNICAMENTE en el contexto proporcionado. Si el contexto no contiene información suficiente para responder completamente, indica esta limitación claramente."""


def format_prompt_with_context(query: str, context: str) -> str:
    """
    Formatea el prompt completo con contexto.
    
    Args:
        query: Consulta del usuario
        context: Contexto de documentos recuperados
        
    Returns:
        Prompt formateado
    """
    if not context:
        context = "No se encontraron documentos relevantes en la base de conocimiento."
    
    template = get_user_prompt_template()
    return template.format(query=query, context=context)


def get_specialized_prompt(query_type: str, query: str, context: str) -> str:
    """
    Genera prompts especializados según el tipo de consulta.
    
    Args:
        query_type: Tipo de consulta (theory, case_study, technique, etc.)
        query: Consulta del usuario
        context: Contexto de documentos
        
    Returns:
        Prompt especializado
    """
    base_prompt = format_prompt_with_context(query, context)
    
    specializations = {
        "theory": "\n\nENFOQUE: Esta consulta requiere un análisis teórico. Enfócate en modelos, teorías y marcos conceptuales.",
        "case_study": "\n\nENFOQUE: Esta consulta requiere análisis de casos específicos. Proporciona detalles contextuales y evidencia documentada.",
        "technique": "\n\nENFOQUE: Esta consulta requiere información sobre técnicas y metodologías. Proporciona pasos, procedimientos y mejores prácticas.",
        "forensic": "\n\nENFOQUE: Esta consulta requiere análisis forense. Enfócate en evidencia, metodologías forenses y procedimientos científicos.",
    }
    
    specialization = specializations.get(query_type, "")
    
    return base_prompt + specialization


def classify_query_type(query: str) -> str:
    """
    Clasifica el tipo de consulta para usar prompts especializados.
    
    Args:
        query: Consulta del usuario
        
    Returns:
        Tipo de consulta
    """
    query_lower = query.lower()
    
    theory_keywords = ["teoría", "theory", "modelo", "model", "marco conceptual", "framework"]
    case_keywords = ["caso", "case", "ejemplo", "example", "estudio de caso"]
    technique_keywords = ["técnica", "technique", "método", "method", "procedimiento", "proceso"]
    forensic_keywords = ["forense", "forensic", "evidencia", "evidence", "balística", "ballistic"]
    
    if any(kw in query_lower for kw in theory_keywords):
        return "theory"
    elif any(kw in query_lower for kw in case_keywords):
        return "case_study"
    elif any(kw in query_lower for kw in technique_keywords):
        return "technique"
    elif any(kw in query_lower for kw in forensic_keywords):
        return "forensic"
    else:
        return "general"
