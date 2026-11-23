
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from main import (
    BOT_TOKEN,
    start,
    choose_language,
    show_packages,
    buy_package,
    receive_phone,
    receive_photo,
    admin_orders,
    admin_panel,
    admin_settings_callback,
    deliver_order
)

WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
BASE_URL = "https://ethio-telecom-packages-bot.onrender.com"

telegram_app = Application.builder().token(BOT_TOKEN).build()

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("orders", admin_orders))
telegram_app.add_handler(CommandHandler("admin", admin_panel))

telegram_app.add_handler(
    CallbackQueryHandler(choose_language, pattern="^lang_")
)
telegram_app.add_handler(
    CallbackQueryHandler(show_packages, pattern="^packages$")
)
telegram_app.add_handler(
    CallbackQueryHandler(buy_package, pattern="^buy_")
)
telegram_app.add_handler(
    CallbackQueryHandler(admin_settings_callback, pattern="^admin_(name|number|view)$")
)
telegram_app.add_handler(
    CallbackQueryHandler(deliver_order, pattern="^deliver_")
)

telegram_app.add_handler(
    MessageHandler(filters.PHOTO, receive_photo)
)
telegram_app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)
)


@asynccontextmanager
async def lifespan(api: FastAPI):
    await telegram_app.initialize()
    await telegram_app.start()

    await telegram_app.bot.set_webhook(
        url=f"{BASE_URL}/telegram-webhook",
        secret_token=WEBHOOK_SECRET
    )

    yield

    await telegram_app.bot.delete_webhook()
    await telegram_app.stop()
    await telegram_app.shutdown()


api = FastAPI(lifespan=lifespan)


@api.get("/")
async def home():
    return {"status": "Ethio Telecom Store Bot is running"}


@api.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    secret = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token"
    )

    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)

    await telegram_app.update_queue.put(update)

    return {"ok": True}
    
