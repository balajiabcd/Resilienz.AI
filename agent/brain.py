"""
agent/brain.py — R_agent AI Orchestration (Now with LLM Switch!)

This file now uses the LLMSwitch to handle resilient reasoning.
"""

import os
import sys
from dotenv import load_dotenv

# ── Import Project Files ──────────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from agent import tools, prompts
from agent.llm.switch import LLMSwitch
import auditing  # Import the new hybrid logic

class RAgent:
    """The core AI Agent class that orchestrates reasoning and tool-use."""

    def __init__(self):
        # Tools are the "Hands" of the agent
        self.tools_list = [
            tools.get_delayed_orders,
            tools.get_inventory_status,
            tools.get_supplier_info,
            tools.search_global_events,
            tools.calculate_risk_score,
            tools.get_alternative_supplier,
            tools.send_risk_alert
        ]

        # The Switch is the "Logic Hub" between models
        self.llm_switch = LLMSwitch(tools_list=self.tools_list)

    def run_risk_audit(self):
        """Triggers the agent's autonomous task using the new Hybrid Logic."""
        print("🧠 R_agent is starting a Hybrid Resilient Risk Audit...")
        
        # We now use the specialized auditing module we built
        report = auditing.run_hybrid_audit()
        return report

    def ask(self, question: str):
        """Allows the user to ask R_agent specific questions."""
        response = self.llm_switch.try_generate(
            prompt=question,
            system_instruction=prompts.SYSTEM_PROMPT
        )
        return response

# ── CLI Entry Point (for manual verification) ──────────────────────────────────
if __name__ == "__main__":
    agent = RAgent()
    report = agent.run_risk_audit()
    
    print("\n" + "="*60)
    print(" R_AGENT RISK REPORT (RESILIENT BRAIN)")
    print("="*60)
    print(report)
    print("="*60)
