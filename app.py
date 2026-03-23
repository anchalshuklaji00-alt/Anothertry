from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii
import requests
from flask import Flask, jsonify, request
from data_pb2 import AccountPersonalShowInfo
from google.protobuf.json_format import MessageToDict
import uid_generator_pb2
from GetWishListItems_pb2 import CSGetWishListItemsRes
from datetime import datetime
import threading
import time
import re
####################################
app = Flask(__name__)
freefire_version = "ob48"
APIS_KEYS = ["CdxGfoxProjext1kmembers", "nikmok"]
##########PLAYER INFO################
jwt_token = None
jwt_lock = threading.Lock()
def extract_token_from_response(data, region):
    if region == "IND":
        if data.get('status') in ['success', 'live']:
            return data.get('token')
    elif region in ["BR", "US", "SAC", "NA"]:
        if isinstance(data, dict) and 'token' in data:
            return data['token']
    else: 
        if data.get('status') == 'success':
            return data.get('token')
    return None
def get_jwt_token_sync(region):
    global jwt_token
    endpoints = {
        "IND": "https://jwtgenerater.vercel.app/token?uid=3828066210&password=C41B0098956AE7B79F752FCA873C747060C71D3C17FBE4794F5EB9BD71D4DA95",
        "BR": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=3787481313&password=JlOivPeosauV0l9SG6gwK39lH3x2kJkO",
        "US": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=3787481313&password=JlOivPeosauV0l9SG6gwK39lH3x2kJkO",
        "SAC": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=3787481313&password=JlOivPeosauV0l9SG6gwK39lH3x2kJkO",
        "NA": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=3787481313&password=JlOivPeosauV0l9SG6gwK39lH3x2kJkO",
        "default": "https://projects-fox-x-get-jwt.vercel.app/get?uid=3763606630&password=7FF33285F290DDB97D9A31010DCAA10C2021A03F27C4188A2F6ABA418426527C"
    }    
    url = endpoints.get(region, endpoints["default"])
    with jwt_lock:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                token = extract_token_from_response(data, region)
                if token:
                    jwt_token = token
                    print(f"JWT Token for {region} updated successfully: {token[:50]}...")
                    return jwt_token
                else:
                    print(f"Failed to extract token from response for {region}")
            else:
                print(f"Failed to get JWT token for {region}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Request error for {region}: {e}")   
    return None
def ensure_jwt_token_sync(region):
    global jwt_token
    if not jwt_token:
        print(f"JWT token for {region} is missing. Attempting to fetch a new one...")
        return get_jwt_token_sync(region)
    return jwt_token
def jwt_token_updater(region):
    while True:
        get_jwt_token_sync(region)
        time.sleep(300)
def get_api_endpoint(region):
    endpoints = {
        "IND": "https://client.ind.freefiremobile.com/GetPlayerPersonalShow",
        "BR": "https://client.us.freefiremobile.com/GetPlayerPersonalShow",
        "US": "https://client.us.freefiremobile.com/GetPlayerPersonalShow",
        "SAC": "https://client.us.freefiremobile.com/GetPlayerPersonalShow",
        "NA": "https://client.us.freefiremobile.com/GetPlayerPersonalShow",
        "default": "https://clientbp.ggblueshark.com/GetPlayerPersonalShow"
    }
    return endpoints.get(region, endpoints["default"])
key = "Yg&tc%DEuh6%Zc^8"
iv = "6oyZDr22E3ychjM%"
def encrypt_aes(hex_data, key, iv):
    key = key.encode()[:16]
    iv = iv.encode()[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(bytes.fromhex(hex_data), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return binascii.hexlify(encrypted_data).decode()
def apis(idd, region):
    global jwt_token    
    token = ensure_jwt_token_sync(region)
    if not token:
        raise Exception(f"Failed to get JWT token for region {region}")    
    endpoint = get_api_endpoint(region)    
    headers = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)',
        'Connection': 'Keep-Alive',
        'Expect': '100-continue',
        'Authorization': f'Bearer {token}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': freefire_version,
        'Content-Type': 'application/x-www-form-urlencoded',
    }    
    try:
        data = bytes.fromhex(idd)
        response = requests.post(
            endpoint,
            headers=headers,
            data=data,
            timeout=10
        )
        response.raise_for_status()
        return response.content.hex()
    except requests.exceptions.RequestException as e:
        print(f"API request to {endpoint} failed: {e}")
        raise
