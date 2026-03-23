#GARENA APIS MADE BY FOX
#IF YOU SHARE MY SCRIPT I WELL FUCK YOU
from flask import Flask, jsonify, request; import requests; import re; import binascii; from Crypto.Cipher import AES; from Crypto.Util.Padding import pad; import zitado_pb2; from datetime import datetime; import urllib3; from concurrent.futures import ThreadPoolExecutor; import threading; from GetWishListItems_pb2 import CSGetWishListItemsReq, CSGetWishListItemsRes
#FUCK SSL BY FOX
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)
#KEYS FOR USE MY APIS BY FOX
KEYS_APIS = ["fox", "test"]
TOKEN_URL = "https://jwtgenerater.vercel.app/token?uid=3828066210&password=C41B0098956AE7B79F752FCA873C747060C71D3C17FBE4794F5EB9BD71D4DA95"
GAME_API_INFO = "https://client.ind.freefiremobile.com/GetPlayerPersonalShow"
GAME_API_EVENT = "https://client.ind.freefiremobile.com/LoginGetSplash"
GAME_API_WISHLIST = "https://client.ind.freefiremobile.com/GetWishListItems"
ENCRYPTED_UID = "03f7f38095daae1bf887928b4f2c0eb4"
FREE_FIRE_VERSION = "ob48"
#Encryption Configuration Region Ind AES-CBC
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'
HEADERS = {
    'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/x-www-form-urlencoded",
    'Expect': "100-continue",
    'X-Unity-Version': "2018.4.11f1",
    'X-GA': "v1 1",
    'ReleaseVersion': FREE_FIRE_VERSION
}
cache = {}
cache_lock = threading.Lock()
CACHE_TIMEOUT = 300
def unix_to_readable(unix_timestamp):
    return "Not In DataBAse" if unix_timestamp == 0 else datetime.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')
def convert_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else "Not In DataBase"
def get_token():
    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(requests.get, TOKEN_URL, timeout=60)
            response = future.result()
            return response.json().get("token") if response.status_code == 200 else None
    except Exception as e:
        print(f"Error getting token: {e}")
        return None
def varint_encode(n):
    buf = []
    n = (1 << 64) + n if n < 0 else n
    while n > 0x7f:
        buf.append((n & 0x7f) | 0x80)
        n >>= 7
    buf.append(n)
    return bytes(buf)
def encrypt_uid(uid):
    try:
        uid_int = int(uid)
        protobuf_data = bytes([0x08, *varint_encode(uid_int), 0x10, 0x01])
        cipher = AES.new(b'Yg&tc%DEuh6%Zc^8', AES.MODE_CBC, b'6oyZDr22E3ychjM%')
        return binascii.hexlify(cipher.encrypt(pad(protobuf_data, AES.block_size))).decode('utf-8')
    except Exception as e:
        print(f"Encryption error: {e}")
        return None
#GARENA PROTO BY FOX
def process_basic_info(user_info, users):
    return {
        'username': user_info.username,
        'region': user_info.region,
        'level': user_info.level,
        'Exp': user_info.Exp,
        'bio': users.bioinfo[0].bio if users.bioinfo else None,
        'banner': user_info.banner,
        'avatar': user_info.avatar,
        'brrankscore': user_info.brrankscore,
        'BadgeCount': user_info.BadgeCount,
        'likes': user_info.likes,
        'lastlogin': unix_to_readable(user_info.lastlogin),
        'csrankpoint': user_info.csrankpoint,
        'csrankscore': user_info.csrankscore,
        'brrankpoint': user_info.brrankpoint,
        'createat': unix_to_readable(user_info.createat),
        'OB': user_info.OB
    }
def process_clan_info(clan):
    return {
        'clanid': clan.clanid,
        'clanname': clan.clanname,
        'guildlevel': clan.guildlevel,
        'livemember': clan.livemember
    }
