import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import data_pb2
import os
import requests
import re
import time
from datetime import datetime, timedelta
import pytz
import json

# إعدادات logging
logging.basicConfig(
    level=logging.INFO,  # مستوى التفاصيل (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # طباعة السجل في الكونسول فقط
    ]
)
logger = logging.getLogger(__name__)

# توكن البوت (استبدله بتوكنك الخاص)
TOKEN = "8631579637:AAEQUi0msNC9-KSnpYpMSmmi97z-Cd8oX78"

# قائمة الأدمن (معرفات المستخدمين المسموح لهم بإدارة البوت)
ADMINS = [7179739121, 5164991393]

# مفتاح التشفير AES
key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

# ملفات البيانات
KEYS_FILE = "keys.txt"
USERS_FILE = "users.txt"

# تحميل البيانات من الملف
def load_data(file_name):
    logger.info(f"جارٍ تحميل البيانات من الملف: {file_name}")
    if os.path.exists(file_name):
        with open(file_name, "r") as file:
            try:
                return json.loads(file.read())
            except json.JSONDecodeError:
                logger.warning(f"الملف {file_name} فارغ أو تالف.")
                return {}
    logger.warning(f"الملف {file_name} غير موجود.")
    return {}

# حفظ البيانات في الملف
def save_data(file_name, data):
    logger.info(f"جارٍ حفظ البيانات في الملف: {file_name}")
    with open(file_name, "w") as file:
        file.write(json.dumps(data, indent=4))

# إضافة مفتاح جديد
def add_key(key, duration, users_limit):
    logger.info(f"جارٍ إضافة مفتاح جديد: {key}")
    keys = load_data(KEYS_FILE)
    
    try:
        num = int(duration[:-2])  # استخراج الرقم
        unit = duration[-2:]      # استخراج الوحدة الزمنية
    except (ValueError, IndexError):
        logger.error("المدة يجب أن تكون بالصيغة: 1dy, 1hr, 1min")
        raise ValueError("المدة يجب أن تكون بالصيغة: 1dy, 1hr, 1min")
    
    if unit == "dy":
        expiration_time = datetime.now(pytz.utc) + timedelta(days=num)
    elif unit == "hr":
        expiration_time = datetime.now(pytz.utc) + timedelta(hours=num)
    elif unit == "min":
        expiration_time = datetime.now(pytz.utc) + timedelta(minutes=num)
    else:
        logger.error("الوحدة الزمنية غير صالحة. يجب أن تكون: dy, hr, min")
        raise ValueError("الوحدة الزمنية غير صالحة. يجب أن تكون: dy, hr, min")
    
    keys[key] = {
        "expiration": expiration_time.strftime("%Y-%m-%d %H:%M:%S"),
        "users_limit": int(users_limit),
        "users": []
    }
    save_data(KEYS_FILE, keys)

# حذف مفتاح والمستخدمين المرتبطين به
def remove_key(key):
    logger.info(f"جارٍ حذف المفتاح: {key}")
    keys = load_data(KEYS_FILE)
    if key in keys:
        # حذف جميع المستخدمين المرتبطين بهذا المفتاح
        users = load_data(USERS_FILE)
        for user_id in keys[key]["users"]:
            if str(user_id) in users:
                logger.info(f"جارٍ حذف المستخدم: {user_id}")
                del users[str(user_id)]
        save_data(USERS_FILE, users)
        
        # حذف المفتاح
        del keys[key]
        save_data(KEYS_FILE, keys)

# إضافة مستخدم
def add_user(user_id, username, key):
    logger.info(f"جارٍ إضافة مستخدم: {username} (ID: {user_id})")
    users = load_data(USERS_FILE)
    keys = load_data(KEYS_FILE)
    if key in keys and len(keys[key]["users"]) < keys[key]["users_limit"]:
        users[str(user_id)] = {
            "username": username,
            "key": key,
            "expiration": keys[key]["expiration"]
        }
        keys[key]["users"].append(user_id)
        save_data(USERS_FILE, users)
        save_data(KEYS_FILE, keys)
        return True
    logger.warning("المفتاح غير صالح أو وصل إلى الحد الأقصى للمستخدمين.\n\n"
        "توصل مع صاحب البوت\n\n"
        "@l7l7aj and @S_DD_F")
    return False