@app.route('/accinfo', methods=['GET'])
def get_player_info():
    try:
        uid = request.args.get('uid')
        
        region = request.args.get('region', 'default').upper()
        code = request.args.get("api_key")
        if not uid or not code:
            return jsonify({"error": "UID parameter is required Or Key"}), 400
        if code not in APIS_KEYS:
            return jsonify({"ErrorKey": "Key is Not Available You Need Dm Telegram @S_DD_F"}), 400
        custom_key = request.args.get('key', key)
        custom_iv = request.args.get('iv', iv)
        threading.Thread(target=jwt_token_updater, args=(region,), daemon=True).start()
        message = uid_generator_pb2.uid_generator()
        message.saturn_ = int(uid)
        message.garena = 1
        protobuf_data = message.SerializeToString()
        hex_data = binascii.hexlify(protobuf_data).decode()
        encrypted_hex = encrypt_aes(hex_data, custom_key, custom_iv)
        api_response = apis(encrypted_hex, region) 
        if not api_response:
            return jsonify({"error": "Empty response from API"}), 400
        message = AccountPersonalShowInfo()
        message.ParseFromString(bytes.fromhex(api_response)) 
        result = MessageToDict(message)
        result['Owners'] = ['ProjectS FoxX!!']
        return jsonify(result)
    except ValueError:
        return jsonify({"error": "Invalid UID format"}), 400
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": f"Failure to process the data: {str(e)}"}), 500
##########INFO WISHLIST###############
def convert_timestamp(release_time):
    return datetime.utcfromtimestamp(release_time).strftime('%Y-%m-%d %H:%M:%S')
def GetJwtTokenToWishList(data, region):
    if region == "IND":
        if data.get('status') in ['success', 'live']:
            return data.get('token')
    elif region in ["BR", "US", "SAC", "NA"]:
        if isinstance(data, dict) and 'token' in data:
            return data['token']
    else: 
        if data.get('status') == 'success':
            return data.get('token')
    return None
def GetJwtTokenSyncWishList(region):
    global jwt_token
    endpoints = {
        "IND": "https://jwtgenerater-gamma.vercel.app/token?uid=3828066210&password=C41B0098956AE7B79F752FCA873C747060C71D3C17FBE4794F5EB9BD71D4DA95",
        "BR": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=3787481313&password=JlOivPeosauV0l9SG6gwK39lH3x2kJkO",
        "US": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=3787481313&password=JlOivPeosauV0l9SG6gwK39lH3x2kJkO",
        "SAC": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=3787481313&password=JlOivPeosauV0l9SG6gwK39lH3x2kJkO",
        "NA": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=3787481313&password=JlOivPeosauV0l9SG6gwK39lH3x2kJkO",
        "default": "https://projects-fox-x-get-jwt.vercel.app/get?uid=3763606630&password=7FF33285F290DDB97D9A31010DCAA10C2021A03F27C4188A2F6ABA418426527C"
    }    
    url = endpoints.get(region, endpoints["default"])
    with jwt_lock:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                token = GetJwtTokenToWishList(data, region)
                if token:
                    jwt_token = token
                    print(f"JWT Token for {region} updated successfully: {token[:50]}...")
                    return jwt_token
                else:
                    print(f"Failed to extract token from response for {region}")
            else:
                print(f"Failed to get JWT token for {region}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Request error for {region}: {e}")   
    return None
def EnsureJwtTokenSyncWishlist(region):
    global jwt_token
    if not jwt_token:
        print(f"JWT token for {region} is missing. Attempting to fetch a new one...")
        return GetJwtTokenSyncWishList(region)
    return jwt_token
def JwtToken8h(region):
    while True:
        GetJwtTokenSyncWishList(region)
        time.sleep(300)
def GetWishListEndpoint(region):
    endpoints = {
        "IND": "https://client.ind.freefiremobile.com/GetWishListItems",
        "BR": "https://client.us.freefiremobile.com/GetWishListItems",
        "US": "https://client.us.freefiremobile.com/GetWishListItems",
        "SAC": "https://client.us.freefiremobile.com/GetWishListItems",
        "NA": "https://client.us.freefiremobile.com/GetWishListItems",
        "default": "https://clientbp.ggblueshark.com/GetWishListItems"
    }
    return endpoints.get(region, endpoints["default"])
