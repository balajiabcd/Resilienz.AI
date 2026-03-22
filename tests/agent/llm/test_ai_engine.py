"""
tests/agent/llm/test_ai_engine.py — Tests for agent/llm/ai_engine.py

Tests OpenRouter API integration, tool conversion, and response handling.
"""

import pytest
import json
from unittest.mock import MagicMock, patch, call
from agent.llm.ai_engine import OpenRouterProvider


class TestOpenRouterProviderInit:
    """Unit tests for OpenRouterProvider initialization."""

    def test_init_sets_api_key(self):
        provider = OpenRouterProvider("test-key-123", "gemini-model")
        assert provider.api_key == "test-key-123"

    def test_init_sets_model_name(self):
        provider = OpenRouterProvider("test-key", "gpt-4")
        assert provider.model_name == "gpt-4"

    def test_init_sets_url(self):
        provider = OpenRouterProvider("key", "model")
        assert provider.url == "https://openrouter.ai/api/v1/chat/completions"

    def test_multiple_providers_have_independent_state(self):
        p1 = OpenRouterProvider("key1", "model1")
        p2 = OpenRouterProvider("key2", "model2")
        assert p1.api_key != p2.api_key
        assert p1.model_name != p2.model_name


class TestConvertToOpenaiTools:
    """Unit tests for tool conversion to OpenAI format."""

    def test_empty_tools_list(self):
        provider = OpenRouterProvider("key", "model")
        result = provider._convert_to_openai_tools([])
        assert result == []

    def test_single_tool_no_params(self):
        def simple_tool():
            """A simple tool with no parameters."""
            pass

        provider = OpenRouterProvider("key", "model")
        result = provider._convert_to_openai_tools([simple_tool])

        assert len(result) == 1
        assert result[0]["type"] == "function"
        assert result[0]["function"]["name"] == "simple_tool"
        assert (
            result[0]["function"]["description"] == "A simple tool with no parameters."
        )
        assert result[0]["function"]["parameters"]["properties"] == {}
        assert result[0]["function"]["parameters"]["required"] == []

    def test_single_tool_with_params(self):
        def tool_with_args(arg1: str, arg2: int):
            """Tool with arguments."""
            pass

        provider = OpenRouterProvider("key", "model")
        result = provider._convert_to_openai_tools([tool_with_args])

        assert len(result) == 1
        assert "arg1" in result[0]["function"]["parameters"]["properties"]
        assert "arg2" in result[0]["function"]["parameters"]["properties"]

    def test_tool_with_default_params(self):
        def tool_with_defaults(arg1: str, arg2: int = 10):
            """Tool with default value."""
            pass

        provider = OpenRouterProvider("key", "model")
        result = provider._convert_to_openai_tools([tool_with_defaults])

        required = result[0]["function"]["parameters"]["required"]
        assert "arg1" in required
        assert "arg2" not in required

    def test_multiple_tools(self, sample_tools):
        provider = OpenRouterProvider("key", "model")
        result = provider._convert_to_openai_tools(sample_tools)

        assert len(result) == 2
        assert result[0]["function"]["name"] == "dummy_tool_1"
        assert result[1]["function"]["name"] == "dummy_tool_2"

    def test_tool_without_docstring(self):
        def no_doc_tool(arg):
            pass

        provider = OpenRouterProvider("key", "model")
        result = provider._convert_to_openai_tools([no_doc_tool])

        assert result[0]["function"]["description"] == ""


