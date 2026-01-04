"""
Módulo de prompts especializados para criminología.
"""

from .criminological_prompts import (
    get_system_prompt,
    get_user_prompt_template,
    format_prompt_with_context
)

__all__ = [
    "get_system_prompt",
    "get_user_prompt_template",
    "format_prompt_with_context"
]
