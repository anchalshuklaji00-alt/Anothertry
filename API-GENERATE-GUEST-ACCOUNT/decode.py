from Crypto.Cipher import AES
import binascii
import message_pb2

ciphertext_hex = """C7 05 D6 DE 21 75 C6 43 0D 26 4C F6 02 8F 18 83 42 46 1A 15 58 64 EE DB CB 15 2A CC 36 C7 E5 33 02 AE B3 22 E1 C4 66 36 5D 65 04 DE 41 8C D4 03 73 1C A5 58 47 6F 93 91 B5 1D 4A F0 83 FD 5F AD A6 75 B6 5F C5 12 8F F7 E9 48 4E 60 CB B0 32 9C C7 64 2A D6 04 1E F9 15 6E 7D 9E CB B2 C3 FF 46 24 7A 73 22 EB B4 25 67 A4 09 18 37 17 4C 50 98 26 86 83 85 44 85 70 75 DF 48 9F A5 27 E9 A2 77 88 00 15 E4 C7 A7 32 28 58 7B 02 7B FB 36 24 72 F9 89 1E 62 59 B1 BF CA 30 D2 A0 D8 EE 6C E7 BA 9D 98 56 3D FA 01 45 43 D8 0F 96 88 7F EB 0C D7"""
ciphertext = bytes.fromhex(ciphertext_hex.replace(" ", ""))
key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = cipher.decrypt(ciphertext)
pad_len = plaintext[-1]
plaintext = plaintext[:-pad_len]
message = message_pb2.MyMessage()  
try:
    message.ParseFromString(plaintext)
    print(" 1:", message.field1)
    print(" 2:", message.field2)
    print(" 3:", message.field3)
except Exception as e:
    print("Erro:", e)
