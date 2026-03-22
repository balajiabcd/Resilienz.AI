"""
tests/test_agent_brain.py — Tests for agent/brain.py

Tests RAgent orchestration, initialization, and interaction modes.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestRAgentInit:
    """Unit tests for RAgent initialization."""

    @patch("agent.brain.LLMSwitch")
    def test_initializes_llm_switch(self, mock_switch_class):
        from agent.brain import RAgent

        agent = RAgent()

        assert agent.llm_switch is not None
        mock_switch_class.assert_called_once()

    @patch("agent.brain.LLMSwitch")
    def test_initializes_tools_list(self, mock_switch_class):
        from agent.brain import RAgent

        agent = RAgent()

        assert hasattr(agent, "tools_list")
        assert len(agent.tools_list) == 7

    @patch("agent.brain.LLMSwitch")
    def test_tools_list_contains_all_tools(self, mock_switch_class):
        from agent.brain import RAgent
        from agent import tools

        agent = RAgent()

        expected_tools = [
            tools.get_delayed_orders,
            tools.get_inventory_status,
            tools.get_supplier_info,
            tools.search_global_events,
            tools.calculate_risk_score,
            tools.get_alternative_supplier,
            tools.send_risk_alert,
        ]

        for tool in expected_tools:
            assert tool in agent.tools_list


class TestRunRiskAudit:
    """Tests for run_risk_audit method."""

    @patch("agent.brain.LLMSwitch")
    @patch("agent.brain.auditing.run_hybrid_audit")
    def test_calls_hybrid_audit(self, mock_hybrid, mock_switch_class):
        from agent.brain import RAgent

        mock_hybrid.return_value = "Test report"
        agent = RAgent()

        result = agent.run_risk_audit()

        assert result == "Test report"
        mock_hybrid.assert_called_once()

    @patch("agent.brain.LLMSwitch")
    @patch("agent.brain.auditing.run_hybrid_audit")
    def test_returns_audit_report(self, mock_hybrid, mock_switch_class):
        from agent.brain import RAgent

        expected_report = "# Risk Assessment Report\n- Critical: PO-2024-001"
        mock_hybrid.return_value = expected_report
        agent = RAgent()

        result = agent.run_risk_audit()

        assert result == expected_report

    @patch("agent.brain.LLMSwitch")
    @patch("agent.brain.auditing.run_hybrid_audit")
    def test_handles_hybrid_audit_exception(self, mock_hybrid, mock_switch_class):
        from agent.brain import RAgent

        mock_hybrid.side_effect = Exception("Audit failed")
        agent = RAgent()

        with pytest.raises(Exception):
            agent.run_risk_audit()


class TestAsk:
    """Tests for ask method."""

    @patch("agent.brain.LLMSwitch")
    @patch("agent.brain.prompts")
    def test_calls_llm_switch(self, mock_prompts, mock_switch_class):
        from agent.brain import RAgent

        mock_switch = MagicMock()
        mock_switch.try_generate.return_value = "Test response"
        mock_switch_class.return_value = mock_switch
        mock_prompts.SYSTEM_PROMPT = "You are helpful"

        agent = RAgent()
        result = agent.ask("What is the risk?")

        assert result == "Test response"
        mock_switch.try_generate.assert_called_once()

    @patch("agent.brain.LLMSwitch")
    @patch("agent.brain.prompts")
    def test_passes_question_to_llm(self, mock_prompts, mock_switch_class):
        from agent.brain import RAgent

        mock_switch = MagicMock()
        mock_switch.try_generate.return_value = "Response"
        mock_switch_class.return_value = mock_switch
        mock_prompts.SYSTEM_PROMPT = "System prompt"

        agent = RAgent()
        question = "What orders are delayed?"
        agent.ask(question)

        call_args = mock_switch.try_generate.call_args
        assert question in call_args[1]["prompt"]

    @patch("agent.brain.LLMSwitch")
    @patch("agent.brain.prompts")
    def test_passes_system_prompt(self, mock_prompts, mock_switch_class):
        from agent.brain import RAgent

        mock_switch = MagicMock()
        mock_switch.try_generate.return_value = "Response"
        mock_switch_class.return_value = mock_switch
        expected_prompt = "You are a supply chain expert"
        mock_prompts.SYSTEM_PROMPT = expected_prompt

        agent = RAgent()
        agent.ask("Question")

        call_args = mock_switch.try_generate.call_args
        assert expected_prompt in call_args[1]["system_instruction"]

    @patch("agent.brain.LLMSwitch")
    @patch("agent.brain.prompts")
    def test_passes_tools_to_llm(self, mock_prompts, mock_switch_class):
        from agent.brain import RAgent

        mock_switch = MagicMock()
        mock_switch.try_generate.return_value = "Response"
        mock_switch_class.return_value = mock_switch
        mock_prompts.SYSTEM_PROMPT = "System"

        agent = RAgent()
        agent.ask("Question")

        mock_switch.try_generate.assert_called()
        assert agent.tools_list is not None

    @patch("agent.brain.LLMSwitch")
    @patch("agent.brain.prompts")
    def test_empty_question_handled(self, mock_prompts, mock_switch_class):
        from agent.brain import RAgent

        mock_switch = MagicMock()
        mock_switch.try_generate.return_value = "Response"
        mock_switch_class.return_value = mock_switch
        mock_prompts.SYSTEM_PROMPT = "System"

        agent = RAgent()
        result = agent.ask("")

        assert mock_switch.try_generate.called


class TestRAgentEdgeCases:
    """Edge case tests for RAgent."""

    @patch("agent.brain.LLMSwitch")
    def test_multiple_initializations(self, mock_switch_class):
        from agent.brain import RAgent

        agent1 = RAgent()
        agent2 = RAgent()

        mock_switch_class.assert_called()
        assert agent1.llm_switch is not None
        assert agent2.llm_switch is not None

    @patch("agent.brain.LLMSwitch")
    @patch("agent.brain.auditing.run_hybrid_audit")
    def test_multiple_audit_runs(self, mock_hybrid, mock_switch_class):
        from agent.brain import RAgent

        mock_hybrid.side_effect = ["Report 1", "Report 2", "Report 3"]
        agent = RAgent()

        results = [agent.run_risk_audit() for _ in range(3)]

        assert results[0] == "Report 1"
        assert results[1] == "Report 2"
        assert results[2] == "Report 3"

    @patch("agent.brain.LLMSwitch")
    @patch("agent.brain.prompts")
    def test_multiple_questions(self, mock_prompts, mock_switch_class):
        from agent.brain import RAgent

        mock_switch = MagicMock()
        mock_switch.try_generate.side_effect = ["Answer 1", "Answer 2", "Answer 3"]
        mock_switch_class.return_value = mock_switch
        mock_prompts.SYSTEM_PROMPT = "System"

        agent = RAgent()
        results = [agent.ask(f"Question {i}") for i in range(3)]

        assert results[0] == "Answer 1"
        assert results[1] == "Answer 2"
        assert results[2] == "Answer 3"

    @patch("agent.brain.LLMSwitch")
    def test_llm_switch_has_tools(self, mock_switch_class):
        from agent.brain import RAgent

        agent = RAgent()

        mock_switch_class.assert_called_with(tools_list=agent.tools_list)


class TestRAgentStress:
    """Stress tests for RAgent."""

    @patch("agent.brain.LLMSwitch")
    @patch("agent.brain.prompts")
    def test_many_rapid_questions(self, mock_prompts, mock_switch_class):
        from agent.brain import RAgent

        mock_switch = MagicMock()
        mock_switch.try_generate.return_value = "Response"
        mock_switch_class.return_value = mock_switch
        mock_prompts.SYSTEM_PROMPT = "System"

        agent = RAgent()

        for i in range(100):
            result = agent.ask(f"Question number {i}")
            assert result == "Response"

        assert mock_switch.try_generate.call_count == 100

    @patch("agent.brain.LLMSwitch")
    @patch("agent.brain.auditing.run_hybrid_audit")
    def test_many_audit_calls(self, mock_hybrid, mock_switch_class):
        from agent.brain import RAgent

        mock_hybrid.return_value = "Report"
        agent = RAgent()

        for _ in range(100):
            result = agent.run_risk_audit()

        assert mock_hybrid.call_count == 100

    @patch("agent.brain.LLMSwitch")
    def test_large_tools_list(self, mock_switch_class):
        from agent.brain import RAgent

        agent = RAgent()

        assert len(agent.tools_list) == 7

        large_list = agent.tools_list * 10
        assert len(large_list) == 70