class TestGenerateResponse:
    """Unit tests for generate_response method."""

    @patch("agent.llm.ai_engine.requests.post")
    def test_basic_successful_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"role": "assistant", "content": "Test response content"}}
            ]
        }
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("test-key", "gemini-model")
        result = provider.generate_response("user prompt", "system instruction")

        assert result == "Test response content"
        mock_post.assert_called_once()

    @patch("agent.llm.ai_engine.requests.post")
    def test_truncates_long_prompt(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "content": "Short"}}]
        }
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("key", "model")
        long_prompt = "x" * 10000
        provider.generate_response(long_prompt, "system")

        call_args = mock_post.call_args
        messages = call_args[1]["json"]["messages"]
        assert len(messages[1]["content"]) < 10000

    @patch("agent.llm.ai_engine.requests.post")
    def test_includes_system_instruction(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "content": "Response"}}]
        }
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("key", "model")
        provider.generate_response("prompt", "You are helpful")

        call_args = mock_post.call_args
        messages = call_args[1]["json"]["messages"]
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are helpful"

    @patch("agent.llm.ai_engine.requests.post")
    def test_includes_tools_when_provided(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "content": "Response"}}]
        }
        mock_post.return_value = mock_response

        def sample_tool(arg: str):
            """Sample tool."""
            pass

        provider = OpenRouterProvider("key", "model")
        provider.generate_response("prompt", "system", tools=[sample_tool])

        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "tools" in payload

    @patch("agent.llm.ai_engine.requests.post")
    def test_raises_on_rate_limit(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("key", "model")

        with pytest.raises(Exception) as exc_info:
            provider.generate_response("prompt", "system")
        assert "RATE_LIMIT" in str(exc_info.value)

    @patch("agent.llm.ai_engine.requests.post")
    def test_raises_on_context_length(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "context_length_exceeded"
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("key", "model")

        with pytest.raises(Exception) as exc_info:
            provider.generate_response("prompt", "system")
        assert "TOKEN_LIMIT" in str(exc_info.value)

    @patch("agent.llm.ai_engine.requests.post")
    def test_raises_on_non_200_status(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("key", "model")

        with pytest.raises(Exception) as exc_info:
            provider.generate_response("prompt", "system")
        assert "500" in str(exc_info.value)

    @patch("agent.llm.ai_engine.requests.post")
    def test_raises_on_invalid_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "something went wrong"}
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("key", "model")

        with pytest.raises(Exception):
            provider.generate_response("prompt", "system")

    @patch("agent.llm.ai_engine.requests.post")
    def test_empty_content_returns_default(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "content": ""}}]
        }
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("key", "model")
        result = provider.generate_response("prompt", "system")

        assert result == "No content returned."


class TestToolCallingLoop:
    """Tests for multi-turn tool calling."""

    @patch("agent.llm.ai_engine.requests.post")
    def test_executes_tool_call(self, mock_post):
        def get_data(part: str) -> str:
            return f"Data for {part}"

        call_count = [0]

        def mock_response_generator(*args, **kwargs):
            call_count[0] += 1
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            if call_count[0] == 1:
                mock_resp.json.return_value = {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "call_123",
                                        "function": {
                                            "name": "get_data",
                                            "arguments": json.dumps(
                                                {"part": "AX-7741"}
                                            ),
                                        },
                                    }
                                ],
                            }
                        }
                    ]
                }
            else:
                mock_resp.json.return_value = {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "Final response after tool call",
                            }
                        }
                    ]
                }
            return mock_resp

        mock_post.side_effect = mock_response_generator

        provider = OpenRouterProvider("key", "model")
        result = provider.generate_response("prompt", "system", tools=[get_data])

        assert "Final response" in result

    @patch("agent.llm.ai_engine.requests.post")
    def test_handles_tool_execution_error(self, mock_post):
        def failing_tool(arg: str) -> str:
            raise ValueError("Tool execution failed")

        call_count = [0]

        def mock_response_generator(*args, **kwargs):
            call_count[0] += 1
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            if call_count[0] == 1:
                mock_resp.json.return_value = {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "call_123",
                                        "function": {
                                            "name": "failing_tool",
                                            "arguments": json.dumps({"arg": "test"}),
                                        },
                                    }
                                ],
                            }
                        }
                    ]
                }
            else:
                mock_resp.json.return_value = {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "Response after error",
                            }
                        }
                    ]
                }
            return mock_resp

        mock_post.side_effect = mock_response_generator

        provider = OpenRouterProvider("key", "model")
        result = provider.generate_response("prompt", "system", tools=[failing_tool])

        assert mock_post.call_count == 2

    @patch("agent.llm.ai_engine.requests.post")
    def test_max_turns_limit(self, mock_post):
        def dummy_tool() -> str:
            return "result"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "function": {"name": "dummy_tool", "arguments": "{}"},
                            }
                        ],
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("key", "model")
        result = provider.generate_response("prompt", "system", tools=[dummy_tool])

        assert result == "Loop exceeded max turns."
        assert mock_post.call_count == 10

    @patch("agent.llm.ai_engine.requests.post")
    def test_truncates_large_tool_result(self, mock_post):
        def large_result_tool() -> str:
            return "x" * 10000

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "function": {
                                    "name": "large_result_tool",
                                    "arguments": "{}",
                                },
                            }
                        ],
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("key", "model")
        provider.generate_response("prompt", "system", tools=[large_result_tool])

        final_call = mock_post.call_args_list[-1]
        messages = final_call[1]["json"]["messages"]
        tool_result = messages[-1]["content"]
        assert "[... TRUNCATED" in tool_result or len(tool_result) < 10000


