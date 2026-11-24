import os
import re
import logging
import unicodedata
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from supabase import create_client

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("ethio_store")

BOT_TOKEN = os.environ["BOT_TOKEN"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
OWNER_ID = 6806823032
CONTACT_USERNAME = "@mosiservicespro"
CONTACT_URL = "https://t.me/mosiservicespro"

db = create_client(SUPABASE_URL, SUPABASE_KEY)

# Admin management is deliberately owner-only. Delegated admins cannot grant
# themselves or others additional privileges.
PERMISSIONS = {
    "view_orders": "View orders",
    "verify_payments": "Verify payments",
    "manage_delivery": "Manage delivery",
    "manage_packages": "Manage packages",
    "manage_payments": "Manage payment methods",
    "message_customers": "Message customers",
}

TEXT = {
    "en": {
        "choose": "Choose your language:",
        "welcome": "Welcome to Ethio Telecom Packages Store!",
        "packages": "Available packages", "buy": "Buy package",
        "back": "⬅️ Back", "cancel": "❌ Cancel order",
        "contact": "Contact support", "change_language": "Change language",
        "no_packages": "There are currently no available packages.",
        "payment_missing": "No payment methods are currently available. Please contact support.",
        "choose_payment": "Choose a payment method:",
        "amount": "Amount", "receipt": "Please upload your payment receipt as a photo.",
        "phone": "Send the Ethio Telecom phone number that should receive the package.",
        "invalid_phone": "That phone number is not valid. Please try again.",
        "submitted": "Your order and receipt have been submitted. Please wait for payment verification.",
        "cancelled": "Your order has been cancelled successfully.",
        "cannot_cancel": "This order can no longer be cancelled because payment has been accepted or its status has changed.",
        "accepted": f"✅ Your payment has been verified and accepted!\n\nPlease wait 4–6 hours for delivery.\n\nIf it is not delivered within 4–6 hours, contact {CONTACT_USERNAME}.",
        "rejected": f"❌ Your payment could not be verified and has been rejected. Please contact {CONTACT_USERNAME} for assistance.",
        "delivered": "✅ Your order has been completed and your package has been delivered. Thank you!",
        "message_received": "Message from our store:",
        "error": f"Something went wrong. Please try again or contact {CONTACT_USERNAME}.",
        "data": "Data", "minutes": "Voice minutes", "validity": "Validity",
        "price": "Price", "bonus": "Bonus and details", "not_specified": "Not specified",
        "menu_home": "🏠 Main menu", "menu_browse": "📦 Browse Packages", "menu_orders": "🧾 My Orders", "menu_profile": "👤 My Profile", "menu_support": "☎️ Support", "menu_admin": "🛠 Admin Panel", "support_text": f"Support: {CONTACT_USERNAME}", "profile": "👤 My Profile", "profile_language": "Language", "orders_empty": "You have no previous orders yet.",
        "payment_details": "PAYMENT DETAILS", "pay_instruction": "Pay using the selected method, then upload a photo of your receipt.",
    },
    "om": {
        "choose": "Maaloo afaan keessan filadhaa:",
        "welcome": "Baga gara Ethio Telecom Packages Store dhuftan!",
        "packages": "Paakeejiiwwan jiran", "buy": "Paakeejii bitadhu",
        "back": "⬅️ Duubatti", "cancel": "❌ Ajaja haqii",
        "contact": "Gargaarsa qunnamaa", "change_language": "Afaan jijjiiri",
        "no_packages": "Yeroo ammaa paakeejiin hin jiru.",
        "payment_missing": "Yeroo ammaa mala kaffaltii hin jiru. Maaloo gargaarsa qunnamaa.",
        "choose_payment": "Mala kaffaltii filadhaa:",
        "amount": "Baay'ina kaffaltii", "receipt": "Maaloo suuraa ragaa kaffaltii keessanii ergaa.",
        "phone": "Maaloo lakkoofsa bilbilaa Ethio Telecom paakeejiin itti ergamu ergaa.",
        "invalid_phone": "Lakkoofsi bilbilaa kun sirrii miti. Maaloo irra deebi'aa.",
        "submitted": "Ajajni keessanii fi ragaan kaffaltii ergameera. Mirkaneessa eeggadhaa.",
        "cancelled": "Ajajni keessan milkaa'inaan haqameera.",
        "cannot_cancel": "Kaffaltiin erga fudhatamee booda ykn haalli ajajaa erga jijjiiramee booda ajaja kana haqachuu hin dandeessan.",
        "accepted": f"✅ Kaffaltiin keessan mirkanaa'ee fudhatameera!\n\nMaaloo sa'aatii 4–6 eeggadhaa.\n\nYoo yeroo kana keessatti hin geenye {CONTACT_USERNAME} qunnamaa.",
        "rejected": f"❌ Kaffaltiin keessan mirkanaa'uu waan hin dandeenyeef didameera. Gargaarsaaf {CONTACT_USERNAME} qunnamaa.",
        "delivered": "✅ Paakeejiin keessan isiniif ergameera. Galatoomaa!",
        "message_received": "Ergaa daldala keenya irraa:",
        "error": f"Rakkoon uumameera. Maaloo irra deebi'aa yaalaa ykn {CONTACT_USERNAME} qunnamaa.",
        "data": "Daataa", "minutes": "Daqiiqaa bilbilaa", "validity": "Yeroo turtii",
        "price": "Gatii", "bonus": "Faayidaa dabalataa fi ibsa", "not_specified": "Hin ibsamne",
        "menu_home": "🏠 Fuula jalqabaa", "menu_browse": "📦 Paakeejiiwwan", "menu_orders": "🧾 Ajajawwan Koo", "menu_profile": "👤 Piroofaayilii Koo", "menu_support": "☎️ Gargaarsa", "menu_admin": "🛠 Bulchiinsa", "support_text": f"Gargaarsa: {CONTACT_USERNAME}", "profile": "👤 Piroofaayilii Koo", "profile_language": "Afaan", "orders_empty": "Ammaaf ajajni duraanii hin jiru.",
        "payment_details": "ODEEFFANNOO KAFFALTII", "pay_instruction": "Mala kaffaltii filattan fayyadamuun kaffalaa, achiis suuraa ragaa kaffaltii ergaa.",
    },
    "am": {
        "choose": "እባክዎ ቋንቋዎን ይምረጡ፦",
        "welcome": "ወደ Ethio Telecom Packages Store እንኳን በደህና መጡ!",
        "packages": "ያሉ ፓኬጆች", "buy": "ፓኬጅ ይግዙ",
        "back": "⬅️ ተመለስ", "cancel": "❌ ትዕዛዝ ይሰርዙ",
        "contact": "ድጋፍ ያግኙ", "change_language": "ቋንቋ ይቀይሩ",
        "no_packages": "በአሁኑ ጊዜ የሚገኝ ፓኬጅ የለም።",
        "payment_missing": "የክፍያ ዘዴዎች አልተዘጋጁም። እባክዎ ድጋፍ ያግኙ።",
        "choose_payment": "የክፍያ ዘዴ ይምረጡ፦",
        "amount": "የክፍያ መጠን", "receipt": "እባክዎ የክፍያ ደረሰኝዎን ፎቶ ይላኩ።",
        "phone": "ፓኬጁ የሚላክበትን የኢትዮ ቴሌኮም ስልክ ቁጥር ይላኩ።",
        "invalid_phone": "የላኩት ስልክ ቁጥር ትክክል አይደለም።",
        "submitted": "ትዕዛዝዎና ደረሰኝዎ ተልኳል። ክፍያዎ እስኪረጋገጥ ይጠብቁ።",
        "cancelled": "ትዕዛዝዎ ተሰርዟል።",
        "cannot_cancel": "ክፍያው ከተቀበለ ወይም የትዕዛዙ ሁኔታ ከተቀየረ በኋላ መሰረዝ አይቻልም።",
        "accepted": f"✅ ክፍያዎ ተረጋግጦ ተቀብሏል!\n\nእባክዎ 4–6 ሰዓት ይጠብቁ።\n\nበዚህ ጊዜ ውስጥ ካልደረሰ {CONTACT_USERNAME} ያነጋግሩ።",
        "rejected": f"❌ ክፍያዎ ማረጋገጥ ስላልተቻለ ውድቅ ተደርጓል። {CONTACT_USERNAME} ያነጋግሩ።",
        "delivered": "✅ ፓኬጅዎ ደርሷል። ስለመረጡን እናመሰግናለን!",
        "message_received": "ከሱቃችን የተላከ መልዕክት፦",
        "error": f"ችግር ተፈጥሯል። {CONTACT_USERNAME} ያነጋግሩ።",
        "data": "ዳታ", "minutes": "የድምፅ ጥሪ ደቂቃዎች", "validity": "የቆይታ ጊዜ",
        "price": "ዋጋ", "bonus": "ተጨማሪ ጥቅም እና መግለጫ", "not_specified": "አልተገለጸም",
        "menu_home": "🏠 ዋና ምናሌ", "menu_browse": "📦 ፓኬጆችን ይመልከቱ", "menu_orders": "🧾 ትዕዛዞቼ", "menu_profile": "👤 መገለጫዬ", "menu_support": "☎️ ድጋፍ", "menu_admin": "🛠 የአስተዳዳሪ ፓነል", "support_text": f"ድጋፍ: {CONTACT_USERNAME}", "profile": "👤 መገለጫዬ", "profile_language": "ቋንቋ", "orders_empty": "እስካሁን የቀድሞ ትዕዛዞች የሉም።",
        "payment_details": "የክፍያ መረጃ", "pay_instruction": "በመረጡት ዘዴ ይክፈሉ፣ ከዚያም የደረሰኝ ፎቶ ይላኩ።",
    },
}



def _dt(value):
    if not value: return None
    if isinstance(value, datetime): return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    x=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    return x if x.tzinfo else x.replace(tzinfo=timezone.utc)


def get_service_control():
    rows=db.table("store_service_control").select("*").eq("id",1).limit(1).execute().data or []
    return rows[0] if rows else None


def service_is_unavailable():
    r=get_service_control()
    if not r or not r.get("is_unavailable"): return False
    now=datetime.now(timezone.utc); start=_dt(r.get("starts_at")); end=_dt(r.get("ends_at"))
    return bool(start and now>=start and (end is None or now<end))


def service_message(lang):
    return {"en":"🚧 Service is currently unavailable. Please try again later.","om":"🚧 Tajaajilli yeroo ammaa hin jiru. Maaloo yeroo biraa irra deebi'aa yaalaa.","am":"🚧 አገልግሎቱ በአሁኑ ጊዜ አይገኝም። እባክዎ ቆይተው ይሞክሩ።"}.get(lang,"🚧 Service is currently unavailable. Please try again later.")


def set_service_control(enabled,start,end,admin_id):
    db.table("store_service_control").upsert({"id":1,"is_unavailable":enabled,"starts_at":start.isoformat() if start else None,"ends_at":end.isoformat() if end else None,"start_notified":False,"end_notified":False,"updated_by":int(admin_id),"updated_at":datetime.now(timezone.utc).isoformat()},on_conflict="id").execute()


async def notify_service_customers(bot,available):
    rows=db.table("customers").select("telegram_id,language").execute().data or []
    for c in rows:
        tid=c.get("telegram_id")
        if not tid: continue
        lang=c.get("language") or "en"
        text=service_message(lang) if not available else {"en":"✅ Package service is available again. You can order packages now.","om":"✅ Tajaajilli paakeejii deebi'ee hojiitti galeera. Amma ajajuu dandeessu.","am":"✅ የፓኬጅ አገልግሎት እንደገና ጀምሯል። አሁን ማዘዝ ይችላሉ።"}.get(lang,"✅ Package service is available again.")
        try: await bot.send_message(chat_id=int(tid),text=text)
        except Exception: log.info("Could not notify customer %s",tid)


async def show_service_controls(q):
    r = get_service_control()
    unavailable = service_is_unavailable()
    body = "Service status: " + ("⛔ Currently unavailable" if unavailable else "✅ Available")
    if unavailable and r and r.get("ends_at"):
        remaining = max(0, int((_dt(r["ends_at"]) - datetime.now(timezone.utc)).total_seconds()))
        body += f"\n\n⏳ Service resumes in: {remaining // 3600:02d}:{(remaining % 3600) // 60:02d}:{remaining % 60:02d}"
    elif unavailable:
        body += "\n\nNo automatic restart is set (manual enable required)."
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⛔ Disable indefinitely", callback_data="service:disable_now")],
        [InlineKeyboardButton("⏱ Disable for a duration", callback_data="service:duration")],
        [InlineKeyboardButton("✅ Enable now", callback_data="service:enable_now")],
        [InlineKeyboardButton("✖ Cancel downtime", callback_data="service:cancel_schedule")],
    ])
    await edit_screen(q, body, kb)


