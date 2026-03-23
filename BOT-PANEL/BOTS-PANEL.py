import requests
import time
import threading
import httpx
jwt_token = None
def get_jwt_token():
    global jwt_token
    url = "https://app-py-amber.vercel.app/get?uid=3742282075&password=B8B4818D83BAAFBA62FEA1447285A5246AD3DFFB5A8D3FC08CC1E3FB4D9BE534"
    try:
        response = httpx.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                jwt_token = data['token']
                #print("JWT Token updated successfully.")
            else:
                #print("Failed to get JWT token: Status is not success.")
                pass
        else:
            print(f"Failed to get JWT token: HTTP {response.status_code}")
    except httpx.RequestError as e:
        print(f"Request error: {e}")
def token_updater():
    while True:
        get_jwt_token()
        time.sleep(8 * 3600)
token_thread = threading.Thread(target=token_updater, daemon=True)
token_thread.start()
print("========================================================================")
choise = input("""                WELCOM IN CODEX BOT-X PANEL:
ENTER=>[1]FOR ADD CLIENT!
ENTER=>[2]FOR REMEV CLIENT!""")
print("==================================")
if choise == "1":
    uid = input("ENTER UID: ")
    url = f"https://foxaddingid.vercel.app/adding_friend?token={jwt_token}&id={uid}"
    res = requests.get(url)
    print(res.json())
elif choise == "2":
    uid = input("ENTER UID: ")
    url = f"https://foxremevid.vercel.app/remove_friend?token={jwt_token}&id={uid}"
    res = requests.get(url)
    print(res.json())