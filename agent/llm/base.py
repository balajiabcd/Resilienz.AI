"""
agent/llm/base.py — LLM Provider Interface

This defines the contract ALL model providers must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMProvider(ABC):
    """Abstract Base Class for LLM Providers."""

    @abstractmethod
    def generate_response(
        self, 
        prompt: str, 
        system_instruction: str,
        tools: Optional[List[Any]] = None
    ) -> str:
        """
        Generates a text response from the LLM.
        
        :param prompt: The user request.
        :param system_instruction: The persona/rules for the agent.
        :param tools: A list of Python functions the model can call.
        """
        return ""
