import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "-5491624728"))

CHANNEL_URL = "https://t.me/+pkYVR5Vylw1kMmMy"
ROSTISLAV_URL = "https://t.me/rostwork48"
DANIIL_URL = "https://t.me/danyawork48"

START_IMAGE = ASSETS_DIR / "01_start_cover.png"
AUDIT_IMAGE = ASSETS_DIR / "02_audit_cover.png"
ABOUT_IMAGE = ASSETS_DIR / "03_about_cover.png"
GUIDE_FILE = ASSETS_DIR / "LeadFlow_AI_Guide_2026.pdf"

CALLBACK_AUDIT_START = "audit_start"
CALLBACK_GUIDE = "guide"
CALLBACK_CHANNEL = "channel"
CALLBACK_ABOUT = "about"
CALLBACK_CONTACT = "contact"
CALLBACK_MAIN_MENU = "main_menu"

MIN_AUDIT_DESCRIPTION_LENGTH = 30


def require_bot_token() -> str:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set. Add it to .env before running the bot.")
    return BOT_TOKEN
