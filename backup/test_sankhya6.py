import urllib.request
import urllib.parse
from urllib.error import HTTPError
import base64
import json

client_id = '11026a04-b106-4507-a748-5b8bb1431e1a'
secret = 'a4fQUBl8WHc9DGD69yQKD0gqN14tgOG5'
auth = base64.b64encode(f'{client_id}:{secret}'.encode()).decode()

endpoints = [
    '/token',
    '/api/token',
    '/oauth/token',
    '/api/oauth/token',
    '/login'
]

data = urllib.parse.urlencode({'grant_type': 'client_credentials'}).encode()

for ep in endpoints:
    url = f'https://api.sandbox.sankhya.com.br{ep}'
    print(f"Testing POST {url}")
    try:
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Authorization', f'Basic {auth}')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        res = urllib.request.urlopen(req)
        print("SUCCESS:", res.read().decode())
    except HTTPError as e:
        if e.code not in [404, 405]:
            print(f"Error {e.code}:", e.read().decode())
    except Exception:
        pass

# Test /login with JSON payload
try:
    url = 'https://api.sandbox.sankhya.com.br/login'
    body = json.dumps({'username': client_id, 'password': secret}).encode()
    print(f"Testing POST {url} with username/password JSON")
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
    res = urllib.request.urlopen(req)
    print("SUCCESS:", res.read().decode())
except HTTPError as e:
    print(f"Error {e.code}:", e.read().decode())
