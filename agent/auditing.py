"""
auditing.py — Hybrid Risk Audit (Python + LLM)

This script implements an ultra-granular, token-efficient audit by:
1. Using Python to fetch data (Zero Tokens).
2. Using LLMs only for reasoning/summarization (Tiny Context).
3. Supporting models with < 1K context windows via decomposition.
"""

import config
from agent import tools
from agent.llm.switch import LLMSwitch
from agent.llm import utils
import pandas as pd
import io
import re


def _emit_thought(step: str, detail: str = ""):
    """Emits a thought event via SSE if running within the Flask app context."""
    try:
        from api.app import emit_thought as _emit

        _emit(step, detail)
    except Exception:
        pass


# ─── Granular Prompts (Self-Contained) ───────────────────────────────────────
# ... (rest of prompts)


PHASE_1_INVESTIGATOR_PROMPT = """
You are a Supply Chain Investigator. Analyze the following data for PO ID: {po_id}.

### DATA:
- **Inventory/Supplier:** {data_internal}
- **Risk Score/Factors:** {data_risk}
- **External Events:** {data_external}

### TASK:
Summarize the risk for this specific order in EXACTLY 2 sentences. 
Focus on visibility—explain WHY it is at risk based on the data.
"""

PHASE_2_REPORTER_PROMPT = """
You are the Lead Resilience Officer. Below are the individual risk summaries for our current delayed orders.

### INDIVIDUAL SUMMARIES:
{summaries}

### TASK:
Combine these into a single, high-level Executive Summary report using Professional Markdown.
1. Include a summary table of the most critical orders.
2. Provide a 1-paragraph synthesis of the overall supply chain health.
3. suggest immediate next steps.
"""

# ─── Hybrid Audit Logic ──────────────────────────────────────────────────────


def extract_po_ids(markdown_table: str) -> list:
    """Extracts PO IDs from the markdown table returned by tools."""
    # Look for patterns like PO-2024-XXX or similar
    return re.findall(r"PO-\d{4}-\d+", markdown_table)


def run_hybrid_audit():
    """Executes the 7-phase hybrid audit."""
    print("🚀 [HYBRID_AUDIT] Starting Granular Resilience Audit...")
    _emit_thought("Detection", "Starting risk audit...")

    try:
        llm = LLMSwitch()

        # PHASE 1: Detection (Python)
        print("🔍 Phase 1: Detecting delayed orders via Python...")
        delayed_orders_md = tools.get_delayed_orders(min_delay_days=1)
        po_ids = list(set(extract_po_ids(delayed_orders_md)))
        _emit_thought("Detection", f"Found {len(po_ids)} delayed orders")

        if not po_ids:
            print("✅ No delayed orders found. Supply chain is healthy.")
            _emit_thought("Done", "No risks found.")
            return "No risks detected."

        print(f"📦 Found {len(po_ids)} targets for analysis: {po_ids}")

        # PHASE 2-4: Data Aggregation & Priority Filtering (Python Only)
        print("🧠 Phase 2-4: Aggregating facts and filtering by risk score...")
        _emit_thought("Aggregation", f"Collecting data for {len(po_ids)} targets")
        po_investigations = []

        for po_id in po_ids:
            conn = tools.get_db_connection()
            po_row = conn.execute(
                "SELECT part_number, supplier_id FROM purchase_orders WHERE po_id = ?",
                [po_id],
            ).fetchone()
            conn.close()

            if not po_row:
                continue
            part_number, supplier_id = po_row["part_number"], po_row["supplier_id"]

            try:
                data_internal = (
                    tools.get_inventory_status(part_number)
                    + "\n"
                    + tools.get_supplier_info(supplier_id)
                )
                data_risk_report = tools.calculate_risk_score(po_id)
                data_external = (
                    tools.search_global_events(
                        f"disruptions for {part_number} {supplier_id}", n_results=1
                    )
                    or "No news found."
                )

                score_match = re.search(r"\*\*SCORE:\*\*\s+(\d+)", data_risk_report)
                score = int(score_match.group(1)) if score_match else 0

                if score > 5:
                    po_investigations.append(
                        {
                            "po_id": po_id,
                            "score": score,
                            "data_internal": data_internal,
                            "data_risk": data_risk_report,
                            "data_external": data_external,
                        }
                    )
            except Exception as e:
                print(f"⚠️ Error gathering data for {po_id}: {str(e)}")
                continue

        # Sort by score descending and take top 5
        po_investigations = sorted(
            po_investigations, key=lambda x: x["score"], reverse=True
        )[:5]
        print(f"🎯 Focused on top {len(po_investigations)} high-risk targets.")

        # PHASE 5: Individual Investigation (Tiny LLM Call)
        sub_summaries = []
        total = len(po_investigations)
        for i, inv in enumerate(po_investigations):
            po_id = inv["po_id"]
            print(
                f"💡 Phase 5: Generating tiny insight for {po_id} (Score: {inv['score']})..."
            )
            _emit_thought("Investigation", f"Analyzing ({i + 1}/{total}) — {po_id}")

            prompt = PHASE_1_INVESTIGATOR_PROMPT.format(
                po_id=po_id,
                data_internal=utils.truncate_content(inv["data_internal"], 1600),
                data_risk=utils.truncate_content(inv["data_risk"], 1600),
                data_external=utils.truncate_content(inv["data_external"], 800),
            )

            summary = llm.try_generate(
                prompt=prompt, system_instruction="You are a tiny analyst."
            )
            sub_summaries.append(f"### {po_id} (Risk Score: {inv['score']})\n{summary}")

        if not sub_summaries:
            print("✅ No critical risks require LLM reasoning.")
            _emit_thought("Done", "No critical risks found.")
            return "Supply chain is stable. No critical risks found."

        # PHASE 6: Synthesis (Final LLM Call)
        print("\n📝 Phase 6: Synthesizing final report...")
        _emit_thought("Synthesis", "Generating final executive report")
        final_prompt = PHASE_2_REPORTER_PROMPT.format(
            summaries="\n\n".join(sub_summaries)
        )

        final_report = llm.try_generate(
            prompt=final_prompt,
            system_instruction="You are a senior reporter. Use Markdown.",
        )

        _emit_thought(
            "Done", f"Report complete. {len(sub_summaries)} risks identified."
        )
        return final_report

    except Exception as e:
        print(f"❌ Audit failed: {e}")
        _emit_thought("Error", str(e))
        raise


if __name__ == "__main__":
    report = run_hybrid_audit()
    print("\n" + "=" * 60)
    print(" HYBRID RESILIENT RISK REPORT")
    print("=" * 60)
    print(report)
    print("=" * 60)