def process_clan_admin(admin):
    return {
        'idadmin': admin.idadmin,
        'adminname': admin.adminname,
        'level': admin.level,
        'exp': admin.exp,
        'brpoint': admin.brpoint,
        'lastlogin': unix_to_readable(admin.lastlogin),
        'cspoint': admin.cspoint
    }
def parse_response(response_data):
    users = zitado_pb2.Users()
    users.ParseFromString(response_data)    
    result = {}    
    with ThreadPoolExecutor() as executor:
        if users.basicinfo:
            result['basicinfo'] = list(executor.map(
                lambda ui: process_basic_info(ui, users),
                users.basicinfo
            ))        
        if users.claninfo:
            result['claninfo'] = list(executor.map(
                process_clan_info,
                users.claninfo
            ))        
        if users.clanadmin:
            result['clanadmin'] = list(executor.map(
                process_clan_admin,
                users.clanadmin
            ))
    return result
#GARENA FAKE PROTO BY FOX
def clean_title(title):
    title = re.sub(r'(_\w{2}\.png|\.png|_\d+x\d+.*|_en|_IND|_BR_pt)$', '', title, flags=re.IGNORECASE)
    title = title.replace('_', ' ').title()
    title = re.sub(r'[^a-zA-Z0-9\s]', '', title)  
    return title.strip()
def process_event_url(url, current_date, current_time):
    clean_url = url.strip()
    raw_title = clean_url.split('/')[-1]
    cleaned_title = clean_title(raw_title)    
    return {
        "title": cleaned_title,
        "image_url": clean_url,
        "date": current_date,
        "time": current_time
    }
#GARENA PROTO BY FOX
def process_wishlist_item(item):
    return {
        "item_id": item.item_id,
        "release_time": convert_timestamp(item.release_time)
    }
#PATH API INFO BY FOX
@app.route('/info', methods=['GET'])
def get_player_info():
    uid = request.args.get('uid')
    key = request.args.get("key")
    if not uid or not key:
        return jsonify({"error": "UID parameter is required or Key"}), 400   
    if key not in KEYS_APIS:
        return jsonify({"Fox-Keys": "Key is Not Available You Need Dm Telegram @S_DD_F"})
    cache_key = f"player_{uid}"
    with cache_lock:
        cached_data = cache.get(cache_key)
        if cached_data and (datetime.now() - cached_data['timestamp']).seconds < CACHE_TIMEOUT:
            return jsonify(cached_data['data'])
    token = get_token()
    if not token:
        return jsonify({"error": "Failed to get authentication token", "status": "error"}), 500    
    encrypted_uid = encrypt_uid(uid)
    if not encrypted_uid:
        return jsonify({"error": "Failed to encrypt UID", "status": "error"}), 500    
    headers = HEADERS.copy()
    headers['Authorization'] = f"Bearer {token}"    
    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(
                requests.post,
                GAME_API_INFO,
                data=bytes.fromhex(encrypted_uid),
                headers=headers,
                timeout=5,
                verify=False
            )
            response = future.result()          
            if response.status_code == 200:
                try:
                    parsed_data = parse_response(response.content)
                    response_data = {
                        "status": "success",
                        "data": parsed_data
                    }
                    with cache_lock:
                        cache[cache_key] = {
                            'data': response_data,
                            'timestamp': datetime.now()
                        }                    
                    return jsonify(response_data)
                except Exception as e:
                    return jsonify({
                        "error": f"Failed to parse response: {str(e)}",
                        "status": "error",
                        "raw_response": response.content.hex()
                    }), 500
            else:
                return jsonify({
                    "error": f"Game API returned status code {response.status_code}",
                    "status": "error",
                    "response": response.text
                }), 500
    except Exception as e:
        return jsonify({
            "error": f"Connection error: {str(e)}",
            "status": "error"
        }), 500