async def scheduled_worker(bot):
    while True:
        try:
            r=get_service_control()
            if r and r.get("is_unavailable"):
                now=datetime.now(timezone.utc); start=_dt(r.get("starts_at")); end=_dt(r.get("ends_at"))
                if start and now>=start and (end is None or now<end) and not r.get("start_notified"):
                    await notify_service_customers(bot,False)
                    db.table("store_service_control").update({"start_notified":True}).eq("id",1).execute()
                if end and now >= end:
                    db.table("store_service_control").update({"is_unavailable":False,"starts_at":None,"ends_at":None,"end_notified":True}).eq("id",1).execute()
                    await notify_service_customers(bot, True)
            await update_active_promotions(bot)
        except Exception:
            log.exception("Scheduled service/promotion task failed")
        await asyncio.sleep(60)


async def update_active_promotions(bot):
    rows=db.table("store_promotions").select("*").eq("status","active").execute().data or []
    for promo in rows:
        expiry=_dt(promo.get("expires_at")); expired=bool(expiry and expiry<=datetime.now(timezone.utc))
        left=max(0,int((expiry-datetime.now(timezone.utc)).total_seconds())) if expiry else 0
        countdown=("❌ OFFER EXPIRED" if expired else f"⏳ Offer ends in: {left//3600:02d}:{(left%3600)//60:02d}:{left%60:02d}") if expiry else ""
        body=(promo.get("message") or "")+("\n\n"+countdown if countdown else "")
        markup=None
        if not expired and promo.get("package_id"):
            pk=db.table("packages").select("id,name,price").eq("id",promo["package_id"]).eq("active",True).limit(1).execute().data or []
            if pk: markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"🛒 Buy Now — {pk[0]['name']} ({pk[0]['price']} Birr)",callback_data=f"buy:{promo['package_id']}")]])
        deliveries=db.table("store_promotion_deliveries").select("telegram_id,message_id,message_kind").eq("promotion_id",promo["id"]).execute().data or []
        for d in deliveries:
            try:
                if d["message_kind"]=="photo": await bot.edit_message_caption(chat_id=d["telegram_id"],message_id=d["message_id"],caption=body[:1024],reply_markup=markup)
                else: await bot.edit_message_text(chat_id=d["telegram_id"],message_id=d["message_id"],text=body,reply_markup=markup)
            except Exception: pass
        if expired: db.table("store_promotions").update({"status":"expired"}).eq("id",promo["id"]).execute()


def tr(lang, key):
    return TEXT.get(lang, TEXT["en"]).get(key, TEXT["en"].get(key, key))

def owner(user_id):
    return int(user_id) == OWNER_ID

def get_admin(user_id):
    if owner(user_id):
        return {"active": True, "permissions": list(PERMISSIONS)}
    result = db.table("store_admins").select("*").eq("telegram_id", int(user_id)).eq("active", True).execute()
    return result.data[0] if result.data else None

def has_permission(user_id, permission):
    admin = get_admin(user_id)
    return bool(admin and permission in (admin.get("permissions") or []))

def admin_ids(permission):
    ids = [OWNER_ID]
    rows = db.table("store_admins").select("telegram_id,permissions").eq("active", True).execute().data or []
    ids.extend(int(r["telegram_id"]) for r in rows if permission in (r.get("permissions") or []))
    return sorted(set(ids))

def get_language(user_id):
    rows = db.table("customers").select("language").eq("telegram_id", int(user_id)).execute().data or []
    return rows[0].get("language") if rows and rows[0].get("language") in TEXT else "en"

def save_language(user, lang):
    db.table("customers").upsert({
        "telegram_id": user.id, "full_name": user.full_name,
        "username": user.username, "language": lang,
    }, on_conflict="telegram_id").execute()

def language_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("English", callback_data="lang:en"),
        InlineKeyboardButton("Afaan Oromoo", callback_data="lang:om"),
        InlineKeyboardButton("አማርኛ", callback_data="lang:am"),
    ]])

def language_reply_keyboard():
    # First-time visitors choose their language from the Telegram bottom keyboard.
    return ReplyKeyboardMarkup(
        [[KeyboardButton("English"), KeyboardButton("Afaan Oromoo"), KeyboardButton("አማርኛ")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def customer_keyboard(lang, user_id=None):
    rows = [
        [KeyboardButton(tr(lang, "menu_browse")), KeyboardButton(tr(lang, "menu_orders"))],
        [KeyboardButton(tr(lang, "menu_profile")), KeyboardButton(tr(lang, "menu_support"))],
    ]
    # Show the admin shortcut only to the owner and active registered admins.
    if user_id is not None and get_admin(user_id):
        rows.append([KeyboardButton(tr(lang, "menu_admin"))])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)


def customer_inline_home(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(lang, "menu_browse"), callback_data="packages")],
        [InlineKeyboardButton(tr(lang, "menu_orders"), callback_data="my_orders")],
        [InlineKeyboardButton(tr(lang, "menu_profile"), callback_data="my_profile")],
    ])

async def edit_screen(query, text, reply_markup=None):
    try:
        if query.message.photo:
            await query.edit_message_caption(caption=text, reply_markup=reply_markup)
        else:
            await query.edit_message_text(text=text, reply_markup=reply_markup)
    except Exception as exc:
        if "message is not modified" not in str(exc).lower():
            log.exception("Could not edit screen")


def admin_keyboard(uid):
    rows = []
    choices = [
        ("view_orders", "🧾 View orders", "admin:orders"),
        ("manage_packages", "📦 Manage packages", "admin:packages"),
        ("manage_payments", "💳 Payment methods", "admin:payments"),
        ("message_customers", "💬 Message customer", "admin:message"),
    ]
    for perm, label, cb in choices:
        if has_permission(uid, perm):
            rows.append([InlineKeyboardButton(label, callback_data=cb)])
    if owner(uid):
        rows.append([InlineKeyboardButton("🛠 Service availability", callback_data="admin:service")])
        rows.append([InlineKeyboardButton("📣 Customer broadcast", callback_data="admin:broadcast")])
        rows.append([InlineKeyboardButton("👮 Manage admins", callback_data="admin:admins")])
    return InlineKeyboardMarkup(rows)

