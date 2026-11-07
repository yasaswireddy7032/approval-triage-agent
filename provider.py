"""Small Ollama adapter: explicit local endpoint, bounded response and timeout."""
import json
import urllib.request

class Ollama:
    def __init__(self, model, url="http://127.0.0.1:11434/api/chat"):
        self.model, self.url = model, url

    def next(self, messages):
        body = json.dumps({"model": self.model, "messages": messages,
                           "stream": False, "format": "json",
                           "options": {"temperature": 0}}).encode()
        req = urllib.request.Request(self.url, data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValueError("Model response exceeds limit")
        data = json.loads(raw)
        decision = json.loads(data["message"]["content"])
        if not isinstance(decision, dict):
            raise ValueError("Expected a JSON decision object")
        return decision

class Scripted:
    """Deterministic fixture for tests and demos. Does not invoke a model."""
    def __init__(self, decisions):
        self.decisions = iter(decisions)
    def next(self, messages):
        return next(self.decisions)
