import requests
from game_session import GameSession

def main():
    API_KEY = "BAh5a5BH_zic0UbuFm8pqlHRcc_ctl1DuYmcDl8-yok"
    player_name = "QuackCoders"
    
    last_result = None
    
    while True:
        game = GameSession(api_key=API_KEY, player_name=player_name)
        result = game.start_game()

        last_result = result
        
        while True:
            result = game.make_decision(decision="Accept")
            # print(result['client_data']['description'])
            filtered_result = {k: v for k, v in result.items() if k != "client_data"}
            print(filtered_result)

            post_url = f"http://172.16.206.75:4160/add_files?outcome={result.get("status")}"
            try:
                result_to_post = last_result if last_result is not None else result
                post_response = requests.post(post_url, json=result_to_post)
                print("POST a last_result:", post_response.status_code, post_response.text)
            except Exception as e:
                print("Error al enviar last_result:", e)
            
            last_result = result
            
            if result.get("status") == "gameover":
                break
        

        print("\nReiniciando partida...\n")

if __name__ == "__main__":
    main()