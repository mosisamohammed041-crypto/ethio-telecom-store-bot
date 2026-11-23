
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from supabase import create_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        "order": "Your order has been received. Please wait for payment instructions.",
        "back": "Back"
    },
    "om": {
        "welcome": "Baga gara Ethio Telecom Packages Store dhuftan!",
        "packages": "Paakeejiiwwan Jiran",
        "buy": "Paakeejii Bitadhu",
        "phone": "Lakkoofsa bilbilaa Ethio Telecom keessan ergaa:",
        "contact": "Admin qunnamaa",
        "order": "Ajajni keessan fudhatameera.",
        "back": "Duubatti"
    },
    "am": {
        "welcome": "ወደ Ethio Telecom Packages Store እንኳን በደህና መጡ!",
        "packages": "ያሉ ፓኬጆች",
        "buy": "ፓኬጅ ይግዙ",
        "phone": "የኢትዮ ቴሌኮም ስልክ ቁጥርዎን ይላኩ፦",
        "contact": "አስተዳዳሪን ያግኙ",
        "order": "ትዕዛዝዎ ተቀብሏል።",
        "back": "ተመለስ"
    }
}

def language_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("English", callback_data="lang_en"),
            InlineKeyboardButton("Afaan Oromoo", callback_data="lang_om"),
            InlineKeyboardButton("አማርኛ", callback_data="lang_am")
        ]
    ])

def menu_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXT[lang]["packages"], callback_data="packages")],
        [InlineKeyboardButton(TEXT[lang]["contact"], url="https://t.me/mosiservicespro")]
    ])

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

    result = db.table("packages").select("*").eq("active", True).order("id").execute()
    packages = result.data or []

    if not packages:
        await query.message.reply_text("No packages are currently available.")
        return

    for p in packages:
        description = p.get("description") or ""
        message = (
            f"📦 {p['name']}\n"
            f"🌐 Data: {p['data_amount']}\n"
            f"📞 Minutes: {p.get('voice_minutes') or 'Not specified'}\n"
            f"⏳ Validity: {p['validity']}\n"
            f"💰 Price: {p['price']} Birr\n\n"
            f"🎁 {description}"
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

    context.user_data["package_id"] = package_id
    await query.message.reply_text(
        TEXT[context.user_data.get("lang", "en")]["phone"]
    )
    context.user_data["waiting_phone"] = True

async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_phone"):
        return

    phone = update.message.text.strip()
    if not phone.replace("+", "").isdigit() or len(phone) < 9:
        await update.message.reply_text("Please send a valid phone number.")
        return

    user = update.effective_user
    customer = db.table("customers").select("id").eq(
        "telegram_id", user.id
    ).execute()

    if not customer.data:
        await update.message.reply_text("Please use /start first.")
        return

    package_id = context.user_data["package_id"]
    order = db.table("orders").insert({
        "customer_id": customer.data[0]["id"],
        "package_id": package_id,
        "status": "pending"
    }).execute()

    order_id = order.data[0]["id"]

    db.table("deliveries").insert({
        "order_id": order_id,
        "recipient_phone": phone,
        "status": "pending"
    }).execute()

    package = db.table("packages").select("*").eq("id", package_id).single().execute().data

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🛒 NEW ORDER #{order_id}\n"
            f"Customer: {user.full_name}\n"
            f"Telegram ID: {user.id}\n"
            f"Phone: {phone}\n"
            f"Package: {package['name']}\n"
            f"Price: {package['price']} Birr"
        )
    )

    await update.message.reply_text(
        TEXT[context.user_data.get("lang", "en")]["order"]
    )
    context.user_data["waiting_phone"] = False

async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    result = db.table("orders").select("*").eq("status", "pending").execute()
    if not result.data:
        await update.message.reply_text("No pending orders.")
        return
    for order in result.data:
        await update.message.reply_text(f"Pending order #{order['id']}")

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("orders", admin_orders))
    app.add_handler(CallbackQueryHandler(choose_language, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(show_packages, pattern="^packages$"))
    app.add_handler(CallbackQueryHandler(buy_package, pattern="^buy_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
  
