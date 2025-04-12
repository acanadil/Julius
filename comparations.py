import redis
import json
from datetime import datetime

r = redis.Redis(host='172.16.206.75', port=6379, decode_responses=True)

try:
    keys = r.keys('*')
    # keys = r.keys('true_right-*')
    # keys = r.keys('true_wrong-*')
    numProfile = 0
    numOK = 0
    numError = 0
  
    if keys:
        for key in keys[:10]:
            numParams = 0
            numParamsOK = 0

            value = r.get(key)

            try:
                numProfile += 1
                json_value = json.loads(value)

                # Verificar que las claves existen
                passport = json_value.get("passport", {})
                profile = json_value.get("profile", {}).get("Client Information", {})
                account = json_value.get("account", {})

                # passport -> passport_num == account -> passport_number == contains(profile -> data_extra)
                passport_num = passport.get("passport_num")
                account_passport = account.get("passport_number")
                passport_extra = passport.get("extra_data")
                if passport_num and account_passport and passport_extra:
                    if passport_num != account_passport or passport_num not in passport_extra:
                        numError += 1
                        #continue
                    numParams += 1
                    numParamsOK += 1
                # passport -> issue/expiry_date == profile -> Id Expiry/issue issue_date < expiry_date
                issue_date = passport.get("issue_date").strip() if passport.get("issue_date") else None
                expiry_date = passport.get("expiry_date").strip() if passport.get("expiry_date") else None

                if issue_date and expiry_date:
                    # Verificar que profile tenga las claves requeridas
                    if "Id issue" in profile and "Id Expiry" in profile:
                        if (datetime.strptime(issue_date, "%Y-%m-%d") != datetime.strptime(profile["Id Issue"], "%Y-%m-%d") or
                                datetime.strptime(expiry_date, "%Y-%m-%d") != datetime.strptime(profile["Id Expiry"], "%Y-%m-%d")):
                            numError += 1
                            #continue
                    else:
                        numError += 1
                        #continue
                    if datetime.strptime(issue_date, "%d-%b-%Y") >= datetime.strptime(expiry_date, "%d-%b-%Y"):
                        numError += 1
                        #continue
                    numParams += 1
                    numParamsOK += 1
                # Comprobación de género
                gender = profile.get("gender")
                if gender and "sex" in passport:
                    if passport["sex"] != gender[:1]:  # Asumimos que 'sex' en passport es una letra
                        numError += 1
                        #continue
                    numParams += 1
                    numParamsOK += 1
                # Verificación de nombre y apellido del titular de la cuenta
                account_name = account.get("account_holder_name")
                account_surname = account.get("account_holder_surname")
                if account_name and account_surname and passport_extra:
                    account_name_parts = account_name.split()
                    surname = account_surname
                    extra_data = passport_extra.lower()
                    if not (any(part.lower() in extra_data for part in account_name_parts)) or not (surname.lower() in extra_data):
                        numError += 1
                        #continue
                    numParams += 1
                    numParamsOK += 1
                
                # Comprobación de los países
                # country_pas = passport.get("country")
                country_pro = profile.get("Country")
                country_acc = account.get("country")

                # Filtramos los valores que no son None o vacíos
                # countries = [country for country in [country_pas, country_pro, country_acc] if country]
                # countries = [country for country in [country_pro, country_acc] if country]

                numParams += 1

                if country_pro and country_acc:
                    if (country_pro != country_acc):
                        numError += 1
                    #continue
                    else:
                        numParamsOK += 1
                        numOK += 1
            
                print(f"Passport: {json.dumps(passport, indent=2)}")
                print(f"Profile: {json.dumps(profile, indent=2)}")
                print(f"Account: {json.dumps(account, indent=2)}")
                print(f"Num Params: {numParams}, Num Params OK: {numParamsOK}, Outcome: {json_value["outcome"]}\n")
                    

            except json.JSONDecodeError:
                print(f"Valor (no es JSON): {value}")
    else:
        print("No hay claves almacenadas en Redis.")

    print(f"Num profile = {numProfile}\nNum Error = {numError}\nNum OK = {numOK}")
    perOK = numOK / numProfile
    perError = numError / numProfile
    print(f"% Error = {perError}\n% OK = {perOK}")

except redis.exceptions.ConnectionError as e:
    print(f"Error de conexión: {e}")