def active_payment_methods():
    return db.table("payment_methods").select("*").eq("active", True).order("id").execute().data or []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not (context.user_data.get("waiting_phone") and context.user_data.get("receipt_file_id")):
        context.user_data.clear()
    rows = db.table("customers").select("language").eq("telegram_id", update.effective_user.id).limit(1).execute().data or []
    lang = rows[0].get("language") if rows else None
    if lang in TEXT:
        context.user_data.pop("awaiting_language", None)
        await update.message.reply_text(tr(lang, "welcome"), reply_markup=customer_keyboard(lang, update.effective_user.id))
    else:
        context.user_data["awaiting_language"] = True
        await update.message.reply_text("Choose your language / Afaan filadhaa / ቋንቋ ይምረጡ:", reply_markup=language_reply_keyboard())


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_phone") and context.user_data.get("receipt_file_id"):
        lang = get_language(update.effective_user.id)
        await update.message.reply_text(
            "Your receipt is saved. Send the recipient phone number to complete checkout, or use the menu to browse and view orders. Your receipt will remain saved."
        )
        return
    context.user_data.clear()
    await update.message.reply_text("Current action cancelled. Use /start to return to the main menu.")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not get_admin(uid):
        await update.message.reply_text("You do not have admin access.")
        return
    await update.message.reply_text("Store Administration", reply_markup=admin_keyboard(uid))

async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not has_permission(uid, "view_orders"):
        await update.message.reply_text("You do not have permission."); return
    await update.message.reply_text("🧾 Order queues — choose a status:", reply_markup=order_queue_keyboard(uid))

def order_queue_keyboard(uid):
    rows = []
    queues = [
        ("payment_submitted", "⏳ Awaiting verification", "verify_payments"),
        ("payment_accepted", "📦 Awaiting delivery", "manage_delivery"),
        ("delivered", "✅ Completed", "view_orders"),
        ("rejected_cancelled", "❌ Rejected / Cancelled", "view_orders"),
    ]
    for status, label, perm in queues:
        if has_permission(uid, perm):
            rows.append([InlineKeyboardButton(label, callback_data=f"queue:{status}")])
    return InlineKeyboardMarkup(rows)

async def show_order_queue(query, context, status):
    uid = query.from_user.id
    allowed = {
        "payment_submitted": "verify_payments", "payment_accepted": "manage_delivery",
        "delivered": "view_orders", "rejected_cancelled": "view_orders",
    }
    if status not in allowed or not has_permission(uid, allowed[status]):
        await query.answer("You do not have permission.", show_alert=True); return
    if status == "rejected_cancelled":
        rejected = db.table("orders").select("id").eq("status", "payment_rejected").order("created_at", desc=True).limit(30).execute().data or []
        cancelled = db.table("orders").select("id").eq("status", "cancelled").order("created_at", desc=True).limit(30).execute().data or []
        rows = sorted(rejected + cancelled, key=lambda r: r.get("id", 0), reverse=True)[:30]
        label = "Rejected / Cancelled"
    else:
        rows = db.table("orders").select("id").eq("status", status).order("created_at", desc=True).limit(30).execute().data or []
        label = status.replace("_", " ").title()
    await edit_screen(query, f"{label}: {len(rows)} order(s).\nOrder details and receipt cards follow below.", InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to queues", callback_data="admin:orders")]]))
    for row in rows:
        await send_order_card(context, query.message.chat_id, row["id"])

async def send_order_card(context, chat_id, order_id):
    order_rows = db.table("orders").select("*").eq("id", order_id).limit(1).execute().data or []
    if not order_rows:
        return
    order = order_rows[0]
    customer_rows = db.table("customers").select("*").eq("id", order["customer_id"]).limit(1).execute().data or []
    package_rows = db.table("packages").select("*").eq("id", order["package_id"]).limit(1).execute().data or []
    payment_rows = db.table("payments").select("*").eq("order_id", order_id).order("created_at", desc=True).limit(1).execute().data or []
    delivery_rows = db.table("deliveries").select("*").eq("order_id", order_id).limit(1).execute().data or []
    if not customer_rows or not package_rows:
        log.error("Missing related row for order %s", order_id)
        return
    customer, package = customer_rows[0], package_rows[0]
    payment = payment_rows[0] if payment_rows else {}
    delivery = delivery_rows[0] if delivery_rows else {}
    caption = (
        f"ORDER #{order_id}\nCustomer: {customer.get('full_name')}\n"
        f"Telegram ID: {customer.get('telegram_id')}\nPhone: {delivery.get('recipient_phone', 'Not available')}\n"
        f"Package: {package.get('name')}\nPrice: {package.get('price')} Birr\n"
        f"Payment method: {payment.get('method', 'Unknown')}\n"
        f"Order status: {order.get('status')}\nPayment status: {payment.get('status')}"
    )
    buttons = []
    if order.get("status") == "payment_submitted" and has_permission(chat_id, "verify_payments"):
        buttons.append([
            InlineKeyboardButton("✅ Accept payment", callback_data=f"pay:accept:{order_id}"),
            InlineKeyboardButton("❌ Reject payment", callback_data=f"pay:reject:{order_id}"),
        ])
    if order.get("status") == "payment_accepted" and has_permission(chat_id, "manage_delivery"):
        buttons.append([InlineKeyboardButton("📦 Mark delivered", callback_data=f"deliver:{order_id}")])
    if has_permission(chat_id, "message_customers"):
        buttons.append([InlineKeyboardButton("💬 Message customer", callback_data=f"message_order:{order_id}")])
    markup = InlineKeyboardMarkup(buttons) if buttons else None
    receipt = payment.get("receipt_file_id")
    if receipt:
        await context.bot.send_photo(chat_id=chat_id, photo=receipt, caption=caption, reply_markup=markup)
    else:
        await context.bot.send_message(chat_id=chat_id, text=caption, reply_markup=markup)

async def show_packages(query, context):
    lang = get_language(query.from_user.id)
    if service_is_unavailable():
        await edit_screen(query, service_message(lang), customer_inline_home(lang)); return
    rows = db.table("packages").select("*").eq("active", True).order("id").execute().data or []
    if not rows:
        await edit_screen(query, tr(lang, "no_packages"), InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main menu", callback_data="home")]]))
        return
    buttons = []
    for p in rows:
        data = p.get("data_amount") or "Data"
        minutes = p.get("voice_minutes")
        label = f"{data or '-'} | {minutes or '—'} min | {p.get('price')} Birr"
        buttons.append([InlineKeyboardButton(label[:60], callback_data=f"detail:{p['id']}")])
    buttons.append([InlineKeyboardButton("🏠 Main menu", callback_data="home")])
    await edit_screen(query, "📦 " + tr(lang, "packages") + "\n\nChoose a package to see full details:", InlineKeyboardMarkup(buttons))

async def show_package_detail(query, context, package_id):
    lang = get_language(query.from_user.id)
    if service_is_unavailable():
        await edit_screen(query, service_message(lang), customer_inline_home(lang)); return
    rows = db.table("packages").select("*").eq("id", package_id).eq("active", True).limit(1).execute().data or []
    if not rows:
        await edit_screen(query, tr(lang, "no_packages"), InlineKeyboardMarkup([[InlineKeyboardButton(tr(lang, "back"), callback_data="packages")]])); return
    p = rows[0]
    context.user_data["selected_package_id"] = package_id
    detail = (f"📦 {p.get('name')}\n🌐 {tr(lang,'data')}: {p.get('data_amount') or '-'}\n"
              f"📞 {tr(lang,'minutes')}: {p.get('voice_minutes') or tr(lang,'not_specified')}\n"
              f"⏳ {tr(lang,'validity')}: {p.get('validity') or '-'}\n"
              f"💰 {tr(lang,'price')}: {p.get('price')} Birr\n"
              f"🎁 {tr(lang,'bonus')}: {p.get('description') or '-'}")
    await edit_screen(query, detail, InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buy now", callback_data=f"buy:{package_id}")],
        [InlineKeyboardButton(tr(lang, "back"), callback_data="packages")],
    ]))

async def buy_package(query, context, package_id):
    lang = get_language(query.from_user.id)
    if service_is_unavailable():
        await edit_screen(query, service_message(lang), customer_inline_home(lang)); return
    if context.user_data.get("waiting_phone") and context.user_data.get("receipt_file_id"):
        await edit_screen(
            query,
            "You already uploaded a receipt for an unfinished checkout. Send the recipient phone number to finish that order; your receipt has been kept.",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("🧾 My Orders", callback_data="my_orders")],
                [InlineKeyboardButton("🏠 Main menu", callback_data="home")],
            ]),
        )
        return
    rows = db.table("packages").select("*").eq("id", package_id).eq("active", True).limit(1).execute().data or []
    if not rows:
        await edit_screen(query, tr(lang, "no_packages"), InlineKeyboardMarkup([[InlineKeyboardButton(tr(lang, "back"), callback_data="packages")]])); return
    methods = active_payment_methods()
    if not methods:
        await edit_screen(query, tr(lang, "payment_missing"), InlineKeyboardMarkup([[InlineKeyboardButton(tr(lang, "back"), callback_data=f"detail:{package_id}")]])); return
    p = rows[0]
    context.user_data.clear()
    context.user_data.update({"package_id": package_id, "waiting_payment_method": True})
    buttons = [[InlineKeyboardButton(m["name"], callback_data=f"payment:choose:{m['id']}")] for m in methods]
    buttons.append([InlineKeyboardButton(tr(lang, "back"), callback_data=f"detail:{package_id}")])
    await edit_screen(query, f"📦 {p['name']}\n💰 {tr(lang,'amount')}: {p['price']} Birr\n\n{tr(lang,'choose_payment')}", InlineKeyboardMarkup(buttons))

