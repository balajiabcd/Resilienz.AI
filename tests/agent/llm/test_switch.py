"""
tests/agent/llm/test_switch.py — Tests for agent/llm/switch.py

Tests LLM model fallback routing, error handling, and rate limiting.
"""

import pytest
from unittest.mock import MagicMock, patch
from agent.llm.switch import LLMSwitch


class TestLLMSwitchInit:
    """Unit tests for LLMSwitch initialization."""

    def test_init_without_tools(self):
        switch = LLMSwitch()
        assert switch.tools_list is None

    def test_init_with_tools(self, sample_tools):
        switch = LLMSwitch(tools_list=sample_tools)
        assert switch.tools_list == sample_tools

    def test_init_with_empty_list(self):
        switch = LLMSwitch(tools_list=[])
        assert switch.tools_list == []


class TestLLMSwitchTryGenerate:
    """Unit tests for try_generate method."""

    def test_no_api_key_returns_error(self, monkeypatch):
        monkeypatch.setattr("config.OPENROUTER_API_KEY", "")
        switch = LLMSwitch()
        result = switch.try_generate("test prompt", "system instruction")
        assert "ERROR" in result
        assert "No OpenRouter API key" in result

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_successful_response(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "google/gemini-2.0-flash:free"}

        mock_provider = MagicMock()
        mock_provider.generate_response.return_value = "Success response"
        mock_provider_class.return_value = mock_provider

        switch = LLMSwitch()
        result = switch.try_generate("test prompt", "system instruction")
        assert result == "Success response"

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_model_fallback_on_exception(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "model-1-fail", 2: "model-2-success"}

        mock_provider = MagicMock()
        mock_provider.generate_response.side_effect = [
            Exception("Model failed"),
            "Success from model 2",
        ]
        mock_provider_class.return_value = mock_provider

        switch = LLMSwitch()
        result = switch.try_generate("test prompt", "system instruction")
        assert result == "Success from model 2"

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_insufficient_credits_halts(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "expensive-model"}

        mock_provider = MagicMock()
        mock_provider.generate_response.side_effect = Exception(
            "Error 402: insufficient_credits"
        )
        mock_provider_class.return_value = mock_provider

        switch = LLMSwitch()
        result = switch.try_generate("test prompt", "system instruction")
        assert "CRITICAL ERROR" in result
        assert "no credits" in result.lower()

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_request_too_large_halts(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "small-context-model"}

        mock_provider = MagicMock()
        mock_provider.generate_response.side_effect = Exception(
            "Error 413: Request too large"
        )
        mock_provider_class.return_value = mock_provider

        switch = LLMSwitch()
        result = switch.try_generate("test prompt", "system instruction")
        assert "CRITICAL ERROR" in result
        assert "too large" in result.lower()

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_rate_limit_waits_and_retries(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "rate-limited-model", 2: "working-model"}

        mock_provider = MagicMock()
        mock_provider.generate_response.side_effect = [
            Exception("Rate limit hit. Try again."),
            "Success after rate limit",
        ]
        mock_provider_class.return_value = mock_provider

        switch = LLMSwitch()
        result = switch.try_generate("test prompt", "system instruction")
        assert result == "Success after rate limit"

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_all_models_exhausted(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "model-1", 2: "model-2", 3: "model-3"}

        mock_provider = MagicMock()
        mock_provider.generate_response.side_effect = Exception("All failed")
        mock_provider_class.return_value = mock_provider

        switch = LLMSwitch()
        result = switch.try_generate("test prompt", "system instruction")
        assert "EXHAUSTED" in result or "RATE LIMITED" in result

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_skips_empty_model_names(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "", 2: "valid-model"}

        mock_provider = MagicMock()
        mock_provider.generate_response.return_value = "Success"
        mock_provider_class.return_value = mock_provider

        switch = LLMSwitch()
        result = switch.try_generate("test prompt", "system instruction")
        assert result == "Success"

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_passes_tools_to_provider(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "model-with-tools"}

        mock_provider = MagicMock()
        mock_provider.generate_response.return_value = "Done"
        mock_provider_class.return_value = mock_provider

        tools = [MagicMock(), MagicMock()]
        switch = LLMSwitch(tools_list=tools)
        switch.try_generate("prompt", "system")

        mock_provider.generate_response.assert_called_once_with(
            "prompt", "system", tools=tools
        )


class TestLLMSwitchEdgeCases:
    """Edge case tests for LLMSwitch."""

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_empty_models_dict(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {}

        switch = LLMSwitch()
        result = switch.try_generate("test prompt", "system instruction")
        assert "EXHAUSTED" in result

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_only_empty_model_names(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "", 2: ""}

        switch = LLMSwitch()
        result = switch.try_generate("test prompt", "system instruction")
        assert "EXHAUSTED" in result

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_long_error_message_truncation(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "model"}

        mock_provider = MagicMock()
        long_error = "x" * 500
        mock_provider.generate_response.side_effect = Exception(long_error)
        mock_provider_class.return_value = mock_provider

        switch = LLMSwitch()
        result = switch.try_generate("prompt", "system")
        assert mock_provider_class.called

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_error_message_with_402(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "model"}

        mock_provider = MagicMock()
        mock_provider.generate_response.side_effect = Exception(
            "Error 402 payment required"
        )
        mock_provider_class.return_value = mock_provider

        switch = LLMSwitch()
        result = switch.try_generate("prompt", "system")
        assert "CRITICAL ERROR" in result

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_error_message_with_429(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "model-429", 2: "model-success"}

        mock_provider = MagicMock()
        mock_provider.generate_response.side_effect = [
            Exception("Error 429: Rate limit exceeded"),
            "Success",
        ]
        mock_provider_class.return_value = mock_provider

        switch = LLMSwitch()
        result = switch.try_generate("prompt", "system")
        assert result == "Success"

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_too_large_in_error_message(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "model"}

        mock_provider = MagicMock()
        mock_provider.generate_response.side_effect = Exception(
            "Request too_large for context window"
        )
        mock_provider_class.return_value = mock_provider

        switch = LLMSwitch()
        result = switch.try_generate("prompt", "system")
        assert "CRITICAL ERROR" in result


class TestLLMSwitchStress:
    """Stress tests for LLMSwitch."""

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_many_models_before_success(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {i: f"model-{i}" for i in range(20)}

        mock_provider = MagicMock()
        mock_provider.generate_response.side_effect = [
            Exception(f"Model {i} failed") for i in range(19)
        ] + ["Success at model 20"]
        mock_provider_class.return_value = mock_provider

        switch = LLMSwitch()
        result = switch.try_generate("prompt", "system")
        assert result == "Success at model 20"

    @patch("agent.llm.switch.OpenRouterProvider")
    @patch("agent.llm.switch.config")
    def test_repeated_rate_limits(self, mock_config, mock_provider_class):
        mock_config.OPENROUTER_API_KEY = "test-key"
        mock_config.models = {1: "rate1", 2: "rate2", 3: "rate3", 4: "success"}

        mock_provider = MagicMock()
        mock_provider.generate_response.side_effect = [
            Exception("Rate limit RT"),
            Exception("Rate limit 429"),
            Exception("Rate limit"),
            "Success",
        ]
        mock_provider_class.return_value = mock_provider

        switch = LLMSwitch()
        result = switch.try_generate("prompt", "system")
        assert result == "Success"