#PATH API EVENT BY FOX
@app.route('/events', methods=['GET'])
def get_events():
    key = request.args.get("key")
    if not key:
        return jsonify({"error": "parameter is required Key"}), 400   
    if key not in KEYS_APIS:
        return jsonify({"Fox-Keys": "Key is Not Available You Need Dm Telegram @S_DD_F"})
    cache_key = 'events_data'
    with cache_lock:
        cached_data = cache.get(cache_key)
        if cached_data and (datetime.now() - cached_data['timestamp']).seconds < CACHE_TIMEOUT:
            return jsonify(cached_data['data'])
    token = get_token()
    if not token:
        return jsonify({"error": "Failed to get authentication token", "status": "error"}), 500    
    headers = HEADERS.copy()
    headers['Authorization'] = f"Bearer {token}"    
    try:
        response = requests.post(
            GAME_API_EVENT,
            data=bytes.fromhex(ENCRYPTED_UID),
            headers=headers,
            timeout=5,
            verify=False
        )
        if response.status_code == 200:
            urls = re.findall(r'https?://[^\s]+\.png', response.text)
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M')            
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(
                    lambda url: process_event_url(url, current_date, current_time),
                    urls
                ))            
            response_data = {
                "status": "success",
                "events": results,
                "count": len(results),
                "date": current_date,
                "time": current_time
            }
            with cache_lock:
                cache[cache_key] = {
                    'data': response_data,
                    'timestamp': datetime.now()
                }            
            return jsonify(response_data)
        else:
            return jsonify({
                "error": f"Server returned status code {response.status_code}",
                "status": "error"
            }), 500
    except Exception as e:
        return jsonify({
            "error": f"Connection error: {str(e)}",
            "status": "error"
        }), 500
#PATH API WISHLIST BY FOX
@app.route('/wishlist', methods=['GET'])
def get_wishlist():
    uid = request.args.get('uid')
    key = request.args.get("key")
    if not uid or not key:
        return jsonify({"error": "UID parameter is required or Key"}), 400   
    if key not in KEYS_APIS:
        return jsonify({"Fox-Keys": "Key is Not Available You Need Dm Telegram @S_DD_F"})
    cache_key = f'wishlist_{uid}'
    with cache_lock:
        cached_data = cache.get(cache_key)
        if cached_data and (datetime.now() - cached_data['timestamp']).seconds < CACHE_TIMEOUT:
            return jsonify(cached_data['data'])
    with ThreadPoolExecutor() as executor:
        token_future = executor.submit(get_token)
        encrypt_future = executor.submit(encrypt_uid, uid)        
        token = token_future.result()
        encrypted_uid = encrypt_future.result()
    if not token:
        return jsonify({"error": "Failed to get authentication token", "status": "error"}), 500
    if not encrypted_uid:
        return jsonify({"error": "Failed to encrypt UID", "status": "error"}), 500
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    try:
        req = CSGetWishListItemsReq()
        req.account_id = int(uid)
        request_data = req.SerializeToString()
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        encrypted_request = cipher.encrypt(pad(request_data, AES.block_size))
        with ThreadPoolExecutor() as executor:
            future = executor.submit(
                requests.post,
                GAME_API_WISHLIST,
                headers=headers,
                data=encrypted_request,
                timeout=5
            )
            response = future.result()
            if response.status_code == 200:
                decoded_response = CSGetWishListItemsRes()
                decoded_response.ParseFromString(response.content)
                with ThreadPoolExecutor() as executor:
                    wishlist = list(executor.map(
                        process_wishlist_item,
                        decoded_response.items
                    ))
                response_data = {
                    "status": "success",
                    "uid": uid,
                    "wishlist": wishlist,
                    "count": len(wishlist),
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                with cache_lock:
                    cache[cache_key] = {
                        'data': response_data,
                        'timestamp': datetime.now()
                    }
                return jsonify(response_data)
            else:
                return jsonify({
                    "error": f"Server returned status code {response.status_code}",
                    "status": "error"
                }), 500
    except Exception as e:
        return jsonify({
            "error": f"Connection error: {str(e)}",
            "status": "error"
        }), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
#GARENA APIS MADE BY FOX
#IF YOU SHARE MY SCRIPT I WELL FUCK YOU