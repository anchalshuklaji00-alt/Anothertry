from Crypto.Cipher import AES
import binascii
import message_pb2
import requests

message = message_pb2.MyMessage()
message.field1 = "trick92838"
message.field2 = 0
message.field3 = b'b8d35edd717bed75835455e4798568bd'

plaintext = message.SerializeToString()
pad_len = 16 - len(plaintext) % 16
plaintext += bytes([pad_len] * pad_len)

key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

cipher = AES.new(key, AES.MODE_CBC, iv)
ciphertext = cipher.encrypt(plaintext)
ciphertext_hex = binascii.hexlify(ciphertext).upper()
formatted_ciphertext = ' '.join([ciphertext_hex[i:i+2].decode() for i in range(0, len(ciphertext_hex), 2)])

print(formatted_ciphertext)

url = "https://loginbp.ggblueshark.com/MajorRegister"

payload_hex = formatted_ciphertext
payload_bytes = bytes.fromhex(payload_hex.replace(" ", "")) 

headers = {
    'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 13; SM-M526B Build/TP1A.220624.014)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/octet-stream",
    'Expect': "100-continue", 
    'X-Unity-Version': "2018.4.11f1",
    'X-GA': "v1 1",
    'ReleaseVersion': "OB48",
}

response = requests.post(url, data=payload_bytes, headers=headers)
print(f"Status Code: {response.status_code}")
print("Response:")
print(response.text)