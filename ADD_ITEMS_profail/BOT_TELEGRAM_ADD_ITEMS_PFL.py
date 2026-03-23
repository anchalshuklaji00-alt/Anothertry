import telebot
from telebot import types
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
import requests
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ndata.proto\x12\x07\x65xample\"\x18\n\tNestedSix\x12\x0b\n\x03six\x18\x06 \x01(\x05\"q\n\tInnerData\x12\x0b\n\x03one\x18\x01 \x01(\x05\x12\x0b\n\x03two\x18\x02 \x01(\x05\x12\r\n\x05three\x18\x03 \x01(\x05\x12\x0c\n\x04\x66our\x18\x04 \x01(\x05\x12\x0c\n\x04\x66ive\x18\x05 \x01(\x05\x12\x1f\n\x03six\x18\x06 \x01(\x0b\x32\x12.example.NestedSix\":\n\nNestedData\x12\x0b\n\x03one\x18\x01 \x01(\x05\x12\x1f\n\x03two\x18\x02 \x03(\x0b\x32\x12.example.InnerData\"5\n\x04\x44\x61ta\x12\x0b\n\x03one\x18\x01 \x01(\x05\x12 \n\x03two\x18\x02 \x03(\x0b\x32\x13.example.NestedDatab\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'data_pb2', _globals)
TOKEN = "8631579637:AAEQUi0msNC9-KSnpYpMSmmi97z-Cd8oX78"
bot = telebot.TeleBot(TOKEN)
key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
def format_encrypted_data(encrypted_data):
    return binascii.hexlify(encrypted_data).decode().upper()
