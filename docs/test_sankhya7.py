import os
import json
import urllib.request
from urllib.error import HTTPError

client_id = '11026a04-b106-4507-a748-5b8bb1431e1a'
client_secret = 'a4fQUBl8WHc9DGD69yQKD0gqN14tgOG5'
x_token = 'e6c32aae-a725-42b8-81fe-67987a55c1e0'

url = 'https://api.sandbox.sankhya.com.br/authenticate'
headers = {
    'Content-Type': 'application/json',
    'X-Token': x_token
}
body = json.dumps({
    "client_id": client_id,
    "client_secret": client_secret
}).encode('utf-8')

print(f"Testing {url}...")
try:
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    res = urllib.request.urlopen(req)
    print("SUCCESS!")
    print(res.read().decode('utf-8'))
except HTTPError as e:
    print(f"Error {e.code}:", e.read().decode('utf-8'))
except Exception as e:
    print(e)
