import logging
import re
from pathlib import Path

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaDocument, InputMediaPhoto, Message

import config
import texts
from keyboards import (
    about_keyboard,
    after_audit_keyboard,
    after_guide_keyboard,
    audit_intro_keyboard,
    channel_keyboard,
    contact_keyboard,
    main_menu_keyboard,
)
from states import LeadFlowStates


router = Router()
logger = logging.getLogger(__name__)

USERNAME_RE = re.compile(r"(?<![\w@])@[A-Za-z0-9_]{5,32}\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")


def extract_contact(text: str) -> str | None:
    for pattern in (USERNAME_RE, EMAIL_RE, PHONE_RE):
        match = pattern.search(text)
        if match:
            return match.group(0).strip(" .,;:")
    return None


def has_contact(text: str) -> bool:
    return extract_contact(text) is not None


def format_admin_notification(
    *,
    first_name: str,
    username: str | None,
    telegram_id: int,
    contact: str,
    audit_text: str,
) -> str:
    username_text = f"@{username}" if username else "@не указан"
    return (
        "Новая заявка на AI-аудит LeadFlow\n\n"
        f"Имя: {first_name}\n"
        f"Username: {username_text}\n"
        f"Telegram ID: {telegram_id}\n"
        f"Профиль: tg://user?id={telegram_id}\n\n"
        "Контакт:\n"
        f"{contact}\n\n"
        "Описание бизнеса:\n"
        f"{audit_text}\n\n"
        "Что сделать:\n"
        "Подготовить 3 идеи автоматизации и первый MVP для внедрения."
    )


async def send_image_if_exists(message: Message, path: Path) -> None:
    if not path.exists():
        logger.error("Image file not found: %s", path)
        await message.answer(texts.IMAGE_UNAVAILABLE_TEXT)
        return
    try:
        await message.answer_photo(FSInputFile(path))
    except Exception:
        logger.exception("Failed to send image: %s", path)
        await message.answer(texts.IMAGE_UNAVAILABLE_TEXT)


async def send_photo_screen(message: Message, path: Path, caption: str, reply_markup=None) -> Message:
    if not path.exists():
        logger.error("Photo screen file not found: %s", path)
        return await message.answer(caption, reply_markup=reply_markup)
    try:
        return await message.answer_photo(FSInputFile(path), caption=caption, reply_markup=reply_markup)
    except Exception:
        logger.exception("Failed to send photo screen: %s", path)
        return await message.answer(caption, reply_markup=reply_markup)


async def show_main_menu(message: Message, state: FSMContext, text: str = texts.MAIN_MENU_TEXT) -> None:
    await state.set_state(LeadFlowStates.main_menu)
    await send_photo_screen(message, config.START_IMAGE, text, main_menu_keyboard())


async def replace_callback_screen(callback: CallbackQuery, text: str, reply_markup=None) -> Message | None:
    if callback.message is None:
        return None

    try:
        return await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as error:
        message = str(error).lower()
        if "message is not modified" in message:
            return callback.message
        logger.warning("Could not edit callback screen, sending fallback message: %s", error)
        return await callback.message.answer(text, reply_markup=reply_markup)


async def seamless_callback_transition(callback: CallbackQuery, text: str, reply_markup=None) -> Message | None:
    return await replace_callback_screen(callback, text, reply_markup)


async def replace_callback_photo_screen(
    callback: CallbackQuery,
    path: Path,
    caption: str,
    reply_markup=None,
) -> Message | None:
    if callback.message is None:
        return None

    if not path.exists():
        logger.error("Photo screen file not found: %s", path)
        return await replace_callback_screen(callback, caption, reply_markup)

    try:
        return await callback.message.edit_media(
            media=InputMediaPhoto(media=FSInputFile(path), caption=caption),
            reply_markup=reply_markup,
        )
    except TelegramBadRequest as error:
        message = str(error).lower()
        if "message is not modified" in message:
            return callback.message
        logger.warning("Could not edit photo screen, sending fallback photo: %s", error)
        return await send_photo_screen(callback.message, path, caption, reply_markup)


