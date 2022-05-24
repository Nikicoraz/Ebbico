import json
from urllib.request import HTTPBasicAuthHandler
from weakref import ref
import webbrowser

from requests import session
from requests.auth import HTTPBasicAuth



class SID:
    @staticmethod
    def get():
        print('Please login via the epic web login!')
        webbrowser.open(
            'https://www.epicgames.com/id/login?redirectUrl='
            'https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fredirect'
        )

        print('If the web page did not open automatically, please manually open the following URL: '
                            'https://www.epicgames.com/id/login?redirectUrl=https://www.epicgames.com/id/api/redirect')
        sid = input('Please enter the "sid" value from the JSON response: ')

        sid = sid.strip()
        return sid
    
    @staticmethod
    def get_exchange_code(sid):
        s = session()
        s.headers.update({
            'X-Epic-Event-Action': 'login',
            'X-Epic-Event-Category': 'login',
            'X-Epic-Strategy-Flags': '',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        f'EpicGamesLauncher/11.0.1-14907503+++Portal+Release-Live '
                        'UnrealEngine/4.23.0-14907503+++Portal+Release-Live '
                        'Chrome/84.0.4147.38 Safari/537.36'
        })
        s.cookies['EPIC_COUNTRY'] = "IT"
        
        # Ottenimento cookie
        _ = s.get('https://www.epicgames.com/id/api/set-sid', params=dict(sid=sid))
        _ = s.get('https://www.epicgames.com/id/api/csrf')
        r = s.post('https://www.epicgames.com/id/api/exchange/generate',
                    headers={'X-XSRF-TOKEN': s.cookies['XSRF-TOKEN']})
        
        if r.status_code == 200:
            return r.json()['code']
        else:
            raise Exception(f'Error while requesting exchange code: {r.status_code}')
        
        
    @staticmethod
    def auth(exchange_token = None, refresh_token = None):
        _user_basic = '34a02cf8f4414e29b15921876da36f9a'
        _pw_basic = 'daafbccc737745039dffe53d94fc76cf'
        _oauth_host = 'account-public-service-prod03.ol.epicgames.com'
        
        oauth_basic = HTTPBasicAuth(_user_basic, _pw_basic)
        
        if exchange_token:
            params = dict(grant_type='exchange_code',
                            exchange_code=exchange_token,
                            token_type='eg1')
        elif refresh_token:
            params = dict(grant_type='refresh_token',
                            refresh_token=refresh_token,
                            token_type='eg1')
            
            
        r = session().post(f'https://{_oauth_host}/account/api/oauth/token',
                            data=params, auth=oauth_basic,
                            timeout=5)
        
        if r.status_code >= 500:
            r.raise_for_status()

        j = r.json()
        return j["access_token"], j["refresh_token"]
        
if __name__ == "__main__":
    try:
        if json.load(open("auth.json", "r"))["refresh_token"]:
            print("found refresh token")
            print("Bearer Token: ", SID.auth(refresh_token=json.load(open("auth.json", "r"))["refresh_token"])[0])
        else:
            raise FileNotFoundError()
    except FileNotFoundError:
        sid = SID.get()
        exchange_token = SID.get_exchange_code(sid)
        access_token, refresh_token = SID.auth(exchange_token)
        json.dump(dict(access_token=access_token, refresh_token=refresh_token), open('auth.json', 'w'))