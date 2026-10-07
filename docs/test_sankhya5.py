import urllib.request
import json
from urllib.error import HTTPError

client_id = '11026a04-b106-4507-a748-5b8bb1431e1a'
x_token = '9db56f27-0792-44f2-8c51-0d353664af26'

url = 'https://api.sandbox.sankhya.com.br/login'
body = json.dumps({'appkey': client_id, 'token': x_token}).encode()

print(f"Testing {url} with body")
try:
    req = urllib.request.Request(url, method='POST', headers={'Content-Type': 'application/json'}, data=body)
    print("Success:", urllib.request.urlopen(req).read().decode())
except HTTPError as e:
    print(f"Error {e.code}:", e.read().decode())
