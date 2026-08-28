# models/ollama_client.py
import requests
import json

class OllamaClient:
    def __init__(self, model_name: str = "qwen3:1.7b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url

    def chat(self, messages: list, tools: list = None) -> dict:
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False
        }
        
        if tools:
            payload["tools"] = tools

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract message response from Ollama structure
            if "message" in data:
                return data["message"]
            elif "response" in data:
                return {"role": "assistant", "content": data["response"]}
            else:
                return {"role": "assistant", "content": str(data)}
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API Connection Error: {e}")
        except json.JSONDecodeError:
            raise Exception(f"Failed to parse JSON response from Ollama: {response.text}")