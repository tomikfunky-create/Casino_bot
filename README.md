# 🎰 Casino Bot

Полнофункциональный Telegram казино-бот с 5 играми, реферальной системой и Telegram Stars.

## 🎮 Игры
- 🎰 Слоты (с джекпотом!)
- 🎲 Рулетка (красное/чёрное, числа, чётное/нечётное)
- 🪙 Монетка (орёл/решка)
- 💥 Краш (авто-вывод и ручной)
- 🃏 Блэкджек (хит, стенд, удвоение)

## 👥 Реферальная система
- 10% от каждого пополнения приглашённого друга
- Зачисляется моментально при пополнении
- Уведомление рефереру о бонусе

## 💳 Монеты
- Покупка через Telegram Stars (1 Star = 10 монет)
- Пакеты: 50 / 100 / 250 / 500 Stars
- Монеты виртуальные (только для игры)

## 🌍 Языки
- Русский и Английский (автоопределение по Telegram)
- Переключение в любой момент через меню

---

## ⚙️ Установка

### 1. Клонировать / скопировать файлы

### 2. Установить зависимости
```bash
pip install -r requirements.txt
```

### 3. Создать бота
- Открой @BotFather в Telegram
- `/newbot` → дай имя → получи токен
- Включи платежи: `/mybots` → твой бот → Payments → Telegram Stars

### 4. Настроить переменные окружения
```bash
export BOT_TOKEN="your_bot_token_here"
export ADMIN_IDS="your_telegram_user_id"
```

Или создай `.env` файл:
```
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789
```

### 5. Запустить
```bash
python bot.py
```

---

## 📁 Структура
```
casino_bot/
├── bot.py              # Точка входа
├── config.py           # Настройки
├── database.py         # SQLite база данных
├── requirements.txt
├── handlers/
│   ├── __init__.py     # Регистрация хендлеров
│   ├── main.py         # Основные команды
│   ├── games.py        # Все игры
│   └── payments.py     # Telegram Stars оплата
├── games/
│   └── engine.py       # Логика всех игр
├── locales/
│   └── strings.py      # RU + EN переводы
└── utils/
    └── keyboards.py    # Все клавиатуры
```

---

## ⚙️ Настройки (config.py)

| Параметр | Значение | Описание |
|---|---|---|
| MIN_BET | 10 | Минимальная ставка |
| MAX_BET | 10000 | Максимальная ставка |
| START_BONUS | 100 | Стартовый бонус монет |
| REFERRAL_PERCENT | 0.10 | 10% реферальный бонус |
| STARS_TO_COINS | 10 | 1 Star = 10 монет |

---

## 🚀 Деплой на сервер (опционально)

### Systemd сервис
```ini
[Unit]
Description=Casino Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/casino_bot
Environment=BOT_TOKEN=your_token
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable casino_bot
sudo systemctl start casino_bot
```

---

## ⚠️ Важно
- Монеты виртуальные и не имеют реальной стоимости
- Бот работает на принципе развлечения
- Не используй для реальных денежных операций
