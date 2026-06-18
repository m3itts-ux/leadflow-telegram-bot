# LeadFlow Telegram Bot

Telegram-бот LeadFlow по ТЗ из `TZ_LeadFlow_Telegram_Bot_Codex.md`.

## Быстрый запуск

1. Установите Python 3.11+.
2. Создайте виртуальное окружение:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Если Python 3.11 установлен без launcher-алиаса, используйте свой путь к `python.exe`.

3. Установите зависимости:

```powershell
pip install -r requirements.txt
```

4. Создайте `.env` по примеру:

```powershell
Copy-Item .env.example .env
```

5. Заполните `.env`:

```env
BOT_TOKEN=ваш_токен_из_BotFather
ADMIN_CHAT_ID=-5491624728
```

6. Запустите бота:

```powershell
py main.py
```

## Структура

```text
main.py
config.py
texts.py
keyboards.py
handlers.py
states.py
requirements.txt
.env.example
assets/
├── 01_start_cover.png
├── 02_audit_cover.png
├── 03_about_cover.png
├── LeadFlow_AI_Guide_2026.pdf
└── logos/
    ├── icon/
    └── full/
```

## Проверка

```powershell
py -m unittest tests.test_leadflow_core
py -m compileall .
py -c "import config, texts, keyboards, states, handlers, main"
```

В Telegram вручную проверьте `/start`, все inline-кнопки, отправку PDF и отправку заявки в админ-чат.
