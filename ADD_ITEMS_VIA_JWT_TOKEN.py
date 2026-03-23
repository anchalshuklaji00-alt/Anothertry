import requests

url = "https://clientbp.ggblueshark.com/SetPlayerGalleryShowInfo"
data_hex = input("ENTER HEX DATA: ")
data_bytes = bytes.fromhex(data_hex.replace(" ", ""))
token = input("ENTER TOKEN: ")
headers = {
    "Expect": "100-continue",
    "Authorization": f"Bearer {token}",
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
print(response.status_code)
print(response.text)