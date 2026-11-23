import os
import re
import logging
from datetime import datetime, timezone
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
        "payment_details": "የክፍያ መረጃ", "pay_instruction": "በመረጡት ዘዴ ይክፈሉ፣ ከዚያም የደረሰኝ ፎቶ ይላኩ።",
    },
}

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

def customer_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(lang, "packages"), callback_data="packages")],
        [InlineKeyboardButton(tr(lang, "change_language"), callback_data="change_language")],
        [InlineKeyboardButton(tr(lang, "contact"), url=CONTACT_URL)],
    ])

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
        rows.append([InlineKeyboardButton("👮 Manage admins", callback_data="admin:admins")])
    return InlineKeyboardMarkup(rows)

def active_payment_methods():
    return db.table("payment_methods").select("*").eq("active", True).order("id").execute().data or []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    rows = db.table("customers").select("language").eq("telegram_id", user.id).execute().data or []
    if rows and rows[0].get("language") in TEXT:
        lang = rows[0]["language"]
        await update.message.reply_text(tr(lang, "welcome"), reply_markup=customer_keyboard(lang))
    else:
        await update.message.reply_text("Choose your language / Afaan filadhaa / ቋንቋ ይምረጡ:", reply_markup=language_keyboard())

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not get_admin(uid):
        await update.message.reply_text("You do not have admin access.")
        return
    await update.message.reply_text("Store Administration", reply_markup=admin_keyboard(uid))

async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not has_permission(uid, "view_orders"):
        await update.message.reply_text("You do not have permission.")
        return
    rows = db.table("orders").select("id").order("created_at", desc=True).limit(30).execute().data or []
    if not rows:
        await update.message.reply_text("No orders found.")
        return
    for row in rows:
        await send_order_card(context, update.effective_chat.id, row["id"])

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
    rows = db.table("packages").select("*").eq("active", True).order("id").execute().data or []
    if not rows:
        await query.message.reply_text(tr(lang, "no_packages"))
        return
    for p in rows:
        msg = (f"📦 {p.get('name')}\n🌐 {tr(lang,'data')}: {p.get('data_amount') or '-'}\n"
               f"📞 {tr(lang,'minutes')}: {p.get('voice_minutes') or tr(lang,'not_specified')}\n"
               f"⏳ {tr(lang,'validity')}: {p.get('validity') or '-'}\n"
               f"💰 {tr(lang,'price')}: {p.get('price')} Birr\n"
               f"🎁 {tr(lang,'bonus')}: {p.get('description') or '-'}")
        await query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(tr(lang, "buy"), callback_data=f"buy:{p['id']}")
        ]]))

