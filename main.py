
import os
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from supabase import create_client

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

BOT_TOKEN = os.environ["BOT_TOKEN"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

ADMIN_ID = 6806823032
db = create_client(SUPABASE_URL, SUPABASE_KEY)

TEXT = {
    "en": {
        "welcome": "Welcome to Ethio Telecom Packages Store!",
        "packages": "Available Packages",
        "buy": "Buy Package",
        "phone": "Please send your Ethio Telecom phone number:",
        "contact": "Contact Admin",
        "order": "Your order and payment screenshot have been submitted. Please wait for verification.",
        "payment": "Please pay the amount below using CBE, then upload a screenshot of your payment receipt.",
        "screenshot": "Please upload your payment screenshot as a photo.",
        "back": "Back"
    },
    "om": {
        "welcome": "Baga gara Ethio Telecom Packages Store dhuftan!",
        "packages": "Paakeejiiwwan Jiran",
        "buy": "Paakeejii Bitadhu",
        "phone": "Lakkoofsa bilbilaa Ethio Telecom keessan ergaa:",
        "contact": "Admin qunnamaa",
        "order": "Ajajni fi ragaan kaffaltii keessan ergameera. Mirkaneessa eeggadhaa.",
        "payment": "Maaloo CBE fayyadamuun kaffalaa, achiis suuraa ragaa kaffaltii ergaa.",
        "screenshot": "Maaloo suuraa ragaa kaffaltii keessanii ergaa.",
        "back": "Duubatti"
    },
    "am": {
        "welcome": "ወደ Ethio Telecom Packages Store እንኳን በደህና መጡ!",
        "packages": "ያሉ ፓኬጆች",
        "buy": "ፓኬጅ ይግዙ",
        "phone": "የኢትዮ ቴሌኮም ስልክ ቁጥርዎን ይላኩ፦",
        "contact": "አስተዳዳሪን ያግኙ",
        "order": "ትዕዛዝዎና የክፍያ ማረጋገጫዎ ተልኳል። ማረጋገጫ ይጠብቁ።",
        "payment": "እባክዎ በCBE ይክፈሉ፣ ከዚያ የክፍያ ደረሰኝ ፎቶ ይላኩ።",
        "screenshot": "እባክዎ የክፍያ ደረሰኝ ፎቶ ይላኩ።",
        "back": "ተመለስ"
    }
}


def language_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("English", callback_data="lang_en"),
        InlineKeyboardButton("Afaan Oromoo", callback_data="lang_om"),
        InlineKeyboardButton("አማርኛ", callback_data="lang_am")
    ]])


def menu_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXT[lang]["packages"], callback_data="packages")],
        [InlineKeyboardButton(TEXT[lang]["contact"],
                              url="https://t.me/mosiservicespro")]
    ])


def admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Set CBE Account Name", callback_data="admin_name")],
        [InlineKeyboardButton("Set CBE Account Number", callback_data="admin_number")],
        [InlineKeyboardButton("View Current CBE Details", callback_data="admin_view")]
    ])


async def get_setting(key):
    result = db.table("store_settings").select("setting_value").eq(
        "setting_key", key
    ).execute()
    return result.data[0]["setting_value"] if result.data else None


async def save_setting(key, value):
    db.table("store_settings").upsert({
        "setting_key": key,
        "setting_value": value
    }, on_conflict="setting_key").execute()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Choose your language / Afaan filadhaa / ቋንቋ ይምረጡ:",
        reply_markup=language_keyboard()
    )


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data.replace("lang_", "")
    context.user_data["lang"] = lang

    user = query.from_user
    db.table("customers").upsert({
        "telegram_id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "language": lang
    }, on_conflict="telegram_id").execute()

    await query.edit_message_text(
        TEXT[lang]["welcome"],
        reply_markup=menu_keyboard(lang)
    )


async def show_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")

    result = db.table("packages").select("*").eq(
        "active", True
    ).order("id").execute()

    packages = result.data or []
    if not packages:
        await query.message.reply_text("No packages are currently available.")
        return

    for p in packages:
        message = (
            f"📦 {p['name']}\n"
            f"🌐 Data: {p['data_amount']}\n"
            f"📞 Minutes: {p.get('voice_minutes') or 'Not specified'}\n"
            f"⏳ Validity: {p['validity']}\n"
            f"💰 Price: {p['price']} Birr\n\n"
            f"🎁 {p.get('description') or ''}"
        )
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                TEXT[lang]["buy"],
                callback_data=f"buy_{p['id']}"
            )
        ]])
        await query.message.reply_text(message, reply_markup=keyboard)


