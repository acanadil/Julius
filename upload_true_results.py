import saving
import os
import subprocess
import base64

for set, outcome in [
                     ("client_001_200", "active"), ("client_201_400", "active"), ("client_401_500", "active"),
                     ("client_501_700", "gameover"), ("client_701_900", "gameover"), ("client_901_1000", "gameover"),
                     ("client_1001_1200", "active"), ("client_1201_1400", "active"), ("client_1401_1500", "active"),
                     ("client_1501_1700", "gameover"), ("client_1701_1900", "gameover"), ("client_1901_2000", "gameover"),
                     ("client_2001_2200", "active"), ("client_2201_2400", "active"), ("client_2401_2500", "active"),
                     ("client_2501_2700", "gameover"), ("client_2701_2900", "gameover"), ("client_2901_3000", "gameover")
                    ]:
    os.makedirs(f"{set}/", exist_ok=True)
    subprocess.run(['unzip', f"{set}.zip", '-d', f"{set}/"])
    users = os.listdir(f"{set}/")
    for user in users:
        os.makedirs(f"{set}/{user.split(".")[0]}/", exist_ok=True)
        subprocess.run(['unzip', f"{set}/{user}", '-d', f"{set}/{user.split(".")[0]}/"])
        os.remove(f"{set}/{user}")

        data = {"client_data": {}}
        with open(f"{set}/{user.split(".")[0]}/account.pdf", 'rb') as file:
            data["client_data"]["account"] = base64.b64encode(file.read())
        with open(f"{set}/{user.split(".")[0]}/description.txt", 'rb') as file:
            data["client_data"]["description"] = base64.b64encode(file.read())
        with open(f"{set}/{user.split(".")[0]}/passport.png", 'rb') as file:
            data["client_data"]["passport"] = base64.b64encode(file.read())
        with open(f"{set}/{user.split(".")[0]}/profile.docx", 'rb') as file:
            data["client_data"]["profile"] = base64.b64encode(file.read())
        saving.cast_files(data, outcome)
    #os.remove(f"{set}.zip")