async def buy_package(query, context, package_id):
    lang = get_language(query.from_user.id)
    rows = db.table("packages").select("*").eq("id", package_id).eq("active", True).limit(1).execute().data or []
    if not rows:
        await query.message.reply_text(tr(lang, "no_packages"))
        return
    methods = active_payment_methods()
    if not methods:
        await query.message.reply_text(tr(lang, "payment_missing"))
        return
    p = rows[0]
    context.user_data.clear()
    context.user_data.update({"package_id": package_id, "waiting_payment_method": True})
    buttons = [[InlineKeyboardButton(m["name"], callback_data=f"payment:choose:{m['id']}")] for m in methods]
    buttons.append([InlineKeyboardButton(tr(lang, "back"), callback_data="packages")])
    await query.message.reply_text(
        f"📦 {p['name']}\n💰 {tr(lang,'amount')}: {p['price']} Birr\n\n{tr(lang,'choose_payment')}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def choose_payment_method(query, context, method_id):
    lang = get_language(query.from_user.id)
    rows = db.table("payment_methods").select("*").eq("id", method_id).eq("active", True).limit(1).execute().data or []
    if not rows:
        await query.message.reply_text(tr(lang, "payment_missing"))
        return
    method = rows[0]
    p_rows = db.table("packages").select("*").eq("id", context.user_data.get("package_id")).eq("active", True).limit(1).execute().data or []
    if not p_rows:
        await query.message.reply_text(tr(lang, "no_packages"))
        return
    p = p_rows[0]
    context.user_data.update({
        "payment_method_id": method_id, "payment_method_name": method["name"],
        "waiting_receipt": True, "waiting_payment_method": False,
    })
    await query.message.reply_text(
        f"📦 {p['name']}\n💰 {tr(lang,'amount')}: {p['price']} Birr\n\n"
        f"🏦 {tr(lang,'payment_details')}: {method['name']}\n{method.get('details') or ''}\n\n"
        f"{method.get('instructions') or tr(lang,'pay_instruction')}\n\n{tr(lang,'receipt')}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(tr(lang, "back"), callback_data="packages")]])
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
    phone = re.sub(r"[\s-]", "", (update.message.text or "").strip())
    if not context.user_data.get("waiting_phone"):
        return
    if not re.fullmatch(r"\+?\d{9,15}", phone):
        await update.message.reply_text(tr(lang, "invalid_phone"))
        return
    receipt_id = context.user_data.get("receipt_file_id")
    package_id = context.user_data.get("package_id")
    method_name = context.user_data.get("payment_method_name")
    if not receipt_id or not package_id or not method_name:
        await update.message.reply_text(tr(lang, "error"))
        context.user_data.clear()
        return
    customer_rows = db.table("customers").select("id").eq("telegram_id", user.id).limit(1).execute().data or []
    package_rows = db.table("packages").select("*").eq("id", package_id).eq("active", True).limit(1).execute().data or []
    if not customer_rows or not package_rows:
        await update.message.reply_text(tr(lang, "error"))
        context.user_data.clear()
        return
    p = package_rows[0]
    order = db.table("orders").insert({
        "customer_id": customer_rows[0]["id"], "package_id": package_id,
        "status": "payment_submitted",
    }).execute().data[0]
    order_id = order["id"]
    db.table("payments").insert({
        "order_id": order_id, "method": method_name, "amount": p["price"],
        "status": "submitted", "receipt_file_id": receipt_id,
    }).execute()
    db.table("deliveries").insert({
        "order_id": order_id, "recipient_phone": phone, "status": "pending",
    }).execute()
    context.user_data.clear()
    await update.message.reply_text(
        tr(lang, "submitted"),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(tr(lang, "cancel"), callback_data=f"cancel:{order_id}")]])
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

