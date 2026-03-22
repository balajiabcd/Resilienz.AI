import config
import requests

def test_free_models():
    print("Testing OpenRouter Models...")
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://resilienz.ai",
        "X-Title": "Resilienz.AI"
    }
    
    for i, model_name in config.models.items():
        if not model_name: continue
        print(f"Testing Model [{i}]: {model_name}...", end=" ", flush=True)
        
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": "hi"}]
        }
        
        try:
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=5)
            if resp.status_code == 200:
                print("✅ OK")
            else:
                print(f"❌ FAILED ({resp.status_code}): {resp.text[:50]}")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_free_models()