# حذف مستخدم
def remove_user(user_id):
    logger.info(f"جارٍ حذف المستخدم: {user_id}")
    users = load_data(USERS_FILE)
    if str(user_id) in users:
        key = users[str(user_id)]["key"]
        keys = load_data(KEYS_FILE)
        if key in keys:
            keys[key]["users"].remove(user_id)
            save_data(KEYS_FILE, keys)
        del users[str(user_id)]
        save_data(USERS_FILE, users)

# التحقق من صلاحية المستخدم
def is_user_active(user_id):
    logger.info(f"جارٍ التحقق من صلاحية المستخدم: {user_id}")
    users = load_data(USERS_FILE)
    if str(user_id) in users:
        expiration = datetime.strptime(users[str(user_id)]["expiration"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
        return datetime.now(pytz.utc) < expiration
    return False

# الحصول على قائمة المستخدمين
def get_user_list():
    logger.info("جارٍ جلب قائمة المستخدمين.")
    return load_data(USERS_FILE)

# تشفير البيانات
def encrypt_data(user_input):
    logger.info("جارٍ تشفير البيانات.")
    if user_input.startswith("#FREEFIRE"):
        user_input = user_input.replace("#FREEFIRE", "", 1)

    data = data_pb2.Data()
    data.field_1 = user_input
    data_bytes = data.SerializeToString()
    padded_data = pad(data_bytes, AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(padded_data)
    formatted_encrypted_data = ' '.join([f"{byte:02X}" for byte in encrypted_data])
    return formatted_encrypted_data

# جلب JWT Token حقيقي
def get_jwt_token():
    logger.info("جارٍ جلب JWT Token...")
    try:
        # إضافة مهلة 3 ثواني
        time.sleep(3)
        
        # الرابط الذي سيتم جلب الـ JWT Token منه
        url = "https://app-py-amber.vercel.app/get?uid=3738140982&password=E848408BB97719AC5DDC63CE647DBFB71A9621D0BE83D0555808873D0859F301"
        
        # إرسال طلب GET للحصول على الـ JWT Token
        response = requests.get(url)
        
        # التحقق من نجاح الطلب
        if response.status_code == 200:
            # تحويل الاستجابة إلى JSON
            data = response.json()
            
            # التحقق من أن الاستجابة تحتوي على الـ Token
            if data.get("status") == "success" and "token" in data:
                # إرجاع الـ Token
                return data["token"]
            else:
                logger.error("الاستجابة لا تحتوي على الـ Token المطلوب.")
                return None
        else:
            logger.error(f"فشل جلب JWT Token. رمز الحالة: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"حدث خطأ أثناء جلب JWT Token: {e}")
        return None

# إرسال البيانات المشفرة
async def send_encrypted_data(update: Update, encrypted_data):
    logger.info("جارٍ إرسال البيانات المشفرة...")
    jwt_token = get_jwt_token()
    if not jwt_token:
        return

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
    data_hex = encrypted_data.replace(" ", "")
    data_bytes = bytes.fromhex(data_hex)
    response = requests.post(url, headers=headers, data=data_bytes)

    error_details = response.text
    links = re.findall(r'https://dl-sg-production\.freefiremobile\.com/.*?(?:EXPORTSETTINGS|PROJECTSETTINGS)', error_details)

    for i, link in enumerate(links):
        try:
            # إضافة مهلة 3 ثواني قبل تحميل كل ملف
            time.sleep(3)
            
            # تحميل الملف
            response = requests.get(link, timeout=10)
            if response.status_code == 200:
                # إرسال الملف مباشرة إلى المستخدم دون حفظه
                file_name = "ProjectData_slot_3.bytes" if "PROJECTSETTINGS" in link else "ProjectData_slot_3.meta"
                await update.message.reply_document(document=response.content, filename=file_name)
                logger.info(f"تم إرسال الملف: {file_name}")
            else:
                logger.error(f"فشل تحميل الملف: {link} - رمز الحالة: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"حدث خطأ أثناء تحميل الملف: {link} - {e}")

# أمر /K لتفعيل البوت باستخدام مفتاح
async def activate_bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    args = context.args
    if len(args) < 1:
        await update.message.reply_text("استخدام: /K <المفتاح>")
        return

    key = args[0]
    keys = load_data(KEYS_FILE)

    if key in keys:
        if add_user(user_id, username, key):
            await update.message.reply_text(f"تم تفعيل البوت بنجاح! المدة المتبقية: {keys[key]['expiration']}")
        else:
            await update.message.reply_text("المفتاح غير صالح أو وصل إلى الحد الأقصى للمستخدمين.\n\n"
        "توصل مع صاحب البوت\n\n"
        "@l7l7aj and @S_DD_F")
    else:
        await update.message.reply_text("المفتاح غير صحيح.\n\n"
        "توصل مع صاحب البوت\n\n"
        "@l7l7aj and @S_DD_F")

# أمر /ky لإضافة مفتاح
async def add_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("أنت لست أدمن.")
        return

    args = context.args
    if len(args) < 3:
        await update.message.reply_text("استخدام: /ky <المفتاح> <المدة> <عدد المستخدمين>")
        return

    key = args[0]
    duration = args[1]
    users_limit = args[2]

    try:
        add_key(key, duration, users_limit)
        await update.message.reply_text(f"تم إضافة المفتاح: {key}")
    except ValueError as e:
        await update.message.reply_text(str(e))

# أمر /Kys لحذف مفتاح
async def remove_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("أنت لست أدمن.")
        return

    args = context.args
    if len(args) < 1:
        await update.message.reply_text("استخدام: /Kys <المفتاح>")
        return

    key = args[0]
    remove_key(key)
    await update.message.reply_text(f"تم حذف المفتاح: {key}")

# أمر /userlist لعرض قائمة المستخدمين
async def user_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("أنت لست أدمن.")
        return

    users = get_user_list()
    if not users:
        await update.message.reply_text("لا يوجد مستخدمين.")
        return

    user_list = "\n".join([f"{user_id}: {data['username']} (تنتهي في {data['expiration']})" for user_id, data in users.items()])
    await update.message.reply_text(f"قائمة المستخدمين:\n{user_list}")

# أمر /userrem لحذف مستخدم
async def remove_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("أنت لست أدمن.")
        return

    args = context.args
    if len(args) < 1:
        await update.message.reply_text("استخدام: /userrem <معرف المستخدم>")
        return

    target_user_id = int(args[0])
    remove_user(target_user_id)
    await update.message.reply_text(f"تم حذف المستخدم: {target_user_id}")

# رسالة الترحيب
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    if is_user_active(user_id):
        await update.message.reply_text(f"مرحبًا {username}! البوت مفعل لديك. أرسل كود الخريطه\n\n"
         "مثال : #FREEFIRE7AAE5E2ED258E267B588A03EE7BEA49E9189")
        context.user_data["waiting_for_input"] = True
    else:
        await update.message.reply_text("البوت غير مفعل لديك. الرجاء إدخال مفتاح التفعيل باستخدام الأمر /K <المفتاح>.\n\n"
        "توصل مع صاحب البوت\n\n"
        "@l7l7aj and @S_DD_F")

# معالجة الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not is_user_active(user_id):
        return

    if context.user_data.get("waiting_for_input"):
        user_input = update.message.text
        
        # التحقق من أن البيانات تبدأ بـ #FREEFIRE
        if not user_input.startswith("#FREEFIRE"):
            await update.message.reply_text("البيانات يجب أن تبدأ بـ #FREEFIRE.")
            return

        encrypted_data = encrypt_data(user_input)
        await update.message.reply_text("جاري تحميل الملفات...")
        await send_encrypted_data(update, encrypted_data)
        context.user_data["waiting_for_input"] = False

# تشغيل البوت
def main():
    application = Application.builder().token(TOKEN).build()

    # الأوامر
    application.add_handler(CommandHandler("K", activate_bot_command))
    application.add_handler(CommandHandler("ky", add_key_command))
    application.add_handler(CommandHandler("Kys", remove_key_command))
    application.add_handler(CommandHandler("userlist", user_list_command))
    application.add_handler(CommandHandler("userrem", remove_user_command))
    application.add_handler(CommandHandler("start", start_command))

    # الرسائل
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # بدء البوت
    application.run_polling()

if __name__ == "__main__":
    main()