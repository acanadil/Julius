from game_session import GameSession

def main():
    API_KEY = "BAh5a5BH_zic0UbuFm8pqlHRcc_ctl1DuYmcDl8-yok" 
    game = GameSession(api_key=API_KEY, player_name="QuackCoders")

    game.start_game()

    while True:
        result = game.make_decision(decision="Accept")
        filtered_result = {k: v for k, v in result.items() if k != "client_data"}
        print(filtered_result)
        if result.get("status") == "gameover":
            break

if __name__ == "__main__":
    main()