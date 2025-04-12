import redis
import json

r = redis.Redis(host='172.16.206.75', port=6379, decode_responses=True)

try:
    keys = r.keys('*')
    # keys = r.keys('true_good_*')
    # keys = r.keys('true_wrong_*')

    if keys:
        print("Claves almacenadas en Redis (mostrando máximo 5):")
        for key in keys: 
            print("____________________________________________________________________________________")
            print(f"- Clave: {key}")
            value = r.get(key)
            try:
                json_value = json.loads(value)
                print(json.dumps(json_value, indent=2, ensure_ascii=False))  # JSON bonito
            except json.JSONDecodeError:
                print(f"Valor (no es JSON): {value}")
    else:
        print("No hay claves almacenadas en Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"Error de conexión: {e}")