async def choose_payment_method(query, context, method_id):
    lang = get_language(query.from_user.id)
    if service_is_unavailable():
        await edit_screen(query, service_message(lang), customer_inline_home(lang)); return
    rows = db.table("payment_methods").select("*").eq("id", method_id).eq("active", True).limit(1).execute().data or []
    if not rows:
        await edit_screen(query, tr(lang, "payment_missing"), InlineKeyboardMarkup([[InlineKeyboardButton(tr(lang, "back"), callback_data=f"detail:{context.user_data.get('package_id')}")]])); return
    method = rows[0]
    p_rows = db.table("packages").select("*").eq("id", context.user_data.get("package_id")).eq("active", True).limit(1).execute().data or []
    if not p_rows:
        await edit_screen(query, tr(lang, "no_packages"), InlineKeyboardMarkup([[InlineKeyboardButton(tr(lang, "back"), callback_data="packages")]])); return
    p = p_rows[0]
    context.user_data.update({"payment_method_id": method_id, "payment_method_name": method["name"], "waiting_receipt": True, "waiting_phone": False})
    await edit_screen(query, f"📦 {p['name']}\n💰 {tr(lang,'amount')}: {p['price']} Birr\n\n🏦 {tr(lang,'payment_details')}: {method['name']}\n{method.get('details') or ''}\n\n{method.get('instructions') or tr(lang,'pay_instruction')}\n\n{tr(lang,'receipt')}", InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main menu", callback_data="home")], [InlineKeyboardButton(tr(lang, "back"), callback_data=f"buy:{p['id']}")]]))

async def show_my_orders(query):
    uid, lang = query.from_user.id, get_language(query.from_user.id)
    customers = db.table("customers").select("id").eq("telegram_id", uid).limit(1).execute().data or []
    if not customers:
        await edit_screen(query, tr(lang, "orders_empty"), customer_inline_home(lang)); return
    orders = db.table("orders").select("id,package_id,status,created_at").eq(
        "customer_id", customers[0]["id"]
    ).order("created_at", desc=True).limit(20).execute().data or []
    if not orders:
        await edit_screen(query, tr(lang, "orders_empty"), customer_inline_home(lang)); return
    lines = ["🧾 " + tr(lang, "menu_orders")]
    for o in orders:
        packs = db.table("packages").select("*").eq("id", o["package_id"]).limit(1).execute().data or []
        pck = packs[0] if packs else {}
        created = (o.get("created_at") or "—").replace("T", " ")[:16]
        lines.append(
            f"\n#{o['id']} — {pck.get('name', 'Package')}\n"
            f"{tr(lang, 'data')}: {pck.get('data_amount') or '—'} | "
            f"{tr(lang, 'minutes')}: {pck.get('voice_minutes') or '—'}\n"
            f"{tr(lang, 'price')}: {pck.get('price', '—')} Birr\n"
            f"Date: {created}\nStatus: {(o.get('status') or '').replace('_', ' ').title()}"
        )
    await edit_screen(query, "\n".join(lines), customer_inline_home(lang))


async def show_profile(query):
    uid, lang = query.from_user.id, get_language(query.from_user.id)
    rows = db.table("customers").select("*").eq("telegram_id", uid).limit(1).execute().data or []
    c = rows[0] if rows else {}
    body = (
        f"{tr(lang, 'profile')}\n\nName: {c.get('full_name') or query.from_user.full_name}\n"
        f"Telegram ID: {uid}\n{tr(lang, 'profile_language')}: { {'en':'English','om':'Afaan Oromoo','am':'አማርኛ'}.get(lang, 'English') }"
    )
    await edit_screen(query, body, InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(lang, "change_language"), callback_data="change_language")],
        [InlineKeyboardButton(tr(lang, "back"), callback_data="home")],
    ]))


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_receipt"):
        return
    lang = get_language(update.effective_user.id)
    context.user_data["receipt_file_id"] = update.message.photo[-1].file_id
    context.user_data["waiting_receipt"] = False
    context.user_data["waiting_phone"] = True
    await update.message.reply_text(
        tr(lang, "phone"),
        reply_markup=customer_keyboard(lang, update.effective_user.id),
    )

def normalize_ethiopian_mobile_phone(value: str) -> Optional[str]:
    """Normalize Ethiopian mobile numbers to +2519XXXXXXXX / +2517XXXXXXXX.

    Accepts local 09/07 numbers and international 251/+251 forms, with
    spaces, hyphens, parentheses, or Unicode decimal digits.
    """
    digits = "".join(str(unicodedata.digit(ch)) for ch in value if ch.isdigit())
    if len(digits) == 10 and digits[0] == "0" and digits[1] in "79":
        return "+251" + digits[1:]
    if len(digits) == 12 and digits.startswith("251") and digits[3] in "79":
        return "+" + digits
    return None


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_language(user.id)
    if service_is_unavailable():
        await update.message.reply_text(service_message(lang) + " Your checkout details are kept; please retry when service returns.", reply_markup=customer_keyboard(lang, user.id))
        return
    phone_input = (update.message.text or "").strip()
    if not context.user_data.get("waiting_phone"):
        return
    phone = normalize_ethiopian_mobile_phone(phone_input)
    if not phone:
        await update.message.reply_text(
            tr(lang, "invalid_phone") + "\nExample: 09XXXXXXXX or +2519XXXXXXXX.",
            reply_markup=customer_keyboard(lang, user.id),
        )
        return
    if context.user_data.get("order_submission_in_progress") and not context.user_data.get("pending_order_id"):
        await update.message.reply_text("Your order is being submitted. Please wait.")
        return
    receipt_id = context.user_data.get("receipt_file_id")
    package_id = context.user_data.get("package_id")
    method_name = context.user_data.get("payment_method_name")
    if not receipt_id or not package_id or not method_name:
        await update.message.reply_text(tr(lang, "error"))
        return
    customer_rows = db.table("customers").select("id").eq("telegram_id", user.id).limit(1).execute().data or []
    package_rows = db.table("packages").select("*").eq("id", package_id).eq("active", True).limit(1).execute().data or []
    if not customer_rows or not package_rows:
        await update.message.reply_text(tr(lang, "error"))
        return
    p = package_rows[0]
    context.user_data["order_submission_in_progress"] = True
    try:
        order_id = context.user_data.get("pending_order_id")
        if not order_id:
            # Recover the existing order after a transient retry using the
            # receipt's already-persisted file ID, without adding schema fields.
            prior_payment = db.table("payments").select("order_id").eq(
                "receipt_file_id", receipt_id
            ).limit(1).execute().data or []
            if prior_payment:
                order_id = prior_payment[0]["order_id"]
            else:
                order = db.table("orders").insert({
                    "customer_id": customer_rows[0]["id"], "package_id": package_id,
                    "status": "payment_submitted",
                }).execute().data[0]
                order_id = order["id"]
            # Persist the new/recovered order ID in conversation state before
            # completing dependent rows.
            context.user_data["pending_order_id"] = order_id

        payments = db.table("payments").select("id").eq("order_id", order_id).limit(1).execute().data or []
        if not payments:
            db.table("payments").insert({
                "order_id": order_id, "method": method_name, "amount": p["price"],
                "status": "submitted", "receipt_file_id": receipt_id,
            }).execute()

        deliveries = db.table("deliveries").select("id").eq("order_id", order_id).limit(1).execute().data or []
        if deliveries:
            db.table("deliveries").update({
                "recipient_phone": phone, "status": "pending",
            }).eq("order_id", order_id).execute()
        else:
            db.table("deliveries").insert({
                "order_id": order_id, "recipient_phone": phone, "status": "pending",
            }).execute()
    except Exception:
        context.user_data["order_submission_in_progress"] = False
        log.exception("Could not finish checkout for customer %s", user.id)
        await update.message.reply_text(
            tr(lang, "error") + " Your receipt is retained; please retry your phone number.",
            reply_markup=customer_keyboard(lang, user.id),
        )
        return

    context.user_data.clear()
    await update.message.reply_text(
        tr(lang, "submitted"),
        reply_markup=customer_keyboard(lang, user.id),
    )
    for aid in admin_ids("verify_payments"):
        try:
            await send_order_card(context, aid, order_id)
        except Exception:
            log.exception("Could not notify admin %s", aid)


async def notify_order_customer(context, order, key):
    rows = db.table("customers").select("telegram_id").eq("id", order["customer_id"]).limit(1).execute().data or []
    if not rows:
        return
    tid = rows[0]["telegram_id"]
    await context.bot.send_message(chat_id=tid, text=tr(get_language(tid), key))

