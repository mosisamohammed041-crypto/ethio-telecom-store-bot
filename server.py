import os
import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
)

from main import (
    BOT_TOKEN, start, admin_panel, admin_orders,
    handle_callback, handle_text, handle_photo, cancel_command, scheduled_worker,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ethio_store_server")

WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
BASE_URL = os.environ.get(
    "RENDER_EXTERNAL_URL",
    "https://ethio-telecom-packages-bot.onrender.com"
).rstrip("/")
WEBHOOK_PATH = "/telegram-webhook"

telegram_app = Application.builder().token(BOT_TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("admin", admin_panel))
telegram_app.add_handler(CommandHandler("orders", admin_orders))
telegram_app.add_handler(CommandHandler("cancel", cancel_command))
telegram_app.add_handler(CallbackQueryHandler(handle_callback))
telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

@asynccontextmanager
async def lifespan(api: FastAPI):
    await telegram_app.initialize()
    await telegram_app.start()
    scheduler_task = asyncio.create_task(scheduled_worker(telegram_app.bot))
    await telegram_app.bot.set_webhook(
        url=BASE_URL + WEBHOOK_PATH,
        secret_token=WEBHOOK_SECRET,
        allowed_updates=Update.ALL_TYPES,
    )
    info = await telegram_app.bot.get_webhook_info()
    log.info("Telegram webhook registered: %s", info.url)
    yield
    # Keep the webhook registered when Render restarts or replaces the instance.
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass
    await telegram_app.stop()
    await telegram_app.shutdown()

api = FastAPI(lifespan=lifespan)

@api.get("/")
async def home():
    return {"status": "Ethio Telecom Packages Store Bot is running", "webhook": "configured"}

@api.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    supplied = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if supplied != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        payload = await request.json()
        update = Update.de_json(payload, telegram_app.bot)
        await telegram_app.update_queue.put(update)
        return {"ok": True}
    except Exception:
        log.exception("Could not process Telegram webhook update")
        raise HTTPException(status_code=500, detail="Could not process update")
