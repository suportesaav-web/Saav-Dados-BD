import os
import urllib.request
import json
from urllib.error import URLError, HTTPError

client_id = '11026a04-b106-4507-a748-5b8bb1431e1a'
x_token = '9db56f27-0792-44f2-8c51-0d353664af26'

url = 'https://api.sandbox.sankhya.com.br/login'
headers = {'appkey': client_id, 'token': x_token}

print(f"Testing {url}")
try:
    req = urllib.request.Request(url, headers=headers, method='POST')
    res = urllib.request.urlopen(req)
    print("Success:", res.read().decode('utf-8'))
except HTTPError as e:
    print(f"Error {e.code}:", e.read().decode('utf-8'))
