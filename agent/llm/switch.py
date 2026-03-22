import config
import time
from agent.llm.ai_engine import OpenRouterProvider
from typing import List, Any, Optional


class LLMSwitch:
    """Orchestrates LLM providers using OpenRouter."""

    def __init__(self, tools_list: Optional[List[Any]] = None):
        self.tools_list = tools_list

    def try_generate(self, prompt: str, system_instruction: str) -> str:
        """
        Iterates through the OpenRouter models dictionary until a response is received.
        """
        print(f"🔄 [LLM_SWITCH] Starting OpenRouter execution loop...")

        if not config.OPENROUTER_API_KEY:
            return "❌ ERROR: No OpenRouter API key found. Check your .env file."

        # Iterate through the dictionary of 20+ models
        for i, model_name in config.models.items():
            if not model_name:
                continue

            print(f"🏃 [LLM_SWITCH] Trying model [{i}]: {model_name}...")

            try:
                # Initialize OpenRouter with tool-calling support
                openrouter = OpenRouterProvider(config.OPENROUTER_API_KEY, model_name)

                return openrouter.generate_response(
                    prompt, system_instruction, tools=self.tools_list
                )
            except Exception as e:
                err_msg = str(e)
                print(f"⚠️ [LLM_SWITCH] Model [{i}] ({model_name}) failed: {err_msg[:100]}...")

                # 🛑 HALT: If we have no credits, no model will work.
                if "insufficient_credits" in err_msg.lower() or "402" in err_msg:
                    return f"❌ CRITICAL ERROR: OpenRouter account has no credits. Please top up your account."

                # 🛑 HALT: If the input is fundamentally too large even for the provider
                if "413" in err_msg or "too_large" in err_msg.lower():
                    return "❌ CRITICAL ERROR: Your request is too large for the API. Try a shorter question."

                # ⏳ BACKOFF: If it's a rate limit, wait a bit before trying the next model
                if "rate_limit" in err_msg.lower() or "RT" in err_msg or "429" in err_msg:
                    print("⏳ [LLM_SWITCH] Rate limit hit. Waiting 2 seconds before next model...")
                    time.sleep(2)

                continue

        return "🔥 ALL OPENROUTER MODELS EXHAUSTED or RATE LIMITED. Please try again in 1 minute."

