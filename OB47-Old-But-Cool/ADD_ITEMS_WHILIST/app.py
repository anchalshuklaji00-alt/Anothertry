from flask import Flask, jsonify, request
import requests
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import threading
import warnings
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import reflection as _reflection 
from google.protobuf import message as _message 
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x08my.proto\"\x13\n\x05Items\x12\n\n\x02id\x18\x01 \x01(\x03\x62\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'my_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _ITEMS = DESCRIPTOR.message_types_by_name['Items']
    Items = _reflection.GeneratedProtocolMessageType('Items', (_message.Message,), {
        'DESCRIPTOR': _ITEMS,
        '__module__': 'my_pb2'
    })
    _sym_db.RegisterMessage(Items)
app = Flask(__name__)
key = "Yg&tc%DEuh6%Zc^8".encode()
iv = "6oyZDr22E3ychjM%".encode()
items_to_send = [
    909038002, 909047003, 909047015, 909047019, 909547001,
    911004701, 912047002, 914047001, 922044002, 1001000001,
    1001000002, 1001000003, 1001000004, 1001000005, 1001000006,
    1001000007, 1001000008, 1001000009, 1001000010, 1001000011,
    1001000012, 1001000013, 1001000014, 1001000015, 1001000016,
    1001000017, 1001000018, 1001000019, 1001000020, 1001000021,
    1001000022, 1001000023, 1001000024, 1001000025, 1001000026,
    1001000027, 1001000028, 1001000029, 1001000030, 1001000031,
    1001000032, 1001000033, 1001000034, 1001000035, 1001000036,
    1001000037, 1001000038, 1001000039, 1001000040, 1001000041,
    1001000042, 1001000043, 1001000044, 1001000045, 801000020, 801000015, 801000016, 827001001, 801000213,
    801000144, 801000140, 801000139, 801000089
]
def encrypt_aes(hex_data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(bytes.fromhex(hex_data), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return binascii.hexlify(encrypted_data).decode()
def wishlistItems_payload(id):
    g = globals()['Items']()
    g.id = id
    serialized_data = g.SerializeToString()
    hex_data = binascii.hexlify(serialized_data).decode("utf-8")
    encrypted_data = encrypt_aes(hex_data)
    return encrypted_data
def add_item(token, encrypted_payload, item_id):
    api = "https://clientbp.ggblueshark.com/ChangeWishListItem"
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/octet-stream",
        'Expect': "100-continue",
        'Authorization': "Bearer " + token,
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB47"
    }
    response = requests.post(api, data=bytes.fromhex(encrypted_payload), headers=headers, verify=False)
    return response.status_code
@app.route('/add-to-wishlist/<path:token>', methods=['GET'])
def add_to_wishlist(token):
    if not token:
        return jsonify({"error": "Token is missing!"}), 401

    threads = []
    results = []

    for item_id in items_to_send:
        encrypted_payload = wishlistItems_payload(item_id)
        thread = threading.Thread(target=lambda: results.append(add_item(token, encrypted_payload, item_id)))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    if all(status == 200 for status in results):
        return jsonify({"message": "Items have been successfully added to the wishlist. Developed by FOX CODEX TEAM"}), 200
    else:
        return jsonify({"error": "Some items could not be added."}), 500

if __name__ == "__main__":
    warnings.filterwarnings("ignore", message="Unverified HTTPS request")
    app.run(debug=False)