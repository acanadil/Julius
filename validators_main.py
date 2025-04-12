import requests
from game_session import GameSession

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

    validators = [
        "http://validator1:8000/decision",
        "http://validator2:8000/decision",
        "http://validator3:8000/decision"
    ]
    validator_iter = round_robin(validators)
    
    stats = {validator: {"success": 0, "fail": 0} for validator in validators}
    
    partida_num = 0
    while True:
        partida_num += 1
        print(f"\n=== Iniciando partida #{partida_num} ===")
        
        game = GameSession(api_key=API_KEY, player_name="QuackCoders")
        game.start_game()
        
        while True:
            validator_url = next(validator_iter)
            decision = get_validator_decision(validator_url)
            print(f"\nDecision del validador ({validator_url}): {decision}")
            
            result = game.make_decision(decision=decision)
            filtered_result = {k: v for k, v in result.items() if k != "client_data"}
            print("Resultado de decisión:")
            for key, value in filtered_result.items():
                print(f"  {key}: {value}")
            
            if result.get("status") == "gameover":
                stats[validator_url]["fail"] += 1
                print(f"\nGameover alcanzado. El validador {validator_url} ha fallado esta ronda.")
                break
            else:
                stats[validator_url]["success"] += 1
        
        print("\n=== Estadísticas de validadores ===")
        for validator, stat in stats.items():
            total = stat["success"] + stat["fail"]
            if total > 0:
                accuracy = (stat["success"] / total) * 100
            else:
                accuracy = 0
            print(f"{validator} -> Acertado: {stat['success']} | Fallado: {stat['fail']} | % Acierto: {accuracy:.2f}%")
        
        print("\nReiniciando partida...\n")

main()
