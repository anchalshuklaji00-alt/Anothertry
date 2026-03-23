from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import data_pb2
import requests
import re
import threading
import time
import httpx
from urllib.parse import unquote  # لإزالة ترميز URL

app = Flask(__name__)

# المفاتيح الثابتة للتشفير
key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

# متغير لتخزين JWT Token
jwt_token = None

# دالة لجلب JWT Token
def get_jwt_token():
    global jwt_token
    url = "https://fox-jwt-convert.onrender.com/get?uid=3742282075&password=B8B4818D83BAAFBA62FEA1447285A5246AD3DFFB5A8D3FC08CC1E3FB4D9BE534"
    try:
        response = httpx.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                jwt_token = data['token']
                print("JWT Token updated successfully.")
                print(f"Token: {jwt_token}")
            else:
                print("Failed to get JWT token: Status is not success.")
        else:
            print(f"Failed to get JWT token: HTTP {response.status_code}")
    except httpx.RequestError as e:
        print(f"Request error: {e}")

# دالة لتحديث JWT Token كل 8 ساعات
def token_updater():
    while True:
        get_jwt_token()
        time.sleep(8 * 3600)  # 8 ساعات

# بدء thread لتحديث JWT Token
token_thread = threading.Thread(target=token_updater, daemon=True)
token_thread.start()

# جلب JWT Token عند بدء التشغيل
get_jwt_token()

# نقطة نهاية API
@app.route('/get_map_files', methods=['GET'])
def get_map_files():
    # الحصول على معلمة map_code من الطلب
    map_code = request.args.get('map_code')
    
    # إذا لم يتم تمرير map_code، إرجاع خطأ
    if not map_code:
        return jsonify({"error": "map_code parameter is required"}), 400

    # إزالة ترميز URL من map_code إذا كان مشفرًا
    map_code = unquote(map_code)

    # التحقق من أن map_code يبدأ بـ #FREEFIRE
    if not map_code.startswith("#FREEFIRE"):
        return jsonify({"error": "map_code must start with #FREEFIRE"}), 400

    # تشفير البيانات
    data = data_pb2.Data()
    data.field_1 = map_code.replace("#FREEFIRE", "", 1)
    data_bytes = data.SerializeToString()
    padded_data = pad(data_bytes, AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(padded_data)
    formatted_encrypted_data = ' '.join([f"{byte:02X}" for byte in encrypted_data])

    # إرسال البيانات المشفرة
    headers = {
        "Expect": "100-continue",
        "Authorization": f"Bearer {jwt_token}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB47",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
        "Host": "clientbp.ggblueshark.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }

    url = "https://clientbp.ggblueshark.com/PreviewWorkshopCode"
    data_hex = formatted_encrypted_data.replace(" ", "")
    data_bytes = bytes.fromhex(data_hex)
    response = requests.post(url, headers=headers, data=data_bytes)

    # استخراج الروابط من الاستجابة
    error_details = response.text
    links = re.findall(r'https://dl-sg-production\.freefiremobile\.com/.*?(?:EXPORTSETTINGS|PROJECTSETTINGS)', error_details)

    # تحميل الملفات
    result = []
    for link in links:
        try:
            response = requests.get(link, timeout=10)
            if response.status_code == 200:
                file_name = "ProjectData_slot_3.bytes" if "PROJECTSETTINGS" in link else "ProjectData_slot_3.meta"
                with open(file_name, "wb") as file:
                    file.write(response.content)
                result.append({"file_name": file_name, "status": "success"})
            else:
                result.append({"file_name": link, "status": "failed", "error": f"HTTP {response.status_code}"})
        except requests.exceptions.RequestException as e:
            result.append({"file_name": link, "status": "failed", "error": str(e)})

    return jsonify({"files": result})

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=False)