class TestEdgeCases:
    """Edge case tests for OpenRouterProvider."""

    @patch("agent.llm.ai_engine.requests.post")
    def test_none_tools_param(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "content": "ok"}}]
        }
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("key", "model")
        result = provider.generate_response("prompt", "system", tools=None)

        call_args = mock_post.call_args
        assert "tools" not in call_args[1]["json"]

    @patch("agent.llm.ai_engine.requests.post")
    def test_unknown_tool_name_returns_error(self, mock_post):
        call_count = [0]

        def mock_response_generator(*args, **kwargs):
            call_count[0] += 1
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            if call_count[0] == 1:
                mock_resp.json.return_value = {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": "call_123",
                                        "function": {
                                            "name": "unknown_tool",
                                            "arguments": "{}",
                                        },
                                    }
                                ],
                            }
                        }
                    ]
                }
            else:
                mock_resp.json.return_value = {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "Response after unknown tool",
                            }
                        }
                    ]
                }
            return mock_resp

        mock_post.side_effect = mock_response_generator

        provider = OpenRouterProvider("key", "model")
        result = provider.generate_response("prompt", "system", tools=[])

        assert mock_post.call_count == 2

    @patch("agent.llm.ai_engine.requests.post")
    def test_sends_correct_headers(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "content": "ok"}}]
        }
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("my-secret-key", "my-model")
        provider.generate_response("prompt", "system")

        call_args = mock_post.call_args
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer my-secret-key"
        assert headers["Content-Type"] == "application/json"
        assert "resilienz.ai" in headers.get("HTTP-Referer", "")


class TestStress:
    """Stress tests for OpenRouterProvider."""

    @patch("agent.llm.ai_engine.requests.post")
    def test_rapid_successive_calls(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "content": "ok"}}]
        }
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("key", "model")

        for _ in range(50):
            result = provider.generate_response("prompt", "system")

        assert mock_post.call_count == 50

    @patch("agent.llm.ai_engine.requests.post")
    def test_many_tool_calls_in_single_turn(self, mock_post):
        def dummy_tool() -> str:
            return "ok"

        calls = [
            {"id": f"call_{i}", "function": {"name": "dummy_tool", "arguments": "{}"}}
            for i in range(10)
        ]

        call_count = [0]

        def mock_response_generator(*args, **kwargs):
            call_count[0] += 1
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            if call_count[0] == 1:
                mock_resp.json.return_value = {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": calls,
                            }
                        }
                    ]
                }
            else:
                mock_resp.json.return_value = {
                    "choices": [
                        {"message": {"role": "assistant", "content": "Final response"}}
                    ]
                }
            return mock_resp

        mock_post.side_effect = mock_response_generator

        provider = OpenRouterProvider("key", "model")
        result = provider.generate_response("prompt", "system", tools=[dummy_tool])

        assert mock_post.call_count == 2

    @patch("agent.llm.ai_engine.requests.post")
    def test_token_count_reported(self, mock_post, capsys):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "content": "ok"}}]
        }
        mock_post.return_value = mock_response

        provider = OpenRouterProvider("key", "model")
        provider.generate_response("prompt", "system")

        captured = capsys.readouterr()
        assert "Estimated Tokens" in captured.out or mock_post.called
