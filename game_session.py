import requests
import time

class GameSession:
    def __init__(self, api_key, base_url="https://hackathon-api.mlo.sehlat.io", player_name="QuackCoders"):
        self.api_key = api_key
        self.base_url = base_url
        self.player_name = player_name
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
        self.session_id = None
        self.client_id = None

    def start_game(self):
        url = f"{self.base_url}/game/start"
        payload = {"player_name": self.player_name}
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        print("🎮 Juego iniciado:")
        print(f"  📩 message: {data['message']}")
        print(f"  🆔 session_id: {data['session_id']}")
        print(f"  👤 player_id: {data['player_id']}")
        print(f"  💻 client_id: {data['client_id']}")
        print(f"  🏁 score: {data['score']}")
        
        self.session_id = data["session_id"]
        self.client_id = data["client_id"]

    def make_decision(self, decision="Accept"):

        start_time = time.time()
        
        url = f"{self.base_url}/game/decision"
        payload = {
            "decision": decision,
            "session_id": self.session_id,
            "client_id": self.client_id
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        elapsed = time.time() - start_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        
        data = response.json()
        self.client_id = data.get("client_id", self.client_id)
        return data
