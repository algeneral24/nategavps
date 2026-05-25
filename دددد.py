import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import quote
import time
import threading
import os
import re
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
import sys
import gc

# تحسين إعدادات Python الأساسية

required_channel = "@ibn_alhaitham2"  
admin_chat_id = 1792449471
admin_chat_id2 = 5321637533
token ="6873478283:AAHltzDnre1J8qm0aPbOTPfAMormy01U4ZM"
bot = telebot.TeleBot(token)

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ================== تحسينات الأداء ==================
def create_optimized_session():
    """إنشاء جلسة محسنة مع إعادة محاولة تلقائية"""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=40)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# جلسة عالمية واحدة لجميع الطلبات
GLOBAL_SESSION = create_optimized_session()

def fetch_fast(url, data=None, headers=None, cookies=None, method='POST', timeout=10):
    """دالة سريعة للطلبات مع timeout"""
    try:
        if method.upper() == 'POST':
            r = GLOBAL_SESSION.post(url, data=data, headers=headers, cookies=cookies, timeout=timeout)
        else:
            r = GLOBAL_SESSION.get(url, headers=headers, cookies=cookies, timeout=timeout)
        r.raise_for_status()
        return r
    except requests.exceptions.Timeout:
        raise Exception("انتهت المهلة")
    except Exception as e:
        raise Exception(str(e)[:100])

# ✅ إضافة دالة load_status
STATUS_FILE = "status.json"

def load_status():
    try:
        with open(STATUS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"notifications_enabled": True}

def save_status(status):
    with open(STATUS_FILE, "w") as file:
        json.dump(status, file, indent=4)

######### 📌 لوحة تحكم الأدمن
def get_admin_keyboard():
    keyboardd = types.InlineKeyboardMarkup(row_width=2)
    
    # الصف الأول
    btn_ban = types.InlineKeyboardButton("🚫 حظر", callback_data="ban_user")
    btn_unban = types.InlineKeyboardButton("✅ فك الحظر", callback_data="unban_user")
    keyboardd.add(btn_ban, btn_unban)
    
    # الصف الثاني
    btn_stats = types.InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")
    btn_broadcast = types.InlineKeyboardButton("📢 إذاعة", callback_data="broadcast")
    keyboardd.add(btn_stats, btn_broadcast)
    
    # الصف الثالث
    send_user = types.InlineKeyboardButton("📩 إرسال رسالة", callback_data="send_user1")
    btn_settings = types.InlineKeyboardButton("⚙️ إعدادات التشغيل", callback_data="show_settings")
    keyboardd.add(send_user, btn_settings)
    
    # الصف الرابع - الإشعارات
    status = load_status()
    notifications_status = "🔔 الإشعارات: ✅ مفعلة" if status["notifications_enabled"] else "🔕 الإشعارات: ❌ متوقفة"
    btn_notifications = types.InlineKeyboardButton(notifications_status, callback_data="toggle_notifications")
    keyboardd.add(btn_notifications)
    
    # الصف الخامس - إدارة الأكواد
    btn_manage_codes = types.InlineKeyboardButton("🔑 إدارة اكواد الوصول", callback_data="manage_access_codes")
    btn_manage_banned_codes = types.InlineKeyboardButton("🔒 إدارة الأكواد المحظورة", callback_data="manage_banned_codes")
    keyboardd.add(btn_manage_codes, btn_manage_banned_codes)
    
    # الصف السادس
    btn_manage_student_codes = types.InlineKeyboardButton("👤 إدارة أكواد الطلاب", callback_data="manage_student_codes")
    btn_whitelist = types.InlineKeyboardButton("⭐ إدارة المستخدمين المسموح لهم", callback_data="manage_whitelist")
    keyboardd.add(btn_manage_student_codes, btn_whitelist)
    
    # الصف السابع
    ranking_button = types.InlineKeyboardButton(text='🏆 الترتيب', callback_data='ranking')
    btn_ranking_system = types.InlineKeyboardButton("🏆 نظام الترتيب المتكامل", callback_data="ranking_admin")
    keyboardd.add(ranking_button, btn_ranking_system)
    
    # الصف الثامن
    btn_cookies_accounts = types.InlineKeyboardButton("🍪 إدارة حسابات الكوكيز", callback_data="manage_cookies_accounts")
    keyboardd.add(btn_cookies_accounts)
    
    # الصف التاسع - الأزرار الجديدة
    btn_bot_control = types.InlineKeyboardButton("🔴 إيقاف البوت" if load_bot_status() else "🟢 تشغيل البوت", callback_data="toggle_bot")
    btn_premium_codes = types.InlineKeyboardButton("👑 إدارة الأكواد المميزة", callback_data="manage_premium_codes")
    keyboardd.add(btn_bot_control, btn_premium_codes)
     
    return keyboardd

#__&&&&_____
keyboard2 = types.InlineKeyboardMarkup()
pas1 = types.InlineKeyboardButton(text='معرفة الباسورد✅', callback_data='send_password')
natega1 = types.InlineKeyboardButton(text='اعادة المحاولة 🔁', callback_data='echo_all')
back_button = types.InlineKeyboardButton(text='رجوع🔙', callback_data='back')
try_login = types.InlineKeyboardButton("💡 المساعدة في كلمة المرور", callback_data="try_login") 
keyboard2.row(try_login)
keyboard2.row(natega1)
keyboard2.row(back_button)

##المطور
keyboard3 = types.InlineKeyboardMarkup()
dev = types.InlineKeyboardButton(text="𓆩⋆ ׅᎯ𝔹Ꮇ ׅ⋆𓆪", url='https://t.me/BO_R0')
keyboard3.row(dev)
# ================== تشغيل وإيقاف البوت ==================
@bot.callback_query_handler(func=lambda call: call.data == "toggle_bot")
def handle_toggle_bot(call):
    """تشغيل أو إيقاف البوت"""
    chat_id = call.message.chat.id
    
    # التحقق من صلاحية الأدمن
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية.")
        return
    
    current_status = load_bot_status()
    new_status = not current_status
    save_bot_status(new_status)
    
    # تغيير نص الزر في لوحة التحكم (اختياري)
    new_button_text = "🔴 إيقاف البوت" if new_status else "🟢 تشغيل البوت"
    
    # تحديث واجهة الأدمن (تغيير الزر فقط دون إعادة إنشاء اللوحة بالكامل)
    try:
        # محاولة تحديث الزر فقط في الرسالة الحالية
        keyboard = get_admin_keyboard()
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )
    except:
        # إذا فشل التحديث، أعد إرسال اللوحة
        bot.edit_message_text(
            text="🎩 *مرحبًا أيها الأدمن! يمكنك استخدام لوحة التحكم أدناه:*",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_admin_keyboard()
        )
    
    # إشعار للمستخدم
    status_text = "تم تشغيل البوت ✅" if new_status else "تم إيقاف البوت 🔴"
    bot.answer_callback_query(call.id, status_text)
    
    # إرسال تأكيد للأدمن
    bot.send_message(
        admin_chat_id2,
        f"🔄 *تم تغيير حالة البوت*\n"
        f"• الحالة الجديدة: {'🟢 تشغيل' if new_status else '🔴 إيقاف'}\n"
        f"• بواسطة: {call.from_user.first_name}",
        parse_mode="Markdown"
    )
###تفعيل وتعطيل الازار ____________

USER_BUTTONS_FILE = "user_buttons.json"

def load_user_buttons():
    default_buttons = {
        "get_result": True,
        "get_password": True,
        "change_password": True,
        "calculate_gpa": True,
        "target_gpa": True,
        "try_login": True,
        "download_student_image": True,
        "download_student_image2": True,
        "subscription_required": True,
        "download_student_data": True,
        "graduates_result": True,
        "no_password_result": True,
        "single_code_per_user": True,   
        "ranking": True,
        "free_result": True,
        "student_ranking": True,  
    }

    try:
        with open(USER_BUTTONS_FILE, "r") as file:
            status = json.load(file)

        updated = False
        for key, value in default_buttons.items():
            if key not in status:
                status[key] = value
                updated = True

        if updated:
            save_user_buttons(status)

        return status

    except (FileNotFoundError, json.JSONDecodeError):
        save_user_buttons(default_buttons)
        return default_buttons

def save_user_buttons(status):
    with open(USER_BUTTONS_FILE, "w") as file:
        json.dump(status, file, indent=4)

# ✅ دالة الحصول على لوحة مفاتيح المستخدم (تعرض الأزرار المفعلة فقط)
def get_user_keyboard(chat_id=None):
    """ إرجاع لوحة مفاتيح المستخدم بناءً على حالة الأزرار 
        - الأدمن والمستخدمون في Whitelist يرون جميع الأزرار
        - المستخدمون العاديون يرون فقط الأزرار المفعلة
        - الأزرار تظهر زرين بجانب بعض """
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button_status = load_user_buttons()
    
    # ✅ التحقق إذا كان المستخدم أدمن أو في Whitelist
    is_admin_or_whitelisted = False
    if chat_id:
        if str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]:
            is_admin_or_whitelisted = True
        elif is_whitelisted(str(chat_id)):
            is_admin_or_whitelisted = True
    
    # ✅ تجميع الأزرار في قوائم حسب المجموعات
    result_buttons = []
    if is_admin_or_whitelisted or button_status.get("get_result", False):
        result_buttons.append(types.InlineKeyboardButton("📊 الحصول على النتيجة", callback_data="echo_all"))
    if is_admin_or_whitelisted or button_status.get("free_result", False):
        result_buttons.append(types.InlineKeyboardButton("📊 النتيجة ²", callback_data="free_result"))
    if is_admin_or_whitelisted or button_status.get("graduates_result", False):
        result_buttons.append(types.InlineKeyboardButton("🎓 نتيجة الخريجين", callback_data="graduates_result"))
    if is_admin_or_whitelisted or button_status.get("no_password_result", False):
        result_buttons.append(types.InlineKeyboardButton("📃 النتيجة بالدرجات", callback_data="no_password_result"))
    
    help_buttons = []
    if is_admin_or_whitelisted or button_status.get("get_password", False):
        help_buttons.append(types.InlineKeyboardButton("🔑 معرفة كلمة المرور", callback_data="send_password"))
    if is_admin_or_whitelisted or button_status.get("change_password", False):
        help_buttons.append(types.InlineKeyboardButton("🔄 تغيير كلمة المرور", callback_data="change_password"))
    if is_admin_or_whitelisted or button_status.get("try_login", False):
        help_buttons.append(types.InlineKeyboardButton("💡 المساعدة في كلمة المرور", callback_data="try_login"))
    
    gpa_buttons = []
    if is_admin_or_whitelisted or button_status.get("calculate_gpa", False):
        gpa_buttons.append(types.InlineKeyboardButton("🎓 حساب المعدل GPA", callback_data="calculate_gpa"))
    if is_admin_or_whitelisted or button_status.get("target_gpa", False):
        gpa_buttons.append(types.InlineKeyboardButton("📈 كم أحتاج للوصول لـ GPA معين؟", callback_data="target_gpa"))
    
    image_buttons = []
    if is_admin_or_whitelisted or button_status.get("download_student_image", False):
        image_buttons.append(types.InlineKeyboardButton("📷 تحميل صورة الطالب", callback_data="download_student_image"))
    if is_admin_or_whitelisted or button_status.get("download_student_image2", False):
        image_buttons.append(types.InlineKeyboardButton("📷 صورة الطالب نظام قديم", callback_data="download_student_image2"))
    if is_admin_or_whitelisted or button_status.get("download_student_data", False):
        image_buttons.append(types.InlineKeyboardButton("🆔 معرفة الاسم من id", callback_data="download_student_data"))
    
    ranking_buttons = []
    #if is_admin_or_whitelisted or button_status.get("ranking", False):
        #ranking_buttons.append(types.InlineKeyboardButton("🏆 الترتيب", callback_data="ranking"))
    if is_admin_or_whitelisted or button_status.get("student_ranking", False):
        ranking_buttons.append(types.InlineKeyboardButton("🏆 معرفة ترتيبك", callback_data="student_ranking_query"))
    
    # ✅ إضافة الأزرار في صفوف (زرين بجانب بعض)
    # أزرار النتائج
    for i in range(0, len(result_buttons), 2):
        if i + 1 < len(result_buttons):
            keyboard.add(result_buttons[i], result_buttons[i+1])
        else:
            keyboard.add(result_buttons[i])
    
    # أزرار المساعدة
    for i in range(0, len(help_buttons), 2):
        if i + 1 < len(help_buttons):
            keyboard.add(help_buttons[i], help_buttons[i+1])
        else:
            keyboard.add(help_buttons[i])
    
    # أزرار GPA
    for i in range(0, len(gpa_buttons), 2):
        if i + 1 < len(gpa_buttons):
            keyboard.add(gpa_buttons[i], gpa_buttons[i+1])
        else:
            keyboard.add(gpa_buttons[i])
    
    # أزرار الصور والبيانات
    for i in range(0, len(image_buttons), 2):
        if i + 1 < len(image_buttons):
            keyboard.add(image_buttons[i], image_buttons[i+1])
        else:
            keyboard.add(image_buttons[i])
    
    # أزرار الترتيب
    for i in range(0, len(ranking_buttons), 2):
        if i + 1 < len(ranking_buttons):
            keyboard.add(ranking_buttons[i], ranking_buttons[i+1])
        else:
            keyboard.add(ranking_buttons[i])
    
    # ✅ أزرار المطور والمجموعة (زرين بجانب بعض)
    keyboard.add(
        types.InlineKeyboardButton("𓆩⋆ ׅᎯ𝔹Ꮇ ׅ⋆𓆪👨‍💻", url='https://t.me/BO_R0'),
        types.InlineKeyboardButton('𝑰𝒃𝒏 𝑨𝒍𝒉𝒂𝒊𝒕𝒉𝒂𝒎 📢', url='https://t.me/+SI15cuZWSTNhODJk')
    )
    
    return keyboard

def get_toggle_buttons():
    """ إرجاع لوحة مفاتيح تحتوي على أزرار تفعيل وتعطيل الميزات """
    status = load_user_buttons()

    keyboard = types.InlineKeyboardMarkup()
    
    btn_subscription = types.InlineKeyboardButton(
        f"📢 اشتراك القناة ({'✅' if status.get('subscription_required', True) else '❌'})",
        callback_data="toggle_subscription"
    )

    btn_result = types.InlineKeyboardButton(
        f"📊 الحصول على النتيجة ({'✅' if status.get('get_result', False) else '❌'})", 
        callback_data="toggle_get_result"
    )
    btn_password = types.InlineKeyboardButton(
        f"🔑 معرفة كلمة المرور ({'✅' if status.get('get_password', False) else '❌'})", 
        callback_data="toggle_get_password"
    )
    btn_change_password = types.InlineKeyboardButton(
        f"🔄 تغيير كلمة المرور ({'✅' if status.get('change_password', False) else '❌'})", 
        callback_data="toggle_change_password"
    )
    btn_calculate_gpa = types.InlineKeyboardButton(
        f"🎓 حساب GPA ({'✅' if status.get('calculate_gpa', False) else '❌'})", 
        callback_data="toggle_calculate_gpa"
    )
    btn_target_gpa = types.InlineKeyboardButton(
        f"📈 استهداف GPA ({'✅' if status.get('target_gpa', False) else '❌'})", 
        callback_data="toggle_target_gpa"
    )
    btn_try_login = types.InlineKeyboardButton(
        f"💡 المساعدة في كلمة المرور ({'✅' if status.get('try_login', False) else '❌'})", 
        callback_data="toggle_try_login"
    )
    btn_download_image2 = types.InlineKeyboardButton(
        f"📥 تحميل صورة 2 ({'✅' if status.get('download_student_image2', False) else '❌'})",
        callback_data="toggle_download_student_image2"
    )
    btn_download_student_data = types.InlineKeyboardButton(
        f"الاسم من 🆔({'✅' if status.get('download_student_data', False) else '❌'})",
        callback_data="toggle_download_student_data"
    )
    btn_graduates_result = types.InlineKeyboardButton(
        f"📜 نتيجة الخريجين ({'✅' if status.get('graduates_result', False) else '❌'})",
        callback_data="toggle_graduates_result"
    )
    btn_download_image = types.InlineKeyboardButton(
        f"📷 تحميل صورة الطالب ({'✅' if status.get('download_student_image', False) else '❌'})",
        callback_data="toggle_download_student_image"
    )
    btn_no_password = types.InlineKeyboardButton(
        f"🔓 نتيجة بدون باسورد ({'✅' if status.get('no_password_result', False) else '❌'})",
        callback_data="toggle_no_password_result"
    )
    btn_ranking = types.InlineKeyboardButton(
        f"🏆 الترتيب ({'✅' if status.get('ranking', False) else '❌'})",
        callback_data="toggle_ranking"
    )
    btn_single_code = types.InlineKeyboardButton(
        f"🔐 كود طالب واحد لكل مستخدم ({'✅' if status.get('single_code_per_user', True) else '❌'})",
        callback_data="toggle_single_code_per_user"
    )
    btn_student_ranking = types.InlineKeyboardButton(
        f"🏆 نظام الترتيب ({'✅' if status.get('student_ranking', True) else '❌'})",
        callback_data="toggle_student_ranking"
    )
    btn_free_result = types.InlineKeyboardButton(
        f"📊 النتيجة بدون رسوم ({'✅' if status.get('free_result', False) else '❌'})",
        callback_data="toggle_free_result"
    )
    btn_back = types.InlineKeyboardButton("🔙 الرجوع", callback_data="back_to_admin")

    keyboard.add(btn_result, btn_password)
    keyboard.add(btn_change_password, btn_calculate_gpa)
    keyboard.add(btn_subscription, btn_download_image)
    keyboard.add(btn_target_gpa, btn_try_login)
    keyboard.add(btn_download_image2, btn_download_student_data)
    keyboard.add(btn_graduates_result, btn_single_code)
    keyboard.add(btn_no_password, btn_ranking)
    keyboard.add(btn_free_result, btn_student_ranking)
    keyboard.add(btn_back)

    return keyboard

@bot.callback_query_handler(func=lambda call: call.data in ["show_settings", "back_to_admin", "toggle_subscription"] or call.data.startswith("toggle_") and call.data != "toggle_notifications")
def handle_settings_buttons(call):
    chat_id = call.message.chat.id

    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية لاستخدام هذا الأمر.")
        return

    if call.data == "show_settings":
        explanation_text = (
            "⚙️ *إعدادات التشغيل:*\n\n"
            "• يمكنك تشغيل أو تعطيل الميزات من هنا.\n\n"
            "🔐 *نظام 'كود طالب واحد لكل مستخدم':*\n"
            "✅ *مفعل:* يمنع المستخدمين من استخدام أكثر من كود طالب\n"
            "❌ *معطل:* يسمح للمستخدمين باستخدام أي كود طالب\n"
            "📌 *ملاحظة:* المستخدمين المسموح لهم (Whitelist) والأدمن مستثنون من هذا النظام"
        )
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=explanation_text,
            parse_mode="Markdown",
            reply_markup=get_toggle_buttons()
        )

    elif call.data == "toggle_subscription":
        status = load_user_buttons()
        status["subscription_required"] = not status.get("subscription_required", True)
        save_user_buttons(status)

        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_toggle_buttons()
        )

        bot.answer_callback_query(call.id, f"🔘 {'تم تفعيل' if status['subscription_required'] else 'تم تعطيل'} اشتراك القناة.")

    elif call.data.startswith("toggle_"):
        feature = call.data.replace("toggle_", "")
        status = load_user_buttons()

        if feature in status:
            status[feature] = not status[feature]
            save_user_buttons(status)
            
            if feature == "single_code_per_user":
                status_text = "✅ تم تفعيل" if status[feature] else "❌ تم تعطيل"
                message_text = f"{status_text} نظام 'كود طالب واحد لكل مستخدم'.\n"
                message_text += "• عند التفعيل: سيتم حظر المستخدمين الذين يحاولون استخدام أكثر من كود طالب.\n"
                message_text += "• عند التعطيل: يمكن للمستخدمين استخدام أي كود طالب."
                bot.answer_callback_query(call.id, message_text, show_alert=True)
            else:
                bot.answer_callback_query(call.id, f"🔘 {'تم تفعيل' if status[feature] else 'تم تعطيل'} الزر.")

        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_toggle_buttons()
        )

    elif call.data == "back_to_admin":
        global stop_broadcasting
        stop_broadcasting = True
        bot.clear_step_handler_by_chat_id(chat_id)
        bot.edit_message_text(chat_id=chat_id,
            message_id=call.message.message_id,
            text="🎩 *مرحبًا أيها الأدمن! يمكنك استخدام لوحة التحكم أدناه:*",
            parse_mode="Markdown",
            reply_markup=get_admin_keyboard()
        )



#_________الاكواد المحظوره
BANNED_CODES_FILE = "banned_codes.json"
BANNED_STUDENT_CODES = ["12345678", "87654321", "11111111"]  # ضع هنا الأكواد التي تريد حظر مستخدميها

# ✅ دوال إدارة الأكواد المحظورة
def load_banned_codes():
    try:
        with open(BANNED_CODES_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return BANNED_STUDENT_CODES.copy()  # القيمة الافتراضية

def save_banned_codes(codes):
    with open(BANNED_CODES_FILE, "w") as file:
        json.dump(codes, file, indent=4)

def is_banned_student_code(student_id):
    codes = load_banned_codes()
    return student_id in codes    
#اداره الكوكيز ____________________»»»»»»»»»»»
# ================= نظام تجديد الكوكيز التلقائي =================
COOKIES_REFRESH_INTERVAL = 3000  # 50 دقيقة = 3000 ثانية
cookies_refresh_thread = None
cookies_refresh_enabled = False
cookies_refresh_lock = threading.Lock()
COOKIES_ACCOUNTS_FILE = "cookies_accounts.json"  # ملف حسابات الكوكيز
def load_file(file_name):
    """تحميل محتوى ملف نصي"""
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []
    except Exception:
        return []
#___&____$__&&&-
# ================= دوال إدارة حسابات الكوكيز =================
def load_cookies_accounts():
    """تحميل حسابات الكوكيز"""
    try:
        if os.path.exists(COOKIES_ACCOUNTS_FILE):
            with open(COOKIES_ACCOUNTS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    return data
        return {"accounts": [], "current_index": 0}
    except Exception:
        return {"accounts": [], "current_index": 0}

def save_cookies_accounts(accounts_data):
    """حفظ حسابات الكوكيز"""
    try:
        with open(COOKIES_ACCOUNTS_FILE, "w", encoding="utf-8") as file:
            json.dump(accounts_data, file, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False

def add_cookies_account(student_id, password):
    """إضافة حساب جديد"""
    data = load_cookies_accounts()
    
    # التحقق من عدم وجود الحساب مسبقاً
    for account in data["accounts"]:
        if account["student_id"] == student_id:
            return False, "الحساب موجود مسبقاً"
    
    data["accounts"].append({
        "student_id": student_id,
        "password": password,
        "added_at": time.time(),
        "last_used": None,
        "status": "active"
    })
    
    save_cookies_accounts(data)
    return True, "تم إضافة الحساب بنجاح"

def remove_cookies_account(student_id):
    """حذف حساب"""
    data = load_cookies_accounts()
    data["accounts"] = [acc for acc in data["accounts"] if acc["student_id"] != student_id]
    if data["current_index"] >= len(data["accounts"]):
        data["current_index"] = 0
    save_cookies_accounts(data)
    return True

def get_next_cookies_account():
    """الحصول على الحساب التالي للاستخدام"""
    data = load_cookies_accounts()
    if not data["accounts"]:
        return None
    
    account = data["accounts"][data["current_index"]]
    data["current_index"] = (data["current_index"] + 1) % len(data["accounts"])
    save_cookies_accounts(data)
    return account
def refresh_cookie_from_account(account):
    """تسجيل الدخول وتحديث الكوكيز من حساب معين (بنفس طريقة التغيير اليدوي)"""
    try:
        student_id = account["student_id"]
        password = account["password"]
        
        login_url = "http://credit.minia.edu.eg/studentLogin"
        
        payload = {
            "UserName": student_id,
            "Password": password,
            "sysID": "313",
            "UserLang": "A",
            "userType": "2"
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://credit.minia.edu.eg',
            'Referer': 'http://credit.minia.edu.eg/static/index.html'
        }
        
        with requests.Session() as session:
            r = session.post(login_url, data=payload, headers=headers, timeout=30)
            
            if r.status_code != 200:
                return False, f"❌ فشل تسجيل الدخول - Status Code: {r.status_code}"
            
            # الحصول على الكوكيز
            cookies = session.cookies.get_dict()
            
            # استخراج الكوكيز المطلوبة
            user_id = cookies.get("userID", "")
            session_dt = cookies.get("sessionDateTime", "")
            
            if not user_id:
                return False, "❌ لم يتم العثور على كوكيز userID"
            
            # تنسيق الكوكيز بالشكل المطلوب بالضبط (مثل التغيير اليدوي)
            cookie_string = f'userID="{user_id}";sessionDateTime="{session_dt}"'
            
            # إعداد البيانات لحفظها (نفس تنسيق التغيير اليدوي)
            cookies_data = {
                "main_cookie": cookie_string,  # نفس المفتاح المستخدم في التغيير اليدوي
                "original_input": cookie_string,
                "modified_by": "auto_system",
                "modified_at": time.time()
            }
            
            # حفظ الكوكيز باستخدام نفس دالة save_cookies المستخدمة في التغيير اليدوي
            if save_cookies(cookies_data):
                # تحديث آخر استخدام للحساب
                accounts_data = load_cookies_accounts()
                for acc in accounts_data["accounts"]:
                    if acc["student_id"] == student_id:
                        acc["last_used"] = time.time()
                        acc["status"] = "active"
                        break
                save_cookies_accounts(accounts_data)
                
                return True, f"✅ تم تحديث الكوكيز بنجاح (مثل التغيير اليدوي)"
            else:
                return False, "❌ فشل في حفظ الكوكيز"
            
    except requests.exceptions.Timeout:
        return False, "❌ انتهت مهلة الاتصال"
    except requests.exceptions.RequestException as e:
        return False, f"❌ خطأ في الاتصال: {str(e)}"
    except Exception as e:
        return False, f"❌ خطأ غير متوقع: {str(e)}" #================= نظام التحديث التلقائي =================
def start_cookies_refresh_thread():
    """بدء تشغيل خيط التحديث التلقائي"""
    global cookies_refresh_thread, cookies_refresh_enabled
    
    with cookies_refresh_lock:
        if cookies_refresh_enabled:
            return False, "نظام التحديث يعمل بالفعل"
        
        cookies_refresh_enabled = True
        cookies_refresh_thread = threading.Thread(target=cookies_refresh_worker, daemon=True)
        cookies_refresh_thread.start()
        return True, "✅ تم تشغيل نظام تحديث الكوكيز (كل 50 دقيقة)"

def stop_cookies_refresh_thread():
    """إيقاف تشغيل خيط التحديث التلقائي"""
    global cookies_refresh_enabled
    
    with cookies_refresh_lock:
        cookies_refresh_enabled = False
        return True, "⏹️ تم إيقاف نظام تحديث الكوكيز"

def cookies_refresh_worker():
    """العامل المسؤول عن التحديث الدوري"""
    global cookies_refresh_enabled
    
    while cookies_refresh_enabled:
        try:
            # التحقق من وجود حسابات
            accounts_data = load_cookies_accounts()
            if accounts_data["accounts"]:
                # الحصول على الحساب التالي
                account = get_next_cookies_account()
                if account:
                    success, message = refresh_cookie_from_account(account)
                    
                    # إرسال إشعار للأدمن
                    status = "✅" if success else "❌"
                    try:
                        bot.send_message(
                            admin_chat_id2,
                            f"{status} *تحديث الكوكيز التلقائي*\n"
                            f"━━━━━━━━━━━━━━━━━━━\n"
                            f"• الحساب: `{account['student_id']}`\n"
                            f"• الحالة: {message}\n"
                            f"• الوقت: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                            parse_mode="Markdown"
                        )
                    except:
                        pass
            else:
                # لا توجد حسابات
                try:
                    bot.send_message(
                        admin_chat_id2,
                        "⚠️ *لا توجد حسابات كوكيز*\n"
                        "يرجى إضافة حسابات لتفعيل التحديث التلقائي",
                        parse_mode="Markdown"
                    )
                except:
                    pass
            
            # انتظار 50 دقيقة (مع إمكانية الإيقاف)
            for _ in range(COOKIES_REFRESH_INTERVAL):
                if not cookies_refresh_enabled:
                    break
                time.sleep(1)
                
        except Exception as e:
            print(f"خطأ في تحديث الكوكيز: {e}")
            time.sleep(60)  # انتظر دقيقة ثم حاول مرة أخرى  
# ================= إدارة حسابات الكوكيز في لوحة الأدمن =================
def get_cookies_accounts_keyboard():
    """لوحة مفاتيح إدارة حسابات الكوكيز"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    global cookies_refresh_enabled
    refresh_status = "✅ مفعل" if cookies_refresh_enabled else "❌ معطل"
    btn_toggle = types.InlineKeyboardButton(
        f"🔄 التحديث التلقائي: {refresh_status}",
        callback_data="cookies_toggle_auto_refresh"
    )
    
    btn_add = types.InlineKeyboardButton("➕ إضافة حساب", callback_data="add_cookie_account")
    btn_remove = types.InlineKeyboardButton("➖ حذف حساب", callback_data="remove_cookie_account")
    btn_list = types.InlineKeyboardButton("📋 عرض الحسابات", callback_data="list_cookie_accounts")
    btn_refresh_now = types.InlineKeyboardButton("⚡ تحديث الآن", callback_data="refresh_cookies_now")
    btn_show_current = types.InlineKeyboardButton("👁️ عرض الكوكيز الحالي", callback_data="show_current_cookie")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_admin")
    
    keyboard.add(btn_toggle)
    keyboard.add(btn_add, btn_remove)
    keyboard.add(btn_list, btn_refresh_now)
    keyboard.add(btn_show_current)
    keyboard.add(btn_back)
    
    return keyboard

@bot.callback_query_handler(func=lambda call: call.data == "manage_cookies_accounts")
def handle_manage_cookies_accounts(call):
    """عرض قائمة إدارة حسابات الكوكيز"""
    chat_id = call.message.chat.id
    
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية.")
        return
    
    accounts_data = load_cookies_accounts()
    accounts = accounts_data["accounts"]
    
    text = (
        "🍪 *إدارة حسابات الكوكيز*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 *الإحصائيات:*\n"
        f"• إجمالي الحسابات: `{len(accounts)}`\n"
        f"• التحديث التلقائي: {'✅ مفعل' if cookies_refresh_enabled else '❌ معطل'}\n"
        f"• مدة التحديث: `50 دقيقة`\n\n"
    )
    
    if accounts:
        text += "📋 *آخر 5 حسابات مضافة:*\n"
        for i, acc in enumerate(accounts[-5:], 1):
            last_used = time.strftime('%Y-%m-%d %H:%M', time.localtime(acc['last_used'])) if acc['last_used'] else 'لم يستخدم بعد'
            text += f"{i}. `{acc['student_id']}` - آخر استخدام: {last_used}\n"
    
    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_cookies_accounts_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == "add_cookie_account")
def handle_add_cookie_account(call):
    """إضافة حساب جديد"""
    chat_id = call.message.chat.id
    
    bot.edit_message_text(
        "✍️ *إضافة حساب جديد*\n\n"
        "📝 أرسل بيانات الحساب بهذا التنسيق:\n"
        "`كود_الطالب|كلمة_المرور`\n\n"
        "مثال: `12345678|MyPassword123`",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )
    
    bot.register_next_step_handler(call.message, process_add_cookie_account)

def process_add_cookie_account(message):
    """معالجة إضافة حساب جديد"""
    chat_id = message.chat.id
    text = message.text.strip()
    
    if '|' not in text:
        bot.reply_to(
            message,
            "❌ *تنسيق غير صحيح*\n"
            "الرجاء استخدام التنسيق: `كود_الطالب|كلمة_المرور`",
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        return
    
    student_id, password = text.split('|', 1)
    student_id = student_id.strip()
    password = password.strip()
    
    if not student_id.isdigit() or len(student_id) != 8:
        bot.reply_to(
            message,
            "❌ *كود الطالب غير صحيح*\n"
            "يجب أن يكون 8 أرقام",
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        return
    
    success, msg = add_cookies_account(student_id, password)
    
    if success:
        bot.reply_to(
            message,
            f"✅ *تم إضافة الحساب بنجاح*\n"
            f"• كود الطالب: `{student_id}`",
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
    else:
        bot.reply_to(
            message,
            f"❌ *فشل إضافة الحساب*\n{msg}",
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )

@bot.callback_query_handler(func=lambda call: call.data == "remove_cookie_account")
def handle_remove_cookie_account(call):
    """حذف حساب"""
    chat_id = call.message.chat.id
    
    accounts_data = load_cookies_accounts()
    accounts = accounts_data["accounts"]
    
    if not accounts:
        bot.answer_callback_query(call.id, "❌ لا توجد حسابات لحذفها")
        return
    
    # عرض أزرار للحذف
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for acc in accounts:
        btn = types.InlineKeyboardButton(
            f"🗑️ {acc['student_id']}",
            callback_data=f"del_cookie_acc_{acc['student_id']}"
        )
        keyboard.add(btn)
    
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="manage_cookies_accounts")
    keyboard.add(btn_back)
    
    bot.edit_message_text(
        "🗑️ *اختر الحساب المراد حذفه:*",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_cookie_acc_"))
def handle_delete_cookie_account(call):
    """تنفيذ حذف الحساب"""
    chat_id = call.message.chat.id
    student_id = call.data.replace("del_cookie_acc_", "")
    
    remove_cookies_account(student_id)
    
    bot.answer_callback_query(call.id, f"✅ تم حذف الحساب {student_id}")
    
    # العودة لقائمة الإدارة
    handle_manage_cookies_accounts(call)

@bot.callback_query_handler(func=lambda call: call.data == "list_cookie_accounts")
def handle_list_cookie_accounts(call):
    """عرض جميع الحسابات"""
    chat_id = call.message.chat.id
    
    accounts_data = load_cookies_accounts()
    accounts = accounts_data["accounts"]
    
    if not accounts:
        bot.edit_message_text(
            "📭 *لا توجد حسابات مضافة*",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        return
    
    text = "📋 *قائمة حسابات الكوكيز:*\n\n"
    for i, acc in enumerate(accounts, 1):
        last_used = time.strftime('%Y-%m-%d %H:%M', time.localtime(acc['last_used'])) if acc['last_used'] else 'لم يستخدم'
        added = time.strftime('%Y-%m-%d', time.localtime(acc['added_at']))
        text += f"{i}. `{acc['student_id']}`\n"
        text += f"   📅 أضيف: {added}\n"
        text += f"   ⏰ آخر استخدام: {last_used}\n"
        text += f"   📊 الحالة: {acc['status']}\n\n"
    
    # إرسال كملف إذا كان النص طويلاً
    if len(text) > 3000:
        filename = f"cookie_accounts_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        
        with open(filename, "rb") as f:
            bot.send_document(chat_id, f, caption="📋 قائمة حسابات الكوكيز")
        
        os.remove(filename)
        
        bot.edit_message_text(
            "✅ *تم إرسال قائمة الحسابات في ملف*",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
    else:
        bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )

@bot.callback_query_handler(func=lambda call: call.data == "cookies_toggle_auto_refresh")
def handle_toggle_auto_refresh(call):
    """تشغيل/إيقاف التحديث التلقائي"""
    global cookies_refresh_enabled
    
    chat_id = call.message.chat.id
    
    if cookies_refresh_enabled:
        success, msg = stop_cookies_refresh_thread()
    else:
        # التحقق من وجود حسابات قبل التشغيل
        accounts_data = load_cookies_accounts()
        if not accounts_data["accounts"]:
            bot.answer_callback_query(
                call.id,
                "❌ لا يمكن تشغيل التحديث التلقائي بدون إضافة حسابات أولاً",
                show_alert=True
            )
            return
        success, msg = start_cookies_refresh_thread()
    
    bot.answer_callback_query(call.id, msg)
    
    # تحديث العرض
    handle_manage_cookies_accounts(call)

@bot.callback_query_handler(func=lambda call: call.data == "refresh_cookies_now")
def handle_refresh_cookies_now(call):
    """تحديث الكوكيز فوراً"""
    chat_id = call.message.chat.id
    
    accounts_data = load_cookies_accounts()
    if not accounts_data["accounts"]:
        bot.answer_callback_query(call.id, "❌ لا توجد حسابات")
        return
    
    account = get_next_cookies_account()
    if not account:
        bot.answer_callback_query(call.id, "❌ فشل في الحصول على حساب")
        return
    
    bot.answer_callback_query(call.id, "⏳ جاري تحديث الكوكيز...")
    
    success, message = refresh_cookie_from_account(account)
    
    if success:
        bot.send_message(
            chat_id,
            f"✅ *تم تحديث الكوكيز بنجاح*\n"
            f"• الحساب: `{account['student_id']}`\n"
            f"• الوقت: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            chat_id,
            f"❌ *فشل تحديث الكوكيز*\n{message}",
            parse_mode="Markdown"
        )

@bot.callback_query_handler(func=lambda call: call.data == "show_current_cookie")
def handle_show_current_cookie(call):
    """عرض محتوى الكوكيز الحالي"""
    chat_id = call.message.chat.id
    
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية.")
        return
    
    try:
        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE, "r", encoding="utf-8") as file:
                content = file.read()
                data = json.loads(content)
            
            # تنسيق العرض
            text = "🍪 *محتوى ملف الكوكيز الحالي:*\n\n"
            text += f"```json\n{json.dumps(data, indent=2, ensure_ascii=False)}\n```\n\n"
            
            # عرض الكوكيز المستخدمة حالياً
            current = get_current_cookie()
            if current:
                text += f"🔑 *الكوكيز المستخدمة:*\n`{current[:100]}...`"
            else:
                text += "⚠️ *لا توجد كوكيز صالحة للاستخدام*"
            
            # أزرار
            keyboard = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="manage_cookies_accounts")
            keyboard.add(btn_back)
            
            # إذا كان النص طويلاً، أرسله كملف
            if len(text) > 3000:
                filename = f"current_cookie_{time.strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(text.replace("```json\n", "").replace("\n```", ""))
                
                with open(filename, "rb") as f:
                    bot.send_document(chat_id, f, caption="📄 محتوى ملف الكوكيز")
                
                os.remove(filename)
                
                bot.edit_message_text(
                    "✅ *تم إرسال محتوى الكوكيز في ملف*",
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            else:
                bot.edit_message_text(
                    text,
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
        else:
            bot.edit_message_text(
                "❌ *ملف الكوكيز غير موجود*",
                chat_id=chat_id,
                message_id=call.message.message_id,
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )
    except Exception as e:
        bot.edit_message_text(
            f"❌ *خطأ في قراءة ملف الكوكيز:*\n`{str(e)}`",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )            
                    
#___&____$__&&&-

COOKIES_FILE = "cookies.json"

# 🔐 دالة لتحويل الكوكيز إلى التنسيق المطلوب
def format_cookie_for_file(cookie):
    """تنسيق الكوكيز لحفظها في الملف"""
    if not cookie:
        return ""
    
    # تنظيف الكوكيز أولاً
    cookie = cookie.strip()
    
    # إزالة علامات الاقتباس والرموز الزائدة
    unwanted = ['"', "'", '\\', '\n', '\r', '\t']
    for char in unwanted:
        cookie = cookie.replace(char, '')
    
    # إزالة userID= أو userID: إذا كانت في البداية
    if cookie.startswith('userID='):
        cookie = cookie[7:]
    elif cookie.startswith('userID:'):
        cookie = cookie[7:]
    
    # التأكد من التنسيق الصحيح
    if '|' not in cookie or len(cookie) < 30:
        return ""
    
    return cookie

# 🔐 دالة تحميل الكوكيز
def load_cookies():
    try:
        with open(COOKIES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict):
                return data
            return {}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    except Exception:
        return {}

# 🔐 دالة حفظ الكوكيز بالتنسيق المطلوب
def save_cookies(cookies):
    """🔐 دالة حفظ الكوكيز بالتنسيق المطلوب (مطابقة للتغيير اليدوي)"""
    try:
        if not isinstance(cookies, dict) or "main_cookie" not in cookies:
            return False
        
        # تنظيف وتنسيق الكوكيز
        main_cookie = format_cookie_for_file(cookies["main_cookie"])
        if not main_cookie:
            return False
        
        # استخراج userID و sessionDateTime من النص
        import re
        user_id = ""
        session_dt = ""
        
        # محاولة استخراج userID
        user_match = re.search(r'userID="([^"]+)"', main_cookie)
        if user_match:
            user_id = user_match.group(1)
        
        # محاولة استخراج sessionDateTime
        session_match = re.search(r'sessionDateTime="([^"]+)"', main_cookie)
        if session_match:
            session_dt = session_match.group(1)
        
        # إنشاء البيانات بالتنسيق المطلوب (مثل التغيير اليدوي)
        cookies_data = {
            "userID": user_id,
            "sessionDateTime": session_dt,
            "main_cookie": main_cookie,  # هذا المفتاح مهم للتغيير اليدوي
            "created_at": time.time(),
            "last_modified": time.time(),
            "modified_by": cookies.get("modified_by", "unknown"),
            "modified_at": time.time()
        }
        
        # إضافة معلومات إضافية إذا كانت موجودة
        if "original_input" in cookies:
            cookies_data["original_input"] = cookies["original_input"]
        
        # الحفظ في الملف
        with open(COOKIES_FILE, "w", encoding="utf-8") as file:
            json.dump(cookies_data, file, indent=4, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"❌ خطأ في حفظ الكوكيز: {e}")
        return False
# 🔐 دالة للحصول على الكوكيز الحالية
def get_current_cookie():
    """🔐 دالة للحصول على الكوكيز الحالية (مطابقة للتغيير اليدوي)"""
    cookies = load_cookies()
    
    # البحث عن الكوكيز في المفاتيح الممكنة
    if isinstance(cookies, dict):
        # محاولة الحصول من المفتاح main_cookie أولاً (للتغيير اليدوي)
        if "main_cookie" in cookies:
            cookie = cookies["main_cookie"]
            if cookie and isinstance(cookie, str) and len(cookie.strip()) > 30:
                return cookie.strip()
        
        # محاولة الحصول من المفتاح userID (للتنسيق الجديد)
        elif "userID" in cookies:
            user_id = cookies.get("userID", "")
            session_dt = cookies.get("sessionDateTime", "")
            if user_id and session_dt:
                return f'userID="{user_id}";sessionDateTime="{session_dt}"'
            elif user_id:
                return f'userID="{user_id}"'
    
    return ""


      
@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None

    # ✅ التحقق التلقائي من الأكواد في رسالة /start
    if message.text:
        check_and_activate_premium(chat_id, user_id, message.text)
    
    # ✅ التحقق من صلاحية الاستخدام قبل أي شيء
    if not can_use_bot(chat_id):
        bot.send_message(
            chat_id,
            "🔴 *البوت متوقف حالياً.*\n\n"
            ,
            parse_mode="Markdown",
            reply_markup=keyboard3
        )
        return

    # إرسال رسالة ترحيب للمستخدم دائمًا
    welcome(message)

    # ✅ توجيه رسالة /start إلى الأدمن إذا لم يكن البوت نفسه أو الأدمن نفسه
    if user_id and chat_id != admin_chat_id2:
        try:
            # توجيه الرسالة للأدمن
            sent_message = bot.forward_message(admin_chat_id2, chat_id, message.message_id)
            
            # حفظ معرف الرسالة المعادة التوجيه
            user_messages[sent_message.message_id] = chat_id
            save_user_messages(user_messages)  # حفظ في الملف
        except:
            pass  # تجاهل أي خطأ بدون طباعة


def welcome(message):
    chat_id = str(message.chat.id)
    bot.send_chat_action(chat_id, 'typing')

    # ✅ التحقق التلقائي من الأكواد في الرسالة
    if message.text:
        check_and_activate_premium(chat_id, message.from_user.id, message.text)
    
    # ✅ التحقق من صلاحية الاستخدام
    if not can_use_bot(chat_id):
        bot.send_message(
            chat_id,
            "🔴 *البوت متوقف حالياً.*\n\n"
         ,
            parse_mode="Markdown",
            reply_markup=keyboard3
        )
        return

    # ✅ تحميل المحظورين والمستخدمين داخل الدالة لضمان التحديث الفوري
    banned_users = set(map(str, load_file("ban.txt")))
    known_users = set(map(str, load_file("ids.txt")))

    if chat_id in banned_users:
        bot.send_message(chat_id, "🚫 *تم حظرك من استخدام هذا البوت.*\n🔹 إذا كنت تعتقد أن هناك خطأ، يرجى التواصل مع المطور.", parse_mode="Markdown", reply_markup=keyboard3)
        return

    if chat_id not in known_users:
        with open("ids.txt", "a") as file:
            file.write(f"{chat_id}\n")
        notify_admin_of_new_user(message)

    # ✅ تحميل إعدادات الأزرار
    button_status = load_user_buttons()
    subscription_required = button_status.get("subscription_required", True)

    if subscription_required and not is_user_subscribed(chat_id):
        send_subscription_message(chat_id)
        return

    if chat_id == str(admin_chat_id):
        bot.send_message(chat_id, "🎩 *مرحبًا أيها الأدمن! يمكنك استخدام لوحة التحكم أدناه:*", parse_mode="Markdown", reply_markup=get_admin_keyboard())
    else:
        send_welcome_message(chat_id, message)


# ✅ التحقق من الاشتراك
def is_user_subscribed(chat_id):
    try:
        return bot.get_chat_member(required_channel, chat_id).status not in ["left", "kicked"]
    except Exception:
        return False

# ✅ إرسال رسالة اشتراك القناة
def send_subscription_message(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔗 انضم للقناة", url=f"https://t.me/{required_channel.lstrip('@')}"))
    keyboard.add(types.InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription"))
    
    bot.send_message(chat_id, "🚨 *عذرًا، لا يمكنك استخدام البوت حتى تقوم بالاشتراك في القناة الرسمية.*\n"
                              "1️⃣ اضغط على الزر أدناه للانضمام إلى القناة.\n"
                              "2️⃣ بعد الاشتراك، اضغط على \"تحقق من الاشتراك\".\n"
                              "✅ *بعد الاشتراك، يمكنك استخدام جميع الميزات بسهولة!*", parse_mode="Markdown", reply_markup=keyboard)

# ✅ الرد على زر "تحقق من الاشتراك"
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def handle_check_subscription(call):
    chat_id = call.message.chat.id
    if is_user_subscribed(chat_id):     
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"🎉 اهلا بك ي بشمهندس "
                 f"في بوت [{bot.get_me().first_name}](https://t.me/{bot.get_me().username}) المخصص لطلاب كلية الزراعة جامعة المنيا! 📚\n\n"
                 f"✨ *ماذا يمكنني فعله؟*\n"
                 f"• 📊 جلب نتائجك بسرعة وسهولة.\n"
                 f"• 🔑 استعادة أو تغيير كلمة مرور ابن الهيثم.\n"
                 f"• 🎓 حساب معدلك التراكمي (GPA).\n"
                 f"• 📷 تحميل صورة الطالب وبياناته.\n\n"
                 f"🚀 *ابدأ الآن!* استخدم الأزرار أدناه.\n"
                 f"💬 *للاستفسارات أو المشاكل:* [اضغط هنا](https://102706971050467064406.sarhne.com)",
            parse_mode='Markdown',
            disable_web_page_preview=True,
            reply_markup=get_user_keyboard(chat_id)
        )
    else:
        bot.answer_callback_query(call.id, "❌ لم يتم العثور على اشتراكك. تأكد من انضمامك ثم أعد المحاولة.", show_alert=True)

# ✅ إشعار الأدمن عند دخول مستخدم جديد
def notify_admin_of_new_user(message):
    try:
        user = message.from_user

        def clean(text):
            # تهريب جميع الرموز الخاصة في MarkdownV2
            symbols = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            for s in symbols:
                text = text.replace(s, f"\\{s}")
            return str(text)

        first_name = clean(user.first_name or "غير معروف")
        last_name = clean(user.last_name or "")
        username = f"@{user.username}" if user.username else "لا يوجد"
        user_id = str(user.id)
        lang = user.language_code.upper() if user.language_code else "؟"
        is_bot = "نعم" if user.is_bot else "لا"

        # رابط مباشر لحساب المستخدم باستخدام اسمه الأول
        user_link = f"[{first_name}](tg://user?id={user_id})"

        msg = (
            f"ℹ️ *مستخدم جديد دخل إلى البوت:*\n"
            f"👤 *الاسم:* {user_link} `{last_name}`\n"
            f"🔹 *المعرف:* `{clean(username)}`\n"
            f"🆔 *ID:* `{user_id}`\n"
            f"🌍 *اللغة:* `{lang}`\n"
            f"🤖 *بوت؟:* `{is_bot}`"
        )

        bot.send_message(admin_chat_id2, msg, parse_mode="MarkdownV2", disable_web_page_preview=True)

    except Exception as e:
        print(f"⚠️ فشل في notify_admin_of_new_user: {e}")


# ✅ إرسال رسالة ترحيب
def send_welcome_message(chat_id, message):
    user = message.from_user
    bot.reply_to(
        message,
        f"🎉 اهلا بك  [{user.first_name}](tg://user?id={user.id}) "
        f"في بوت [{bot.get_me().first_name}](https://t.me/{bot.get_me().username}) المخصص لطلاب جامعة المنيا! 📚\n\n"
        f"✨ *ماذا يمكنني فعله؟*\n"
        f"• 📊 جلب نتائجك بسرعة وسهولة.\n"
        f"• 🔑 استعادة أو تغيير كلمة مرور ابن الهيثم.\n"
        f"• 🎓 حساب معدلك التراكمي (GPA).\n"
        f"• 📷 تحميل صورة الطالب وبياناته.\n\n"
        f"🚀 *ابدأ الآن!* استخدم الأزرار أدناه.\n"
        f"💬 *للاستفسارات أو المشاكل:* [اضغط هنا](https://102706971050467064406.sarhne.com)",
        parse_mode='Markdown',
        disable_web_page_preview=True,
        reply_markup=get_user_keyboard(chat_id)  # ✅ تمرير chat_id
    )
keyboard1 = types.InlineKeyboardMarkup()
back_button = types.InlineKeyboardButton(text='رجوع🔙', callback_data='back')
keyboard1.row(back_button)
#______
# ⭐ المستخدمون المسموح لهم (Whitelist)
WHITELIST_FILE = "whitelist_users.json"

def load_whitelist():
    try:
        with open(WHITELIST_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_whitelist(users):
    with open(WHITELIST_FILE, "w") as f:
        json.dump(users, f, indent=4)

def is_whitelisted(chat_id):
    return str(chat_id) in load_whitelist()


# --- إدارة القائمة البيضاء ---
@bot.callback_query_handler(func=lambda call: call.data == "manage_whitelist")
def manage_whitelist(call):
    chat_id = call.message.chat.id

    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        return

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("➕ إضافة مستخدم", callback_data="add_whitelist"),
        types.InlineKeyboardButton("➖ حذف مستخدم", callback_data="remove_whitelist")
    )
    kb.add(types.InlineKeyboardButton("👁️ عرض المستخدمين", callback_data="view_whitelist"))
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_admin"))

    # إلغاء أي انتظار سابق
    try:
        bot.clear_step_handler_by_chat_id(chat_id)
    except:
        pass

    bot.edit_message_text(
        "⭐ *إدارة المستخدمين المسموح لهم:*\n\n"
        "• **لا يتم حظرهم عند تغيير كود الطالب**\n"
        "• **يمكنهم استخدام الأزرار حتى لو كانت متوقفة**",
        chat_id,
        call.message.message_id,
        parse_mode="Markdown",
        reply_markup=kb
    )

# --- إضافة مستخدم ---
@bot.callback_query_handler(func=lambda call: call.data == "add_whitelist")
def add_whitelist(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # إلغاء أي انتظار خطوة حالية
    try:
        bot.clear_step_handler_by_chat_id(chat_id)
    except:
        pass

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="manage_whitelist"))

    bot.edit_message_text(
        "✍️ **أرسل ID المستخدم لإضافته:**",
        chat_id,
        message_id,
        parse_mode="Markdown",
        reply_markup=kb
    )
    bot.register_next_step_handler_by_chat_id(chat_id, process_add_whitelist)

def process_add_whitelist(message):
    chat_id = message.chat.id
    users = load_whitelist()
    uid = message.text.strip()

    if uid not in users:
        users.append(uid)
        save_whitelist(users)
        text = f"✅ **تم إضافة المستخدم بنجاح:** `{uid}`"
    else:
        text = f"⚠️ المستخدم `{uid}` موجود بالفعل في القائمة"

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="manage_whitelist"))
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)

# --- حذف مستخدم ---
@bot.callback_query_handler(func=lambda call: call.data == "remove_whitelist")
def remove_whitelist(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # إلغاء أي انتظار خطوة حالية
    try:
        bot.clear_step_handler_by_chat_id(chat_id)
    except:
        pass

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="manage_whitelist"))

    bot.edit_message_text(
        "✍️ **أرسل ID المستخدم لحذفه:**",
        chat_id,
        message_id,
        parse_mode="Markdown",
        reply_markup=kb
    )
    bot.register_next_step_handler_by_chat_id(chat_id, process_remove_whitelist)

def process_remove_whitelist(message):
    chat_id = message.chat.id
    users = load_whitelist()
    uid = message.text.strip()

    if uid in users:
        users.remove(uid)
        save_whitelist(users)
        text = f"✅ **تم حذف المستخدم بنجاح:** `{uid}`"
    else:
        text = f"⚠️ المستخدم `{uid}` غير موجود في القائمة"

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="manage_whitelist"))
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=kb)

# --- عرض المستخدمين ---
@bot.callback_query_handler(func=lambda call: call.data == "view_whitelist")
def view_whitelist(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    users = load_whitelist()

    # إلغاء أي انتظار خطوة حالية
    try:
        bot.clear_step_handler_by_chat_id(chat_id)
    except:
        pass

    if not users:
        text = "📭 **لا يوجد مستخدمون مسموح لهم حالياً.**"
    else:
        text = "👑 **قائمة المستخدمين المسموح لهم:**\n\n"
        for i, uid in enumerate(users, 1):
            text += f"{i}. 🆔 `{uid}`\n"
        text += f"\n📊 **الإجمالي:** {len(users)} مستخدم"

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="manage_whitelist"))

    bot.edit_message_text(
        text,
        chat_id,
        message_id,
        parse_mode="Markdown",
        reply_markup=kb
    )

def check_button_permission(chat_id, button_name):
    """
    التحقق من صلاحية استخدام زر معين.
    يرجع True إذا كان المستخدم:
    1. في Whitelist
    2. أدمن
    3. الزر مفعل في الإعدادات
    """
    # ✅ التحقق إذا كان المستخدم في Whitelist
    if is_whitelisted(str(chat_id)):
        return True
    
    # ✅ التحقق إذا كان المستخدم أدمن
    if str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]:
        return True
    
    # ✅ التحقق من حالة الزر في الإعدادات
    button_status = load_user_buttons()
    return button_status.get(button_name, False)
# ================= نظام الترتيب المتكامل =================

chat_data = {}

RANKING_FILES_FOLDER = "ranking_files"  # مجلد ملفات الترتيب
os.makedirs(RANKING_FILES_FOLDER, exist_ok=True)

ITEMS_PER_PAGE = 15  # عدد النتائج في كل صفحة

# ================= نظام البحث المتقدم =================
class AdvancedSearchSystem:
    """نظام بحث متقدم - يتعرف تلقائياً على الاسم أو الكود"""
    
    def __init__(self):
        self.search_cache = {}
        self.cache_expiry = 300
        self.user_sessions = {}
        
    def normalize_text(self, text):
        if not text:
            return ""
        text = text.replace('ة', 'ه').replace('ى', 'ي')
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = ' '.join(text.split())
        return text.lower()
    
    def is_code(self, text):
        text = text.strip()
        if text.isdigit() and 5 <= len(text) <= 10:
            return True
        return False
    
    def is_valid_name(self, text):
        """التحقق من أن الاسم ثنائي على الأقل (كلمتين)"""
        words = text.strip().split()
        return len(words) >= 2
    
    def get_all_students_data(self):
        cache_key = "all_students"
        current_time = time.time()
        
        if cache_key in self.search_cache:
            timestamp, data = self.search_cache[cache_key]
            if current_time - timestamp < self.cache_expiry:
                return data
        
        files = get_ranking_files()
        all_students = []
        
        for file_info in files:
            students = parse_ranking_file(file_info['path'])
            for student in students:
                student['source_file'] = file_info['name']
                student['file_title'] = file_info['title']
                all_students.append(student)
        
        self.search_cache[cache_key] = (current_time, all_students)
        return all_students
    
    def search_by_code(self, code, students_data):
        results = []
        for student in students_data:
            if student.get('code') == code:
                results.append(student)
        return results
    
    def search_by_name_starts_with(self, name, students_data):
        name = self.normalize_text(name)
        results = []
        
        for student in students_data:
            student_name = student.get('name', '')
            if not student_name:
                continue
                
            normalized_name = self.normalize_text(student_name)
            
            if normalized_name.startswith(name):
                results.append(student)
        
        results.sort(key=lambda x: x.get('gpa', 0), reverse=True)
        return results
    
    def search(self, query):
        if not query:
            return [], None
        
        students_data = self.get_all_students_data()
        
        if not students_data:
            return [], None
        
        if self.is_code(query):
            results = self.search_by_code(query, students_data)
            return results, "code"
        else:
            if not self.is_valid_name(query):
                return [], "invalid_name"
            results = self.search_by_name_starts_with(query, students_data)
            return results, "name"
    
    def save_session(self, chat_id, query, results, search_type, total_pages, current_page=0):
        self.user_sessions[chat_id] = {
            'query': query,
            'results': results,
            'search_type': search_type,
            'current_page': current_page,
            'total_pages': total_pages,
            'timestamp': time.time()
        }
    
    def get_session(self, chat_id):
        if chat_id in self.user_sessions:
            session = self.user_sessions[chat_id]
            if time.time() - session.get('timestamp', 0) < 1800:
                return session
            else:
                del self.user_sessions[chat_id]
        return None
    
    def get_page_results(self, chat_id, page):
        session = self.get_session(chat_id)
        if not session:
            return None, 0, 0
        
        results = session['results']
        total_pages = session['total_pages']
        
        if page < 0:
            page = 0
        if page >= total_pages:
            page = total_pages - 1
        
        start = page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        page_results = results[start:end]
        
        session['current_page'] = page
        return page_results, page, total_pages


advanced_search = AdvancedSearchSystem()


# ================= دوال تحليل ملفات الترتيب =================
def parse_ranking_file(file_path):
    students = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_student = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('[#'):
                if current_student and 'name' in current_student:
                    students.append(current_student)
                
                current_student = {}
                
                rank_match = re.match(r'\[#(\d+)(=?)\] (.*)', line)
                if rank_match:
                    current_student['rank'] = int(rank_match.group(1))
                    current_student['rank_equal'] = rank_match.group(2) == '='
                    current_student['name'] = rank_match.group(3).strip()
            
            elif 'الرقم الجامعي:' in line:
                code_match = re.search(r'الرقم الجامعي:\s*(\d+)', line)
                if code_match:
                    current_student['code'] = code_match.group(1)
            
            elif 'المعدل التراكمي:' in line:
                gpa_match = re.search(r'المعدل التراكمي:\s*([\d.]+)', line)
                if gpa_match:
                    current_student['gpa'] = float(gpa_match.group(1))
            
            elif 'الساعات المكتسبة:' in line:
                hours_match = re.search(r'الساعات المكتسبة:\s*(\d+)', line)
                if hours_match:
                    current_student['hours'] = int(hours_match.group(1))
            
            elif 'الكلية:' in line:
                college_match = re.search(r'الكلية:\s*([^|]+)', line)
                if college_match:
                    current_student['college'] = college_match.group(1).strip()
            
            elif 'البرنامج:' in line:
                prog_match = re.search(r'البرنامج:\s*([^|]+)', line)
                if prog_match:
                    current_student['program'] = prog_match.group(1).strip()
        
        if current_student and 'name' in current_student:
            students.append(current_student)
        
        return students
    except Exception as e:
        print(f"خطأ في تحليل الملف: {e}")
        return []


def get_ranking_files():
    try:
        files = []
        for file in os.listdir(RANKING_FILES_FOLDER):
            if file.endswith('.txt'):
                file_path = os.path.join(RANKING_FILES_FOLDER, file)
                file_size = os.path.getsize(file_path)
                modified_time = os.path.getmtime(file_path)
                
                title = file.replace('.txt', '').replace('_', ' ')
                college_name = "غير معروف"
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        if first_line:
                            title = first_line
                            if ' - ' in first_line:
                                college_name = first_line.split(' - ')[0].strip()
                            else:
                                college_name = first_line
                except:
                    pass
                
                students = parse_ranking_file(file_path)
                student_count = len(students)
                
                files.append({
                    "name": file,
                    "path": file_path,
                    "size": file_size,
                    "modified": modified_time,
                    "title": title,
                    "college": college_name,
                    "student_count": student_count
                })
        
        return sorted(files, key=lambda x: x["modified"], reverse=True)
    except Exception as e:
        print(f"خطأ في قراءة الملفات: {e}")
        return []


def get_student_complete_ranking(student_code, files=None):
    """الحصول على جميع معلومات ترتيب الطالب"""
    if files is None:
        files = get_ranking_files()
    
    result = {
        'student': None,
        'file_name': None,
        'file_title': None,
        'college_ranking': None,
        'program_ranking': None,
        'total_college': 0,
        'total_program': 0,
        'college_rank_equal': False,
        'program_rank_equal': False,
        'same_gpa_college': 0,
        'same_gpa_program': 0
    }
    
    for file_info in files:
        students = parse_ranking_file(file_info['path'])
        
        for student in students:
            if student.get('code') == student_code:
                result['student'] = student
                result['file_name'] = file_info['name']
                result['file_title'] = file_info['title']
                
                all_students = students
                
                # ترتيب الكلية
                college_name = student.get('college', '')
                college_students = [s for s in all_students if s.get('college') == college_name]
                college_students.sort(key=lambda x: x.get('gpa', 0), reverse=True)
                
                college_rank = 1
                prev_gpa = None
                rank_counter = 1
                rank_map = {}
                student_gpa = student.get('gpa', 0)
                
                for s in college_students:
                    current_gpa = s.get('gpa', 0)
                    
                    if prev_gpa is not None and abs(current_gpa - prev_gpa) > 0.001:
                        college_rank = rank_counter
                    
                    rank_map[s.get('code')] = {
                        'rank': college_rank,
                        'equal': prev_gpa is not None and abs(current_gpa - prev_gpa) < 0.001
                    }
                    
                    prev_gpa = current_gpa
                    rank_counter += 1
                
                if student_code in rank_map:
                    result['college_ranking'] = rank_map[student_code]['rank']
                    result['college_rank_equal'] = rank_map[student_code]['equal']
                
                result['total_college'] = len(college_students)
                
                same_gpa_college = [s for s in college_students if abs(s.get('gpa', 0) - student_gpa) < 0.001]
                result['same_gpa_college'] = len(same_gpa_college)
                
                # ترتيب القسم
                program_name = student.get('program', '')
                program_students = [s for s in all_students if s.get('program') == program_name]
                program_students.sort(key=lambda x: x.get('gpa', 0), reverse=True)
                
                program_rank = 1
                prev_gpa = None
                rank_counter = 1
                prog_rank_map = {}
                
                for s in program_students:
                    current_gpa = s.get('gpa', 0)
                    
                    if prev_gpa is not None and abs(current_gpa - prev_gpa) > 0.001:
                        program_rank = rank_counter
                    
                    prog_rank_map[s.get('code')] = {
                        'rank': program_rank,
                        'equal': prev_gpa is not None and abs(current_gpa - prev_gpa) < 0.001
                    }
                    
                    prev_gpa = current_gpa
                    rank_counter += 1
                
                if student_code in prog_rank_map:
                    result['program_ranking'] = prog_rank_map[student_code]['rank']
                    result['program_rank_equal'] = prog_rank_map[student_code]['equal']
                
                result['total_program'] = len(program_students)
                
                same_gpa_program = [s for s in program_students if abs(s.get('gpa', 0) - student_gpa) < 0.001]
                result['same_gpa_program'] = len(same_gpa_program)
                
                return result
    
    return None


# ================= زر البحث المتقدم =================
@bot.callback_query_handler(func=lambda call: call.data == "student_ranking_query")
def handle_advanced_ranking(call):
    """معالج نظام الترتيب المتكامل مع التحقق من الإعدادات"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # ✅ التحقق من تفعيل زر نظام الترتيب في الإعدادات
    button_status = load_user_buttons()
    
    # استثناء الأدمن والوايت ليست من شرط تفعيل الزر
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        if not button_status.get("student_ranking", True):
            bot.answer_callback_query(call.id, "❌ نظام الترتيب معطل حالياً من قبل الأدمن.")
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="❌ *نظام الترتيب معطل حاليًا من قبل الأدمن.*\n\n"
                     "🔹 يمكنك التواصل مع الأدمن لتفعيل النظام.",
                parse_mode="Markdown",
                reply_markup=keyboard3
            )
            return
    
    try:
        with open("ban.txt", "r") as file:
            banned_users = file.read().splitlines()
    except FileNotFoundError:
        banned_users = []
    
    if str(chat_id) in banned_users:
        bot.answer_callback_query(call.id, "🚫 أنت محظور!", show_alert=True)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🚫 تم حظرك من استخدام هذا البوت.",
            parse_mode="HTML",
            reply_markup=keyboard3
        )
        return
    
    if not is_whitelisted(str(chat_id)) and str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        button_status = load_user_buttons()
        if button_status.get("subscription_required", True) and not is_user_subscribed(chat_id):
            bot.answer_callback_query(call.id, "❌ يجب الاشتراك في القناة", show_alert=True)
            send_subscription_message(chat_id)
            return
    
    files = get_ranking_files()
    if not files:
        bot.edit_message_text(
            "❌ لا توجد ملفات ترتيب متاحة\n\nيرجى التواصل مع الأدمن لرفع ملفات الترتيب",
            chat_id=chat_id,
            message_id=message_id,
            parse_mode="HTML",
            reply_markup=keyboard1
        )
        return
    
    bot.edit_message_text(
    "🔍 *معرفة ترتيبك*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "📌 *يمكنك البحث عن طريق:*\n\n"
    "• 🆔 *كود الطالب:* `8 أرقام`\n"
    "  مثال: `12345678`\n\n"
    "• 👤 *اسم الطالب:* (ثنائي أو ثلاثي)\n"
    "  مثال: `احمد عمرو` أو `احمد عمرو سامي`\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "✍️ *أدخل كود الطالب أو الاسم:*",
    chat_id=chat_id,
    message_id=message_id,
    parse_mode="Markdown",
    reply_markup=keyboard1
)
    
    bot.register_next_step_handler(call.message, process_ranking_input)


def process_ranking_input(message):
    chat_id = message.chat.id
    user = message.from_user
    query = message.text.strip()
    
    if not query:
        bot.reply_to(message, "❌ الرجاء إدخال رقم جامعي أو اسم طالب", parse_mode="HTML")
        return
    
    # التحقق من الأكواد المحظورة
    if query.isdigit() and len(query) >= 5:
        if is_banned_student_code(query) and str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)] and not is_whitelisted(str(chat_id)):
            with open("ban.txt", "a") as file:
                file.write(str(chat_id) + "\n")
            
            bot.reply_to(message, 
                        "🚫 تم حظرك من استخدام البوت بسبب استخدام كود طالب غير مسموح به.", 
                        parse_mode="HTML",
                        reply_markup=keyboard3)
            
            admin_msg = (
                f"🚨 تم حظر مستخدم تلقائيا\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"المستخدم: {user.first_name}\n"
                f"المعرف: {user.id}\n"
                f"اليوزر: @{user.username if user.username else 'لا يوجد'}\n"
                f"الكود المحظور: {query}"
            )
            bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
            return
    
    loading = bot.reply_to(message, "⏳ جاري البحث...", parse_mode="HTML")
    
    results, search_type = advanced_search.search(query)
    
    if search_type == "invalid_name":
        bot.edit_message_text(
            "❌ اسم الطالب يجب أن يكون ثنائي على الأقل (كلمتين)\n\n"
            "مثال: احمد علي\n"
            "أو: احمد محمد علي",
            chat_id=chat_id,
            message_id=loading.message_id,
            parse_mode="HTML",
            reply_markup=keyboard1
        )
        return
    
    if not results:
        bot.edit_message_text(
            f"❌ لم يتم العثور على طالب: {query}",
            chat_id=chat_id,
            message_id=loading.message_id,
            parse_mode="HTML",
            reply_markup=keyboard1
        )
        return
    
    search_type_text = "كود الطالب" if search_type == "code" else "الاسم"
    total_pages = (len(results) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    advanced_search.save_session(chat_id, query, results, search_type_text, total_pages, 0)
    
    admin_msg = (
        f"🔍 بحث في نظام الترتيب\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"المستخدم: {user.first_name}\n"
        f"المعرف: {user.id}\n"
        f"اليوزر: @{user.username if user.username else 'لا يوجد'}\n"
        f"نوع البحث: {search_type_text}\n"
        f"البحث عن: {query}\n"
        f"عدد النتائج: {len(results)}"
    )
    bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
    
    # عرض النتائج
    if search_type == "code" and len(results) == 1:
        display_student_detail(chat_id, loading.message_id, results[0], query, search_type_text, user)
    else:
        show_student_buttons(chat_id, loading.message_id, 0)


def show_student_buttons(chat_id, msg_id, page):
    """عرض أزرار الطلاب فقط مع أزرار التنقل"""
    page_results, current_page, total_pages = advanced_search.get_page_results(chat_id, page)
    
    if not page_results:
        bot.edit_message_text(
            "❌ انتهت جلسة البحث، يرجى البدء من جديد",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="HTML",
            reply_markup=keyboard1
        )
        return
    
    session = advanced_search.get_session(chat_id)
    if not session:
        return
    
    query = session['query']
    search_type = session['search_type']
    start_num = current_page * ITEMS_PER_PAGE + 1
    
    # بناء الرسالة البسيطة
    text = f"🔍 نتائج البحث عن: {query}\n"
    text += f"نوع البحث: {search_type}\n"
    text += f"إجمالي النتائج: {len(session['results'])} طالب\n"
    text += f"الصفحة {current_page + 1} من {total_pages}\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "اختر الطالب من القائمة:\n"
    
    # أزرار الطلاب فقط
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    for i, student in enumerate(page_results, start=start_num):
        name = student.get('name', 'غير معروف')
        code = student.get('code', 'غير معروف')
        
        # زر بسيط بالاسم فقط
        keyboard.add(types.InlineKeyboardButton(
            f"{i}. {name}", 
            callback_data=f"select_student_{code}"
        ))
    
    # أزرار التنقل بين الصفحات
    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(types.InlineKeyboardButton("◀️ السابق", callback_data=f"nav_page_{current_page - 1}"))
    if current_page + 1 < total_pages:
        nav_buttons.append(types.InlineKeyboardButton("التالي ▶️", callback_data=f"nav_page_{current_page + 1}"))
    
    if nav_buttons:
        keyboard.row(*nav_buttons)
    
    # أزرار إضافية
    btn_new = types.InlineKeyboardButton("🏆 بحث جديد", callback_data="student_ranking_query")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back")
    keyboard.add(btn_new, btn_back)
    
    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=msg_id,
        parse_mode="HTML",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("nav_page_"))
def handle_nav_page(call):
    """معالجة التنقل بين الصفحات"""
    chat_id = call.message.chat.id
    page = int(call.data.replace("nav_page_", ""))
    
    session = advanced_search.get_session(chat_id)
    if not session:
        bot.answer_callback_query(call.id, "❌ انتهت جلسة البحث")
        bot.edit_message_text(
            "❌ انتهت جلسة البحث، يرجى البدء من جديد",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="HTML",
            reply_markup=keyboard1
        )
        return
    
    if page < 0:
        page = 0
    if page >= session['total_pages']:
        page = session['total_pages'] - 1
    
    show_student_buttons(chat_id, call.message.message_id, page)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("select_student_"))
def handle_select_student(call):
    """معالجة اختيار طالب من القائمة"""
    chat_id = call.message.chat.id
    code = call.data.replace("select_student_", "")
    
    # التحقق من أن المستخدم ليس محظوراً
    try:
        with open("ban.txt", "r") as file:
            banned_users = file.read().splitlines()
    except FileNotFoundError:
        banned_users = []
    
    if str(chat_id) in banned_users:
        bot.answer_callback_query(call.id, "🚫 أنت محظور!", show_alert=True)
        return
    
    # التحقق من الكود المحظور
    is_banned = is_banned_student_code(code)
    is_admin = str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]
    is_whitelisted_user = is_whitelisted(str(chat_id))
    
    # للمستخدم العادي: إذا كان الكود محظور، يتم حظره
    if is_banned and not is_admin and not is_whitelisted_user:
        with open("ban.txt", "a") as file:
            file.write(str(chat_id) + "\n")
        
        bot.answer_callback_query(call.id, "🚫 تم حظرك بسبب محاولة عرض طالب محظور!", show_alert=True)
        bot.edit_message_text(
            "🚫 تم حظرك من استخدام البوت بسبب محاولة عرض طالب محظور.",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="HTML",
            reply_markup=keyboard3
        )
        
        admin_msg = (
            f"🚨 تم حظر مستخدم تلقائيا\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"المستخدم: {call.from_user.first_name}\n"
            f"المعرف: {call.from_user.id}\n"
            f"اليوزر: @{call.from_user.username if call.from_user.username else 'لا يوجد'}\n"
            f"السبب: محاولة عرض طالب محظور\n"
            f"الكود: {code}"
        )
        bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
        return
    
    # للأدمن أو المستخدم في الوايت ليست: عرض النتيجة حتى لو كان الكود محظور
    session = advanced_search.get_session(chat_id)
    search_query = session['query'] if session else code
    search_type = session['search_type'] if session else "الاسم"
    
    # الحصول على بيانات الطالب
    students_data = advanced_search.get_all_students_data()
    student = None
    
    for s in students_data:
        if s.get('code') == code:
            student = s
            break
    
    if not student:
        bot.answer_callback_query(call.id, "❌ لم يتم العثور على الطالب")
        return
    
    # إذا كان المستخدم أدمن أو في الوايت ليست والطالب محظور، نعرض تحذير مع النتيجة
    if is_banned and (is_admin or is_whitelisted_user):
        bot.answer_callback_query(call.id, "⚠️ هذا الطالب محظور (أنت مستثنى من الحظر)", show_alert=True)
    
    display_student_detail(chat_id, call.message.message_id, student, search_query, search_type, call.from_user, is_banned)


def display_student_detail(chat_id, msg_id, student, search_query, search_type, user, is_banned=False):
    """عرض تفاصيل الطالب"""
    
    code = student.get('code', 'غير معروف')
    
    ranking_result = get_student_complete_ranking(code)
    
    name = student.get('name', 'غير معروف')
    gpa = student.get('gpa', 0)
    hours = student.get('hours', 0)
    college = student.get('college', 'غير معروف')
    program = student.get('program', 'غير معروف')
    file_name = ranking_result.get('file_name', 'غير معروف') if ranking_result else 'غير معروف'
    file_title = student.get('file_title', 'غير معروف')
    
    # إضافة تحذير إذا كان الطالب محظور
    result_text = ""
    if is_banned:
        result_text += "⚠️ تنبيه: هذا الطالب مدرج في قائمة المحظورين ⚠️\n"
        result_text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    
    result_text += (
        f"✅ تفاصيل الطالب\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"الاسم: {name}\n"
        f"الرقم الجامعي: {code}\n"
        f"الكلية: {college}\n"
        f"القسم: {program}\n"
        f"المعدل التراكمي: {gpa:.3f}\n"
        f"الساعات المكتسبة: {hours}\n\n"
    )
    
    if ranking_result and ranking_result['college_ranking']:
        result_text += f"الترتيب في الكلية: #{ranking_result['college_ranking']}"
        if ranking_result['college_rank_equal']:
            result_text += " (مشترك)"
        result_text += f" من {ranking_result['total_college']} طالب\n"
        
        if ranking_result['same_gpa_college'] > 1:
            result_text += f"👥 عدد الطلاب بنفس المعدل في الكلية: {ranking_result['same_gpa_college']} طالب\n"
    
    if ranking_result and ranking_result['program_ranking']:
        result_text += f"الترتيب في القسم: #{ranking_result['program_ranking']}"
        if ranking_result['program_rank_equal']:
            result_text += " (مشترك)"
        result_text += f" من {ranking_result['total_program']} طالب\n"
        
        if ranking_result['same_gpa_program'] > 1:
            result_text += f"👥 عدد الطلاب بنفس المعدل في القسم: {ranking_result['same_gpa_program']} طالب\n"
    
    if file_name != 'غير معروف':
        result_text += f"\n📁 الملف: {file_name}\n"
    elif file_title != 'غير معروف':
        result_text += f"\n📁 الملف: {file_title}\n"
    
    result_text += f"━━━━━━━━━━━━━━━━━━━━━━"
    
    if user:
        admin_msg = (
            f"📊 عرض تفاصيل طالب\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"المستخدم: {user.first_name}\n"
            f"المعرف: {user.id}\n"
            f"اليوزر: @{user.username if user.username else 'لا يوجد'}\n"
            f"بحث عن: {search_query}\n"
            f"نوع البحث: {search_type}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"الطالب: {name}\n"
            f"الكود: {code}\n"
            f"المعدل: {gpa:.3f}\n"
        )
        if is_banned:
            admin_msg += f"⚠️ ملاحظة: هذا الطالب محظور (تم عرضه للأدمن/وايت ليست)\n"
        bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    current_page = advanced_search.get_session(chat_id)['current_page'] if advanced_search.get_session(chat_id) else 0
    btn_back = types.InlineKeyboardButton("🔙 رجوع للنتائج", callback_data=f"nav_page_{current_page}")
    btn_new = types.InlineKeyboardButton("🔍 بحث جديد", callback_data="student_ranking_query")
    keyboard.add(btn_back, btn_new)
    
    bot.edit_message_text(
        result_text,
        chat_id=chat_id,
        message_id=msg_id,
        parse_mode="HTML",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data == "noop")
def handle_noop(call):
    bot.answer_callback_query(call.id)

# ================== نظام جلب ترتيب الطلاب من ملف IDs (بدون إدارة جلسات) ==================
import requests
import json
import time
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

# ================== تعريف الأنواع ==================
class RequestStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"

@dataclass
class StudentResult:
    data: Optional[Dict] = None
    error: Optional[str] = None
    retries: int = 0
    status: RequestStatus = RequestStatus.FAILED

# ================== الإعدادات ==================
TEMP_IDS_FILE = "temp_ids.txt"
MAX_WORKERS = 10
MAX_RETRIES = 2
REQUEST_TIMEOUT = 8
DELAY_BETWEEN_REQUESTS = 0.03
RETRY_DELAY = 0.5

BASE_PARAM2 = {
    "ScopeID": "179.11.",
    "ScopeProgID": "12.",
    "ScopeLevelID": None,
    "ReportID": "",
    "silang": "A",
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}

# ================== إدارة الجلسة (المفتاح لحل مشكلة الفشل) ==================
# ================== إدارة الجلسة (الإصدار المحسن للسرعة) ==================
class SessionManager:
    def __init__(self, cookie_value: str):
        self.cookie_value = cookie_value
        # ✅ استخدام قفل على مستوى الفئة (class level lock) للتحكم في المعدل
        # هذا يضمن أن جميع الطلبات تتحكم في المعدل بشكل مركزي
        self._rate_limit_lock = threading.Lock()
        self._last_request_time = 0
        
    def get_session(self):
        """إنشاء جلسة جديدة لكل طلب (أفضل للتزامن)"""
        session = requests.Session()
        session.headers.update(HEADERS)
        session.cookies.set('userID', self.cookie_value)
        
        # إعدادات الاتصال المحسنة
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=MAX_WORKERS,
            pool_maxsize=MAX_WORKERS,
            max_retries=2
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def _wait_if_needed(self):
        """التحكم في معدل الطلبات (يتم تنفيذه بشكل متزامن)"""
        with self._rate_limit_lock:
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < DELAY_BETWEEN_REQUESTS:
                sleep_time = DELAY_BETWEEN_REQUESTS - time_since_last
                time.sleep(sleep_time)
            self._last_request_time = time.time()
    
    def make_request(self, student_id: str, retry_count: int = 0) -> StudentResult:
        """إرسال طلب لجلب بيانات الطالب (يعمل بشكل متوازي)"""
        
        # ✅ فقط التحكم في المعدل يتم بقفل، باقي الكود بدون قفل
        self._wait_if_needed()
        
        # ✅ إنشاء جلسة جديدة لكل طلب (أفضل للتزامن)
        session = self.get_session()
        
        payload = {
            "param0": "Reports.StudentData",
            "param1": "getStudentCourse",
            "param2": json.dumps({
                **BASE_PARAM2,
                "StudentCurrentID": student_id
            })
        }
        
        try:
            timeout = REQUEST_TIMEOUT * (retry_count + 1)
            
            response = session.post(
                "http://credit.minia.edu.eg/getJCI",
                data=payload,
                timeout=timeout,
                verify=False
            )
            
            if response.status_code != 200:
                if response.status_code == 429:  # Too Many Requests
                    time.sleep(1)
                    return StudentResult(error=f"rate_limit_{response.status_code}", retries=retry_count)
                return StudentResult(error=f"http_{response.status_code}", retries=retry_count)
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                text = response.text.strip()
                if text and '"data"' in text:
                    start = text.find('"data"')
                    end = text.find('}]', start) + 2
                    if end > start:
                        json_str = text[start-1:end] + '}'
                        try:
                            data = json.loads(json_str)
                        except:
                            return StudentResult(error="invalid_json", retries=retry_count)
                    else:
                        return StudentResult(error="invalid_json", retries=retry_count)
                else:
                    return StudentResult(error="invalid_json", retries=retry_count)
            
            if "data" not in data:
                return StudentResult(error="missing_data", retries=retry_count)
            
            if not data["data"] or not isinstance(data["data"], list):
                return StudentResult(error="no_data", retries=retry_count)
            
            first_record = data["data"][0]
            
            # ✅ استخراج المعدل التراكمي بشكل صحيح
            gpa = 0.0
            try:
                gpa = float(first_record.get("stuGPA", 0))
            except:
                gpa = 0.0
            
            student_data = {
                "id": student_id,
                "name": extract_name(first_record),
                "gpa": gpa,
                "earned_hours": first_record.get("stuEarnedHours", 0),
                "faculty": extract_faculty(first_record),
                "program": extract_program(first_record),
                "level": extract_level(first_record)
            }
            
            return StudentResult(data=student_data, status=RequestStatus.SUCCESS)
                
        except requests.exceptions.Timeout:
            return StudentResult(error="timeout", retries=retry_count)
        except requests.exceptions.ConnectionError:
            return StudentResult(error="connection", retries=retry_count)
        except Exception as e:
            return StudentResult(error=f"exception_{type(e).__name__}", retries=retry_count)
        finally:
            session.close()  # ✅ إغلاق الجلسة بعد الاستخدام

# ================== دوال استخراج البيانات ==================
def extract_name(record: Dict) -> str:
    name = record.get("StuName", "")
    if isinstance(name, str):
        return name.split("|")[0].strip()
    return "غير معروف"

def extract_gpa(record: Dict) -> float:
    try:
        gpa = record.get("stuGPA")
        if gpa:
            return float(gpa)
    except:
        pass
    return 0.0

def extract_faculty(record: Dict) -> str:
    faculty = record.get("faculty", "")
    if isinstance(faculty, str):
        return faculty.split("|")[0].strip()
    return "غير معروف"

def extract_program(record: Dict) -> str:
    prog = record.get("prog", "")
    if isinstance(prog, str):
        return prog.split("|")[0].strip()
    return "غير معروف"

def extract_level(record: Dict) -> str:
    level = record.get("lvl", "")
    if isinstance(level, str):
        return level.split("|")[0].strip()
    return "غير معروف"

# ================== جلب بيانات طالب مع إعادة المحاولة ==================
def fetch_student_with_retry(session_manager: SessionManager, student_id: str) -> Tuple[str, StudentResult]:
    result = session_manager.make_request(student_id)
    
    retry_count = 0
    while result.status != RequestStatus.SUCCESS and retry_count < MAX_RETRIES:
        retry_count += 1
        time.sleep(RETRY_DELAY * retry_count)
        result = session_manager.make_request(student_id, retry_count)
    
    return student_id, result

# ================== دوال مساعدة ==================
def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.0f} ثانية"
    minutes = seconds / 60
    return f"{minutes:.1f} دقيقة"

def load_ids_from_file(file_path: str) -> List[str]:
    student_ids = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and line.isdigit() and len(line) >= 8:
                    student_ids.append(line)
    except Exception as e:
        print(f"خطأ في قراءة الملف: {e}")
    return student_ids

# ================== تعيين الترتيب ==================
def assign_ranks(students: List[Dict]) -> List[Dict]:
    """تعيين الرتب مع إضافة علامة التعادل (tie)"""
    if not students:
        return []
    
    sorted_students = sorted(students, key=lambda x: x["gpa"], reverse=True)
    ranked_students = []
    current_rank = 1
    i = 0
    n = len(sorted_students)
    
    while i < n:
        current_gpa = sorted_students[i]["gpa"]
        same_gpa_count = 0
        
        # عد الطلاب الذين لديهم نفس المعدل
        j = i
        while j < n and abs(sorted_students[j]["gpa"] - current_gpa) < 0.0001:
            same_gpa_count += 1
            j += 1
        
        # أضف جميع الطلاب بنفس الرتبة
        for k in range(i, j):
            student = sorted_students[k].copy()
            student["rank"] = current_rank
            student["tie"] = same_gpa_count > 1  # ✅ إذا كان هناك أكثر من طالب بنفس المعدل
            ranked_students.append(student)
        
        i = j
        current_rank += same_gpa_count  # انتقل إلى الرتبة التالية بعد عدد الطلاب في الرتبة الحالية
    
    return ranked_students
# ================== حفظ النتائج ==================
def save_ranking_results(ranked_students: List[Dict], failed: List[Dict], total: int):
    """حفظ النتائج بالتنسيق المطلوب"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"ranking_{timestamp}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        # ترويسة الملف
        f.write("=" * 80 + "\n")
        f.write(f"ترتيب الطلاب حسب المعدل التراكمي - {timestamp}\n")
        f.write("=" * 80 + "\n\n")
        
        for student in ranked_students:
            # استخراج البيانات
            rank = student.get('rank', 1)
            name = student.get('name', 'غير معروف')
            code = student.get('id', 'غير معروف')
            gpa = student.get('gpa', 0)
            hours = student.get('earned_hours', 0)
            faculty = student.get('faculty', 'غير معروف')
            program = student.get('program', 'غير معروف')
            
            # ✅ إنشاء علامة التساوي (=) إذا كان هناك تعادل
            rank_str = f"#{rank}" + ("=" if student.get('tie', False) else "")
            
            # ✅ كتابة البيانات بنفس تنسيق الملف المطلوب
            f.write(f"[{rank_str}] {name}\n")
            f.write(f"   • الرقم الجامعي: {code}\n")
            f.write(f"   • المعدل التراكمي: {gpa:.3f}\n")
            f.write(f"   • الساعات المكتسبة: {hours}\n")
            f.write(f"   • الكلية: {faculty}\n")
            f.write(f"   • البرنامج: {program}\n")
            f.write("-" * 50 + "\n\n")
    
    return filename
# ================= نهاية نظام الترتيب المتكامل =================

# ================= دوال إدارة ملفات الترتيب =================

# ================== دالة المعالجة الرئيسية (تم التعديل) ==================
def process_students(chat_id: int, student_ids: List[str], progress_msg_id: int, cookie_value: str):
    """معالجة الطلاب باستخدام SessionManager"""
    try:
        total = len(student_ids)
        session_manager = SessionManager(cookie_value)  # إنشاء مدير الجلسة مرة واحدة
        successful = []
        failed = []
        error_stats = {}
        processed = 0
        
        start_time = time.time()
        last_update = time.time()
        
        bot.edit_message_text(
            f"🚀 *بدء معالجة {total} طالب...*\n"
            f"⚙️ العمال: {MAX_WORKERS} | 🔄 محاولات: {MAX_RETRIES+1}",
            chat_id=chat_id,
            message_id=progress_msg_id,
            parse_mode="Markdown"
        )
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_id = {
                executor.submit(fetch_student_with_retry, session_manager, sid): sid 
                for sid in student_ids
            }
            
            total_futures = len(future_to_id)
            
            for future in as_completed(future_to_id):
                processed += 1
                student_id = future_to_id[future]
                
                try:
                    _, result = future.result()
                    
                    if result.status == RequestStatus.SUCCESS and result.data:
                        successful.append(result.data)
                    else:
                        error_type = result.error or "unknown"
                        failed.append({
                            "id": student_id,
                            "error": error_type,
                            "retries": result.retries
                        })
                        error_stats[error_type] = error_stats.get(error_type, 0) + 1
                    
                    # تحديث التقدم
                    current_time = time.time()
                    if (processed % 5 == 0) or (current_time - last_update >= 1) or (processed == total_futures):
                        elapsed = current_time - start_time
                        speed = processed / elapsed if elapsed > 0 else 0
                        progress_percent = (processed / total_futures) * 100
                        
                        status_text = (
                            f"🚀 *معالجة الطلاب...*\n\n"
                            f"📊 {processed}/{total_futures} ({progress_percent:.1f}%)\n"
                            f"⚡ السرعة: {speed:.1f}/ثانية\n"
                            f"✅ ناجح: {len(successful)} | ❌ فاشل: {len(failed)}"
                        )
                        
                        try:
                            bot.edit_message_text(
                                status_text,
                                chat_id=chat_id,
                                message_id=progress_msg_id,
                                parse_mode="Markdown"
                            )
                        except:
                            pass
                        
                        last_update = current_time
                        
                except Exception as e:
                    failed.append({
                        "id": student_id,
                        "error": f"exception_{type(e).__name__}",
                        "retries": 0
                    })
        
        elapsed_time = time.time() - start_time
        
        if not successful:
            bot.edit_message_text(
                "❌ *فشلت المعالجة بالكامل*",
                chat_id=chat_id,
                message_id=progress_msg_id,
                parse_mode="Markdown"
            )
            return
        
        ranked_students = assign_ranks(successful)
        result_file = save_ranking_results(ranked_students, failed, total)
        
        success_rate = (len(successful) / total) * 100
        avg_speed = total / elapsed_time if elapsed_time > 0 else 0
        
        summary = (
            f"✅ *اكتملت المعالجة*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏱️ الوقت: {format_time(elapsed_time)}\n"
            f"📊 الإجمالي: {total}\n"
            f"✅ ناجح: {len(successful)} ({success_rate:.1f}%)\n"
            f"❌ فاشل: {len(failed)}\n"
            f"⚡ السرعة: {avg_speed:.1f}/ثانية\n\n"
            f"📁 النتائج في: `{result_file}`"
        )
        
        bot.send_message(chat_id, summary, parse_mode="Markdown")
        
        with open(result_file, 'rb') as f:
            bot.send_document(chat_id, f)
        
        # تنظيف
        if os.path.exists(TEMP_IDS_FILE):
            os.remove(TEMP_IDS_FILE)
        if chat_id in chat_data:
            chat_data[chat_id].pop('temp_ids', None)
            chat_data[chat_id].pop('progress_msg_id', None)
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطأ: {str(e)[:100]}")

# ================== معالج رفع الملف (تم التعديل لتمرير الكوكيز) ==================
@bot.callback_query_handler(func=lambda call: call.data == "admin_upload_ids")
def handle_admin_upload_ids(call):
    chat_id = call.message.chat.id
    
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية.")
        return
    
    # التحقق من الكوكيز
    try:
        current_cookie = get_current_cookie()
        if not current_cookie or len(current_cookie) < 30:
            keyboard = types.InlineKeyboardMarkup()
            btn_cookies = types.InlineKeyboardButton("🍪 إدارة الكوكيز", callback_data="manage_cookies_accounts")
            keyboard.add(btn_cookies)
            
            bot.edit_message_text(
                "❌ *لا توجد كوكيز صالحة*",
                chat_id=chat_id,
                message_id=call.message.message_id,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return
    except:
        pass
    
    # تخزين الكوكيز مؤقتاً للاستخدام لاحقاً
    if chat_id not in chat_data:
        chat_data[chat_id] = {}
    chat_data[chat_id]['temp_cookie'] = get_current_cookie()
    
    bot.edit_message_text(
        "📤 *رفع ملف IDs*\n\n"
        "أرسل ملف txt بأرقام الطلاب\n"
        "كل رقم في سطر",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )
    
    bot.register_next_step_handler(call.message, process_ids_file)

def process_ids_file(message):
    chat_id = message.chat.id
    
    if not message.document:
        bot.reply_to(message, "❌ أرسل ملف صالح")
        return
    
    file_info = bot.get_file(message.document.file_id)
    
    if not file_info.file_path.endswith('.txt'):
        bot.reply_to(message, "❌ الملف يجب أن يكون .txt")
        return
    
    downloaded = bot.download_file(file_info.file_path)
    
    with open(TEMP_IDS_FILE, 'wb') as f:
        f.write(downloaded)
    
    student_ids = load_ids_from_file(TEMP_IDS_FILE)
    
    if not student_ids:
        os.remove(TEMP_IDS_FILE)
        bot.reply_to(message, "❌ لا توجد أرقام صالحة")
        return
    
    # تخزين IDs
    if chat_id not in chat_data:
        chat_data[chat_id] = {}
    chat_data[chat_id]['temp_ids'] = student_ids
    
    total = len(student_ids)
    estimated_time = total / 8
    
    keyboard = types.InlineKeyboardMarkup()
    btn_start = types.InlineKeyboardButton("✅ بدء", callback_data="start_ranking_process")
    btn_cancel = types.InlineKeyboardButton("❌ إلغاء", callback_data="back_to_admin")
    keyboard.add(btn_start, btn_cancel)
    
    bot.reply_to(
        message,
        f"✅ *تم استلام {total} طالب*\n"
        f"⏱️ الوقت المتوقع: {format_time(estimated_time)}\n\n"
        f"هل تريد البدء؟",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "start_ranking_process")
def handle_start_ranking_process(call):
    chat_id = call.message.chat.id
    
    student_ids = chat_data.get(chat_id, {}).get('temp_ids', [])
    cookie_value = chat_data.get(chat_id, {}).get('temp_cookie', '')
    
    if not student_ids:
        bot.edit_message_text("❌ لا توجد بيانات", chat_id=chat_id, message_id=call.message.message_id)
        return
    
    if not cookie_value:
        bot.edit_message_text("❌ لا توجد كوكيز صالحة", chat_id=chat_id, message_id=call.message.message_id)
        return
    
    # إنشاء رسالة التقدم
    progress = bot.edit_message_text(
        f"🚀 *بدء معالجة {len(student_ids)} طالب...*",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown"
    )
    
    # تخزين معرف رسالة التقدم
    chat_data[chat_id]['progress_msg_id'] = progress.message_id
    
    # بدء المعالجة مع تمرير الكوكيز
    threading.Thread(
        target=process_students,
        args=(chat_id, student_ids, progress.message_id, cookie_value),
        daemon=True
    ).start()
# ================= لوحة تحكم الأدمن =================
@bot.callback_query_handler(func=lambda call: call.data == "ranking_admin")
def handle_ranking_admin(call):
    """عرض لوحة تحكم الترتيب للأدمن"""
    chat_id = call.message.chat.id
    
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية.")
        return
    
    files = get_ranking_files()
    
    text = (
        "🏆 *نظام الترتيب - لوحة التحكم*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📁 عدد الملفات: `{len(files)}`\n"
    )
    
    if files:
        text += f"📅 آخر تحديث: `{time.strftime('%Y-%m-%d %H:%M', time.localtime(files[0]['modified']))}`\n\n"
        text += "📋 *أحدث الملفات:*\n"
        for i, f in enumerate(files[:5], 1):
            modified = time.strftime('%Y-%m-%d', time.localtime(f['modified']))
            size_kb = f['size'] / 1024
            text += f"{i}. `{f['name']}`\n"
            text += f"   📅 {modified} | 📊 {size_kb:.1f} KB\n"
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_upload = types.InlineKeyboardButton("📤 رفع ملف ترتيب", callback_data="ranking_upload_file")
    btn_list = types.InlineKeyboardButton("📋 إدارة الملفات", callback_data="ranking_manage_files")
    btn_ids = types.InlineKeyboardButton("📊 جلب ترتيب من IDs", callback_data="admin_upload_ids")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_admin")
    
    keyboard.add(btn_upload, btn_list)
    keyboard.add(btn_ids)
    keyboard.add(btn_back)
    
    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data == "ranking_manage_files")
def handle_ranking_manage_files(call):
    """عرض قائمة الملفات مع أزرار الإدارة (باستخدام callback_data قصير)"""
    chat_id = call.message.chat.id
    files = get_ranking_files()
    
    if not files:
        bot.edit_message_text(
            "📭 *لا توجد ملفات ترتيب*\n\n"
            "يمكنك رفع ملف جديد باستخدام زر '📤 رفع ملف ترتيب'",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        return
    
    text = "📋 *إدارة ملفات الترتيب*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "اختر ملفاً للتعامل معه:\n\n"
    
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    # تخزين قائمة الملفات في chat_data
    if chat_id not in chat_data:
        chat_data[chat_id] = {}
    chat_data[chat_id]['ranking_files'] = files[:10]  # خذ أول 10 ملفات فقط
    
    for i, file in enumerate(files[:10], 1):
        # استخدام اسم قصير للعرض
        display_name = file['name']
        if len(display_name) > 30:
            display_name = display_name[:27] + "..."
        
        # استخدام callback_data قصير جداً
        btn = types.InlineKeyboardButton(
            f"{i}. {display_name}",
            callback_data=f"rf_{i}"  # rf = ranking file
        )
        keyboard.add(btn)
    
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="ranking_admin")
    keyboard.add(btn_back)
    
    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("rf_"))
def handle_ranking_file_select(call):
    """معالجة اختيار ملف من القائمة"""
    chat_id = call.message.chat.id
    file_index = int(call.data.replace("rf_", "")) - 1
    
    # استرجاع اسم الملف من البيانات المخزنة
    files = chat_data.get(chat_id, {}).get('ranking_files', [])
    
    if file_index < 0 or file_index >= len(files):
        bot.answer_callback_query(call.id, "❌ ملف غير صالح")
        return
    
    filename = files[file_index]['name']
    
    # تخزين اسم الملف بهاش قصير
    import hashlib
    file_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
    
    if chat_id not in chat_data:
        chat_data[chat_id] = {}
    chat_data[chat_id][f'file_{file_hash}'] = filename
    
    # عرض خيارات الملف
    show_file_options(call, chat_id, filename, file_hash)

def show_file_options(call, chat_id, filename, file_hash):
    """عرض خيارات ملف معين"""
    filepath = os.path.join(RANKING_FILES_FOLDER, filename)
    
    if not os.path.exists(filepath):
        bot.answer_callback_query(call.id, "❌ الملف غير موجود")
        return
    
    students = parse_ranking_file(filepath)
    file_size = os.path.getsize(filepath) / 1024
    modified = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(filepath)))
    
    # اسم قصير للعرض
    display_name = filename
    if len(display_name) > 40:
        display_name = display_name[:37] + "..."
    
    text = f"📄 *الملف: {display_name}*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"📏 الحجم: `{file_size:.1f} KB`\n"
    text += f"📅 آخر تعديل: `{modified}`\n"
    text += f"👥 عدد الطلاب: `{len(students)}`\n"
    
    if students:
        text += f"🏆 أعلى معدل: `{max(s.get('gpa', 0) for s in students):.3f}`\n"
        text += f"📉 أقل معدل: `{min(s.get('gpa', 0) for s in students):.3f}`\n"
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # استخدام callback_data قصير جداً
    btn_rename = types.InlineKeyboardButton("✏️ تعديل", callback_data=f"rn_{file_hash}")
    btn_delete = types.InlineKeyboardButton("🗑️ حذف", callback_data=f"del_{file_hash}")
    btn_view = types.InlineKeyboardButton("👁️ عرض", callback_data=f"vw_{file_hash}")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="ranking_manage_files")
    
    keyboard.add(btn_rename, btn_delete)
    keyboard.add(btn_view)
    keyboard.add(btn_back)
    
    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("rn_"))
def handle_ranking_rename_file(call):
    """تعديل اسم ملف"""
    chat_id = call.message.chat.id
    file_hash = call.data.replace("rn_", "")
    
    filename = chat_data.get(chat_id, {}).get(f'file_{file_hash}')
    if not filename:
        bot.answer_callback_query(call.id, "❌ ملف غير صالح")
        return
    
    bot.edit_message_text(
        f"✏️ *تعديل اسم الملف*\n\n"
        f"الملف الحالي: `{filename}`\n\n"
        f"📝 أرسل الاسم الجديد للملف (مع الامتداد .txt):",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )
    
    bot.register_next_step_handler(call.message, process_ranking_rename_file, filename)
def rename_ranking_file(old_filename, new_filename):
    """إعادة تسمية ملف ترتيب"""
    try:
        old_path = os.path.join(RANKING_FILES_FOLDER, old_filename)
        new_path = os.path.join(RANKING_FILES_FOLDER, new_filename)
        
        if not os.path.exists(old_path):
            return False, f"الملف {old_filename} غير موجود"
        
        if os.path.exists(new_path):
            return False, f"الملف {new_filename} موجود بالفعل"
        
        os.rename(old_path, new_path)
        return True, f"تم إعادة تسمية الملف إلى {new_filename}"
    except Exception as e:
        return False, f"خطأ في إعادة التسمية: {str(e)}"

def delete_ranking_file(filename):
    """حذف ملف ترتيب"""
    try:
        filepath = os.path.join(RANKING_FILES_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return False, f"الملف {filename} غير موجود"
        
        os.remove(filepath)
        return True, f"تم حذف الملف {filename} بنجاح"
    except Exception as e:
        return False, f"خطأ في الحذف: {str(e)}"


def process_ranking_rename_file(message, old_filename):
    """معالجة تعديل اسم الملف"""
    chat_id = message.chat.id
    new_filename = message.text.strip()
    
    if not new_filename.endswith('.txt'):
        new_filename += '.txt'
    
    # التحقق من صحة الاسم
    if not re.match(r'^[\w\s\-_.]+\.txt$', new_filename):
        bot.reply_to(
            message,
            "❌ *اسم ملف غير صالح*\n"
            "استخدم أحرف وأرقام وشرطات فقط",
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        return
    
    success, msg = rename_ranking_file(old_filename, new_filename)
    
    if success:
        bot.reply_to(
            message,
            f"✅ *{msg}*",
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
    else:
        bot.reply_to(
            message,
            f"❌ *{msg}*",
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_"))
def handle_ranking_delete_file(call):
    """تأكيد حذف ملف"""
    chat_id = call.message.chat.id
    file_hash = call.data.replace("del_", "")
    
    filename = chat_data.get(chat_id, {}).get(f'file_{file_hash}')
    if not filename:
        bot.answer_callback_query(call.id, "❌ ملف غير صالح")
        return
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_confirm = types.InlineKeyboardButton("✅ نعم، احذف", callback_data=f"cf_{file_hash}")
    btn_cancel = types.InlineKeyboardButton("❌ إلغاء", callback_data="ranking_manage_files")
    
    keyboard.add(btn_confirm, btn_cancel)
    
    bot.edit_message_text(
        f"⚠️ *تأكيد حذف الملف*\n\n"
        f"هل أنت متأكد من حذف الملف:\n"
        f"`{filename}`؟\n\n"
        f"❗ هذا الإجراء لا يمكن التراجع عنه",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("cf_"))
def handle_ranking_confirm_delete(call):
    """تنفيذ حذف الملف"""
    chat_id = call.message.chat.id
    file_hash = call.data.replace("cf_", "")
    
    filename = chat_data.get(chat_id, {}).get(f'file_{file_hash}')
    if not filename:
        bot.answer_callback_query(call.id, "❌ ملف غير صالح")
        return
    
    success, msg = delete_ranking_file(filename)
    
    if success:
        bot.answer_callback_query(call.id, f"✅ تم حذف {filename}")
        # العودة لقائمة الملفات
        handle_ranking_manage_files(call)
    else:
        bot.answer_callback_query(call.id, f"❌ فشل الحذف")
        handle_ranking_manage_files(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("vw_"))
def handle_ranking_view_file(call):
    """عرض محتوى ملف معين"""
    chat_id = call.message.chat.id
    file_hash = call.data.replace("vw_", "")
    
    filename = chat_data.get(chat_id, {}).get(f'file_{file_hash}')
    if not filename:
        bot.answer_callback_query(call.id, "❌ ملف غير صالح")
        return
    
    filepath = os.path.join(RANKING_FILES_FOLDER, filename)
    
    if not os.path.exists(filepath):
        bot.answer_callback_query(call.id, "❌ الملف غير موجود")
        return
    
    students = parse_ranking_file(filepath)
    
    if not students:
        bot.edit_message_text(
            "❌ *لا توجد بيانات في هذا الملف*",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        return
    
    text = f"📄 *{filename}*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"👥 عدد الطلاب: `{len(students)}`\n"
    text += f"🏆 أعلى معدل: `{max(s.get('gpa', 0) for s in students):.3f}`\n"
    text += f"📉 أقل معدل: `{min(s.get('gpa', 0) for s in students):.3f}`\n"
    text += f"📊 متوسط المعدلات: `{sum(s.get('gpa', 0) for s in students) / len(students):.3f}`\n\n"
    
    # أفضل 5 طلاب
    text += "🏅 *أفضل 5 طلاب:*\n"
    top_students = sorted(students, key=lambda x: x.get('gpa', 0), reverse=True)[:5]
    for i, s in enumerate(top_students, 1):
        text += f"{i}. `{s.get('name', '')[:30]}` - معدل: `{s.get('gpa', 0):.3f}`\n"
    
    keyboard = types.InlineKeyboardMarkup()
    btn_download = types.InlineKeyboardButton("📥 تحميل الملف", callback_data=f"dn_{file_hash}")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="ranking_manage_files")
    
    keyboard.add(btn_download)
    keyboard.add(btn_back)
    
    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("dn_"))
def handle_ranking_download_file(call):
    """تحميل ملف ترتيب"""
    chat_id = call.message.chat.id
    file_hash = call.data.replace("dn_", "")
    
    filename = chat_data.get(chat_id, {}).get(f'file_{file_hash}')
    if not filename:
        bot.answer_callback_query(call.id, "❌ ملف غير صالح")
        return
    
    filepath = os.path.join(RANKING_FILES_FOLDER, filename)
    
    if not os.path.exists(filepath):
        bot.answer_callback_query(call.id, "❌ الملف غير موجود")
        return
    
    with open(filepath, 'rb') as f:
        bot.send_document(chat_id, f, caption=f"📥 {filename}")
    
    bot.answer_callback_query(call.id, "✅ تم إرسال الملف")

@bot.callback_query_handler(func=lambda call: call.data == "ranking_upload_file")
def handle_ranking_upload(call):
    """رفع ملف ترتيب جديد"""
    chat_id = call.message.chat.id
    
    bot.edit_message_text(
        "📤 *رفع ملف ترتيب جديد*\n\n"
        "أرسل ملف `.txt` يحتوي على بيانات الترتيب\n\n"
        "✅ *ملاحظات:*\n"
        "• الملف يجب أن يكون بصيغة `.txt`\n"
        "• سيتم حفظه في مجلد `ranking_files`\n"
        "• يمكنك إرسال عدة ملفات",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )
    
    bot.register_next_step_handler(call.message, process_ranking_file_upload)

def process_ranking_file_upload(message):
    """معالجة ملف الترتيب المرفوع"""
    chat_id = message.chat.id
    
    if not message.document:
        bot.reply_to(message, "❌ *الرجاء إرسال ملف صالح*", parse_mode="Markdown")
        return
    
    file_info = bot.get_file(message.document.file_id)
    
    # التحقق من امتداد الملف
    if not file_info.file_path.endswith('.txt'):
        bot.reply_to(message, "❌ *الملف يجب أن يكون بصيغة .txt*", parse_mode="Markdown")
        return
    
    # تحميل الملف
    downloaded_file = bot.download_file(file_info.file_path)
    
    # إنشاء اسم للملف
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"ranking_{timestamp}.txt"
    filepath = os.path.join(RANKING_FILES_FOLDER, filename)
    
    # حفظ الملف
    with open(filepath, 'wb') as f:
        f.write(downloaded_file)
    
    # تحليل الملف للتحقق من صحته
    students = parse_ranking_file(filepath)
    
    if students:
        bot.reply_to(
            message,
            f"✅ *تم رفع الملف بنجاح*\n\n"
            f"📁 اسم الملف: `{filename}`\n"
            f"👥 عدد الطلاب: `{len(students)}`\n"
            f"🏆 أعلى معدل: `{max(s.get('gpa', 0) for s in students):.3f}`",
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
    else:
        # إذا كان الملف فارغاً أو غير صالح، احذفه
        os.remove(filepath)
        bot.reply_to(
            message,
            "❌ *الملف لا يحتوي على بيانات صالحة*\n"
            "تأكد من تنسيق الملف ثم حاول مرة أخرى",
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
# ================== نظام الأكواد المميزة (المعدل بالكامل) ==================
import random
import string

PREMIUM_CODES_FILE = "premium_codes.json"
USER_PREMIUM_FILE = "user_premium.json"

# ================== دوال توليد الأكواد العشوائية ==================
def generate_random_code(prefix="abm_"):
    """توليد كود عشوائي بالتنسيق abm_XXXXXX"""
    letters = ''.join(random.choices(string.ascii_lowercase, k=3))
    digits = ''.join(random.choices(string.digits, k=3))
    mixed = list(letters + digits)
    random.shuffle(mixed)
    code_suffix = ''.join(mixed)
    return f"{prefix}{code_suffix}"

def generate_multiple_codes(num_codes, prefix="abm_"):
    """توليد عدة أكواد عشوائية"""
    codes = []
    seen = set()
    
    for _ in range(num_codes):
        new_code = generate_random_code(prefix)
        while new_code in seen:
            new_code = generate_random_code(prefix)
        seen.add(new_code)
        codes.append(new_code)
    
    return codes

# ================== دوال تحميل وحفظ الأكواد ==================
def load_premium_codes():
    try:
        with open(PREMIUM_CODES_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_premium_codes(codes):
    with open(PREMIUM_CODES_FILE, "w") as f:
        json.dump(codes, f, indent=4)

def load_user_premium():
    try:
        with open(USER_PREMIUM_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_user_premium(users):
    with open(USER_PREMIUM_FILE, "w") as f:
        json.dump(users, f, indent=4)

def add_premium_code(code, code_type="single_use", created_by=None):
    """إضافة كود مميز"""
    codes = load_premium_codes()
    codes[code] = {
        "type": code_type,
        "used": False,
        "used_by": None,
        "used_at": None,
        "created_at": time.time(),
        "created_by": created_by
    }
    save_premium_codes(codes)
    return True

def add_multiple_premium_codes(codes_list, code_type="single_use", created_by=None):
    """إضافة عدة أكواد مميزة دفعة واحدة"""
    codes = load_premium_codes()
    added = 0
    
    for code in codes_list:
        if code not in codes:
            codes[code] = {
                "type": code_type,
                "used": False,
                "used_by": None,
                "used_at": None,
                "created_at": time.time(),
                "created_by": created_by
            }
            added += 1
    
    save_premium_codes(codes)
    return added

def delete_premium_code(code):
    """حذف كود مميز"""
    codes = load_premium_codes()
    if code in codes:
        del codes[code]
        save_premium_codes(codes)
        return True
    return False

def delete_all_premium_codes():
    """حذف جميع الأكواد المميزة"""
    codes = load_premium_codes()
    count = len(codes)
    save_premium_codes({})
    return count

def is_premium_code_valid(code, user_id):
    """التحقق من صحة الكود المميز وتفعيله للمستخدم"""
    codes = load_premium_codes()
    
    if code not in codes:
        return False
    
    code_data = codes[code]
    
    if code_data["type"] == "single_use" and code_data.get("used", False):
        return False
    
    if code_data["type"] == "single_use":
        code_data["used"] = True
        code_data["used_by"] = str(user_id)
        code_data["used_at"] = time.time()
        save_premium_codes(codes)
    
    return True

def get_premium_codes_stats():
    """إحصائيات الأكواد المميزة"""
    codes = load_premium_codes()
    permanent = sum(1 for c in codes.values() if c.get("type") == "permanent")
    single_use_total = sum(1 for c in codes.values() if c.get("type") == "single_use")
    single_use_used = sum(1 for c in codes.values() if c.get("type") == "single_use" and c.get("used", False))
    
    return {
        "total": len(codes),
        "permanent": permanent,
        "single_use_total": single_use_total,
        "single_use_used": single_use_used,
        "single_use_available": single_use_total - single_use_used
    }

# ================== دوال إدارة المستخدمين المميزين ==================
def add_premium_user_directly(user_id, added_by=None, reason=None):
    """إضافة مستخدم مميز مباشرة (بدون كود)"""
    users = load_user_premium()
    user_id_str = str(user_id)
    
    if user_id_str in users:
        return False, "المستخدم موجود بالفعل في قائمة المميزين"
    
    users[user_id_str] = {
        "activated_at": time.time(),
        "activated_by": added_by,
        "reason": reason or "تمت الإضافة يدوياً بواسطة الأدمن",
        "code": "manual_add",
        "type": "manual"
    }
    save_user_premium(users)
    return True, "تمت إضافة المستخدم إلى قائمة المميزين بنجاح"

def remove_premium_user(user_id):
    """حذف مستخدم من قائمة المميزين"""
    users = load_user_premium()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        return False, "المستخدم غير موجود في قائمة المميزين"
    
    del users[user_id_str]
    save_user_premium(users)
    return True, "تم حذف المستخدم من قائمة المميزين"

def get_premium_users_details():
    """الحصول على تفاصيل المستخدمين المميزين"""
    users = load_user_premium()
    details = []
    
    for user_id, data in users.items():
        details.append({
            "user_id": user_id,
            "activated_at": data.get("activated_at", 0),
            "activated_by": data.get("activated_by", "غير معروف"),
            "reason": data.get("reason", "غير محدد"),
            "code": data.get("code", "غير معروف"),
            "type": data.get("type", "code")
        })
    
    details.sort(key=lambda x: x["activated_at"], reverse=True)
    return details

def check_and_activate_premium(chat_id, user_id, text):
    """التحقق التلقائي من وجود كود وتفعيله"""
    if not text:
        return False
    
    codes = load_premium_codes()
    
    for code, data in codes.items():
        if code in text:
            if data["type"] == "permanent":
                users = load_user_premium()
                if str(chat_id) not in users:
                    users[str(chat_id)] = {
                        "activated_at": time.time(),
                        "code": code,
                        "type": "code",
                        "activated_by": "user"
                    }
                    save_user_premium(users)
                    
                    bot.send_message(chat_id, f"✅ *تم تفعيل البوت بنجاح!*\n📌 الكود: `{code}`\n🎉 يمكنك استخدام البوت حتى في أوقات الصيانة.", parse_mode="Markdown")
                    bot.send_message(admin_chat_id2, f"👑 *تم تفعيل كود مميز*\n• المستخدم: `{chat_id}`\n• الكود: `{code}`\n• النوع: دائم", parse_mode="Markdown")
                return True
                
            elif data["type"] == "single_use" and not data.get("used", False):
                data["used"] = True
                data["used_by"] = str(user_id)
                data["used_at"] = time.time()
                save_premium_codes(codes)
                
                users = load_user_premium()
                if str(chat_id) not in users:
                    users[str(chat_id)] = {
                        "activated_at": time.time(),
                        "code": code,
                        "type": "code",
                        "activated_by": "user"
                    }
                    save_user_premium(users)
                    
                    bot.send_message(chat_id, f"✅ *تم تفعيل البوت بنجاح!*\n📌 الكود: `{code}`\n🎉 يمكنك استخدام البوت حتى في أوقات الصيانة.", parse_mode="Markdown")
                    bot.send_message(admin_chat_id2, f"👑 *تم تفعيل كود مميز*\n• المستخدم: `{chat_id}`\n• الكود: `{code}`\n• النوع: لمرة واحدة", parse_mode="Markdown")
                return True
    return False

def is_premium_user(chat_id):
    """التحقق من أن المستخدم مميز"""
    users = load_user_premium()
    return str(chat_id) in users

def can_use_bot(chat_id):
    """التحقق من إمكانية استخدام البوت"""
    if load_bot_status():
        return True
    return is_premium_user(chat_id)

def load_bot_status():
    try:
        with open("bot_running.json", "r") as f:
            data = json.load(f)
            return data.get("running", True)
    except:
        return True

def save_bot_status(running):
    with open("bot_running.json", "w") as f:
        json.dump({"running": running}, f)


# ================== لوحة إدارة الأكواد المميزة ==================
@bot.callback_query_handler(func=lambda call: call.data == "manage_premium_codes")
def handle_manage_premium_codes(call):
    chat_id = call.message.chat.id
    
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية.")
        return
    
    stats = get_premium_codes_stats()
    users_count = len(load_user_premium())
    
    text = (
        "👑 *إدارة الأكواد والمستخدمين المميزين*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 *إحصائيات الأكواد:*\n"
        f"• ✅ أكواد دائمة: `{stats['permanent']}`\n"
        f"• 🔄 أكواد لمرة واحدة: `{stats['single_use_total']}`\n"
        f"  - متاحة: `{stats['single_use_available']}`\n"
        f"  - مستخدمة: `{stats['single_use_used']}`\n\n"
        f"👥 *المستخدمين المميزين:* `{users_count}`\n"
    )
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_add_permanent = types.InlineKeyboardButton("➕ إضافة كود دائم", callback_data="add_permanent_code")
    btn_add_single = types.InlineKeyboardButton("🎲 إضافة أكواد عشوائية", callback_data="add_single_code")
    btn_delete_code = types.InlineKeyboardButton("🗑️ حذف كود", callback_data="delete_premium_code")
    btn_delete_all_codes = types.InlineKeyboardButton("⚠️ حذف جميع الأكواد", callback_data="delete_all_codes")
    btn_list_codes = types.InlineKeyboardButton("📋 عرض جميع الأكواد", callback_data="list_all_premium_codes")
    
    btn_add_user = types.InlineKeyboardButton("👤 إضافة مستخدم مميز", callback_data="add_premium_user")
    btn_remove_user = types.InlineKeyboardButton("🗑️ حذف مستخدم مميز", callback_data="remove_premium_user")
    btn_list_users = types.InlineKeyboardButton("👥 عرض المستخدمين المميزين", callback_data="list_premium_users")
    
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_admin")
    
    keyboard.add(btn_add_permanent, btn_add_single)
    keyboard.add(btn_delete_code, btn_delete_all_codes)
    keyboard.add(btn_list_codes)
    keyboard.add(btn_add_user, btn_remove_user)
    keyboard.add(btn_list_users)
    keyboard.add(btn_back)
    
    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ================== إضافة كود دائم ==================
@bot.callback_query_handler(func=lambda call: call.data == "add_permanent_code")
def handle_add_permanent_code(call):
    chat_id = call.message.chat.id
    
    bot.edit_message_text(
        "✍️ *إضافة كود دائم*\n\n"
        "أدخل الكود الذي تريد إضافته (كود دائم صالح دائماً):\n"
        "مثال: `PERM-ABC-123`\n\n"
        "📌 هذا الكود يمكن استخدامه من قبل أي مستخدم وسيبقى صالحاً للأبد.",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )
    bot.register_next_step_handler(call.message, process_add_permanent_code)


def process_add_permanent_code(message):
    chat_id = message.chat.id
    code = message.text.strip()
    
    if not code:
        bot.reply_to(message, "❌ الكود لا يمكن أن يكون فارغاً.", reply_markup=get_back_button())
        return
    
    codes = load_premium_codes()
    if code in codes:
        bot.reply_to(message, f"❌ *الكود `{code}` موجود بالفعل.*", parse_mode="Markdown", reply_markup=get_back_button())
        return
    
    add_premium_code(code, "permanent", message.from_user.id)
    
    bot.reply_to(
        message,
        f"✅ *تم إضافة الكود الدائم:*\n`{code}`\n\n"
        f"📌 هذا الكود صالح دائماً ويمكن لأي مستخدم استخدامه.",
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )


# ================== إضافة أكواد عشوائية ==================
@bot.callback_query_handler(func=lambda call: call.data == "add_single_code")
def handle_add_single_code(call):
    chat_id = call.message.chat.id
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_5 = types.InlineKeyboardButton("🎲 5 أكواد", callback_data="generate_5_codes")
    btn_10 = types.InlineKeyboardButton("🎲 10 أكواد", callback_data="generate_10_codes")
    btn_20 = types.InlineKeyboardButton("🎲 20 كود", callback_data="generate_20_codes")
    btn_50 = types.InlineKeyboardButton("🎲 50 كود", callback_data="generate_50_codes")
    btn_custom = types.InlineKeyboardButton("✏️ عدد مخصص", callback_data="generate_custom_codes")
    btn_manual = types.InlineKeyboardButton("✍️ إدخال كود يدوياً", callback_data="manual_single_code")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="manage_premium_codes")
    
    keyboard.add(btn_5, btn_10)
    keyboard.add(btn_20, btn_50)
    keyboard.add(btn_custom, btn_manual)
    keyboard.add(btn_back)
    
    bot.edit_message_text(
        "🎲 *توليد أكواد عشوائية*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📝 *تنسيق الكود:* `abm_xxxxxx`\n"
        "• يبدأ بـ `abm_` متبوعاً بـ 6 أحرف وأرقام عشوائية\n"
        "• كل كود صالح لمرة واحدة فقط\n\n"
        "🔢 *اختر عدد الأكواد التي تريد توليدها:*",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data in ["generate_5_codes", "generate_10_codes", "generate_20_codes", "generate_50_codes"])
def handle_generate_fixed_codes(call):
    chat_id = call.message.chat.id
    
    num_map = {
        "generate_5_codes": 5,
        "generate_10_codes": 10,
        "generate_20_codes": 20,
        "generate_50_codes": 50
    }
    
    num_codes = num_map.get(call.data, 5)
    new_codes = generate_multiple_codes(num_codes, "abm_")
    added = add_multiple_premium_codes(new_codes, "single_use", call.from_user.id)
    
    generated_text = ""
    for i, code in enumerate(new_codes, 1):
        generated_text += f"{i}. `{code}`\n"
    
    stats = get_premium_codes_stats()
    
    text = (
        f"✅ *تم توليد {added} كود عشوائي بنجاح!*\n\n"
        f"📋 *الأكواد المولدة:*\n{generated_text}\n"
        f"📊 *إحصائيات الأكواد:*\n"
        f"• إجمالي الأكواد: `{stats['total']}`\n"
        f"• أكواد متاحة: `{stats['single_use_available']}`\n"
        f"• أكواد دائمة: `{stats['permanent']}`\n"
        f"• أكواد لمرة واحدة: `{stats['single_use_total']}`\n"
        f"• أكواد مستخدمة: `{stats['single_use_used']}`"
    )
    
    if added > 20:
        filename = f"premium_codes_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("الأكواد العشوائية المولدة:\n")
            f.write("=" * 50 + "\n")
            f.write(f"التاريخ: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"عدد الأكواد: {added}\n")
            f.write("=" * 50 + "\n\n")
            for i, code in enumerate(new_codes, 1):
                f.write(f"{i}. {code}\n")
        
        with open(filename, "rb") as f:
            bot.send_document(chat_id, f, caption=text[:200])
        os.remove(filename)
        
        bot.edit_message_text(
            f"✅ *تم توليد {added} كود عشوائي*\n📁 تم إرسال الأكواد في ملف مرفق.",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
    else:
        bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )


@bot.callback_query_handler(func=lambda call: call.data == "generate_custom_codes")
def handle_generate_custom_codes(call):
    chat_id = call.message.chat.id
    
    bot.edit_message_text(
        "✏️ *توليد عدد مخصص من الأكواد*\n\n"
        "📝 *أدخل عدد الأكواد التي تريد توليدها:*\n"
        "• أقل عدد: `1`\n"
        "• أكبر عدد: `100`\n\n"
        "🔐 *تنسيق الكود:* `abm_xxxxxx`",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )
    bot.register_next_step_handler(call.message, process_custom_generation)


def process_custom_generation(message):
    chat_id = message.chat.id
    
    try:
        num_codes = int(message.text.strip())
        if num_codes < 1 or num_codes > 100:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "❌ *الرجاء إدخال رقم بين 1 و 100.*", 
                    parse_mode="Markdown", reply_markup=get_back_button())
        return
    
    loading_msg = bot.reply_to(message, "⏳ *جاري توليد الأكواد...*", parse_mode="Markdown")
    
    new_codes = generate_multiple_codes(num_codes, "abm_")
    added = add_multiple_premium_codes(new_codes, "single_use", message.from_user.id)
    
    generated_text = ""
    for i, code in enumerate(new_codes, 1):
        generated_text += f"{i}. `{code}`\n"
    
    stats = get_premium_codes_stats()
    
    text = (
        f"✅ *تم توليد {added} كود عشوائي بنجاح!*\n\n"
        f"📋 *الأكواد المولدة:*\n{generated_text}\n"
        f"📊 *إحصائيات الأكواد:*\n"
        f"• إجمالي الأكواد: `{stats['total']}`\n"
        f"• أكواد متاحة: `{stats['single_use_available']}`"
    )
    
    bot.delete_message(chat_id, loading_msg.message_id)
    
    if added > 20:
        filename = f"premium_codes_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for i, code in enumerate(new_codes, 1):
                f.write(f"{i}. {code}\n")
        
        with open(filename, "rb") as f:
            bot.send_document(chat_id, f, caption=text[:300])
        os.remove(filename)
        
        bot.send_message(
            chat_id,
            f"✅ *تم توليد {added} كود عشوائي*\n📁 تم إرسال الأكواد في ملف مرفق.",
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
    else:
        bot.reply_to(message, text, parse_mode="Markdown", reply_markup=get_back_button())


@bot.callback_query_handler(func=lambda call: call.data == "manual_single_code")
def handle_manual_single_code(call):
    chat_id = call.message.chat.id
    
    bot.edit_message_text(
        "✍️ *إضافة كود لمرة واحدة يدوياً*\n\n"
        "أدخل الكود الذي تريد إضافته (سيتم استخدامه مرة واحدة فقط):\n"
        "مثال: `SINGLE-ABC-123`",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )
    bot.register_next_step_handler(call.message, process_manual_single_code)


def process_manual_single_code(message):
    chat_id = message.chat.id
    code = message.text.strip()
    
    if not code:
        bot.reply_to(message, "❌ الكود لا يمكن أن يكون فارغاً.", reply_markup=get_back_button())
        return
    
    codes = load_premium_codes()
    if code in codes:
        bot.reply_to(message, f"❌ *الكود `{code}` موجود بالفعل.*", parse_mode="Markdown", reply_markup=get_back_button())
        return
    
    add_premium_code(code, "single_use", message.from_user.id)
    
    bot.reply_to(
        message,
        f"✅ *تم إضافة الكود لمرة واحدة:*\n`{code}`",
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )


# ================== حذف كود (بإدخال الكود مباشرة فقط) ==================
@bot.callback_query_handler(func=lambda call: call.data == "delete_premium_code")
def handle_delete_premium_code(call):
    chat_id = call.message.chat.id
    
    bot.edit_message_text(
        "✍️ *حذف كود مميز*\n\n"
        "📝 *أدخل الكود الذي تريد حذفه:*\n\n"
        "مثال: `abm_a3b4c5` أو `PERM-ABC-123`\n\n"
        "⚠️ *ملاحظة:* يمكنك إدخال كود واحد فقط في كل مرة",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )
    bot.register_next_step_handler(call.message, process_delete_premium_code_by_id)


def process_delete_premium_code_by_id(message):
    chat_id = message.chat.id
    code_input = message.text.strip()
    
    if not code_input:
        bot.reply_to(message, "❌ *الرجاء إدخال كود صالح.*", 
                    parse_mode="Markdown", reply_markup=get_back_button())
        return
    
    codes = load_premium_codes()
    
    if code_input not in codes:
        # عرض إحصائيات بسيطة بدلاً من القائمة
        stats = get_premium_codes_stats()
        response = (
            f"❌ *الكود `{code_input}` غير موجود.*\n\n"
            f"📊 *إحصائيات الأكواد الحالية:*\n"
            f"• إجمالي الأكواد: `{stats['total']}`\n"
            f"• أكواد دائمة: `{stats['permanent']}`\n"
            f"• أكواد لمرة واحدة: `{stats['single_use_total']}`\n"
            f"• أكواد متاحة: `{stats['single_use_available']}`\n"
            f"• أكواد مستخدمة: `{stats['single_use_used']}`\n\n"
            f"💡 *تلميح:* استخدم زر '📋 عرض جميع الأكواد' لرؤية الأكواد الموجودة"
        )
        bot.reply_to(message, response, parse_mode="Markdown", reply_markup=get_back_button())
        return
    
    code_data = codes[code_input]
    code_type = "دائم" if code_data.get("type") == "permanent" else "لمرة واحدة"
    is_used = code_data.get("used", False) if code_data.get("type") == "single_use" else False
    created_at = time.strftime('%Y-%m-%d %H:%M', time.localtime(code_data.get("created_at", time.time())))
    
    # تأكيد الحذف
    keyboard = types.InlineKeyboardMarkup()
    btn_confirm = types.InlineKeyboardButton("✅ نعم، احذف", callback_data=f"confirm_delete_code_{code_input}")
    btn_cancel = types.InlineKeyboardButton("❌ إلغاء", callback_data="manage_premium_codes")
    keyboard.add(btn_confirm, btn_cancel)
    
    status_text = " (مستخدم)" if is_used else ""
    
    bot.reply_to(
        message,
        f"⚠️ *تأكيد حذف الكود*\n\n"
        f"📌 الكود: `{code_input}`\n"
        f"📝 النوع: {code_type}{status_text}\n"
        f"📅 تاريخ الإنشاء: {created_at}\n"
        f"👤 تم الإنشاء بواسطة: `{code_data.get('created_by', 'غير معروف')}`\n\n"
        f"هل أنت متأكد من حذف هذا الكود؟",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_delete_code_"))
def handle_delete_premium_code_execute(call):
    chat_id = call.message.chat.id
    code = call.data.replace("confirm_delete_code_", "")
    
    if delete_premium_code(code):
        bot.answer_callback_query(call.id, f"✅ تم حذف الكود {code}")
        
        stats = get_premium_codes_stats()
        
        bot.edit_message_text(
            f"✅ *تم حذف الكود بنجاح*\n\n"
            f"📌 الكود: `{code}`\n\n"
            f"📊 *الإحصائيات بعد الحذف:*\n"
            f"• إجمالي الأكواد: `{stats['total']}`\n"
            f"• أكواد دائمة: `{stats['permanent']}`\n"
            f"• أكواد لمرة واحدة: `{stats['single_use_total']}`\n"
            f"• أكواد متاحة: `{stats['single_use_available']}`",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
    else:
        bot.answer_callback_query(call.id, "❌ فشل حذف الكود")


# ================== حذف جميع الأكواد ==================
@bot.callback_query_handler(func=lambda call: call.data == "delete_all_codes")
def handle_delete_all_codes(call):
    chat_id = call.message.chat.id
    stats = get_premium_codes_stats()
    
    if stats['total'] == 0:
        bot.edit_message_text(
            "📭 *لا توجد أكواد مميزة لحذفها.*",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        return
    
    # تأكيد الحذف
    keyboard = types.InlineKeyboardMarkup()
    btn_confirm = types.InlineKeyboardButton("⚠️ نعم، احذف الكل", callback_data="confirm_delete_all_codes")
    btn_cancel = types.InlineKeyboardButton("❌ إلغاء", callback_data="manage_premium_codes")
    keyboard.add(btn_confirm, btn_cancel)
    
    bot.edit_message_text(
        f"⚠️ *تحذير: حذف جميع الأكواد*\n\n"
        f"📊 *سيتم حذف:*\n"
        f"• إجمالي الأكواد: `{stats['total']}`\n"
        f"• أكواد دائمة: `{stats['permanent']}`\n"
        f"• أكواد لمرة واحدة: `{stats['single_use_total']}`\n"
        f"  - متاحة: `{stats['single_use_available']}`\n"
        f"  - مستخدمة: `{stats['single_use_used']}`\n\n"
        f"❗ *هذا الإجراء لا يمكن التراجع عنه!*\n\n"
        f"هل أنت متأكد من حذف جميع الأكواد؟",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data == "confirm_delete_all_codes")
def handle_confirm_delete_all_codes(call):
    chat_id = call.message.chat.id
    
    count = delete_all_premium_codes()
    
    bot.answer_callback_query(call.id, f"✅ تم حذف {count} كود")
    
    bot.edit_message_text(
        f"✅ *تم حذف جميع الأكواد بنجاح*\n\n"
        f"📊 *تم حذف {count} كود*\n"
        f"🗑️ جميع الأكواد المميزة تم مسحها بالكامل.",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )


# ================== عرض جميع الأكواد ==================
@bot.callback_query_handler(func=lambda call: call.data == "list_all_premium_codes")
def handle_list_all_premium_codes(call):
    chat_id = call.message.chat.id
    codes = load_premium_codes()
    
    if not codes:
        bot.edit_message_text(
            "📭 *لا توجد أكواد مميزة حالياً.*",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        return
    
    text = "👑 *قائمة جميع الأكواد المميزة:*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    permanent_text = ""
    single_unused_text = ""
    single_used_text = ""
    
    for code, data in codes.items():
        created_at = time.strftime('%Y-%m-%d', time.localtime(data.get("created_at", time.time())))
        
        if data.get("type") == "permanent":
            permanent_text += f"• `{code}` (دائم - أنشئ: {created_at})\n"
        elif data.get("type") == "single_use":
            if data.get("used", False):
                used_by = data.get("used_by", "غير معروف")
                used_at = time.strftime('%Y-%m-%d', time.localtime(data.get("used_at", time.time())))
                single_used_text += f"• `{code}` (مستخدم - بواسطة: `{used_by}` - في: {used_at})\n"
            else:
                single_unused_text += f"• `{code}` (لم يستخدم - أنشئ: {created_at})\n"
    
    if permanent_text:
        text += f"✅ *الأكواد الدائمة:*\n{permanent_text}\n"
    if single_unused_text:
        text += f"🔄 *أكواد لمرة واحدة (متاحة):*\n{single_unused_text}\n"
    if single_used_text:
        text += f"❌ *أكواد لمرة واحدة (مستخدمة):*\n{single_used_text}\n"
    
    if len(text) > 3000:
        filename = f"premium_codes_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        with open(filename, "rb") as f:
            bot.send_document(chat_id, f, caption="📋 قائمة الأكواد المميزة")
        os.remove(filename)
        bot.edit_message_text(
            "✅ *تم إرسال قائمة الأكواد في ملف.*",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
    else:
        bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )


# ================== إضافة مستخدم مميز ==================
@bot.callback_query_handler(func=lambda call: call.data == "add_premium_user")
def handle_add_premium_user(call):
    chat_id = call.message.chat.id
    
    bot.edit_message_text(
        "👤 *إضافة مستخدم مميز يدوياً*\n\n"
        "📝 *أدخل ID المستخدم الذي تريد إضافته إلى قائمة المميزين:*\n\n"
        "مثال: `123456789`\n\n"
        "📌 *ملاحظة:* المستخدم سيكون مميزاً حتى لو تم إيقاف البوت",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )
    bot.register_next_step_handler(call.message, process_add_premium_user)


def process_add_premium_user(message):
    chat_id = message.chat.id
    user_id_input = message.text.strip()
    
    if not user_id_input.isdigit():
        bot.reply_to(message, "❌ *الرجاء إدخال ID صالح (أرقام فقط).*", 
                    parse_mode="Markdown", reply_markup=get_back_button())
        return
    
    try:
        bot.send_chat_action(int(user_id_input), 'typing')
        user_exists = True
    except:
        user_exists = False
    
    success, msg = add_premium_user_directly(user_id_input, message.from_user.id, "تمت الإضافة يدوياً بواسطة الأدمن")
    
    if success:
        response = f"✅ *{msg}*\n\n👤 المستخدم: `{user_id_input}`"
        if not user_exists:
            response += f"\n\n⚠️ *ملاحظة:* يبدو أن المستخدم لم يبدأ البوت بعد أو قام بحظره"
        
        try:
            bot.send_message(
                int(user_id_input),
                "🎉 *تهانينا!*\n\n"
                "📌 *تمت إضافتك إلى قائمة المستخدمين المميزين في البوت.*\n\n"
                "✨ *المميزات:*\n"
                "• يمكنك استخدام البوت حتى في أوقات الصيانة\n"
                "• أولوية في الدعم\n"
                "• ميزات حصرية أخرى\n\n"
                "شكراً لاستخدامك البوت! 🤖",
                parse_mode="Markdown"
            )
        except:
            pass
    else:
        response = f"❌ *{msg}*"
    
    bot.reply_to(message, response, parse_mode="Markdown", reply_markup=get_back_button())


# ================== حذف مستخدم مميز (بإدخال ID فقط) ==================
@bot.callback_query_handler(func=lambda call: call.data == "remove_premium_user")
def handle_remove_premium_user(call):
    chat_id = call.message.chat.id
    
    bot.edit_message_text(
        "✍️ *حذف مستخدم مميز*\n\n"
        "📝 *أدخل ID المستخدم الذي تريد حذفه من قائمة المميزين:*\n\n"
        "مثال: `123456789`\n\n"
        "⚠️ *ملاحظة:* يمكنك إدخال ID واحد فقط في كل مرة",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )
    bot.register_next_step_handler(call.message, process_remove_premium_user_by_id)


def process_remove_premium_user_by_id(message):
    chat_id = message.chat.id
    user_id_input = message.text.strip()
    
    if not user_id_input.isdigit():
        bot.reply_to(message, "❌ *الرجاء إدخال ID صالح (أرقام فقط).*", 
                    parse_mode="Markdown", reply_markup=get_back_button())
        return
    
    users = load_user_premium()
    
    if user_id_input not in users:
        users_count = len(users)
        response = (
            f"❌ *المستخدم `{user_id_input}` غير موجود في قائمة المميزين.*\n\n"
            f"📊 *إحصائيات المستخدمين المميزين:*\n"
            f"• إجمالي المستخدمين: `{users_count}`\n\n"
            f"💡 *تلميح:* استخدم زر '👥 عرض المستخدمين المميزين' لرؤية المستخدمين الموجودين"
        )
        bot.reply_to(message, response, parse_mode="Markdown", reply_markup=get_back_button())
        return
    
    # تأكيد الحذف
    keyboard = types.InlineKeyboardMarkup()
    btn_confirm = types.InlineKeyboardButton("✅ نعم، احذف", callback_data=f"confirm_remove_id_{user_id_input}")
    btn_cancel = types.InlineKeyboardButton("❌ إلغاء", callback_data="manage_premium_codes")
    keyboard.add(btn_confirm, btn_cancel)
    
    user_data = users[user_id_input]
    activated_at = time.strftime('%Y-%m-%d %H:%M', time.localtime(user_data.get("activated_at", time.time())))
    
    bot.reply_to(
        message,
        f"⚠️ *تأكيد حذف مستخدم مميز*\n\n"
        f"👤 المستخدم: `{user_id_input}`\n"
        f"📅 تم التفعيل: {activated_at}\n"
        f"✨ طريقة التفعيل: {'يدوي' if user_data.get('type') == 'manual' else 'كود تفعيل'}\n\n"
        f"هل أنت متأكد من حذف هذا المستخدم من قائمة المميزين؟",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_remove_id_"))
def handle_remove_premium_user_execute(call):
    chat_id = call.message.chat.id
    user_id = call.data.replace("confirm_remove_id_", "")
    
    success, msg = remove_premium_user(user_id)
    
    if success:
        bot.answer_callback_query(call.id, f"✅ تم حذف المستخدم {user_id}")
        
        try:
            bot.send_message(
                int(user_id),
                "📌 *تم إلغاء اشتراكك المميز في البوت.*\n\n"
                "🔹 إذا كان هناك خطأ، يرجى التواصل مع الأدمن.\n"
                "🔹 يمكنك استخدام كود تفعيل جديد للعودة إلى القائمة المميزة.",
                parse_mode="Markdown"
            )
        except:
            pass
        
        users_count = len(load_user_premium())
        
        bot.edit_message_text(
            f"✅ *{msg}*\n\n"
            f"👤 المستخدم: `{user_id}`\n\n"
            f"📊 *المستخدمين المتبقين:* `{users_count}`",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
    else:
        bot.answer_callback_query(call.id, f"❌ {msg}")


# ================== عرض المستخدمين المميزين ==================
@bot.callback_query_handler(func=lambda call: call.data == "list_premium_users")
def handle_list_premium_users(call):
    chat_id = call.message.chat.id
    users_details = get_premium_users_details()
    
    if not users_details:
        bot.edit_message_text(
            "👥 *لا توجد مستخدمين مميزين حالياً.*",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        return
    
    text = "👑 *المستخدمون المميزون:*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, user in enumerate(users_details, 1):
        activated_at = time.strftime('%Y-%m-%d %H:%M', time.localtime(user["activated_at"]))
        
        text += f"{i}. 👤 **المستخدم:** `{user['user_id']}`\n"
        text += f"   📅 **تاريخ التفعيل:** {activated_at}\n"
        
        if user['type'] == 'manual':
            text += f"   ✨ **طريقة التفعيل:** إضافة يدوية\n"
            text += f"   👤 **تم بواسطة:** {user['activated_by']}\n"
            text += f"   📝 **السبب:** {user['reason']}\n"
        else:
            text += f"   🔑 **الكود المستخدم:** `{user['code']}`\n"
            text += f"   ✨ **طريقة التفعيل:** كود تفعيل\n"
        
        text += "\n"
    
    text += f"📊 **الإجمالي:** {len(users_details)} مستخدم مميز"
    
    if len(text) > 3000:
        filename = f"premium_users_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        with open(filename, "rb") as f:
            bot.send_document(chat_id, f, caption="👥 قائمة المستخدمين المميزين")
        os.remove(filename)
        bot.edit_message_text(
            "✅ *تم إرسال قائمة المستخدمين المميزين في ملف.*",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
    else:
        bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )


# ================== دالة مساعدة للرجوع ==================
def get_back_button():
    keyboard = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton("🔙 رجوع إلى إدارة المميزين", callback_data="manage_premium_codes")
    keyboard.add(btn_back)
    return keyboard
        
@bot.callback_query_handler(
    func=lambda call: not call.data.startswith("grade_") and call.data not in [
        "enter_cgpa", "cancel_cgpa", "send_user1", "toggle_notifications",
        "try_login", "toggle_", "download_student_image", "broadcast_new",
        "broadcast_forward", "check_subscription", "download_student_image2",
        "download_student_data", "no_password_result", "manage_banned_codes",
        "add_banned_code", "delete_banned_code", "view_banned_codes",
        "manage_student_codes", "view_user_code", "reset_user_code",
        "view_all_codes", "manage_access_codes", "add_access_code",
        "delete_access_code", "generate_access_codes", "generate_5_codes",
        "generate_10_codes", "generate_custom_codes", "clear_all_codes",
        "confirm_clear_all", "access_codes_stats", "view_access_codes",
        "manage_whitelist", "add_whitelist", "remove_whitelist",
        "view_whitelist", "ranking", "free_result",
        # أزرار نظام الكوكيز
        "manage_cookies_accounts", "add_cookie_account", "remove_cookie_account",
        "list_cookie_accounts", "cookies_toggle_auto_refresh", "refresh_cookies_now",
        "show_current_cookie", "del_cookie_acc_",
        # أزرار نظام الترتيب المتكامل
        "student_ranking_query", "ranking_admin", "ranking_upload_file", 
        "ranking_manage_files", "rf_", "rn_", "del_", "vw_", "dn_", "cf_",
        # أزرار الاستعلام الشامل للمستخدم
        "search_all_files", "show_colleges", "col_", "lev_", "all_",
        # أزرار نظام جلب IDs
        "admin_upload_ids", "start_ranking_process",
        # ✅ الأزرار الجديدة لإدارة البوت والأكواد
        "toggle_bot", "manage_premium_codes", "add_permanent_code", "add_single_code",
        "generate_random_code", "manual_single_code", "delete_premium_code",
        "list_all_premium_codes", "list_premium_users",

       
    ]
)
def callback_query(call):
    handle_callback_query(call)


def handle_callback_query(call):
    chat_id = call.message.chat.id
    button_status = load_user_buttons()
    subscription_required = button_status.get("subscription_required", True)

    if subscription_required and not is_user_subscribed(chat_id):
        bot.answer_callback_query(
            call.id,
            "❌ يجب عليك الاشتراك في القناة لاستخدام هذا الزر.",
            show_alert=True
        )
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        send_subscription_message(chat_id)
        return

    # ===== أوامر الأدمن =====
    admin_commands = ["ban_user", "unban_user", "stats", "broadcast"]
    if call.data in admin_commands:
        if str(chat_id) != str(admin_chat_id):
            bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية لاستخدام هذه الأوامر.")
            return

        if call.data == "ban_user":
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text="• *أرسل ID المستخدم الذي تريد حظره:*",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )
            bot.register_next_step_handler(call.message, process_ban)

        elif call.data == "unban_user":
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text="• *أرسل ID المستخدم الذي تريد فك الحظر عنه:*",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )
            bot.register_next_step_handler(call.message, process_unban)

        elif call.data == "stats":
            stats(call.message)

        elif call.data == "broadcast":
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text="✉️ *أرسل الرسالة التي تريد إذاعتها لجميع المستخدمين:*",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )
            bot.register_next_step_handler(call.message, process_broadcast_media)

        return

    # ===== التحقق من الحظر =====
    try:
        with open("ban.txt", "r") as file:
            banned_users = file.read().splitlines()
    except FileNotFoundError:
        banned_users = []

    if str(chat_id) in banned_users:
        bot.answer_callback_query(call.id, "🚫 أنت محظور من استخدام هذا البوت.", show_alert=True)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="🚫 *تم حظرك من استخدام هذا البوت.*\n🔹 إذا كنت تعتقد أن هناك خطأ، يرجى التواصل مع المطور.",
            parse_mode="Markdown",
            reply_markup=keyboard3
        )
        return

    # ===== الأزرار =====
    if call.data == "echo_all":
        bot.clear_step_handler(call.message)
        echo_all(call.message)

    elif call.data == "graduates_result":
        bot.clear_step_handler(call.message)
        request_graduate_result(call)
        


    elif call.data == "back":
        bot.clear_step_handler(call.message)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=(
                "✨ *ماذا يمكنني فعله؟*\n"
                "• 📊 جلب نتائجك بسرعة وسهولة.\n"
                "• 🔑 استعادة أو تغيير كلمة مرور ابن الهيثم.\n"
                "• 🎓 حساب معدلك التراكمي (GPA).\n"
                "• 📷 تحميل صورة الطالب وبياناته.\n\n"
                "🚀 *ابدأ الآن!* استخدم الأزرار أدناه.\n"
                "💬 *للاستفسارات أو المشاكل:* [اضغط هنا](https://102706971050467064406.sarhne.com)"
            ),
            parse_mode="Markdown",
            disable_web_page_preview=True,
        reply_markup=get_user_keyboard(chat_id)
        )

    elif call.data == "send_password":
        bot.clear_step_handler(call.message)
        send_password(call)

    elif call.data == "change_password":
        bot.clear_step_handler(call.message)
        change_password_step1(call)

    elif call.data == "calculate_gpa":
        bot.clear_step_handler(call.message)
        request_course_count(call)

    elif call.data == "target_gpa":
        bot.clear_step_handler(call.message)
        request_target_gpa(call)

#____%+&_-++(((+(((())))))))
@bot.callback_query_handler(func=lambda call: call.data in ["manage_access_codes", "add_access_code", "delete_access_code", "generate_access_codes", "generate_5_codes", "generate_10_codes", "generate_custom_codes", "clear_all_codes", "confirm_clear_all", "access_codes_stats", "view_access_codes"])
def handle_all_access_code_operations(call):
    chat_id = call.message.chat.id
    
    # التحقق من صلاحية الأدمن
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية.")
        return
    
    if call.data == "manage_access_codes":
        handle_manage_access_codes(call)
    elif call.data == "add_access_code":
        bot.edit_message_text("✍️ *أدخل الكود الجديد لإضافته:*\n\n"
                             "📝 *ملاحظة:* الكود الذي تدخله يدوياً سيكون صالحاً دائماً ✅", 
                             chat_id=chat_id, message_id=call.message.message_id, 
                             parse_mode="Markdown", reply_markup=get_back_button1())
        bot.register_next_step_handler(call.message, process_add_code1)
    elif call.data == "delete_access_code":
        bot.edit_message_text("✍️ *أدخل الكود المراد حذفه:*", 
                             chat_id=chat_id, message_id=call.message.message_id, 
                             parse_mode="Markdown", reply_markup=get_back_button1())
        bot.register_next_step_handler(call.message, process_delete_code1)
    elif call.data == "generate_access_codes":
        handle_generate_access_codes(call)
    elif call.data in ["generate_5_codes", "generate_10_codes"]:
        handle_generate_fixed_codes(call)
    elif call.data == "generate_custom_codes":
        handle_generate_custom_codes(call)
    elif call.data == "clear_all_codes":
        handle_clear_all_codes(call)
    elif call.data == "confirm_clear_all":
        handle_confirm_clear_all(call)
    elif call.data == "access_codes_stats":
        handle_access_codes_stats(call)
    elif call.data == "view_access_codes":
        handle_view_access_codes(call)

# ================= ملفات التخزين المعدلة =================
# ================= ملفات التخزين المعدلة =================
ACCESS_CODES_FILE = "access_codes.json"

def load_access_codes():
    """تحميل الأكواد مع معلومات الاستخدام"""
    try:
        with open(ACCESS_CODES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            
            # إذا كان الملف قديماً (قائمة فقط)، قم بتحويله إلى التنسيق الجديد
            if isinstance(data, list):
                new_data = {}
                for code in data:
                    if isinstance(code, str):
                        new_data[code] = {
                            "used": False, 
                            "used_by": None, 
                            "created_at": time.time(),
                            "created_by": "system",
                            "type": "manual",  # الكود اليدوي صالح دائماً
                            "single_use": False  # غير لمرة واحدة - كود دائم
                        }
                save_access_codes(new_data)
                return new_data
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_access_codes(codes):
    """حفظ الأكواد مع معلومات الاستخدام"""
    with open(ACCESS_CODES_FILE, "w", encoding="utf-8") as file:
        json.dump(codes, file, indent=4, ensure_ascii=False)

def is_valid_access_code(code):
    """التحقق من صلاحية الكود"""
    codes = load_access_codes()
    
    if code in codes:
        code_data = codes[code]
        
        # إذا كان الكود دائم (يدوي) - صالح دائماً
        if not code_data.get("single_use", True):
            return True
        
        # إذا كان الكود لمرة واحدة - تحقق إذا تم استخدامه
        if code_data.get("single_use", False):
            return not code_data.get("used", False)
    
    return False

def get_code_type(code):
    """الحصول على نوع الكود"""
    codes = load_access_codes()
    if code in codes:
        if codes[code].get("single_use", True):
            return "single_use"
        else:
            return "permanent"
    return None

def mark_code_as_used(code, user_id):
    """تحديث حالة الكود إذا كان لمرة واحدة فقط"""
    codes = load_access_codes()
    if code in codes:
        code_data = codes[code]
        
        # تحديث فقط إذا كان كود مرة واحدة ولم يتم استخدامه
        if code_data.get("single_use", False) and not code_data.get("used", False):
            code_data["used"] = True
            code_data["used_by"] = str(user_id)
            code_data["used_at"] = time.time()
            save_access_codes(codes)
            return True
    
    return False

def get_unused_codes_count():
    """عدد الأكواد المتاحة (غير المستخدمة)"""
    codes = load_access_codes()
    count = 0
    for code, data in codes.items():
        if data.get("single_use", False):
            if not data.get("used", False):
                count += 1
        else:
            # الكود اليدوي يعتبر متاح دائماً
            count += 1
    return count

def get_permanent_codes_count():
    """عدد الأكواد الدائمة (التي أدخلت يدوياً)"""
    codes = load_access_codes()
    return sum(1 for data in codes.values() if not data.get("single_use", True))

def get_single_use_codes_count():
    """عدد الأكواد لمرة واحدة"""
    codes = load_access_codes()
    return sum(1 for data in codes.values() if data.get("single_use", False))

def get_used_single_use_codes_count():
    """عدد الأكواد لمرة واحدة التي تم استخدامها"""
    codes = load_access_codes()
    count = 0
    for data in codes.values():
        if data.get("single_use", False) and data.get("used", False):
            count += 1
    return count

def cleanup_expired_codes():
    """حذف الأكواد لمرة واحدة المستخدمة منذ أكثر من 30 يوم"""
    codes = load_access_codes()
    current_time = time.time()
    month_ago = current_time - (30 * 24 * 60 * 60)
    
    expired_count = 0
    codes_to_delete = []
    
    for code, data in codes.items():
        if isinstance(data, dict):
            if data.get("single_use", False) and data.get("used", False):
                used_at = data.get("used_at", 0)
                if used_at > 0 and used_at < month_ago:
                    codes_to_delete.append(code)
    
    for code in codes_to_delete:
        del codes[code]
        expired_count += 1
    
    if expired_count > 0:
        save_access_codes(codes)
    
    return expired_count

# تشغيل التنظيف مرة واحدة عند بدء البوت
cleanup_expired_codes()

# ================= توليد أكواد لمرة واحدة =================
@bot.callback_query_handler(func=lambda call: call.data == "generate_access_codes")
def handle_generate_access_codes(call):
    chat_id = call.message.chat.id
    
    keyboard = types.InlineKeyboardMarkup()
    btn_5 = types.InlineKeyboardButton("5 أكواد", callback_data="generate_5_codes")
    btn_10 = types.InlineKeyboardButton("10 أكواد", callback_data="generate_10_codes")
    btn_custom = types.InlineKeyboardButton("عدد مخصص", callback_data="generate_custom_codes")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="manage_access_codes")
    
    keyboard.add(btn_5, btn_10)
    keyboard.add(btn_custom)
    keyboard.add(btn_back)
    
    bot.edit_message_text(
        "🎲 *توليد أكواد جديدة لمرة واحدة:*\n\n"
        "🔐 *ملاحظة:* الأكواد المولدة عشوائياً صالحة لمرة واحدة فقط\n\n"
        "اختر عدد الأكواد التي تريد توليدها:",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# ================= توليد 5 أو 10 أكواد لمرة واحدة =================
def handle_generate_fixed_codes(call):
    chat_id = call.message.chat.id
    
    if call.data == "generate_5_codes":
        num_codes = 5
    else:
        num_codes = 10
    
    codes = load_access_codes()
    generated_text = ""
    
    import random
    import string
    
    codes_generated = 0
    
    for _ in range(num_codes):
        # توليد كود عشوائي مكون من 6 أحرف وأرقام (3 أحرف + 3 أرقام)
        letters = ''.join(random.choices(string.ascii_lowercase, k=4))
        digits = ''.join(random.choices(string.digits, k=3))
        new_code = letters + digits
        
        # التأكد من عدم تكرار الكود
        while new_code in codes:
            letters = ''.join(random.choices(string.ascii_uppercase, k=3))
            digits = ''.join(random.choices(string.digits, k=3))
            new_code = letters + digits
        
        # تخزين الكود ككود لمرة واحدة
        codes[new_code] = {
            "used": False,
            "used_by": None,
            "created_at": time.time(),
            "created_by": chat_id,
            "type": "generated",
            "single_use": True  # ✅ كود لمرة واحدة
        }
        
        generated_text += f"• {new_code}\n"
        codes_generated += 1
    
    save_access_codes(codes)
    
    unused_count = get_unused_codes_count()
    permanent_count = get_permanent_codes_count()
    single_use_count = get_single_use_codes_count()
    
    text = f"✅ *تم توليد {codes_generated} اكواد لمرة واحدة:*\n\n"
    text += "```\n"
    text += generated_text
    text += "```\n\n"
    text += f"📊 *إحصائيات الأكواد:*\n"
    text += f"• الإجمالي: {len(codes)} كود\n"
    text += f"• المتاحة للاستخدام: {unused_count} كود\n"
    text += f"• دائمة (يدوية): {permanent_count} كود\n"
    text += f"• لمرة واحدة: {single_use_count} كود"
    
    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard3
    )

# ================= توليد عدد مخصص من الأكواد لمرة واحدة =================
def handle_generate_custom_codes(call):
    chat_id = call.message.chat.id
    
    bot.edit_message_text(
        "✍️ *أدخل عدد الأكواد التي تريد توليدها:*\n"
        "(يجب أن يكون بين 1 و 100)\n\n"
        "🔐 *ملاحظة:*\n"
        "• الأكواد المولدة عشوائياً صالحة لمرة واحدة فقط\n"
        "• ستكون مكونة من 3 أحرف + 3 أرقام (مثال: ABC123)",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button1()
    )
    bot.register_next_step_handler(call.message, process_custom_generation)

def process_custom_generation(message):
    chat_id = message.chat.id
    
    try:
        num_codes = int(message.text.strip())
        if num_codes < 1 or num_codes > 100:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "❌ *الرجاء إدخال رقم بين 1 و 100.*", 
                    parse_mode="Markdown", reply_markup=get_back_button1())
        return
    
    codes = load_access_codes()
    generated_text = ""
    
    import random
    import string
    
    codes_generated = 0
    
    for _ in range(num_codes):
        letters = ''.join(random.choices(string.ascii_lowercase, k=3))
        digits = ''.join(random.choices(string.digits, k=3))
        new_code = letters + digits
        
        while new_code in codes:
            letters = ''.join(random.choices(string.ascii_uppercase, k=3))
            digits = ''.join(random.choices(string.digits, k=3))
            new_code = letters + digits
        
        codes[new_code] = {
            "used": False,
            "used_by": None,
            "created_at": time.time(),
            "created_by": chat_id,
            "type": "generated",
            "single_use": True  # ✅ كود لمرة واحدة
        }
        
        generated_text += f"• {new_code}\n"
        codes_generated += 1
    
    save_access_codes(codes)
    
    unused_count = get_unused_codes_count()
    permanent_count = get_permanent_codes_count()
    single_use_count = get_single_use_codes_count()
    
    text = f"✅ *تم توليد {codes_generated} أكواد لمرة واحدة:*\n\n"
    text += "```\n"
    text += generated_text
    text += "```\n\n"
    text += f"📊 *إحصائيات الأكواد:*\n"
    text += f"• الإجمالي: {len(codes)} كود\n"
    text += f"• المتاحة للاستخدام: {unused_count} كود\n"
    text += f"• دائمة (يدوية): {permanent_count} كود\n"
    text += f"• لمرة واحدة: {single_use_count} كود"
    
    bot.reply_to(message, text, parse_mode="Markdown", reply_markup=get_back_button1())

# ================= معالجة حذف الكود =================
def process_delete_code1(message):
    code = message.text.strip()
    codes = load_access_codes()
    
    if code in codes:
        # الحصول على نوع الكود قبل حذفه
        code_type = "يدوي (دائم)" if not codes[code].get("single_use", True) else "عشوائي (لمرة واحدة)"
        code_status = "مستخدم" if codes[code].get("used", False) else "غير مستخدم"
        
        # حذف الكود
        del codes[code]
        save_access_codes(codes)
        
        # حساب الإحصائيات الجديدة
        unused_count = get_unused_codes_count()
        permanent_count = get_permanent_codes_count()
        single_use_count = get_single_use_codes_count()
        used_count = get_used_single_use_codes_count()
        
        bot.reply_to(message, 
                    f"✅ *تم حذف الكود `{code}` بنجاح.*\n\n"
                    f"📝 *معلومات الكود المحذوف:*\n"
                    f"• النوع: {code_type}\n"
                    f"• الحالة: {code_status}\n\n"
                    f"📊 *إحصائيات الأكواد بعد الحذف:*\n"
                    f"• الإجمالي: {len(codes)} كود\n"
                    f"• المتاحة للاستخدام: {unused_count} كود\n"
                    f"• دائمة (يدوية): {permanent_count} كود\n"
                    f"• لمرة واحدة: {single_use_count} كود\n"
                    f"• مستخدمة: {used_count} كود", 
                    parse_mode="Markdown", 
                    reply_markup=get_back_button1())
    else:
        bot.reply_to(message, 
                    f"⚠️ *الكود `{code}` غير موجود في القائمة.*\n\n"
                    f"📊 *توجد {len(codes)} كود في القائمة.*", 
                    parse_mode="Markdown", 
                    reply_markup=get_back_button1())

# ================= معالجة مسح الكل =================
def handle_clear_all_codes(call):
    chat_id = call.message.chat.id
    
    keyboard = types.InlineKeyboardMarkup()
    btn_confirm = types.InlineKeyboardButton("✅ نعم، مسح الكل", callback_data="confirm_clear_all")
    btn_cancel = types.InlineKeyboardButton("❌ إلغاء", callback_data="manage_access_codes")
    
    keyboard.add(btn_confirm, btn_cancel)
    
    codes = load_access_codes()
    permanent_count = get_permanent_codes_count()
    single_use_count = get_single_use_codes_count()
    
    bot.edit_message_text(
        f"⚠️ *تحذير: مسح جميع الأكواد*\n\n"
        f"📊 *الإحصائيات الحالية:*\n"
        f"• إجمالي الأكواد: {len(codes)}\n"
        f"• دائمة (يدوية): {permanent_count}\n"
        f"• لمرة واحدة: {single_use_count}\n\n"
        f"هل أنت متأكد من أنك تريد مسح جميع أكواد الوصول؟\n"
        f"*هذا الإجراء لا يمكن التراجع عنه!*",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

def handle_confirm_clear_all(call):
    chat_id = call.message.chat.id
    
    save_access_codes({})  # حفظ قائمة فارغة
    
    bot.edit_message_text(
        "✅ *تم مسح جميع أكواد الوصول بنجاح.*",
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button1()
    )

# ================= عرض قائمة الأكواد مع حالتها =================
def handle_manage_access_codes(call):
    chat_id = call.message.chat.id
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية.")
        return

    codes = load_access_codes()
    permanent_count = get_permanent_codes_count()
    single_use_count = get_single_use_codes_count()
    used_single_use_count = get_used_single_use_codes_count()
    unused_count = get_unused_codes_count()
    
    text = "🔑 *نظام أكواد الوصول:*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    text += "📝 *معلومات النظام:*\n"
    text += f"• ✅ *الأكواد اليدوية:* صالحة دائماً\n"
    text += f"• 🔄 *الأكواد العشوائية:* صالحة لمرة واحدة\n\n"
    text += "📊 *إحصائيات الأكواد:*\n"
    text += f"• 📈 *الإجمالي:* `{len(codes)}` كود\n"
    text += f"• ✅ *المتاحة للاستخدام:* `{unused_count}` كود\n"
    text += f"• 🔄 *دائمة (يدوية):* `{permanent_count}` كود\n"
    text += f"• ⏳ *لمرة واحدة:* `{single_use_count}` كود\n"
    text += f"• ❌ *تم استخدامها:* `{used_single_use_count}` كود\n"
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_add = types.InlineKeyboardButton("➕ إضافة كود دائم", callback_data="add_access_code")
    btn_del = types.InlineKeyboardButton("➖ حذف كود", callback_data="delete_access_code")
    btn_generate = types.InlineKeyboardButton("🎲 توليد أكواد عشوائية", callback_data="generate_access_codes")
    btn_clear = types.InlineKeyboardButton("🗑️ مسح الكل", callback_data="clear_all_codes")
    btn_stats = types.InlineKeyboardButton("📊 إحصائيات مفصلة", callback_data="access_codes_stats")
    btn_view = types.InlineKeyboardButton("👁️ عرض جميع الأكواد", callback_data="view_access_codes")
    btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_admin")
    
    keyboard.add(btn_add, btn_del)
    keyboard.add(btn_generate, btn_clear)
    keyboard.add(btn_stats, btn_view)
    keyboard.add(btn_back)

    bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=keyboard)

def handle_view_access_codes(call):
    chat_id = call.message.chat.id
    codes = load_access_codes()
    
    text = "🔑 *قائمة جميع الأكواد وحالتها:*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    if codes:
        permanent_text = ""
        unused_single_use_text = ""
        used_single_use_text = ""
        
        permanent_counter = 0
        unused_single_use_counter = 0
        used_single_use_counter = 0
        
        for code, data in codes.items():
            if not data.get("single_use", True):  # كود دائم (يدوي)
                permanent_counter += 1
                created_at = data.get("created_at", 0)
                if created_at:
                    created_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(created_at))
                else:
                    created_time = "غير معروف"
                    
                if permanent_counter <= 10:
                    permanent_text += f"{permanent_counter:2d}. {code} (أنشئ: {created_time})\n"
                    permanent_text += f"     👤 بواسطة: {data.get('created_by', 'غير معروف')}\n"
            elif data.get("used", False):  # كود لمرة واحدة تم استخدامه
                used_single_use_counter += 1
                used_by = data.get("used_by", "غير معروف")
                used_at = data.get("used_at", 0)
                created_at = data.get("created_at", 0)
                
                if used_at:
                    used_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(used_at))
                else:
                    used_time = "غير معروف"
                    
                if created_at:
                    created_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(created_at))
                else:
                    created_time = "غير معروف"
                    
                if used_single_use_counter <= 5:
                    used_single_use_text += f"{used_single_use_counter:2d}. {code}\n"
                    used_single_use_text += f"     📅 أنشئ: {created_time}\n"
                    used_single_use_text += f"     👤 استخدمه: {used_by}\n"
                    used_single_use_text += f"     ⏰ وقت الاستخدام: {used_time}\n"
            else:  # كود لمرة واحدة لم يستخدم بعد
                unused_single_use_counter += 1
                created_at = data.get("created_at", 0)
                if created_at:
                    created_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(created_at))
                else:
                    created_time = "غير معروف"
                    
                if unused_single_use_counter <= 10:
                    unused_single_use_text += f"{unused_single_use_counter:2d}. {code} (أنشئ: {created_time})\n"
                    unused_single_use_text += f"     👤 بواسطة: {data.get('created_by', 'غير معروف')}\n"
        
        # عرض الأكواد الدائمة
        if permanent_counter > 0:
            text += f"✅ *الأكواد الدائمة ({permanent_counter}):*\n"
            text += "```\n"
            text += permanent_text
            
            if permanent_counter > 10:
                text += f"... +{permanent_counter - 10} أكواد أخرى\n"
            
            text += "```\n\n"
        
        # عرض الأكواد لمرة واحدة المتاحة
        if unused_single_use_counter > 0:
            text += f"🔄 *الأكواد لمرة واحدة المتاحة ({unused_single_use_counter}):*\n"
            text += "```\n"
            text += unused_single_use_text
            
            if unused_single_use_counter > 10:
                text += f"... +{unused_single_use_counter - 10} أكواد أخرى\n"
            
            text += "```\n\n"
        
        # عرض الأكواد لمرة واحدة المستخدمة
        if used_single_use_counter > 0:  # ✅ إصلاح: تغيير used_single_use_count إلى used_single_use_counter
            text += f"❌ *الأكواد لمرة واحدة المستخدمة ({used_single_use_counter}):*\n"  # ✅ إصلاح هنا أيضاً
            text += "```\n"
            text += used_single_use_text
            
            if used_single_use_counter > 5:  # ✅ إصلاح هنا أيضاً
                text += f"... +{used_single_use_counter - 5} أكواد أخرى\n"  # ✅ إصلاح هنا أيضاً
            
            text += "```"
    else:
        text += "📭 *لا توجد أكواد حالياً.*\n"
        text += "يمكنك إضافة أكواد جديدة للمستخدمين."

    bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=get_back_button1())
def handle_access_codes_stats(call):
    chat_id = call.message.chat.id
    codes = load_access_codes()
    
    # حساب الإحصائيات بدقة
    permanent_available = 0
    permanent_total = 0
    single_use_available = 0
    single_use_used = 0
    single_use_total = 0
    
    for code, data in codes.items():
        if isinstance(data, dict):
            if data.get("single_use", True):  # مرة واحدة
                single_use_total += 1
                if data.get("used", False):
                    single_use_used += 1
                else:
                    single_use_available += 1
            else:  # دائم
                permanent_total += 1
                permanent_available += 1  # الدائم دائماً متاح
    
    text = "📊 *إحصائيات مفصلة لأكواد الوصول:*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    text += f"📈 *إجمالي الأكواد:* `{len(codes)}`\n\n"
    
    text += "🔐 *الأكواد الدائمة:*\n"
    text += f"• ✅ *المتاحة دائماً:* `{permanent_available}` كود\n"
    text += f"• 📊 *الإجمالي:* `{permanent_total}` كود\n\n"
    
    text += "🔄 *الأكواد لمرة واحدة:*\n"
    text += f"• ✅ *المتاحة:* `{single_use_available}` كود\n"
    text += f"• ❌ *المستخدمة:* `{single_use_used}` كود\n"
    text += f"• 📊 *الإجمالي:* `{single_use_total}` كود\n\n"
    
    if single_use_total > 0:
        used_percentage = (single_use_used / single_use_total) * 100
        available_percentage = (single_use_available / single_use_total) * 100
        text += f"📊 *النسب المئوية (لمرة واحدة):*\n"
        text += f"• نسبة الاستخدام: `{used_percentage:.1f}%`\n"
        text += f"• نسبة المتاحة: `{available_percentage:.1f}%`\n"
    
    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=call.message.message_id,
        parse_mode="Markdown",
        reply_markup=get_back_button1()
    )

# ================= تعديل دالة إضافة كود يدوياً (دائم) =================
def process_add_code1(message):
    try:
        code = message.text.strip()  # تحويل للأحرف الكبيرة
        
        if not code:
            bot.reply_to(message, "⚠️ *يجب إدخال كود صالح.*", parse_mode="Markdown", reply_markup=get_back_button1())
            return
        
        if len(code) < 3:
            bot.reply_to(message, "⚠️ *الكود يجب أن يكون 3 أحرف على الأقل.*", parse_mode="Markdown", reply_markup=get_back_button1())
            return
        
        codes = {}
        try:
            if os.path.exists(ACCESS_CODES_FILE):
                with open(ACCESS_CODES_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.strip():
                        data = json.loads(content)
                        if isinstance(data, dict):
                            codes = data
                        elif isinstance(data, list):
                            codes = {}
                            for item in data:
                                if isinstance(item, str):
                                    codes[item] = {
                                        "used": False,
                                        "single_use": False,
                                        "created_at": time.time(),
                                        "created_by": "converted"
                                    }
        except Exception as e:
            codes = {}
        
        if code in codes:
            bot.reply_to(message, f"⚠️ *الكود `{code}` موجود بالفعل في القائمة.*", 
                        parse_mode="Markdown", reply_markup=get_back_button1())
            return
        
        # إضافة الكود الجديد ككود دائم
        codes[code] = {
            "used": False,
            "used_by": None,
            "created_at": time.time(),
            "created_by": message.from_user.id,
            "type": "manual",
            "single_use": False  # ✅ كود دائم
        }
        
        with open(ACCESS_CODES_FILE, "w", encoding="utf-8") as f:
            json.dump(codes, f, indent=4, ensure_ascii=False)
        
        # حساب الإحصائيات المباشرة
        permanent_count = 0
        single_use_count = 0
        used_count = 0
        
        for code_item, data in codes.items():
            if isinstance(data, dict):
                if data.get("single_use", False):
                    single_use_count += 1
                    if data.get("used", False):
                        used_count += 1
                else:
                    permanent_count += 1
        
        total_codes = len(codes)
        available_codes = permanent_count + (single_use_count - used_count)
        
        response = (f"✅ *تم إضافة الكود `{code}` بنجاح.*\n\n"
                   f"📝 *نوع الكود:* يدوي (دائم) ✅\n"
                   f"⏰ *صلاحية الكود:* صالح دائماً\n\n"
                   f"📊 *إحصائيات الأكواد:*\n"
                   f"• الإجمالي: {total_codes} كود\n"
                   f"• المتاحة للاستخدام: {available_codes} كود\n"
                   f"• دائمة (يدوية): {permanent_count} كود\n"
                   f"• لمرة واحدة: {single_use_count} كود")
        
        bot.reply_to(message, response, parse_mode="Markdown", reply_markup=get_back_button1())
        
    except Exception as e:
        bot.reply_to(message, f"❌ *حدث خطأ:* `{str(e)[:100]}`", 
                    parse_mode="Markdown", reply_markup=get_back_button1())

# ================= دالة زر الرجوع =================
def get_back_button1():
    """زر للرجوع إلى القائمة الرئيسية للأكواد"""
    keyboard = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton("🔙 رجوع إلى إدارة الأكواد", callback_data="manage_access_codes")
    keyboard.add(btn_back)
    return keyboard


 #___&__&&&&&&_______
 # 🔐 أوامر إدارة أكواد الطلاب
@bot.callback_query_handler(func=lambda call: call.data in ["manage_student_codes", "view_user_code", "reset_user_code", "view_all_codes"])
def handle_manage_student_codes(call):
    chat_id = call.message.chat.id
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية.")
        return

    if call.data == "manage_student_codes":
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        btn_view = types.InlineKeyboardButton("👁️ عرض كود مستخدم", callback_data="view_user_code")
        btn_reset = types.InlineKeyboardButton("🔄 إعادة تعيين كود", callback_data="reset_user_code")
        btn_all = types.InlineKeyboardButton("📋 عرض جميع الأكواد", callback_data="view_all_codes")
        btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_admin")
        keyboard.add(btn_view, btn_reset)
        keyboard.add(btn_all)
        keyboard.add(btn_back)

        bot.edit_message_text(
            "🔐 *إدارة أكواد الطلاب:*\n\n"
            "• يمكنك عرض كود مستخدم معين\n"
            "• إعادة تعيين كود مستخدم\n"
            "• عرض جميع الأكواد المسجلة",
            chat_id=chat_id, 
            message_id=call.message.message_id, 
            parse_mode="Markdown", 
            reply_markup=keyboard
        )

    elif call.data == "view_user_code":
        bot.edit_message_text(
            "✍️ *أدخل معرف المستخدم (ID) لعرض كود الطالب المسجل له:*",
            chat_id=chat_id, 
            message_id=call.message.message_id, 
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        bot.register_next_step_handler(call.message, process_view_user_code)

    elif call.data == "reset_user_code":
        bot.edit_message_text(
            "✍️ *أدخل معرف المستخدم (ID) لإعادة تعيين كود الطالب المسجل له:*",
            chat_id=chat_id, 
            message_id=call.message.message_id, 
            parse_mode="Markdown",
            reply_markup=get_back_button()
        )
        bot.register_next_step_handler(call.message, process_reset_user_code)

    elif call.data == "view_all_codes":
        codes = load_student_codes()
        if not codes:
            bot.edit_message_text(
                "📭 *لا توجد أكواد مسجلة حاليًا.*",
                chat_id=chat_id, 
                message_id=call.message.message_id, 
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )
            return
        
        # إذا كان عدد الأكواد كبيراً، نرسلها كمستند نصي
        if len(codes) > 30:
            # إنشاء ملف نصي مؤقت
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False, encoding='utf-8') as tmp:
                tmp.write("📋 جميع الأكواد المسجلة للطلاب:\n\n")
                for user_id, student_code in codes.items():
                    tmp.write(f"المستخدم: {user_id} → الكود: {student_code}\n")
                tmp_path = tmp.name
            
            # إرسال الملف
            with open(tmp_path, 'rb') as doc:
                bot.send_document(
                    chat_id,
                    doc,
                    caption=f"📊 *إجمالي الأكواد:* {len(codes)}\n"
                            "🔍 يمكنك فتح الملف لعرض جميع الأكواد.",
                    parse_mode="Markdown"
                )
            
            # حذف الملف المؤقت
            os.unlink(tmp_path)
            
            bot.edit_message_text(
                "✅ *تم إرسال جميع الأكواد في ملف نصي.*\n"
                "📁 يمكنك تحميله وعرضه على جهازك.",
                chat_id=chat_id,
                message_id=call.message.message_id,
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )
        else:
            # إذا كان عدد الأكواد قليلاً، نعرضها مباشرة في الرسالة
            text = "📋 *جميع الأكواد المسجلة:*\n\n"
            for index, (user_id, student_code) in enumerate(codes.items(), 1):
                text += f"{index}. المستخدم: `{user_id}` → الكود: `{student_code}`\n"
            
            # إضافة إجمالي العدد
            text += f"\n📊 *الإجمالي:* {len(codes)} كود"
            
            bot.edit_message_text(
                text,
                chat_id=chat_id, 
                message_id=call.message.message_id, 
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )

def process_view_user_code(message):
    user_id = message.text.strip()
    student_code = get_user_student_code(user_id)
    
    if student_code:
        bot.reply_to(message, f"📋 *كود الطالب المسجل للمستخدم* `{user_id}`:\n\n`{student_code}`", 
                    parse_mode="Markdown", reply_markup=get_back_button())
    else:
        bot.reply_to(message, f"❌ *لا يوجد كود مسجل للمستخدم* `{user_id}`", 
                    parse_mode="Markdown", reply_markup=get_back_button())

def process_reset_user_code(message):
    user_id = message.text.strip()
    codes = load_student_codes()
    
    if user_id in codes:
        del codes[user_id]
        save_student_codes(codes)
        bot.reply_to(message, f"✅ *تم إعادة تعيين كود الطالب للمستخدم* `{user_id}`", 
                    parse_mode="Markdown", reply_markup=get_back_button())
    else:
        bot.reply_to(message, f"❌ *لا يوجد كود مسجل للمستخدم* `{user_id}`", 
                    parse_mode="Markdown", reply_markup=get_back_button())
                    
def process_add_code(message):
    code = message.text.strip()
    
    # التحقق من صحة الكود
    if not code:
        bot.reply_to(message, "⚠️ *يجب إدخال كود صالح.*", parse_mode="Markdown", reply_markup=get_back_button())
        return
    
    if len(code) < 3:
        bot.reply_to(message, "⚠️ *الكود يجب أن يكون 4 أحرف على الأقل.*", parse_mode="Markdown", reply_markup=get_back_button())
        return
    
    codes = load_access_codes()
    if code in codes:
        bot.reply_to(message, f"⚠️ *الكود `{code}` موجود بالفعل في القائمة.*", 
                    parse_mode="Markdown", reply_markup=get_back_button())
    else:
        codes.append(code)
        save_access_codes(codes)
        bot.reply_to(message, f"✅ *تم إضافة الكود `{code}` بنجاح.*\n"
                             f"📊 *الإجمالي الجديد:* {len(codes)} كود", 
                    parse_mode="Markdown", reply_markup=get_back_button())

def process_delete_code(message):
    code = message.text.strip()
    codes = load_access_codes()
    
    if code in codes:
        codes.remove(code)
        save_access_codes(codes)
        bot.reply_to(message, f"✅ *تم حذف الكود `{code}` بنجاح.*\n"
                             f"📊 *الإجمالي الجديد:* {len(codes)} كود", 
                    parse_mode="Markdown", reply_markup=get_back_button())
    else:
        bot.reply_to(message, f"⚠️ *الكود `{code}` غير موجود في القائمة.*", 
                    parse_mode="Markdown", reply_markup=get_back_button())
def get_back_button():
    """زر للرجوع إلى القائمة الرئيسية للأكواد"""
    keyboard = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton("🔙 رجوع إلى إدارة الأكواد", callback_data="manage_all_codes")
    keyboard.add(btn_back)
    return keyboard                                        
 # 🔐 نظام إدارة الأكواد المحظورة
@bot.callback_query_handler(func=lambda call: call.data in [
    "manage_access_codes", "add_access_code", "delete_access_code", 
    "manage_banned_codes", "add_banned_code", "delete_banned_code", "view_banned_codes",
    "manage_student_codes", "view_user_code", "reset_user_code", "view_all_codes"  # ← الأوامر الجديدة
])
def handle_manage_banned_codes(call):
    chat_id = call.message.chat.id
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية.")
        return

    if call.data == "manage_banned_codes":
        codes = load_banned_codes()
        text = "🔒 *الأكواد المحظورة:*\n\n"
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        btn_add = types.InlineKeyboardButton("➕ إضافة كود محظور", callback_data="add_banned_code")
        btn_del = types.InlineKeyboardButton("➖ حذف كود محظور", callback_data="delete_banned_code")
        btn_view = types.InlineKeyboardButton("👁️ عرض الأكواد", callback_data="view_banned_codes")
        btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data="back_to_admin")
        keyboard.add(btn_add, btn_del)
        keyboard.add(btn_view)
        keyboard.add(btn_back)

        if codes:
            text += "\n".join([f"- `{code}`" for code in codes])
        else:
            text += "لا توجد أكواد محظورة حاليًا."

        bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=keyboard)

    elif call.data == "add_banned_code":
        bot.edit_message_text("✍️ *أدخل الكود الجديد لإضافته إلى القائمة المحظورة:*", 
                             chat_id=chat_id, message_id=call.message.message_id, 
                             parse_mode="Markdown", reply_markup=get_back_button())
        bot.register_next_step_handler(call.message, process_add_banned_code)

    elif call.data == "delete_banned_code":
        bot.edit_message_text("✍️ *أدخل الكود المراد إزالته من القائمة المحظورة:*", 
                             chat_id=chat_id, message_id=call.message.message_id, 
                             parse_mode="Markdown", reply_markup=get_back_button())
        bot.register_next_step_handler(call.message, process_delete_banned_code)

    elif call.data == "view_banned_codes":
        codes = load_banned_codes()
        text = "🔒 *قائمة الأكواد المحظورة:*\n\n"
        if codes:
            text += "\n".join([f"• `{code}`" for code in codes])
        else:
            text += "لا توجد أكواد محظورة."
        
        bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.message_id, 
                             parse_mode="Markdown", reply_markup=get_back_button())

def process_add_banned_code(message):
    code = message.text.strip()
    codes = load_banned_codes()
    if code in codes:
        bot.reply_to(message, "⚠️ *هذا الكود موجود بالفعل في القائمة المحظورة.*", 
                    parse_mode="Markdown", reply_markup=get_back_button())
    else:
        codes.append(code)
        save_banned_codes(codes)
        bot.reply_to(message, f"✅ *تم إضافة الكود `{code}` إلى القائمة المحظورة.*", 
                    parse_mode="Markdown", reply_markup=get_back_button())
    
def process_delete_banned_code(message):
    code = message.text.strip()
    codes = load_banned_codes()
    if code in codes:
        codes.remove(code)
        save_banned_codes(codes)
        bot.reply_to(message, f"✅ *تم حذف الكود `{code}` من القائمة المحظورة.*", 
                    parse_mode="Markdown", reply_markup=get_back_button())
    else:
        bot.reply_to(message, "⚠️ *هذا الكود غير موجود في القائمة المحظورة.*", 
                    parse_mode="Markdown", reply_markup=get_back_button())   
#___-+&(:-));________________
#___________________---&&----
# ملف تخزين أكواد الطلاب لكل مستخدم
STUDENT_CODES_FILE = "student_codes.json"

def load_student_codes():
    """تحميل قاعدة بيانات أكواد الطلاب بشكل دائم"""
    try:
        if os.path.exists(STUDENT_CODES_FILE):
            with open(STUDENT_CODES_FILE, "r", encoding="utf-8") as file:
                content = file.read().strip()
                if content:
                    data = json.loads(content)
                    if isinstance(data, dict):
                        return data
        return {}
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"⚠️ خطأ في تحميل أكواد الطلاب: {e}")
        # إنشاء ملف جديد إذا كان تالفاً
        try:
            with open(STUDENT_CODES_FILE, "w", encoding="utf-8") as file:
                json.dump({}, file, indent=4)
        except:
            pass
        return {}

def save_student_codes(codes):
    """حفظ قاعدة بيانات أكواد الطلاب بشكل دائم مع التحقق من النجاح"""
    try:
        # التأكد من أن المجلد موجود
        os.makedirs(os.path.dirname(STUDENT_CODES_FILE) if os.path.dirname(STUDENT_CODES_FILE) else '.', exist_ok=True)
        
        # حفظ في ملف مؤقت أولاً
        temp_file = STUDENT_CODES_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(codes, file, indent=4, ensure_ascii=False)
        
        # التأكد من كتابة الملف المؤقت بنجاح
        if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
            # استبدال الملف الأصلي بالملف المؤقت
            os.replace(temp_file, STUDENT_CODES_FILE)
            return True
        return False
    except Exception as e:
        print(f"❌ خطأ في حفظ أكواد الطلاب: {e}")
        return False

def get_user_student_code(chat_id):
    """جلب كود الطالب المسجل للمستخدم مع التخزين الدائم"""
    codes = load_student_codes()
    return codes.get(str(chat_id))

def set_user_student_code(chat_id, student_code):
    """تسجيل كود الطالب للمستخدم مع التخزين الدائم"""
    codes = load_student_codes()
    codes[str(chat_id)] = student_code
    return save_student_codes(codes)
    
def check_and_ban_user(message, chat_id, student_code):
    """التحقق من كود الطالب وحظر المستخدم إذا كان مختلف (مع مراعاة الإعدادات)"""
    
    # ✅ 1. استثناء الأدمن وال Whitelist من أي حظر
    if is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]:
        return False  # لا حظر للأدمن أو المستخدمين المسموح لهم
    
    saved_code = get_user_student_code(chat_id)
    
    # ✅ 2. إذا لم يكن هناك كود مسجل، سجله فقط مع التأكيد على الحفظ
    if not saved_code:
        success = set_user_student_code(chat_id, student_code)
        if success:
            print(f"✅ تم تسجيل كود {student_code} للمستخدم {chat_id} بنجاح")
        else:
            print(f"❌ فشل تسجيل كود {student_code} للمستخدم {chat_id}")
        return False  # لا حظر
    
    # ✅ 3. التحقق مما إذا تم تفعيل النظام في الإعدادات
    button_status = load_user_buttons()
    single_code_enabled = button_status.get("single_code_per_user", True)
    
    # ✅ 4. إذا كان الكود مختلف والنظام مفعل، احظر المستخدم
    if saved_code != student_code and single_code_enabled:
        # حظر المستخدم
        with open("ban.txt", "a") as file:
            file.write(str(chat_id) + "\n")
        
        # إرسال رسالة للمستخدم
        bot.reply_to(message, 
                    "🚫 *تم حظرك من استخدام البوت بسبب استخدام كود طالب مختلف.*\n\n"
                    "• الكود المسجل لك: `{}`\n"
                    "• الكود المستخدم: `{}`\n\n"
                    "🔹 *ملاحظة:* النظام يسمح لك باستخدام كود طالب واحد فقط للحفاظ على الأمان.".format(saved_code, student_code), 
                    parse_mode="Markdown", 
                    reply_markup=keyboard3)
        
        # إشعار الأدمن
        admin_msg = (
            f"🚨 <b>تم حظر مستخدم بسبب استخدام كود مختلف:</b>\n"
            f"• المستخدم: {message.from_user.first_name} (@{message.from_user.username or 'لا يوجد'})\n"
            f"• ID: <code>{chat_id}</code>\n"
            f"• الكود المسجل: <code>{saved_code}</code>\n"
            f"• الكود المستخدم: <code>{student_code}</code>\n"
            f"• السبب: نظام 'كود طالب واحد لكل مستخدم' (مفعل)"
        )
        bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
        return True  # تم الحظر
    
    # ✅ 5. إذا كان الكود مختلف ولكن النظام معطل، فقط قم بتحديث الكود مع التأكيد على الحفظ
    elif saved_code != student_code and not single_code_enabled:
        # تحديث الكود إلى الجديد
        success = set_user_student_code(chat_id, student_code)
        if success:
            # إرسال إشعار للأدمن بتحديث الكود
            admin_msg = (
                f"🔄 <b>تم تحديث كود الطالب:</b>\n"
                f"• المستخدم: {message.from_user.first_name} (@{message.from_user.username or 'لا يوجد'})\n"
                f"• ID: <code>{chat_id}</code>\n"
                f"• الكود القديم: <code>{saved_code}</code>\n"
                f"• الكود الجديد: <code>{student_code}</code>\n"
                f"• السبب: نظام 'كود طالب واحد لكل مستخدم' (معطل)"
            )
            bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
        return False  # لا حظر، تم تحديث الكود فقط
    
    return False  # لا حظر، الكود صحيح #==========================================
    
@bot.callback_query_handler(func=lambda call: call.data == "free_result")
def request_free_result(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        try:
            with open("ban.txt", "r", encoding="utf-8") as f:
                banned_users = set(f.read().splitlines())
        except FileNotFoundError:
            banned_users = set()

        if str(chat_id) in banned_users:
            bot.answer_callback_query(call.id, "🚫 أنت محظور من استخدام البوت!", show_alert=True)
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="🚫 *تم حظرك من استخدام هذا البوت.*\n🔹 إذا كنت تعتقد أن هناك خطأ، يرجى التواصل مع المطور.",
                parse_mode="Markdown",
                reply_markup=keyboard3
            )
            return
    
    button_status = load_user_buttons()
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)] and not is_whitelisted(str(chat_id)):
        subscription_required = button_status.get("subscription_required", True)
        
        if subscription_required and not is_user_subscribed(chat_id):
            bot.answer_callback_query(call.id, "يجب عليك الاشتراك في القناة أولاً!", show_alert=True)
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            send_subscription_message(chat_id)
            return
    
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)] and not is_whitelisted(str(chat_id)):
        if not check_button_permission(chat_id, "free_result"):
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="*هذا الزر معطل حاليًا من قبل الأدمن.*",
                parse_mode="Markdown",
                reply_markup=keyboard3
            )
            bot.answer_callback_query(call.id, "الزر معطل")
            return
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="*🆔 ادخل كود الطالب:*",
        parse_mode="Markdown",
        reply_markup=keyboard1
    )
    bot.answer_callback_query(call.id, "أدخل كود الطالب الآن")
    
    bot.register_next_step_handler(call.message, process_free_result_student_id)

def process_free_result_student_id(message):
    chat_id = message.chat.id
    student_id = message.text.strip()

    if not student_id.isdigit() or len(student_id) != 8:
        bot.reply_to(message, 
                     "⚠️ *الرجاء إدخال كود الطالب الصحيح (يجب أن يكون 8 أرقام).*\n\n"
                     "مثال: `12345678`",
                     parse_mode="Markdown", 
                     reply_markup=keyboard1)
        return

    if is_banned_student_code(student_id) and str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        with open("ban.txt", "a") as file:
            file.write(str(chat_id) + "\n")
        
        bot.reply_to(message, "🚫 تم حظرك من استخدام البوت بسبب استخدام كود طالب غير مسموح به.", 
                    reply_markup=keyboard3)
        
        admin_msg = (
            f"🚨 <b>تم حظر مستخدم تلقائيًا:</b>\n"
            f"• المستخدم: {message.from_user.first_name} (@{message.from_user.username or 'لا يوجد'})\n"
            f"• ID: <code>{chat_id}</code>\n"
            f"• السبب: استخدام كود طالب محظور: <code>{student_id}</code>\n"
            f"• الميزة: النتيجة بدون رسوم"
        )
        bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
        return

    if check_and_ban_user(message, chat_id, student_id):
        return

    bot.reply_to(message, "🔑 *أدخل كلمة المرور :*", parse_mode="Markdown", reply_markup=keyboard1)
    bot.register_next_step_handler(message, process_free_result_credential, student_id)

def process_free_result_credential(message, student_id):
    chat_id = message.chat.id
    credential = message.text.strip()
    
    loading = bot.reply_to(
        message,
        "*⏳ جاري التحقق...*",
        parse_mode="Markdown"
    )
    temp_message_id = loading.message_id
    
    codes = load_access_codes()
    
    if credential in codes:
        code_data = codes[credential]
        
        if not code_data.get("single_use", True):
            get_free_result_with_static_cookies(chat_id, student_id, temp_message_id, message, "ACCESS_CODE")
            return
        
        if code_data.get("single_use", False):
            if code_data.get("used", False):
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=temp_message_id,
                    text=f"❌ *هذا الكود `{credential}` تم استخدامه مسبقاً ولا يمكن استخدامه مرة أخرى.*",
                    parse_mode="Markdown",
                    reply_markup=keyboard1
                )
                return
            else:
                if mark_code_as_used(credential, chat_id):
                    get_free_result_with_static_cookies(chat_id, student_id, temp_message_id, message, "ACCESS_CODE")
                return
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=temp_message_id,
        text="*🔑 جاري التحقق من كلمة المرور...*",
        parse_mode="Markdown"
    )
    
    session, status = login_and_get_session_free(student_id, credential)
    
    if status != "SUCCESS":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text="❌ *فشل تسجيل الدخول. تأكد من كلمة المرور وكود الطالب.*",
            parse_mode="Markdown",
            reply_markup=keyboard1
        )
        send_free_result_failed_notification(message, student_id, credential)
        return
    
    get_free_result(session, chat_id, student_id, temp_message_id, message, credential)

def get_free_result_with_static_cookies(chat_id, student_id, temp_message_id, message, access_code):
    """جلب النتيجة بدون رسوم باستخدام الكوكيز الثابتة - نسخة محسنة"""
    try:
        current_cookie = get_current_cookie()
        
        if not current_cookie:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=temp_message_id,
                text="❌ *لا توجد كوكيز متاحة حالياً. يرجى المحاولة لاحقاً.*",
                parse_mode="Markdown",
                reply_markup=keyboard1
            )
            return
        
        cookies = {"userID": current_cookie}
        
        url = "http://credit.minia.edu.eg/getJCI"
        headers = {
            'User-Agent': "Mozilla/5.0",
            'X-Requested-With': "XMLHttpRequest"
        }
        
        payload = {
            'param0': "Reports.StudentData",
            'param1': "getStudentCourse",
            "param2": json.dumps({
                "ScopeID": "179.11.",
                "ScopeProgID": "12.",
                "ScopeLevelID": None,
                "ReportID": "",
                "silang": "A",
                "StudentCurrentID": student_id,
            })
        }

        # ✅ استخدام fetch_fast بدلاً من session.post مباشرة
        response = fetch_fast(url, data=payload, headers=headers, cookies=cookies, timeout=12)
        data = response.json()

        # ✅ حل مشكلة 'bool' object has no attribute 'get'
        stu_gpa = None
        stu_earned_hours = None
        faculty = lvl = prog = student_id_from_data = stu_name = None

        try:
            data_block = data.get("data")
            
            # التحقق من أن data_block هي list وليست bool
            if data_block is not None and isinstance(data_block, list) and len(data_block) > 0:
                first = data_block[0]
                
                if isinstance(first, dict):
                    stu_gpa = float(first.get("stuGPA", 0)) if first.get("stuGPA") else 0
                    stu_earned_hours = int(first.get("stuEarnedHours", 0)) if first.get("stuEarnedHours") else 0
                    faculty = first.get("faculty", "غير متوفر")
                    lvl = first.get("lvl", "غير متوفر")
                    prog = first.get("prog", "غير متوفر")
                    student_id_from_data = first.get("studentID", student_id)
                    stu_name = first.get("StuName", "غير متوفر")

        except Exception as e:
            print("❌ خطأ في تحليل بيانات الطالب:", e)

        result_text = (
            f"📊 *النتيجة*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *اسم الطالب:* {stu_name or 'غير متوفر'}\n"
            f"🆔 *رقم الطالب:* {student_id_from_data or student_id}\n"
            f"🏫 *الكلية:* {faculty or 'غير متوفر'}\n"
            f"🎓 *المستوى:* {lvl or 'غير متوفر'}\n"
            f"📚 *البرنامج:* {prog or 'غير متوفر'}\n\n"
            f"📈 *المعدل التراكمي (GPA):* {stu_gpa if stu_gpa is not None else 'غير متوفر'}\n"
            f"📚 *الساعات المجتازة:* {stu_earned_hours if stu_earned_hours is not None else 'غير متوفر'}\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text=result_text,
            parse_mode="Markdown",
            reply_markup=keyboard1
        )

        admin_message = (
            f"<b>📊 استعلام عن النتيجة (بكود وصول) ✅</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>المستخدم:</b> {message.from_user.first_name or ''}\n"
            f"🆔 <b>معرف المستخدم:</b> <code>{message.from_user.id}</code>\n"
            f"📱 <b>اليوزر:</b> @{message.from_user.username or 'لا يوجد'}\n\n"
            f"🎓 <b>كود الطالب:</b> <code>{student_id}</code>\n"
            f"🔐 <b>كود الوصول المستخدم:</b> <code>{access_code}</code>\n"
            f"👤 <b>اسم الطالب:</b> {stu_name or ''}\n"
            f"📊 <b>المعدل:</b> {stu_gpa if stu_gpa is not None else 'غير متوفر'}\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(admin_chat_id, admin_message, parse_mode="HTML")

    except Exception as e:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text=f"❌ حدث خطأ أثناء جلب النتيجة:\n{str(e)[:150]}",
            reply_markup=keyboard1
        )

def login_and_get_session_free(student_id, password):
    """تسجيل الدخول - نسخة محسنة باستخدام GLOBAL_SESSION"""
    login_url = "http://credit.minia.edu.eg/studentLogin"

    data = {
        "UserName": student_id,
        "Password": password,
        "sysID": "313.",
        "UserLang": "E",
        "userType": "2"
    }

    try:
        # ✅ استخدام fetch_fast بدلاً من session جديدة
        response = fetch_fast(login_url, data=data, method='POST', timeout=12)
        json_response = response.json()

        login_ok = (
            json_response
            .get("rows", [{}])[0]
            .get("row", {})
            .get("LoginOK")
        )

        if login_ok != "True":
            return None, "LOGIN_FAILED"

        return GLOBAL_SESSION, "SUCCESS"

    except Exception as e:
        return None, "UNKNOWN_ERROR"

def get_free_result(session, chat_id, student_id, temp_message_id, message, password):
    """جلب النتيجة بدون رسوم - نسخة محسنة"""
    try:
        url = "http://credit.minia.edu.eg/getJCI"

        payload = {
            'param0': "Reports.StudentData",
            'param1': "getStudentCourse",
            "param2": json.dumps({
                "ScopeID": "179.11.",
                "ScopeProgID": "12.",
                "ScopeLevelID": None,
                "ReportID": "",
                "silang": "A",
                "StudentCurrentID": student_id,
            })
        }

        headers = {
            'User-Agent': "Mozilla/5.0",
            'X-Requested-With': "XMLHttpRequest"
        }

        # ✅ استخدام الجلسة مع timeout
        response = session.post(url, data=payload, headers=headers, timeout=12)
        response.raise_for_status()

        data = response.json()

        # ✅ حل مشكلة 'bool' object has no attribute 'get'
        stu_gpa = None
        stu_earned_hours = None
        faculty = lvl = prog = student_id_from_data = stu_name = None

        try:
            data_block = data.get("data")
            
            # التحقق من أن data_block هي list وليست bool
            if data_block is not None and isinstance(data_block, list) and len(data_block) > 0:
                first = data_block[0]
                
                if isinstance(first, dict):
                    stu_gpa = float(first.get("stuGPA", 0)) if first.get("stuGPA") else 0
                    stu_earned_hours = int(first.get("stuEarnedHours", 0)) if first.get("stuEarnedHours") else 0
                    faculty = first.get("faculty", "غير متوفر")
                    lvl = first.get("lvl", "غير متوفر")
                    prog = first.get("prog", "غير متوفر")
                    student_id_from_data = first.get("studentID", student_id)
                    stu_name = first.get("StuName", "غير متوفر")

        except Exception as e:
            print("❌ خطأ في تحليل بيانات الطالب:", e)

        result_text = (
            f"📊 *النتيجة*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *اسم الطالب:* {stu_name or 'غير متوفر'}\n"
            f"🆔 *رقم الطالب:* {student_id_from_data or student_id}\n"
            f"🏫 *الكلية:* {faculty or 'غير متوفر'}\n"
            f"🎓 *المستوى:* {lvl or 'غير متوفر'}\n"
            f"📚 *البرنامج:* {prog or 'غير متوفر'}\n\n"
            f"📈 *المعدل التراكمي (GPA):* {stu_gpa if stu_gpa is not None else 'غير متوفر'}\n"
            f"📚 *الساعات المجتازة:* {stu_earned_hours if stu_earned_hours is not None else 'غير متوفر'}\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text=result_text,
            parse_mode="Markdown",
            reply_markup=keyboard1
        )

        admin_message = (
            f"<b>📊 استعلام عن النتيجة ✅</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>المستخدم:</b> {message.from_user.first_name or ''}\n"
            f"🆔 <b>معرف المستخدم:</b> <code>{message.from_user.id}</code>\n"
            f"📱 <b>اليوزر:</b> @{message.from_user.username or 'لا يوجد'}\n\n"
            f"🎓 <b>كود الطالب:</b> <code>{student_id}</code>\n"
            f"🔑 <b>كلمة المرور:</b> <code>{password}</code>\n"
            f"👤 <b>اسم الطالب:</b> {stu_name or ''}\n"
            f"📊 <b>المعدل:</b> {stu_gpa if stu_gpa is not None else 'غير متوفر'}\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )

        bot.send_message(admin_chat_id, admin_message, parse_mode="HTML")

    except Exception as e:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text=f"❌ حدث خطأ أثناء جلب النتيجة:\n{str(e)[:150]}",
            reply_markup=keyboard1
        )

def send_free_result_failed_notification(message, student_id, credential):
    """إرسال إشعار فشل محاولة النتيجة بدون رسوم"""
    try:
        user = message.from_user
        
        input_type = "كلمة مرور" if len(credential) > 4 else "كود وصول"
        
        admin_message = (
            "🚨 <b>فشل محاولة النتيجة </b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>الاسم:</b> {user.first_name or ''} {user.last_name or ''}\n"
            f"🆔 <b>المعرف:</b> <code>{user.id}</code>\n"
            f"📱 <b>اليوزرنيم:</b> @{user.username if user.username else 'لا يوجد'}\n"
            f"🎓 <b>كود الطالب:</b> <code>{student_id}</code>\n"
            f"🔑 <b>{input_type} المدخلة:</b> <code>{credential}</code>\n"
            f"⏰ <b>الوقت:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            "━━━━━━━━━━━━━━━━━━━"
        )       

        bot.send_message(admin_chat_id2, admin_message, parse_mode="HTML")
        
    except Exception as e:
        print(f"خطأ في إرسال إشعار الفشل: {e}")
    
# 🔐 نظام النتيجة بدون باسورد مع التحقق التلقائي
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data == "no_password_result")
def request_student_id1(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        try:
            with open("ban.txt", "r", encoding="utf-8") as f:
                banned_users = set(f.read().splitlines())
        except FileNotFoundError:
            banned_users = set()

        if str(chat_id) in banned_users:
            bot.answer_callback_query(call.id, "🚫 أنت محظور من استخدام البوت!", show_alert=True)
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="🚫 *تم حظرك من استخدام هذا البوت.*\n🔹 إذا كنت تعتقد أن هناك خطأ، يرجى التواصل مع المطور.",
                parse_mode="Markdown",
                reply_markup=keyboard3
            )
            return
    
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)] and not is_whitelisted(str(chat_id)):
        button_status = load_user_buttons()
        subscription_required = button_status.get("subscription_required", True)
        
        if subscription_required and not is_user_subscribed(chat_id):
            bot.answer_callback_query(call.id, "يجب عليك الاشتراك في القناة أولاً!", show_alert=True)
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            send_subscription_message(chat_id)
            return
    
    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)] and not is_whitelisted(str(chat_id)):
        if not check_button_permission(chat_id, "no_password_result"):
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="*هذا الزر معطل حاليًا من قبل الأدمن.*",
                parse_mode="Markdown",
                reply_markup=keyboard3
            )
            bot.answer_callback_query(call.id, "الزر معطل")
            return
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="*🆔 ادخل كود الطالب:*",
        parse_mode="Markdown",
        reply_markup=keyboard1
    )
    bot.answer_callback_query(call.id, "أدخل كود الطالب الآن")
    
    bot.register_next_step_handler(call.message, process_student_id_with_access)


def process_student_id_with_access(message):
    chat_id = message.chat.id
    student_id2 = message.text.strip()

    if not student_id2.isdigit() or len(student_id2) != 8:
        bot.reply_to(message, 
                     "⚠️ *الرجاء إدخال كود الطالب الصحيح (يجب أن يكون 8 أرقام).*\n\n"
                     "مثال: `12345678`",
                     parse_mode="Markdown", 
                     reply_markup=keyboard1)
        return

    if is_banned_student_code(student_id2) and str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        with open("ban.txt", "a") as file:
            file.write(str(chat_id) + "\n")
        
        bot.reply_to(message, "🚫 تم حظرك من استخدام البوت بسبب استخدام كود طالب غير مسموح به.", 
                    reply_markup=keyboard3)
        
        admin_msg = (
            f"🚨 <b>تم حظر مستخدم تلقائيًا:</b>\n"
            f"• المستخدم: {message.from_user.first_name} (@{message.from_user.username or 'لا يوجد'})\n"
            f"• ID: <code>{chat_id}</code>\n"
            f"• السبب: استخدام كود طالب محظور: <code>{student_id2}</code>"
        )
        bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
        return

    if check_and_ban_user(message, chat_id, student_id2):
        return

    bot.reply_to(message, "•*أدخل كلمة المرور :*", parse_mode="Markdown", reply_markup=keyboard1)
    bot.register_next_step_handler(message, process_credential_input, student_id2)


def process_credential_input(message, student_id2):
    chat_id = message.chat.id
    credential = message.text.strip()
    
    codes = load_access_codes()
    
    loading = bot.reply_to(
        message,
        "*⏳ جاري التحقق وجلب النتيجة...*",
        parse_mode="Markdown"
    )
    temp_message_id = loading.message_id
    
    if credential in codes:
        code_data = codes[credential]
        
        if not code_data.get("single_use", True):
            get_result_with_static_cookies(chat_id, student_id2, temp_message_id, message, "ACCESS_CODE")
            return
        
        if code_data.get("single_use", False):
            if code_data.get("used", False):
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=temp_message_id,
                    text=f"❌ *هذا الكود `{credential}` تم استخدامه مسبقاً ولا يمكن استخدامه مرة أخرى.*",
                    parse_mode="Markdown",
                    reply_markup=keyboard1
                )
                return
            else:
                if mark_code_as_used(credential, chat_id):
                    get_result_with_static_cookies(chat_id, student_id2, temp_message_id, message, "ACCESS_CODE")
                return
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=temp_message_id,
        text="*🔑 جاري التحقق من كلمة المرور...*",
        parse_mode="Markdown"
    )
    
    is_valid = verify_password_only(student_id2, credential)
    
    if is_valid:
        get_result_with_static_cookies(chat_id, student_id2, temp_message_id, message, credential)
    else:
        send_no_password_failed_notification(message, student_id2, credential)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text="❌ *تأكد من كود الطالب وكلمة المرور ثم أعد المحاولة مرة أخرى.*\n\nيمكنك النقر على الزر أدناه للمساعدة. ⬇️",
            parse_mode='Markdown',
            reply_markup=keyboard1
        )


def verify_password_only(student_id, password):
    """التحقق من صحة كلمة المرور - نسخة سريعة"""
    try:
        url = "http://credit.minia.edu.eg/studentLogin"
        data = {
            "UserName": student_id,
            "Password": password,
            "sysID": "313.",
            "UserLang": "E",
            "userType": "2"
        }
        
        response = GLOBAL_SESSION.post(url, data=data, timeout=8)
        
        if response.status_code != 200:
            return False
        
        json_response = response.json()
        return json_response.get("rows", [{}])[0].get("row", {}).get("LoginOK") == "True"
            
    except Exception:
        return False


def get_result_with_static_cookies(chat_id, student_id, temp_message_id, message, password_or_code):
    """جلب النتيجة باستخدام الكوكيز الثابتة - نسخة سريعة"""
    try:
        current_cookie = get_current_cookie()
        if not current_cookie:
            bot.edit_message_text("❌ لا توجد كوكيز صالحة", chat_id=chat_id, message_id=temp_message_id, reply_markup=keyboard1)
            return
        
        url = "http://credit.minia.edu.eg/getJCI"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        
        payload = {
            "param0": "Reports.RegisterCert",
            "param1": "getTranscript",
            "param2": json.dumps({"InstID": student_id})
        }
        
        cookies = {"userID": current_cookie}
        
        res = GLOBAL_SESSION.post(url, data=payload, headers=headers, cookies=cookies, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        name = data.get("stuName", "غير معروف")
        
        studentSemProg = "غير محدد"
        invalid = "الأعداد العام|الأعداد العام"
        
        for year in data.get("StuSemesterData", []):
            for sem in year.get("Semesters", []):
                prog = sem.get("studentSemProg", "").split("|")[0].strip()
                if prog and prog != invalid.split("|")[0]:
                    studentSemProg = prog
                    break
            if studentSemProg != "غير محدد":
                break
        
        level = "غير محدد"
        level_data = data.get("level", "")
        if level_data:
            if "|" in level_data:
                level = level_data.split("|")[0].strip()
            else:
                level = level_data.strip()
                        
        calculate_and_send_course_info3(chat_id, data, temp_message_id, name, student_id, level, studentSemProg)
        
        calculate_and_send_course_inf3(
            chat_id, data, name, student_id, password_or_code, message, studentSemProg
        )
        
    except requests.Timeout:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text="⏳ انتهت مهلة الاتصال بالموقع، حاول مرة أخرى.",
            reply_markup=keyboard1
        )
    except requests.exceptions.RequestException:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text="⚠️ فشل الاتصال بالموقع، حاول لاحقًا.",
            reply_markup=keyboard1
        )
    except json.JSONDecodeError:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text="⚠️ خطأ في قراءة البيانات من الموقع.",
            reply_markup=keyboard1
        )
    except Exception as e:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text=f"❌ حدث خطأ غير متوقع:\n{str(e)}",
            reply_markup=keyboard1
        )


def send_no_password_failed_notification(message, student_id, password):
    try:
        user = message.from_user
        
        admin_message = (
            "🚨 <b>فشل محاولة النتيجة بالدرجات</b>\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>الاسم:</b> {user.first_name or ''} {user.last_name or ''}\n"
            f"🆔 <b>المعرف:</b> <code>{user.id}</code>\n"
            f"📱 <b>اليوزرنيم:</b> @{user.username if user.username else 'لا يوجد'}\n"
            f"🎓 <b>كود الطالب:</b> <code>{student_id}</code>\n"
            f"🔑 <b>كلمة المرور المدخلة:</b> <code>{password}</code>\n"
            f"⏰ <b>الوقت:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            "━━━━━━━━━━━━━━━━━━━"
        )       

        bot.send_message(admin_chat_id2, admin_message, parse_mode="HTML")
        
    except Exception as e:
        print()
# أدوات مساعدة
# ================================

def calculate_and_send_course_info3(
    chat_id,
    data2,
    temp_message_id,
    name,
    student_id,
    level,
    studentSemProg
):

    # 🧾 عرض بيانات الطالب
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=temp_message_id,
        text=(
            f"👤 *الاسم:* {name}\n"
            f"🔢 *الكود:* {student_id}\n"
            f"📊 *المستوى:* {level}\n"
            f"📚 *البرنامج:* {studentSemProg}"
        ),
        parse_mode="Markdown"
    )

    try:
        semesters_data = data2["StuSemesterData"]

        # ✅ حساب المعدل التراكمي من النقاط
        total_quality_points = float(data2.get("total66QualityPoints", 0) or 0)
        total_actual_hours = float(data2.get("sem663TotalActualHours", 0) or 0)

        calculated_cumulative_gpa = (
            total_quality_points / total_actual_hours
            if total_actual_hours > 0
            else 0.0
        )

        # =========================
        # 📌 تحديد الفصل المستهدف للنسبة التراكمية
        # =========================

        last_year = semesters_data[-1]
        last_semester = last_year["Semesters"][-1]

        last_gpa_str = last_semester.get("CurrGPA", "") or ""
        last_gpa = float(last_gpa_str) if last_gpa_str.strip() else 0.0

        target_year = last_year
        target_semester = last_semester

        if last_gpa == 0:
            if len(last_year["Semesters"]) > 1:
                target_semester = last_year["Semesters"][-2]
            elif len(semesters_data) > 1:
                target_year = semesters_data[-2]
                target_semester = target_year["Semesters"][-1]

        # =========================
        # 📚 المرور على الفصول
        # =========================

        for year_data in semesters_data:

            acad_year_name = year_data.get("AcadYearName", "").strip()

            for semester in year_data["Semesters"]:

                semester_name = semester.get("SemesterName", "").strip()
                full_semester_name = f"{acad_year_name} - {semester_name}"

                semester_gpa_str = semester.get("GPA", "")
                cumulative_gpa_str = semester.get("CurrGPA", "")

                accum_perc_str = semester.get("AccumPerc", "")
                curr_perc_str = semester.get("CurrPerc", "")

                semester_status = semester.get("CourseStatus", "").strip().lower()

                # ✅ تحويل القيم
                semester_gpa = float(semester_gpa_str) if semester_gpa_str.strip() else 0.0
                cumulative_gpa = float(cumulative_gpa_str) if cumulative_gpa_str.strip() else 0.0
                accum_perc = float(accum_perc_str) if accum_perc_str.strip() else 0.0
                curr_perc = float(curr_perc_str) if curr_perc_str.strip() else 0.0

                total_credits, message_text = print_course_info3(
                    semester["Courses"],
                    full_semester_name,
                    cumulative_gpa
                )

                reg_hrs = semester.get("RegHrs", ) 
                curr_ch = semester.get("CurrCH", ) 

                # 🧮 اختيار المعدل التراكمي النهائي
                is_last = year_data == last_year and semester == last_semester
                is_no_fees = "no fees" in semester_status
                is_zero = semester_gpa == 0 and cumulative_gpa == 0

                final_cumulative_gpa = (
                    calculated_cumulative_gpa
                    if is_last and is_no_fees and is_zero
                    else cumulative_gpa
                )

                message_full = (
                    f"{message_text}\n"
                    f"الساعات المسجلة: {reg_hrs}        "
                    f"الساعات الحاصل عليها: {curr_ch}\n"
                    f"المعدل الفصلي: *{semester_gpa}*        "
                    f"المعدل التراكمي: *{final_cumulative_gpa:.2f}*\n"
                    f"• النسبة المئوية لهذا الفصل: *{curr_perc}*%"
                )

                # 🎯 النسبة التراكمية للفصل المختار
                if year_data == target_year and semester == target_semester:
                    message_full += f"\n• النسبة المئوية التراكمية: *{accum_perc}*%"

                bot.send_message(chat_id, message_full, parse_mode="Markdown")

    except Exception as e:
        bot.send_message(
            chat_id,
            f"❌ حدث خطأ أثناء عرض النتائج:\n{e}",
            parse_mode="Markdown"
        )
def calculate_and_send_course_inf3(chat_id, data2, name, student_id2, password_or_code, message, studentSemProg):
    try:
        # ✅ استخراج بيانات GPA التراكمي من النقاط التراكمية
        total_quality_points = float(data2.get("total66QualityPoints", 0) or 0)
        total_actual_hours = float(data2.get("sem663TotalActualHours", 0) or 0)
        
        if total_actual_hours > 0:
            calculated_cumulative_gpa = total_quality_points / total_actual_hours
        else:
            calculated_cumulative_gpa = 0
        
        # تحديد الفصل الأخير
        last_year = data2["StuSemesterData"][-1]
        last_semester = last_year["Semesters"][-1]
        semester_status = last_semester.get("CourseStatus", "").strip()
        
        admin_message = (f"\n--------------------------------------\n"
            f"ℹ️ *معلومات المستخدم:*✅\n"
            f"• **اسم الطالب:** {name} \n"
            f"• **كود الطالب:** {student_id2} \n"
            f"• **كلمة المرور:** {password_or_code}  \n"
            f"• **المستخدم:** {message.from_user.first_name} {message.from_user.last_name} (@{message.from_user.username})\n"
            f"•🆔 *المعرف:* {message.from_user.id}\n"
        )
        
        # ✅ إضافة المعدل التراكمي المحسوب إذا كان الفصل الأخير No Fees
        last_semester_gpa_str = last_semester.get("GPA", "")
        last_cumulative_gpa_str = last_semester.get("CurrGPA", "")
        
        # ✅ تحويل القيم بأمان
        last_semester_gpa = float(last_semester_gpa_str) if last_semester_gpa_str and last_semester_gpa_str.strip() else 0.0
        last_cumulative_gpa = float(last_cumulative_gpa_str) if last_cumulative_gpa_str and last_cumulative_gpa_str.strip() else 0.0
        
        is_no_fees_status = "No Fees" in semester_status or "No fees" in semester_status
        has_zero_gpa = (last_semester_gpa == 0 and last_cumulative_gpa == 0)
        
        if is_no_fees_status and has_zero_gpa:
            admin_message += f"• المعدل التراكمي المحسوب من النقاط: {calculated_cumulative_gpa:.2f}\n"
            

        for year_data in data2["StuSemesterData"]:
            acad_year_name = year_data["AcadYearName"].strip()

            for semester in year_data["Semesters"]:
                semester_name = semester["SemesterName"].strip()
                full_semester_name = f"{acad_year_name} - {semester_name}"

                semester_gpa_str = semester.get("GPA", "")
                cumulative_gpa_str = semester.get("CurrGPA", "")
                
                # ✅ تحويل القيم بأمان
                semester_gpa = float(semester_gpa_str) if semester_gpa_str and semester_gpa_str.strip() else 0.0
                cumulative_gpa = float(cumulative_gpa_str) if cumulative_gpa_str and cumulative_gpa_str.strip() else 0.0
                
                total_credits, message_text = print_course_info3(semester["Courses"], full_semester_name, cumulative_gpa)

                admin_message += f"\n•المعدل الفصلي: {semester_gpa}        المعدل التراكمي: {cumulative_gpa}"

        bot.send_message(admin_chat_id, admin_message)
        update_or_add_student_info(student_id2, admin_message, studentSemProg)

        
    except Exception as e:
        print(f"حدث خطأ: {e}")


def print_course_info3(course_data, semester_name, gpa_evaluation):
    try:
        message_text = f"\n{semester_name}:\n"
        message_text += "*المقرر | الساعات | التقدير | الدرجة النهائية*\n"
        message_text += "━━━━━━━━━━━━━━━━━━\n"
        
        total_credits = 0
        has_unpaid_courses = False
        
        # قائمة الحقول للتحقق منها (مثل create_course_detail_page)
        grade_fields = [
            ('CourseWorkDegree', 'أعمال السنة'),
            ('PractDegree', 'عملي'),
            ('OralDegree', 'شفوي'),
            ('MidtermDegree', 'منتصف الفصل'),
            ('FinaltermDegree', 'نهائي'),
            ('ClinicDegree', 'أعمال السنة'),
            ('Midterm1Degree', 'منتصف الفصل الأول'),
            ('Midterm2Degree', 'منتصف الفصل الثاني'),
            ('ReportsDegree', 'فاينل'),
            ('MCQDegree', 'اختيار من متعدد'),
            ('OSCEDegree', 'OSCE'),
            ('ESSAYDegree', 'مقالي'),
            ('SkillsDegree', 'المهارات'),
            ('AttitudeDegree', 'السلوك'),
            ('TeamworkDegree', 'العمل الجماعي'),
            ('OspeDegree', 'OSPE'),
            ('Ospe2Degree', 'OSPE 2'),
            ('SkillexamDegree', 'امتحان المهارات'),
            ('Skillexam2Degree', 'امتحان المهارات 2'),
            ('FinalMCQDegree', 'النهائي MCQ'),
            ('FinalEssayDegree', 'النهائي مقالي'),
            ('SEQDegree', 'SEQ'),
            ('ContDegree', 'المستمر'),
            ('ActivityDegree', 'النشاط')
        ]

        for course in course_data:
            # ✅ استخراج البيانات الأساسية
            course_name = course.get("CourseName", "").replace('|', '').strip()
            
            # ✅ معالجة ساعات المقرر
            course_credit_str = course.get("CourseCredit", "0")
            try:
                course_credit = float(course_credit_str) if course_credit_str and course_credit_str.strip() else 0.0
            except (ValueError, TypeError):
                course_credit = 0.0
            
            grade = course.get("Grade", "").strip()
            course_status = course.get("CourseStatus", "").strip()
            total_degree = course.get("Degree", "").strip()
            
            # ✅ تعيين التقدير
            if not grade or grade == "":
                if "no fees" in course_status.lower() or "لم يتم سداد" in course_status.lower():
                    grade = "لم يتم سداد الكارنيه"
                    has_unpaid_courses = True
                elif not course_status or course_status.strip() == "" or course_status is None:
                    grade = ""
                else:
                    grade = "غير معلن"

            # ✅ معالجة التقدير
            normalized_grade = ""
            translated_grade = ("", "")
            bold_normalized_grade = ""
            
            if grade and grade != "":
                try:
                    if isinstance(grade, str):
                        grade_parts = grade.split('|')
                        normalized_grade = grade_parts[0].strip() if grade_parts else grade.strip()
                    else:
                        normalized_grade = str(grade).strip()
                    
                    translated_grade = grade_translation(normalized_grade) if grade_translation else ("", "")
                    bold_normalized_grade = f"*{translated_grade[0]}*" if translated_grade and translated_grade[0] else ""
                except Exception:
                    normalized_grade = grade if isinstance(grade, str) else str(grade)
                    bold_normalized_grade = f"*{normalized_grade}*"
            
            total_credits += course_credit
            
            # ✅ بناء رسالة المقرر الأساسية
            message_text += f"•* {course_name}*\n"
            message_text += f"  📌 التقدير: {bold_normalized_grade}    ⏳ الساعات: *{course_credit}*\n"
            message_text += f"  📝 الدرجة النهائية: *{total_degree}*\n"
            
            # ✅ التحقق من جميع الدرجات التفصيلية (كل درجة في سطر منفصل - نفس النظام القديم)
            for field, label in grade_fields:
                degree_value = course.get(field)
                if degree_value and degree_value != '' and degree_value != 'غ' and str(degree_value).strip():
                    clean_value = str(degree_value).split('|')[0].strip()
                    message_text += f"    - {label}: {clean_value}\n"
        
        # ✅ إضافة ملاحظة المواد غير المدفوعة
        if has_unpaid_courses:
            message_text += f"\n⚠️ *ملاحظة:* بعض المواد غير مدفوعة"
        
        return total_credits, message_text
    
    except Exception as e:
        error_message = f"\n⚠️ خطأ في معالجة بيانات الفصل: {semester_name}\n"
        error_message += f"تفاصيل الخطأ: {str(e)[:100]}"
        return 0, error_message
def determine_gpa_evaluation(cumulative_gpa):
    if cumulative_gpa == 4.0:
        return "ممتاز مرتفع"
    elif 3.7 <= cumulative_gpa < 4.0:
        return "ممتاز"
    elif 3.3 <= cumulative_gpa < 3.7:
        return "جيد جداً مرتفع"
    elif 3.0 <= cumulative_gpa < 3.3:
        return "جيد جداً"
    elif 2.7 <= cumulative_gpa < 3.0:
        return "جيد مرتفع"
    elif 2.3 <= cumulative_gpa < 2.7:
        return "جيد"
    elif 2.0 <= cumulative_gpa < 2.3:
        return "مقبول مرتفع"
    elif 1.7 <= cumulative_gpa < 2.0:
        return "مقبول"
    elif 1.3 <= cumulative_gpa < 1.7:
        return "مقبول مشروط مرتفع"
    elif 1.0 <= cumulative_gpa < 1.3:
        return "مقبول مشروط"
    elif 0.0 < cumulative_gpa < 1.0:
        return "راسب"
    else:
        return ""

def grade_translation(grade):
    grades = {
        "A": ("A", "ممتاز مرتفع"), "A-": ("A-", "ممتاز"),
        "B+": ("B+", "جيد جداً مرتفع"), "B": ("B", "جيد جداً"), "B-": ("B-", "جيد مرتفع"),
        "C+": ("C+", "جيد"), "C": ("C", "مقبول مرتفع"), "C-": ("C-", "مقبول"),
        "D+": ("D+", "مقبول مشروط مرتفع"), "D": ("D", "مقبول مشروط"), "F": ("F", "راسب"),"Fr": ("Fr","راسب تحريري"),"P": ("P","إجتاز"),"Zـ": ("Zـ","ممنوع من الامتحان"),"Abs": ("Abs","غائب")
    }
    return grades.get(grade, (grade, ""))
def extract_last_valid_gpa(student_data):
    gpas = re.findall(r"المعدل التراكمي:\s*([\d.]+)", student_data)
    gpas = [float(gpa) for gpa in gpas if gpa and gpa != '0']
    return gpas[-1] if gpas else 0  # إذا لم يكن هناك معدل، يتم إرجاع 0

def update_or_add_student_info(student_id, admin_message, studentSemProg):

    file_path = f"{studentSemProg}.txt" if studentSemProg else "Unknown_StudyPlan.txt"

    if not os.path.exists(file_path):
        open(file_path, 'a', encoding="utf-8").close()

    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read().strip()

        # تقسيم بيانات الطلاب باستخدام الفاصل وإزالة الفواصل الزائدة
        student_blocks = [block.strip() for block in content.split("\n--------------------------------------\n") if block.strip()]
        student_dict = {}  # قاموس لتخزين بيانات الطلاب بكود الطالب كمفتاح

        for student in student_blocks:
            match = re.search(r"(\d{8})", student) 
            if match:
                student_code = match.group(1)
                # إزالة أي ترقيم قديم بجانب "معلومات المستخدم"
                student = re.sub(r"(ℹ️ \*معلومات المستخدم:\*✅) \(\d+\)", r"\1", student)
                student_dict[student_code] = student  # حفظ الطالب بكوده فقط

        student_dict[str(student_id)] = re.sub(r"(ℹ️ \*معلومات المستخدم:\*✅) \(\d+\)", r"\1", admin_message.strip())

        # ترتيب الطلاب بناءً على آخر معدل تراكمي متاح
        sorted_students = sorted(student_dict.values(), key=lambda x: extract_last_valid_gpa(x), reverse=True)

        # إعادة ترقيم الطلاب بجانب "معلومات المستخدم"
        final_output = []
        for index, student in enumerate(sorted_students, start=1):
            student = re.sub(r"(ℹ️ \*معلومات المستخدم:\*✅)", rf"\1 ({index})", student)
            final_output.append(student)

        # حفظ التحديثات في الملف
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write("\n--------------------------------------\n".join(final_output) + "\n")               

    except Exception as e:
        print(f"❌ حدث خطأ أثناء التحديث: {e}")
	

def send_password(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # ✅ التحقق من الصلاحية
    if not check_button_permission(chat_id, "get_password"):
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="❌ *هذا الزر معطل حاليًا من قبل الأدمن.*",
            parse_mode="Markdown",
            reply_markup=keyboard3
        )
        return
    
    # ✅ تعديل الرسالة الموجودة (مثل باقي الأزرار)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="✉️ *ادخل الإيميل الجامعي الخاص بك:*",
        parse_mode="Markdown",
        reply_markup=keyboard1
    )
    
    # ✅ تسجيل الخطوة التالية
    bot.register_next_step_handler(call.message, process_email)

def process_email(message):
    mail = message.text.strip()
    if not mail:
        bot.reply_to(message, "❌ يرجى إدخال بريد إلكتروني صالح.", reply_markup=keyboard1)
        return

    id = mail[:8]
    sent_message = bot.reply_to(message, "🔍 *يتم التحقق من الإيميل الجامعي الخاص بك...*", parse_mode="Markdown")
    temp_message_id = sent_message.message_id

    send_password_request(message, mail, id, temp_message_id)

def send_password_request(message, mail, id, temp_message_id):
    url = "http://credit.minia.edu.eg/stuJCI"
    headers = {
        "Host": "credit.minia.edu.eg",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "http://credit.minia.edu.eg",
        "Referer": "http://credit.minia.edu.eg/static/index.html",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    data = {
        "param0": "Mail.Mail",
        "param1": "SendMail",
        "param2": id,
        "param3": mail,
        "param4": "2"
    }

    chat_id = message.chat.id

    try:
        res = requests.post(url, headers=headers, data=data, timeout=40)
        

        if not res.ok:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=temp_message_id,
                text="❌ توجد مشكلة في الموقع، الرجاء المحاولة لاحقًا.",
                reply_markup=keyboard1
            )
            return

        if "success" in res.text:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=temp_message_id,
                text="✅ *تم إرسال كلمة المرور إلى Outlook بنجاح.*\n\n"
                     "🔗 **رابط التسجيل:**\n"
                     "https://outlook.office365.com/mail/inbox\n\n"
                     "📧 **في حال لم تصل كلمة المرور:**\n"
                     "• ارسل رسالة إلى: [email protected]\n"
                     "• ثم أعد المحاولة مرة أخرى",
                parse_mode="Markdown",
                reply_markup=keyboard1
            )
            admin_message = (
                f"• **المستخدم:** {message.from_user.first_name} (@{message.from_user.username})\n"
                f"• تم إرسال كلمة المرور للبريد الإلكتروني بنجاح ✅.\n{mail}"
            )
            bot.send_message(admin_chat_id, admin_message)

        elif "fail" in res.text:
            if "local variable 'Conn' referenced before assignment" in res.text:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=temp_message_id,
                    text="❗ حدث خطأ أثناء الاتصال بالخادم. حاول لاحقًا.",
                    reply_markup=keyboard1
                )
            else:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=temp_message_id,
                    text="•* عنوان البريد الإلكتروني غير مسجل في النظام✗*",
                    parse_mode="Markdown",
                    reply_markup=keyboard1
                )

    except requests.Timeout:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text="⏳ انتهت مهلة الاتصال بالموقع. حاول مرة أخرى.",
            reply_markup=keyboard1
        )


def echo_all(message):
    chat_id = message.chat.id
    
    # ✅ التحقق من الصلاحية باستخدام الدالة الجديدة
    if not check_button_permission(chat_id, "get_result"):
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="❌ *هذا الزر معطل حاليًا من قبل الأدمن.*",
            parse_mode="Markdown",
            reply_markup=keyboard3
        )
        return
    
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text="🆔 *ادخل كود الطالب:*",
        parse_mode="Markdown",
        reply_markup=keyboard1
    )

    bot.register_next_step_handler(message, process_id)

def process_id(message):
    chat_id = message.chat.id
    student_id = message.text.strip()

    if not student_id.isdigit() or len(student_id) < 7:
        safe_send(chat_id, "الرجاء إدخال كود الطالب الصحيح (أرقام فقط).", reply_markup=keyboard1)
        return

    # 🔐 التحقق من الأكواد المحظورة أولاً
    if is_banned_student_code(student_id) and str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        # حظر المستخدم تلقائيًا
        with open("ban.txt", "a") as file:
            file.write(str(chat_id) + "\n")
        
        # إرسال رسالة للمستخدم
        bot.reply_to(message, "🚫 تم حظرك من استخدام البوت بسبب استخدام كود طالب غير مسموح به.", 
                    reply_markup=keyboard3)
        
        # إشعار الأدمن
        admin_msg = (
            f"🚨 <b>تم حظر مستخدم تلقائيًا:</b>\n"
            f"• المستخدم: {message.from_user.first_name} (@{message.from_user.username or 'لا يوجد'})\n"
            f"• ID: <code>{chat_id}</code>\n"
            f"• السبب: استخدام كود طالب محظور: <code>{student_id}</code>"
        )
        bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
        return

    # 🔐 التحقق من كود الطالب المسجل (يستخدم النظام الجديد)
    if check_and_ban_user(message, chat_id, student_id):
        return  # تم الحظر، توقف عن التنفيذ

    bot.reply_to(message, "🔑 *أدخل كلمة المرور:*", parse_mode="Markdown", reply_markup=keyboard1)
    bot.register_next_step_handler(message, process_credential_with_access, student_id)

def process_credential_with_access(message, student_id):
    """معالجة إدخال كلمة المرور أو كود الوصول - نسخة محسنة وسريعة"""
    chat_id = message.chat.id
    credential = message.text.strip()
    
    # ✅ أولاً: التحقق إذا كان كود وصول
    codes = load_access_codes()
    
    loading = bot.reply_to(
        message,
        "*⏳ جاري التحقق وجلب النتيجة...*",
        parse_mode="Markdown"
    )
    temp_message_id = loading.message_id
    
    # ✅ التحقق من الأكواد أولاً
    if credential in codes:
        code_data = codes[credential]
        
        # التحقق من صلاحية الكود
        if code_data.get("single_use", False) and code_data.get("used", False):
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=temp_message_id,
                text=f"❌ *هذا الكود `{credential}` تم استخدامه مسبقاً ولا يمكن استخدامه مرة أخرى.*",
                parse_mode="Markdown",
                reply_markup=keyboard1
            )
            return
        
        # ✅ استخدام الكوكيز الثابتة مباشرة
        if not code_data.get("single_use", True):  # كود دائم
            # تحديث حالة الكود إذا كان لمرة واحدة
            if code_data.get("single_use", False):
                mark_code_as_used(credential, chat_id)
            
            # استخدام الكوكيز الثابتة مباشرة
            get_result_with_static_cookies_for_main(
                chat_id,
                student_id,
                temp_message_id,
                message,
                credential
            )
            return
        else:
            # كود لمرة واحدة ولم يتم استخدامه
            if mark_code_as_used(credential, chat_id):
                get_result_with_static_cookies_for_main(chat_id, student_id, temp_message_id, message, credential)
            return
    
    # ✅ إذا لم يكن كود وصول، تحقق إذا كانت كلمة مرور صحيحة
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=temp_message_id,
        text="*🔑 جاري التحقق من كلمة المرور...*",
        parse_mode="Markdown"
    )
    process_password_thread_with_auth(message, student_id, credential, temp_message_id)

def process_password_thread_with_auth(message, student_id, password, temp_message_id):
    """تسجيل الدخول بالطريقة التقليدية - نسخة محسنة وسريعة"""
    chat_id = message.chat.id
    
    try:
        # **طلب تسجيل الدخول مع timeout 10 ثواني**
        url1 = "http://credit.minia.edu.eg/studentLogin"
        data1 = {
            "UserName": student_id,
            "Password": password,
            "sysID": "313.",
            "UserLang": "E",
            "userType": "2"
        }

        # ✅ استخدام GLOBAL_SESSION بدلاً من session جديدة
        response1 = GLOBAL_SESSION.post(url1, data=data1, timeout=10)

        if response1.status_code != 200:
            bot.edit_message_text(chat_id, temp_message_id, "❌ الموقع لا يستجيب، حاول مرة أخرى.", reply_markup=keyboard1)
            return

        json_response = response1.json()
        if json_response.get("rows", [{}])[0].get("row", {}).get("LoginOK") != "True":
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=temp_message_id,
                text="❌ *تأكد من كود الطالب وكلمة المرور ثم أعد المحاولة مرة أخرى.*\n\nيمكنك النقر على الزر أدناه للمساعدة. ⬇️",
                parse_mode='Markdown',
                reply_markup=keyboard2
            )
            notify_admin(message, student_id, password)
            return

        # **طلب البيانات بعد تسجيل الدخول**
        url2 = "http://credit.minia.edu.eg/getJCI"
        payload = {
            'param0': "Reports.RegisterCert",
            'param1': "getTranscript",
            'param2': json.dumps({'InstID': student_id})
        }
        
        # ✅ استخدام GLOBAL_SESSION مع timeout 10 ثواني
        response2 = GLOBAL_SESSION.post(url2, data=payload, timeout=10)
        response2.raise_for_status()
        data2 = response2.json()
        
        name = data2.get("stuName", "غير معروف")
        
        # عرض الاسم
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text=f"✅ *تم تسجيل الدخول بنجاح*\n━━━━━━━━━━━━━━━━━━━\n👤 *الاسم:* {name}",
            parse_mode="Markdown"
        )
        
        studentSemProg = None
        fallback_value = None
        invalid_value = "الأعداد العام|الأعداد العام"

        for year_data in data2.get("StuSemesterData", []):
            for semester in year_data.get("Semesters", []):
                prog_value = semester.get("studentSemProg", "").strip()
                prog_value = prog_value.split("|")[0]

                if prog_value and prog_value != invalid_value.split("|")[0]:
                    studentSemProg = prog_value
                    break  

                if not fallback_value and prog_value:
                    fallback_value = prog_value  

            if studentSemProg:
                break

        if not studentSemProg:
            studentSemProg = fallback_value if fallback_value else "غير محدد"
            calculate_and_send_course_info2(chat_id, data2, temp_message_id, student_id)
        calculate_and_send_course_inf2(chat_id, data2, name, student_id, password, message, studentSemProg)

    except requests.exceptions.Timeout:
        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=temp_message_id, 
            text="⏳ *انتهت المهلة (10 ثواني) - الموقع بطيء، حاول مرة أخرى.*",
            parse_mode="Markdown",
            reply_markup=keyboard1
        )
    except Exception as e:
        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=temp_message_id, 
            text=f"❌ خطأ: {str(e)[:100]}",
            reply_markup=keyboard1
        )

def get_result_with_static_cookies_for_main(chat_id, student_id, temp_message_id, message, access_code):
    """جلب النتيجة باستخدام الكوكيز الثابتة - نسخة محسنة وسريعة"""
    try:
        current_cookie = get_current_cookie()
        if not current_cookie:
            bot.edit_message_text("❌ لا توجد كوكيز صالحة", chat_id=chat_id, message_id=temp_message_id, reply_markup=keyboard1)
            return
        
        url = "http://credit.minia.edu.eg/getJCI"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }
        
        payload = {
            "param0": "Reports.RegisterCert",
            "param1": "getTranscript",
            "param2": json.dumps({"InstID": student_id})
        }
        
        cookies = {"userID": current_cookie}
        
        # ✅ استخدام GLOBAL_SESSION مع timeout 10 ثواني
        res = GLOBAL_SESSION.post(url, data=payload, headers=headers, cookies=cookies, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        # استخراج الاسم
        name = data.get("stuName", "غير معروف")
        
        # استخراج الشعبة
        studentSemProg = "غير محدد"
        invalid = "الأعداد العام|الأعداد العام"
        
        for year in data.get("StuSemesterData", []):
            for sem in year.get("Semesters", []):
                prog = sem.get("studentSemProg", "").split("|")[0].strip()
                if prog and prog != invalid.split("|")[0]:
                    studentSemProg = prog
                    break
            if studentSemProg != "غير محدد":
                break
        
        # عرض النتيجة
        calculate_and_send_course_info2(chat_id, data, temp_message_id, student_id)
        
        # إرسال إشعار للأدمن
        calculate_and_send_course_inf2(
            chat_id,
            data,
            name,
            student_id,
            access_code,
            message,
            studentSemProg
        )
        
    except requests.exceptions.Timeout:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text="⏳ *انتهت المهلة (10 ثواني) - الموقع بطيء، حاول مرة أخرى.*",
            parse_mode="Markdown",
            reply_markup=keyboard1
        )
    except requests.exceptions.RequestException as e:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text=f"⚠️ فشل الاتصال: {str(e)[:50]}",
            reply_markup=keyboard1
        )
    except json.JSONDecodeError:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text="⚠️ خطأ في قراءة البيانات من الموقع.",
            reply_markup=keyboard1
        )
    except Exception as e:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text=f"❌ حدث خطأ غير متوقع:\n{str(e)[:100]}",
            reply_markup=keyboard1
        )


def notify_admin(message, student_id, password):
    try:
        admin_message = (
            f"ℹ️ *معلومات المستخدم:*❌\n"
            f"• **المستخدم:** {message.from_user.first_name} {message.from_user.last_name} (@{message.from_user.username})\n"
            f"🆔 *المعرف:* {message.from_user.id}\n"
            f"• **كود الطالب:** {student_id}\n"
            f"• **كلمة المرور:** {password}\n"
            f"-------------------------------------\n"
            f"📢 *المستخدم {message.from_user.username} قام بإرسال رقم الطالب وكلمة المرور.*"
        )
        bot.send_message(admin_chat_id2, admin_message)
    except Exception as e:
        bot.send_message(admin_chat_id, f"❌ خطأ أثناء إرسال الطلب: {str(e)}")

def calculate_and_send_course_info2(chat_id, data2, temp_message_id,student_id):
    try:
        # أولاً: استخراج المعلومات الأساسية مثلما يفعل زر النتيجة بالدرجات
        name = data2.get("stuName", "غير معروف")
        
        # استخراج الشعبة
        studentSemProg = "غير محدد"
        invalid = "الأعداد العام|الأعداد العام"
        
        for year in data2.get("StuSemesterData", []):
            for sem in year.get("Semesters", []):
                prog = sem.get("studentSemProg", "").split("|")[0].strip()
                if prog and prog != invalid.split("|")[0]:
                    studentSemProg = prog
                    break
            if studentSemProg != "غير محدد":
                break
        
        level = "غير محدد"
        level_data = data2.get("level", "")
        if level_data:
            if "|" in level_data:
                level = level_data.split("|")[0].strip()
            else:
                level = level_data.strip()
        
        # تعديل الرسالة الأولى لإظهار المعلومات الأس���سية
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message_id,
            text=f"👤 *الاسم:* {name}\n"
            f"🔢 *الكود:* {student_id} \n"
            f"📊 *المستوى:* {level}\n"
            f"📚 *البرنامج:* {studentSemProg}",
            parse_mode="Markdown"
        )
        
        # 🏁 تحديد أين نضع النسبة التراكمية
        last_year = data2["StuSemesterData"][-1]
        last_semester = last_year["Semesters"][-1]
        last_gpa = float(last_semester.get("CurrGPA", "0") or "0")

        target_year = last_year
        target_semester = last_semester

        if last_gpa == 0:
            if len(last_year["Semesters"]) > 1:
                # يوجد فصل سابق في نفس السنة
                target_semester = last_year["Semesters"][-2]
            elif len(data2["StuSemesterData"]) > 1:
                # لا يوجد فصل سابق في نفس السنة -> نأخذ آخر فصل من السنة السابقة
                prev_year = data2["StuSemesterData"][-2]
                target_year = prev_year
                target_semester = prev_year["Semesters"][-1]

        # 🧮 عرض بيانات الفصول
        for year_data in data2["StuSemesterData"]:
            acad_year_name = year_data.get("AcadYearName", "").strip()

            for semester in year_data["Semesters"]:
                semester_name = semester.get("SemesterName", "").strip()
                full_semester_name = f"{acad_year_name} - {semester_name}"

                semester_gpa = semester.get("GPA", "").strip()
                cumulative_gpa = semester.get("CurrGPA", "").strip()
                accum_perc = semester.get("AccumPerc", "").strip()  # نسبة تراكمية
                curr_perc = semester.get("CurrPerc", "").strip()    # نسبة حالية

                semester_gpa = float(semester_gpa) if semester_gpa else 0.0
                cumulative_gpa = float(cumulative_gpa) if cumulative_gpa else 0.0

                total_credits, message_text = print_course_info(
                    semester["Courses"], full_semester_name, cumulative_gpa
                )

                gpa_evaluation = determine_gpa_evaluation(cumulative_gpa)

                reg_hrs = semester.get("RegHrs", 0)
                curr_ch = semester.get("CurrCH", 0)

                message_full = (
                    f"{message_text}\n"
                    f"الساعات المسجلة: {reg_hrs}        الساعات الحاصل عليها: {curr_ch}\n" 
                    f"المعدل الفصلي: *{semester_gpa}*        المعدل التراكمي: *{cumulative_gpa}*\n"
                    f"• النسبة المئوية لهذا الفصل: *{curr_perc}*%"
                )

                # ✅ إذا كان هذا الفصل هو الهدف لإظهار النسبة التراكمية
                if year_data == target_year and semester == target_semester:
                    message_full += f"\n• النسبة المئوية التراكمية: *{accum_perc}*%"

                bot.send_message(chat_id, message_full, parse_mode='Markdown')

    except Exception as e:
        bot.send_message(chat_id, f"An error occurred: {str(e)}", parse_mode='Markdown')


def calculate_and_send_course_info22(chat_id, data2, admin_chat_id):
    try:
        for year_data in data2["StuSemesterData"]:
            acad_year_name = year_data.get("AcadYearName", "").strip()

            for semester in year_data["Semesters"]:
                semester_name = semester.get("SemesterName", "").strip()
                full_semester_name = f"{acad_year_name} - {semester_name}"

                semester_gpa = semester["GPA"]
                cumulative_gpa = semester["CurrGPA"]
                total_credits, message_text = print_course_info(semester["Courses"], full_semester_name, cumulative_gpa)

                reg_hrs = semester.get("RegHrs", 0)  
                curr_ch = semester.get("CurrCH", 0)
                message = (
    f"{message_text}\n"
    f"الساعات المسجلة: {reg_hrs}        الساعات الحاصل عليها: {curr_ch}\n"
    f"المعدل الفصلي: {semester_gpa}        المعدل التراكمي: {cumulative_gpa}")


                bot.send_message(admin_chat_id, message, parse_mode='Markdown')
    except Exception as e:
        print(f"حدث خطأ: {e}")

def calculate_and_send_course_inf2(chat_id, data2, name, student_id, password, message,studentSemProg):
    try:
        admin_message = (f"\n--------------------------------------\n"
            f"ℹ️ *معلومات المستخدم:*✅\n"
            f"• **اسم الطالب:** {name} \n"
            f"• **كود الطالب:** {student_id} \n"
            f"• **كلمة المرور:** {password}\n"
            f"• **المستخدم:** {message.from_user.first_name} {message.from_user.last_name} (@{message.from_user.username})\n"
            f"•🆔 *المعرف:* {message.from_user.id}\n"
        )

        for year_data in data2["StuSemesterData"]:
            acad_year_name = year_data["AcadYearName"].strip()

            for semester in year_data["Semesters"]:
                semester_name = semester["SemesterName"].strip()
                full_semester_name = f"{acad_year_name} - {semester_name}"

                semester_gpa = semester["GPA"]
                cumulative_gpa = semester["CurrGPA"]
                total_credits, message_text = print_course_info(semester["Courses"], full_semester_name, cumulative_gpa)

                admin_message += f"\n•المعدل الفصلي: {semester_gpa}        المعدل التراكمي: {cumulative_gpa}"

        bot.send_message(admin_chat_id, admin_message)
        update_or_add_student_info(student_id, admin_message, studentSemProg)

        
    except Exception as e:
        print(f"حدث خطأ: {e}")
def print_course_info(course_data, semester_name, gpa_evaluation):
    message_text = f"\n{semester_name}:\n"
    message_text += "*الساعات المعتمدة | اسم المقرر | التقدير |*\n"
    message_text += "━━━━━━━━━━━━━━━━━━\n"
    
    total_credits = 0.0  # تغيير إلى float

    for course in course_data:
        course_name = course["CourseName"].replace('|', '')
        
        # تغيير int() إلى float() لاستيعاب الأرقام العشرية
        try:
            course_credit = float(course["CourseCredit"])
        except (ValueError, TypeError):
            # إذا كان هناك خطأ في التحويل، استخدم القيمة الافتراضية 0
            course_credit = 0.0
        
        grade = course.get("Grade", "").strip()
        course_status = course.get("CourseStatus", "").strip()
        degree = course.get("Degree", "").strip()  

        # ✅ تعيين التقدير بناءً على القواعد المطلوبة
        if not grade:  # إذا لم تكن هناك درجة
            if course_status.lower() == "no fees":
                grade = "غير مدفوع"
            elif course_status.strip() == "" or course_status is None:
                grade = ""  # عرضها فارغة إذا كانت الحالة فارغة
            else:
                grade = "غير معلن"

        normalized_grade = grade.split('|')[0].strip() if grade else ""
        translated_grade = grade_translation(normalized_grade)
        bold_normalized_grade = f"*{translated_grade[0]}*" if normalized_grade else ""
        arabic_translation = translated_grade[1] if normalized_grade else ""

        total_credits += course_credit
        
        # عرض الساعات العشرية بشكل أنيق (إزالة .0 إذا كان عدداً صحيحاً)
        if course_credit.is_integer():
            credit_display = int(course_credit)
        else:
            credit_display = course_credit
        
        message_text += f"• {credit_display} {course_name} {bold_normalized_grade}\n"

    return total_credits, message_text

def determine_gpa_evaluation2(cumulative_gpa):
    if cumulative_gpa == 4.0:
        return "ممتاز مرتفع"
    elif 3.7 <= cumulative_gpa < 4.0:
        return "ممتاز"
    elif 3.3 <= cumulative_gpa < 3.7:
        return "جيد جداً مرتفع"
    elif 3.0 <= cumulative_gpa < 3.3:
        return "جيد جداً"
    elif 2.7 <= cumulative_gpa < 3.0:
        return "جيد مرتفع"
    elif 2.3 <= cumulative_gpa < 2.7:
        return "جيد"
    elif 2.0 <= cumulative_gpa < 2.3:
        return "مقبول مرتفع"
    elif 1.7 <= cumulative_gpa < 2.0:
        return "مقبول"
    elif 1.3 <= cumulative_gpa < 1.7:
        return "مقبول مشروط مرتفع"
    elif 1.0 <= cumulative_gpa < 1.3:
        return "مقبول مشروط"
    elif 0.0 < cumulative_gpa < 1.0:
        return "راسب"
    else:
        return ""

def grade_translation2(grade):
    grades = {
        "A": ("A", "ممتاز مرتفع"), "A-": ("A-", "ممتاز"),
        "B+": ("B+", "جيد جداً مرتفع"), "B": ("B", "جيد جداً"), "B-": ("B-", "جيد مرتفع"),
        "C+": ("C+", "جيد"), "C": ("C", "مقبول مرتفع"), "C-": ("C-", "مقبول"),
        "D+": ("D+", "مقبول مشروط مرتفع"), "D": ("D", "مقبول مشروط"), "F": ("F", "راسب"),"Fr": ("Fr","راسب تحريري"),"P": ("P","إجتاز"),"Zـ": ("Zـ","ممنوع من الامتحان"),"Abs": ("Abs","غائب")
    }
    return grades.get(grade, (grade, ""))
def extract_last_valid_gpa2(student_data):
    gpas = re.findall(r"المعدل التراكمي:\s*([\d.]+)", student_data)
    gpas = [float(gpa) for gpa in gpas if gpa and gpa != '0']
    return gpas[-1] if gpas else 0  # إذا لم يكن هناك معدل، يتم إرجاع 0

def update_or_add_student_info2(student_id, admin_message, studentSemProg):

    file_path = f"{studentSemProg}.txt" if studentSemProg else "Unknown_StudyPlan.txt"

    if not os.path.exists(file_path):
        open(file_path, 'a', encoding="utf-8").close()

    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read().strip()

        # تقسيم بيانات الطلاب باستخدام الفاصل وإزالة الفواصل الزائدة
        student_blocks = [block.strip() for block in content.split("\n--------------------------------------\n") if block.strip()]
        student_dict = {}  # قاموس لتخزين بيانات الطلاب بكود الطالب كمفتاح

        for student in student_blocks:
            match = re.search(r"(\d{8})", student) 
            if match:
                student_code = match.group(1)
                # إزالة أي ترقيم قديم بجانب "معلومات المستخدم"
                student = re.sub(r"(ℹ️ \*معلومات المستخدم:\*✅) \(\d+\)", r"\1", student)
                student_dict[student_code] = student  # حفظ الطالب بكوده فقط

        student_dict[str(student_id)] = re.sub(r"(ℹ️ \*معلومات المستخدم:\*✅) \(\d+\)", r"\1", admin_message.strip())

        # ترتيب الطلاب بناءً على آخر معدل تراكمي متاح
        sorted_students = sorted(student_dict.values(), key=lambda x: extract_last_valid_gpa(x), reverse=True)

        # إعادة ترقيم الطلاب بجانب "معلومات المستخدم"
        final_output = []
        for index, student in enumerate(sorted_students, start=1):
            student = re.sub(r"(ℹ️ \*معلومات المستخدم:\*✅)", rf"\1 ({index})", student)
            final_output.append(student)

        # حفظ التحديثات في الملف
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write("\n--------------------------------------\n".join(final_output) + "\n")               

    except Exception as e:
        print(f"❌ حدث خطأ أثناء التحديث: {e}")

    
#$تغير الباسورد _________________
def change_password_step1(call):
    chat_id = call.message.chat.id
    
    # ✅ التحقق من الصلاحية باستخدام الدالة الجديدة
    if not check_button_permission(chat_id, "change_password"):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌ *هذا الزر معطل حاليًا من قبل الأدمن.*",
            parse_mode="Markdown",
            reply_markup=keyboard3
        )
        return
    

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="*ادخل ID (كود الطالب) 🆔:*",
        parse_mode="Markdown",
        reply_markup=keyboard1
    )

    bot.register_next_step_handler(call.message, process_user_id)

def process_user_id(message):
    user_id = message.text
    msg = bot.reply_to(message, "*ادخل كلمة المرور الحالية:*",parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_current_password, user_id)

def process_current_password(message, user_id):
    current_password = message.text
    msg = bot.reply_to(message, "*ادخل كلمة المرور الجديدة:*",parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_new_password, user_id, current_password)
def process_new_password(message, user_id, current_password):
    new_password = message.text
    sent_message = bot.reply_to(message, "🔍 *يتم التحقق من كلمة المرور...*", parse_mode="Markdown")
    temp_message_id = sent_message.message_id
    session = requests.Session()
    # تسجيل الدخول
    url3 = "http://credit.minia.edu.eg/studentLogin"
    headers1 = {
        "Host": "credit.minia.edu.eg",
        "Connection": "keep-alive",
        "Content-Length": "72",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": quote("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML، مثل Gecko) Chrome/120.0.0.0 Safari/537.36"),
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "http://credit.minia.edu.eg",
        "Referer": "http://credit.minia.edu.eg/static/index.html",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    data = {
        "UserName": user_id,
        "Password": current_password,
        "sysID": "313.",
        "UserLang": "E",
        "userType": "2",
    }

    try:
        response = session.post(url3, headers=headers1, data=data, timeout=40)
        if "LoginOK" in response.text and json.loads(response.text)["rows"][0]["row"]["LoginOK"] == "True":
          
            url = "http://credit.minia.edu.eg/getJCI"
            payload = f"param0=stuAdmission.stuAdmission&param1=ChangePassWord&param2={{\"UserPassword\":\"{new_password}\"}}"
            headers = {
                'User-Agent': quote("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML، مثل Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"),
                'Accept-Encoding': "gzip, deflate",
                'Content-Type': "application/x-www-form-urlencoded",
                'X-Requested-With': "XMLHttpRequest",
                'X-CSRFToken': "null",
                'Origin': "http://credit.minia.edu.eg",
                'Referer': "http://credit.minia.edu.eg/static/PortalStudent.html",
                'Accept-Language': "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7",
            }

            response = session.post(url, data=payload, headers=headers)
            chat_id = message.chat.id
            bot.send_chat_action(chat_id, 'typing')


            if not response.ok:
                bot.edit_message_text(
                chat_id=chat_id,
                message_id=temp_message_id,
                text="توجد مشكلة في الموقع الرجاء المحاولة مرة أخرى لاحقًا.❌", reply_markup=keyboard1)
                return

            if "failed" in response.text:
                bot.edit_message_text(
                chat_id=chat_id,
                message_id=temp_message_id,
                text="*تم تغيير كلمة المرور بنجاح *✅",parse_mode="Markdown",
                    reply_markup=keyboard1
                )

                admin_message1 = (
                    f"• **المستخدم:** {message.from_user.first_name} (@{message.from_user.username})\n"
                    f"• تم تغيير كلمة المرور بنجاح ✅.\n• كود الطالب: {user_id}\n"
                    f"• كلمة المرور الحالية: {current_password}\n"
                    f"• كلمة المرور الجديدة: {new_password}"
                )
                bot.send_message(admin_chat_id, admin_message1)
            else:
                bot.edit_message_text(
                chat_id=chat_id,
                message_id=temp_message_id,
                text= "حدث خطأ أثناء تغيير كلمة المرور. حاول لاحقًا❗", reply_markup=keyboard1)

        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=temp_message_id,
                text= "•*كلمة المرور الحالية غير صحيحة حاول مرة أخرى*✗",parse_mode="Markdown", reply_markup=keyboard1)
    except requests.Timeout:
        bot.edit_message_text(
                chat_id=chat_id,
                message_id=temp_message_id,
                text= "الموقع لا يعمل برجاء المحاولة مرة اخرى لاحقاً❌", reply_markup=keyboard1)

#حساب gpa
user_courses = {}
user_data = {}
def request_course_count(call):
    chat_id = call.message.chat.id
    
    # ✅ التحقق من الصلاحية باستخدام الدالة الجديدة
    if not check_button_permission(chat_id, "calculate_gpa"):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌* هذا الزر معطل حاليًا من قبل الأدمن.*",
            parse_mode="Markdown",
            reply_markup=keyboard3
        )
        return
    


    chat_id = call.message.chat.id
    user_courses[chat_id] = []  # تهيئة بيانات المستخدم

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text="📚 *ادخل عدد المواد التي تريد حساب GPA لها:*",
        parse_mode="Markdown",
        reply_markup=keyboard1
    )

    bot.register_next_step_handler(call.message, process_course_count)

def process_course_count(message):
    try:
        chat_id = message.chat.id
        num_courses = int(message.text)
        if num_courses <= 0:
            bot.send_message(chat_id, "يرجى إدخال رقم صحيح (1 أو أكثر). حاول مجددًا.",reply_markup=keyboard1)
            return
        bot.send_message(chat_id, f"*الآن، سنبدأ اختيار التقديرات والساعات لكل مادة.*",parse_mode="Markdown")
        ask_for_grade(chat_id, num_courses, 0)
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال رقم صحيح.",reply_markup=keyboard1)

# عرض أزرار التقديرات للمستخدم
def ask_for_grade(chat_id, total_courses, current_course):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    grades = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"]
    buttons = [types.InlineKeyboardButton(text=grade, callback_data=f"grade_{grade}_{total_courses}_{current_course}") for grade in grades]
    keyboard.add(*buttons)
    
    bot.send_message(chat_id, f"📌 اختر تقدير المادة {current_course + 1}:", reply_markup=keyboard)

# استقبال اختيار التقديرات
@bot.callback_query_handler(func=lambda call: call.data.startswith("grade_"))
def handle_grade_selection(call):
    bot.answer_callback_query(call.id)  # تأكيد استقبال الضغط على الزر

    try:
        _, grade, total_courses, current_course = call.data.split("_")
        total_courses = int(total_courses)
        current_course = int(current_course)
        chat_id = call.message.chat.id

        if chat_id not in user_courses:
            user_courses[chat_id] = []

        # التأكد من تهيئة المادة الحالية بقيم افتراضية
        if len(user_courses[chat_id]) <= current_course:
            user_courses[chat_id].append({"grade": grade, "credit_hours": None})
        else:
            user_courses[chat_id][current_course]["grade"] = grade

        # طلب إدخال عدد الساعات بعد اختيار التقدير
        msg = bot.send_message(chat_id, f"📚 *ادخل عدد الساعات المعتمدة للمادة {current_course + 1}:*",parse_mode="Markdown")
        bot.register_next_step_handler(msg, handle_credit_hours, total_courses, current_course)

        # حذف رسالة الاختيار بعد التأكد من تسجيل البيانات
        bot.delete_message(chat_id, call.message.message_id)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ حدث خطأ: {str(e)}")


# استقبال عدد الساعات لكل مادة
def handle_credit_hours(message, total_courses, current_course):
    try:
        chat_id = message.chat.id
        credit_hours = int(message.text)
        if credit_hours <= 0:
            msg = bot.send_message(chat_id, "⚠️ يرجى إدخال رقم صحيح (1 أو أكثر) للساعات.",reply_markup=keyboard1)
            bot.register_next_step_handler(msg, handle_credit_hours, total_courses, current_course)
            return

        if chat_id in user_courses and len(user_courses[chat_id]) > current_course:
            user_courses[chat_id][current_course]["credit_hours"] = credit_hours
        else:
            bot.send_message(chat_id, "❌ خطأ: لم يتم العثور على بيانات المادة!",reply_markup=keyboard1)
            return

        if current_course + 1 < total_courses:
            ask_for_grade(chat_id, total_courses, current_course + 1)
        else:
            calculate_gpa(chat_id)

    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ يرجى إدخال رقم صحيح للساعات.",reply_markup=keyboard1)
        bot.register_next_step_handler(msg, handle_credit_hours, total_courses, current_course)

# حساب الـ GPA
def calculate_gpa(chat_id):
    grade_points = {
        "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0,
        "F": 0.0
    }

    courses = user_courses[chat_id]
    total_points = sum(grade_points[course["grade"]] * course["credit_hours"] for course in courses)
    total_hours = sum(course["credit_hours"] for course in courses)

    if total_hours == 0:
        bot.send_message(chat_id, "لا يمكن حساب الـ GPA لأن عدد الساعات المعتمدة يساوي 0.",reply_markup=keyboard1)
        return

    gpa = total_points / total_hours
    user_data[chat_id] = {"gpa": gpa, "hours": total_hours}  # حفظ المعدل الفصلي

    grades_summary = "\n".join([f"• {course['grade']} ({course['credit_hours']} ساعة)" for course in courses])
    message_text = f"📚 المواد التي تم اختيارها:\n{grades_summary}\n\n🎓 *المعدل الفصلي (GPA): {gpa:.3f}*\n\n📊 هل تريد إدخال بيانات لحساب **المعدل التراكمي (CGPA)**؟"
    keyboard = types.InlineKeyboardMarkup()
    cgpa_button = types.InlineKeyboardButton(text='إدخال المعدل التراكمي السابق',
    callback_data='enter_cgpa')
    cancel_button = types.InlineKeyboardButton(text='إلغاء', callback_data='cancel_cgpa')
    keyboard.row(cgpa_button)
    keyboard.row(cancel_button)
    bot.send_message(chat_id, message_text, parse_mode="Markdown", reply_markup=keyboard)


# استقبال إدخال CGPA أو الإلغاء
@bot.callback_query_handler(func=lambda call: call.data in ["enter_cgpa", "cancel_cgpa"])

def handle_cgpa_input(call):
    chat_id = call.message.chat.id
    if call.data == "enter_cgpa":
        # نطلب أولاً إدخال المعدل التراكمي السابق فقط
        bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="•🔢 *ادخل المعدل التراكمي السابق:*",parse_mode="Markdown"
        
    )
        bot.register_next_step_handler(call.message, save_prev_gpa)
    else:
        bot.delete_message(chat_id, call.message.message_id)

# حفظ المعدل التراكمي السابق
def save_prev_gpa(message):
    chat_id = message.chat.id
    try:
        prev_gpa = float(message.text)
        # حفظ المعدل السابق في بيانات المستخدم
        if chat_id not in user_data:
            user_data[chat_id] = {}
        user_data[chat_id]['prev_gpa'] = prev_gpa

        # الآن نطلب من المستخدم إدخال عدد الساعات السابقة
        bot.send_message(chat_id, "🔢 *ادخل عدد الساعات الكلية السابقة:*")
        bot.register_next_step_handler(message, save_prev_hours)
    except ValueError:
        bot.send_message(chat_id, "❌ الرجاء إدخال رقم صحيح للمعدل التراكمي.",reply_markup=keyboard1)
        bot.register_next_step_handler(message, save_prev_gpa)

# حفظ عدد الساعات السابقة وحساب الـ CGPA
def save_prev_hours(message):
    chat_id = message.chat.id
    try:
        prev_hours = float(message.text)
        if prev_hours <= 0:
            msg = bot.send_message(chat_id, "❌ عدد الساعات يجب أن يكون أكبر من 0. حاول مرة أخرى.", reply_markup=keyboard1)
            bot.register_next_step_handler(msg, save_prev_hours)
            return

        # حفظ عدد الساعات السابقة في بيانات المستخدم
        user_data.setdefault(chat_id, {})  # تأكد من أن القاموس موجود
        user_data[chat_id]['prev_hours'] = prev_hours

        # التحقق من وجود بيانات المعدل الفصلي
        required_keys = ['gpa', 'hours', 'prev_gpa', 'prev_hours']
        if not all(key in user_data[chat_id] for key in required_keys):
            bot.send_message(chat_id, "⚠️ لم يتم إدخال بيانات المعدل الفصلي. الرجاء إدخالها أولاً.", reply_markup=keyboard1)
            return

        # استرجاع بيانات المعدل الفصلي والتراكمي
        gpa = user_data[chat_id]["gpa"]
        hours = user_data[chat_id]["hours"]
        prev_gpa = user_data[chat_id]["prev_gpa"]

        # حساب المعدل التراكمي الجديد
        cgpa = ((prev_gpa * prev_hours) + (gpa * hours)) / (prev_hours + hours)

        # تحديد التقدير النهائي بناءً على المعدل التراكمي
        if cgpa == 4.0:
            gpa_evaluation = "ممتاز مرتفع"
        elif 3.7 <= cgpa < 4.0:
            gpa_evaluation = "ممتاز"
        elif 3.3 <= cgpa < 3.7:
            gpa_evaluation = "جيد جداً مرتفع"
        elif 3.0 <= cgpa < 3.3:
            gpa_evaluation = "جيد جداً"
        elif 2.7 <= cgpa < 3.0:
            gpa_evaluation = "جيد مرتفع"
        elif 2.3 <= cgpa < 2.7:
            gpa_evaluation = "جيد"
        elif 2.0 <= cgpa < 2.3:
            gpa_evaluation = "مقبول مرتفع"
        elif 1.7 <= cgpa < 2.0:
            gpa_evaluation = "مقبول"
        elif 1.3 <= cgpa < 1.7:
            gpa_evaluation = "مقبول مشروط مرتفع"
        elif 1.0 <= cgpa < 1.3:
            gpa_evaluation = "مقبول مشروط"
        elif 0.0 < cgpa < 1.0:
            gpa_evaluation = "راسب"
        else:
            gpa_evaluation = "غير محدد"

        # إرسال الرسالة بتفاصيل المعدل التراكمي
        message_text = (
            f"📊 *تفاصيل المعدل التراكمي (CGPA):*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *المعدل الفصلي (GPA):* `{gpa:.3f}`\n"
            f"📌 *عدد ساعات الفصل:* `{hours}` ساعة\n"
            f"📌 *المعدل التراكمي السابق:* `{prev_gpa:.2f}`\n"
            f"📌 *عدد الساعات السابقة:* `{prev_hours}` ساعة\n"
            f"📌 *المعدل التراكمي :* `{cgpa:.3f}`\n"
            f"📌 *التقدير التراكمي:* `{gpa_evaluation}`\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )

        bot.send_message(chat_id, message_text, parse_mode="Markdown", reply_markup=keyboard1)
        bot.send_message(
    admin_chat_id2, 
    f"👤 *الاسم:* {message.from_user.first_name}\n"
    f"🆔 *المعرف:* `{message.from_user.id}`\n"   
    f"{message_text}", 
    parse_mode="Markdown"
)

    except ValueError:
        msg = bot.send_message(chat_id, "❌ الرجاء إدخال رقم صحيح لعدد الساعات.", reply_markup=keyboard1)
        bot.register_next_step_handler(msg, save_prev_hours)
#_______________


def request_target_gpa(call):
    chat_id = call.message.chat.id
    
    # ✅ التحقق من الصلاحية باستخدام الدالة الجديدة
    if not check_button_permission(chat_id, "target_gpa"):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌* هذا الزر معطل حاليًا من قبل الأدمن.*",
            parse_mode="Markdown",
            reply_markup=keyboard3
        )
        return

    chat_id = call.message.chat.id
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text="🎯 *يرجى إدخال المعدل (GPA) الذي ترغب في الوصول إليه (يجب أن يكون بين 0 و 4):*",
        parse_mode="Markdown",
        reply_markup=keyboard1
    )

    bot.register_next_step_handler(call.message, process_target_gpa)
def process_current_hours(message, target_gpa, current_gpa):
    chat_id = message.chat.id
    try:
        current_hours = float(message.text)
        if current_hours <= 0:
            raise ValueError

        bot.send_message(chat_id, "📊 *أدخل عدد الساعات هذا الفصل*",parse_mode="Markdown")
        bot.register_next_step_handler(message, calculate_required_gpa, target_gpa, current_gpa, current_hours)
    except ValueError:
        bot.send_message(chat_id, "⚠️ خطأ! أدخل عدد ساعات صحيحًا (أكبر من 0).",reply_markup=keyboard1)
        bot.register_next_step_handler(message, process_current_hours, target_gpa, current_gpa)

def process_target_gpa(message):
    chat_id = message.chat.id
    try:
        target_gpa = float(message.text)
        if not (0 <= target_gpa <= 4):
            raise ValueError

        bot.send_message(chat_id, "🔢* أدخل معدلك التراكمي الحالي:*",parse_mode="Markdown")
        bot.register_next_step_handler(message, process_current_gpa, target_gpa)
    except ValueError:
        bot.send_message(chat_id, "⚠️ خطأ! أدخل معدلًا صحيحًا بين 0 و 4.",reply_markup=keyboard1)
        bot.register_next_step_handler(message, process_target_gpa)

def process_current_gpa(message, target_gpa):
    chat_id = message.chat.id
    try:
        current_gpa = float(message.text)
        if not (0 <= current_gpa <= 4):
            raise ValueError

        bot.send_message(chat_id, "📚 *أدخل عدد الساعات الكلية التي حصلت عليها*",parse_mode="Markdown")
        bot.register_next_step_handler(message, process_current_hours, target_gpa, current_gpa)
    except ValueError:
        bot.send_message(chat_id, "⚠️ خطأ! أدخل معدلًا صحيحًا بين 0 و 4.",reply_markup=keyboard1)
        bot.register_next_step_handler(message, process_current_gpa, target_gpa)


def calculate_required_gpa(message, target_gpa, current_gpa, current_hours):
    chat_id = message.chat.id
    try:
        semester_hours = float(message.text)
        if semester_hours <= 0:
            raise ValueError

        required_gpa = ((target_gpa * (current_hours + semester_hours)) - (current_gpa * current_hours)) / semester_hours

        if required_gpa > 4:
            bot.send_message(
                chat_id,
                "⚠️ من المستحيل الوصول إلى المعدل المستهدف في فصل واحد، حتى مع معدل 4.0.",
                reply_markup=keyboard1
            )
        elif required_gpa < 0:
            bot.send_message(
                chat_id,
                "✅* معدلك الحالي بالفعل أعلى من المعدل المستهدف!*",parse_mode="Markdown",
                reply_markup=keyboard1
            )
        else:
            message_text = (
    f"📊 *حساب المعدل المطلوب:*\n"
    f"━━━━━━━━━━━━━━━━━━━\n"
    f"📌 *المعدل التراكمي الحالي:* `{current_gpa:.2f}`\n"
    f"📚 *عدد الساعات الكلية :* `{current_hours}` ساعة\n"
    f"🆕 *عدد ساعات الفصل :* `{semester_hours}` ساعة\n"
    f"🎯 *المعدل المستهدف:* `{target_gpa}`\n"
    f"🔢 *المعدل المطلوب :* `{required_gpa:.2f}`\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
)


            bot.send_message(chat_id, message_text, parse_mode="Markdown",reply_markup=keyboard3)
            
            bot.send_message(
    admin_chat_id2, 
    f"👤 *الاسم:* {message.from_user.first_name}\n"
    f"🆔 *المعرف:* `{message.from_user.id}`\n"   
    f"{message_text}", 
    parse_mode="Markdown"
)


    except ValueError:
        bot.send_message(
            chat_id,
            "⚠️ خطأ! أدخل عدد ساعات صحيحًا (أكبر من 0)."
        )
        bot.register_next_step_handler(message, calculate_required_gpa, target_gpa, current_gpa, current_hours)
  #زر الرجوع الي لوحة الادمن ______
  
def get_back_button():

    keyboard = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton("🔙 الرجوع إلى لوحة الأدمن", callback_data="back_to_admin")
    keyboard.add(btn_back)
    return keyboard
@bot.callback_query_handler(func=lambda call: call.data == "back_to_admin")
def back_to_admin_menu(call):
    chat_id = call.message.chat.id

    if str(chat_id) not in [str(admin_chat_id), str(admin_chat_id2)]:
        bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية لاستخدام هذا الأمر.")
        return

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text="🎩 *مرحبًا أيها الأدمن! يمكنك استخدام لوحة التحكم أدناه:*",
        parse_mode="Markdown",
        reply_markup=get_admin_keyboard()
    )
   
      
          

# 📌 أمر حظر مستخدم
def process_ban(message):
    user_id = message.text.strip()

    if not user_id.isdigit():
        bot.reply_to(message, "❌ يرجى إدخال رقم ID صالح.",reply_markup=get_back_button())
        return

    with open("ban.txt", "a") as file:
        file.write(user_id + "\n")

    bot.send_message(user_id, "🚫 *تم حظرك من البوت.*\n🔹 إذا كنت تعتقد أن هناك خطأ، يرجى التواصل مع المطور.", parse_mode="Markdown",reply_markup=keyboard3)
    bot.reply_to(message, f"✅ تم حظر المستخدم `{user_id}` بنجاح.", parse_mode="Markdown",reply_markup=get_back_button())

# 📌 أمر فك حظر مستخدم
def process_unban(message):
    user_id = message.text.strip()

    if not user_id.isdigit():
        bot.reply_to(message, "❌ يرجى إدخال رقم ID صالح.",reply_markup=get_back_button())
        return

    if not os.path.exists("ban.txt"):
        bot.reply_to(message, "❌ لا يوجد مستخدمون محظورون.",reply_markup=get_back_button())
        return

    with open("ban.txt", "r") as file:
        lines = file.readlines()

    with open("ban.txt", "w") as file:
        found = False
        for line in lines:
            if line.strip() != user_id:
                file.write(line)
            else:
                found = True

    if found:
        bot.send_message(user_id, "✅ *تم إلغاء حظرك من البوت، يمكنك استخدامه الآن.*", parse_mode="Markdown",reply_markup=keyboard3)
        bot.reply_to(message, f"✅ تم إلغاء حظر المستخدم `{user_id}` بنجاح.", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ المستخدم غير موجود في قائمة المحظورين.",reply_markup=get_back_button())

# 📌 أمر الإحصائيات
import glob  
def stats(message):
    total_users = 0
    banned_users = 0
    files_to_send = []

    # ✅ التحقق من وجود ملف المستخدمين
    if os.path.exists("Users.txt"):
        with open("Users.txt", "r") as f:
            total_users = len(f.readlines())
        files_to_send.append("Users.txt")
    else:
        bot.send_message(message.chat.id, "⚠️ لا يوجد مستخدمون مسجلون بعد.", parse_mode="Markdown")
        
    if os.path.exists("ids.txt"):
        with open("ids.txt", "r") as f:
            total_users = len(f.readlines())
        files_to_send.append("ids.txt")
    else:
        bot.send_message(message.chat.id, "⚠️ لا يوجد مستخدمون مسجلون بعد.", parse_mode="Markdown")

    # ✅ التحقق من وجود ملف المحظورين
    if os.path.exists("ban.txt"):
        with open("ban.txt", "r") as f:
            banned_users = len(f.readlines())
        files_to_send.append("ban.txt")
    else:
        bot.send_message(message.chat.id, "⚠️ لا يوجد مستخدمون محظورون بعد.", parse_mode="Markdown")

    # ✅ البحث عن جميع ملفات `studentSemProg.txt` وإضافتها إلى `files_to_send`
    student_files = glob.glob("*.txt")  # جلب جميع الملفات النصية في المجلد الحالي
    for file in student_files:
        if file not in ["Users.txt", "ids.txt", "ban.txt"]:  # استبعاد الملفات الأخرى
            files_to_send.append(file)

    # ✅ إرسال الإحصائيات
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=f"📊 *إحصائيات البوت:*\n"
             f"👤 *عدد المستخدمين:* `{total_users}`\n"
             f"🚫 *عدد المحظورين:* `{banned_users}`",
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )

    # ✅ إرسال الملفات إذا كانت موجودة
    for file in files_to_send:
        try:
            with open(file, "rb") as doc:
                bot.send_document(message.chat.id, doc)
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ خطأ في إرسال الملف {file}: {str(e)}")



# 📌 أمر الإذاعة
def process_broadcast_media(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"message": message}

    keyboard = types.InlineKeyboardMarkup()
    forward_button = types.InlineKeyboardButton("📤 توجيه الرسالة", callback_data="broadcast_forward")
    send_new_button = types.InlineKeyboardButton("📝 إرسال كرسالة جديدة", callback_data="broadcast_new")
    keyboard.add(forward_button, send_new_button)

    bot.send_message(chat_id, "⚡ هل تريد توجيه الرسالة كما هي أم إرسالها كرسالة جديدة؟", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in ["broadcast_forward", "broadcast_new"])
def handle_broadcast_type(call):
    chat_id = call.message.chat.id
    message = user_data.get(chat_id, {}).get("message")
    if not message:
        bot.answer_callback_query(call.id, "❌ لم يتم العثور على الرسالة!")
        return

    if call.data == "broadcast_forward":
        send_forward_broadcast(chat_id, message)
    else:
        send_new_broadcast(chat_id, message)


def send_forward_broadcast(chat_id, message):
    global stop_broadcasting
    stop_broadcasting = False

    sent_count, failed_count = 0, 0

    try:
        with open("ids.txt", "r", encoding="utf-8", errors="ignore") as f:
            user_ids = f.read().splitlines()
    except FileNotFoundError:
        bot.send_message(chat_id, "❌ لا يوجد مستخدمون مسجلون.")
        return

    progress_msg = bot.send_message(
        chat_id,
        "📢 *جاري إرسال الإذاعة الموجهة...*\n✅ *ناجحة:* `0`\n❌ *فاشلة:* `0`",
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )

    for i, user_id in enumerate(user_ids, 1):
        if stop_broadcasting:
            bot.edit_message_text(
                chat_id=progress_msg.chat.id,
                message_id=progress_msg.message_id,
                text="⏹️ *تم إيقاف الإذاعة من قبل الأدمن.*",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )
            return

        try:
            bot.forward_message(user_id, chat_id, message.message_id)
            sent_count += 1
        except telebot.apihelper.ApiTelegramException as e:
            if e.error_code == 429:  # Too Many Requests
                retry_after = int(re.search(r'retry after (\d+)', str(e)).group(1))
                time.sleep(retry_after + 1)
            else:
                failed_count += 1
        except Exception:
            failed_count += 1

        # تحديث التقدم كل 5 رسائل
        if i % 5 == 0 or i == len(user_ids):
            try:
                bot.edit_message_text(
                    chat_id=progress_msg.chat.id,
                    message_id=progress_msg.message_id,
                    text=f"📢 *تحديث الإذاعة:*\n✅ *ناجحة:* `{sent_count}`\n❌ *فاشلة:* `{failed_count}`",
                    parse_mode="Markdown",
                    reply_markup=get_back_button()
                )
            except:
                pass

        time.sleep(0.05)  # تأخير لتجنب الحظر

    bot.edit_message_text(
        chat_id=progress_msg.chat.id,
        message_id=progress_msg.message_id,
        text=f"✅ *تم الانتهاء من الإذاعة الموجهة!*\n\n📢 *إجمالي:* {len(user_ids)}\n✅ *ناجحة:* {sent_count}\n❌ *فاشلة:* {failed_count}",
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )


def send_new_broadcast(chat_id, message):
    global stop_broadcasting
    stop_broadcasting = False

    sent_count, failed_count = 0, 0

    try:
        with open("ids.txt", "r", encoding="utf-8", errors="ignore") as f:
            user_ids = f.read().splitlines()
    except FileNotFoundError:
        bot.send_message(chat_id, "❌ لا يوجد مستخدمون مسجلون.")
        return

    progress_msg = bot.send_message(
        chat_id,
        "📢 *جاري إرسال الإذاعة...*\n✅ *ناجحة:* `0`\n❌ *فاشلة:* `0`",
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )

    for i, user_id in enumerate(user_ids, 1):
        if stop_broadcasting:
            bot.edit_message_text(
                chat_id=progress_msg.chat.id,
                message_id=progress_msg.message_id,
                text="⏹️ *تم إيقاف الإذاعة من قبل الأدمن.*",
                parse_mode="Markdown",
                reply_markup=get_back_button()
            )
            return

        try:
            if message.text:
                bot.send_message(user_id, message.text)
            elif message.photo:
                bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption or "")
            elif message.video:
                bot.send_video(user_id, message.video.file_id, caption=message.caption or "")
            elif message.document:
                bot.send_document(user_id, message.document.file_id, caption=message.caption or "")
            elif message.audio:
                bot.send_audio(user_id, message.audio.file_id, caption=message.caption or "")
            elif message.voice:
                bot.send_voice(user_id, message.voice.file_id, caption=message.caption or "")
            sent_count += 1

        except telebot.apihelper.ApiTelegramException as e:
            if e.error_code == 429:
                retry_after = int(re.search(r'retry after (\d+)', str(e)).group(1))
                time.sleep(retry_after + 1)
            else:
                failed_count += 1
        except Exception:
            failed_count += 1

        # تحديث كل 5 رسائل
        if i % 5 == 0 or i == len(user_ids):
            try:
                bot.edit_message_text(
                    chat_id=progress_msg.chat.id,
                    message_id=progress_msg.message_id,
                    text=f"📢 *تحديث الإذاعة:*\n✅ *ناجحة:* `{sent_count}`\n❌ *فاشلة:* `{failed_count}`",
                    parse_mode="Markdown",
                    reply_markup=get_back_button()
                )
            except:
                pass

        time.sleep(0.05)  # تأخير لتجنب الحظر

    bot.edit_message_text(
        chat_id=progress_msg.chat.id,
        message_id=progress_msg.message_id,
        text=f"✅ *تم الانتهاء من الإذاعة!*\n\n📢 *إجمالي:* {len(user_ids)}\n✅ *ناجحة:* {sent_count}\n❌ *فاشلة:* {failed_count}",
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )

# ملف تخزين الرسائل
MESSAGES_FILE = "user_messages.json"

def load_user_messages():
    """تحميل الرسائل المحفوظة من الملف"""
    try:
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user_messages(messages_dict):
    """حفظ الرسائل إلى الملف"""
    with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(messages_dict, f, ensure_ascii=False, indent=4)

# تحميل الرسائل عند بدء التشغيل
user_messages = load_user_messages()
# ================ نهاية الإضافة ================
@bot.message_handler(
    func=lambda message: message.chat.id != admin_chat_id2, 
    content_types=['text', 'photo', 'document', 'video', 'voice', 'audio', 'sticker', 'animation']
)
def forward_messages_to_admin(message):
    chat_id = message.chat.id
    welcome(message)  # استدعاء رسالة الترحيب إذا لزم الأمر

    # حفظ الرسالة الأصلية في الذاكرة والملف
    user_messages[str(message.message_id)] = str(chat_id)
    save_user_messages(user_messages)  # حفظ في الملف
    
    # إعادة توجيه جميع الرسائل (النصوص + المرفقات) إلى الأدمن كما هي
    sent_message = bot.forward_message(admin_chat_id2, chat_id, message.message_id)

    # حفظ الرسالة المعاد توجيهها في الذاكرة والملف
    user_messages[str(sent_message.message_id)] = str(chat_id)
    save_user_messages(user_messages)  # حفظ في الملف

# 📌 تمكين الأدمن من الرد مباشرة إلى المستخدم
@bot.message_handler(func=lambda message: message.reply_to_message and message.chat.id == admin_chat_id2 and not message.text.startswith('/info'))
def reply_to_user(message):
    original_message = message.reply_to_message
    user_id = None
    
    # محاولة 1: البحث في الذاكرة الحالية
    user_id = user_messages.get(str(original_message.message_id))
    
    # محاولة 2: إذا لم يكن في الذاكرة، تحميل من الملف
    if not user_id:
        saved_messages = load_user_messages()  # تحميل من الملف
        user_id = saved_messages.get(str(original_message.message_id))
        
        # إذا وجد في الملف، تحديث الذاكرة
        if user_id:
            user_messages[str(original_message.message_id)] = user_id

    if user_id:
        try:
            text = message.text  # استخدم النص بدون تعديل
            bot.send_message(int(user_id), text, parse_mode="HTML")  # تحويل إلى int
        except Exception as e:
            error_message = f"⚠️ خطأ أثناء إرسال الرسالة إلى المستخدم: {str(e)}"
            bot.send_message(admin_chat_id2, error_message, parse_mode="HTML")
    else:
        bot.send_message(admin_chat_id2, "❌ *تعذر العثور على المستخدم للرد عليه.*", parse_mode="Markdown")

##معلومات المستخدم__________   

@bot.message_handler(commands=['info'])
def send_user_info(message):
    if message.reply_to_message and message.chat.id == admin_chat_id2:
        original_message = message.reply_to_message
        user_id = None

        # المحاولة 1: إذا كانت الرسالة معاد توجيهها
        if original_message.forward_from:  
            user_id = original_message.forward_from.id
        
        # المحاولة 2: البحث في قاعدة البيانات المحفوظة
        elif str(original_message.message_id) in user_messages:  
            user_id = user_messages[str(original_message.message_id)]
        
        # المحاولة 3: إذا فشل كل شيء، جرب تحميل من الملف
        elif not user_id:
            saved_messages = load_user_messages()
            user_id = saved_messages.get(str(original_message.message_id))
            if user_id:
                # تحديث الذاكرة الحالية
                user_messages[str(original_message.message_id)] = user_id
        
        # المحاولة 4: مرسل الرسالة نفسه (إذا كان الأدمن يتحدث مع البوت)
        if not user_id and original_message.from_user:  
            user_id = original_message.from_user.id

        # التحقق إذا كان البوت نفسه
        if user_id and str(user_id) == str(bot.get_me().id):
            bot.send_message(
                admin_chat_id2, 
                "❌ *هذه الرسالة مرسلة من البوت نفسه، لا يمكن جلب بياناته.*", 
                parse_mode="Markdown"
            )
            return

        # التحقق مما إذا لم يتم العثور على `user_id`
        if not user_id:
            bot.send_message(
                admin_chat_id2, 
                "❌ *تعذر العثور على معرف المستخدم:*\n"
                "• ربما قام المستخدم بإغلاق إعادة التوجيه\n"
                "• أو هذه الرسالة قديمة جداً\n"
                "• أو الرسالة من قناة/مجموعة", 
                parse_mode="Markdown"
            )
            return

        try:
            # جلب بيانات المستخدم
            user_info = bot.get_chat(int(user_id))

            # جلب السيرة الذاتية (bio) إن وجدت
            user_bio = user_info.bio if hasattr(user_info, 'bio') and user_info.bio else "لا يوجد"

            # التحقق مما إذا كان المستخدم قد حظر البوت
            is_blocked = False
            bot_status = "✅"
            try:
                bot.send_chat_action(int(user_id), 'typing')
            except Exception as e:
                if "bot was blocked" in str(e).lower() or "user is deactivated" in str(e).lower():
                    is_blocked = True
                    bot_status = "❌"

            # إرسال معلومات المستخدم للأدمن
            info_text = (
                f"ℹ️ *تفاصيل المستخدم:*\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"👤 | *اسم المستخدم:* ➢ {user_info.first_name} {user_info.last_name or ''}\n"
                f"ℹ️ | *معرف المستخدم:* `{user_info.id}`\n"
                f"📍 | *المعرف:* {f'@{user_info.username}' if user_info.username else 'لا يوجد'}\n"
                f"🏵 | *السيرة الذاتية:* {user_bio}\n"
                f"🌀 | *حالة المستخدم:* {'❌ محظور' if is_blocked else '✅ غير محظور'}\n"
                f"🎗 | *حالة عمل البوت مع المستخدم:* {bot_status}\n"
                f"━━━━━━━━━━━━━━━━━━━"
            )
            
            bot.send_message(admin_chat_id2, info_text, parse_mode="Markdown")

        except Exception as e:
            error_msg = str(e)
            if "chat not found" in error_msg.lower():
                bot.send_message(
                    admin_chat_id2, 
                    f"❌ *تعذر العثور على المستخدم:*\n"
                    f"• ربما قام بحذف حسابه\n"
                    f"• أو قام بحظر البوت\n"
                    f"• أو المعرف غير صحيح", 
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(
                    admin_chat_id2, 
                    f"⚠️ خطأ أثناء جلب بيانات المستخدم:\n`{error_msg[:100]}`", 
                    parse_mode="Markdown"
                )

    else:
        bot.send_message(
            admin_chat_id2, 
            "❌ *يجب الرد على رسالة المستخدم ثم كتابة /info للحصول على المعلومات.*", 
            parse_mode="Markdown"
        )
@bot.callback_query_handler(func=lambda call: call.data == "send_user1")
def handle_send_user(call):
    bot.clear_step_handler(call.message)  
    send_user_message_command(call)  # تمرير `call` وليس `call.message`

def send_user_message_command(call):
    chat_id = call.message.chat.id

    if str(chat_id) != str(admin_chat_id):  # تأكد من أن المستخدم هو الأدمن
        bot.send_message(chat_id, "❌ ليس لديك صلاحية لاستخدام هذا الأمر.", reply_markup=keyboard1)
        return

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,  # استخدم call.message.message_id مباشرة
        text="✍️ *أدخل معرف المستخدم الذي تريد إرسال رسالة إليه:*",
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )

    bot.register_next_step_handler(call.message, get_user_id_for_message)  # استخدم call.message هنا


def get_user_id_for_message(message):
    chat_id = message.chat.id
    user_id = message.text.strip()

    if not user_id.isdigit():
        bot.send_message(chat_id, "❌ *يرجى إدخال معرف مستخدم صالح (أرقام فقط).*", parse_mode="Markdown",reply_markup=get_back_button())
        return

    bot.send_message(chat_id, f"✅ تم إدخال المعرف: {user_id}\n📩 *أدخل الرسالة التي تريد إرسالها:*", parse_mode="Markdown",reply_markup=get_back_button())
    bot.register_next_step_handler(message, send_message_to_user, user_id)

def send_message_to_user(message, user_id):
    
    try:
        bot.send_message(int(user_id), f"{message.text}")
        bot.send_message(message.chat.id, "✅ *تم إرسال الرسالة بنجاح.*", parse_mode="Markdown",reply_markup=get_back_button())
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ *حدث خطأ أثناء إرسال الرسالة: {str(e)}*", parse_mode="Markdown",reply_markup=get_back_button())
#اشعارظهور النتيجة
STATUS_FILE = "status.json"
admin_chat_id = 1792449471
# تحميل حالة الإشعارات من الملف
def load_status():
    try:
        with open(STATUS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"notifications_enabled": True}

# حفظ حالة الإشعارات
def save_status(status):
    with open(STATUS_FILE, "w") as file:
        json.dump(status, file, indent=4)




result_checking_thread = None  # متغير لتخزين حالة العملية

@bot.callback_query_handler(func=lambda call: call.data == "toggle_notifications")
def toggle_notifications(call):
    global result_checking_thread  # السماح بتعديل المتغير خارج الدالة
    
    if call.message.chat.id != admin_chat_id:
        bot.answer_callback_query(call.id, "❌ ليس لديك صلاحية لاستخدام هذا الأمر.")
        return

    status = load_status()
    status["notifications_enabled"] = not status["notifications_enabled"]
    save_status(status)

    notifications_status = "🔔 الإشعارات: ✅ مفعلة" if status["notifications_enabled"] else "🔕 الإشعارات: ❌ متوقفة"

    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=get_admin_keyboard()
    )

    bot.answer_callback_query(call.id, f"🔔 {'تم تشغيل الإشعارات ✅' if status['notifications_enabled'] else 'تم إيقاف الإشعارات ❌'}")

    # تشغيل البحث عند تفعيل الإشعارات إذا لم يكن يعمل
    if status["notifications_enabled"] and (result_checking_thread is None or not result_checking_thread.is_alive()):
        start_result_checking()

current_cookie = get_current_cookie()
cookies = {
            "userID": current_cookie
        }
URL = "http://credit.minia.edu.eg/getJCI"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "http://credit.minia.edu.eg/static/PortalStudent.html",
  

}
PAYLOAD = {
    "param0": "Reports.RegisterCert",
    "param1": "getTranscript",
    "param2": '{"crsReplaceHide":"true","ShowDetails":"true","portalFlag":"true","RegType":"student","AppType":"result"}'
}

# جلب النتيجة
def get_result():
    try:
        # استخدام الكوكيز الثابتة
        current_cookie = get_current_cookie()
        if not current_cookie:
            return None
        
        cookies = {
            "userID": current_cookie
        }
        
        # جلب البيانات باستخدام الكوكيز الثابتة
        response = requests.post(URL, headers=HEADERS, data=PAYLOAD, cookies=cookies, timeout=40)
        response.raise_for_status()
        
        # تحليل البيانات JSON
        try:
            data2 = response.json()
        except:
            return None

        # التحقق من وجود بيانات الفصول الدراسية
        if "StuSemesterData" not in data2 or not data2["StuSemesterData"]:
            return None

        # الحصول على آخر سنة دراسية (الأحدث)
        last_year = data2["StuSemesterData"][-1]
        
        # الحصول على آخر فصل دراسي (الأحدث)
        if "Semesters" not in last_year or not last_year["Semesters"]:
            return None
            
        last_semester = last_year["Semesters"][-1]
        
        # التحقق من وجود GPA في الفصل الأخير (الأحدث)
        semester_gpa = last_semester.get("GPA", "").strip()
        
        # إذا كان GPA الفصل الأخير غير موجود أو صفر، فهذا يعني النتيجة لم تظهر بعد
        # لا نبحث عن فصول سابقة، ننتظر فقط ظهور نتيجة الفصل الأخير
        if not semester_gpa or semester_gpa == "0":
            return None  # النتيجة لم تظهر بعد

        # استخراج معلومات الفصل الأخير
        semester_name = last_semester.get("SemesterName", "").strip()
        acad_year_name = last_year.get("AcadYearName", "").strip()
        full_semester_name = f"{acad_year_name} - {semester_name}"
        
        cumulative_gpa = last_semester.get("CurrGPA", "").strip()
        
        # التحقق من وجود النسبة المئوية
        accum_perc = last_semester.get("AccumPerc", "").strip()
        curr_perc = last_semester.get("CurrPerc", "").strip()
        
        # إنشاء رسالة الإشعار للمستخدمين
        message = (
            f"🎉 *ظهرت النتيجة الجديدة!*\n\n"
            f"📅 *الفصل الدراسي:* {full_semester_name}\n"
            f"📊 *معدل الفصل:* {semester_gpa}\n"
            f"🏆 *المعدل التراكمي:* {cumulative_gpa}\n"
        )
        
        if accum_perc and accum_perc != "0":
            message += f"📈 *النسبة التراكمية:* {accum_perc}%\n"
        
        if curr_perc and curr_perc != "0":
            message += f"📊 *نسبة الفصل:* {curr_perc}%\n"
        
        message += f"\n🏫 *يمكنك الآن الحصول على نتيجتك الكاملة من خلال البوت.*"
        
        # إرسال تفاصيل الفصل للأدمن
        admin_message = (
            f"🔔 *إشعار ظهور نتيجة جديدة*\n\n"
            f"📊 *تفاصيل الفصل الذي تم التحقق منه:*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 *السنة الدراسية:* {acad_year_name}\n"
            f"📚 *الفصل:* {semester_name}\n"
            f"📈 *GPA الفصل:* {semester_gpa}\n"
            f"🏆 *GPA التراكمي:* {cumulative_gpa}\n"
        )
        
        if accum_perc and accum_perc != "0":
            admin_message += f"📊 *النسبة التراكمية:* {accum_perc}%\n"
        
        if curr_perc and curr_perc != "0":
            admin_message += f"📈 *نسبة الفصل:* {curr_perc}%\n"
        
        admin_message += f"━━━━━━━━━━━━━━━━━━━━\n"
        admin_message += f"⏰ *الوقت:* {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        admin_message += f"✅ *تم الكشف عن نتيجة الفصل الأخير وإرسال الإشعارات*"
        
        # إرسال الرسالة للأدمن
        try:
            bot.send_message(admin_chat_id2, admin_message, parse_mode="Markdown")
        except:
            pass  # تجاهل الخطأ إذا لم يتمكن من الإرسال
        
        return message
        
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.RequestException:
        return None
    except json.JSONDecodeError:
        return None
    except KeyError:
        return None
    except Exception:
        return None
# تحميل قائمة المستخدمين
def load_users():
    try:
        with open("ids.txt", "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# إرسال إشعار ظهور النتيجة للمستخدمين

def send_notifications(result_message):
    users = load_users()
    sent_count, failed_count = 0, 0

    # إرسال رسالة أولية للأدمن لمتابعة التقدم
    progress_msg = bot.send_message(
        admin_chat_id,
        "\U0001F4E2 *جاري إرسال إشعار للمستخدمين...*\n✅ *ناجحة:* `0`\n❌ *فاشلة:* `0`",
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )

    def send_message(user_id):
        nonlocal sent_count, failed_count
        try:
            bot.send_message(
    user_id,
    "\U0001F4E2 • *النتيجة ظهرت الآن ✅*\n"
    "\U0001F393 • يمكنك الآن الحصول على نتيجتك من خلال البوت أو الموقع الرسمي.\n\n",
    parse_mode="Markdown",
    reply_markup=keyboard3
)


            sent_count += 1
            return True
        except Exception:
            failed_count += 1
            return False

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(send_message, user_id): user_id for user_id in users}
        total = len(users)

        for i, future in enumerate(as_completed(futures), 1):
            try:
                future.result()  # الحصول على نتيجة التنفيذ لرصد أي استثناء
            except Exception as e:
                print(f"Error sending message: {e}")

            # تحديث الرسالة أثناء التقدم، لكن لا تحدثها إذا كان هذا هو التحديث الأخير
            if i % 2 == 0 and i < total:
                try:
                    bot.edit_message_text(
                        chat_id=progress_msg.chat.id,
                        message_id=progress_msg.message_id,
                        text=f"\U0001F4E2 *جاري إرسال إشعار ظهور النتيجة للمستخدمين...*\n✅ *ناجحة:* `{sent_count}`\n❌ *فاشلة:* `{failed_count}`",
                        parse_mode="Markdown",reply_markup=get_back_button())
                except Exception:
                    pass  
    
    # بعد انتهاء جميع المهام، تحديث الرسالة النهائية
    bot.edit_message_text(
        chat_id=progress_msg.chat.id,
        message_id=progress_msg.message_id,
        text=f"\U0001F389 *تم الانتهاء من إرسال الإشعارات!*\n\n✅ *ناجحة:* `{sent_count}`\n❌ *فاشلة:* `{failed_count}`\n\nشكراً لاستخدام البوت!",
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )




# التحقق المتكرر  ظهور النتيجة
def check_results():
    attempts = 0
    while True:
        status = load_status()

        if not status["notifications_enabled"]:
            print("🔕 الإشعارات متوقفة، تم إنهاء عملية التحقق.")
            break  

        attempts += 1
        print(f"\033[32mAttempt {attempts}: Checking if the result is available...\033[0m")

        result_message = get_result()
        if result_message:
            print(f"✅ النتيجة ظهرت بعد {attempts} محاولات، يتم إرسالها للمستخدمين...")
            send_notifications(result_message)
            break  
        time.sleep(60)  

def start_result_checking():
    global result_checking_thread  # السماح بتعديل المتغير خارج الدالة
    if result_checking_thread is None or not result_checking_thread.is_alive():
        result_checking_thread = threading.Thread(target=check_results, daemon=True)
        result_checking_thread.start()

if load_status()["notifications_enabled"]:
    start_result_checking()

#معرفة الحروف الكابتل من الاسمول ______
import itertools
LOGIN_URL = "http://credit.minia.edu.eg/studentLogin"
char_variations = {
    "i": ("i", "I", "j", "l", "J", "L"),
    "j": ("i", "I", "j", "l", "J", "L"),
    "l": ("i", "I", "j", "l", "J", "L"),
}

user_data = {}
attempt_locks = {}
found_event = threading.Event()  
correct_password = None  

def generate_password_variations(password):
    possible_replacements = [
        (char.lower(), char.upper()) if char.isalpha() else (char,)
        for char in password
    ]
    return ["".join(variant) for variant in itertools.product(*possible_replacements)]

def apply_char_variations(password_list):
    final_variations = set()
    for password in password_list:
        variation_positions = [i for i, char in enumerate(password) if char in char_variations]
        replacement_options = [
            char_variations[password[i]] if i in variation_positions else (password[i],)
            for i in range(len(password))
        ]
        for variant in itertools.product(*replacement_options):
            final_variations.add("".join(variant))
    return list(final_variations)

@bot.callback_query_handler(func=lambda call: call.data == "try_login")
def start_message(call):
    chat_id = call.message.chat.id
    
    # ✅ التحقق من الصلاحية باستخدام الدالة الجديدة
    if not check_button_permission(chat_id, "try_login"):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌* هذا الزر معطل حاليًا من قبل الأدمن.*",
            parse_mode="Markdown",
            reply_markup=keyboard3
        )
        return
    


    bot.edit_message_text(
        chat_id=call.message.chat.id, 
        message_id=call.message.message_id, 
        text="🆔 أدخل *اسم المستخدم* (يجب أن يكون أرقامًا فقط):", 
        parse_mode="Markdown",
        reply_markup=keyboard1
    )

    bot.register_next_step_handler(call.message, get_username)

def get_username(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "⚠️ يجب أن يكون اسم المستخدم أرقامًا فقط! أعد المحاولة.",reply_markup=keyboard1)
        
    else:
        user_data[message.chat.id] = {"username": message.text}
        bot.send_message(message.chat.id, "أدخل *كلمة المرور* (يجب أن تبدأ بـ 4 أحرف ثم 3 ارقام ثم علامة ):", parse_mode="Markdown")
        bot.register_next_step_handler(message, get_password)

def get_password(message):
    password = message.text

    # التحقق من أن كلمة المرور تحتوي على 4 أحرف في البداية فقط
    if len(password) < 4 or not password[:4].isalpha():
        bot.send_message(message.chat.id, 
                 "❌ *كلمة المرور غير صحيحة!*\n"
                 "🔹 يجب أن تبدأ بـ *4 أحرف*\n"
                 "🔹 من المحتمل أن كلمة المرور التي أدخلتها *تخص منصة الكتب* وليس *موقع ابن الهيثم*.", 
                 parse_mode="Markdown",reply_markup=keyboard1)
        return
    
    # التحقق من عدم وجود أكثر من 4 أحرف في البداية
    if len(password) > 4 and password[4].isalpha():
        bot.send_message(message.chat.id, 
                 "❌ *كلمة المرور غير صحيحة!*\n"
                 "🔹 يجب أن تبدأ بـ *4 أحرف*\n"
                 "", 
                 parse_mode="Markdown",reply_markup=keyboard1)
        return

        
    else:
        user_data[message.chat.id]["password"] = password
        msg = bot.send_message(message.chat.id, "🔍* جاري تجربة كلمات المرور...*\n🔢 المحاولات: 0", parse_mode="Markdown")
        attempt_locks[message.chat.id] = threading.Lock()
        found_event.clear()  
        threading.Thread(target=login_attempt, args=(message.chat.id, msg)).start()

def login_attempt(chat_id, msg):
    global correct_password 

    username = user_data[chat_id]["username"]
    base_password = user_data[chat_id]["password"]

    case_variations = generate_password_variations(base_password)
    all_password_variations = apply_char_variations(case_variations)

    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36",
        'X-Requested-With': "XMLHttpRequest",
        'Origin': "http://credit.minia.edu.eg",
        'Referer': "http://credit.minia.edu.eg/static/index.html",
    }

    attempt_count = 0
    threads = []

    def try_password(password):
        nonlocal attempt_count
        global correct_password 
        if found_event.is_set(): 
            return

        with attempt_locks[chat_id]:
            if found_event.is_set():
                return
            attempt_count += 1

            if not found_event.is_set():
                try:
                    bot.edit_message_text(f"🔍 جاري تجربة كلمات المرور...\n🔢 المحاولات: {attempt_count}", 
                                          chat_id, msg.message_id, parse_mode="Markdown")
                except:
                    pass  

        payload = {
            'UserName': username,
            'Password': password,
            'sysID': "313.",
            'UserLang': "E",
            'userType': "2"
        }

        try:
            response = requests.post(LOGIN_URL, data=payload, headers=headers, timeout=40)
            data = response.json()
            login_ok = data.get("rows", [{}])[0].get("row", {}).get("LoginOK", "False")

            if login_ok == "True":
                if not found_event.is_set():
                    found_event.set()  
                    correct_password = password  

        except:
            pass

    for password in all_password_variations:
        if found_event.is_set():  
            break
        thread = threading.Thread(target=try_password, args=(password,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    if found_event.is_set():  
        if correct_password:  
            try:
                bot.edit_message_text(f"✅ تم تسجيل الدخول بنجاح!\n👤 اسم المستخدم: `{username}`\n🔑 كلمة المرور: `{correct_password if correct_password else 'لم يتم تخزينها بشكل صحيح'}`", 
                      chat_id, msg.message_id, parse_mode="Markdown",reply_markup=keyboard1)

            except:
                pass
        else:
            try:
                bot.edit_message_text(f"✅ تم تسجيل الدخول بنجاح!\n👤 اسم المستخدم: `{username}`\n🔑 كلمة المرور: `{correct_password if correct_password else 'لم يتم تخزينها بشكل صحيح'}`", 
                      chat_id, msg.message_id, parse_mode="Markdown",reply_markup=keyboard1)
            except:
                pass
        return

    bot.edit_message_text(f"⛔ لم يتم العثور على كلمة المرور الصحيحة بعد {attempt_count} محاولة.\nتأكد من البيانات وأعد المحاولة.", 
                          chat_id, msg.message_id, parse_mode="Markdown",reply_markup=keyboard1)

#تحميل صورة الطالب __________________

# أولاً: تعريف الدوال المساعدة (يجب أن تكون في بداية الملف بعد الاستيرادات)
if not os.path.exists("tmp"):
    os.makedirs("tmp")

def clean_old_images(folder='tmp', age_limit=3600):
    now = time.time()
    for filename in os.listdir(folder):
        if filename.endswith('.png'):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                if now - os.path.getmtime(filepath) > age_limit:
                    try:
                        os.remove(filepath)
                    except:
                        pass  # تجاهل أي خطأ في الحذف

def delete_file_after_delay(file_path, delay_seconds):
    def delete_file():
        if os.path.exists(file_path):
            os.remove(file_path)
    threading.Timer(delay_seconds, delete_file).start()

def delete_message_after_delay(bot, chat_id, message_id, delay_seconds):
    def delete_message():
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
    threading.Timer(delay_seconds, delete_message).start()

# ثانياً: تعريف دالة download_image
def download_image(chat_id, image_url, message_id, message, bot, student_id):
    clean_old_images()

    filename = f"tmp/{student_id}.png"

    loading_message = bot.send_message(
        chat_id,
        "⏳ *جاري تحميل الصورة يرجى الانتظار...*",
        parse_mode="Markdown",
        reply_to_message_id=message_id
    )

    try:
        response = requests.get(image_url, stream=True, timeout=15)

        if response.status_code == 200 and int(response.headers.get('Content-Length', 0)) >= 1024:
            with open(filename, "wb") as file:
                for chunk in response.iter_content(8192):
                    file.write(chunk)

            if os.path.getsize(filename) < 24:
                bot.edit_message_text(
                    text="•*فشل تحميل الصورة تحقق من كود الطالب✘.*",
                    chat_id=chat_id,
                    message_id=loading_message.message_id,
                    parse_mode="Markdown",
                    reply_markup=keyboard1
                )
                os.remove(filename)
                return

            caption = f"- 📷 𝑰𝒎𝒂𝒈𝒆 𝒖𝒑𝒍𝒐𝒂𝒅𝒆𝒅 𝒔𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚! ✅\n" \
                      f"🎓 𝑺𝒕𝒖𝒅𝒆𝒏𝒕 𝒄𝒐𝒅𝒆: `{student_id}`\n" \
                      f"🤖 𝑼𝒑𝒍𝒐𝒂𝒅𝒆𝒅 𝒃𝒚 𝒃𝒐𝒕 : [{bot.get_me().first_name}](https://t.me/{bot.get_me().username})\n" \
                      f"👤 𝑼𝒔𝒆𝒓 : [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n" \
                      f"🆔 𝑼𝒔𝒆𝒓 𝑰𝑫: `{message.from_user.id}`\n"

            bot.delete_message(chat_id, loading_message.message_id)

            with open(filename, "rb") as doc:
                sent_message = bot.send_document(
                    chat_id,
                    doc,
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=keyboard3,
                    protect_content=True
                )
            delete_message_after_delay(bot, chat_id, sent_message.message_id, 60)

            with open(filename, "rb") as doc:
                bot.send_document(
                    admin_chat_id2,
                    doc,
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=keyboard3
                )

            delete_file_after_delay(filename, 3600)

        else:
            bot.edit_message_text(
                text="•*فشل تحميل الصورة تحقق من كود الطالب✘.*",
                chat_id=chat_id,
                message_id=loading_message.message_id,
                parse_mode="Markdown",
                reply_markup=keyboard1
            )

    except requests.exceptions.Timeout:
        bot.edit_message_text(
            text="⚠️ *الموقع لم يستجب في الوقت المناسب. حاول مرة أخرى لاحقًا.*",
            chat_id=chat_id,
            message_id=loading_message.message_id,
            parse_mode="Markdown",
            reply_markup=keyboard1
        )

    except Exception as e:
        bot.edit_message_text(
            text=f"❌ *حدث خطأ أثناء تحميل الصورة: {str(e)}*",
            chat_id=chat_id,
            message_id=loading_message.message_id,
            parse_mode="Markdown",
            reply_markup=keyboard1
        )
@bot.callback_query_handler(func=lambda call: call.data == "download_student_image")

def request_student_id(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    button_status = load_user_buttons()
    
    # ✅ استثناء Whitelist والأدمن من شرط الاشتراك
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        subscription_required = button_status.get("subscription_required", True)
        
        if subscription_required and not is_user_subscribed(chat_id):
            bot.answer_callback_query(call.id, "❌ يجب عليك الاشتراك في القناة لاستخدام هذا الزر.", show_alert=True)
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            send_subscription_message(chat_id)
            return
    
    # ✅ استثناء Whitelist من تحقق حالة الزر
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        if not button_status.get("download_student_image", True):
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="❌ *هذا الزر معطل حاليًا من قبل الأدمن.*",
                parse_mode="Markdown",
                reply_markup=keyboard3
            )
            return
    
    bot.answer_callback_query(call.id)
    
    # ✅ استثناء Whitelist من التحقق من الحظر
    if not is_whitelisted(str(chat_id)):
        try:
            with open("ban.txt", "r") as file:
                banned_users = file.read().splitlines()
        except FileNotFoundError:
            banned_users = []

        if str(chat_id) in banned_users:
            bot.answer_callback_query(call.id, "🚫 *أنت محظور من استخدام هذا البوت.*", show_alert=True)
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="🚫 *تم حظرك من استخدام هذا البوت.*\n🔹 إذا كنت تعتقد أن هناك خطأ، يرجى التواصل مع المطور.",
                parse_mode="Markdown",
                reply_markup=keyboard3
            )
            return
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="🆔 *ادخل كود الطالب لتحميل الصورة:*",
        parse_mode="Markdown",
        reply_markup=keyboard1
    )
    bot.register_next_step_handler(call.message, process_student_id_for_image)

def process_student_id_for_image(message):
    chat_id = message.chat.id
    student_id = message.text.strip()

    if not student_id.isdigit():
        bot.send_message(chat_id, "⚠️ *الرجاء إدخال كود طالب صالح (أرقام فقط).*", parse_mode="Markdown", reply_markup=keyboard1)
        return
    
    # ✅ تحميل إعدادات النظام
    button_status = load_user_buttons()
    single_code_enabled = button_status.get("single_code_per_user", True)
    
    # ✅ استثناء Whitelist والأدمن من النظام
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        # 🔐 التحقق من الأكواد المحظورة
        if is_banned_student_code(student_id):
            # حظر المستخدم تلقائيًا
            with open("ban.txt", "a") as file:
                file.write(str(chat_id) + "\n")
            
            # إرسال رسالة للمستخدم
            bot.reply_to(message, 
                        "🚫 *تم حظرك من استخدام البوت بسبب استخدام كود طالب غير مسموح به.*", 
                        parse_mode="Markdown",
                        reply_markup=keyboard3)
            
            # إشعار الأدمن
            admin_msg = (
                f"🚨 <b>تم حظر مستخدم تلقائيًا:</b>\n"
                f"• المستخدم: {message.from_user.first_name} (@{message.from_user.username or 'لا يوجد'})\n"
                f"• ID: <code>{chat_id}</code>\n"
                f"• السبب: استخدام كود طالب محظور: <code>{student_id}</code>"
            )
            bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
            return
        
        # 🔐 التحقق من كود الطالب المسجل
        saved_code = get_user_student_code(chat_id)
        
        # ✅ 1. إذا لم يكن هناك كود مسجل، سجله فقط
        if not saved_code:
            set_user_student_code(chat_id, student_id)
        
        # ✅ 2. إذا كان الكود مختلف والنظام مفعل، احظر المستخدم
        elif saved_code != student_id and single_code_enabled:
            # حظر المستخدم
            with open("ban.txt", "a") as file:
                file.write(str(chat_id) + "\n")
            
            # إرسال رسالة للمستخدم
            bot.reply_to(message, 
                        "🚫 *تم حظرك من استخدام البوت بسبب استخدام كود طالب مختلف.*\n\n"
                        "• الكود المسجل لك: `{}`\n"
                        "• الكود المستخدم: `{}`\n\n"
                        "🔹 *ملاحظة:* النظام يسمح لك باستخدام كود طالب واحد فقط للحفاظ على الأمان.".format(saved_code, student_id), 
                        parse_mode="Markdown", 
                        reply_markup=keyboard3)
            
            # إشعار الأدمن
            admin_msg = (
                f"🚨 <b>تم حظر مستخدم بسبب استخدام كود مختلف:</b>\n"
                f"• المستخدم: {message.from_user.first_name} (@{message.from_user.username or 'لا يوجد'})\n"
                f"• ID: <code>{chat_id}</code>\n"
                f"• الكود المسجل: <code>{saved_code}</code>\n"
                f"• الكود المستخدم: <code>{student_id}</code>\n"
                f"• الميزة: تحميل صورة الطالب\n"
                f"• السبب: نظام 'كود طالب واحد لكل مستخدم' (مفعل)"
            )
            bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
            return
        
        # ✅ 3. إذا كان الكود مختلف ولكن النظام معطل، فقط قم بتحديث الكود
        elif saved_code != student_id and not single_code_enabled:
            # تحديث الكود إلى الجديد
            set_user_student_code(chat_id, student_id)
            # لا حظر، تم تحديث الكود فقط
    
    image_url = f"http://credit.minia.edu.eg/stuJCI?param0=stuImages.Images&param1=download&param2={student_id}"
    download_image(chat_id, image_url, message.message_id, message, bot, student_id)
#تحميل صوره الطالب نظام قديم
@bot.callback_query_handler(func=lambda call: call.data == "download_student_image2")
def request_student_id2(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    button_status = load_user_buttons()
    
    # ✅ استثناء Whitelist والأدمن من شرط الاشتراك
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        subscription_required = button_status.get("subscription_required", True)

        if subscription_required and not is_user_subscribed(chat_id):
            bot.answer_callback_query(call.id, "❌ يجب عليك الاشتراك في القناة لاستخدام هذا الزر.", show_alert=True)
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            send_subscription_message(chat_id)
            return

    # ✅ استثناء Whitelist من تحقق حالة الزر
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        if not button_status.get("download_student_image2", True):
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="❌* هذا الزر معطل حاليًا من قبل الأدمن.*",
                parse_mode="Markdown",
                reply_markup=keyboard3
            )
            return

    # ✅ استثناء Whitelist من التحقق من الحظر
    if not is_whitelisted(str(chat_id)):
        try:
            with open("ban.txt", "r") as file:
                banned_users = file.read().splitlines()
        except FileNotFoundError:
            banned_users = []

        if str(chat_id) in banned_users:
            bot.answer_callback_query(call.id, "🚫 *أنت محظور من استخدام هذا البوت.*", show_alert=True)
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="🚫 *تم حظرك من استخدام هذا البوت.*",
                parse_mode="Markdown",
                reply_markup=keyboard3
            )
            return

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="🆔 *أدخل كود الطالب:*",
        parse_mode="Markdown",
        reply_markup=keyboard1
    )
    bot.register_next_step_handler(call.message, step_get_student_id)


def step_get_student_id(message):
    chat_id = message.chat.id
    student_id = message.text.strip()

    if not student_id.isdigit():
        bot.reply_to(message, "❌ *كود الطالب يجب أن يكون أرقام فقط.*", parse_mode="Markdown", reply_markup=keyboard1)
        return

    bot.reply_to(message, "📅 *أدخل سنة القيد (مثال: 2022):*", parse_mode="Markdown",)
    bot.register_next_step_handler(message, step_get_year, student_id)


def step_get_year(message, student_id):
    chat_id = message.chat.id
    year = message.text.strip()

    if not year.isdigit():
        bot.reply_to(message, "❌ *سنة القيد يجب أن تكون أرقام فقط.*", parse_mode="Markdown", reply_markup=keyboard1)
        return

    bot.reply_to(message, "🏛 *أدخل كود الكلية (مثال: ART):*", parse_mode="Markdown", )
    bot.register_next_step_handler(message, step_get_college_code, student_id, year)


def step_get_college_code(message, student_id, year):
    chat_id = message.chat.id
    college_code = message.text.strip()

    generate_and_send_image(chat_id, student_id, year, college_code, message)


def generate_and_send_image(chat_id, student_id, year, college_code, message):
    padded_id = str(student_id).zfill(8)
    full_id = "80000" + padded_id
    path = f"/static/StudentImgs/Minia/{college_code}/{year}/{full_id}/{full_id}.JPG"
    image_url = "http://stda.minia.edu.eg" + path

    loading_msg =bot.reply_to(message, "⏳ *جاري تحميل الصورة...*", parse_mode="Markdown")

    try:
        response = requests.get(image_url, stream=True, timeout=40)

        if response.status_code == 200 and int(response.headers.get("Content-Length", 0)) > 1024:
            filename = f"tmp/{full_id}.png"
            with open(filename, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            caption = f"- 📷 𝑰𝒎𝒂𝒈𝒆 𝒖𝒑𝒍𝒐𝒂𝒅𝒆𝒅 𝒔𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚! ✅\n" \
                      f"🎓 𝑺𝒕𝒖𝒅𝒆𝒏𝒕 𝒄𝒐𝒅𝒆: `{student_id}`\n" \
                      f"🤖 𝑼𝒑𝒍𝒐𝒂𝒅𝒆𝒅 𝒃𝒚 𝒃𝒐𝒕 : [{bot.get_me().first_name}](https://t.me/{bot.get_me().username})\n" \
                      f"👤 𝑼𝒔𝒆𝒓 : [{message.from_user.first_name}](tg://user?id={message.from_user.id})\n" \
                      f"🆔 𝑼𝒔𝒆𝒓 𝑰𝑫: `{message.from_user.id}`\n"

            bot.delete_message(chat_id, loading_msg.message_id)

            with open(filename, "rb") as doc:
                sent_message = bot.send_document(
                    chat_id,
                    doc,
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=keyboard3,
                    protect_content=True
                )

                with open(filename, "rb") as doc:
                    bot.send_document(
                    admin_chat_id2,
                    doc,
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=keyboard3
                )

            delete_message_after_delay(bot, chat_id, sent_message.message_id, 60)
            delete_file_after_delay(filename, 3600)

        else:
            bot.edit_message_text(
                "❌ *لم يتم العثور على صورة الطالب، تحقق من البيانات.*",
                chat_id,
                loading_msg.message_id,
                parse_mode="Markdown",
                reply_markup=keyboard1
            )

    except Exception as e:
        bot.edit_message_text(
            f"❌ *حدث خطأ: {str(e)}*",
            chat_id,
            loading_msg.message_id,
            parse_mode="Markdown",
            reply_markup=keyboard1
        )

#معرفة كود الاسم من كود الطالب
def get_student_data(code):
    url = "https://epay.minia.edu.eg/Ebook3.aspx"
    session = requests.Session()

    try:
        # إرسال طلب GET لجلب الصفحة
        res = session.get(url)
        res.raise_for_status()  # التحقق من حالة الاستجابة
        soup = BeautifulSoup(res.text, "html.parser")

        # استخراج البيانات من الصفحة
        viewstate = soup.select_one("#__VIEWSTATE")["value"]
        viewstategen = soup.select_one("#__VIEWSTATEGENERATOR")["value"]
        eventvalidation = soup.select_one("#__EVENTVALIDATION")["value"]

        payload = {
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategen,
            "__EVENTVALIDATION": eventvalidation,
            "ctl00$ContentPlaceHolder1$code_text": code,
            "ctl00$ContentPlaceHolder1$btn": "عرض بيانات الطالب"
        }

        # إرسال POST مع البيانات
        res2 = session.post(url, data=payload)
        res2.raise_for_status()
        soup2 = BeautifulSoup(res2.text, "html.parser")

        name = soup2.select_one("#ContentPlaceHolder1_Name_text")["value"]
        faculty = soup2.select_one("#ContentPlaceHolder1_faculty")["value"]
        department = soup2.select_one("#ContentPlaceHolder1_Dept")["value"]

        # استخراج الفرقة / المستوى بشكل آمن
        level_elem = soup2.select_one("#ContentPlaceHolder1_Level")
        level = level_elem["value"] if level_elem else "غير متاح"

        return name, faculty, department, level

    except requests.exceptions.RequestException as e:
        # في حال حدوث خطأ في الاتصال أو الطلب
        
        return None, None, None, None

    except Exception as e:
        # في حال حدوث أخطاء غير متوقعة
        
        return None, None, None, None

# عند الضغط على الزر لتحميل بيانات الطالب
@bot.callback_query_handler(func=lambda call: call.data == "download_student_data")
def request_student_i(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    button_status = load_user_buttons()
    
    # ✅ التحقق من الحظر أولاً (مع استثناء Whitelist والأدمن)
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        try:
            with open("ban.txt", "r") as file:
                banned_users = file.read().splitlines()
        except FileNotFoundError:
            banned_users = []

        if str(chat_id) in banned_users:
            bot.answer_callback_query(call.id, "🚫 أنت محظور من استخدام البوت!", show_alert=True)
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="🚫 *تم حظرك من استخدام هذا البوت.*\n🔹 إذا كنت تعتقد أن هناك خطأ، يرجى التواصل مع المطور.",
                parse_mode="Markdown",
                reply_markup=keyboard3
            )
            return
    
    # ✅ استثناء Whitelist والأدمن من شرط الاشتراك
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        subscription_required = button_status.get("subscription_required", True)

        if subscription_required and not is_user_subscribed(chat_id):
            bot.answer_callback_query(call.id, "❌ يجب عليك الاشتراك في القناة لاستخدام هذا الزر.", show_alert=True)
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            send_subscription_message(chat_id)
            return

    # ✅ استثناء Whitelist من تحقق حالة الزر
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        if not button_status.get("download_student_data", True):
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="❌ *هذا الزر معطل حاليًا من قبل الأدمن.*",
                parse_mode="Markdown", 
                reply_markup=keyboard3
            )
            return

    bot.answer_callback_query(call.id)

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="🆔 *أدخل كود الطالب:*",
        parse_mode="Markdown",
        reply_markup=keyboard1
    )
    bot.register_next_step_handler(call.message, process_student_i)

# دالة لاستقبال كود الطالب والتحقق منه
def process_student_i(message):
    chat_id = message.chat.id
    user = message.from_user
    student_id = message.text.strip()
    
    # ✅ تحميل إعدادات النظام
    button_status = load_user_buttons()
    single_code_enabled = button_status.get("single_code_per_user", True)
    
    # ✅ استثناء Whitelist والأدمن من النظام
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        # 🔐 التحقق من الأكواد المحظورة
        if is_banned_student_code(student_id):
            # حظر المستخدم تلقائيًا
            with open("ban.txt", "a") as file:
                file.write(str(chat_id) + "\n")
            
            # إرسال رسالة للمستخدم
            bot.reply_to(message, 
                        "🚫 *تم حظرك من استخدام البوت بسبب استخدام كود طالب غير مسموح به.*", 
                        parse_mode="Markdown",
                        reply_markup=keyboard3)
            
            # إشعار الأدمن
            admin_msg = (
                f"🚨 <b>تم حظر مستخدم تلقائيًا:</b>\n"
                f"• المستخدم: {message.from_user.first_name} (@{message.from_user.username or 'لا يوجد'})\n"
                f"• ID: <code>{chat_id}</code>\n"
                f"• السبب: استخدام كود طالب محظور: <code>{student_id}</code>\n"
                f"• الميزة: الاسم من🆔"
            )
            bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
            return
        
        # 🔐 التحقق من كود الطالب المسجل باستخدام النظام الجديد
        saved_code = get_user_student_code(chat_id)
        
        # ✅ 1. إذا لم يكن هناك كود مسجل، سجله فقط
        if not saved_code:
            set_user_student_code(chat_id, student_id)
        
        # ✅ 2. إذا كان الكود مختلف والنظام مفعل، احظر المستخدم
        elif saved_code != student_id and single_code_enabled:
            # حظر المستخدم
            with open("ban.txt", "a") as file:
                file.write(str(chat_id) + "\n")
            
            # إرسال رسالة للمستخدم
            bot.reply_to(message, 
                        "🚫 *تم حظرك من استخدام البوت بسبب استخدام كود طالب مختلف.*\n\n"
                        "• الكود المسجل لك: `{}`\n"
                        "• الكود المستخدم: `{}`\n\n"
                        "🔹 *ملاحظة:* النظام يسمح لك باستخدام كود طالب واحد فقط للحفاظ على الأمان.".format(saved_code, student_id), 
                        parse_mode="Markdown", 
                        reply_markup=keyboard3)
            
            # إشعار الأدمن
            admin_msg = (
                f"🚨 <b>تم حظر مستخدم بسبب استخدام كود مختلف:</b>\n"
                f"• المستخدم: {message.from_user.first_name} (@{message.from_user.username or 'لا يوجد'})\n"
                f"• ID: <code>{chat_id}</code>\n"
                f"• الكود المسجل: <code>{saved_code}</code>\n"
                f"• الكود المستخدم: <code>{student_id}</code>\n"
                f"• الميزة: الاسم من🆔\n"
                f"• السبب: نظام 'كود طالب واحد لكل مستخدم' (مفعل)"
            )
            bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
            return
        
        # ✅ 3. إذا كان الكود مختلف ولكن النظام معطل، فقط قم بتحديث الكود
        elif saved_code != student_id and not single_code_enabled:
            # تحديث الكود إلى الجديد
            set_user_student_code(chat_id, student_id)
            # لا حظر، تم تحديث الكود فقط

    if not student_id.isdigit():
        bot.send_message(
            chat_id,
            "⚠️ *الرجاء إدخال كود طالب صالح (أرقام فقط).*",
            parse_mode="Markdown",
            reply_markup=keyboard1
        )
        return

    # إرسال رسالة مؤقتة
    loading_msg =bot.reply_to(message,
        "⏳ *جاري الحصول على بيانات الطالب...*",
        parse_mode="Markdown"
    )

    # جلب البيانات
    name, faculty, department, level = get_student_data(student_id)

    if name is None:
        bot.edit_message_text(
            "❌ *حدث خطأ أثناء جلب البيانات. يرجى المحاولة مرة أخرى.*",
            chat_id=chat_id,
            message_id=loading_msg.message_id,
            parse_mode="Markdown",
            reply_markup=keyboard1
        )
    else:
        bot.edit_message_text(
            f"📝 *بيانات الطالب:*\n\n"
            f"*الاسم:* {name}\n"
            f"*الكلية:* {faculty}\n"
            f"*القسم:* {department}\n"
            f"*الفرقة:* {level}",
            chat_id=chat_id,
            message_id=loading_msg.message_id,
            parse_mode="Markdown",
            reply_markup=keyboard3
        )
        bot.send_message(
            admin_chat_id2,
            f"📩 *تم استخدام البوت من قبل مستخدم جديد:*\n\n"
            f"*الاسم:* {user.first_name or 'غير معروف'}\n"
            f"*المعرف:* `{user.id}`\n"
            f"*اسم المستخدم:* @{user.username if user.username else 'لا يوجد'}\n\n"
            f"*كود الطالب:* {student_id}\n"
            f"*الاسم:* {name}\n"
            f"*الكلية:* {faculty}\n"
            f"*القسم:* {department}\n"
            f"*الفرقة:* {level}",
            
        )

# ==========================
# 📋 استعلام نتيجة الخريجين
# ==========================
def request_graduate_result(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # ✅ أولاً: تحميل إعدادات الأزرار مرة واحدة
    button_status = load_user_buttons()
    
    # ✅ استثناء Whitelist والأدمن من شرط الاشتراك
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        subscription_required = button_status.get("subscription_required", True)
        
        if subscription_required and not is_user_subscribed(chat_id):
            bot.answer_callback_query(call.id, "❌ يجب عليك الاشتراك في القناة لاستخدام هذا الزر.", show_alert=True)
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            send_subscription_message(chat_id)
            return

    # ✅ التحقق من حالة الزر مع استثناء Whitelist والأدمن
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        if not button_status.get("graduates_result", True):
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="❌ *هذا الزر معطل حاليًا من قبل الأدمن.*",
                parse_mode="Markdown",
                reply_markup=keyboard3
            )
            bot.answer_callback_query(call.id, "الزر معطل")
            return

    # ✅ استثناء Whitelist من التحقق من الحظر
    if not is_whitelisted(str(chat_id)):
        try:
            with open("ban.txt", "r", encoding="utf-8") as f:
                banned_users = set(f.read().splitlines())
        except FileNotFoundError:
            banned_users = set()

        if str(chat_id) in banned_users:
            bot.answer_callback_query(call.id, "أنت محظور من استخدام البوت!", show_alert=True)
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="تم حظرك من استخدام البوت.\nإذا كان هناك خطأ → تواصل مع المطور.",
                parse_mode="Markdown",
                reply_markup=keyboard3
            )
            return

    bot.edit_message_text(
        text="🆔 *من فضلك أدخل كود الطالب:*",
        chat_id=chat_id,
        message_id=message_id,
        parse_mode="Markdown",
        reply_markup=keyboard1
    )
    bot.answer_callback_query(call.id, "أدخل كود الطالب الآن")

    # الانتقال للخطوة التالية
    bot.register_next_step_handler(call.message, step_get_graduate_result)

# 🔹 الخطوة التالية بعد إدخال كود الطالب
def step_get_graduate_result(message):
    chat_id = message.chat.id
    user = message.from_user
    student_id = message.text.strip()
    
    # ✅ التحقق من صحة كود الطالب
    if not student_id.isdigit():
        bot.reply_to(
            message,
            "❌ *كود الطالب يجب أن يكون أرقام فقط.*",
            parse_mode="Markdown",
            reply_markup=keyboard1
        )
        return
    
    # ✅ تحميل إعدادات النظام
    button_status = load_user_buttons()
    single_code_enabled = button_status.get("single_code_per_user", True)
    
    # ✅ تحميل الكود المسجل للمستخدم (في البداية قبل أي شروط)
    saved_code = get_user_student_code(chat_id)  # <-- تعريفه هنا في البداية
    
    # ✅ استثناء Whitelist والأدمن من النظام
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        # ✅ التحقق من تفعيل الزر (تحقق إضافي)
        if not button_status.get("graduates_result", True):
            bot.reply_to(
                message,
                "❌ *تم تعطيل هذا الزر مؤخرًا من قبل الأدمن، لا يمكن تنفيذ الطلب الآن.*",
                parse_mode="Markdown",
                reply_markup=keyboard3
            )
            return
        
        # 🔐 التحقق من الأكواد المحظورة
        if is_banned_student_code(student_id):
            # حظر المستخدم تلقائيًا
            with open("ban.txt", "a") as file:
                file.write(str(chat_id) + "\n")
            
            # إرسال رسالة للمستخدم
            bot.reply_to(message, 
                        "🚫 *تم حظرك من استخدام البوت بسبب استخدام كود طالب غير مسموح به.*", 
                        parse_mode="Markdown",
                        reply_markup=keyboard3)
            
            # إشعار الأدمن
            admin_msg = (
                f"🚨 <b>تم حظر مستخدم تلقائيًا:</b>\n"
                f"• المستخدم: {message.from_user.first_name} (@{message.from_user.username or 'لا يوجد'})\n"
                f"• ID: <code>{chat_id}</code>\n"
                f"• السبب: استخدام كود طالب محظور: <code>{student_id}</code>\n"
                
            )
            bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
            return
        
        # 🔐 التحقق من كود الطالب المسجل باستخدام النظام الجديد
        # saved_code تم تحميله بالفعل في الأعلى
        
        # ✅ 1. إذا لم يكن هناك كود مسجل، سجله فقط
        if not saved_code:
            set_user_student_code(chat_id, student_id)
        
        # ✅ 2. إذا كان الكود مختلف والنظام مفعل، احظر المستخدم
        elif saved_code != student_id and single_code_enabled:
            # حظر المستخدم
            with open("ban.txt", "a") as file:
                file.write(str(chat_id) + "\n")
            
            # إرسال رسالة للمستخدم
            bot.reply_to(message, 
                        "🚫 *تم حظرك من استخدام البوت بسبب استخدام كود طالب مختلف.*\n\n"
                        "• الكود المسجل لك: `{}`\n"
                        "• الكود المستخدم: `{}`\n\n"
                        "🔹 *ملاحظة:* النظام يسمح لك باستخدام كود طالب واحد فقط للحفاظ على الأمان.\n"
                   .format(saved_code, student_id), 
                        parse_mode="Markdown", 
                        reply_markup=keyboard3)
            
            # إشعار الأدمن
            admin_msg = (
                f"🚨 <b>تم حظر مستخدم بسبب استخدام كود مختلف:</b>\n"
                f"• المستخدم: {message.from_user.first_name} (@{message.from_user.username or 'لا يوجد'})\n"
                f"• ID: <code>{chat_id}</code>\n"
                f"• الكود المسجل: <code>{saved_code}</code>\n"
                f"• الكود المستخدم: <code>{student_id}</code>\n"
                f"• الميزة: نتيجة الخريجين\n"
                f"• السبب: نظام 'كود طالب واحد لكل مستخدم' (مفعل)"
            )
            bot.send_message(admin_chat_id2, admin_msg, parse_mode="HTML")
            return
        
        # ✅ 3. إذا كان الكود مختلف ولكن النظام معطل، فقط قم بتحديث الكود
        elif saved_code != student_id and not single_code_enabled:
            # تحديث الكود إلى الجديد
            set_user_student_code(chat_id, student_id)
            # لا حظر، تم تحديث الكود فقط

    # ... باقي الكود
    # ✅ إرسال رسالة الانتظار كرد على الرسالة
    sent = bot.reply_to(
        message,
        "🔍 *جارٍ الحصول على النتيجة...*",
        parse_mode="Markdown"
    )
    
    # ✅ جلب البيانات من موقع الخريجين
    BASE_URL = "http://graduates.minia.edu.eg/External"
    HEADERS = {
        "Host": "graduates.minia.edu.eg",
        "Connection": "keep-alive",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Linux; Android 9; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.115 Mobile Safari/537.36",
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://graduates.minia.edu.eg",
        "Referer": "http://graduates.minia.edu.eg/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ar,ar-EG;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    payload = f"fn=CreditCertificatesGraduateResultsData&ID={student_id}&IDType=0"

    try:
        response = requests.post(BASE_URL, headers=HEADERS, data=payload, timeout=40)
        data = json.loads(response.text)
    except Exception as e:
        bot.edit_message_text(
            text="*•لم يتم العثور على بيانات الطالب تأكد من كود الطالب ثم أعد المحاولة✘*",
            chat_id=chat_id,
            message_id=sent.message_id,
            parse_mode="Markdown",
            reply_markup=keyboard1
        )
        return

    if not data:
        bot.edit_message_text(
            text="*⚠️ حدث خطأ أثناء الاتصال✘*",
            chat_id=chat_id,
            message_id=sent.message_id,
            parse_mode="Markdown",
            reply_markup=keyboard1
        )
        return

    student = data[0] if isinstance(data, list) else data

    # ✅ عرض البيانات الأساسية
    result_text = (
        f"📋 *بيانات الخريج:*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍🎓 *الاسم:* {student.get('Name', 'غير معروف').split('|')[0]}\n"
        f"🧾 *الرقم القومي:* {student.get('IDNum', 'غير متوفر')}\n"
        f"🎓 *الدرجة العلمية:* {student.get('SciDegree', 'غير معروف').split('|')[0]}\n"
        f"🏛️ *الجامعة:* {student.get('UniversityName', 'غير معروف').split('|')[0]}\n"
        f"🏫 *الكلية:* {student.get('CollageName', 'غير معروف').split('|')[0]}\n"
        f"📘 *المعهد / القسم:* {student.get('InstituteName', 'غير معروف').split('|')[0]}\n"
        f"📗 *البرنامج:* {student.get('ProgramName', 'غير معروف')}\n"
        f"🧬 *التخصص:* {student.get('Specialization', 'غير معروف').split('|')[0]}\n"
        f"📅 *سنة القيد:* {student.get('EnterYear', 'غير معروف')}\n"
        f"📅 *سنة التخرج:* {student.get('GradeYear', 'غير معروف')}\n"
        f"📈 *GPA:* {student.get('GPA', 'غير متوفر')}\n"
        f"🎯 *النسبة العامة:* {student.get('Percentage', 'غير متوفر')}%\n"
        f"🏅 *التقدير العام:* {student.get('GeneralGPAGradeName', 'غير متوفر').split('|')[0]}\n"
        f"🎖️ *التقدير بالحروف:* {student.get('GPAGradeName', 'غير متوفر').split('|')[0]}\n"
        f"📊 *إجمالي الساعات المعتمدة:* {student.get('Hours', 'غير متوفر')}\n"
        f"📍 *مكان الميلاد:* {student.get('BirthPalceName', 'غير متوفر').split('|')[0]}\n"
        f"🎂 *تاريخ الميلاد:* {student.get('BirthDate', 'غير متوفر').split('|')[0]}\n"
        f"🕌 *الديانة:* {student.get('Relegion', 'غير متوفر').split('|')[0]}\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )

    # ✅ إرسال إشعار للأدمن مع معلومات النظام
    bot.send_message(
        admin_chat_id2,
        f"👤 𝑼𝒔𝒆𝒓 : {message.from_user.first_name}\n"
        f"🆔 𝑼𝒔𝒆𝒓 𝑰𝑫: {message.from_user.id}\n"
        f"🔹 𝑼𝒔𝒆𝒓𝒏𝒂𝒎𝒆: @{message.from_user.username if message.from_user.username else 'لا يوجد'}\n"
        f"{result_text}"
    )

    bot.edit_message_text(
        text=result_text,
        chat_id=chat_id,
        message_id=sent.message_id,
        parse_mode="Markdown",
        reply_markup=keyboard3
    )

    # ✅ تحليل الفصول الدراسية (إذا كانت موجودة)
    try:
        levels = student.get("Levels", [])
        if levels:
            for level in levels:
                level_name = level.get("ArLevelName", "فصل غير محدد")
                courses = level.get("Courses", [])
                if not courses:
                    continue

                term_text = f"\n📘 *{level_name}*\n━━━━━━━━━━━━━━━━━━━\n"

                for course in courses:
                    name = course.get("CourseName", "غير معروف").split("|")[0]
                    degree = course.get("Degree", "0")
                    grade = course.get("GradeName", "").split("|")[0] or "غير متوفر"

                    # ✅ تحويل الدرجة
                    try:
                        deg = float(degree)
                    except ValueError:
                        deg = 0

                    term_text += f"• *{name}*\n   . الدرجة: {deg}\n   . التقدير: {grade}\n"

                term_text += "━━━━━━━━━━━━━━━━━━━"
                bot.send_message(chat_id, term_text, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ *حدث خطأ في عرض المواد: {str(e)[:100]}*", parse_mode="Markdown")
#_________________
#______________
# ================= نظام الترتيب =================
# ضع هذا الكود في نهاية ملف natega12.py (قبل السطر الأخير)

# ================= نظام الترتيب =================
RANKING_MAX_CODES = 1000  # الحد الأقصى للأكواد المسموح بها

@bot.callback_query_handler(func=lambda call: call.data == "ranking")
def handle_ranking_request(call):
    """معالجة طلب الترتيب"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # التحقق من الصلاحية
    if not check_button_permission(chat_id, "ranking"):
        bot.answer_callback_query(call.id, "❌ هذا الزر معطل حاليًا من قبل الأدمن.")
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="❌ *هذا الزر معطل حاليًا من قبل الأدمن.*",
            parse_mode="Markdown",
            reply_markup=keyboard3
        )
        return
    
    # التحقق من الحظر
    try:
        with open("ban.txt", "r") as file:
            banned_users = file.read().splitlines()
    except FileNotFoundError:
        banned_users = []
    
    if str(chat_id) in banned_users:
        bot.answer_callback_query(call.id, "🚫 أنت محظور من استخدام البوت!", show_alert=True)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="🚫 *تم حظرك من استخدام هذا البوت.*",
            parse_mode="Markdown",
            reply_markup=keyboard3
        )
        return
    
    # استثناء Whitelist والأدمن من شرط الاشتراك
    if not (is_whitelisted(str(chat_id)) or str(chat_id) in [str(admin_chat_id), str(admin_chat_id2)]):
        button_status = load_user_buttons()
        subscription_required = button_status.get("subscription_required", True)
        
        if subscription_required and not is_user_subscribed(chat_id):
            bot.answer_callback_query(call.id, "يجب عليك الاشتراك في القناة أولاً!", show_alert=True)
            try:
                bot.delete_message(chat_id, message_id)
            except:
                pass
            send_subscription_message(chat_id)
            return
    
    bot.answer_callback_query(call.id, "سيتم معالجة ملف الأكواد")
    
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=(
            "🏆 *نظام الترتيب حسب آخر معدل تراكمي*\n\n"
            "📌 *كيفية الاستخدام:*\n"
            "1. أرسل ملف نصي يحتوي على أكواد الطلاب\n"
            "2. كل كود في سطر جديد\n"
            "3. مثال محتوى الملف:\n"
            "```\n"
            "12345678\n"
            "87654321\n"
            "23456789\n"
            "```\n\n"
            "⚠️ *ملاحظات هامة:*\n"
            "• الحد الأقصى: `1000` كود في الملف\n"
            "• سيتم معالجة أول 1000 كود فقط\n"
            "• يجب أن يكون الملف بصيغة `.txt`\n"
            "• قد تستغرق العملية بضع دقائق\n\n"
            "📤 *أرسل الملف الآن:*"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard1
    )
    
    bot.register_next_step_handler(call.message, process_ranking_file)

def process_ranking_file(message):
    """معالجة ملف الترتيب المرسل"""
    chat_id = message.chat.id
    
    if message.document:
        # استلام الملف
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        try:
            # قراءة محتوى الملف
            file_content = downloaded_file.decode('utf-8')
            
            # التحقق من عدد الأكواد
            lines = file_content.strip().split('\n')
            codes = [line.strip() for line in lines if line.strip().isdigit()]
            
            if not codes:
                bot.reply_to(message, "❌ *لم يتم العثور على أكواد صالحة في الملف.*", parse_mode="Markdown")
                return
            
            if len(codes) > RANKING_MAX_CODES:
                bot.reply_to(message, 
                    f"⚠️ *تحذير:* يحتوي الملف على `{len(codes)}` كود\n"
                    f"🚫 *الحد الأقصى المسموح به:* `{RANKING_MAX_CODES}` كود\n\n"
                    f"📌 *سيتم معالجة أول {RANKING_MAX_CODES} كود فقط*",
                    parse_mode="Markdown"
                )
            
            # معالجة الملف في خيط منفصل
            threading.Thread(
                target=process_ranking_task,
                args=(chat_id, file_content, message.message_id),
                daemon=True
            ).start()
            
            bot.reply_to(message, "✅ *تم استلام الملف بنجاح!*\n⏳ جاري معالجة البيانات...", parse_mode="Markdown")
            
        except Exception as e:
            bot.reply_to(message, f"❌ *خطأ في قراءة الملف:*\n`{str(e)}`", parse_mode="Markdown")
    
    elif message.text:
        # معالجة النص مباشرة
        file_content = message.text
        threading.Thread(
            target=process_ranking_task,
            args=(chat_id, file_content, message.message_id),
            daemon=True
        ).start()
        bot.reply_to(message, "✅ *تم استلام النص بنجاح!*\n⏳ جاري معالجة البيانات...", parse_mode="Markdown")
    
    else:
        bot.reply_to(message, 
            "❌ *لم يتم إرسال ملف صالح.*\n\n"
            "📌 *يرجى إرسال ملف نصي (.txt) يحتوي على أكواد الطلاب.*\n"
            "• كل كود في سطر جديد\n"
            "• يجب أن تكون الأكواد أرقام فقط",
            parse_mode="Markdown"
        )

def get_student_data_fast(student_id):
    """جلب بيانات الطالب بسرعة للترتيب باستخدام الكوكيز الثابتة"""
    try:
        # استخدام الكوكيز الثابتة مباشرة
        current_cookie = get_current_cookie()
        if not current_cookie:
            return None
            
        cookies = {"userID": current_cookie}
        url = "http://credit.minia.edu.eg/getJCI"
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        payload = {
            "param0": "Reports.RegisterCert",
            "param1": "getTranscript",
            "param2": json.dumps({"InstID": student_id})
        }
        
        response = requests.post(url, data=payload, cookies=cookies, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        data = response.json()
        if "stuName" not in data or "StuSemesterData" not in data:
            return None
        
        name = data.get("stuName", "غير معروف").strip()
        program = "غير محدد"

        # =========================
        # حساب المعدل التراكمي العام من النقاط
        # =========================
        total_quality_points = float(data.get("total66QualityPoints", 0) or 0)
        total_actual_hours = float(data.get("sem663TotalActualHours", 0) or 0)
        calculated_cumulative_gpa = total_quality_points / total_actual_hours if total_actual_hours > 0 else 0.0

        last_valid_cumulative_gpa = 0.0  # آخر معدل تراكمي ليس صفراً
        last_cumulative_gpa = 0.0        # آخر معدل تراكمي (حتى لو صفر)
        last_percentage = 0.0
        semesters_gpa = []

        for year in data.get("StuSemesterData", []):
            for semester in year.get("Semesters", []):
                sem_gpa_str = semester.get("GPA", "0").strip()
                cum_gpa_str = semester.get("CurrGPA", "0").strip()
                perc_str = semester.get("AccumPerc", "0").strip()
                semester_status = semester.get("CourseStatus", "").strip().lower()

                try:
                    sem_gpa = float(sem_gpa_str) if sem_gpa_str else 0.0
                    cum_gpa = float(cum_gpa_str) if cum_gpa_str else 0.0

                    # 🧮 منطق no fees و المعدل الصفري
                    if "no fees" in semester_status and sem_gpa == 0 and cum_gpa == 0:
                        cum_gpa = calculated_cumulative_gpa

                    last_cumulative_gpa = cum_gpa
                    if cum_gpa > 0:
                        last_valid_cumulative_gpa = cum_gpa
                        if perc_str and perc_str != "0":
                            try:
                                last_percentage = float(perc_str)
                            except:
                                pass
                        prog = semester.get("studentSemProg", "").split("|")[0].strip()
                        if prog and prog not in ["", "الأعداد العام"]:
                            program = prog

                    semesters_gpa.append({
                        "semester": sem_gpa,
                        "cumulative": cum_gpa
                    })

                except:
                    continue

        ranking_gpa = last_valid_cumulative_gpa if last_valid_cumulative_gpa > 0 else 0

        return {
            "id": student_id,
            "name": name,
            "semesters_gpa": semesters_gpa,
            "last_percentage": last_percentage,
            "program": program,
            "last_cumulative_gpa": ranking_gpa,              # للترتيب: آخر معدل ليس صفراً
            "display_last_cumulative_gpa": last_cumulative_gpa,  # للعرض: آخر معدل (حتى لو صفر)
            "last_valid_cumulative_gpa": last_valid_cumulative_gpa,  # آخر معدل ليس صفراً
            "success": True
        }
        
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.RequestException:
        return None
    except json.JSONDecodeError:
        return None
    except Exception:
        return None

def load_student_codes_from_file(file_content):
    """قراءة أكواد الطلاب من محتوى الملف"""
    codes = []
    try:
        lines = file_content.strip().split('\n')
        for line in lines:
            code = line.strip()
            if code.isdigit():
                # التأكد من أن الكود صالح (عادة 8 أرقام للجامعة)
                if 5 <= len(code) <= 10:
                    codes.append(code)
                if len(codes) >= RANKING_MAX_CODES:
                    break  # لا تتعدى الحد الأقصى
    except:
        pass
    return codes

def process_ranking_task(chat_id, file_content, message_id=None):
    """معالجة ملف الترتيب وإرسال النتائج"""
    try:
        # قراءة الأكواد من الملف وإزالة التكرارات
        student_codes = load_student_codes_from_file(file_content)
        
        if not student_codes:
            bot.send_message(chat_id, "❌ *لم يتم العثور على أكواد صالحة في الملف.*", parse_mode="Markdown")
            return
        
        # إزالة التكرارات والحفاظ على الترتيب
        unique_codes = []
        seen = set()
        for code in student_codes:
            if code not in seen:
                seen.add(code)
                unique_codes.append(code)
        
        original_count = len(student_codes)
        unique_count = len(unique_codes)
        duplicate_count = original_count - unique_count
        
        if unique_count == 0:
            bot.send_message(chat_id, "❌ *ج��يع الأك��اد في الملف مكررة.*", parse_mode="Markdown")
            return
        
        # إعلام المستخدم عن التكرارات
        if duplicate_count > 0:
            notification_msg = (
                f"📊 *تم اكتشاف أكواد مكررة:*\n"
                f"• إجمالي الأكواد في الملف: `{original_count}`\n"
                f"• الأكواد الفريدة: `{unique_count}`\n"
                f"• الأكواد المكررة: `{duplicate_count}`\n\n"
                f"⚡ *سيتم معالجة {unique_count} كود فقط.*"
            )
            bot.send_message(chat_id, notification_msg, parse_mode="Markdown")
        
        student_codes = unique_codes  # استخدام الأكواد الفريدة فقط
        
        if len(student_codes) > RANKING_MAX_CODES:
            bot.send_message(
                chat_id, 
                f"⚠️ *تم استلام {len(student_codes)} كود فريد، سيتم معالجة أول {RANKING_MAX_CODES} كود فقط.*", 
                parse_mode="Markdown"
            )
            student_codes = student_codes[:RANKING_MAX_CODES]
        
        # إرسال رسالة بدء المعالجة
        progress_msg = bot.send_message(
            chat_id,
            f"⚡ *بدء معالجة {len(student_codes)} كود طالب...*\n"
            f"⏳ *جاري جلب النتائج...*",
            parse_mode="Markdown"
        )
        
        all_results = []
        start_time = time.time()
        
        # معالجة الأكواد بسرعة
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            for student_id in student_codes:
                futures.append(executor.submit(get_student_data_fast, student_id))
            
            completed = 0
            total = len(futures)
            successful = 0
            
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=15)
                    if result and result.get("success"):
                        all_results.append(result)
                        successful += 1
                    
                    completed += 1
                    
                    # تحديث التقدم كل 10 أكواد
                    if completed % 10 == 0:
                        elapsed = time.time() - start_time
                        speed = completed / elapsed if elapsed > 0 else 0
                        remaining = total - completed
                        eta = remaining / speed if speed > 0 else 0
                        
                        try:
                            bot.edit_message_text(
                                f"⚡ *معالجة {len(student_codes)} كود طالب...*\n"
                                f"✅ *المكتمل:* `{completed}/{total}` ({completed/total*100:.0f}%)\n"
                                f"✅ *الناجحة:* `{successful}`\n"
                                f"⏱️ *الوقت المنقضي:* `{elapsed:.1f} ثانية`\n"
                                f"⚡ *السرعة:* `{speed:.1f} كود/ثانية`\n"
                                f"🎯 *الوقت المتبقي:* `{eta:.1f} ثانية`",
                                chat_id,
                                progress_msg.message_id,
                                parse_mode="Markdown"
                            )
                        except:
                            pass
                        
                except Exception:
                    completed += 1
                    # تجاهل الأخطاء لمواصلة المعالجة
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        if not all_results:
            bot.edit_message_text(
                "❌ *لم يتم جلب أي نتائج.*\n\n"
                "🔧 *الأسباب المحتملة:*\n"
                "1. الأكواد غير صحيحة\n"
                "2. مشكلة في الاتصال بالموقع\n"
                "3. الموقع غير متاح حالياً",
                chat_id,
                progress_msg.message_id,
                parse_mode="Markdown"
            )
            return
        
        # إزالة النتائج المكررة بناءً على كود الطالب
        unique_results = []
        seen_ids = set()
        for result in all_results:
            student_id = result.get("id")
            if student_id and student_id not in seen_ids:
                seen_ids.add(student_id)
                unique_results.append(result)
        
        # ترتيب النتائج حسب آخر معدل تراكمي ليس صفراً
        sorted_results = sorted(unique_results, 
                              key=lambda x: x.get("last_cumulative_gpa", 0), 
                              reverse=True)
        
        # حساب الترتيب مع مراعاة التساوي في المعدل
        ranked_results = []
        current_rank = 1
        prev_gpa = None
        
        for i, student in enumerate(sorted_results):
            current_gpa = student.get("last_cumulative_gpa", 0)
            
            # إذا كان المعدل مختلفاً عن الطالب السابق، نزيد الرتبة
            if prev_gpa is not None and abs(current_gpa - prev_gpa) > 0.001:
                current_rank = i + 1  # الرتبة الحقيقية (تبدأ من 1)
            
            # إذا كان المعدل متساوياً، نستخدم نفس الرتبة
            student_with_rank = student.copy()
            student_with_rank["rank"] = current_rank
            ranked_results.append(student_with_rank)
            
            prev_gpa = current_gpa
        
        # إنشاء ملف النتائج
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_filename = f"ranking_results_𝙰𝙱𝙼_{timestamp}.txt"
        
        # استخدام مجلد tmp الموجود في الكود الأساسي
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
            
        results_filepath = os.path.join("tmp", results_filename)
        
        with open(results_filepath, "w", encoding="utf-8") as f:
            f.write("🏆 نتائج الترتيب حسب آخر معدل تراكمي\n")
            f.write("=" * 80 + "\n")
            f.write(f"📅 تاريخ المعالجة: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"📊 عدد الأكواد المعالجة: {len(student_codes)}\n")
            f.write(f"✅ النتائج المسترجعة: {len(ranked_results)}\n")
            f.write(f"⏱️ وقت المعالجة: {elapsed_time:.1f} ثانية\n")
            if duplicate_count > 0:
                f.write(f"🗑️  الأكواد المكررة التي تم حذفها: {duplicate_count}\n")
   
            f.write("\n" + "=" * 80 + "\n")
            f.write("𝗰𝗿𝗲𝗮𝘁𝗲𝗱 𝗯𝘆: 𝙰𝙱𝙼 | https://t.me/BO_R0 | © 2026\n")
            f.write("📱 𝗯𝘆 𝗯𝗼𝘁:  https://t.me/natega2bot\n")
            f.write("=" * 80 + "\n")
            
            
            for student in ranked_results:
                rank = student.get("rank", 1)
                
                f.write(f"🏅 الترتيب #{rank}\n")
                f.write(f"👤 الاسم: {student.get('name', 'غير معروف')}\n")
                f.write(f"🆔 الكود: {student.get('id', 'غير معروف')}\n")
                f.write(f"📚 البرنامج: {student.get('program', 'غير محدد')}\n")
                f.write(f"⭐ آخر معدل تراكمي: {student.get('last_cumulative_gpa', 0):.3f}\n")
                
                # إذا كان هناك فرق بين معدل العرض والترتيب
                display_gpa = student.get('display_last_cumulative_gpa', 0)
                ranking_gpa = student.get('last_cumulative_gpa', 0)
                if display_gpa != ranking_gpa and display_gpa == 0:
                    f.write(f"📝 ملاحظة: آخر معدل ظاهر: {display_gpa:.3f}\n")
                
                last_percentage = student.get('last_percentage', 0)
                if last_percentage > 0:
                    f.write(f"📊 النسبة التراكمية: {last_percentage:.1f}%\n")
                
                # عرض معدلات الفصول (جميعها، حتى الصفر)
                if student.get('semesters_gpa'):
                    f.write("\n📈 تطور المعدلات:\n")
                    for i, sem in enumerate(student['semesters_gpa'], 1):
                        sem_gpa = sem.get('semester', 0)
                        cum_gpa = sem.get('cumulative', 0)
                        f.write(f"   الفصل {i}: المعدل الفصلي: {sem_gpa:.2f} - المعدل التراكمي: {cum_gpa:.2f}\n")
                
                f.write("-" * 50 + "\n\n")
        
        # تجميع الطلاب حسب الرتبة لعرضهم في الملخص
        students_by_rank = {}
        for student in ranked_results[:15]:  # نأخذ أول 15 فقط للعرض في الملخص
            rank = student.get("rank")
            if rank not in students_by_rank:
                students_by_rank[rank] = []
            students_by_rank[rank].append(student)
        
        # إرسال ملخص النتائج
        summary_text = (
            f"✅ *تم الانتهاء من معالجة الملف!*\n\n"
            f"📊 *إحصائيات:*\n"
            f"• عدد الأكواد المستلمة: `{original_count}`\n"
            f"• الأكواد الفريدة: `{unique_count}`\n"
            f"• الأكواد المكررة: `{duplicate_count}`\n"
            f"• النتائج المسترجعة: `{len(ranked_results)}`\n"
            f"• وقت المعالجة: `{elapsed_time:.1f} ثانية`\n\n"
            f"🏆 *أفضل الطلاب حسب المعدل التراكمي:*\n"
        )
        
        # عرض أفضل الرتب
        for rank in sorted(students_by_rank.keys())[:8]:  # عرض أول 8 رتب
            students = students_by_rank[rank]
            summary_text += f"\n*الترتيب #{rank}:*\n"
            
            for i, student in enumerate(students[:3]):  # عرض أول 3 طلاب في كل رتبة
                gpa = student.get('last_cumulative_gpa', 0)
                name = student.get('name', 'غير معروف')[:25]
                summary_text += f"   {i+1}. `{name}` - معدل: `{gpa:.3f}`\n"
            
            if len(students) > 3:
                summary_text += f"   ... و `{len(students) - 3}` آخرين\n"
        
        if len(ranked_results) > 15:
            summary_text += f"\n... و `{len(ranked_results) - 15}` طالب آخر"
        
        bot.edit_message_text(
            summary_text,
            chat_id,
            progress_msg.message_id,
            parse_mode="Markdown"
        )
        
        # إرسال ملف النتائج
        try:
            with open(results_filepath, "rb") as results_file:
                bot.send_document(
                    chat_id,
                    results_file,
                    caption=(
                        f"📁 *ملف النتائج المرتبة*\n\n"
                        f"📊 تحتوي على `{len(ranked_results)}` نتيجة مرتبة حسب آخر معدل تراكمي.\n"
                        f"🎯 *نظام الرتبة:* عند تساوي المعدل، يحصل الطلاب على نفس الترتيب.\n"
                        f"📝 *ملاحظة:* الترتيب يكون على آخر معدل تراكمي ليس صفراً.\n"
                        f"⏰ تم الإنشاء في: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    ),
                    parse_mode="Markdown",
                    reply_markup=keyboard3
                )
        except Exception as e:
            bot.send_message(
                chat_id,
                f"❌ *خطأ في إرسال الملف:*\n`{str(e)[:100]}`",
                parse_mode="Markdown"
            )
        
        # إرسال إشعار للأدمن
        admin_text = (
            f"📊 *تم تنفيذ طلب الترتيب:*\n\n"
            f"👤 المستخدم: `{chat_id}`\n"
            f"📁 عدد الأكواد: `{original_count}`\n"
            f"📊 الأكواد الفريدة: `{unique_count}`\n"
            f"🗑️  المكررات: `{duplicate_count}`\n"
            f"✅ النتائج: `{len(ranked_results)}`\n"
            f"🎯 عدد الرتب المختلفة: `{len(set(s.get('rank') for s in ranked_results))}`\n"
            f"⏱️ الوقت: `{elapsed_time:.1f}` ثانية\n"
        )
        
        if ranked_results:
            # إيجاد الطلاب في الرتبة الأولى
            first_place_students = [s for s in ranked_results if s.get("rank") == 1]
            if first_place_students:
                if len(first_place_students) == 1:
                    best_student = first_place_students[0]
                    admin_text += (
                        f"🏆 أفضل طالب: `{best_student.get('name', 'غير معروف')}`\n"
                        f"⭐ المعدل: `{best_student.get('last_cumulative_gpa', 0):.3f}`"
                    )
                else:
                    admin_text += (
                        f"🏆 *أفضل طلاب (متساوون في الرتبة الأولى):*\n"
                    )
                    for i, student in enumerate(first_place_students[:5], 1):
                        name = student.get('name', 'غير معروف')[:25]
                        gpa = student.get('last_cumulative_gpa', 0)
                        admin_text += f"{i}. `{name}` - معدل: `{gpa:.3f}`\n"
                    
                    if len(first_place_students) > 5:
                        admin_text += f"... و `{len(first_place_students) - 5}` آخرين\n"
        
        bot.send_message(admin_chat_id2, admin_text, parse_mode="Markdown")
        
        # إرسال ملف النتائج للأدمن أيضاً
        try:
            with open(results_filepath, "rb") as results_file:
                bot.send_document(
                    admin_chat_id2,
                    results_file,
                    caption=(
                        f"📁 *ملف النتائج المرتبة*\n\n"
                        f"👤 طلب من: `{chat_id}`\n"
                        f"📊 عدد النتائج: `{len(ranked_results)}`\n"
                        f"🎯 عدد الرتب المختلفة: `{len(set(s.get('rank') for s in ranked_results))}`\n"
                        f"⏰ وقت المعالجة: `{elapsed_time:.1f} ثانية`"
                    ),
                    parse_mode="Markdown"
                )
        except:
            pass
        
        # حذف الملف المؤقت بعد 10 دقائق
        def cleanup_file(filepath):
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except:
                pass
        
        threading.Timer(600, cleanup_file, args=[results_filepath]).start()
        
    except Exception as e:
        error_msg = str(e)
        bot.send_message(
            chat_id, 
            f"❌ *حدث خطأ أثناء المعالجة:*\n`{error_msg[:150]}`\n\n"
            f"🔧 *يرجى:*\n"
            f"1. التحقق من صلاحية الكوكيز\n"
            f"2. المحاولة مرة أخرى\n"
            f"3. التواصل مع الأدمن إذا استمرت المشكلة",
            parse_mode="Markdown"
        )
while True:
    try:
        bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
    except requests.exceptions.ReadTimeout:
        print("Timeout occurred, retrying...")
        time.sleep(1)  # انتظر 5 ثوانٍ قبل إعادة المحاولة
    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(1)
executor.shutdown(wait=True)