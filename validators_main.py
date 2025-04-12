from game_session import GameSession
import requests

def get_validator_decision(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        decision = response.json().get("decision")
        if decision in ["Accept", "Reject"]:
            return decision
    except Exception as e:
        print(f"Error al consultar el validador en {url}: {e}")
    return "Accept"

def round_robin(validators):
    while True:
        for validator in validators:
            yield validator

def main():
    API_KEY = "BAh5a5BH_zic0UbuFm8pqlHRcc_ctl1DuYmcDl8-yok" 
    game = GameSession(api_key=API_KEY, player_name="QuackCoders")

    game.start_game()
    
    validators = [
        "http://validator1:8000/decision",
        "http://validator2:8000/decision",
        "http://validator3:8000/decision"
    ]
    
    validator_iter = round_robin(validators)

    while True:
        validator_url = next(validator_iter)
        decision = get_validator_decision(validator_url)
        print(f"Decision del validador ({validator_url}): {decision}")
        
        result = game.make_decision(decision=decision)

        filtered_result = {k: v for k, v in result.items() if k != "client_data"}
        print(filtered_result)
        if result.get("status") == "gameover":
            break

main()