async def replace_callback_document_screen(
    callback: CallbackQuery,
    path: Path,
    caption: str,
    reply_markup=None,
) -> Message | None:
    if callback.message is None:
        return None

    if not path.exists():
        logger.error("Document screen file not found: %s", path)
        return await replace_callback_screen(callback, texts.GUIDE_UNAVAILABLE_TEXT, contact_keyboard())

    try:
        return await callback.message.edit_media(
            media=InputMediaDocument(media=FSInputFile(path), caption=caption),
            reply_markup=reply_markup,
        )
    except TelegramBadRequest as error:
        message = str(error).lower()
        if "message is not modified" in message:
            return callback.message
        logger.warning("Could not edit document screen, sending fallback document: %s", error)
        return await callback.message.answer_document(
            FSInputFile(path),
            caption=caption,
            reply_markup=reply_markup,
        )


async def cleanup_guide_file(state: FSMContext, bot) -> None:
    data = await state.get_data()
    chat_id = data.pop("guide_file_chat_id", None)
    message_id = data.pop("guide_file_message_id", None)
    if chat_id and message_id:
        try:
            await bot.delete_message(chat_id, message_id)
        except Exception:
            logger.exception("Failed to delete old guide file message")
    await state.set_data(data)


async def edit_stored_photo_screen(
    bot,
    *,
    chat_id: int,
    message_id: int,
    path: Path,
    caption: str,
    reply_markup=None,
) -> None:
    if not path.exists():
        logger.error("Stored photo screen file not found: %s", path)
        await bot.send_message(chat_id, caption, reply_markup=reply_markup)
        return

    try:
        await bot.edit_message_media(
            chat_id=chat_id,
            message_id=message_id,
            media=InputMediaPhoto(media=FSInputFile(path), caption=caption),
            reply_markup=reply_markup,
        )
    except Exception:
        logger.exception("Failed to edit stored photo screen")
        await bot.send_photo(chat_id, FSInputFile(path), caption=caption, reply_markup=reply_markup)


async def send_admin_notification(message: Message, contact: str, audit_text: str) -> None:
    user = message.from_user
    if user is None:
        raise RuntimeError("Message has no from_user")

    admin_text = format_admin_notification(
        first_name=user.first_name or "не указано",
        username=user.username,
        telegram_id=user.id,
        contact=contact,
        audit_text=audit_text,
    )
    await message.bot.send_message(config.ADMIN_CHAT_ID, admin_text)


async def finish_audit_request(message: Message, state: FSMContext, contact: str, audit_text: str) -> None:
    try:
        await send_admin_notification(message, contact, audit_text)
    except Exception:
        logger.exception("Failed to send audit request to admin chat")

    data = await state.get_data()
    await state.clear()
    await state.set_state(LeadFlowStates.main_menu)

    screen_chat_id = data.get("screen_chat_id")
    screen_message_id = data.get("screen_message_id")
    if screen_chat_id and screen_message_id:
        await edit_stored_photo_screen(
            message.bot,
            chat_id=screen_chat_id,
            message_id=screen_message_id,
            path=config.START_IMAGE,
            caption=texts.AUDIT_SUCCESS_SCREEN_TEXT,
            reply_markup=after_audit_keyboard(),
        )
        return

    await send_photo_screen(message, config.START_IMAGE, texts.AUDIT_SUCCESS_SCREEN_TEXT, after_audit_keyboard())


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    await cleanup_guide_file(state, message.bot)
    await state.clear()
    await state.set_state(LeadFlowStates.main_menu)
    sent = await send_photo_screen(message, config.START_IMAGE, texts.START_SCREEN_TEXT, main_menu_keyboard())
    await state.update_data(screen_chat_id=sent.chat.id, screen_message_id=sent.message_id)


@router.callback_query(F.data == config.CALLBACK_MAIN_MENU)
async def handle_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await cleanup_guide_file(state, callback.message.bot)
    await state.clear()
    await state.set_state(LeadFlowStates.main_menu)
    screen_message = await replace_callback_photo_screen(
        callback,
        config.START_IMAGE,
        texts.MAIN_MENU_SCREEN_TEXT,
        main_menu_keyboard(),
    )
    if screen_message:
        await state.update_data(screen_chat_id=screen_message.chat.id, screen_message_id=screen_message.message_id)


