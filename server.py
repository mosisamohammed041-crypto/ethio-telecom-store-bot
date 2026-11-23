
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from main import (
    BOT_TOKEN,
    start,
    admin_panel,
    admin_orders,
    handle_callback,
    handle_text,
    handle_photo,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
BASE_URL = "https://ethio-telecom-packages-bot.onrender.com"
WEBHOOK_PATH = "/telegram-webhook"

telegram_app = Application.builder().token(BOT_TOKEN).build()

# Commands
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("admin", admin_panel))
telegram_app.add_handler(CommandHandler("orders", admin_orders))

# All inline keyboard buttons
telegram_app.add_handler(
    CallbackQueryHandler(handle_callback)
)

# Customer receipt photos
telegram_app.add_handler(
    MessageHandler(filters.PHOTO, handle_photo)
)

# Customer phone numbers and admin text inputs
telegram_app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
)


@asynccontextmanager
async def lifespan(api: FastAPI):
    await telegram_app.initialize()
    await telegram_app.start()

    webhook_url = BASE_URL.rstrip("/") + WEBHOOK_PATH

    await telegram_app.bot.set_webhook(
        url=webhook_url,
        secret_token=WEBHOOK_SECRET,
        allowed_updates=Update.ALL_TYPES,
    )

    info = await telegram_app.bot.get_webhook_info()
    log.info("Telegram webhook registered: %s", info.url)

    yield

    # Do not delete the webhook during shutdown.
    # This prevents an old Render instance from deleting
    # the webhook registered by a newer instance.
    await telegram_app.stop()
    await telegram_app.shutdown()


api = FastAPI(lifespan=lifespan)


@api.get("/")
async def home():
    return {
        "status": "Ethio Telecom Packages Store Bot is running",
        "webhook": "configured",
    }


@api.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    received_secret = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token"
    )

    if received_secret != WEBHOOK_SECRET:
        raise HTTPException(
            status_code=403,
            detail="Forbidden",
        )

    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.update_queue.put(update)
        return {"ok": True}

    except Exception:
        log.exception("Could not process Telegram webhook update")
        raise HTTPException(
            status_code=500,
            detail="Could not process update",
)
