"""
alerts/pdf_generator.py — Professional Risk Reports

Templates for generating high-quality PDF summaries for R_agent.
"""

from fpdf import FPDF
import datetime
import os

class RiskReport(FPDF):
    """Custom PDF template for Resilienz.AI reports."""

    def header(self):
        # Logo placeholder (can be replaced with actual image later)
        self.set_font("Arial", "B", 18)
        self.set_text_color(20, 40, 100)
        self.cell(0, 10, "Resilienz.AI — Risk Audit Report", 0, 1, "C")
        self.set_font("Arial", "I", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

def generate_risk_report(po_id, risk_score, summary, suggestions):
    """Creates a professional PDF risk report."""
    
    pdf = RiskReport()
    pdf.add_page()
    
    # 1. Main Severity Section
    color = (200, 0, 0) if risk_score >= 70 else (200, 100, 0) # Red for high, Orange for med
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(*color)
    pdf.cell(0, 10, f"PURCHASE ORDER: {po_id}", 1, 1, "L")
    pdf.cell(0, 10, f"RESILIENCE SCORE: {risk_score} / 100", 1, 1, "L")
    pdf.ln(5)

    # 2. Executive Summary
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Executive Summary", 0, 1)
    
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, summary)
    pdf.ln(10)

    # 3. Recommended Actions
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(20, 100, 20)
    pdf.cell(0, 10, "Recommended Mitigation Actions", 0, 1)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 7, suggestions)

    # 4. Save the File
    out_dir = "reports"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    filename = f"{out_dir}/{po_id}_risk_audit.pdf"
    pdf.output(filename)
    return os.path.abspath(filename)

# ── SELF TEST (Optional) ──────────────────────────────────────────────────────
if __name__ == "__main__":
    path = generate_risk_report(
        po_id="PO-2024-001",
        risk_score=75,
        summary="Impact of Hamburg Port Strike leading to a delay of 8 days. Inventory buffer is only 2.5 days.",
        suggestions="1. Switch to Alternative Supplier (SUP-DE-001).\n2. Contact logistics for air-freight quote."
    )
    print(f"✅ Sample PDF generated at: {path}")
