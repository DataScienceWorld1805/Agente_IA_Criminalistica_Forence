# Sistema RAG Criminológico

Sistema de Retrieval-Augmented Generation (RAG) especializado en criminología, medicina forense, balística y análisis de escenas de crimen. Utiliza LangGraph para orquestación de flujos, Groq LLM para generación de respuestas, embeddings BGE-M3 multilingües para búsqueda semántica y ChromaDB como base de datos vectorial.

## ✨ Características

- **RAG Especializado**: Enfocado en dominios criminológicos y forenses
- **LangGraph**: Flujo de trabajo con grafos de estado para procesamiento complejo
- **Embeddings Multilingües**: BGE-M3 (1024 dimensiones) para soporte multilingüe
- **Chunking Semántico**: División inteligente de documentos (500-800 tokens, overlap 10-20%)
- **Metadata Rica**: Extracción automática de metadata criminológica (tipo de crimen, MO, autoridad, etc.)
- **Retriever Avanzado**: MMR (Max Marginal Relevance) y filtros de metadata
- **Reranking Opcional**: Mejora de relevancia con cross-encoders
- **Logging Forense**: Trazabilidad completa de consultas y respuestas en formato JSON
- **Múltiples Colecciones**: Organización por dominios (teoría, casos, legislación, etc.)
- **Interfaz Web Moderna**: Interfaz Gradio tipo ChatGPT con visualización de fuentes
- **Interfaz CLI**: Modo interactivo para consultas desde terminal

## Arquitectura

```
[ PDFs Fuente ] 
      ↓
[ Ingesta + Preprocesamiento ]
      ↓
[ Chunking Semántico ]
      ↓
[ Embeddings BGE-M3 ]
      ↓
[ ChromaDB Vector Store ]
      ↓
[ LangGraph State ]
      ↓
[ Retriever Avanzado ]
      ↓
[ Reranker (Opcional) ]
      ↓
[ Groq LLM ]
      ↓
[ Respuesta Citada ]
```

## 📋 Requisitos

