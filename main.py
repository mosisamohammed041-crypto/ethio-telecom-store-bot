
import os
import logging
from datetime import datetime, timezone

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from supabase import create_client

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

OWNER_ID = 6806823032
CONTACT_USERNAME = "@mosiservicespro"

db = create_client(SUPABASE_URL, SUPABASE_KEY)

PERMISSIONS = {
    "view_orders": "View orders",
    "verify_payments": "Verify payments",
    "manage_delivery": "Manage delivery",
    "manage_packages": "Manage packages",
    "message_customers": "Message customers",
    "manage_cbe": "Manage CBE details",
    "manage_admins": "Manage other admins",
}

TEXT = {
    "en": {
        "choose": "Choose your language:",
        "welcome": "Welcome to Ethio Telecom Packages Store!",
        "packages": "Available packages",
        "buy": "Buy package",
        "back": "⬅️ Back",
        "cancel": "❌ Cancel order",
        "contact": "Contact support",
        "change_language": "Change language",
        "no_packages": "There are currently no available packages.",
        "payment_missing": "Payment details are not configured. Please contact support.",
        "payment_title": "CBE PAYMENT DETAILS",
        "account_name": "Account name",
        "account_number": "Account number",
        "amount": "Amount",
        "pay_instruction": "Please pay using CBE, then upload a photo of your payment receipt.",
        "receipt": "Please upload your payment receipt as a photo.",
        "phone": "Please send the Ethio Telecom phone number that should receive the package.",
        "invalid_phone": "That phone number is not valid. Please try again.",
        "submitted": "Your order and payment receipt have been submitted. Please wait for payment verification.",
        "cancelled": "Your order has been cancelled successfully.",
        "cannot_cancel": "This order can no longer be cancelled because payment has been accepted or its status has changed.",
        "accepted": "✅ Your payment has been successfully verified and accepted!\n\nPlease wait 4–6 hours for your package delivery.\n\nIf your package is not delivered within 4–6 hours, please contact our admin: @mosiservicespro.",
        "rejected": "❌ Your payment could not be verified and has been rejected. Please contact our admin @mosiservicespro for assistance.",
        "delivered": "✅ Your order has been completed! Your Ethio Telecom package has been delivered. Thank you for choosing us!",
        "message_received": "Message from our store:",
        "error": "Something went wrong. Please try again or contact @mosiservicespro.",
        "data": "Data",
        "minutes": "Voice minutes",
        "validity": "Validity",
        "price": "Price",
        "bonus": "Bonus and details",
        "not_specified": "Not specified",
    },
    "om": {
        "choose": "Maaloo afaan keessan filadhaa:",
        "welcome": "Baga gara Ethio Telecom Packages Store dhuftan!",
        "packages": "Paakeejiiwwan jiran",
        "buy": "Paakeejii bitadhu",
        "back": "⬅️ Duubatti",
        "cancel": "❌ Ajaja haqii",
        "contact": "Gargaarsa qunnamaa",
        "change_language": "Afaan jijjiiri",
        "no_packages": "Yeroo ammaa paakeejiin hin jiru.",
        "payment_missing": "Odeeffannoon kaffaltii hin qophoofne. Maaloo gargaarsa qunnamaa.",
        "payment_title": "ODEEFFANNOO KAFFALTII CBE",
        "account_name": "Maqaa abbaa herregaa",
        "account_number": "Lakkoofsa herregaa",
        "amount": "Baay'ina kaffaltii",
        "pay_instruction": "Maaloo CBE fayyadamuun kaffalaa, achiis suuraa ragaa kaffaltii keessanii ergaa.",
        "receipt": "Maaloo suuraa ragaa kaffaltii keessanii ergaa.",
        "phone": "Maaloo lakkoofsa bilbilaa Ethio Telecom paakeejiin itti ergamu ergaa.",
        "invalid_phone": "Lakkoofsi bilbilaa kun sirrii miti. Maaloo irra deebi'aa.",
        "submitted": "Ajajni keessanii fi ragaan kaffaltii ergameera. Mirkaneessa kaffaltii eeggadhaa.",
        "cancelled": "Ajajni keessan milkaa'inaan haqameera.",
        "cannot_cancel": "Kaffaltiin erga fudhatamee booda ykn haalli ajajaa erga jijjiiramee booda ajaja kana haqachuu hin dandeessan.",
        "accepted": "✅ Kaffaltiin keessan mirkanaa'ee fudhatameera!\n\nMaaloo paakeejiin keessan akka isiniif ergamu sa'aatii 4–6 eeggadhaa.\n\nYoo sa'aatii 4–6 keessatti paakeejiin keessan isiniif hin geenye, admin keenya @mosiservicespro qunnamaa.",
        "rejected": "❌ Kaffaltiin keessan mirkanaa'uu waan hin dandeenyeef didameera. Gargaarsaaf admin keenya @mosiservicespro qunnamaa.",
        "delivered": "✅ Ajajni keessan xumurameera! Paakeejiin Ethio Telecom keessan isiniif ergameera. Nu filachuu keessaniif galatoomaa!",
        "message_received": "Ergaa daldala keenya irraa:",
        "error": "Rakkoon uumameera. Maaloo irra deebi'aa yaalaa ykn @mosiservicespro qunnamaa.",
        "data": "Daataa",
        "minutes": "Daqiiqaa bilbilaa",
        "validity": "Yeroo turtii",
        "price": "Gatii",
        "bonus": "Faayidaa dabalataa fi ibsa",
        "not_specified": "Hin ibsamne",
    },
    "am": {
        "choose": "እባክዎ ቋንቋዎን ይምረጡ፦",
        "welcome": "ወደ Ethio Telecom Packages Store እንኳን በደህና መጡ!",
        "packages": "ያሉ ፓኬጆች",
        "buy": "ፓኬጅ ይግዙ",
        "back": "⬅️ ተመለስ",
        "cancel": "❌ ትዕዛዝ ይሰርዙ",
        "contact": "ድጋፍ ያግኙ",
        "change_language": "ቋንቋ ይቀይሩ",
        "no_packages": "በአሁኑ ጊዜ የሚገኝ ፓኬጅ የለም።",
        "payment_missing": "የክፍያ መረጃ አልተዘጋጀም። እባክዎ ድጋፍ ያግኙ።",
        "payment_title": "የCBE ክፍያ መረጃ",
        "account_name": "የሂሳብ ባለቤት ስም",
        "account_number": "የሂሳብ ቁጥር",
        "amount": "የክፍያ መጠን",
        "pay_instruction": "እባክዎ በCBE ይክፈሉ፣ ከዚያም የክፍያ ደረሰኝ ፎቶ ይላኩ።",
        "receipt": "እባክዎ የክፍያ ደረሰኝዎን ፎቶ ይላኩ።",
        "phone": "ፓኬጁ የሚላክበትን የኢትዮ ቴሌኮም ስልክ ቁጥር ይላኩ።",
        "invalid_phone": "የላኩት ስልክ ቁጥር ትክክል አይደለም። እባክዎ እንደገና ይሞክሩ።",
        "submitted": "ትዕዛዝዎና የክፍያ ደረሰኝዎ ተልኳል። ክፍያዎ እስኪረጋገጥ ይጠብቁ።",
        "cancelled": "ትዕዛዝዎ በተሳካ ሁኔታ ተሰርዟል።",
        "cannot_cancel": "ክፍያው ከተቀበለ ወይም የትዕዛዙ ሁኔታ ከተቀየረ በኋላ ይህን ትዕዛዝ መሰረዝ አይቻልም።",
        "accepted": "✅ ክፍያዎ በተሳካ ሁኔታ ተረጋግጦ ተቀብሏል!\n\nእባክዎ ፓኬጅዎ እስኪደርስ 4–6 ሰዓት ይጠብቁ።\n\nበ4–6 ሰዓት ውስጥ ፓኬጅዎ ካልደረሰ፣ አስተዳዳሪያችንን @mosiservicespro ያነጋግሩ።",
        "rejected": "❌ ክፍያዎ ማረጋገጥ ስላልተቻለ ውድቅ ተደርጓል። እባክዎ እገዛ ለማግኘት @mosiservicespro ያነጋግሩ።",
        "delivered": "✅ ትዕዛዝዎ ተጠናቋል! የኢትዮ ቴሌኮም ፓኬጅዎ ደርሷል። ስለመረጡን እናመሰግናለን!",
        "message_received": "ከሱቃችን የተላከ መልዕክት፦",
        "error": "ችግር ተፈጥሯል። እባክዎ እንደገና ይሞክሩ ወይም @mosiservicespro ያነጋግሩ።",
        "data": "ዳታ",
        "minutes": "የድምፅ ጥሪ ደቂቃዎች",
        "validity": "የቆይታ ጊዜ",
        "price": "ዋጋ",
        "bonus": "ተጨማሪ ጥቅም እና መግለጫ",
        "not_specified": "አልተገለጸም",
    },
}


