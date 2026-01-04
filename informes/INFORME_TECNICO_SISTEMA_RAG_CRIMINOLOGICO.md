# INFORME TÉCNICO
## Sistema RAG Criminológico con LangGraph

**Sistema de Retrieval-Augmented Generation Especializado en Criminología, Medicina Forense y Balística**

---

**Fecha:** Enero 2025  
**Versión:** 1.0  
**Estado:** Implementación Completada

---

## Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Introducción](#introducción)
3. [Objetivos del Proyecto](#objetivos-del-proyecto)
4. [Arquitectura del Sistema](#arquitectura-del-sistema)
5. [Componentes Técnicos](#componentes-técnicos)
6. [Metodología de Implementación](#metodología-de-implementación)
7. [Tecnologías Utilizadas](#tecnologías-utilizadas)
8. [Estado de Implementación](#estado-de-implementación)
9. [Características Principales](#características-principales)
10. [Conclusiones](#conclusiones)
11. [Referencias Técnicas](#referencias-técnicas)

---

## Resumen Ejecutivo

Este informe documenta el desarrollo e implementación de un sistema avanzado de **Retrieval-Augmented Generation (RAG)** especializado en dominios criminológicos, medicina forense y balística. El sistema utiliza **LangGraph** para la orquestación de flujos complejos, **Groq LLM** para la generación de respuestas, **embeddings BGE-M3** multilingües para búsqueda semántica y **ChromaDB** como base de datos vectorial.

El sistema ha sido diseñado para procesar documentos PDF especializados, indexarlos con embeddings semánticos y utilizar técnicas avanzadas de recuperación y reranking para proporcionar respuestas precisas, citadas y basadas en evidencia documental. La implementación incluye un sistema completo de ingesta, procesamiento, almacenamiento vectorial y generación de respuestas con trazabilidad forense completa.

**Estado del Proyecto:** ✅ **Completado** - Todas las funcionalidades principales han sido implementadas y están operativas.

---

## Introducción

### Contexto

La necesidad de sistemas de información especializados en criminología y medicina forense ha crecido significativamente en los últimos años. Los profesionales de estas áreas requieren acceso rápido y preciso a información documental especializada, incluyendo manuales técnicos, estudios de casos, legislación y documentos de autoridades como el FBI y el DOJ.

Los sistemas tradicionales de búsqueda de información presentan limitaciones en la comprensión semántica y en la capacidad de sintetizar información compleja de múltiples fuentes. El enfoque RAG (Retrieval-Augmented Generation) combina la precisión de la recuperación de información con la capacidad de generación de lenguaje natural, permitiendo crear asistentes especializados que pueden responder consultas complejas basándose en una base de conocimiento documental.

### Problema a Resolver

El desafío principal consiste en crear un sistema que:

1. **Procese documentos especializados** en formato PDF con contenido técnico y forense
2. **Extraiga y organice metadata criminológica** de manera automática
3. **Realice búsquedas semánticas precisas** en grandes volúmenes de documentos
4. **Genere respuestas coherentes y citadas** basadas en evidencia documental
5. **Mantenga trazabilidad completa** de consultas y respuestas para auditoría
6. **Proporcione interfaces de usuario** accesibles y profesionales

---

## Objetivos del Proyecto

### Objetivo General

Desarrollar un sistema RAG completo y especializado que permita a usuarios consultar información criminológica y forense mediante procesamiento de lenguaje natural, con respuestas precisas basadas en documentos fuente y trazabilidad completa.

### Objetivos Específicos

1. **Sistema de Ingesta Robusto**
   - Carga y procesamiento de documentos PDF
   - Preprocesamiento y limpieza de texto
   - Extracción automática de metadata criminológica

2. **Chunking Semántico Estratégico**
   - División inteligente de documentos (500-800 tokens)
   - Overlap del 10-20% para preservar contexto
   - Clasificación por tipo de contenido

3. **Indexación Vectorial Avanzada**
   - Embeddings multilingües BGE-M3 (1024 dimensiones)
   - Almacenamiento en ChromaDB con múltiples colecciones
   - Metadata rica indexada para filtrado

4. **Recuperación y Reranking**
   - Retriever avanzado con MMR (Max Marginal Relevance)
   - Filtros de metadata por tipo de crimen, autoridad, período
   - Reranking opcional con cross-encoders

5. **Orquestación con LangGraph**
   - Flujo de trabajo estructurado con grafos de estado
   - Nodos especializados: retrieve, rerank, generate, format
   - Manejo de errores y flujos condicionales

6. **Generación de Respuestas**
   - Integración con Groq LLM (múltiples modelos)
   - Prompts especializados para criminología
   - Formateo con citas y referencias

7. **Logging Forense**
   - Trazabilidad completa en formato JSON
   - Registro de consultas, documentos usados y respuestas
   - Sistema de auditoría

8. **Interfaces de Usuario**
   - Interfaz CLI interactiva
   - Interfaz web moderna con Gradio

---

## Arquitectura del Sistema

### Diagrama de Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCUMENTOS FUENTE (PDFs)                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ FBI Docs     │ │ Forensic     │ │ Academic     │        │
│  │              │ │ Manuals      │ │ Papers       │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              SISTEMA DE INGESTA                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ PDF Loader   │ │ Preprocessor │ │ Metadata     │        │
│  │              │ │              │ │ Extractor    │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              CHUNKING SEMÁNTICO                              │
│  • Tamaño: 500-800 tokens                                   │
│  • Overlap: 10-20%                                          │
│  • Clasificación por tipo                                   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              EMBEDDINGS BGE-M3                               │
│  • Modelo: BAAI/bge-m3                                      │
│  • Dimensiones: 1024                                        │
│  • Multilingüe                                              │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              CHROMADB VECTOR STORE                           │
│  • Múltiples colecciones                                    │
│  • Metadata rica indexada                                   │
│  • Persistencia local                                       │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              LANGRAPH ORCHESTRATION                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Retrieve │→│ Rerank   │→│ Generate │→│ Format   │      │
│  │          │ │ (opcional)│ │          │ │          │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              RESPUESTA CITADA + LOGGING                      │
│  • Respuesta formateada con citas                           │
│  • Fuentes consultadas                                      │
│  • Logging forense (JSON)                                   │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Procesamiento

1. **Fase de Ingesta**
   - Los documentos PDF se cargan desde directorios organizados
   - Se preprocesan (normalización, limpieza, OCR opcional)
   - Se extrae metadata criminológica automáticamente

2. **Fase de Indexación**
   - Los documentos se dividen en chunks semánticos
   - Se generan embeddings con BGE-M3
   - Se almacenan en ChromaDB con metadata enriquecida

3. **Fase de Consulta**
   - El usuario realiza una consulta en lenguaje natural
   - LangGraph orquesta el flujo:
     - **Retrieve**: Búsqueda semántica en ChromaDB
     - **Rerank** (opcional): Mejora de relevancia
     - **Generate**: Generación de respuesta con Groq LLM
     - **Format**: Formateo con citas y referencias
   - Se registra todo el proceso en logs forenses

---

## Componentes Técnicos

### 1. Sistema de Ingesta

**Ubicación:** `ingest/`

#### 1.1 PDF Loader (`pdf_loader.py`)
- Utiliza `pdfplumber` y `PyPDF2` para carga de PDFs
- Soporte para PDFs con texto y escaneados (OCR opcional)
- Extracción de texto preservando estructura

#### 1.2 Preprocessor (`preprocessor.py`)
- Normalización de texto (encoding, caracteres especiales)
- Limpieza de headers, footers, números de página
- Detección y procesamiento OCR cuando es necesario
- Normalización de espacios y formato

#### 1.3 Metadata Extractor (`metadata_extractor.py`)
- Extracción automática de metadata criminológica:
  - `crime_type`: Tipo de crimen
  - `offender_type`: Tipo de ofensor
  - `victimology`: Información sobre víctimas
  - `modus_operandi`: MO del crimen
  - `signature_behavior`: Comportamiento de firma
  - `geography`: Ubicación geográfica
  - `time_period`: Período temporal
  - `source_reliability`: Confiabilidad (alta/media/baja)
  - `document_authority`: Autoridad (FBI, DOJ, académico, etc.)

### 2. Chunking Semántico

**Ubicación:** `chunking/semantic_chunker.py`

- **Estrategia**: División semántica inteligente (no solo por tokens)
- **Tamaño**: 500-800 tokens por chunk
- **Overlap**: 10-20% entre chunks para preservar contexto
- **Clasificación**: Tipos de chunk (Teoría, Hechos, Análisis, Conclusiones)
- **Metadata por chunk**: `section`, `case`, `confidence_level`

### 3. Embeddings BGE-M3

**Ubicación:** `embeddings/bge_m3_embedder.py`

- **Modelo**: `BAAI/bge-m3`
- **Dimensiones**: 1024
- **Características**:
  - Soporte multilingüe
  - Optimizado para tareas de recuperación
  - Batch processing para eficiencia
- **Integración**: `sentence-transformers` o `FlagEmbedding`

### 4. Vector Store ChromaDB

**Ubicación:** `vectorstore/chroma_manager.py`

- **Persistencia**: Almacenamiento local en disco
- **Colecciones Organizadas**:
  - `criminology_theory`: Teorías criminológicas
  - `forensic_cases`: Casos forenses
  - `serial_killers`: Estudios de asesinos seriales
  - `legislation`: Legislación penal
  - `investigation_techniques`: Técnicas de investigación
- **Metadata Indexada**: Todos los campos de metadata son indexados para filtrado rápido

### 5. Retriever Avanzado

**Ubicación:** `retriever/advanced_retriever.py`

- **Similarity Search**: Búsqueda por similitud semántica
- **MMR (Max Marginal Relevance)**: Diversificación de resultados
- **Filtros de Metadata**: Filtrado por:
  - Tipo de crimen
  - Autoridad del documento
  - Período temporal
  - Confiabilidad
  - Geografía
- **k dinámico**: 3-10 documentos según necesidad

### 6. Reranker Opcional

**Ubicación:** `retriever/reranker.py`

- **Modelo**: Cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
- **Función**: Mejora de relevancia mediante reranking semántico
- **Priorización**: Fuentes oficiales y de alta autoridad
- **Opcional**: Puede deshabilitarse para mayor velocidad

### 7. LangGraph Orchestration

**Ubicación:** `graph/`

#### 7.1 Estado (`state.py`)
- Estado tipado con Pydantic:
  - `query`: Consulta del usuario
  - `documents`: Documentos recuperados
  - `reranked_docs`: Documentos rerankeados (opcional)
  - `context`: Contexto formateado para LLM
  - `response`: Respuesta generada
  - `sources`: Fuentes citadas
  - `metadata`: Metadata adicional
  - `error`: Manejo de errores

#### 7.2 Nodos (`nodes.py`)
- **`retrieve`**: Búsqueda en ChromaDB
- **`rerank`**: Reranking opcional
- **`generate`**: Generación con Groq LLM
- **`format_response`**: Formateo con citas

#### 7.3 Grafo (`graph.py`)
- Definición del grafo LangGraph completo
- Flujo lineal con condicionales para reranking
- Manejo de errores y validación

### 8. Integración Groq LLM

**Ubicación:** `llm/groq_client.py`

- **Cliente Groq**: Integración con Groq API
- **Modelos Soportados**:
  - `llama-3.3-70b-versatile` (recomendado)
  - `llama-3.1-70b-versatile`
  - `llama-3.1-8b-instant`
  - `mixtral-8x7b-32768`
- **Manejo de Errores**: Rate limiting, timeouts, reintentos
- **Streaming**: Opcional para respuestas en tiempo real

### 9. Prompts Especializados

**Ubicación:** `prompts/criminological_prompts.py`

- **Prompt Sistema**: Analista criminológico senior
- **Reglas Éticas**:
  - No inventar datos
  - Citar fuentes siempre
  - Diferenciar hechos vs inferencias
  - Disclaimer legal incluido
- **Templates**: Diferentes tipos de consultas

### 10. Logging Forense

**Ubicación:** `utils/logger.py`

- **Formato**: JSON estructurado
- **Trazabilidad Completa**:
  - Pregunta original
  - Documentos utilizados
  - Prompt final enviado al LLM
  - Respuesta generada
  - Fuentes citadas
  - Metadata completa
  - Timestamp
- **Almacenamiento**: `logs/` con archivos por fecha

### 11. Interfaces de Usuario

#### 11.1 CLI (`ui/cli.py`)
- Interfaz de línea de comandos interactiva
- Comandos especiales: `/help`, `/quit`, `/sources`
- Visualización de fuentes y citas

#### 11.2 Gradio (`ui/gradio_app.py`)
- Interfaz web moderna tipo ChatGPT
- Visualización de fuentes con metadata
- Diseño profesional y responsivo

---

## Metodología de Implementación

### Fases de Desarrollo

1. **Fase 1: Configuración y Estructura Base**
   - ✅ Creación de estructura de directorios
   - ✅ Configuración de variables de entorno
   - ✅ Definición de dependencias

2. **Fase 2: Sistema de Ingesta**
   - ✅ Implementación de PDF loader
   - ✅ Preprocesamiento y limpieza
   - ✅ Extracción de metadata

3. **Fase 3: Chunking y Embeddings**
   - ✅ Chunking semántico estratégico
   - ✅ Integración BGE-M3

4. **Fase 4: Vector Store**
   - ✅ Configuración ChromaDB
   - ✅ Múltiples colecciones
   - ✅ Indexación de metadata

5. **Fase 5: Retrieval y Reranking**
   - ✅ Retriever avanzado con MMR
   - ✅ Reranker opcional

6. **Fase 6: LangGraph**
   - ✅ Definición de estado
   - ✅ Implementación de nodos
   - ✅ Definición del grafo

7. **Fase 7: Integración LLM**
   - ✅ Cliente Groq
   - ✅ Prompts especializados

8. **Fase 8: Logging y Utilidades**
   - ✅ Sistema de logging forense
   - ✅ Validadores

9. **Fase 9: Interfaces**
   - ✅ Interfaz CLI
   - ✅ Interfaz Gradio

10. **Fase 10: Documentación**
    - ✅ README completo
    - ✅ Scripts de utilidad

---

## Tecnologías Utilizadas

### Lenguaje y Framework Base
- **Python 3.9+**: Lenguaje de programación principal
- **Pydantic 2.5+**: Validación de datos y tipado

### Orquestación y Flujos
- **LangGraph 0.2+**: Framework de grafos para orquestación
- **LangChain 0.2+**: Integración con componentes

### Base de Datos Vectorial
- **ChromaDB 0.4+**: Base de datos vectorial persistente

### Procesamiento de Lenguaje Natural
- **Groq 0.4+**: Cliente para Groq LLM API
- **sentence-transformers 2.3+**: Modelos de embeddings
- **FlagEmbedding 1.2+**: Alternativa para embeddings BGE-M3

### Procesamiento de Documentos
- **pdfplumber 0.10+**: Extracción de texto de PDFs
- **PyPDF2 3.0+**: Procesamiento adicional de PDFs
- **pytesseract 0.3+**: OCR opcional

### Machine Learning (Opcional)
- **torch 2.0+**: Framework para reranking
- **transformers 4.35+**: Modelos de reranking

### Utilidades
- **python-dotenv 1.0+**: Variables de entorno
- **tiktoken 0.5+**: Tokenización
- **python-json-logger 2.0+**: Logging estructurado

### Interfaz Web
- **gradio 4.0+**: Framework para interfaz web

---

## Estado de Implementación

### Componentes Completados ✅

| Componente | Estado | Descripción |
|------------|--------|-------------|
| Sistema de Ingesta | ✅ Completado | PDF loader, preprocessor, metadata extractor |
| Chunking Semántico | ✅ Completado | División inteligente 500-800 tokens, overlap 10-20% |
| Embeddings BGE-M3 | ✅ Completado | Integración completa, 1024 dimensiones |
| ChromaDB Vector Store | ✅ Completado | Múltiples colecciones, metadata rica |
| Retriever Avanzado | ✅ Completado | MMR, filtros de metadata |
| Reranker | ✅ Completado | Cross-encoder opcional |
| LangGraph State | ✅ Completado | Estado tipado con Pydantic |
| LangGraph Nodes | ✅ Completado | retrieve, rerank, generate, format |
| LangGraph Definition | ✅ Completado | Grafo completo con flujos condicionales |
| Integración Groq | ✅ Completado | Cliente con manejo de errores |
| Prompts Especializados | ✅ Completado | Prompts para criminología con reglas éticas |
| Logging Forense | ✅ Completado | Trazabilidad completa en JSON |
| Interfaz CLI | ✅ Completado | CLI interactiva con comandos |
| Interfaz Gradio | ✅ Completado | Interfaz web moderna tipo ChatGPT |
| Documentación | ✅ Completado | README y scripts de utilidad |

### Funcionalidades Principales

✅ **Procesamiento de PDFs**: Carga, preprocesamiento y extracción de texto  
✅ **Extracción de Metadata**: Automática con campos criminológicos  
✅ **Chunking Inteligente**: Semántico con preservación de contexto  
✅ **Búsqueda Semántica**: Embeddings multilingües BGE-M3  
✅ **Recuperación Avanzada**: MMR y filtros de metadata  
✅ **Reranking Opcional**: Mejora de relevancia  
✅ **Generación de Respuestas**: Con Groq LLM y prompts especializados  
✅ **Citas y Referencias**: Formateo profesional con fuentes  
✅ **Logging Forense**: Trazabilidad completa  
✅ **Interfaces Múltiples**: CLI y web (Gradio)  

### Mejoras Futuras 🔄

- Optimización de rendimiento y velocidad
- Soporte para más formatos (DOCX, TXT, HTML)
- Mejoras en extracción automática de metadata
- Historial persistente en interfaz web
- Exportación de consultas y respuestas
- Análisis estadístico de consultas

---

## Características Principales

### 1. Especialización en Dominio Criminológico

El sistema está específicamente diseñado para dominios criminológicos y forenses, con:
- Metadata especializada (tipo de crimen, MO, autoridad, etc.)
- Prompts especializados con reglas éticas
- Organización por colecciones temáticas
- Filtros específicos para búsquedas forenses

### 2. Arquitectura Modular y Escalable

- Componentes independientes y reutilizables
- Fácil extensión para nuevos tipos de documentos
- Configuración centralizada
- Separación de responsabilidades

### 3. Trazabilidad Forense Completa

- Logging estructurado en JSON
- Registro de todas las consultas y respuestas
- Documentos utilizados en cada respuesta
- Timestamps y metadata completa

### 4. Búsqueda Semántica Avanzada

- Embeddings multilingües BGE-M3
- MMR para diversificación
- Reranking opcional para precisión
- Filtros de metadata granulares

### 5. Interfaz de Usuario Profesional

- CLI interactiva con comandos especiales
- Interfaz web moderna tipo ChatGPT
- Visualización de fuentes con metadata
- Diseño profesional y responsivo

### 6. Ética y Seguridad

- Read-only knowledge base
- Disclaimer legal en prompts
- Sin inferencias acusatorias
- Uso académico y de investigación

---

## Conclusiones

### Logros Principales

1. **Sistema Completo y Funcional**: Se ha implementado exitosamente un sistema RAG completo especializado en criminología, con todas las funcionalidades principales operativas.

2. **Arquitectura Robusta**: La arquitectura modular basada en LangGraph permite escalabilidad y mantenibilidad, con componentes bien definidos y separados.

3. **Tecnologías de Vanguardia**: El uso de BGE-M3, LangGraph, ChromaDB y Groq LLM proporciona capacidades avanzadas de procesamiento y generación.

4. **Trazabilidad Forense**: El sistema de logging forense proporciona trazabilidad completa, esencial para aplicaciones en dominios legales y forenses.

5. **Interfaces Accesibles**: Las interfaces CLI y web permiten acceso fácil al sistema para diferentes tipos de usuarios.

### Impacto y Aplicaciones

El sistema puede ser utilizado para:
- **Investigación Académica**: Acceso rápido a literatura especializada
- **Formación Profesional**: Herramienta de aprendizaje para estudiantes
- **Análisis Forense**: Consulta rápida de procedimientos y técnicas
- **Referencia Técnica**: Base de conocimiento consultable

### Limitaciones y Consideraciones

- **Dependencia de API Externa**: Requiere conexión a internet para Groq API
- **Procesamiento Inicial**: La primera consulta es más lenta debido a carga de modelos
- **Límites de API**: Sujeto a límites de rate limiting de Groq
- **Metadata Manual**: Algunos campos de metadata pueden requerir revisión manual

### Recomendaciones Futuras

1. Implementar caché local para embeddings y respuestas frecuentes
2. Agregar soporte para más formatos de documentos
3. Mejorar extracción automática de metadata con NLP avanzado
4. Implementar análisis estadístico de consultas
5. Agregar autenticación y control de acceso para producción

---

## Referencias Técnicas

### Documentación Oficial

- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **LangChain**: https://python.langchain.com/
- **ChromaDB**: https://www.trychroma.com/
- **Groq**: https://console.groq.com/docs
- **BGE-M3**: https://github.com/FlagOpen/FlagEmbedding
- **Gradio**: https://www.gradio.app/

### Modelos y APIs

- **BGE-M3 Embeddings**: `BAAI/bge-m3` (1024 dimensiones)
- **Groq Models**: `llama-3.3-70b-versatile`, `llama-3.1-70b-versatile`, etc.
- **Reranker**: `cross-encoder/ms-marco-MiniLM-L-6-v2`

### Estándares y Buenas Prácticas

- **Pydantic**: Validación de datos y tipado estático
- **JSON Logging**: Formato estructurado para trazabilidad
- **Modular Architecture**: Separación de responsabilidades
- **Error Handling**: Manejo robusto de errores y edge cases

---

**Fin del Informe Técnico**

---

*Este informe documenta la implementación completa del Sistema RAG Criminológico con LangGraph. Para más información técnica, consultar el código fuente y la documentación en el repositorio del proyecto.*