def encrypt_data(user_id):
    data = _globals['Data']()
    data.one = 1
    nested_1 = data.two.add()
    nested_1.one = 1
    entries = [
        {"one": 2, "six": user_id},
        {"one": 2, "five": 2, "six": user_id},
        {"one": 2, "five": 4, "six": user_id},
        {"one": 2, "four": 2, "six": user_id},
        {"one": 2, "four": 2, "five": 2, "six": user_id},
        {"one": 2, "four": 2, "five": 4, "six": user_id},
        {"one": 2, "three": 1, "four": 2, "six": user_id},
        {"one": 2, "three": 1, "five": 2, "six": user_id},
        {"one": 2, "three": 1, "five": 4, "six": user_id},
        {"one": 2, "three": 1, "four": 2, "five": 2, "six": user_id},
        {"one": 2, "three": 1, "four": 4, "six": user_id},
        {"one": 9, "two": 9, "three": 1, "four": 4, "five": 2, "six": user_id},
    ]
    for entry in entries:
        inner_data = nested_1.two.add()
        inner_data.one = entry["one"]
        inner_data.two = entry.get("two", 0)
        inner_data.three = entry.get("three", 0)
        inner_data.four = entry.get("four", 0)
        inner_data.five = entry.get("five", 0)
        inner_data.six.six = entry["six"]
    nested_2 = data.two.add()
    nested_2.one = 5
    inner_data_2 = nested_2.two.add()
    inner_data_2.three = 1
    inner_data_2.four = 6
    serialized_data = data.SerializeToString()
    padded_data = pad(serialized_data, AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(padded_data)
    return format_encrypted_data(encrypted_data)
def send_to_server(data_hex, token):
    url = "https://clientbp.ggblueshark.com/SetPlayerGalleryShowInfo"
    data_bytes = bytes.fromhex(data_hex.replace(" ", ""))
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
    return response.status_code, response.text
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = """
    Welcome to the Codex Bot! 🚀

    This bot allows you to:
    1. Encrypt user IDs and add them to your profile.
    2. Use a single UID for all fields.
    3. Send encrypted data to the server.

    Available commands:
    - /encrypt <UID>: Encrypt a single UID and use it in all fields.
    - /additems <encrypted_data> <token>: Send encrypted data to the server.

    Made with ❤️ by @S_DD_F & @l7l7aj
    """
    bot.send_message(message.chat.id, welcome_message)
@bot.message_handler(commands=['encrypt'])
def handle_encrypt_command(message):
    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.send_message(message.chat.id, "⚠️ Usage: /encrypt <UID>")
            return        
        user_id = command_parts[1]
        user_id_int = int(user_id)
        encrypted_data = encrypt_data(user_id_int)
        bot.send_message(message.chat.id, f"🔐 Encrypted data:\n`{encrypted_data}`", parse_mode="Markdown")
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Please enter a valid number.")
@bot.message_handler(commands=['encr'])
def handle_encrypt_multiple_ids(message):
    try:
        # استخراج المعرفات من الأمر
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.send_message(message.chat.id, "⚠️ Usage: /encr <UID1> <UID2> <UID3> ...")
            return

        user_ids = []
        invalid_ids = []

        # التحقق من صحة المعرفات
        for uid in command_parts[1:]:
            try:
                user_ids.append(int(uid))  # تحويل إلى int
            except ValueError:
                invalid_ids.append(uid)  # حفظ المعرفات غير الصالحة

        if invalid_ids:
            bot.send_message(message.chat.id, f"⚠️ Invalid IDs: {', '.join(invalid_ids)}")
            return

        # إنشاء كائن البيانات
        data = _globals['Data']()
        data.one = 1
        nested_1 = data.two.add()
        nested_1.one = 1

        # إدخال جميع المعرفات في الـ entries، مع السماح بالتكرار
        for user_id in user_ids:
            entries = [
                {"one": 2, "six": user_id},
                {"one": 2, "five": 2, "six": user_id},
                {"one": 2, "five": 4, "six": user_id},
                {"one": 2, "four": 2, "six": user_id},
                {"one": 2, "four": 2, "five": 2, "six": user_id},
                {"one": 2, "four": 2, "five": 4, "six": user_id},
                {"one": 2, "three": 1, "four": 2, "six": user_id},
                {"one": 2, "three": 1, "five": 2, "six": user_id},
                {"one": 2, "three": 1, "five": 4, "six": user_id},
                {"one": 2, "three": 1, "four": 2, "five": 2, "six": user_id},
                {"one": 2, "three": 1, "four": 4, "six": user_id},
                {"one": 9, "two": 9, "three": 1, "four": 4, "five": 2, "six": user_id},
            ]
            for entry in entries:
                inner_data = nested_1.two.add()
                inner_data.one = entry["one"]
                inner_data.two = entry.get("two", 0)
                inner_data.three = entry.get("three", 0)
                inner_data.four = entry.get("four", 0)
                inner_data.five = entry.get("five", 0)
                inner_data.six.six = entry["six"]

        # إضافة NestedData ثاني
        nested_2 = data.two.add()
        nested_2.one = 5

        inner_data_2 = nested_2.two.add()
        inner_data_2.three = 1
        inner_data_2.four = 6

        # تسلسل البيانات باستخدام Protobuf
        serialized_data = data.SerializeToString()

        # تطبيق التشفير AES/CBC
        padded_data = pad(serialized_data, AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(padded_data)

        # تنسيق الناتج المشفر
        encrypted_hex = format_encrypted_data(encrypted_data)
        
        # إرسال النتيجة
        bot.send_message(message.chat.id, f"🔐 Encrypted Data:\n`{encrypted_hex}`", parse_mode="Markdown")
    
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ An error occurred: {e}")
@bot.message_handler(commands=['additems'])
def handle_add_items_command(message):
    try:
        command_parts = message.text.split()
        if len(command_parts) < 3:
            bot.send_message(message.chat.id, "⚠️ Usage: /additems <encrypted_data> <token>")
            return        
        encrypted_data = command_parts[1]
        token = command_parts[2]        
        if not all(c in "0123456789ABCDEFabcdef" for c in encrypted_data):
            bot.send_message(message.chat.id, "⚠️ Invalid encrypted data. Please enter valid HEX data.")
            return
        status_code, response_text = send_to_server(encrypted_data, token)
        bot.send_message(message.chat.id, f"📤 Data sent to server.\n\n**Result:**\n- Status code: `{status_code}`\n- Text: `{response_text}`", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ An error occurred: {e}")
bot.polling()