def tr(lang, key):
    return TEXT.get(lang, TEXT["en"]).get(key, TEXT["en"][key])


def owner(user_id):
    return int(user_id) == OWNER_ID


def get_admin(user_id):
    if owner(user_id):
        return {"active": True, "permissions": list(PERMISSIONS)}
    result = db.table("store_admins").select("*").eq(
        "telegram_id", user_id
    ).eq("active", True).execute()
    return result.data[0] if result.data else None


def has_permission(user_id, permission):
    admin = get_admin(user_id)
    return bool(admin and permission in (admin.get("permissions") or []))


def admin_ids(permission):
    ids = [OWNER_ID]
    result = db.table("store_admins").select(
        "telegram_id,permissions"
    ).eq("active", True).execute()
    for row in result.data:
        if permission in (row.get("permissions") or []):
            ids.append(row["telegram_id"])
    return list(set(ids))


def get_language(user_id):
    result = db.table("customers").select("language").eq(
        "telegram_id", user_id
    ).execute()
    if result.data and result.data[0].get("language") in TEXT:
        return result.data[0]["language"]
    return "en"


def save_language(user, lang):
    db.table("customers").upsert({
        "telegram_id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "language": lang,
    }, on_conflict="telegram_id").execute()


def setting(key):
    result = db.table("store_settings").select("setting_value").eq(
        "setting_key", key
    ).execute()
    return result.data[0]["setting_value"] if result.data else None