async def accept_payment(query, context, order_id):
    if not has_permission(query.from_user.id, "verify_payments"):
        await query.answer("You do not have permission.", show_alert=True)
        return
    rows = db.table("orders").select("*").eq("id", order_id).limit(1).execute().data or []
    if not rows or rows[0]["status"] != "payment_submitted":
        await query.answer("This order is no longer awaiting verification.", show_alert=True)
        return
    order = rows[0]
    db.table("orders").update({"status": "payment_accepted"}).eq("id", order_id).eq("status", "payment_submitted").execute()
    db.table("payments").update({"status": "verified"}).eq("order_id", order_id).execute()
    await notify_order_customer(context, order, "accepted")
    await safe_edit_admin_message(query, (query.message.caption or query.message.text or f"ORDER #{order_id}") + "\n\n✅ PAYMENT ACCEPTED — awaiting delivery.")
    for aid in admin_ids("manage_delivery"):
        if aid != query.from_user.id:
            try:
                await send_order_card(context, aid, order_id)
            except Exception:
                log.exception("Could not send delivery card to %s", aid)

async def reject_payment(query, context, order_id):
    if not has_permission(query.from_user.id, "verify_payments"):
        await query.answer("You do not have permission.", show_alert=True)
        return
    rows = db.table("orders").select("*").eq("id", order_id).limit(1).execute().data or []
    if not rows or rows[0]["status"] != "payment_submitted":
        await query.answer("This order is no longer awaiting verification.", show_alert=True)
        return
    order = rows[0]
    db.table("orders").update({"status": "payment_rejected"}).eq("id", order_id).eq("status", "payment_submitted").execute()
    db.table("payments").update({"status": "rejected"}).eq("order_id", order_id).execute()
    await notify_order_customer(context, order, "rejected")
    await safe_edit_admin_message(query, (query.message.caption or query.message.text or f"ORDER #{order_id}") + "\n\n❌ PAYMENT REJECTED.")

async def cancel_order(query, context, order_id):
    user_id = query.from_user.id
    rows = db.table("customers").select("id").eq("telegram_id", user_id).limit(1).execute().data or []
    lang = get_language(user_id)
    if not rows:
        await query.answer(tr(lang, "cannot_cancel"), show_alert=True)
        return
    orders = db.table("orders").select("*").eq("id", order_id).eq("customer_id", rows[0]["id"]).limit(1).execute().data or []
    if not orders or orders[0]["status"] != "payment_submitted":
        await query.answer(tr(lang, "cannot_cancel"), show_alert=True)
        return
    db.table("orders").update({"status": "cancelled"}).eq("id", order_id).eq("status", "payment_submitted").execute()
    db.table("payments").update({"status": "cancelled"}).eq("order_id", order_id).execute()
    db.table("deliveries").update({"status": "cancelled"}).eq("order_id", order_id).execute()
    await query.edit_message_text(tr(lang, "cancelled"))

async def deliver_order(query, context, order_id):
    if not has_permission(query.from_user.id, "manage_delivery"):
        await query.answer("You do not have permission.", show_alert=True)
        return
    rows = db.table("orders").select("*").eq("id", order_id).limit(1).execute().data or []
    if not rows or rows[0]["status"] != "payment_accepted":
        await query.answer("Payment must be accepted before delivery.", show_alert=True)
        return
    order = rows[0]
    db.table("orders").update({"status": "delivered"}).eq("id", order_id).eq("status", "payment_accepted").execute()
    db.table("deliveries").update({
        "status": "delivered", "delivered_at": datetime.now(timezone.utc).isoformat(),
    }).eq("order_id", order_id).execute()
    await notify_order_customer(context, order, "delivered")
    await safe_edit_admin_message(query, (query.message.caption or query.message.text or f"ORDER #{order_id}") + "\n\n📦 DELIVERED — customer notified.")

async def safe_edit_admin_message(query, text):
    try:
        if query.message.photo:
            await query.edit_message_caption(caption=text, reply_markup=None)
        else:
            await query.edit_message_text(text, reply_markup=None)
    except Exception:
        log.exception("Could not update admin order message")

async def admin_message_start(query, context, order_id=None):
    if not has_permission(query.from_user.id, "message_customers"):
        await query.answer("You do not have permission.", show_alert=True)
        return
    if order_id is not None:
        o = db.table("orders").select("customer_id").eq("id", order_id).limit(1).execute().data[0]
        c = db.table("customers").select("telegram_id").eq("id", o["customer_id"]).limit(1).execute().data[0]
        context.user_data["message_target"] = c["telegram_id"]
        context.user_data["admin_state"] = "message_body"
        await query.message.reply_text("Send the message for this customer. Use /cancel to stop.")
    else:
        context.user_data["message_target"] = None
        context.user_data["admin_state"] = "message_target"
        await query.message.reply_text("Send the customer's numeric Telegram ID. Use /cancel to stop.")

async def show_admin_packages(query):
    rows = db.table("packages").select("*").order("id").execute().data or []
    if not rows:
        await query.message.reply_text("No packages found."); return
    for p in rows:
        status = "ACTIVE" if p.get("active") else "INACTIVE"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Edit name", callback_data=f"pkg:edit:{p['id']}:name"), InlineKeyboardButton("Edit price", callback_data=f"pkg:edit:{p['id']}:price")],
            [InlineKeyboardButton("Edit data", callback_data=f"pkg:edit:{p['id']}:data_amount"), InlineKeyboardButton("Edit minutes", callback_data=f"pkg:edit:{p['id']}:voice_minutes")],
            [InlineKeyboardButton("Edit validity", callback_data=f"pkg:edit:{p['id']}:validity"), InlineKeyboardButton("Edit details", callback_data=f"pkg:edit:{p['id']}:description")],
            [InlineKeyboardButton("Deactivate" if p.get("active") else "Activate", callback_data=f"pkg:toggle:{p['id']}")],
        ])
        await query.message.reply_text(f"#{p['id']} {p['name']} — {p['price']} Birr — {status}", reply_markup=kb)

