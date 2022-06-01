from utils.auth import Auth
from enum import Enum
import os

class Giochi(Enum):
    ELITE_DANGEROUS             = 'D:/Program Files/Epic Games/EliteDangerous/EDLaunch.exe'
    SHADOW_OF_THE_TOMB_RAIDER   = "D:/Program Files/Epic Games/ShadowoftheTombRaider/SOTTR.exe"
    CIVILIZATION_6              = "D:/Program Files/Epic Games/SidMeiersCivilizationVI/2KLauncher/LauncherPatcher.exe"
    REBEL_GALAXY                = "D:/Program Files/Epic Games/RebelGalaxy/RebelGalaxy.exe"
    BIOSHOCK_REMASTERED         = "D:/Program Files/Epic Games/BioshockRemastered/2KLauncher/LauncherPatcher.exe"

auth = Auth()

auth.auth_code()

while 1:
    q = input("""
            1. Elite dangerous
            2. Shadow of The Tomb Raider
            3. CivilizationVI
            4. Rebel Galaxy
            5. Bioshock Remastered
            6. Uscire
            \nInserire cosa avviare: """)
    gioco = ""
    if(q == "1"):
        gioco = Giochi.ELITE_DANGEROUS
        os.system(r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Elite Dangerous Market Connector.lnk")
    elif(q == "2"):
        gioco = Giochi.SHADOW_OF_THE_TOMB_RAIDER
    elif (q == "3"):
        gioco  = Giochi.CIVILIZATION_6
    elif q == "4":
        gioco = Giochi.REBEL_GALAXY
    elif q == "5":
        gioco = Giochi.BIOSHOCK_REMASTERED
    elif(q == "6"):
        exit()
    
    auth.launch_game(gioco.value)
    
    os.system("cls")