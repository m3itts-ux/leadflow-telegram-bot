from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Получить разбор", callback_data=config.CALLBACK_AUDIT_START)],
            [InlineKeyboardButton(text="Забрать гайд", callback_data=config.CALLBACK_GUIDE)],
            [InlineKeyboardButton(text="Канал с разборами", callback_data=config.CALLBACK_CHANNEL)],
            [InlineKeyboardButton(text="О нас", callback_data=config.CALLBACK_ABOUT)],
            [InlineKeyboardButton(text="Написать нам", callback_data=config.CALLBACK_CONTACT)],
        ]
    )


def audit_intro_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Посмотреть разборы в канале", callback_data=config.CALLBACK_CHANNEL)],
            [InlineKeyboardButton(text="Назад в меню", callback_data=config.CALLBACK_MAIN_MENU)],
        ]
    )


def after_audit_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Забрать гайд", callback_data=config.CALLBACK_GUIDE)],
            [InlineKeyboardButton(text="Канал с разборами", callback_data=config.CALLBACK_CHANNEL)],
            [InlineKeyboardButton(text="Написать нам", callback_data=config.CALLBACK_CONTACT)],
            [InlineKeyboardButton(text="Назад в меню", callback_data=config.CALLBACK_MAIN_MENU)],
        ]
    )


def after_guide_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Получить разбор", callback_data=config.CALLBACK_AUDIT_START)],
            [InlineKeyboardButton(text="Канал с разборами", callback_data=config.CALLBACK_CHANNEL)],
            [InlineKeyboardButton(text="Назад в меню", callback_data=config.CALLBACK_MAIN_MENU)],
        ]
    )


def channel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Перейти в канал", url=config.CHANNEL_URL)],
            [InlineKeyboardButton(text="Получить разбор", callback_data=config.CALLBACK_AUDIT_START)],
            [InlineKeyboardButton(text="Назад в меню", callback_data=config.CALLBACK_MAIN_MENU)],
        ]
    )


def about_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Получить разбор", callback_data=config.CALLBACK_AUDIT_START)],
            [InlineKeyboardButton(text="Забрать гайд", callback_data=config.CALLBACK_GUIDE)],
            [InlineKeyboardButton(text="Написать нам", callback_data=config.CALLBACK_CONTACT)],
            [InlineKeyboardButton(text="Назад в меню", callback_data=config.CALLBACK_MAIN_MENU)],
        ]
    )


def contact_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Получить разбор", callback_data=config.CALLBACK_AUDIT_START)],
            [InlineKeyboardButton(text="Написать Ростиславу", url=config.ROSTISLAV_URL)],
            [InlineKeyboardButton(text="Написать Даниилу", url=config.DANIIL_URL)],
            [InlineKeyboardButton(text="Назад в меню", callback_data=config.CALLBACK_MAIN_MENU)],
        ]
    )
