import os
import urllib.request
import json
from urllib.error import URLError, HTTPError

# Load Env
env_file = r"C:\Users\SAAV054\Documents\Desenvolvimento\Saav-Dados-BD\.env"
with open(env_file, 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, val = line.strip().split('=', 1)
            os.environ[key] = val

client_id = os.environ.get('SANKHYA_CLIENT_ID')
client_secret = os.environ.get('SANKHYA_CLIENT_SECRET')
x_token = os.environ.get('SANKHYA_X_TOKEN')

base_urls = [
    "https://api.sankhya.com.br",
    "https://api.sandbox.sankhya.com.br"
]

endpoints = [
    "/login",
    "/api/authenticate",
    "/gateway/v1/login",
    "/mge/service.sbr?serviceName=MobileLoginSP.login"
]

headers_variations = [
    {"appkey": client_id, "token": x_token},
    {"client_id": client_id, "client_secret": client_secret, "token": x_token}
]

print("Starting tests...")
for base in base_urls:
    for endpoint in endpoints:
        url = base + endpoint
        for headers in headers_variations:
            try:
                req = urllib.request.Request(url, headers=headers, method="GET")
                res = urllib.request.urlopen(req)
                print(f"SUCCESS GET {url} with headers {list(headers.keys())}: {res.status}")
                continue
            except HTTPError as e:
                # 401 is unauthorized (maybe needs POST or wrong creds), 404 is not found, 405 method not allowed
                if e.code not in [404, 405, 500]:
                    print(f"GET {url} : {e.code}")
            except Exception as e:
                pass
            
            try:
                data = json.dumps(headers).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
                res = urllib.request.urlopen(req)
                print(f"SUCCESS POST {url} with body {list(headers.keys())}: {res.status}")
            except HTTPError as e:
                if e.code not in [404, 405, 500]:
                    print(f"POST {url} : {e.code}")
            except Exception as e:
                pass

print("Tests completed.")
