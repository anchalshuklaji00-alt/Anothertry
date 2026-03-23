import requests
import httpx
import time
from threading import Thread
import data_pb2
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
                print("JWT Token updated successfully.")
            else:
                print("Failed to get JWT token: Status is not success.")
        else:
            print(f"Failed to get JWT token: HTTP {response.status_code}")
    except httpx.RequestError as e:
        print(f"Request error: {e}")
def token_updater():
    while True:
        get_jwt_token()
        time.sleep(8 * 3600)
token_thread = Thread(target=token_updater, daemon=True)
token_thread.start()
time.sleep(5)
url = "https://clientbp.ggblueshark.com/GetClanInfoByClanID"
data_hex = "21 D4 A6 7D CA F8 83 22 A7 FE 4A 05 1B 40 57 22"
data_bytes = bytes.fromhex(data_hex.replace(" ", ""))
headers = {
    "Expect": "100-continue",
    "Authorization": f"Bearer {jwt_token}",
    "X-Unity-Version": "2018.4.11f1",
    "X-GA": "v1 1",
    "ReleaseVersion": "OB47",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
    "Host": "clientbp.ggblueshark.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip"
}
response = requests.post(url, headers=headers, data=data_bytes)
if response.status_code == 200:
    if response.content:
        response_message = data_pb2.response()
        response_message.ParseFromString(response.content)
        print(f"ID: {response_message.id}")
        print(f"Special Code: {response_message.special_code}")
        print(f"Timestamp1: {response_message.timestamp1}")
        print(f"Value A: {response_message.value_a}")
        print(f"Status Code: {response_message.status_code}")
        print(f"Sub Type: {response_message.sub_type}")
        print(f"Version: {response_message.version}")
        print(f"Level: {response_message.level}")
        print(f"Flags: {response_message.flags}")
        print(f"Welcome Message: {response_message.welcome_message}")
        print(f"Region: {response_message.region}")
        print(f"JSON Metadata: {response_message.json_metadata}")
        print(f"Big Numbers: {response_message.big_numbers}")
        print(f"Balance: {response_message.balance}")
        print(f"Score: {response_message.score}")
        print(f"Upgrades: {response_message.upgrades}")
        print(f"Achievements: {response_message.achievements}")
        print(f"Total Playtime: {response_message.total_playtime}")
        print(f"Energy: {response_message.energy}")
        print(f"Rank: {response_message.rank}")
        print(f"XP: {response_message.xp}")
        print(f"Timestamp2: {response_message.timestamp2}")
        print(f"Error Code: {response_message.error_code}")
        print(f"Last Active: {response_message.last_active}")
        print(f"Guild Details - Region: {response_message.guild_details.region}")
        print(f"Guild Details - Clan ID: {response_message.guild_details.clan_id}")
        print(f"Guild Details - Members Online: {response_message.guild_details.members_online}")
        print(f"Guild Details - Total Members: {response_message.guild_details.total_members}")
        print(f"Guild Details - Regional: {response_message.guild_details.regional}")
        print(f"Guild Details - Reward Time: {response_message.guild_details.reward_time}")
        print(f"Guild Details - Expire Time: {response_message.guild_details.expire_time}")
        print(f"Empty Field: {response_message.empty_field}")
    else:
        print("Received empty response from the server.")
else:
    print(f"Failed to fetch data: {response.status_code}")