async def show_payment_methods(query):
    rows = db.table("payment_methods").select("*").order("id").execute().data or []
    if not rows:
        await query.message.reply_text("No payment methods configured.")
        return
    for m in rows:
        status = "ACTIVE" if m.get("active") else "INACTIVE"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Edit name/details/instructions", callback_data=f"pm:edit:{m['id']}")],
            [InlineKeyboardButton("Deactivate" if m.get("active") else "Activate", callback_data=f"pm:toggle:{m['id']}"),
             InlineKeyboardButton("Remove", callback_data=f"pm:remove:{m['id']}")],
        ])
        await query.message.reply_text(f"#{m['id']} {m['name']} — {status}\n{m.get('details') or ''}\n{m.get('instructions') or ''}", reply_markup=kb)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data, uid = q.data, q.from_user.id
    if data.startswith("lang:"):
        lang = data.split(":")[1]
        if lang not in TEXT: return
        save_language(q.from_user, lang)
        await q.edit_message_text(tr(lang, "welcome"))
        await q.message.reply_text(tr(lang, "welcome"), reply_markup=customer_keyboard(lang, q.from_user.id))
        return
    if data == "change_language":
        await edit_screen(q, tr(get_language(uid), "choose"), language_keyboard()); return
    if data == "home":
        await edit_screen(q, tr(get_language(uid), "welcome"), customer_inline_home(get_language(uid))); return
    if data == "packages":
        await show_packages(q, context); return
    if data.startswith("detail:"):
        await show_package_detail(q, context, int(data.split(":")[1])); return
    if data == "my_orders":
        await show_my_orders(q); return
    if data == "my_profile":
        await show_profile(q); return
    if data.startswith("promo_buy:"):
        try:
            _, promo_raw, package_raw = data.split(":", 2)
            promo_id, package_id = int(promo_raw), int(package_raw)
            promos = db.table("store_promotions").select("status,expires_at").eq("id", promo_id).limit(1).execute().data or []
            expiry_value = _dt(promos[0].get("expires_at")) if promos else None
            if not promos or promos[0].get("status") != "active" or not expiry_value or expiry_value <= datetime.now(timezone.utc):
                await edit_screen(q, "❌ This promotion has expired.", customer_inline_home(get_language(uid)))
                return
            await buy_package(q, context, package_id)
        except (TypeError, ValueError):
            await edit_screen(q, "This promotion link is no longer valid.", customer_inline_home(get_language(uid)))
        return
    if data.startswith("buy:"):
        await buy_package(q, context, int(data.split(":")[1])); return
    if data.startswith("payment:choose:"):
        await choose_payment_method(q, context, int(data.split(":")[2])); return
    if data.startswith("cancel:"):
        await cancel_order(q, context, int(data.split(":")[1])); return
    if data.startswith("pay:accept:"):
        await accept_payment(q, context, int(data.split(":")[2])); return
    if data.startswith("pay:reject:"):
        await reject_payment(q, context, int(data.split(":")[2])); return
    if data.startswith("deliver:"):
        await deliver_order(q, context, int(data.split(":")[1])); return
    if data.startswith("message_order:"):
        await admin_message_start(q, context, int(data.split(":")[1])); return

    if data.startswith("queue:"):
        await show_order_queue(q, context, data.split(":", 1)[1]); return

    if data == "service:disable_now" and owner(uid):
        set_service_control(True, datetime.now(timezone.utc), None, uid)
        await notify_service_customers(context.bot, False)
        db.table("store_service_control").update({"start_notified": True}).eq("id", 1).execute()
        await show_service_controls(q); return
    if data == "service:enable_now" and owner(uid):
        was_unavailable = service_is_unavailable()
        db.table("store_service_control").upsert({"id":1,"is_unavailable":False,"starts_at":None,"ends_at":None,"start_notified":False,"end_notified":True,"updated_by":uid,"updated_at":datetime.now(timezone.utc).isoformat()}, on_conflict="id").execute()
        if was_unavailable:
            await notify_service_customers(context.bot, True)
        context.user_data.pop("service_duration_seconds", None)
        await show_service_controls(q); return
    if data == "service:duration" and owner(uid):
        context.user_data["admin_state"] = "service_duration"
        context.user_data.pop("service_duration_seconds", None)
        await q.message.reply_text("How long should package service stay unavailable? Examples: 2h 30m, 90m, 1d 2h. Maximum 30 days.")
        return
    if data == "service:confirm_duration" and owner(uid):
        seconds = int(context.user_data.get("service_duration_seconds") or 0)
        if seconds < 60 or seconds > 30 * 86400:
            await edit_screen(q, "Please enter a valid downtime duration again.", admin_keyboard(uid))
            return
        start = datetime.now(timezone.utc)
        end = start + timedelta(seconds=seconds)
        set_service_control(True, start, end, uid)
        await notify_service_customers(context.bot, False)
        db.table("store_service_control").update({"start_notified": True}).eq("id", 1).execute()
        context.user_data.pop("service_duration_seconds", None)
        context.user_data.pop("admin_state", None)
        await show_service_controls(q); return
    if data == "service:cancel_schedule" and owner(uid):
        was_unavailable = service_is_unavailable()
        context.user_data.pop("service_duration_seconds", None)
        context.user_data.pop("admin_state", None)
        db.table("store_service_control").upsert({"id":1,"is_unavailable":False,"starts_at":None,"ends_at":None,"start_notified":False,"end_notified":False,"updated_by":uid,"updated_at":datetime.now(timezone.utc).isoformat()},on_conflict="id").execute()
        if was_unavailable:
            await notify_service_customers(context.bot, True)
        await show_service_controls(q); return
    if data.startswith("broadcast:type:") and owner(uid):
        kind=data.split(":",2)[2]
        if kind not in ("promotion","general"): return
        context.user_data["broadcast_draft"]={"type":kind}; context.user_data["admin_state"]="broadcast_text"
        await edit_screen(q,"Send the " + ("package promotion" if kind=="promotion" else "general announcement") + " text. An optional photo can follow."); return
    if data == "broadcast:skip_photo" and owner(uid):
        context.user_data["broadcast_draft"]["photo"] = None
        if context.user_data.get("broadcast_draft", {}).get("type") == "promotion":
            context.user_data["admin_state"] = "broadcast_offer"
            await edit_screen(q, "Send optional offer details, or type none:")
        else:
            context.user_data["admin_state"] = None
            await show_broadcast_preview(q, context)
        return
    if data.startswith("broadcast:package:") and owner(uid):
        pid = int(data.split(":")[2])
        active = db.table("packages").select("*").eq("id", pid).eq("active", True).limit(1).execute().data or []
        if not active:
            await q.answer("That package is no longer active.", show_alert=True); return
        context.user_data["broadcast_draft"]["package_id"] = pid
        await show_broadcast_preview(q, context)
        return
    if data == "broadcast:no_package" and owner(uid):
        context.user_data["broadcast_draft"]["package_id"] = None
        await show_broadcast_preview(q, context)
        return
    if data == "broadcast:confirm" and owner(uid):
        await send_broadcast(q, context)
        return
    if data == "broadcast:cancel" and owner(uid):
        context.user_data.pop("broadcast_draft", None)
        context.user_data.pop("admin_state", None)
        await edit_screen(q, "Broadcast cancelled.", admin_keyboard(uid))
        return

    if data.startswith("admin:"):
        action = data.split(":")[1]
        if action == "orders" and has_permission(uid, "view_orders"):
            await edit_screen(q, "🧾 Order queues — choose a status:", order_queue_keyboard(uid))
        elif action == "packages" and has_permission(uid, "manage_packages"):
            await q.message.reply_text("Package management:", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add package", callback_data="pkg:add")],
                [InlineKeyboardButton("📋 View / edit / deactivate packages", callback_data="pkg:list")],
            ]))
        elif action == "payments" and has_permission(uid, "manage_payments"):
            await q.message.reply_text("Payment methods:", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add payment method", callback_data="pm:add")],
                [InlineKeyboardButton("📋 View / edit / remove methods", callback_data="pm:list")],
            ]))
        elif action == "message" and has_permission(uid, "message_customers"):
            await admin_message_start(q, context)
        elif action == "service" and owner(uid):
            await show_service_controls(q)
        elif action == "broadcast" and owner(uid):
            context.user_data["broadcast_draft"] = {}
            await edit_screen(q, "Choose the broadcast type:", InlineKeyboardMarkup([
                [InlineKeyboardButton("🎁 Package promotion", callback_data="broadcast:type:promotion")],
                [InlineKeyboardButton("📢 General announcement", callback_data="broadcast:type:general")],
                [InlineKeyboardButton("Cancel", callback_data="broadcast:cancel")],
            ]))
        elif action == "admins" and owner(uid):
            await q.message.reply_text("Admin management:", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add admin and permissions", callback_data="admins:add")],
                [InlineKeyboardButton("➖ Revoke admin", callback_data="admins:remove")],
                [InlineKeyboardButton("📋 List admins", callback_data="admins:list")],
            ]))
        return

    if data == "pkg:add" and has_permission(uid, "manage_packages"):
        context.user_data["admin_state"] = "pkg_add_name"; context.user_data["new_package"] = {}
        await q.message.reply_text("Enter package name:"); return
    if data == "pkg:list" and has_permission(uid, "manage_packages"):
        await show_admin_packages(q); return
    if data.startswith("pkg:toggle:") and has_permission(uid, "manage_packages"):
        pid = int(data.split(":")[2])
        rows = db.table("packages").select("active").eq("id", pid).limit(1).execute().data or []
        if rows:
            db.table("packages").update({"active": not rows[0]["active"]}).eq("id", pid).execute()
            await q.edit_message_text("Package status updated.")
        return
    if data.startswith("pkg:edit:") and has_permission(uid, "manage_packages"):
        _, _, pid, field = data.split(":")
        if field not in {"name", "price", "data_amount", "voice_minutes", "validity", "description"}: return
        context.user_data["admin_state"] = f"pkg_edit:{pid}:{field}"
        await q.message.reply_text(f"Send new value for {field}. Type none to clear optional fields:"); return

    if data == "pm:add" and has_permission(uid, "manage_payments"):
        context.user_data["admin_state"] = "payment_add_name"
        context.user_data["payment_draft"] = {}
        await q.message.reply_text("Enter payment method name (e.g. CBE, Telebirr):"); return
    if data == "pm:list" and has_permission(uid, "manage_payments"):
        await show_payment_methods(q); return
    if data.startswith("pm:edit:") and has_permission(uid, "manage_payments"):
        mid = int(data.split(":")[2])
        rows = db.table("payment_methods").select("*").eq("id", mid).limit(1).execute().data or []
        if not rows: return
        context.user_data["payment_edit_id"] = mid
        context.user_data["payment_draft"] = {"name": rows[0]["name"]}
        context.user_data["admin_state"] = "payment_edit_name"
        await q.message.reply_text(f"Current name: {rows[0]['name']}\nSend the new name:"); return
    if data.startswith("pm:toggle:") and has_permission(uid, "manage_payments"):
        mid = int(data.split(":")[2])
        rows = db.table("payment_methods").select("active").eq("id", mid).limit(1).execute().data or []
        if rows:
            db.table("payment_methods").update({"active": not rows[0]["active"]}).eq("id", mid).execute()
            await q.edit_message_text("Payment method status updated.")
        return
    if data.startswith("pm:remove:") and has_permission(uid, "manage_payments"):
        mid = int(data.split(":")[2])
        # Soft remove to preserve payment history and avoid breaking existing orders.
        db.table("payment_methods").update({"active": False}).eq("id", mid).execute()
        await q.edit_message_text("Payment method deactivated (historical payments preserved).")
        return

    if data == "admins:add" and owner(uid):
        context.user_data["admin_state"] = "add_admin_id"
        await q.message.reply_text("Send the Telegram ID of the new admin:"); return
    if data == "admins:remove" and owner(uid):
        context.user_data["admin_state"] = "remove_admin_id"
        await q.message.reply_text("Send the Telegram ID whose admin access should be revoked:"); return
    if data == "admins:list" and owner(uid):
        rows = db.table("store_admins").select("*").order("telegram_id").execute().data or []
        if not rows: await q.message.reply_text("No additional admins.")
        for a in rows:
            await q.message.reply_text(f"ID: {a['telegram_id']}\nActive: {a['active']}\nPermissions: {', '.join(a.get('permissions') or []) or 'None'}")
        return

async def _broadcast_preview_content(draft):
    body=draft.get("text","")
    if draft.get("offer"):
        body += "\n\n🎁 " + draft["offer"]
    if draft.get("duration_seconds"):
        seconds=int(draft["duration_seconds"])
        body += f"\n\n⏳ Countdown starts when sent: {seconds//3600}h {(seconds%3600)//60}m"
    package=None
    if draft.get("type")=="promotion" and draft.get("package_id"):
        found=db.table("packages").select("id,name,price").eq("id",draft["package_id"]).eq("active",True).limit(1).execute().data or []
        package=found[0] if found else None
    if package:
        body += f"\n\nSelected package: {package['name']} — {package['price']} Birr"
    body += "\n\nPREVIEW — confirm to send to all registered customers."
    return body,package


