import requests
hex = bytes.fromhex("76e634b964c9c04b1b239b6509c15576273fe008b461c317d333e1944c52e09b500010f007e9b60e2da2ad80f9ed354b")
api = "https://clientbp.ggblueshark.com/ModifyClanInfo"
payload = hex
token = ""
headers = {
    'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/octet-stream",
    'Expect': "100-continue",
    'Authorization': f"Bearer {token}",
    'X-GA': "v1 1",
    'ReleaseVersion': "OB52"
}
response = requests.post(api, data=payload, headers=headers)
guest = response.content.hex()
print(guest)
