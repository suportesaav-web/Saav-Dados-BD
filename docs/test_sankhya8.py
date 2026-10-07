import os
import json
import urllib.request
import urllib.parse
from urllib.error import HTTPError

client_id = '11026a04-b106-4507-a748-5b8bb1431e1a'
client_secret = 'a4fQUBl8WHc9DGD69yQKD0gqN14tgOG5'
x_token = 'e6c32aae-a725-42b8-81fe-67987a55c1e0'
url = 'https://api.sandbox.sankhya.com.br/authenticate'

headers_json = {
    'Content-Type': 'application/json',
    'X-Token': x_token
}
body_json = json.dumps({
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "client_credentials"
}).encode('utf-8')

print("Testing JSON...")
try:
    req = urllib.request.Request(url, data=body_json, headers=headers_json, method='POST')
    res = urllib.request.urlopen(req)
    print("SUCCESS JSON!", res.read().decode('utf-8'))
except HTTPError as e:
    print(f"Error JSON {e.code}:", e.read().decode('utf-8'))


headers_form = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Token': x_token
}
body_form = urllib.parse.urlencode({
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "client_credentials"
}).encode('utf-8')

print("\nTesting Form...")
try:
    req = urllib.request.Request(url, data=body_form, headers=headers_form, method='POST')
    res = urllib.request.urlopen(req)
    print("SUCCESS FORM!", res.read().decode('utf-8'))
except HTTPError as e:
    print(f"Error FORM {e.code}:", e.read().decode('utf-8'))
