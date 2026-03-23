import requests

data = bytes.fromhex("06 67 54 a1 de 93 c4 d0 5b ba 9c 64 41 d8 f6 ec")
token = "eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ.eyJhY2NvdW50X2lkIjoxMTA1ODEzMjgxMywibmlja25hbWUiOiJDT0RFWC1CT1QtWCIsIm5vdGlfcmVnaW9uIjoiTUUiLCJsb2NrX3JlZ2lvbiI6Ik1FIiwiZXh0ZXJuYWxfaWQiOiIyOTdhNjI4YThkNzM1OGFjY2MwZjllODA5NWYwYTc4OCIsImV4dGVybmFsX3R5cGUiOjQsInBsYXRfaWQiOjEsImNsaWVudF92ZXJzaW9uIjoiMS4xMDguMyIsImVtdWxhdG9yX3Njb3JlIjowLCJpc19lbXVsYXRvciI6ZmFsc2UsImNvdW50cnlfY29kZSI6IlVTIiwiZXh0ZXJuYWxfdWlkIjozNzQyMjgyMDc1LCJyZWdfYXZhdGFyIjoxMDIwMDAwMDcsInNvdXJjZSI6MCwibG9ja19yZWdpb25fdGltZSI6MTczODkzMzY0OCwiY2xpZW50X3R5cGUiOjIsInNpZ25hdHVyZV9tZDUiOiI3NDI4YjI1M2RlZmMxNjQwMThjNjA0YTFlYmJmZWJkZiIsInVzaW5nX3ZlcnNpb24iOjEsInJlbGVhc2VfY2hhbm5lbCI6ImFuZHJvaWQiLCJyZWxlYXNlX3ZlcnNpb24iOiJPQjQ4IiwiZXhwIjoxNzQwODE5NDAyfQ.ISrwzOO-tMb3esbGKilkQ3kfKI74YVojDJc7jJOw3ks"
url = "https://clientbp.ggblueshark.com/Leaderboard"
headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB48",
        "Host": "clientbp.common.ggbluefox.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "User-Agent": "Free%20Fire/2019117061 CFNetwork/1399 Darwin/22.1.0",
        "Connection": "keep-alive",
        "Authorization": f"Bearer {token}",
        "X-Unity-Version": "2018.4.11f1",
        "Accept": "/"
}
response = requests.post(url, headers=headers, data=data, verify=False)
print(response.text)