from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import data_pb2

# تعريف المفتاح والمتجه الأولي
key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

# إنشاء رسالة
message = message_pb2.MyMessage()
message.field2 = "59A3F3AAA0BA95A07AC274D33C130BFB2730"
message.field3 = 3
message.field5 = 3
message.field6 = b"\x01\x02\x03\x04\x05\x06\x07"
message.field8 = b"\x01\x02"

# تحويل الرسالة إلى bytes
serialized_message = message.SerializeToString()

# تشفير الرسالة باستخدام AES
cipher = AES.new(key, AES.MODE_CBC, iv)
encrypted_message = cipher.encrypt(pad(serialized_message, AES.block_size))

# حفظ الرسالة المشفرة في ملف
with open("encrypted_message.bin", "wb") as f:
    f.write(encrypted_message)

print("تم تشفير الرسالة وحفظها في ملف encrypted_message.bin")