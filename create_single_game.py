import saving
import requests

api_key = "BAh5a5BH_zic0UbuFm8pqlHRcc_ctl1DuYmcDl8-yok"
base_url = "https://hackathon-api.mlo.sehlat.io"
player_name = "QuackCoders"

headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "X-API-Key": api_key
}

url = f"{base_url}/game/start"
payload = {"player_name": player_name}

response = requests.post(url, headers=headers, json=payload)

saving.cast_files(response.json(), "gameover")