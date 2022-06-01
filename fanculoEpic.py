from utils.auth import Auth

auth = Auth()

auth.auth_code()
auth.launch_game("D:\Program Files\Epic Games\EliteDangerous\EDLaunch.exe".replace("\\", "/"))