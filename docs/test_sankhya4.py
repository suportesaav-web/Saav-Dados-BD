import urllib.request
import base64
from urllib.error import HTTPError

client_id = '11026a04-b106-4507-a748-5b8bb1431e1a'
secret = 'a4fQUBl8WHc9DGD69yQKD0gqN14tgOG5'
x_token = '9db56f27-0792-44f2-8c51-0d353664af26'

auth = base64.b64encode(f'{client_id}:{secret}'.encode()).decode()

def test(url, headers, data=None):
    print(f"Testing {url} with headers {headers}")
    try:
        req = urllib.request.Request(url, method='POST', headers=headers, data=data)
        print("Success:", urllib.request.urlopen(req).read().decode())
    except HTTPError as e:
        print(f"Error {e.code}:", e.read().decode())

test('https://api.sandbox.sankhya.com.br/api/authenticate', {'Authorization': f'Basic {auth}'})
test('https://api.sandbox.sankhya.com.br/api/authenticate', {'Authorization': f'Bearer {x_token}'})
test('https://api.sandbox.sankhya.com.br/login', {'appkey': client_id, 'token': x_token, 'Content-Type': 'application/json'}, b'{}')
