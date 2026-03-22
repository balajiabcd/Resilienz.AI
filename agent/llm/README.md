# Agent LLM Drivers 🧠🔄

This subfolder houses the **Resilient Brain** architecture, allowing the agent to switch between multiple AI providers seamlessly.

### File Roles:
- **`base.py`**: The "Contract" (Interface). Ensures any new model we add works the same way.
- **`gemini_provider.py`**: Primary driver for Google Gemini models.
- **`ai_engine.py`**: Fallback driver for 20+ models on OpenRouter.
- **`switch.py`**: **The "Middle-Man"**. This is the traffic controller that prioritizes Gemini and automatically fails-over to the OpenRouter model chain if a request fails.

### Resiliency Logic:
1. Try Gemini first (Free context).
2. If `ResourceExhausted` or Error occurs, switch to OpenRouter.
3. Iterate through `models[0...N]` in `config.py` until the task succeeds.
