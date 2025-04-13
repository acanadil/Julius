import requests
from game_session import GameSession
import saving
import json
import threading
import time
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Variables globales para guardar históricos
historial_partidas = []
historial_partida_actual = []

def get_validator_decision(url, result_to_post):
    # try:
    #     # print(type(result_to_post))
    #     result_to_post = saving.cast_files(result_to_post, None)
    #     response = requests.post(url, json=result_to_post)
    #     response.raise_for_status()
    #     response_data = response.json()
    #     decision = response_data['decision']
    #     if decision in ["Accept", "Reject"]:
    #         return decision
    # except Exception as e:
    #     print(f"Error al consultar el validador en {url}: {e}")
    return "Accept"

def round_robin(validators):
    while True:
        for validator in validators:
            yield validator

def game_loop():
    global historial_partidas, historial_partida_actual
    API_KEY = "BAh5a5BH_zic0UbuFm8pqlHRcc_ctl1DuYmcDl8-yok"

    validators = [
        "http://localhost:5000/evaluate",
        # "http://validator2:8000/decision",
        # "http://validator3:8000/decision"
    ]
    validator_iter = round_robin(validators)
    
    stats = {validator: {"success": 0, "fail": 0} for validator in validators}
    
    partida_num = 0
    # Bucle principal de partidas
    while True:
        partida_num += 1
        print(f"\n=== Iniciando partida #{partida_num} ===")
        
        # Inicializamos el historial de la partida actual
        historial_partida_actual = []
        
        game = GameSession(api_key=API_KEY, player_name="QuackCoders")
        result = game.start_game()
        next_client_info = saving.cast_files(result, None)
        client_info = next_client_info
        
        while True:
            validator_url = next(validator_iter)

            decision = get_validator_decision(validator_url, result)
            print(f"\nDecision del validador ({validator_url}): {decision}")
            
            result = game.make_decision(decision=decision)
            if result.get("status") != "gameover":
                next_client_info = saving.cast_files(result, None)

            # Se construye el registro a agregar. En caso de que el status sea "gameover",
            # no se espera disponer de datos de client_info.
            registro = {
                "decision": decision,
                "client_info": client_info['passport'] if result.get("status") != "gameover" else None,
                "status": result.get("status")
            }
            print(registro)
            historial_partida_actual.append(registro)
            
            if result.get("status") == "gameover":
                stats[validator_url]["fail"] += 1
                print(f"\nGameover alcanzado. El validador {validator_url} ha fallado esta ronda.")
                break
            else:
                stats[validator_url]["success"] += 1
                # Actualizamos client_info con la siguiente información
                client_info = next_client_info
            
            time.sleep(2)

        # Guardamos el historial de la partida actual en el historial global de partidas.
        historial_partidas.append(historial_partida_actual)
        
        # Mostrar el historial de la partida actual
        print("\n=== Historial de decisiones de la partida ===")
        for idx, registro in enumerate(historial_partida_actual):
            print(f"Paso {idx+1}:")
            print(f"  Decision: {registro['decision']}")
            print(f"  Client_info: {registro['client_info']}")
            print(f"  Status: {registro['status']}")
        
        # Mostrar las estadísticas de validadores
        print("\n=== Estadísticas de validadores ===")
        for validator, stat in stats.items():
            total = stat["success"] + stat["fail"]
            accuracy = (stat["success"] / total) * 100 if total > 0 else 0
            print(f"{validator} -> Acertado: {stat['success']} | Fallado: {stat['fail']} | % Acierto: {accuracy:.2f}%")
        
        # Opcional: mostrar el historial global de partidas
        print("\n=== Historial global de partidas ===")
        for p_index, partida_hist in enumerate(historial_partidas, start=1):
            print(f"\nPartida #{p_index}:")
            for idx, registro in enumerate(partida_hist):
                print(f"  Paso {idx+1}: Decision: {registro['decision']}, Client_info: {registro['client_info']}, Status: {registro['status']}")
        
        print("\nReiniciando partida...\n")
        # Se espera un tiempo antes de iniciar la siguiente partida (ajustar o eliminar según se desee)
        time.sleep(2)

