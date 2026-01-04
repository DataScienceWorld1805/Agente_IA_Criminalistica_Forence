"""
Cliente Groq para generación de respuestas en el sistema RAG criminológico.
"""
import logging
import time
from typing import Optional, Dict, Any
from groq import Groq
from config import settings

logger = logging.getLogger(__name__)


class GroqClient:
    """Cliente para interactuar con Groq LLM."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Inicializa el cliente Groq.
        
        Args:
            api_key: API key de Groq (default: config)
            model: Modelo a usar (default: desde config o llama-3.3-70b-versatile)
        """
        self.api_key = api_key or settings.GROQ_API_KEY
        if not self.api_key:
            raise ValueError("GROQ_API_KEY no proporcionada")
        
        # Usar modelo de config si no se especifica
        self.model = model or getattr(settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa el cliente de Groq."""
        try:
            logger.info("Inicializando cliente Groq")
            self.client = Groq(api_key=self.api_key)
            logger.info(f"Cliente Groq inicializado con modelo: {self.model}")
        except Exception as e:
            logger.error(f"Error inicializando cliente Groq: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> str:
        """
        Genera una respuesta usando Groq LLM.
        
        Args:
            prompt: Prompt del usuario
            system_prompt: Prompt del sistema (opcional)
            temperature: Temperatura para generación
            max_tokens: Máximo de tokens a generar
            stream: Si generar en streaming
            
        Returns:
            Respuesta generada
        """
        if not prompt:
            raise ValueError("Prompt vacío")
        
        logger.info(f"Generando respuesta con Groq (modelo: {self.model})")
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Manejar rate limiting con retry
            max_retries = 3
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=stream
                    )
                    
                    if stream:
                        # Procesar streaming
                        full_response = ""
                        for chunk in response:
                            if chunk.choices[0].delta.content:
                                full_response += chunk.choices[0].delta.content
                        return full_response
                    else:
                        # Respuesta completa
                        return response.choices[0].message.content
                        
                except Exception as e:
                    error_str = str(e).lower()
                    # Verificar si es un error de rate limit
                    if "rate_limit" in error_str or "429" in str(e):
                        # Extraer tiempo de espera del mensaje de error si está disponible
                        wait_time = retry_delay * (2 ** attempt)
                        
                        # Intentar extraer el tiempo de espera del mensaje de error
                        import re
                        time_match = re.search(r'(\d+)m(\d+\.?\d*)s', str(e))
                        if time_match:
                            minutes = int(time_match.group(1))
                            seconds = float(time_match.group(2))
                            wait_time = (minutes * 60) + seconds
                            logger.warning(f"Límite diario de tokens alcanzado. Espera {minutes}m {int(seconds)}s antes de reintentar...")
                        else:
                            logger.warning(f"Rate limit alcanzado. Esperando {wait_time}s antes de reintentar...")
                        
                        if attempt < max_retries - 1:
                            time.sleep(min(wait_time, 60))  # Máximo 60 segundos de espera
                            continue
                        else:
                            # Si es límite diario, lanzar error más descriptivo
                            if "tokens per day" in error_str or "tpd" in error_str:
                                raise ValueError(
                                    f"Límite diario de tokens alcanzado para el modelo {self.model}. "
                                    f"Por favor, espera hasta mañana o considera cambiar a un modelo diferente "
                                    f"(ej: llama-3.1-8b-instant) configurando GROQ_MODEL en tu archivo .env"
                                )
                            raise
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"Error generando respuesta con Groq: {e}")
            raise
    
    def generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """
        Genera respuesta con reintentos automáticos.
        
        Args:
            prompt: Prompt del usuario
            system_prompt: Prompt del sistema
            max_retries: Número máximo de reintentos
            **kwargs: Argumentos adicionales para generate()
            
        Returns:
            Respuesta generada
        """
        for attempt in range(max_retries):
            try:
                return self.generate(prompt, system_prompt, **kwargs)
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Intento {attempt + 1} falló: {e}. Reintentando...")
                    time.sleep(1 * (attempt + 1))
                else:
                    logger.error(f"Todos los intentos fallaron: {e}")
                    raise
        
        return ""
