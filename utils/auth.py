import json
from msilib.schema import Error
import webbrowser
import requests
from base64 import b64encode
import subprocess

def to_native_string(string, encoding='ascii'):
    """Given a string object, regardless of type, returns a representation of
    that string in the native string type, encoding and decoding where
    necessary. This assumes ASCII unless told otherwise.
    """
    if isinstance(string, str):
        out = string
    else:
        out = string.decode(encoding)

    return out

class HTTPBasicAuth():
    """Attaches HTTP Basic Authentication to the given Request object."""

    _user_basic = '34a02cf8f4414e29b15921876da36f9a'
    _pw_basic = 'daafbccc737745039dffe53d94fc76cf'


    def __init__(self):
        self.authstr = 'Basic ' + to_native_string(
        b64encode(b':'.join((self._user_basic.encode("latin1"), self._pw_basic.encode("latin1")))).strip()
        )

    def __eq__(self, other):
        return all([
            self.username == getattr(other, 'username', None),
            self.password == getattr(other, 'password', None)
        ])

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers['Authorization'] = self.authstr
        return r

class Auth:
    _sito_sid = 'https://www.epicgames.com/id/login?redirectUrl=https://www.epicgames.com/id/api/redirect'
    _oauth_host = 'account-public-service-prod03.ol.epicgames.com'
    _user_agent = 'UELauncher/11.0.1-14907503+++Portal+Release-Live Windows/10.0.19041.1.256.64bit'



    def __init__(self):
        try:
            self.data = json.load(open('auth.json', "r"))
        except FileNotFoundError:
            self.data = {}
        self._egl_version = '11.0.1-14907503+++Portal+Release-Live'
        if self.data == {}:
            self.data["sid"] = "-1"
            self.data["exch"] = "-1"
            self.data["refr"] = "-1"

        self.session = requests.session()
        self.session.headers['User-Agent'] = self._user_agent
        # increase maximum pool size for multithreaded metadata requests
        self.session.mount('https://', requests.adapters.HTTPAdapter(pool_maxsize=16))

        try:
            self.userdata = json.load(open("user.json", "r"))
        except:
            print("Found no user data")
            self.userdata = []
    
    def get_sid(self):
        if not self.data["sid"]:
            webbrowser.open(self._sito_sid)
            sid = input("Enter the SID: ")
            sid = sid.strip('"')
        else:
            sid = self.data["sid"]
            
        return sid
    
    def auth_sid(self, sid):
        s = requests.session()
        s.headers.update({
            'X-Epic-Event-Action': 'login',
            'X-Epic-Event-Category': 'login',
            'X-Epic-Strategy-Flags': '',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        f'EpicGamesLauncher/{self._egl_version} '
                        'UnrealEngine/4.23.0-14907503+++Portal+Release-Live '
                        'Chrome/84.0.4147.38 Safari/537.36'
        })
        s.cookies["EPIC_COUNTRY"] = "IT"
        
                # get first set of cookies (EPIC_BEARER_TOKEN etc.)
        _ = s.get('https://www.epicgames.com/id/api/set-sid', params=dict(sid=sid))
        # get XSRF-TOKEN and EPIC_SESSION_AP cookie
        _ = s.get('https://www.epicgames.com/id/api/csrf')
        # finally, get the exchange code
        r = s.post('https://www.epicgames.com/id/api/exchange/generate',
                headers={'X-XSRF-TOKEN': s.cookies['XSRF-TOKEN']})
        
        if r.status_code == 200:
            return r.json()['code']
        else:
            print(f'Getting exchange code failed: {r.json()}')
            return ''

    def reset(self):
        self.data["exch"] = None
        self.data["sid"] = None
        self.data["refr"] = None
        
    def get_exch(self,):
        if not self.data["exch"]:
            self.data["sid"] = self.get_sid()
            self.data["exch"] = self.auth_sid(self.data["sid"])
        return self.data["exch"]
    
    
    def start_session(self, refresh_token: str = None, exchange_token: str = None):
        if refresh_token:
            params = dict(grant_type='refresh_token',
                        refresh_token=refresh_token,
                        token_type='eg1')
        elif exchange_token:
            params = dict(grant_type='exchange_code',
                        exchange_code=exchange_token,
                        token_type='eg1')
        
        r = requests.session().post(f'https://{self._oauth_host}/account/api/oauth/token',
                                data=params, auth=HTTPBasicAuth())

        if r.status_code >= 500:
            r.raise_for_status()
            
        j = r.json()
        if 'error' in j:
            print(f'Login to EGS API failed with errorCode: {j["errorCode"]}')
            if j["errorCode"] == "errors.com.epicgames.account.oauth.exchange_code_not_found" and exchange_token != None:
                self.reset()
                self.get_exch()
                self.start_session(exchange_token=self.data["exch"])
                return self.user

        self.session.headers['Authorization'] = f'bearer {j["access_token"]}'
        # only set user info when using non-anonymous login
        self.user = j

        return j
    
    def resume_session(self, session):
        self.session.headers['Authorization'] = f'bearer {session["access_token"]}'
        r = self.session.get(f'https://{self._oauth_host}/account/api/oauth/verify')
        
        if r.status_code >= 500:
            r.raise_for_status()
            
        j = r.json()
        
        if 'errorMessage' in j:
            print(f'Login to EGS API failed with errorCode: {j["errorCode"]}')
            raise Exception(j['errorCode'])

        self.user = session
        return self.user
    
    def auth_code(self, code=None) -> bool:
        """
        Handles authentication via exchange code (either retrieved manually or automatically)
        """
        try:
            if self.userdata != None:
                self.userdata = self.resume_session(self.userdata)
                json.dump(self.userdata, open('user.json', "w"))
                return self.userdata
            else:
                raise Exception("No user data")
        except:
            try:
                try:
                    self.userdata = self.start_session(refresh_token=self.data["refr"])
                except:
                    self.userdata = self.start_session(exchange_token=code)
                self.data["refr"] = self.userdata["refresh_token"]
                json.dump(self.data, open('auth.json', "w"))
                json.dump(self.userdata, open('user.json', "w"))
                return self.userdata
            except Exception as e:
                print(f'Logging in failed with {e!r}, please try again.')
                return False
    
    def get_game_token(self):
        r = self.session.get(f'https://{self._oauth_host}/account/api/oauth/exchange')
        r.raise_for_status()
        
        return r.json()
    
        
    def launch_game(self, game_path):
        if not self.data["sid"]:
            print("Login first!")
            return
        g_token = self.get_game_token()["code"]
        subprocess.call(f"{game_path} /EPIC -AUTH_LOGIN=unused -AUTH_PASSWORD={g_token} -AUTH_TYPE=exchangecode -epicapp=9c203b6ed35846e8a4a9ff1e314f6593 -epicenv=Prod -EpicPortal  -epicusername={self.userdata['displayName']} -epicuserid={self.userdata['account_id']} -epiclocale=en /NOVR")