"""
agent/llm/ai_engine.py — AI Engine (Optimized for Token Efficiency)

This handles 20+ models using a standard OpenAI-compatible API.
Optimized to never exceed 1000 tokens and prevent redundant tool calls.
"""

import requests
import json
from typing import List, Any, Optional, Dict, Set
from agent.llm.base import LLMProvider
from agent.llm import utils

MAX_TOKENS = 1000
MAX_INPUT_TOKENS = 1000
MAX_TURNS = 3


class OpenRouterProvider(LLMProvider):
    """Implementation of LLMProvider for OpenRouter with Tool Support."""

    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def _convert_to_openai_tools(self, tools: List[Any]) -> List[dict]:
        """Converts Python functions to OpenAI-style tool definitions."""
        import inspect

        openai_tools = []
        for func in tools:
            sig = inspect.signature(func)
            params = {"type": "object", "properties": {}, "required": []}
            for name, param in sig.parameters.items():
                params["properties"][name] = {"type": "string"}
                if param.default == inspect.Parameter.empty:
                    params["required"].append(name)

            openai_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": func.__name__,
                        "description": (func.__doc__ or "").strip().split("\n")[0],
                        "parameters": params,
                    },
                }
            )
        return openai_tools

    def _summarize_messages(
        self, messages: List[dict], max_tokens: int = 600
    ) -> List[dict]:
        """Summarizes old tool results to save tokens."""
        if len(messages) <= 4:
            return messages

        system_msg = messages[0] if messages[0]["role"] == "system" else None
        user_msg = (
            messages[1] if len(messages) > 1 and messages[1]["role"] == "user" else None
        )

        tool_results = [m for m in messages[2:] if m["role"] == "tool"]

        summary_parts = []
        for tool_msg in tool_results[-6:]:
            content = tool_msg.get("content", "")[:200]
            summary_parts.append(f"[{tool_msg.get('name', 'unknown')}] {content}")

        summary_text = " | ".join(summary_parts)

        new_messages = [m for m in messages[:2]]
        new_messages.append(
            {"role": "system", "content": f"[SUMMARIZED HISTORY] {summary_text}"}
        )

        return new_messages

    def _count_tokens(self, messages: List[dict]) -> int:
        """Count estimated tokens in messages."""
        return utils.count_messages_tokens(messages)

    def _enforce_token_budget(self, messages: List[dict]) -> List[dict]:
        """Ensures total tokens never exceed MAX_INPUT_TOKENS."""
        token_count = self._count_tokens(messages)

        while token_count > MAX_INPUT_TOKENS and len(messages) > 2:
            messages = self._summarize_messages(messages, 500)
            token_count = self._count_tokens(messages)

        if token_count > MAX_INPUT_TOKENS:
            system_content = (
                messages[0].get("content", "")
                if messages[0]["role"] == "system"
                else ""
            )
            user_content = (
                messages[1].get("content", "")
                if len(messages) > 1 and messages[1]["role"] == "user"
                else ""
            )

            remaining = MAX_INPUT_TOKENS - 50
            system_tokens = int(remaining * 0.4)
            user_tokens = int(remaining * 0.6)

            safe_system = utils.truncate_by_tokens(system_content, system_tokens)
            safe_user = utils.truncate_by_tokens(user_content, user_tokens)

            messages = [
                {"role": "system", "content": safe_system},
                {"role": "user", "content": safe_user},
            ]

        return messages

    def _enforce_message_size(
        self, content: str, role: str, max_tokens: int
    ) -> List[dict]:
        """Enforces strict token limit on a single message."""
        safe_content = utils.truncate_content(content, max_tokens)
        return [{"role": role, "content": safe_content}]

    def generate_response(
        self, prompt: str, system_instruction: str, tools: Optional[List[Any]] = None
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://resilienz.ai",
            "X-Title": "Resilienz.AI",
            "Content-Type": "application/json",
        }

        safe_prompt = utils.truncate_content(prompt, 400)
        safe_sys = utils.truncate_content(system_instruction, 300)

        messages = [
            {"role": "system", "content": safe_sys},
            {"role": "user", "content": safe_prompt},
        ]

        messages = self._enforce_token_budget(messages)

        openai_tools = self._convert_to_openai_tools(tools) if tools else None
        name_to_func = {t.__name__: t for t in tools} if tools else {}

        called_tools: Dict[str, str] = {}

        for turn in range(MAX_TURNS):
            token_count = self._count_tokens(messages)
            print(f"📊 [OPENROUTER] turn {turn + 1}: Estimated Tokens = ~{token_count}")

            if token_count > MAX_INPUT_TOKENS:
                print(
                    f"⚠️ [OPENROUTER] Exceeds {MAX_INPUT_TOKENS} tokens, enforcing limit..."
                )
                messages = self._enforce_token_budget(messages)
                token_count = self._count_tokens(messages)

            if token_count > MAX_TOKENS:
                print("⚠️ [OPENROUTER] Token budget exceeded, summarizing history...")
                messages = self._summarize_messages(messages)
                token_count = self._count_tokens(messages)
                print(f"📊 [OPENROUTER] After summarization: ~{token_count} tokens")

            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.2,
            }
            if openai_tools:
                payload["tools"] = openai_tools

            try:
                resp = requests.post(
                    self.url, headers=headers, json=payload, timeout=25
                )
            except Exception as e:
                raise Exception(f"Request failed: {str(e)}")

            if resp.status_code == 429:
                raise Exception(
                    f"RATE_LIMIT: Model [{self.model_name}] has reached its limit."
                )

            if resp.status_code == 400:
                if "context_length" in resp.text:
                    raise Exception(
                        f"TOKEN_LIMIT: Request too large for {self.model_name}."
                    )
                raise Exception(f"OpenRouter Error (400): {resp.text[:100]}")

            if resp.status_code != 200:
                raise Exception(
                    f"OpenRouter Error ({resp.status_code}): {resp.text[:200]}"
                )

            res_json = resp.json()
            if "choices" not in res_json:
                raise Exception(
                    f"Invalid OpenRouter Response: {json.dumps(res_json)[:200]}"
                )

            choice = res_json["choices"][0]["message"]
            messages.append(choice)

            if not choice.get("tool_calls"):
                return choice.get("content") or "No content returned."

            for call in choice["tool_calls"]:
                func_name = call["function"]["name"]

                call_key = f"{func_name}:{call['function']['arguments']}"
                if call_key in called_tools:
                    print(f"🔄 [OPENROUTER] Skipping duplicate call: {func_name}")
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call["id"],
                            "name": func_name,
                            "content": f"[Already retrieved] {called_tools[call_key]}",
                        }
                    )
                    continue

                args = json.loads(call["function"]["arguments"])  # noqa: E501
                print(f"🛠️ [OPENROUTER] Executing: {func_name}({args})")

                try:
                    result = name_to_func[func_name](**args)
                    safe_result = utils.truncate_by_tokens(str(result), 300)
                    called_tools[call_key] = safe_result[:150]

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call["id"],
                            "name": func_name,
                            "content": safe_result,
                        }
                    )
                except Exception as e:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call["id"],
                            "name": func_name,
                            "content": f"Error: {str(e)}",
                        }
                    )

        messages = self._summarize_messages(messages, 300)
        messages = self._enforce_token_budget(messages)

        final_payload = {
            "model": self.model_name,
            "messages": messages
            + [{"role": "user", "content": "Brief summary (under 150 tokens)."}],
            "temperature": 0.2,
        }

        final_token_count = self._count_tokens(final_payload["messages"])
        print(
            f"📊 [OPENROUTER] Final request: ~{final_token_count} tokens (max: {MAX_INPUT_TOKENS})"
        )

        resp = requests.post(self.url, headers=headers, json=final_payload, timeout=25)
        if resp.status_code == 200:
            result = resp.json()
            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"].get(
                    "content", "Response generated."
                )

        return "Response complete. Check results above."
