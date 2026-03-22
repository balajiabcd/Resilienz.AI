"""
tests/agent/llm/test_utils.py — Tests for agent/llm/utils.py

Tests token estimation, message counting, and content truncation.
"""

import pytest
from agent.llm.utils import estimate_tokens, count_messages_tokens, truncate_content


class TestEstimateTokens:
    """Unit tests for estimate_tokens function."""

    def test_empty_string(self):
        assert estimate_tokens("") == 0

    def test_none_input_handled(self):
        result = estimate_tokens(None)
        assert result == 0

    def test_exact_four_characters(self):
        assert estimate_tokens("test") == 1

    def test_multiple_of_four(self):
        assert estimate_tokens("a" * 8) == 2

    def test_remainder_chars(self):
        assert estimate_tokens("a" * 10) == 2

    def test_long_text(self):
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100
        expected = len(text) // 4
        assert estimate_tokens(text) == expected

    def test_german_text(self):
        text = "Lieferverzögerung due to Hamburg Port Streik"
        result = estimate_tokens(text)
        assert result >= 5
        assert result == len(text) // 4


class TestCountMessagesTokens:
    """Unit tests for count_messages_tokens function."""

    def test_empty_messages(self):
        assert count_messages_tokens([]) == 0

    def test_single_message_string_content(self):
        messages = [{"role": "user", "content": "test"}]
        result = count_messages_tokens(messages)
        assert result > 0

    def test_single_message_empty_content(self):
        messages = [{"role": "user", "content": ""}]
        result = count_messages_tokens(messages)
        assert result == 10

    def test_multiple_messages(self):
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        result = count_messages_tokens(messages)
        assert result > 30

    def test_multimodal_content(self):
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "First part"},
                    {"type": "text", "text": "Second part"},
                ],
            }
        ]
        result = count_messages_tokens(messages)
        assert result >= 10

    def test_message_without_content(self):
        messages = [{"role": "system"}]
        result = count_messages_tokens(messages)
        assert result == 10

    def test_message_with_missing_role(self):
        messages = [{"content": "test"}]
        result = count_messages_tokens(messages)
        assert result >= 10

    def test_large_message_volume(self):
        messages = [{"role": "user", "content": "x" * 1000} for _ in range(50)]
        result = count_messages_tokens(messages)
        assert result > 0


class TestTruncateContent:
    """Unit tests for truncate_content function."""

    def test_below_max_chars(self):
        text = "Short text"
        result = truncate_content(text, 5000)
        assert result == text

    def test_exactly_max_chars(self):
        text = "a" * 5000
        result = truncate_content(text, 5000)
        assert result == text

    def test_above_max_chars_adds_truncation_marker(self):
        text = "a" * 10000
        result = truncate_content(text, 5000)
        assert "[... TRUNCATED" in result
        assert len(result) < len(text)

    def test_truncation_preserves_start_and_end(self):
        start = "BEGINNING"
        end = "END"
        text = start + "x" * 10000 + end
        result = truncate_content(text, 5000)
        assert result.startswith(start)
        assert result.endswith(end)

    def test_custom_max_chars(self):
        text = "a" * 200
        result = truncate_content(text, 100)
        assert "[... TRUNCATED" in result

    def test_default_max_chars(self):
        text = "a" * 6000
        result = truncate_content(text)
        assert "[... TRUNCATED" in result

    def test_very_short_max_chars(self):
        text = "This is a longer text"
        result = truncate_content(text, 5)
        assert "[... TRUNCATED" in result

    def test_zero_max_chars(self):
        text = "Hello"
        result = truncate_content(text, 0)
        assert "[... TRUNCATED" in result

    def test_unicode_content(self):
        text = "Hallo Welt 🌍 " * 1000
        result = truncate_content(text, 100)
        assert "[... TRUNCATED" in result


class TestEstimateTokensEdgeCases:
    """Edge case tests for estimate_tokens."""

    def test_single_character(self):
        assert estimate_tokens("a") == 0

    def test_whitespace_only(self):
        assert estimate_tokens("   \n\t  ") == 1

    def test_special_characters(self):
        text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        result = estimate_tokens(text)
        assert result >= 5

    def test_newlines_and_tabs(self):
        text = "line1\nline2\nline3\n"
        result = estimate_tokens(text)
        assert result >= 4


class TestCountMessagesTokensEdgeCases:
    """Edge case tests for count_messages_tokens."""

    def test_none_messages(self):
        with pytest.raises(TypeError):
            count_messages_tokens(None)

    def test_message_with_none_content(self):
        messages = [{"role": "user", "content": None}]
        result = count_messages_tokens(messages)
        assert result >= 10

    def test_nested_list_content(self):
        messages = [
            {
                "role": "user",
                "content": [{"type": "image", "data": "fake"}, {"text": "actual text"}],
            }
        ]
        result = count_messages_tokens(messages)
        assert result > 10

    def test_tool_call_format(self):
        messages = [
            {
                "role": "tool",
                "tool_call_id": "call_123",
                "name": "get_data",
                "content": "Result data here",
            }
        ]
        result = count_messages_tokens(messages)
        assert result >= 10


class TestTruncateContentEdgeCases:
    """Edge case tests for truncate_content."""

    def test_unicode_beyond_max(self):
        text = "α" * 10000
        result = truncate_content(text, 5000)
        assert "[... TRUNCATED" in result

    def test_empty_string_above_max(self):
        text = ""
        result = truncate_content(text, 0)
        assert result == text

    def test_exactly_max_chars_minus_one(self):
        text = "a" * 4999
        result = truncate_content(text, 5000)
        assert result == text

    def test_exactly_max_chars_plus_one(self):
        text = "a" * 5001
        result = truncate_content(text, 5000)
        assert "[... TRUNCATED" in result


class TestTruncateContentStress:
    """Stress tests for truncate_content."""

    def test_very_large_text(self):
        text = "x" * 100000
        result = truncate_content(text, 5000)
        assert len(result) < 10000

    def test_many_small_truncations(self):
        for size in [100, 500, 1000, 2000, 4000, 5000, 6000]:
            text = "y" * size
            result = truncate_content(text, 3000)
            if size > 3000:
                assert "[... TRUNCATED" in result

    def test_repeated_truncation_calls(self):
        text = "z" * 10000
        for _ in range(100):
            result = truncate_content(text, 5000)
            assert "[... TRUNCATED" in result