key = "Yg&tc%DEuh6%Zc^8"
iv = "6oyZDr22E3ychjM%"
def encrypt_aes(hex_data, key, iv):
    key = key.encode()[:16]
    iv = iv.encode()[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(bytes.fromhex(hex_data), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return binascii.hexlify(encrypted_data).decode()
def HostsGetInfoWishLsit(idd, region):
    global jwt_token    
    token = EnsureJwtTokenSyncWishlist(region)
    if not token:
        raise Exception(f"Failed to get JWT token for region {region}")    
    endpoint = GetWishListEndpoint(region)    
    headers = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)',
        'Connection': 'Keep-Alive',
        'Expect': '100-continue',
        'Authorization': f'Bearer {token}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': freefire_version,
        'Content-Type': 'application/x-www-form-urlencoded',
    }    
    try:
        data = bytes.fromhex(idd)
        response = requests.post(
            endpoint,
            headers=headers,
            data=data,
            timeout=10
        )
        response.raise_for_status()
        return response.content.hex()
    except requests.exceptions.RequestException as e:
        print(f"API request to {endpoint} failed: {e}")
        raise
@app.route('/wish', methods=['GET'])
def GetIdInfoWishLsit():
    try:
        uid = request.args.get('uid')
        region = request.args.get('region', 'default').upper()
        code = request.args.get("api_key")
        if not uid or not code:
            return jsonify({"error": "UID parameter is required Or Key"}), 400
        if code not in APIS_KEYS:
            return jsonify({"ErrorKey": "Key is Not Available You Need Dm Telegram @S_DD_F"}), 400
        custom_key = request.args.get('key', key)
        custom_iv = request.args.get('iv', iv)        
        if not uid:
            return jsonify({"error": "UID parameter is required"}), 400          
        threading.Thread(target=JwtToken8h, args=(region,), daemon=True).start()
        message = uid_generator_pb2.uid_generator()
        message.saturn_ = int(uid)
        message.garena = 1
        protobuf_data = message.SerializeToString()
        hex_data = binascii.hexlify(protobuf_data).decode()
        encrypted_hex = encrypt_aes(hex_data, custom_key, custom_iv)
        api_response_hex = HostsGetInfoWishLsit(encrypted_hex, region)         
        if not api_response_hex:
            return jsonify({"error": "Empty response from API"}), 400
        api_response_bytes = bytes.fromhex(api_response_hex)
        decoded_response = CSGetWishListItemsRes()
        decoded_response.ParseFromString(api_response_bytes)    
        wishlist = [
            {
                "item_id": item.item_id, 
                "release_time": convert_timestamp(item.release_time)
            }
            for item in decoded_response.items
        ]            
        return jsonify({"uid": uid, "wishlist": wishlist})  
    except ValueError:
        return jsonify({"error": "Invalid UID format"}), 400
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": f"Failure to process the data: {str(e)}"}), 500
##########GAME EVENTES##############
cache = {}
cache_lock = threading.Lock()
def GetJwtTokenToEventes(data, region):
    if region == "IND":
        if data.get('status') in ['success', 'live']:
            return data.get('token')
    elif region in ["BR", "US", "SAC", "NA"]:
        if isinstance(data, dict) and 'token' in data:
            return data['token']
    else: 
        if data.get('status') == 'success':
            return data.get('token')
    return None

def GetJwtTokenSyncEventes(region):
    global jwt_token
    endpoints = {
        "IND": "https://jwtgenerater.vercel.app/token?uid=3828066210&password=C41B0098956AE7B79F752FCA873C747060C71D3C17FBE4794F5EB9BD71D4DA95",
        "BR": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=3787481313&password=JlOivPeosauV0l9SG6gwK39lH3x2kJkO",
        "US": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=&password=",
        "SAC": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=&password=",
        "NA": "https://tokenalljwt.onrender.com/api/oauth_guest?uid=3787481313&password=JlOivPeosauV0l9SG6gwK39lH3x2kJkO",
        "ME": "https://projects-fox-x-get-jwt.vercel.app/get?uid=3763606630&password=7FF33285F290DDB97D9A31010DCAA10C2021A03F27C4188A2F6ABA418426527C",
        "SG": "https://projects-fox-x-get-jwt.vercel.app/get?uid=3829602603&password=601849AE2D73FC68E34E84240DF09B814C270876365CEFBA454861A6B264199B",
        "CIS": "https://projects-fox-x-get-jwt.vercel.app/get?uid=3804678376&password=CC026379A10A6ABAEEE7C48C6E0AEA3A5361603C9481165AD06E6E4689912596",
        "BD": "https://projects-fox-x-get-jwt.vercel.app/get?uid=3533430236&password=A284E7DD367F808EB079EAF4DDE85AB4F977A249E510A3A168298FE44011BB93"
    }
    url = endpoints.get(region, endpoints["IND"])
    with jwt_lock:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                token = GetJwtTokenToEventes(data, region)
                if token:
                    jwt_token = token
                    print(f"JWT Token for {region} updated successfully: {token[:50]}...")
                    return jwt_token
                else:
                    print(f"Failed to extract token from response for {region}")
            else:
                print(f"Failed to get JWT token for {region}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Request error for {region}: {e}")   
    return None

