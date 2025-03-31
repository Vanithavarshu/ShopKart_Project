import requests
from django.conf import settings

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"  # Example URL (Check DeepSeek Docs)

def deepseek_chatbot(message):
    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-llm",  # Change based on DeepSeek documentation
        "messages": [{"role": "user", "content": message}]
    }
    
    response = requests.post(DEEPSEEK_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Sorry, I couldn't process your request right now."
