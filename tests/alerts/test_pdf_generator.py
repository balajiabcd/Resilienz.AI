"""
tests/alerts/test_pdf_generator.py — Tests for alerts/pdf_generator.py

Tests PDF report generation and RiskReport class.
"""

import pytest
from unittest.mock import MagicMock, patch
from alerts.pdf_generator import RiskReport


class TestRiskReportInit:
    """Unit tests for RiskReport class."""

    def test_creates_pdf_instance(self):
        pdf = RiskReport()
        assert pdf is not None

    def test_pdf_has_header_method(self):
        pdf = RiskReport()
        assert hasattr(pdf, "header")
        assert callable(pdf.header)

    def test_pdf_has_footer_method(self):
        pdf = RiskReport()
        assert hasattr(pdf, "footer")
        assert callable(pdf.footer)

    def test_pdf_has_add_page(self):
        pdf = RiskReport()
        assert hasattr(pdf, "add_page")
        assert callable(pdf.add_page)

    def test_pdf_has_output(self):
        pdf = RiskReport()
        assert hasattr(pdf, "output")
        assert callable(pdf.output)

    def test_pdf_has_set_font(self):
        pdf = RiskReport()
        assert hasattr(pdf, "set_font")
        assert callable(pdf.set_font)

    def test_pdf_has_cell(self):
        pdf = RiskReport()
        assert hasattr(pdf, "cell")
        assert callable(pdf.cell)

    def test_pdf_has_multi_cell(self):
        pdf = RiskReport()
        assert hasattr(pdf, "multi_cell")
        assert callable(pdf.multi_cell)

    def test_pdf_has_set_text_color(self):
        pdf = RiskReport()
        assert hasattr(pdf, "set_text_color")
        assert callable(pdf.set_text_color)

    def test_pdf_has_set_fill_color(self):
        pdf = RiskReport()
        assert hasattr(pdf, "set_fill_color")
        assert callable(pdf.set_fill_color)

    def test_pdf_has_ln(self):
        pdf = RiskReport()
        assert hasattr(pdf, "ln")
        assert callable(pdf.ln)

    def test_pdf_default_page_count(self):
        pdf = RiskReport()
        assert pdf.page == 0

    def test_pdf_accepts_font_parameters(self):
        pdf = RiskReport()
        pdf.set_font("helvetica", "", 12)
        assert pdf.font_size_pt == 12

    def test_pdf_text_color_default(self):
        pdf = RiskReport()
        assert pdf.text_color is not None

    def test_pdf_fill_color_default(self):
        pdf = RiskReport()
        assert pdf.fill_color is not None

    def test_pdf_has_line_width(self):
        pdf = RiskReport()
        assert hasattr(pdf, "line_width")
        assert pdf.line_width >= 0