async def buy_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    package_id = int(query.data.replace("buy_", ""))
    package = db.table("packages").select("*").eq(
        "id", package_id
    ).single().execute().data

    account_name = await get_setting("cbe_account_name")
    account_number = await get_setting("cbe_account_number")

    if not account_name or not account_number:
        await query.message.reply_text(
            "Payment details are not configured yet. Please contact the admin."
        )
        return

    context.user_data["package_id"] = package_id
    context.user_data["waiting_receipt"] = True
    context.user_data["waiting_phone"] = False
    context.user_data.pop("receipt_file_id", None)

    lang = context.user_data.get("lang", "en")
    await query.message.reply_text(
        f"📦 {package['name']}\n"
        f"💰 Amount: {package['price']} Birr\n\n"
        f"🏦 CBE PAYMENT DETAILS\n"
        f"Account Name: {account_name}\n"
        f"Account Number: {account_number}\n\n"
        f"{TEXT[lang]['payment']}\n\n"
        f"{TEXT[lang]['screenshot']}"
    )


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_receipt"):
        return

    photo = update.message.photo[-1]
    context.user_data["receipt_file_id"] = photo.file_id
    context.user_data["waiting_receipt"] = False
    context.user_data["waiting_phone"] = True

    lang = context.user_data.get("lang", "en")
    await update.message.reply_text(TEXT[lang]["phone"])


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message.text.strip()

    # Admin account settings
    if user.id == ADMIN_ID and context.user_data.get("admin_waiting"):
        setting = context.user_data.pop("admin_waiting")
        if setting == "name":
            await save_setting("cbe_account_name", message)
            await update.message.reply_text("CBE account name saved successfully.")
        elif setting == "number":
            await save_setting("cbe_account_number", message)
            await update.message.reply_text("CBE account number saved successfully.")
        return

    if not context.user_data.get("waiting_phone"):
        return

    phone = message.replace(" ", "").replace("-", "")
    if not phone.replace("+", "").isdigit() or len(phone) < 9:
        await update.message.reply_text("Please send a valid phone number.")
        return

    receipt_file_id = context.user_data.get("receipt_file_id")
    package_id = context.user_data.get("package_id")

    if not receipt_file_id or not package_id:
        await update.message.reply_text("Please start the purchase again using /start.")
        return

    customer = db.table("customers").select("id").eq(
        "telegram_id", user.id
    ).execute()

    if not customer.data:
        await update.message.reply_text("Please use /start first.")
        return

    package = db.table("packages").select("*").eq(
        "id", package_id
    ).single().execute().data

    order = db.table("orders").insert({
        "customer_id": customer.data[0]["id"],
        "package_id": package_id,
        "status": "payment_submitted"
    }).execute()

    order_id = order.data[0]["id"]

    db.table("payments").insert({
        "order_id": order_id,
        "method": "CBE",
        "amount": package["price"],
        "status": "submitted",
        "receipt_file_id": receipt_file_id
    }).execute()

    db.table("deliveries").insert({
        "order_id": order_id,
        "recipient_phone": phone,
        "status": "pending"
    }).execute()

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "Mark Delivered & Notify Customer",
            callback_data=f"deliver_{order_id}"
        )
    ]])

    caption = (
        f"🛒 NEW ORDER #{order_id}\n"
        f"Customer: {user.full_name}\n"
        f"Telegram ID: {user.id}\n"
        f"Phone: {phone}\n"
        f"Package: {package['name']}\n"
        f"Price: {package['price']} Birr\n"
        f"Payment: Screenshot submitted — verify manually."
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=receipt_file_id,
        caption=caption,
        reply_markup=keyboard
    )

    lang = context.user_data.get("lang", "en")
    await update.message.reply_text(TEXT[lang]["order"])

    context.user_data["waiting_phone"] = False
    context.user_data.pop("waiting_receipt", None)
    context.user_data.pop("receipt_file_id", None)
    context.user_data.pop("package_id", None)


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(
        "Store Admin Settings:",
        reply_markup=admin_keyboard()
    )


async def admin_settings_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    if query.data == "admin_name":
        context.user_data["admin_waiting"] = "name"
        await query.message.reply_text("Send the new CBE account holder name:")
    elif query.data == "admin_number":
        context.user_data["admin_waiting"] = "number"
        await query.message.reply_text("Send the new CBE account number:")
    elif query.data == "admin_view":
        name = await get_setting("cbe_account_name") or "Not set"
        number = await get_setting("cbe_account_number") or "Not set"
        await query.message.reply_text(
            f"Current CBE details:\nAccount Name: {name}\nAccount Number: {number}"
        )


async def deliver_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    order_id = int(query.data.replace("deliver_", ""))

    order = db.table("orders").select("*").eq(
        "id", order_id
    ).single().execute().data

    customer = db.table("customers").select("telegram_id").eq(
        "id", order["customer_id"]
    ).single().execute().data

    db.table("orders").update({
        "status": "delivered"
    }).eq("id", order_id).execute()

    db.table("deliveries").update({
        "status": "delivered",
        "delivered_at": "now()"
    }).eq("order_id", order_id).execute()

    await context.bot.send_message(
        chat_id=customer["telegram_id"],
        text=(
            f"✅ Your order #{order_id} has been completed!\n"
            "Your Ethio Telecom package has been delivered. Thank you for choosing us!"
        )
    )

    await query.edit_message_caption(
        caption=query.message.caption + "\n\n✅ Marked delivered. Customer notified.",
        reply_markup=None
    )


async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    result = db.table("orders").select("*").eq(
        "status", "payment_submitted"
    ).execute()

    if not result.data:
        await update.message.reply_text("No pending orders.")
        return

    for order in result.data:
        await update.message.reply_text(f"Order #{order['id']} — payment submitted.")


