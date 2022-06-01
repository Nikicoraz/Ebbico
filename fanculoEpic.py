from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
import json
import http.client
import os
import subprocess
from utils.auth import SID

edlaunch_path = 'D:/Program Files/Epic Games/EliteDangerous/EDLaunch.exe'
sottr_path = "D:/Program Files/Epic Games/ShadowoftheTombRaider/SOTTR.exe"
civ6path = "D:/Program Files/Epic Games/SidMeiersCivilizationVI/2KLauncher/LauncherPatcher.exe"
rebel_path = "D:/Program Files/Epic Games/RebelGalaxy/RebelGalaxy.exe"
bio_rem_path = "D:/Program Files/Epic Games/BioshockRemastered/2KLauncher/LauncherPatcher.exe"

# def OttieniCookie(browser : webdriver.Firefox):
#     global code
#     browser.get(r"https://www.epicgames.com/id/login?productName=epic-games&redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fsite%2F&client_id=5a6fcd3b82e04f8fa0065253835c5221&noHostRedirect=true")
#     username = open("cred", "r").readlines()[0]
#     passwd = open("cred", "r").readlines()[1]
#     browser.implicitly_wait(10)
#     browser.find_element_by_id("login-with-epic").click()
#     browser.find_element_by_id("email").send_keys(username)
#     browser.find_element_by_id("password").send_keys(passwd)
#     sleep(2)
#     browser.find_element_by_css_selector("div.sc-bdfBQB:nth-child(5)").click()
#     print(browser.get_cookies())
#     sleep(20)
#     code = browser.get_cookie("EPIC_BEARER_TOKEN")["value"]

# def SalvaCookie():
#     pass


def lanciaGioco(path):
    ottieniCodice()
    os.chdir("/".join(path.replace("\\", "/").split("/")[:-1]))
    subprocess.call('"' + path + '" /Epic -AUTH_LOGIN=unused -AUTH_PASSWORD=' + password + ' -AUTH_TYPE=exchangecode -epicapp=9c203b6ed35846e8a4a9ff1e314f6593 -epicenv=Prod -EpicPortal  -epicusername="' + epicusername + '" -epicuserid=' + epicuserid + ' -epiclocale=en /NOVR')

def ottieniCodice(browser = None):
    global password, epicuserid, epicusername, code
    op = webdriver.FirefoxOptions()
    op.add_argument('--headless')
    
    # Aggiunto profilo forse cambia qualcosa
    if(browser == None):
        browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=op)


    browser.get("https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code");
    
    browser.add_cookie({"name": "EPIC_BEARER_TOKEN", "value" : "a00add2428d04a8c8674b91fe1230e3b", "host" : ".epicgames.com"})
    browser.refresh()

    code = json.loads(browser.find_element_by_id("json").text).get("authorizationCode")
    browser.close()

    # if code == None:
    #     print("Ora di eseguire l'accesso con epic...")
    #     OttieniCookie(browser)

    conn = http.client.HTTPSConnection("account-public-service-prod.ol.epicgames.com")

    payload = "grant_type=authorization_code&code=" + code

    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Authorization': "basic ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ6M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ="
        }

    conn.request("POST", "/account/api/oauth/token", payload, headers)

    res = conn.getresponse()
    data = res.read()
    data_json = json.loads(data.decode("utf-8"))

    token = data_json["access_token"]
    epicusername = data_json["displayName"]
    epicuserid = data_json["account_id"]

    conn = http.client.HTTPSConnection("account-public-service-prod.ol.epicgames.com")

    payload = ""

    headers = {
            'Authorization': "bearer " + token
        }

    conn.request("GET", "/account/api/oauth/exchange", payload, headers)

    res = conn.getresponse()
    data = res.read()
    password = json.loads(data.decode("utf-8"))["code"]
    
    conn.close()

    os.system("cls")

    print("Autenticato!")

while 1:
    q = input("""
            1. Elite dangerous
            2. Shadow of The Tomb Raider
            3. CivilizationVI
            4. Rebel Galaxy
            5. Bioshock Remastered
            6. Uscire
            \nInserire cosa avviare: """)
    if(q == "1"):
        lanciaGioco(edlaunch_path)
        os.system(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Elite Dangerous Market Connector.lnk")
    elif(q == "2"):
        lanciaGioco(sottr_path)
    elif (q == "3"):
        lanciaGioco(civ6path)
    elif q == "4":
        lanciaGioco(rebel_path)
    elif q == "5":
        lanciaGioco(bio_rem_path)
    elif(q == "6"):
        exit()
        
    os.system("cls")