- **Python 3.9+**
- **Groq API Key** (obtener en https://console.groq.com/)
- **Conexión a Internet** (para descargar modelos de embeddings y acceder a Groq API)
- **Memoria RAM**: Mínimo 4GB (recomendado 8GB+ para embeddings)
- **Espacio en disco**: ~2GB para modelos y base de datos vectorial

## Instalación

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd RAG_ForenceyCriminal
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:

Crea un archivo `.env` en la raíz del proyecto con:
```bash
GROQ_API_KEY=tu_api_key_aqui
GROQ_MODEL=llama-3.3-70b-versatile  # Opcional: otros modelos disponibles
CHROMA_DB_PATH=./chroma_db          # Opcional: ruta para ChromaDB
USE_RERANKER=false                  # Opcional: habilitar reranking
```

O usa el script de ayuda:
```bash
python scripts/create_env.py
```

**Modelos Groq disponibles:**
- `llama-3.3-70b-versatile` (recomendado, mejor calidad)
- `llama-3.1-70b-versatile` (alta calidad)
- `llama-3.1-8b-instant` (más rápido, límite más alto)
- `mixtral-8x7b-32768` (buena calidad, límite más alto)

## 📁 Estructura del Proyecto

```
RAG_ForenceyCriminal/
├── .cursor/                    # Planes de desarrollo y documentación
│   └── plans/                  # Archivos de planificación del proyecto
├── config/                     # Configuración centralizada
│   └── settings.py             # Variables de configuración
├── data/                       # PDFs fuente (organizados por tipo)
│   ├── fbi_documents/          # Documentos del FBI
│   ├── forensic_manual/        # Manuales forenses (actualmente contiene PDFs)
│   ├── academic_papers/        # Papers académicos
│   ├── case_studies/           # Estudios de casos
│   └── legislation/            # Legislación y manuales (actualmente contiene PDFs)
├── ingest/                     # Sistema de ingesta de PDFs
│   ├── pdf_loader.py           # Carga de PDFs
│   ├── preprocessor.py         # Preprocesamiento y limpieza
│   └── metadata_extractor.py   # Extracción de metadata
├── chunking/                   # Chunking semántico
│   └── semantic_chunker.py     # División inteligente de documentos
├── embeddings/                 # Embeddings BGE-M3
│   └── bge_m3_embedder.py      # Generación de embeddings
├── vectorstore/                # Gestión de ChromaDB
│   └── chroma_manager.py       # Administración de base vectorial
├── retriever/                  # Retriever avanzado y reranker
│   ├── advanced_retriever.py   # Búsqueda con MMR y filtros
│   └── reranker.py            # Reranking opcional
├── graph/                      # LangGraph (orquestación)
│   ├── state.py               # Estado del grafo (Pydantic)
│   ├── nodes.py               # Nodos del grafo
│   └── graph.py               # Definición del grafo
├── llm/                       # Cliente Groq
│   └── groq_client.py         # Integración con Groq API
├── prompts/                     # Prompts especializados
│   └── criminological_prompts.py  # Prompts para criminología
├── utils/                       # Utilidades
│   ├── logger.py              # Logging forense
│   └── validators.py          # Validación de datos
├── ui/                          # Interfaces de usuario
│   ├── cli.py                 # Interfaz de línea de comandos
│   └── gradio_app.py          # Interfaz web Gradio
├── scripts/                     # Scripts de utilidad
│   ├── ingest_documents.py    # Script de ingesta
│   ├── test_system.py         # Pruebas del sistema
│   ├── test_query.py         # Prueba de consultas
│   ├── create_env.py         # Crear archivo .env
│   ├── organize_pdfs.py      # Organizar PDFs
│   └── update_reliability.py # Actualizar confiabilidad
├── main.py                      # Punto de entrada principal (CLI)
├── run_gradio.py               # Script para ejecutar interfaz Gradio
├── requirements.txt            # Dependencias Python
├── .env                        # Variables de entorno (crear manualmente)
└── logs/                       # Logs forenses (generados automáticamente)
```

## Uso

### 1. Ingesta de Documentos

Coloca tus PDFs en los directorios correspondientes dentro de `data/`:

- `data/fbi_documents/` - Documentos del FBI
- `data/forensic_manual/` - Manuales forenses (ej: balística, autopsia, escena del crimen)
- `data/academic_papers/` - Papers académicos
- `data/case_studies/` - Estudios de casos
- `data/legislation/` - Legislación y manuales técnicos

**Nota:** El proyecto ya incluye algunos PDFs de ejemplo en `data/forensic_manual/` y `data/legislation/`.

Luego ejecuta el script de ingesta:

```bash
python scripts/ingest_documents.py
```

Este script:
- Carga PDFs de todos los directorios
- Preprocesa y limpia el texto (normalización, OCR si es necesario)
- Extrae metadata criminológica automáticamente
- Divide en chunks semánticos (500-800 tokens, overlap 10-20%)
- Genera embeddings con BGE-M3
- Almacena en ChromaDB con metadata enriquecida
- Organiza documentos en colecciones según su tipo

**Tiempo estimado:** Depende del número y tamaño de PDFs. Un PDF de 50 páginas puede tomar 2-5 minutos.

### 2. Consultas

#### Modo Interactivo (CLI)

```bash
python main.py
```

O directamente:

```bash
python ui/cli.py
```

En modo interactivo puedes usar comandos especiales:
- `/help` - Mostrar ayuda
- `/quit` o `/exit` - Salir
- `/sources on/off` - Activar/desactivar visualización de fuentes

#### Consulta Única desde CLI

```bash
python ui/cli.py "¿Cuál es el modus operandi típico de homicidas seriales organizados?"
```

#### Desde Código Python

```python
from ui.cli import RAGCLI
from graph.state import RAGState

# Inicializar sistema
rag_system = RAGCLI()

# Crear estado inicial
initial_state: RAGState = {
    "query": "¿Qué técnicas forenses se usan en análisis de balística?",
    "documents": [],
    "reranked_docs": None,
    "context": None,
    "response": None,
    "sources": [],
    "metadata": {},
    "error": None
}

# Ejecutar consulta
final_state = rag_system.graph.invoke(initial_state)
print(final_state["response"])
```

### 3. Interfaz Web (Gradio) 🌐

Para usar la interfaz web moderna y profesional tipo ChatGPT:

```bash
python run_gradio.py
```

O con opciones personalizadas:

```bash
# Especificar puerto
python run_gradio.py --port 8080

# Crear enlace público compartido (temporal)
python run_gradio.py --share

# Especificar host y puerto
python run_gradio.py --host 127.0.0.1 --port 7860
```

**Características de la interfaz web:**
- **Chat interactivo**: Interfaz tipo ChatGPT con historial de conversación
- **Respuesta formateada**: Respuestas renderizadas en Markdown con formato profesional
- **Citas integradas**: Referencias automáticas a fuentes consultadas
- **Panel de fuentes**: Visualización detallada de fuentes con:
  - Nombre del documento
  - Autoridad (FBI, DOJ, académico, etc.)
  - Nivel de confiabilidad (alta/media/baja) con badges de color
  - Año de publicación
  - Tipo de crimen
- **Ejemplos predefinidos**: Botones con consultas de ejemplo para comenzar rápidamente
- **Diseño moderno**: Interfaz profesional con gradientes y animaciones suaves
- **Header informativo**: Muestra las capacidades del sistema (Medicina Forense, Criminología, Balística, etc.)

Una vez iniciado, abre tu navegador en `http://localhost:7860` (o el puerto especificado).

**Nota:** La primera consulta puede tardar más tiempo debido a la carga inicial del modelo de embeddings.

### 4. Scripts de Utilidad

El proyecto incluye varios scripts útiles en `scripts/`:

#### Probar el Sistema
```bash
# Prueba completa del sistema (sin necesidad de API key)
python scripts/test_system.py
```

#### Probar Consultas
```bash
# Prueba una consulta de ejemplo
python scripts/test_query.py
```

#### Organizar PDFs
```bash
# Organiza PDFs en directorios según su tipo
python scripts/organize_pdfs.py
```

#### Actualizar Confiabilidad
```bash
# Actualiza niveles de confiabilidad de documentos
python scripts/update_reliability.py
```

## ⚙️ Configuración

### Variables de Entorno (`.env`)

Edita el archivo `.env` para personalizar:

```bash
# Groq Configuration
GROQ_API_KEY=tu_api_key_aqui
GROQ_MODEL=llama-3.3-70b-versatile  # Modelo a usar

# ChromaDB Configuration
CHROMA_DB_PATH=./chroma_db          # Ruta de persistencia

# Embeddings Configuration
EMBEDDING_MODEL=BAAI/bge-m3         # Modelo de embeddings
EMBEDDING_DEVICE=cpu                 # cpu o cuda

# Chunking Configuration
CHUNK_SIZE=600                      # Tamaño de chunks (tokens)
CHUNK_OVERLAP=100                   # Overlap entre chunks
MIN_CHUNK_SIZE=200                  # Tamaño mínimo

# Retrieval Configuration
DEFAULT_K=2                          # Número de documentos por defecto
MAX_K=10                             # Máximo de documentos
MMR_DIVERSITY=0.5                    # Diversidad MMR (0-1)

# Reranking Configuration
USE_RERANKER=false                   # Habilitar reranking
RERANKER_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2

# Logging
LOG_LEVEL=INFO                       # Nivel de logging
```

### Configuración en Código (`config/settings.py`)

Para cambios más avanzados, edita `config/settings.py`:

- **Chunking**: `CHUNK_SIZE`, `CHUNK_OVERLAP`, `MIN_CHUNK_SIZE`
- **Retrieval**: `DEFAULT_K`, `MAX_K`, `MMR_DIVERSITY`
- **Reranking**: `USE_RERANKER`, `RERANKER_MODEL`
- **Embeddings**: `EMBEDDING_MODEL`, `EMBEDDING_DEVICE`, `EMBEDDING_DIMENSION`
- **Colecciones**: `CHROMA_COLLECTIONS` - Define nuevas colecciones
- **Metadata**: `METADATA_FIELDS` - Campos de metadata personalizados

## Colecciones ChromaDB

El sistema organiza documentos en colecciones:

- `criminology_theory` - Teorías criminológicas
- `forensic_cases` - Casos forenses
- `serial_killers` - Estudios de asesinos seriales
- `legislation` - Legislación penal
- `investigation_techniques` - Técnicas de investigación

## Metadata Criminológica

Cada documento incluye metadata extraída automáticamente:

- `crime_type` - Tipo de crimen
- `offender_type` - Tipo de ofensor
- `victimology` - Información sobre víctimas
- `modus_operandi` - MO del crimen
- `signature_behavior` - Comportamiento de firma
- `geography` - Ubicación geográfica
- `time_period` - Período temporal
- `source_reliability` - Confiabilidad (alta/media/baja)
- `document_authority` - Autoridad (FBI, DOJ, académico, etc.)

## Logging Forense

Todas las consultas se registran en `logs/` con:

- Pregunta original
- Documentos utilizados
- Prompt final enviado al LLM
- Respuesta generada
- Fuentes citadas
- Metadata completa
- Timestamp

Formato: JSON estructurado para auditoría y análisis.

## Seguridad y Ética

- **Read-only knowledge base**: No modifica documentos originales
- **Disclaimer legal**: Incluido en prompts del sistema
- **Sin inferencias acusatorias**: No perfilado de personas reales
- **Uso académico**: Diseñado para investigación y educación


## 🛠️ Desarrollo

### Estructura de Componentes

- **Ingesta**: 
  - `ingest/pdf_loader.py` - Carga PDFs con pdfplumber/PyPDF2
  - `ingest/preprocessor.py` - Normalización, limpieza, OCR opcional
  - `ingest/metadata_extractor.py` - Extracción de metadata criminológica
  
- **Chunking**: 
  - `chunking/semantic_chunker.py` - División semántica inteligente
  
- **Embeddings**: 
  - `embeddings/bge_m3_embedder.py` - Generación de embeddings BGE-M3
  
- **Vector Store**: 
  - `vectorstore/chroma_manager.py` - Gestión de ChromaDB y colecciones
  
- **Retriever**: 
  - `retriever/advanced_retriever.py` - Búsqueda con MMR y filtros
  - `retriever/reranker.py` - Reranking opcional con cross-encoder
  
- **LangGraph**: 
  - `graph/state.py` - Estado tipado con Pydantic
  - `graph/nodes.py` - Nodos: retrieve, rerank, generate, format
  - `graph/graph.py` - Definición del grafo completo
  
- **LLM**: 
  - `llm/groq_client.py` - Cliente Groq con manejo de errores
  
- **Prompts**: 
  - `prompts/criminological_prompts.py` - Prompts especializados con reglas éticas
  
- **UI**: 
  - `ui/cli.py` - Interfaz CLI interactiva
  - `ui/gradio_app.py` - Interfaz web Gradio

### Extender el Sistema

1. **Agregar nuevos tipos de documentos**: 
   - Extiende `MetadataExtractor` en `ingest/metadata_extractor.py`
   - Agrega patrones de detección para nuevos tipos

2. **Personalizar chunking**: 
   - Modifica `SemanticChunker` en `chunking/semantic_chunker.py`
   - Ajusta tamaños y estrategias de overlap

3. **Agregar colecciones**: 
   - Actualiza `CHROMA_COLLECTIONS` en `config/settings.py`
   - Modifica `determine_collection()` en `vectorstore/chroma_manager.py`

4. **Modificar prompts**: 
   - Edita `prompts/criminological_prompts.py`
   - Ajusta reglas éticas y formato de respuestas

5. **Agregar nuevos nodos al grafo**: 
   - Define nuevos nodos en `graph/nodes.py`
   - Actualiza el grafo en `graph/graph.py`

### Testing

Ejecuta las pruebas del sistema:

```bash
# Prueba completa (imports, ChromaDB, retrieval)
python scripts/test_system.py

# Prueba de consulta específica
python scripts/test_query.py
```

### Logging y Debugging

- Los logs se guardan en `logs/` en formato JSON
- Cada consulta genera un log con trazabilidad completa
- Usa `LOG_LEVEL=DEBUG` en `.env` para más detalles

## 📊 Estado del Proyecto

Este proyecto está en desarrollo activo. Las características principales están implementadas y funcionales según los planes de desarrollo documentados en `.cursor/plans/`:

✅ **Completado:**
- Sistema de ingesta de PDFs con preprocesamiento y OCR opcional
- Chunking semántico estratégico (500-800 tokens, overlap 10-20%)
- Embeddings BGE-M3 multilingües (1024 dimensiones)
- ChromaDB con múltiples colecciones y metadata rica
- Retriever avanzado con MMR y filtros de metadata
- Reranker opcional con cross-encoder
- LangGraph para orquestación de flujos complejos
- Integración con Groq LLM (múltiples modelos soportados)
- Interfaz CLI interactiva con comandos especiales
- Interfaz web Gradio tipo ChatGPT con visualización de fuentes
- Logging forense con trazabilidad completa (JSON)
- Scripts de utilidad (ingesta, pruebas, organización)


**Planes de desarrollo documentados:**
- `.cursor/plans/rag_criminológico_con_langgraph_dd46c1e8.plan.md` - Arquitectura base del sistema
- `.cursor/plans/interfaz_gradio_para_rag_criminológico_23cabb9e.plan.md` - Implementación de interfaz web

## 📚 Documentos Incluidos

El proyecto incluye documentos de ejemplo en:
- `data/forensic_manual/` - Manuales de balística, autopsia, escena del crimen, etc.
- `data/legislation/` - Manuales de criminalística, técnicas de investigación, psicología criminal

**Nota:** Estos son documentos de ejemplo. Agrega tus propios documentos según tus necesidades.

## 🔐 Seguridad y Ética

- **Read-only knowledge base**: El sistema no modifica documentos originales
- **Disclaimer legal**: Incluido en prompts del sistema
- **Sin inferencias acusatorias**: No perfilado de personas reales
- **Uso académico**: Diseñado para investigación y educación
- **Privacidad**: Los datos se almacenan localmente (ChromaDB)
- **API Keys**: Nunca compartas tu `GROQ_API_KEY` públicamente

## 📝 Notas Adicionales

- **Primera ejecución**: La primera vez que ejecutes el sistema, se descargarán los modelos de embeddings (~1.5GB)
- **Persistencia**: ChromaDB guarda los datos en `chroma_db/` localmente
- **Rendimiento**: La primera consulta es más lenta debido a la carga inicial de modelos
- **Límites Groq**: Respeta los límites de tu plan de Groq API

## 📄 Licencia

[Especificar licencia]

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Contacto

[Información de contacto]

---

**Desarrollado con:** LangGraph, Groq, ChromaDB, BGE-M3, Gradio
