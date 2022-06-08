from utils.auth import Auth
from enum import Enum
import os

# Inserire il path dei giochi in questo enum
class Giochi(Enum):
    ELITE_DANGEROUS             = 'D:/Program Files/Epic Games/EliteDangerous/EDLaunch.exe'
    SHADOW_OF_THE_TOMB_RAIDER   = "D:/Program Files/Epic Games/ShadowoftheTombRaider/SOTTR.exe"
    CIVILIZATION_6              = "D:/Program Files/Epic Games/SidMeiersCivilizationVI/2KLauncher/LauncherPatcher.exe"
    REBEL_GALAXY                = "D:/Program Files/Epic Games/RebelGalaxy/RebelGalaxy.exe"
    BIOSHOCK_REMASTERED         = "D:/Program Files/Epic Games/BioshockRemastered/2KLauncher/LauncherPatcher.exe"
    WOLFENSTEIN_TNO             = "D:/Program Files/Epic Games/WolfensteinTNO/WolfNewOrder_x64.exe"


# Zona no tocca >:(
auth = Auth()

if not auth.auth_code():
    exit(1)

lista_giochi = "\n".join(f"{i}: {x.name}" for i, x in enumerate(Giochi, 1))
while 1:
    q = input(f"""------------\n{lista_giochi}\n{len(Giochi) + 1}: Esci\nInserire cosa avviare: """)
    gioco = ""
    gioco = list(Giochi)[int(q) - 1] if q.isdigit() and int(q) <= len(Giochi) else ""

    if gioco != "":
        auth.launch_game(gioco.value)
    if int(q) == len(Giochi) + 1:
        exit(0)
    os.system("cls")