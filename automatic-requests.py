# import requests

# url = "https://hackathon-api.mlo.sehlat.io/game/start"
# headers = {
#     "accept": "application/json",
#     "Content-Type": "application/json",
#     "X-API-Key": "BAh5a5BH_zic0UbuFm8pqlHRcc_ctl1DuYmcDl8-yok"  # Reemplaza con tu API key real
# }
# data = {
#     "player_name": "QuackCoders"
# }

# response = requests.post(url, headers=headers, json=data)

# # Mostrar la respuesta
# print("Status Code:", response.status_code)
# print("Response JSON:", response.json())



import requests
import time

API_KEY = "BAh5a5BH_zic0UbuFm8pqlHRcc_ctl1DuYmcDl8-yok"  # Reemplaza con tu API key real
BASE_URL = "https://hackathon-api.mlo.sehlat.io"

HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def start_game(player_name="QuackCoders"):
    url = f"{BASE_URL}/game/start"
    payload = {"player_name": player_name}
    
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    
    data = response.json()

    print("🎮 Juego iniciado:")
    print(f"  📩 message: {data['message']}")
    print(f"  🆔 session_id: {data['session_id']}")
    print(f"  👤 player_id: {data['player_id']}")
    print(f"  💻 client_id: {data['client_id']}")
    print(f"  🏁 score: {data['score']}")

    return data["session_id"], data["client_id"]

def make_decision(session_id, client_id, decision="Accept"):
    start_time = time.time()

    url = f"{BASE_URL}/game/decision"
    payload = {
        "decision": decision,
        "session_id": session_id,
        "client_id": client_id
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    # response.raise_for_status()
    
    elapsed = time.time() - start_time
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)

    return response.json()

def main():
    session_id, client_id = start_game()
    
    while True:
        result = make_decision(session_id, client_id)
        client_id = result['client_id']
        # Filtramos client_data si existe
        filtered_result = {k: v for k, v in result.items() if k != "client_data"}
        
        print("📦 Resultado de decisión:")
        for key, value in filtered_result.items():
            print(f"  {key}: {value}")
        
        if result["status"] == "gameover":
            print("💀 El juego ha terminado.")
            break

if __name__ == "__main__":
    main()