# Endpoint GET que devuelve el historial de la partida actual y el historial global de partidas.
@app.route('/historial', methods=['GET'])
def get_historial():
    return jsonify({
        "historial_partida_actual": historial_partida_actual,
        "historial_partidas": historial_partidas
    })
    # return jsonify({
    #     "historial_partida_actual": [{'decision':'Accept','client_info':{'document_type': 'PASSPORT', 'country': 'RÉPUBLIQUE FRANÇAISE / French Republic', 'code': 'FRA', 'passport_number': 'RF6881702', 'surname': 'MARCHAND', 'given_names': 'BONNET', 'birth_date': '14-Nov-1998', 'citizenship': 'French/FRANÇAISE', 'sex': 'M', 'issue_date': '16-Apr-2018', 'expiry_date': '15-Apr-2028', 'signature': 'Bonnet Marchand'},'status':'active'},
    #                                  {'decision':'Accept','client_info':{'document_type': 'PASSPORT', 'country': 'REPUBLICA ITALIANA / Italian Republic', 'code': 'ITA', 'passport_number': 'OP8747894', 'surname': 'BIANCHI', 'given_names': 'MATTEO FILIPPO', 'birth_date': '31-Dec-1972', 'citizenship': 'Italian/ITALIANA', 'sex': 'M', 'issue_date': '21-Oct-2024', 'expiry_date': '20-Oct-2034', 'signature': 'Matteo Bianchi'},'status':'active'},
    #                                  {'decision':'Accept','client_info':{'document_type': 'PASSPORT', 'country': 'ÖSTERREICH / Republic of Austria', 'code': 'AUT', 'passport_number': 'HR0871328', 'surname': 'HUBER', 'given_names': 'LEA RENATE', 'birth_date': '13-Mar-1986', 'citizenship': 'Austrian/ÖSTERREICH', 'sex': 'F', 'issue_date': '30-Sep-2022', 'expiry_date': '29-Sep-2032', 'signature': 'Lea Huber', 'machine_readable_zone': 'P<AUTHUBER<<LEA<RENATE<<<<<<<<<<<<<<<<<<HR0871328AUT860313<<<<<<<<<<<<<<<0'},'status':'active'},
    #                                  {'decision':'Accept','client_info':{'document_type': 'PASSPORT', 'country': 'BUNDESREPUBLIK DEUTSCHLAND / Federal Republic of Germany', 'code': 'DEU', 'passport_number': 'PM6996746', 'surname': 'NEUMANN', 'given_names': 'KATHARINA ANNA', 'birth_date': '18-Apr-1986', 'citizenship': 'German/DEUTSCH', 'sex': 'F', 'issue_date': '01-Feb-2024', 'expiry_date': '31-Jan-2034', 'signature': 'Katharina Neumann'},'status':'active'}],
    #     "historial_partidas": [
    #         [
    #             {
    #                 "client_info": {
    #                     "birth_date": "03-Jun-1969",
    #                     "citizenship": "Polish/POLSKIE",
    #                     "code": "POL",
    #                     "country": "RZECZPOSPOLITA POLSKA / Republic of Poland",
    #                     "document_type": "PASSPORT",
    #                     "expiry_date": "25-Sep-2027",
    #                     "given_names": "ALEKSANDRA IWONA",
    #                     "issue_date": "26-Sep-2017",
    #                     "passport_number": "BG0267742",
    #                     "sex": "F",
    #                     "signature": "Aleksandra Nowak",
    #                     "surname": "NOWAK"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "17-Jun-1980",
    #                     "citizenship": "Portuguese/PORTUGUESA",
    #                     "code": "PRT",
    #                     "country": "REPUBLICA PORTUGUESA / Portuguese Republic",
    #                     "document_type": "PASSPORT / PASSAPORTE",
    #                     "expiry_date": "02-Jun-2026",
    #                     "given_names": "MARTIM NUNO",
    #                     "issue_date": "03-Jun-2021",
    #                     "passport_number": "HA6458699",
    #                     "sex": "M",
    #                     "signature": "Martim Tavares",
    #                     "surname": "TAVARES"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "1985-08-24",
    #                     "citizenship": "Danish",
    #                     "code": "DNK",
    #                     "country": "Denmark",
    #                     "expiry_date": "2027-07-09",
    #                     "given_names": "KATRINE ALMA",
    #                     "issue_date": "2017-07-10",
    #                     "passport_number": "GZ7883724",
    #                     "sex": "F",
    #                     "surname": "PEDERSEN"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "03-Nov-1959",
    #                     "citizenship": "Hungarian",
    #                     "code": "HUN",
    #                     "country": "Hungary",
    #                     "expiry_date": "22-Aug-2029",
    #                     "given_names": "MAJA ZSÓFIA",
    #                     "issue_date": "23-Aug-2019",
    #                     "passport_number": "AZ6522105",
    #                     "sex": "F",
    #                     "signature": "Maja Szabó",
    #                     "surname": "SZABÓ",
    #                     "type": "PASSPORT"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "07-Oct-1974",
    #                     "citizenship": "Finnish/SUOMALAINEN",
    #                     "code": "FIN",
    #                     "document": {
    #                         "country": "SUOMEN TASAVALTA / Republic of Finland",
    #                         "type": "PASSPORT"
    #                     },
    #                     "expiry_date": "01-May-2033",
    #                     "given_names": "VEETI OSKARI",
    #                     "issue_date": "02-May-2023",
    #                     "mrz": "P<FINPAANANEN<<VEETI<OSKARIOQ7934282FIN741007",
    #                     "passport_number": "OQ7934282",
    #                     "sex": "M",
    #                     "signature": "Veeti Paananen",
    #                     "surname": "PAANANEN"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "02-Oct-1975",
    #                     "citizenship": "Czech/ČESKÁ REPUBLIKA",
    #                     "code": "CZE",
    #                     "country": "ČESKÁ REPUBLIKA / Czech Republic",
    #                     "document_type": "PASSPORT / CESTOVNÍ PAS",
    #                     "expiry_date": "28-May-2033",
    #                     "given_names": "PETR RADEK",
    #                     "issue_date": "29-May-2023",
    #                     "passport_number": "FP4918991",
    #                     "sex": "M",
    #                     "surname": "HAVLÍČEK"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "26-Feb-1955",
    #                     "citizenship": "Czech/ČESKÁ REPUBLIKA",
    #                     "code": "CZE",
    #                     "country": "CZECH REPUBLIC",
    #                     "document_type": "PASSPORT",
    #                     "expiry_date": "25-Nov-2029",
    #                     "given_names": "KAMILA MARKÉTA",
    #                     "issue_date": "26-Nov-2019",
    #                     "machine_readable_zone": "P<CZECERNY<<KAMILA<MARKETA<<<<<<<<<<<<<<<XE5382230CZE550226<<<<<<<<<<<<<<",
    #                     "passport_number": "XE5382230",
    #                     "sex": "F",
    #                     "signature": "Kamila Černý",
    #                     "surname": "ČERNÝ"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "15-Oct-1972",
    #                     "citizenship": "German/DEUTSCH",
    #                     "code": "DEU",
    #                     "country": "BUNDESREPUBLIK DEUTSCHLAND / Federal Republic of Germany",
    #                     "document_type": "PASSPORT",
    #                     "expiry_date": "12-Oct-2030",
    #                     "given_names": "TOBIAS PAUL",
    #                     "issue_date": "13-Oct-2020",
    #                     "machine_readable_zone": "P<DEUBAUER<<TOBIAS<PAUL<<<<<<<<<<<<<<<WC5511857DEU721015<<<<<<<<<<<<<<",
    #                     "passport_number": "WC5511857",
    #                     "sex": "M",
    #                     "signature": "Tobias Bauer",
    #                     "surname": "BAUER"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "11-Jan-2004",
    #                     "citizenship": "Hungarian/MAGYAR",
    #                     "code": "HUN",
    #                     "country": "Hungary",
    #                     "expiry_date": "16-Jun-2032",
    #                     "given_names": "BÉLA BALÁZS",
    #                     "issue_date": "17-Jun-2022",
    #                     "passport_number": "XU3107453",
    #                     "sex": "M",
    #                     "signature": "Béla Gulyás",
    #                     "surname": "GULYÁS",
    #                     "type": "PASSPORT"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": "",
    #                 "decision": "Accept",
    #                 "status": "gameover"
    #             }
    #         ],
    #         [
    #             {
    #                 "client_info": {
    #                     "birth_date": "09-Sep-1987",
    #                     "citizenship": "Polish",
    #                     "code": "POL",
    #                     "country": "Republic of Poland",
    #                     "document_type": "PASSPORT",
    #                     "expiry_date": "21-Sep-2030",
    #                     "given_names": "TERESA RENATA",
    #                     "issue_date": "22-Sep-2020",
    #                     "mrz": "P<POLPIOTROWSKI<<TERESA<RENATA<<<<<<<<<<<<<<<SO1529306POL870909<<<<<<<<<<<<<<<",
    #                     "passport_number": "SO1529306",
    #                     "sex": "F",
    #                     "signature": "Teresa Piotrowski",
    #                     "surname": "PIOTROWSKI"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "12-Jan-2003",
    #                     "citizenship": "Finnish",
    #                     "country": "Republic of Finland",
    #                     "country_code": "FIN",
    #                     "document_type": "PASSPORT",
    #                     "expiry_date": "16-May-2033",
    #                     "given_names": "JOONA ARTTU",
    #                     "issue_date": "17-May-2023",
    #                     "passport_number": "DZ3745201",
    #                     "sex": "M",
    #                     "surname": "RISSANEN"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "14-Mar-1996",
    #                     "citizenship": "Polish",
    #                     "code": "POL",
    #                     "country": "Republic of Poland",
    #                     "document_type": "PASSPORT",
    #                     "expiry_date": "02-Apr-2027",
    #                     "given_names": "JOANNA EWA",
    #                     "issue_date": "03-Apr-2017",
    #                     "machine_readable_zone": "P<POLKRAWCZYK<<JOANNA<EWA<<<<<<<<<<<<<<<<<<<WJ4889217POL960314<<<<<<<<<<<<<<<<<4",
    #                     "passport_number": "WJ4889217",
    #                     "sex": "F",
    #                     "signature": "Joanna Krawczyk",
    #                     "surname": "KRAWCZYK"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "1979-03-21",
    #                     "citizenship": "Dutch",
    #                     "code": "NLD",
    #                     "country": "Kingdom of the Netherlands",
    #                     "document_type": "PASSPORT",
    #                     "expiry_date": "2027-03-24",
    #                     "given_names": "JORIS JOEP",
    #                     "issue_date": "2017-03-25",
    #                     "mrz": "P<NLDPEETERS<<JORIS<JOEP<<<<<<<<<<<<<<<KA1824541NLD790321<<<<<<<<<<<<<<31",
    #                     "passport_number": "KA1824541",
    #                     "sex": "M",
    #                     "signature": "Joris Peeters",
    #                     "surname": "PEETERS"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "14-Jul-1970",
    #                     "citizenship": "Polish/POLSKIE",
    #                     "code": "POL",
    #                     "country": "RZECZPOSPOLITA POLSKA / Republic of Poland",
    #                     "document_type": "PASSPORT",
    #                     "expiry_date": "09-Sep-2033",
    #                     "given_names": "MATEUSZ",
    #                     "issue_date": "10-Sep-2023",
    #                     "passport_number": "LT7012765",
    #                     "sex": "M",
    #                     "signature": "Mateusz Mazur",
    #                     "surname": "MAZUR"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "14-Nov-1984",
    #                     "citizenship": "French/FRANÇAISE",
    #                     "country_code": "FRA",
    #                     "document_type": "PASSPORT",
    #                     "expiry_date": "20-Sep-2030",
    #                     "given_names": "MARCHAND LAURENT",
    #                     "issue_date": "21-Sep-2020",
    #                     "passport_number": "AZ1787440",
    #                     "sex": "M",
    #                     "signature": "Marchand Legrand",
    #                     "surname": "LEGRAND"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "24-Jun-1982",
    #                     "citizenship": "German/DEUTSCH",
    #                     "country": "BUNDESREPUBLIK DEUTSCHLAND / Federal Republic of Germany",
    #                     "document_type": "PASSPORT",
    #                     "expiry_date": "03-Aug-2030",
    #                     "given_names": "PHILIPP SAMUEL",
    #                     "issue_date": "04-Aug-2020",
    #                     "machine_readable_zone": "P<DEUUHLIG<<PHILIPP<SAMUEL<<<<<<<<<<<<<<<NF9568344DEU820624<<<<<<<<<<<<<<<<<<<",
    #                     "passport_code": "DEU",
    #                     "passport_number": "NF9568344",
    #                     "sex": "M",
    #                     "signature": "Philipp Uhlig",
    #                     "surname": "UHLIG"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "01-Sep-1964",
    #                     "citizenship": "French/FRANÇAISE",
    #                     "code": "FRA",
    #                     "country": "REPUBLIQUE FRANCAISE / French Republic",
    #                     "document_type": "PASSPORT",
    #                     "expiry_date": "17-Apr-2028",
    #                     "given_names": "ROBIN MARCHAND",
    #                     "issue_date": "18-Apr-2018",
    #                     "passport_number": "VX1043290",
    #                     "sex": "M",
    #                     "signature": "Robin Laurent",
    #                     "surname": "LAURENT"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": {
    #                     "birth_date": "30-Jan-1989",
    #                     "citizenship": "Swiss/SCHWEIZ",
    #                     "code": "CHE",
    #                     "document_type": "PASSPORT",
    #                     "expiry_date": "28-Apr-2032",
    #                     "given_names": "DARIO DAVID",
    #                     "issue_date": "29-Apr-2022",
    #                     "issuing_country": "SCHWEIZERISCHE EIDGENOSSENSCHAFT / Swiss Confederation",
    #                     "passport_number": "XQ7251768",
    #                     "passport_type": "REISEPASS",
    #                     "sex": "M",
    #                     "signature": "Dario Huber",
    #                     "surname": "HUBER"
    #                 },
    #                 "decision": "Accept",
    #                 "status": "active"
    #             },
    #             {
    #                 "client_info": "",
    #                 "decision": "Accept",
    #                 "status": "gameover"
    #             }
    #         ]
    #     ],
    # })

if __name__ == '__main__':
    # Iniciar el game_loop en un hilo en segundo plano
    hilo_juego = threading.Thread(target=game_loop, daemon=True)
    hilo_juego.start()
    
    # Iniciar el servidor Flask, escuchando en todas las interfaces de red.
    app.run(host="0.0.0.0", port=5000)
