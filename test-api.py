import http.client
import json

def get_token():
    conn = http.client.HTTPConnection("127.0.0.1:8000")
    conn.request("POST",
                 "/login/",
                 '{"email": "user@example.com", "password": "string"}',
                 headers={'Content-Type': 'application/json'})
    return json.loads(conn.getresponse().read().decode())['token']

token = get_token()
print(get_token())

conn = http.client.HTTPConnection("127.0.0.1:8000")
conn.request("GET", 
             "/course/grammar-a1/", 
             headers={'Content-Type': 'application/json', 
                      'Authorization': f'Bearer {token}'})

print(conn.getresponse().read().decode())