def set_setting(key, value):
    db.table("store_settings").upsert({
        "setting_key": key,
        "setting_value": value,
    }, on_conflict="setting_key").execute()


def language_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("English", callback_data="lang:en"),
        InlineKeyboardButton("Afaan Oromoo", callback_data="lang:om"),
        InlineKeyboardButton("አማርኛ", callback_data="lang:am"),
    ]])


def customer_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(lang, "packages"), callback_data="packages")],
        [InlineKeyboardButton(tr(lang, "change_language"), callback_data="change_language")],
        [InlineKeyboardButton(tr(lang, "contact"), url="https://t.me/mosiservicespro")],
    ])


def admin_keyboard(user_id):
    rows = []
    if has_permission(user_id, "view_orders"):
        rows.append([InlineKeyboardButton("🧾 View orders", callback_data="admin:orders")])
    if has_permission(user_id, "manage_packages"):
        rows.append([InlineKeyboardButton("📦 Manage packages", callback_data="admin:packages")])
    if has_permission(user_id, "message_customers"):
        rows.append([InlineKeyboardButton("💬 Message customer", callback_data="admin:message")])
    if has_permission(user_id, "manage_cbe"):
        rows.append([InlineKeyboardButton("🏦 CBE settings", callback_data="admin:cbe")])
    if owner(user_id):
        rows.append([InlineKeyboardButton("👮 Manage admins", callback_data="admin:admins")])
    return InlineKeyboardMarkup(rows)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    result = db.table("customers").select("language").eq(
        "telegram_id", user.id
    ).execute()
    if result.data and result.data[0].get("language") in TEXT:
        lang = result.data[0]["language"]
        await update.message.reply_text(
            tr(lang, "welcome"), reply_markup=customer_keyboard(lang)
        )
    else:
        await update.message.reply_text(
            "Choose your language / Afaan filadhaa / ቋንቋ ይምረጡ:",
            reply_markup=language_keyboard(),
        )


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not get_admin(user_id):
        await update.message.reply_text("You do not have admin access.")
        return
    await update.message.reply_text(
        "Store Administration",
        reply_markup=admin_keyboard(user_id),
    )


