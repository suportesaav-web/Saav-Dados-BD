import urllib.request
import json
from urllib.error import HTTPError

client_id = '11026a04-b106-4507-a748-5b8bb1431e1a'
x_token = '9db56f27-0792-44f2-8c51-0d353664af26'

url = 'https://api.sandbox.sankhya.com.br/mge/service.sbr?serviceName=MobileLoginSP.login'

payload = {
    "serviceName": "MobileLoginSP.login",
    "requestBody": {
        "TOKEN": {
            "$": x_token
        }
    }
}

body = json.dumps(payload).encode()
headers = {
    'Content-Type': 'application/json',
    'appkey': client_id
}

print(f"Testing {url} with Token body")
try:
    req = urllib.request.Request(url, method='POST', headers=headers, data=body)
    res = urllib.request.urlopen(req)
    print("Success:", res.read().decode())
except HTTPError as e:
    print(f"Error {e.code}:", e.read().decode())