async def admin_text(update, context, message):
    uid = update.effective_user.id
    state = context.user_data.get("admin_state")
    if state == "message_target":
        if not has_permission(uid, "message_customers"):
            return
        if not message.isdigit():
            await update.message.reply_text("Please enter a numeric Telegram ID.")
            return
        context.user_data["message_target"] = int(message)
        context.user_data["admin_state"] = "message_body"
        await update.message.reply_text("Now send the message.")
        return
    if state == "message_body":
        if not has_permission(uid, "message_customers"):
            return
        target = context.user_data.get("message_target")
        try:
            await context.bot.send_message(chat_id=target, text=f"{tr(get_language(target), 'message_received')}\n\n{message}")
            await update.message.reply_text("Message sent successfully.")
        except Exception:
            await update.message.reply_text("Message could not be sent. Confirm the Telegram ID and that the customer has started the bot.")
        context.user_data.pop("admin_state", None)
        context.user_data.pop("message_target", None)
        return

    if state in ("payment_add_name", "payment_edit_name"):
        if not has_permission(uid, "manage_payments"): return
        context.user_data["payment_draft"] = {"name": message}
        context.user_data["admin_state"] = "payment_add_details" if state == "payment_add_name" else f"payment_edit_details:{context.user_data['payment_edit_id']}"
        await update.message.reply_text("Send account details (account name, number, wallet ID, etc.) in one message:")
        return
    if state.startswith("payment_add_details") or state.startswith("payment_edit_details:"):
        if not has_permission(uid, "manage_payments"): return
        draft = context.user_data.setdefault("payment_draft", {})
        draft["details"] = message
        context.user_data["admin_state"] = "payment_add_instructions" if state == "payment_add_details" else f"payment_edit_instructions:{context.user_data['payment_edit_id']}"
        await update.message.reply_text("Send customer payment instructions, or type none:")
        return
    if state in ("payment_add_instructions",) or state.startswith("payment_edit_instructions:"):
        if not has_permission(uid, "manage_payments"): return
        draft = context.user_data.get("payment_draft", {})
        draft["instructions"] = "" if message.lower() == "none" else message
        draft["active"] = True
        if state == "payment_add_instructions":
            db.table("payment_methods").insert(draft).execute()
            await update.message.reply_text("Payment method added.")
        else:
            method_id = int(state.split(":")[1])
            db.table("payment_methods").update(draft).eq("id", method_id).execute()
            await update.message.reply_text("Payment method updated.")
        context.user_data.pop("admin_state", None)
        context.user_data.pop("payment_draft", None)
        context.user_data.pop("payment_edit_id", None)
        return

    if state == "message_body": return
    if state == "add_admin_id":
        if not owner(uid): return
        if not message.isdigit():
            await update.message.reply_text("Send a numeric Telegram ID."); return
        new_id = int(message)
        if new_id == OWNER_ID:
            await update.message.reply_text("The owner already has full access."); return
        context.user_data["new_admin_id"] = new_id
        context.user_data["admin_state"] = "add_admin_permissions"
        await update.message.reply_text("Send permission keys separated by commas, or 'all':\n" + "\n".join(f"{k} — {v}" for k,v in PERMISSIONS.items()))
        return
    if state == "add_admin_permissions":
        if not owner(uid): return
        new_id = context.user_data.get("new_admin_id")
        permissions = list(PERMISSIONS) if message.lower() == "all" else [x.strip() for x in message.split(",") if x.strip()]
        invalid = [x for x in permissions if x not in PERMISSIONS]
        if invalid:
            await update.message.reply_text("Unknown permission(s): " + ", ".join(invalid)); return
        db.table("store_admins").upsert({"telegram_id": new_id, "permissions": permissions, "active": True}, on_conflict="telegram_id").execute()
        await update.message.reply_text(f"Admin {new_id} saved. Permissions: {', '.join(permissions) or 'None'}")
        context.user_data.pop("admin_state", None); context.user_data.pop("new_admin_id", None)
        return
    if state == "remove_admin_id":
        if not owner(uid): return
        if not message.isdigit():
            await update.message.reply_text("Send a numeric Telegram ID."); return
        target = int(message)
        if target == OWNER_ID:
            await update.message.reply_text("The owner cannot be removed."); return
        db.table("store_admins").update({"active": False}).eq("telegram_id", target).execute()
        await update.message.reply_text("Admin access revoked if that ID existed.")
        context.user_data.pop("admin_state", None)
        return

    if state == "pkg_add_name":
        if not has_permission(uid, "manage_packages"): return
        context.user_data["new_package"] = {"name": message}
        context.user_data["admin_state"] = "pkg_add_data"
        await update.message.reply_text("Enter data amount, e.g. 10 GB:"); return
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
        await update.message.reply_text("Enter validity, e.g. 3 months:"); return
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
        await update.message.reply_text("Package added successfully."); return
    if state.startswith("pkg_edit:"):
        if not has_permission(uid, "manage_packages"): return
        _, pid, field = state.split(":")
        allowed = {"name", "price", "data_amount", "voice_minutes", "validity", "description"}
        if field not in allowed: return
        value = message
        if field == "price":
            try: value = float(message)
            except ValueError:
                await update.message.reply_text("Enter a numeric price."); return
        elif field == "voice_minutes" and message.lower() == "none":
            value = None
        elif field == "description" and message.lower() == "none":
            value = ""
        db.table("packages").update({field: value}).eq("id", int(pid)).execute()
        context.user_data.pop("admin_state", None)
        await update.message.reply_text("Package updated successfully."); return
    if state == "payment_edit_name":
        return

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
        await q.edit_message_text(tr(lang, "welcome"), reply_markup=customer_keyboard(lang)); return
    if data == "change_language":
        await q.message.reply_text(tr(get_language(uid), "choose"), reply_markup=language_keyboard()); return
    if data == "packages":
        await show_packages(q, context); return
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

    if data.startswith("admin:"):
        action = data.split(":")[1]
        if action == "orders" and has_permission(uid, "view_orders"):
            rows = db.table("orders").select("id").order("created_at", desc=True).limit(30).execute().data or []
            if not rows: await q.message.reply_text("No orders found.")
            for r in rows: await send_order_card(context, q.message.chat_id, r["id"])
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

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    message = update.message.text.strip()
    uid = update.effective_user.id
    if message == "/cancel":
        for k in list(context.user_data):
            context.user_data.pop(k, None)
        await update.message.reply_text("Current action cancelled."); return
    if context.user_data.get("admin_state"):
        if not get_admin(uid):
            context.user_data.clear(); return
        await admin_text(update, context, message); return
    if context.user_data.get("waiting_phone"):
        await receive_phone(update, context)

async def admin_text(update, context, message):
    uid = update.effective_user.id
    state = context.user_data.get("admin_state", "")
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
    await receive_photo(update, context)
