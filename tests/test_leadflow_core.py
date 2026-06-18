import unittest
import asyncio
from pathlib import Path


class LeadFlowCoreTests(unittest.TestCase):
    def test_extract_contact_finds_username_phone_and_email(self):
        from handlers import extract_contact

        self.assertEqual(extract_contact("Контакт: @leadflow_user"), "@leadflow_user")
        self.assertEqual(
            extract_contact("Телефон +7 999 123-45-67, напишите"),
            "+7 999 123-45-67",
        )
        self.assertEqual(
            extract_contact("Почта owner@example.com для связи"),
            "owner@example.com",
        )

    def test_extract_contact_returns_none_without_contact(self):
        from handlers import extract_contact

        text = "Мебель под заказ. Заявки идут с Avito. Менеджер отвечает вручную."

        self.assertIsNone(extract_contact(text))

    def test_admin_notification_matches_required_shape(self):
        from handlers import format_admin_notification

        message = format_admin_notification(
            first_name="Иван",
            username=None,
            telegram_id=12345,
            contact="@ivan",
            audit_text="Описание бизнеса длиннее тридцати символов.",
        )

        self.assertEqual(
            message,
            (
                "Новая заявка на AI-аудит LeadFlow\n\n"
                "Имя: Иван\n"
                "Username: @не указан\n"
                "Telegram ID: 12345\n"
                "Профиль: tg://user?id=12345\n\n"
                "Контакт:\n"
                "@ivan\n\n"
                "Описание бизнеса:\n"
                "Описание бизнеса длиннее тридцати символов.\n\n"
                "Что сделать:\n"
                "Подготовить 3 идеи автоматизации и первый MVP для внедрения."
            ),
        )

    def test_required_asset_paths_exist(self):
        import config

        required_paths = [
            config.START_IMAGE,
            config.AUDIT_IMAGE,
            config.ABOUT_IMAGE,
            config.GUIDE_FILE,
        ]

        for path in required_paths:
            self.assertTrue(Path(path).exists(), path)

    def test_photo_screen_captions_fit_telegram_limit(self):
        import texts

        captions = [
            texts.START_SCREEN_TEXT,
            texts.AUDIT_SCREEN_TEXT,
            texts.GUIDE_SCREEN_TEXT,
            texts.CHANNEL_SCREEN_TEXT,
            texts.ABOUT_SCREEN_TEXT,
            texts.CONTACT_SCREEN_TEXT,
            texts.MAIN_MENU_SCREEN_TEXT,
        ]

        for caption in captions:
            self.assertLessEqual(len(caption), 1024, caption[:50])

    def test_cleanup_guide_file_deletes_stored_pdf_message(self):
        from handlers import cleanup_guide_file

        class FakeBot:
            def __init__(self):
                self.deleted = []

            async def delete_message(self, chat_id, message_id):
                self.deleted.append((chat_id, message_id))

        class FakeState:
            def __init__(self):
                self.data = {
                    "guide_file_chat_id": 10,
                    "guide_file_message_id": 20,
                    "other": "keep",
                }

            async def get_data(self):
                return dict(self.data)

            async def set_data(self, data):
                self.data = data

        bot = FakeBot()
        state = FakeState()

        asyncio.run(cleanup_guide_file(state, bot))

        self.assertEqual(bot.deleted, [(10, 20)])
        self.assertEqual(state.data, {"other": "keep"})

    def test_replace_callback_screen_edits_current_message(self):
        from handlers import replace_callback_screen

        class FakeMessage:
            def __init__(self):
                self.edited_text = None
                self.edited_reply_markup = None
                self.answer_calls = []

            async def edit_text(self, text, reply_markup=None):
                self.edited_text = text
                self.edited_reply_markup = reply_markup
                return self

            async def answer(self, text, reply_markup=None):
                self.answer_calls.append((text, reply_markup))
                return self

        class FakeCallback:
            def __init__(self):
                self.message = FakeMessage()

        callback = FakeCallback()
        keyboard = object()

        result = asyncio.run(replace_callback_screen(callback, "Новый экран", keyboard))

        self.assertIs(result, callback.message)
        self.assertEqual(callback.message.edited_text, "Новый экран")
        self.assertIs(callback.message.edited_reply_markup, keyboard)
        self.assertEqual(callback.message.answer_calls, [])

    def test_seamless_callback_transition_edits_only_final_screen(self):
        from handlers import seamless_callback_transition

        class FakeMessage:
            def __init__(self):
                self.edits = []

            async def edit_text(self, text, reply_markup=None):
                self.edits.append((text, reply_markup))
                return self

        class FakeCallback:
            def __init__(self):
                self.message = FakeMessage()

        callback = FakeCallback()
        keyboard = object()

        result = asyncio.run(
            seamless_callback_transition(callback, "Финальный экран", keyboard)
        )

        self.assertIs(result, callback.message)
        self.assertEqual(callback.message.edits, [("Финальный экран", keyboard)])


if __name__ == "__main__":
    unittest.main()
