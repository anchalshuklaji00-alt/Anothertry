import httpx
import time
import concurrent.futures
from byte import encrypt_api, Encrypt_ID
to = "eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ.eyJhY2NvdW50X2lkIjo5NzU5MzYzMTQxLCJuaWNrbmFtZSI6IuKAlM2ezZ_imIXvvLLvvKXvvJfvvKLvvKHvvKzjhaQiLCJub3RpX3JlZ2lvbiI6Ik1FIiwibG9ja19yZWdpb24iOiJNRSIsImV4dGVybmFsX2lkIjoiYzI4MGQzNTg4MDcxYjg4MTE3NjZlZDE4N2JjYTQ2MmIiLCJleHRlcm5hbF90eXBlIjo4LCJwbGF0X2lkIjoxLCJjbGllbnRfdmVyc2lvbiI6IjEuMTA4LjE0IiwiZW11bGF0b3Jfc2NvcmUiOjAsImlzX2VtdWxhdG9yIjpmYWxzZSwiY291bnRyeV9jb2RlIjoiTUEiLCJleHRlcm5hbF91aWQiOjE5MjMwMDExNjkzNjIsInJlZ19hdmF0YXIiOjEwMjAwMDAwNSwic291cmNlIjowLCJsb2NrX3JlZ2lvbl90aW1lIjoxNzIyODAyNTUxLCJjbGllbnRfdHlwZSI6Miwic2lnbmF0dXJlX21kNSI6Ijc0MjhiMjUzZGVmYzE2NDAxOGM2MDRhMWViYmZlYmRmIiwidXNpbmdfdmVyc2lvbiI6MSwicmVsZWFzZV9jaGFubmVsIjoiYW5kcm9pZCIsInJlbGVhc2VfdmVyc2lvbiI6Ik9CNDciLCJleHAiOjE3MzkxNTA5NTh9.mNHcRon4alcBaIkHLsafNSx9jcegyMyaCEY34baUcS4"
def Get_player_information(player_id):
    encrypted_id = Encrypt_ID(player_id)
    encrypted_api = encrypt_api(f"08{encrypted_id}1007")       
    TARGET = bytes.fromhex(encrypted_api)
    url = "https://clientbp.common.ggbluefox.com/GetPlayerPersonalShow"
    headers = {
        "Authorization": f"Bearer {to}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB47",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-N975F Build/PI)",
        "Host": "clientbp.common.ggbluefox.com",
        "Connection": "close",
        "Accept-Encoding": "gzip, deflate, br",
    }    
    try:
        with httpx.Client(verify=False) as client:
            response = client.post(url, headers=headers, data=TARGET)
        if response.status_code == 200:
            print(f"[{player_id}]GOOD VISIT✅")
        else:
            pass
    except httpx.RequestError as e:
        pass
def fetch_100_requests_per_second():
    player_ids = [10414593349 + i for i in range(1000)] 
    with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
        executor.map(Get_player_information, player_ids)
    time.sleep(0.01)
while True:
    fetch_100_requests_per_second()