async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not has_permission(user_id, "view_orders"):
        await update.message.reply_text("You do not have permission.")
        return
    result = db.table("orders").select("*").order(
        "created_at", desc=True
    ).limit(30).execute()
    if not result.data:
        await update.message.reply_text("No orders found.")
        return
    for order in result.data:
        await send_order_card(context, update.effective_chat.id, order["id"])


async def send_order_card(context, chat_id, order_id):
    order = db.table("orders").select("*").eq(
        "id", order_id
    ).single().execute().data
    customer = db.table("customers").select("*").eq(
        "id", order["customer_id"]
    ).single().execute().data
    package = db.table("packages").select("*").eq(
        "id", order["package_id"]
    ).single().execute().data
    payments = db.table("payments").select("*").eq(
        "order_id", order_id
    ).execute().data
    payment = payments[0] if payments else {}
    deliveries = db.table("deliveries").select("*").eq(
        "order_id", order_id
    ).execute().data
    phone = deliveries[0]["recipient_phone"] if deliveries else "Not available"

    caption = (
        f"ORDER #{order_id}\n"
        f"Customer: {customer.get('full_name')}\n"
        f"Telegram ID: {customer.get('telegram_id')}\n"
        f"Phone: {phone}\n"
        f"Package: {package.get('name')}\n"
        f"Price: {package.get('price')} Birr\n"
        f"Order status: {order.get('status')}\n"
        f"Payment status: {payment.get('status')}"
    )

    buttons = []
    if order["status"] == "payment_submitted" and has_permission(chat_id, "verify_payments"):
        buttons.append([
            InlineKeyboardButton("✅ Accept payment", callback_data=f"pay:accept:{order_id}"),
            InlineKeyboardButton("❌ Reject payment", callback_data=f"pay:reject:{order_id}"),
        ])
    if order["status"] == "payment_accepted" and has_permission(chat_id, "manage_delivery"):
        buttons.append([
            InlineKeyboardButton("📦 Mark delivered", callback_data=f"deliver:{order_id}")
        ])
    if has_permission(chat_id, "message_customers"):
        buttons.append([
            InlineKeyboardButton("💬 Message customer", callback_data=f"message_order:{order_id}")
        ])

    markup = InlineKeyboardMarkup(buttons) if buttons else None
    receipt = payment.get("receipt_file_id")
    if receipt:
        await context.bot.send_photo(
            chat_id=chat_id, photo=receipt, caption=caption, reply_markup=markup
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id, text=caption, reply_markup=markup
        )


async def show_packages(query, context):
    lang = get_language(query.from_user.id)
    result = db.table("packages").select("*").eq(
        "active", True
    ).order("id").execute()
    if not result.data:
        await query.message.reply_text(tr(lang, "no_packages"))
        return

    for package in result.data:
        message = (
            f"📦 {package['name']}\n"
            f"🌐 {tr(lang, 'data')}: {package.get('data_amount') or '-'}\n"
            f"📞 {tr(lang, 'minutes')}: {package.get('voice_minutes') or tr(lang, 'not_specified')}\n"
            f"⏳ {tr(lang, 'validity')}: {package.get('validity') or '-'}\n"
            f"💰 {tr(lang, 'price')}: {package['price']} Birr\n"
            f"🎁 {tr(lang, 'bonus')}: {package.get('description') or '-'}"
        )
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                tr(lang, "buy"), callback_data=f"buy:{package['id']}"
            )
        ]])
        await query.message.reply_text(message, reply_markup=keyboard)


