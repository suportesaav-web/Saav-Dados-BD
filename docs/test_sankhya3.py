import os
import urllib.request
import json
from urllib.error import URLError, HTTPError

client_id = '11026a04-b106-4507-a748-5b8bb1431e1a'
client_secret = 'a4fQUBl8WHc9DGD69yQKD0gqN14tgOG5'

url = 'https://api.sandbox.sankhya.com.br/api/authenticate'
body = json.dumps({
    "client_id": client_id,
    "client_secret": client_secret
}).encode('utf-8')

print(f"Testing {url}")
try:
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
    res = urllib.request.urlopen(req)
    print("Success:", res.read().decode('utf-8'))
except HTTPError as e:
    print(f"Error {e.code}:", e.read().decode('utf-8'))