@router.callback_query(F.data == config.CALLBACK_AUDIT_START)
async def handle_audit_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await cleanup_guide_file(state, callback.message.bot)
    await state.clear()
    screen_message = await replace_callback_photo_screen(
        callback,
        config.AUDIT_IMAGE,
        texts.AUDIT_SCREEN_TEXT,
        audit_intro_keyboard(),
    )
    if screen_message:
        await state.update_data(
            screen_chat_id=screen_message.chat.id,
            screen_message_id=screen_message.message_id,
        )
        await state.set_state(LeadFlowStates.waiting_audit_description)


@router.callback_query(F.data == config.CALLBACK_GUIDE)
async def handle_guide(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await cleanup_guide_file(state, callback.message.bot)
    await state.clear()
    await state.set_state(LeadFlowStates.main_menu)
    screen_message = await replace_callback_document_screen(
        callback,
        config.GUIDE_FILE,
        texts.GUIDE_SCREEN_TEXT,
        after_guide_keyboard(),
    )
    if screen_message:
        await state.update_data(screen_chat_id=screen_message.chat.id, screen_message_id=screen_message.message_id)


@router.callback_query(F.data == config.CALLBACK_CHANNEL)
async def handle_channel(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await cleanup_guide_file(state, callback.message.bot)
    await state.clear()
    await state.set_state(LeadFlowStates.main_menu)
    screen_message = await replace_callback_photo_screen(
        callback,
        config.START_IMAGE,
        texts.CHANNEL_SCREEN_TEXT,
        channel_keyboard(),
    )
    if screen_message:
        await state.update_data(screen_chat_id=screen_message.chat.id, screen_message_id=screen_message.message_id)


@router.callback_query(F.data == config.CALLBACK_ABOUT)
async def handle_about(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await cleanup_guide_file(state, callback.message.bot)
    await state.clear()
    await state.set_state(LeadFlowStates.main_menu)
    screen_message = await replace_callback_photo_screen(
        callback,
        config.ABOUT_IMAGE,
        texts.ABOUT_SCREEN_TEXT,
        about_keyboard(),
    )
    if screen_message:
        await state.update_data(screen_chat_id=screen_message.chat.id, screen_message_id=screen_message.message_id)


@router.callback_query(F.data == config.CALLBACK_CONTACT)
async def handle_contact(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    if callback.message:
        await cleanup_guide_file(state, callback.message.bot)
    await state.clear()
    await state.set_state(LeadFlowStates.main_menu)
    screen_message = await replace_callback_photo_screen(
        callback,
        config.START_IMAGE,
        texts.CONTACT_SCREEN_TEXT,
        contact_keyboard(),
    )
    if screen_message:
        await state.update_data(screen_chat_id=screen_message.chat.id, screen_message_id=screen_message.message_id)


@router.message(LeadFlowStates.waiting_audit_description)
async def handle_audit_description(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(texts.ASK_TEXT_DESCRIPTION, reply_markup=audit_intro_keyboard())
        return

    audit_text = message.text.strip()
    if len(audit_text) < config.MIN_AUDIT_DESCRIPTION_LENGTH:
        await message.answer(texts.SHORT_AUDIT_TEXT, reply_markup=audit_intro_keyboard())
        return

    contact = extract_contact(audit_text)
    if not contact and message.from_user and message.from_user.username:
        contact = f"@{message.from_user.username}"

    if contact:
        await finish_audit_request(message, state, contact, audit_text)
        return

    await state.update_data(audit_text=audit_text)
    await state.set_state(LeadFlowStates.waiting_contact)
    await message.answer(texts.ASK_CONTACT_TEXT)


@router.message(LeadFlowStates.waiting_contact)
async def handle_contact_for_audit(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(texts.ASK_CONTACT_AGAIN)
        return

    contact_text = message.text.strip()
    contact = extract_contact(contact_text) or contact_text
    if len(contact) < 5:
        await message.answer(texts.ASK_CONTACT_AGAIN)
        return

    data = await state.get_data()
    audit_text = data.get("audit_text")
    if not audit_text:
        logger.error("Missing audit_text in FSM data while waiting for contact")
        await show_main_menu(message, state, texts.UNKNOWN_TEXT)
        return

    await finish_audit_request(message, state, contact, audit_text)


@router.message()
async def handle_unknown(message: Message, state: FSMContext) -> None:
    await show_main_menu(message, state, texts.UNKNOWN_TEXT)