async def buy_package(query, context, package_id):
    lang = get_language(query.from_user.id)
    result = db.table("packages").select("*").eq(
        "id", package_id
    ).eq("active", True).execute()
    if not result.data:
        await query.message.reply_text(tr(lang, "no_packages"))
        return
    package = result.data[0]

    account_name = setting("cbe_account_name")
    account_number = setting("cbe_account_number")
    if not account_name or not account_number:
        await query.message.reply_text(tr(lang, "payment_missing"))
        return

    context.user_data["package_id"] = package_id
    context.user_data["waiting_receipt"] = True
    context.user_data["waiting_phone"] = False
    context.user_data.pop("receipt_file_id", None)

    await query.message.reply_text(
        f"📦 {package['name']}\n"
        f"💰 {tr(lang, 'amount')}: {package['price']} Birr\n\n"
        f"🏦 {tr(lang, 'payment_title')}\n"
        f"{tr(lang, 'account_name')}: {account_name}\n"
        f"{tr(lang, 'account_number')}: {account_number}\n\n"
        f"{tr(lang, 'pay_instruction')}\n\n{tr(lang, 'receipt')}",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(tr(lang, "back"), callback_data="packages")
        ]]),
    )


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_receipt"):
        return
    lang = get_language(update.effective_user.id)
    context.user_data["receipt_file_id"] = update.message.photo[-1].file_id
    context.user_data["waiting_receipt"] = False
    context.user_data["waiting_phone"] = True
    await update.message.reply_text(tr(lang, "phone"))


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_language(user.id)
    phone = (update.message.text or "").strip().replace(" ", "").replace("-", "")

    if not context.user_data.get("waiting_phone"):
        return

    if not phone.replace("+", "").isdigit() or len(phone) < 9:
        await update.message.reply_text(tr(lang, "invalid_phone"))
        return

    receipt_id = context.user_data.get("receipt_file_id")
    package_id = context.user_data.get("package_id")
    if not receipt_id or not package_id:
        await update.message.reply_text(tr(lang, "error"))
        return

    customer_result = db.table("customers").select("id").eq(
        "telegram_id", user.id
    ).execute()
    if not customer_result.data:
        await update.message.reply_text(tr(lang, "error"))
        return

    package_result = db.table("packages").select("*").eq(
        "id", package_id
    ).eq("active", True).execute()
    if not package_result.data:
        await update.message.reply_text(tr(lang, "no_packages"))
        return
    package = package_result.data[0]

    order = db.table("orders").insert({
        "customer_id": customer_result.data[0]["id"],
        "package_id": package_id,
        "status": "payment_submitted",
    }).execute().data[0]
    order_id = order["id"]

    db.table("payments").insert({
        "order_id": order_id,
        "method": "CBE",
        "amount": package["price"],
        "status": "submitted",
        "receipt_file_id": receipt_id,
    }).execute()

    db.table("deliveries").insert({
        "order_id": order_id,
        "recipient_phone": phone,
        "status": "pending",
    }).execute()

    await update.message.reply_text(
        tr(lang, "submitted"),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(
                tr(lang, "cancel"), callback_data=f"cancel:{order_id}"
            )
        ]]),
    )

    context.user_data["waiting_phone"] = False
    context.user_data.pop("waiting_receipt", None)
    context.user_data.pop("receipt_file_id", None)
    context.user_data.pop("package_id", None)

    for admin_id in admin_ids("verify_payments"):
        try:
            await send_order_card(context, admin_id, order_id)
        except Exception:
            log.exception("Could not notify admin %s", admin_id)


async def notify_order_customer(context, order, text_key):
    customer = db.table("customers").select("telegram_id").eq(
        "id", order["customer_id"]
    ).single().execute().data
    lang = get_language(customer["telegram_id"])
    await context.bot.send_message(
        chat_id=customer["telegram_id"],
        text=tr(lang, text_key),
    )


async def accept_payment(query, context, order_id):
    if not has_permission(query.from_user.id, "verify_payments"):
        await query.answer("You do not have permission.", show_alert=True)
        return
    result = db.table("orders").select("*").eq("id", order_id).execute()
    if not result.data or result.data[0]["status"] != "payment_submitted":
        await query.answer("This order is no longer awaiting verification.", show_alert=True)
        return
    order = result.data[0]
    db.table("orders").update({"status": "payment_accepted"}).eq(
        "id", order_id
    ).execute()
    db.table("payments").update({"status