def EnsureJwtTokenSyncEventes(region):
    global jwt_token
    if not jwt_token:
        print(f"JWT token for {region} is missing. Attempting to fetch a new one...")
        return GetJwtTokenSyncEventes(region)
    return jwt_token

def JwtToken8hh(region):
    while True:
        GetJwtTokenSyncEventes(region)
        time.sleep(300)

def HostsGetGameEventes(region):
    endpoints = {
        "IND": "https://client.ind.freefiremobile.com/LoginGetSplash",
        "BR": "https://client.us.freefiremobile.com/LoginGetSplash",
        "US": "https://client.us.freefiremobile.com/LoginGetSplash",
        "SAC": "https://client.us.freefiremobile.com/LoginGetSplash",
        "NA": "https://client.us.freefiremobile.com/LoginGetSplash",
        "ME": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "CIS": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "SG": "https://clientbp.ggblueshark.com/LoginGetSplash",
        "BD": "https://clientbp.ggblueshark.com/LoginGetSplash"
    }
    return endpoints.get(region, endpoints["IND"])

def GetEventesEndpoint(idd, region):
    global jwt_token    
    token = EnsureJwtTokenSyncEventes(region)
    if not token:
        raise Exception(f"Failed to get JWT token for region {region}")    
    endpoint = HostsGetGameEventes(region)    
    headers = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)',
        'Connection': 'Keep-Alive',
        'Expect': '100-continue',
        'Authorization': f'Bearer {token}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': freefire_version,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    region_data = {
        "IND": "03f7f38095daae1bf887928b4f2c0eb4",
        "BR": "",
        "US": "",
        "SAC": "",
        "NA": "9223af2eab91b7a150d528f657731074",
        "BD": "9223af2eab91b7a150d528f657731074",
        "ME": "9223af2eab91b7a150d528f657731074",
        "CIS": "5b 27 f0 86 9e 37 f9 2b 6f 84 c3 a7 39 34 7d b1",
        "SG": "9223af2eab91b7a150d528f657731074"
    }
    
    data_hex = region_data.get(region, "")
    if not data_hex:
        raise Exception("Invalid region or missing data")
    
    try:
        data = bytes.fromhex(data_hex)
        response = requests.post(
            endpoint,
            headers=headers,
            data=data,
            timeout=10
        )
        response.raise_for_status()
        return response.content.hex()
    except requests.exceptions.RequestException as e:
        print(f"API request to {endpoint} failed: {e}")
        raise

@app.route('/eventes', methods=['GET'])
def GetGameEventes():
    try:
        region = request.args.get('region', 'IND').upper()
        code = request.args.get("api_key")
        if not code:
            return jsonify({"error": " code parameter is required"}), 400
        if code not in APIS_KEYS:
            return jsonify({"ErrorKey": "Key is Not Available You Need Dm Telegram @S_DD_F"}), 400
        
        cache_key = f"{region}_{key}"
        with cache_lock:
            cached = cache.get(cache_key)
            if cached and (datetime.now() - cached['timestamp']).seconds < 300:
                return jsonify(cached['data'])
        
        response_hex = GetEventesEndpoint(key, region)
        if not response_hex:
            return jsonify({"error": "Failed to get response from API"}), 500
            
        response_text = binascii.unhexlify(response_hex).decode('utf-8', errors='ignore')
        urls = re.findall(r'https?://[^\s]+\.png', response_text)
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        
        results = []
        for url in urls:
            clean_url = url.strip()
            event_name = clean_url.split('/')[-1].replace('_880x520_BR_pt.png', '').replace('_', ' ')
            results.append({
                "title": event_name,
                "image_url": clean_url
            })     
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500
####################################
@app.route('/favicon.ico')
def favicon():
    return '', 404
if __name__ == "__main__":
    ensure_jwt_token_sync("default")
    app.run(host="0.0.0.0", port=5552)