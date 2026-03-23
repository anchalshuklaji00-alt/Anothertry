import my_pb2 
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
def encrypt_message(key, iv, plaintext):
    cipher = AES.new(key, AES.MODE_CBC, iv)    
    padded_message = pad(plaintext, AES.block_size)    
    encrypted_message = cipher.encrypt(padded_message)    
    return encrypted_message
message = my_pb2.UserProfile()
message.uid = int(input("Enter Uid Clan: "))
message.bio = "BOT MOD V1"
message.field3 = "BOT MOD V1"
message.field4 = 1
message.field5 = 499999
message.avatar = 19
message.frame = 19
serialized_message = message.SerializeToString()
encrypted_data = encrypt_message(AES_KEY, AES_IV, serialized_message)
hex_encrypted_data = binascii.hexlify(encrypted_data).decode('utf-8')
print(f"{hex_encrypted_data}")
