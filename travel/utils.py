import requests

def generate_itinerary(prompt):
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {
        "Authorization": f"Bearer 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"
    }
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 500}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        return "Error generating itinerary."
