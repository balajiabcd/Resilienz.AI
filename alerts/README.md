# Alerts Folder — Actions & Notifications 📬🔔

The `alerts/` directory contains the logic that bridges the gap between the AI's "thoughts" and professional business "actions."

## 📄 Key Components

| File | Purpose |
|------|---------|
| `notifier.py` | **The Action Hub**: Logic for automated SMTP email sending and generating professional PDF risk reports using `fpdf2`. |

## 🌟 Peak Demo: Decision Thresholds
When **R_agent** concludes its risk audit, it evaluates the final scores.
- **Critical Threshold**: Any order with a calculated score **> 70** automatically triggers an executive PDF report and an email notification to the procurement manager.
- **Mitigation Action**: The notifier includes "Plan B" (alternative suppliers) directly in the generated report.

---

*For alert-specific details, see the [8_development_journal.md](../documentation/8_development_journal.md).*