async def show_broadcast_preview(query, context):
    draft=context.user_data.get("broadcast_draft",{})
    body,package=await _broadcast_preview_content(draft)
    markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirm broadcast",callback_data="broadcast:confirm")],[InlineKeyboardButton("❌ Cancel",callback_data="broadcast:cancel")]])
    if draft.get("photo"):
        await query.edit_message_text("Review the photo and announcement below:")
        await query.message.reply_photo(draft["photo"],caption=body[:1024],reply_markup=markup)
        if len(body)>1024: await query.message.reply_text(body[1024:])
    else:
        await edit_screen(query,body,markup)


async def show_broadcast_preview_from_message(update,context):
    draft=context.user_data.get("broadcast_draft",{})
    body,_=await _broadcast_preview_content(draft)
    markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirm broadcast",callback_data="broadcast:confirm")],[InlineKeyboardButton("❌ Cancel",callback_data="broadcast:cancel")]])
    if draft.get("photo"):
        await update.message.reply_photo(draft["photo"],caption=body[:1024],reply_markup=markup)
        if len(body)>1024: await update.message.reply_text(body[1024:])
    else:
        await update.message.reply_text(body,reply_markup=markup)


async def send_broadcast(query, context):
    if not owner(query.from_user.id):
        await query.answer("Owner only.",show_alert=True); return
    draft=context.user_data.get("broadcast_draft") or {}
    kind=draft.get("type","general")
    if kind not in {"promotion","general"}:
        await query.answer("Choose a broadcast type first.",show_alert=True); return
    body=draft.get("text","")
    # Duration is converted to an absolute UTC expiry only at send time.
    duration=int(draft.get("duration_seconds") or 0) if kind=="promotion" else 0
    expiry=(datetime.now(timezone.utc) + timedelta(seconds=duration)).isoformat() if duration > 0 else None
    if kind=="promotion" and draft.get("offer"):
        body += "\n\n🎁 "+draft["offer"]
    package_id=draft.get("package_id") if kind=="promotion" else None
    if expiry:
        body = body[:850]
    markup=None
    if package_id:
        active=db.table("packages").select("id,name,price,active").eq("id",package_id).eq("active",True).limit(1).execute().data or []
        if active:
            markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"🛒 Buy Now — {active[0]['name']} ({active[0]['price']} Birr)",callback_data=f"buy:{package_id}")]])
        else:
            package_id=None
    promotion_id=None
    if kind=="promotion" and expiry:
        rec=db.table("store_promotions").insert({"message":body,"photo_file_id":draft.get("photo"),"package_id":package_id,"expires_at":expiry,"status":"active"}).execute().data
        promotion_id=rec[0]["id"]
        if package_id:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton(
                f"🛒 Buy Now — {active[0]['name']} ({active[0]['price']} Birr)",
                callback_data=f"promo_buy:{promotion_id}:{package_id}"
            )]])
        if expiry:
            end=datetime.fromisoformat(expiry.replace("Z","+00:00"))
            sec=max(0,int((end-datetime.now(timezone.utc)).total_seconds()))
            body += f"\n\n⏳ Offer ends in: {sec//3600:02d}:{(sec%3600)//60:02d}:{sec%60:02d}"
    customers=db.table("customers").select("telegram_id").execute().data or []
    sent=failed=0
    for customer in customers:
        target=customer.get("telegram_id")
        if not target: continue
        try:
            if draft.get("photo"):
                msg=await context.bot.send_photo(chat_id=target,photo=draft["photo"],caption=body[:1024],reply_markup=markup)
                if len(body)>1024: await context.bot.send_message(chat_id=target,text=body[1024:])
                message_kind="photo"
            else:
                msg=await context.bot.send_message(chat_id=target,text=body,reply_markup=markup)
                message_kind="text"
            if promotion_id:
                db.table("store_promotion_deliveries").insert({"promotion_id":promotion_id,"telegram_id":int(target),"message_id":msg.message_id,"message_kind":message_kind}).execute()
            sent+=1
        except Exception:
            failed+=1
            log.warning("Broadcast could not reach customer %s",target)
    context.user_data.pop("broadcast_draft",None); context.user_data.pop("admin_state",None)
    await edit_screen(query,f"Broadcast finished. Sent: {sent}. Failed: {failed}.",admin_keyboard(query.from_user.id))


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    message = update.message.text.strip()
    uid = update.effective_user.id
    language_choices = {
        "English": "en",
        "Afaan Oromoo": "om",
        "አማርኛ": "am",
    }
    if message in language_choices and context.user_data.get("awaiting_language"):
        selected_lang = language_choices[message]
        save_language(update.effective_user, selected_lang)
        context.user_data.pop("awaiting_language", None)
        await update.message.reply_text(
            tr(selected_lang, "welcome"),
            reply_markup=customer_keyboard(selected_lang, uid),
        )
        return
    if message == "/cancel":
        if context.user_data.get("waiting_phone") and context.user_data.get("receipt_file_id"):
            await update.message.reply_text("Your receipt is saved. Send the recipient phone number to complete checkout, or use the menu to browse and view orders. Your receipt will remain saved.")
            return
        for k in list(context.user_data):
            context.user_data.pop(k, None)
        await update.message.reply_text("Current action cancelled."); return
    lang = get_language(uid)
    if message == tr(lang, "menu_admin"):
        if not get_admin(uid):
            await update.message.reply_text("You do not have admin access.")
            return
        await update.message.reply_text("Store Administration", reply_markup=admin_keyboard(uid))
        return
    menu_actions = {
        tr(lang, "menu_browse"): "packages",
        tr(lang, "menu_orders"): "my_orders",
        tr(lang, "menu_profile"): "my_profile",
        tr(lang, "menu_support"): "support",
    }
    if message in menu_actions:
        action = menu_actions[message]
        if action == "support":
            await update.message.reply_text(tr(lang, "support_text"), reply_markup=customer_keyboard(lang, uid))
        elif action == "packages":
            if service_is_unavailable():
                await update.message.reply_text(service_message(lang), reply_markup=customer_keyboard(lang, uid)); return
            rows = db.table("packages").select("*").eq("active", True).order("id").execute().data or []
            if not rows:
                await update.message.reply_text(tr(lang, "no_packages"), reply_markup=customer_keyboard(lang, uid))
            else:
                kb = [[InlineKeyboardButton(
                    f"{p.get('data_amount') or '-'} | {p.get('voice_minutes') or '—'} min | {p.get('price')} Birr"[:60],
                    callback_data=f"detail:{p['id']}"
                )] for p in rows]
                await update.message.reply_text("📦 " + tr(lang, "packages") + "\n\nChoose a package:", reply_markup=InlineKeyboardMarkup(kb))
        elif action == "my_orders":
            customers = db.table("customers").select("id").eq("telegram_id", uid).limit(1).execute().data or []
            orders = db.table("orders").select("id,package_id,status,created_at").eq("customer_id", customers[0]["id"]).order("created_at", desc=True).limit(20).execute().data or [] if customers else []
            lines = ["🧾 " + tr(lang, "menu_orders")]
            for o in orders:
                pp = db.table("packages").select("*").eq("id", o["package_id"]).limit(1).execute().data or []
                pk = pp[0] if pp else {}
                lines.append(f"\n#{o['id']} — {pk.get('name', 'Package')}\n{pk.get('data_amount') or '—'} | {pk.get('voice_minutes') or '—'} min | {pk.get('price', '—')} Birr\nDate: {(o.get('created_at') or '—')[:16]}\nStatus: {(o.get('status') or '').replace('_',' ').title()}")
            await update.message.reply_text("\n".join(lines) if orders else tr(lang, "orders_empty"), reply_markup=customer_keyboard(lang, uid))
        else:
            rows = db.table("customers").select("*").eq("telegram_id", uid).limit(1).execute().data or []
            c = rows[0] if rows else {}
            await update.message.reply_text(
                f"{tr(lang, 'profile')}\nName: {c.get('full_name') or update.effective_user.full_name}\nTelegram ID: {uid}\n{tr(lang, 'profile_language')}: {lang}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(tr(lang, "change_language"), callback_data="change_language")]])
            )
        return
    if context.user_data.get("admin_state") == "broadcast_photo" and owner(uid):
        await update.message.reply_text("Please upload a photo or choose Skip photo.")
        return
    if context.user_data.get("admin_state"):
        if not get_admin(uid):
            context.user_data.clear(); return
        await admin_text(update, context, message); return
    if context.user_data.get("waiting_phone"):
        await receive_phone(update, context)
        return


