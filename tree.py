import redis
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, plot_tree
import matplotlib.pyplot as plt
import json

r = redis.Redis(host='172.16.206.75', port=6379, decode_responses=True)

try:
    keys = r.keys('*')

    if keys:
        for key in keys:
            data = json.loads(r.get(key))
    else:
        print("No hay claves almacenadas en Redis.")
except redis.exceptions.ConnectionError as e:
    print(f"Error de conexión: {e}")


data_list = [data]  
features = [extract_features(d) for d in data_list]
df = pd.DataFrame(features)

X = df.drop("outcome", axis=1)
y = df["outcome"].apply(lambda x: 1 if x == "active" else 0)

tree = DecisionTreeClassifier(max_depth=3)
tree.fit(X, y)

plt.figure(figsize=(12, 6))
plot_tree(tree, feature_names=X.columns, class_names=["gameover", "active"], filled=True)
plt.show()


from datetime import datetime

def extract_features(entry):
    features = {}
    passport = entry.get("passport", {})
    profile = entry.get("profile", {}).get("Client Information", {})
    account = entry.get("account", {})
    outcome = entry.get("outcome", "unknown")
    
    try:
        expiry_date = datetime.strptime(passport.get("expiry_date", ""), "%d-%b-%Y")
        features["passport_expired"] = expiry_date < datetime.now()
    except:
        features["passport_expired"] = True

    try:
        birth_date = datetime.strptime(passport.get("birth_date", "").strip(), "%d-%b-%Y")
        dob = datetime.strptime(profile.get("Dob", ""), "%Y-%m-%d")
        features["birth_date_mismatch"] = birth_date.date() != dob.date()
    except:
        features["birth_date_mismatch"] = True

    features["country_mismatch"] = passport.get("country", "").lower() != account.get("country", "").lower()
    features["has_real_estate"] = entry.get("profile", {}).get("Professional Background", {}).get("Wealth", {}).get("Real Estate", 0) > 0
    features["has_income_info"] = bool(entry.get("profile", {}).get("Professional Background", {}).get("Income"))
    features["chf_off"] = account.get("chf", "") == "/Off"
    features["eur_off"] = account.get("eur", "") == "/Off"
    features["usd_off"] = account.get("usd", "") == "/Off"
    features["outcome"] = outcome

    return features

