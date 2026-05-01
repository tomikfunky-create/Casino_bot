"""Multilingual strings for the casino bot."""

STRINGS = {
    "ru": {
        # General
        "welcome": (
            "🎰 *Добро пожаловать в Casino Bot!*\n\n"
            "Тебе начислено *{bonus} монет* в подарок!\n\n"
            "🎮 Доступные игры:\n"
            "• 🎰 Слоты\n"
            "• 🎲 Рулетка\n"
            "• 🪙 Монетка\n"
            "• 💥 Краш\n"
            "• 🃏 Блэкджек\n\n"
            "Используй кнопки ниже для навигации!"
        ),
        "welcome_back": "👋 С возвращением, *{name}*!\n💰 Баланс: *{coins} монет*",
        "choose_language": "🌍 Выбери язык / Choose language:",
        
        # Menu buttons
        "btn_games": "🎮 Игры",
        "btn_balance": "💰 Баланс",
        "btn_deposit": "💳 Пополнить",
        "btn_referral": "👥 Рефералы",
        "btn_history": "📜 История",
        "btn_leaderboard": "🏆 Лидеры",
        "btn_help": "❓ Помощь",
        "btn_language": "🌍 Язык",
        "btn_back": "◀️ Назад",
        "btn_play_again": "🔄 Играть ещё",
        
        # Balance
        "balance": (
            "💰 *Твой баланс*\n\n"
            "🪙 Основной: *{coins} монет*\n"
            "👥 Реферальный: *{ref_balance} монет*\n\n"
            "📊 Статистика:\n"
            "• Игр сыграно: *{games_played}*\n"
            "• Всего поставлено: *{total_wagered}* монет\n"
            "• Всего выиграно: *{total_won}* монет\n"
            "• Профит: *{profit}* монет"
        ),
        
        # Deposit
        "deposit_menu": (
            "💳 *Пополнение баланса*\n\n"
            "Выбери количество Telegram Stars для покупки монет:\n"
            "⭐ 1 Star = 🪙 {rate} монет\n\n"
            "_Оплата производится через Telegram Stars_"
        ),
        "deposit_invoice_title": "🪙 Пополнение Casino Bot",
        "deposit_invoice_desc": "Покупка {coins} монет для игры в Casino Bot",
        "deposit_success": "✅ Успешно! Зачислено *{coins} монет*\nВаш баланс: *{balance} монет*",
        "deposit_options": ["⭐ 50 Stars → 500 монет", "⭐ 100 Stars → 1000 монет", 
                           "⭐ 250 Stars → 2500 монет", "⭐ 500 Stars → 5000 монет"],
        
        # Games menu
        "games_menu": "🎮 *Выбери игру:*",
        "enter_bet": "💰 Введи ставку (от {min} до {max} монет):",
        "invalid_bet": "❌ Некорректная ставка! Введи число от {min} до {max}.",
        "insufficient_funds": "❌ Недостаточно монет!\nТвой баланс: *{balance}* монет.\nПополни баланс через /deposit",
        "bet_too_low": "❌ Минимальная ставка: *{min}* монет",
        "bet_too_high": "❌ Максимальная ставка: *{max}* монет",
        
        # Slots
        "slots_spinning": "🎰 Крутим барабаны...",
        "slots_win": "🎰 *СЛОТЫ*\n\n{reels}\n\n🎉 *ВЫИГРЫШ!* +{payout} монет\n💰 Баланс: {balance} монет",
        "slots_loss": "🎰 *СЛОТЫ*\n\n{reels}\n\n😔 Не повезло! -{bet} монет\n💰 Баланс: {balance} монет",
        "slots_jackpot": "🎰 *СЛОТЫ*\n\n{reels}\n\n🏆 *ДЖЕКПОТ!!!* +{payout} монет\n💰 Баланс: {balance} монет",
        
        # Roulette
        "roulette_menu": (
            "🎲 *Рулетка*\n\n"
            "Выбери тип ставки:\n"
            "• 🔴 Красное / ⚫ Чёрное — выплата x2\n"
            "• 🟢 Зеро — выплата x35\n"
            "• Чётное / Нечётное — выплата x2\n"
            "• 1-18 / 19-36 — выплата x2\n"
            "• Число (0-36) — выплата x35"
        ),
        "roulette_spinning": "🎲 Крутим рулетку...",
        "roulette_result": (
            "🎲 *РУЛЕТКА*\n\n"
            "Выпало: *{number}* {color}\n"
            "Твоя ставка: {bet_type}\n\n"
            "{outcome_emoji} {outcome_text}\n"
            "💰 Баланс: {balance} монет"
        ),
        "roulette_win": "🎉 *+{payout} монет*",
        "roulette_loss": "😔 *-{bet} монет*",
        "roulette_enter_number": "Введи число от 0 до 36:",
        "roulette_invalid_number": "❌ Введи число от 0 до 36!",
        
        # Coin flip
        "coin_choose": "🪙 *Монетка*\n\nВыбери сторону:\n• 👑 Орёл — выплата x1.95\n• 🌊 Решка — выплата x1.95",
        "coin_flipping": "🪙 Подбрасываем монетку...",
        "coin_result": (
            "🪙 *МОНЕТКА*\n\n"
            "Выпало: *{result}*\n"
            "Твоя ставка: {choice}\n\n"
            "{outcome_emoji} {outcome_text}\n"
            "💰 Баланс: {balance} монет"
        ),
        "coin_heads": "👑 Орёл",
        "coin_tails": "🌊 Решка",
        
        # Crash
        "crash_info": (
            "💥 *КРАШ*\n\n"
            "Самолёт взлетает и множитель растёт.\n"
            "Успей забрать выигрыш до того как он врежется!\n\n"
            "Введи ставку и выбери автовывод (или забирай вручную):"
        ),
        "crash_flying": "✈️ Летим! Множитель: *{mult}x*\n\nНажми *Забрать* чтобы выйти!",
        "crash_cashed_out": "💥 *КРАШ*\n\n✅ Забрал на *{mult}x*!\n+{payout} монет\n💰 Баланс: {balance} монет",
        "crash_lost": "💥 *КРАШ*\n\n✈️ Разбился на *{mult}x*!\n-{bet} монет\n💰 Баланс: {balance} монет",
        "crash_cashout": "💰 Забрать",
        "crash_autowin": "🎯 Авто-вывод на:",
        
        # Blackjack
        "blackjack_start": (
            "🃏 *БЛЭКДЖЕК*\n\n"
            "Твои карты: {player_cards} = *{player_score}*\n"
            "Дилер: {dealer_card} + 🂠\n\n"
            "Что делаем?"
        ),
        "blackjack_hit": "➕ Ещё карту",
        "blackjack_stand": "✋ Хватит",
        "blackjack_double": "💰 Удвоить",
        "blackjack_result": (
            "🃏 *БЛЭКДЖЕК*\n\n"
            "Твои карты: {player_cards} = *{player_score}*\n"
            "Дилер: {dealer_cards} = *{dealer_score}*\n\n"
            "{outcome_emoji} *{outcome_text}*\n"
            "{payout_text}\n"
            "💰 Баланс: {balance} монет"
        ),
        "blackjack_bust": "💥 Перебор!",
        "blackjack_win": "🎉 Ты выиграл! +{payout} монет",
        "blackjack_loss": "😔 Дилер выиграл! -{bet} монет",
        "blackjack_push": "🤝 Ничья! Ставка возвращена",
        "blackjack_natural": "🃏 БЛЭКДЖЕК! +{payout} монет",
        
        # Referral
        "referral_info": (
            "👥 *Реферальная программа*\n\n"
            "💸 Получай *10%* от каждого пополнения друга!\n\n"
            "🔗 Твоя ссылка:\n`{link}`\n\n"
            "📊 Статистика:\n"
            "• Рефералов: *{count}*\n"
            "• Заработано всего: *{earned}* монет\n\n"
            "👥 *Список рефералов:*\n{referrals_list}"
        ),
        "referral_empty": "_Пока нет рефералов_",
        "referral_item": "• {name} — заработано: {earned} монет",
        "referral_bonus_received": "🎉 Ты получил *{amount} монет* реферального бонуса от пополнения друга!",
        
        # History
        "history_empty": "📜 *История игр пуста*\n\nСыграй первую игру!",
        "history_title": "📜 *Последние 10 игр:*\n\n",
        "history_item": "{emoji} *{game}* | Ставка: {bet} | {result}: {profit}\n",
        
        # Leaderboard
        "leaderboard_title": "🏆 *Топ игроков:*\n\n",
        "leaderboard_item": "{pos}. {name} — 🪙 {coins} монет\n",
        
        # Help
        "help": (
            "❓ *Помощь*\n\n"
            "🎮 *Команды:*\n"
            "/start — Главное меню\n"
            "/balance — Твой баланс\n"
            "/deposit — Пополнить баланс\n"
            "/referral — Реферальная программа\n"
            "/history — История игр\n"
            "/leaderboard — Топ игроков\n"
            "/help — Помощь\n\n"
            "🎲 *Правила игр:*\n"
            "• Минимальная ставка: {min_bet} монет\n"
            "• Максимальная ставка: {max_bet} монет\n\n"
            "💳 *Монеты:*\n"
            "• 1 Telegram Star = {rate} монет\n"
            "• Монеты виртуальные, используются только для игры\n\n"
            "👥 *Рефералы:*\n"
            "• Приглашай друзей и получай 10% от их пополнений"
        ),
        
        # Errors
        "error": "❌ Произошла ошибка. Попробуй позже.",
        "game_in_progress": "⚠️ У тебя уже идёт игра! Заверши её сначала.",
    },
    
    "en": {
        # General
        "welcome": (
            "🎰 *Welcome to Casino Bot!*\n\n"
            "You received *{bonus} coins* as a welcome bonus!\n\n"
            "🎮 Available games:\n"
            "• 🎰 Slots\n"
            "• 🎲 Roulette\n"
            "• 🪙 Coin Flip\n"
            "• 💥 Crash\n"
            "• 🃏 Blackjack\n\n"
            "Use the buttons below to navigate!"
        ),
        "welcome_back": "👋 Welcome back, *{name}*!\n💰 Balance: *{coins} coins*",
        "choose_language": "🌍 Выбери язык / Choose language:",
        
        # Menu buttons
        "btn_games": "🎮 Games",
        "btn_balance": "💰 Balance",
        "btn_deposit": "💳 Deposit",
        "btn_referral": "👥 Referrals",
        "btn_history": "📜 History",
        "btn_leaderboard": "🏆 Leaderboard",
        "btn_help": "❓ Help",
        "btn_language": "🌍 Language",
        "btn_back": "◀️ Back",
        "btn_play_again": "🔄 Play again",
        
        # Balance
        "balance": (
            "💰 *Your Balance*\n\n"
            "🪙 Main: *{coins} coins*\n"
            "👥 Referral: *{ref_balance} coins*\n\n"
            "📊 Statistics:\n"
            "• Games played: *{games_played}*\n"
            "• Total wagered: *{total_wagered}* coins\n"
            "• Total won: *{total_won}* coins\n"
            "• Profit: *{profit}* coins"
        ),
        
        # Deposit
        "deposit_menu": (
            "💳 *Deposit*\n\n"
            "Choose the amount of Telegram Stars to buy coins:\n"
            "⭐ 1 Star = 🪙 {rate} coins\n\n"
            "_Payment via Telegram Stars_"
        ),
        "deposit_invoice_title": "🪙 Casino Bot Top-up",
        "deposit_invoice_desc": "Buying {coins} coins for Casino Bot",
        "deposit_success": "✅ Success! *{coins} coins* added!\nYour balance: *{balance} coins*",
        "deposit_options": ["⭐ 50 Stars → 500 coins", "⭐ 100 Stars → 1000 coins",
                           "⭐ 250 Stars → 2500 coins", "⭐ 500 Stars → 5000 coins"],
        
        # Games menu
        "games_menu": "🎮 *Choose a game:*",
        "enter_bet": "💰 Enter your bet ({min} to {max} coins):",
        "invalid_bet": "❌ Invalid bet! Enter a number from {min} to {max}.",
        "insufficient_funds": "❌ Insufficient coins!\nYour balance: *{balance}* coins.\nDeposit via /deposit",
        "bet_too_low": "❌ Minimum bet: *{min}* coins",
        "bet_too_high": "❌ Maximum bet: *{max}* coins",
        
        # Slots
        "slots_spinning": "🎰 Spinning the reels...",
        "slots_win": "🎰 *SLOTS*\n\n{reels}\n\n🎉 *WIN!* +{payout} coins\n💰 Balance: {balance} coins",
        "slots_loss": "🎰 *SLOTS*\n\n{reels}\n\n😔 No luck! -{bet} coins\n💰 Balance: {balance} coins",
        "slots_jackpot": "🎰 *SLOTS*\n\n{reels}\n\n🏆 *JACKPOT!!!* +{payout} coins\n💰 Balance: {balance} coins",
        
        # Roulette
        "roulette_menu": (
            "🎲 *Roulette*\n\n"
            "Choose your bet type:\n"
            "• 🔴 Red / ⚫ Black — pays x2\n"
            "• 🟢 Zero — pays x35\n"
            "• Even / Odd — pays x2\n"
            "• 1-18 / 19-36 — pays x2\n"
            "• Number (0-36) — pays x35"
        ),
        "roulette_spinning": "🎲 Spinning the wheel...",
        "roulette_result": (
            "🎲 *ROULETTE*\n\n"
            "Result: *{number}* {color}\n"
            "Your bet: {bet_type}\n\n"
            "{outcome_emoji} {outcome_text}\n"
            "💰 Balance: {balance} coins"
        ),
        "roulette_win": "🎉 *+{payout} coins*",
        "roulette_loss": "😔 *-{bet} coins*",
        "roulette_enter_number": "Enter a number from 0 to 36:",
        "roulette_invalid_number": "❌ Enter a number from 0 to 36!",
        
        # Coin flip
        "coin_choose": "🪙 *Coin Flip*\n\nChoose a side:\n• 👑 Heads — pays x1.95\n• 🌊 Tails — pays x1.95",
        "coin_flipping": "🪙 Flipping the coin...",
        "coin_result": (
            "🪙 *COIN FLIP*\n\n"
            "Result: *{result}*\n"
            "Your pick: {choice}\n\n"
            "{outcome_emoji} {outcome_text}\n"
            "💰 Balance: {balance} coins"
        ),
        "coin_heads": "👑 Heads",
        "coin_tails": "🌊 Tails",
        
        # Crash
        "crash_info": (
            "💥 *CRASH*\n\n"
            "The plane takes off and the multiplier grows.\n"
            "Cash out before it crashes!\n\n"
            "Enter your bet and choose an auto-cashout (or cash out manually):"
        ),
        "crash_flying": "✈️ Flying! Multiplier: *{mult}x*\n\nPress *Cash Out* to exit!",
        "crash_cashed_out": "💥 *CRASH*\n\n✅ Cashed out at *{mult}x*!\n+{payout} coins\n💰 Balance: {balance} coins",
        "crash_lost": "💥 *CRASH*\n\n✈️ Crashed at *{mult}x*!\n-{bet} coins\n💰 Balance: {balance} coins",
        "crash_cashout": "💰 Cash Out",
        "crash_autowin": "🎯 Auto-cashout at:",
        
        # Blackjack
        "blackjack_start": (
            "🃏 *BLACKJACK*\n\n"
            "Your cards: {player_cards} = *{player_score}*\n"
            "Dealer: {dealer_card} + 🂠\n\n"
            "What do you do?"
        ),
        "blackjack_hit": "➕ Hit",
        "blackjack_stand": "✋ Stand",
        "blackjack_double": "💰 Double Down",
        "blackjack_result": (
            "🃏 *BLACKJACK*\n\n"
            "Your cards: {player_cards} = *{player_score}*\n"
            "Dealer: {dealer_cards} = *{dealer_score}*\n\n"
            "{outcome_emoji} *{outcome_text}*\n"
            "{payout_text}\n"
            "💰 Balance: {balance} coins"
        ),
        "blackjack_bust": "💥 Bust!",
        "blackjack_win": "🎉 You win! +{payout} coins",
        "blackjack_loss": "😔 Dealer wins! -{bet} coins",
        "blackjack_push": "🤝 Push! Bet returned",
        "blackjack_natural": "🃏 BLACKJACK! +{payout} coins",
        
        # Referral
        "referral_info": (
            "👥 *Referral Program*\n\n"
            "💸 Earn *10%* from every deposit your friends make!\n\n"
            "🔗 Your link:\n`{link}`\n\n"
            "📊 Stats:\n"
            "• Referrals: *{count}*\n"
            "• Total earned: *{earned}* coins\n\n"
            "👥 *Your referrals:*\n{referrals_list}"
        ),
        "referral_empty": "_No referrals yet_",
        "referral_item": "• {name} — earned: {earned} coins",
        "referral_bonus_received": "🎉 You received *{amount} coins* referral bonus from your friend's deposit!",
        
        # History
        "history_empty": "📜 *Game history is empty*\n\nPlay your first game!",
        "history_title": "📜 *Last 10 games:*\n\n",
        "history_item": "{emoji} *{game}* | Bet: {bet} | {result}: {profit}\n",
        
        # Leaderboard
        "leaderboard_title": "🏆 *Top Players:*\n\n",
        "leaderboard_item": "{pos}. {name} — 🪙 {coins} coins\n",
        
        # Help
        "help": (
            "❓ *Help*\n\n"
            "🎮 *Commands:*\n"
            "/start — Main menu\n"
            "/balance — Your balance\n"
            "/deposit — Deposit coins\n"
            "/referral — Referral program\n"
            "/history — Game history\n"
            "/leaderboard — Top players\n"
            "/help — Help\n\n"
            "🎲 *Game rules:*\n"
            "• Minimum bet: {min_bet} coins\n"
            "• Maximum bet: {max_bet} coins\n\n"
            "💳 *Coins:*\n"
            "• 1 Telegram Star = {rate} coins\n"
            "• Coins are virtual, used for in-game play only\n\n"
            "👥 *Referrals:*\n"
            "• Invite friends and earn 10% from their deposits"
        ),
        
        # Errors
        "error": "❌ An error occurred. Please try again later.",
        "game_in_progress": "⚠️ You already have a game in progress! Finish it first.",
    }
}


def get_string(lang: str, key: str, **kwargs) -> str:
    strings = STRINGS.get(lang, STRINGS["ru"])
    text = strings.get(key, STRINGS["ru"].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text