async def admin_text(update, context, message):
    uid = update.effective_user.id
    state = context.user_data.get("admin_state", "")
    if state.startswith("broadcast_"):
        if not owner(uid):
            context.user_data.pop("admin_state", None)
            context.user_data.pop("broadcast_draft", None)
            return
        draft = context.user_data.setdefault("broadcast_draft", {})
        if state == "broadcast_text":
            draft["text"] = message
            context.user_data["admin_state"] = "broadcast_photo"
            await update.message.reply_text(
                "Optional: upload one promotional photo, or skip it.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Skip photo", callback_data="broadcast:skip_photo")]])
            )
            return
        if state == "broadcast_offer":
            draft["offer"] = "" if message.lower() == "none" else message
            context.user_data["admin_state"] = "broadcast_expiry"
            await update.message.reply_text(
                "Optional countdown duration. Examples: 2h 30m, 90m, or 1h. Type none for no expiry:"
            )
            return
        if state == "broadcast_expiry":
            draft["duration_seconds"] = 0
            if message.lower() != "none":
                match = re.fullmatch(r"(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?", message.lower().strip())
                if not match or not any(match.groups()):
                    await update.message.reply_text("Enter a duration such as 2h 30m, 90m, or type none:"); return
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                total_seconds = hours * 3600 + minutes * 60
                if total_seconds <= 0 or total_seconds > 30 * 24 * 3600:
                    await update.message.reply_text("Duration must be between 1 minute and 30 days. Try again:"); return
                draft["duration_seconds"] = total_seconds
            context.user_data["admin_state"] = "broadcast_package"
            packages = db.table("packages").select("id,name,price").eq("active", True).order("id").execute().data or []
            buttons = [[InlineKeyboardButton(f"{p['name']} — {p['price']} Birr", callback_data=f"broadcast:package:{p['id']}")] for p in packages]
            buttons.append([InlineKeyboardButton("No package link", callback_data="broadcast:no_package")])
            await update.message.reply_text("Optionally select a package for the Buy Now button:", reply_markup=InlineKeyboardMarkup(buttons))
            return
    if state == "service_duration" and owner(uid):
        match = re.fullmatch(r"(?:(\d+)\s*d)?\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?", message.lower().strip())
        if not match or not any(match.groups()):
            await update.message.reply_text("Enter a duration such as 2h 30m, 90m, or 1d 2h. Type /cancel to stop.")
            return
        days, hours, minutes = (int(x or 0) for x in match.groups())
        seconds = days * 86400 + hours * 3600 + minutes * 60
        if seconds < 60 or seconds > 30 * 86400:
            await update.message.reply_text("Duration must be between 1 minute and 30 days. Try again:")
            return
        context.user_data["service_duration_seconds"] = seconds
        context.user_data["admin_state"] = None
        total_minutes = seconds // 60
        summary = f"{total_minutes // 1440}d {(total_minutes % 1440) // 60}h {total_minutes % 60}m"
        await update.message.reply_text(
            f"Disable package service for {summary}? It will automatically become available again when the countdown ends.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Confirm downtime", callback_data="service:confirm_duration")],
                [InlineKeyboardButton("Cancel", callback_data="service:cancel_schedule")],
            ]),
        )
        return
    if state == "message_target":
        if not has_permission(uid, "message_customers"): return
        if not message.isdigit():
            await update.message.reply_text("Send a numeric Telegram ID."); return
        context.user_data["message_target"] = int(message)
        context.user_data["admin_state"] = "message_body"
        await update.message.reply_text("Now send the message."); return
    if state == "message_body":
        target = context.user_data.get("message_target")
        if not has_permission(uid, "message_customers"): return
        try:
            await context.bot.send_message(target, f"{tr(get_language(target), 'message_received')}\n\n{message}")
            await update.message.reply_text("Message sent.")
        except Exception:
            await update.message.reply_text("Could not send message. Confirm the customer has started the bot.")
        context.user_data.pop("admin_state", None); context.user_data.pop("message_target", None); return

    if state in {"payment_add_name", "payment_edit_name"}:
        if not has_permission(uid, "manage_payments"): return
        context.user_data.setdefault("payment_draft", {})["name"] = message
        if state == "payment_edit_name":
            context.user_data["admin_state"] = f"payment_edit_details:{context.user_data['payment_edit_id']}"
        else:
            context.user_data["admin_state"] = "payment_add_details"
        await update.message.reply_text("Send payment details (account holder, account number, wallet ID, etc.):"); return
    if state.startswith("payment_add_details") or state.startswith("payment_edit_details:"):
        if not has_permission(uid, "manage_payments"): return
        context.user_data.setdefault("payment_draft", {})["details"] = message
        context.user_data["admin_state"] = "payment_add_instructions" if state == "payment_add_details" else f"payment_edit_instructions:{context.user_data['payment_edit_id']}"
        await update.message.reply_text("Send customer instructions, or type none:"); return
    if state == "payment_add_instructions" or state.startswith("payment_edit_instructions:"):
        if not has_permission(uid, "manage_payments"): return
        draft = context.user_data.get("payment_draft", {})
        draft["instructions"] = "" if message.lower() == "none" else message
        draft["active"] = True
        if state == "payment_add_instructions":
            db.table("payment_methods").insert(draft).execute()
            await update.message.reply_text("Payment method added.")
        else:
            db.table("payment_methods").update(draft).eq("id", context.user_data["payment_edit_id"]).execute()
            await update.message.reply_text("Payment method updated.")
        for k in ("admin_state", "payment_draft", "payment_edit_id"): context.user_data.pop(k, None)
        return

    if state == "add_admin_id":
        if not owner(uid): return
        if not message.isdigit():
            await update.message.reply_text("Send a numeric Telegram ID."); return
        new_id = int(message)
        if new_id == OWNER_ID:
            await update.message.reply_text("Owner already has full access."); return
        context.user_data["new_admin_id"] = new_id
        context.user_data["admin_state"] = "add_admin_permissions"
        await update.message.reply_text("Send permission keys separated by commas, or 'all':\n" + "\n".join(f"{k} — {v}" for k,v in PERMISSIONS.items())); return
    if state == "add_admin_permissions":
        if not owner(uid): return
        perms = list(PERMISSIONS) if message.lower() == "all" else [x.strip() for x in message.split(",") if x.strip()]
        invalid = [x for x in perms if x not in PERMISSIONS]
        if invalid:
            await update.message.reply_text("Unknown permission(s): " + ", ".join(invalid)); return
        db.table("store_admins").upsert({"telegram_id": context.user_data["new_admin_id"], "permissions": perms, "active": True}, on_conflict="telegram_id").execute()
        await update.message.reply_text("Admin saved. Permissions: " + (", ".join(perms) or "None"))
        context.user_data.pop("admin_state", None); context.user_data.pop("new_admin_id", None); return
    if state == "remove_admin_id":
        if not owner(uid): return
        if not message.isdigit():
            await update.message.reply_text("Send a numeric Telegram ID."); return
        target = int(message)
        if target == OWNER_ID:
            await update.message.reply_text("Owner cannot be removed."); return
        db.table("store_admins").update({"active": False}).eq("telegram_id", target).execute()
        await update.message.reply_text("Admin access revoked if that ID existed.")
        context.user_data.pop("admin_state", None); return

    if state == "pkg_add_name":
        if not has_permission(uid, "manage_packages"): return
        context.user_data["new_package"] = {"name": message}
        context.user_data["admin_state"] = "pkg_add_data"
        await update.message.reply_text("Enter data amount (e.g. 10 GB):"); return
    if state == "pkg_add_data":
        context.user_data["new_package"]["data_amount"] = message
        context.user_data["admin_state"] = "pkg_add_minutes"
        await update.message.reply_text("Enter voice minutes, or type none:"); return
    if state == "pkg_add_minutes":
        context.user_data["new_package"]["voice_minutes"] = None if message.lower() == "none" else message
        context.user_data["admin_state"] = "pkg_add_price"
        await update.message.reply_text("Enter price in Birr:"); return
    if state == "pkg_add_price":
        try: context.user_data["new_package"]["price"] = float(message)
        except ValueError:
            await update.message.reply_text("Enter a numeric price."); return
        context.user_data["admin_state"] = "pkg_add_validity"
        await update.message.reply_text("Enter validity (e.g. 3 months):"); return
    if state == "pkg_add_validity":
        context.user_data["new_package"]["validity"] = message
        context.user_data["admin_state"] = "pkg_add_description"
        await update.message.reply_text("Enter bonus/details, or type none:"); return
    if state == "pkg_add_description":
        p = context.user_data["new_package"]
        p["description"] = "" if message.lower() == "none" else message
        p["active"] = True
        db.table("packages").insert(p).execute()
        context.user_data.pop("new_package", None); context.user_data.pop("admin_state", None)
        await update.message.reply_text("Package added."); return
    if state.startswith("pkg_edit:"):
        if not has_permission(uid, "manage_packages"): return
        _, pid, field = state.split(":")
        if field not in {"name", "price", "data_amount", "voice_minutes", "validity", "description"}: return
        value = message
        if field == "price":
            try: value = float(message)
            except ValueError:
                await update.message.reply_text("Enter a numeric price."); return
        if field in {"voice_minutes", "description"} and message.lower() == "none":
            value = None if field == "voice_minutes" else ""
        db.table("packages").update({field: value}).eq("id", int(pid)).execute()
        context.user_data.pop("admin_state", None)
        await update.message.reply_text("Package updated."); return

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("admin_state") == "broadcast_photo":
        if not owner(update.effective_user.id):
            return
        context.user_data.setdefault("broadcast_draft", {})["photo"] = update.message.photo[-1].file_id
        if context.user_data.get("broadcast_draft", {}).get("type") == "promotion":
            context.user_data["admin_state"] = "broadcast_offer"
            await update.message.reply_text("Photo saved. Send optional offer details, or type none:")
        else:
            context.user_data.pop("admin_state",None)
            await show_broadcast_preview_from_message(update, context)
        return
    await receive_photo(update, context)
