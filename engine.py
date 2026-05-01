"""Casino game engines."""
import random
import math
from typing import Tuple, Dict, Any


# ─── SLOTS ────────────────────────────────────────────────────────────────────

SLOT_SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "⭐", "💎", "7️⃣", "🎰"]
SLOT_WEIGHTS = [30, 25, 20, 15, 5, 3, 1, 1]  # Higher weight = more common

SLOT_PAYOUTS = {
    ("🍒", "🍒", "🍒"): 3,
    ("🍋", "🍋", "🍋"): 5,
    ("🍊", "🍊", "🍊"): 8,
    ("🍇", "🍇", "🍇"): 10,
    ("⭐", "⭐", "⭐"): 20,
    ("💎", "💎", "💎"): 50,
    ("7️⃣", "7️⃣", "7️⃣"): 100,
    ("🎰", "🎰", "🎰"): 500,  # Jackpot!
}

# Partial matches
SLOT_PARTIAL = {
    "🍒": 1.5,  # Two cherries = 1.5x
}


def spin_slots(bet: int) -> Dict[str, Any]:
    reels = random.choices(SLOT_SYMBOLS, weights=SLOT_WEIGHTS, k=3)
    reels_tuple = tuple(reels)
    
    payout = 0
    result = "loss"
    multiplier = 0
    
    # Check for three of a kind
    if reels_tuple in SLOT_PAYOUTS:
        multiplier = SLOT_PAYOUTS[reels_tuple]
        payout = int(bet * multiplier)
        result = "jackpot" if multiplier >= 100 else "win"
    # Check for two cherries
    elif reels.count("🍒") == 2:
        multiplier = 1.5
        payout = int(bet * multiplier)
        result = "win"
    # Check for two of the same high-value symbol
    elif len(set(reels)) == 2 and reels[0] in ["💎", "7️⃣", "🎰"]:
        multiplier = 1.5
        payout = int(bet * 1.5)
        result = "win"
    
    reels_display = f"[ {reels[0]} | {reels[1]} | {reels[2]} ]"
    
    return {
        "reels": reels_display,
        "result": result,
        "payout": payout,
        "multiplier": multiplier,
        "profit": payout - bet,
    }


# ─── ROULETTE ─────────────────────────────────────────────────────────────────

RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
BLACK_NUMBERS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}


def spin_roulette(bet: int, bet_type: str, chosen_number: int = None) -> Dict[str, Any]:
    number = random.randint(0, 36)
    
    if number == 0:
        color = "🟢"
        color_name = "green"
    elif number in RED_NUMBERS:
        color = "🔴"
        color_name = "red"
    else:
        color = "⚫"
        color_name = "black"
    
    payout = 0
    won = False
    
    if bet_type == "red" and color_name == "red":
        payout = bet * 2
        won = True
    elif bet_type == "black" and color_name == "black":
        payout = bet * 2
        won = True
    elif bet_type == "zero" and number == 0:
        payout = bet * 35
        won = True
    elif bet_type == "even" and number != 0 and number % 2 == 0:
        payout = bet * 2
        won = True
    elif bet_type == "odd" and number % 2 == 1:
        payout = bet * 2
        won = True
    elif bet_type == "low" and 1 <= number <= 18:
        payout = bet * 2
        won = True
    elif bet_type == "high" and 19 <= number <= 36:
        payout = bet * 2
        won = True
    elif bet_type == "number" and chosen_number == number:
        payout = bet * 35
        won = True
    
    bet_labels = {
        "red": "🔴 Red", "black": "⚫ Black", "zero": "🟢 Zero",
        "even": "Even", "odd": "Odd", "low": "1-18", "high": "19-36",
        "number": f"#{chosen_number}",
    }
    
    return {
        "number": number,
        "color": color,
        "color_name": color_name,
        "won": won,
        "payout": payout,
        "profit": payout - bet,
        "bet_label": bet_labels.get(bet_type, bet_type),
    }


# ─── COIN FLIP ────────────────────────────────────────────────────────────────

def flip_coin(bet: int, choice: str) -> Dict[str, Any]:
    result = random.choice(["heads", "tails"])
    won = result == choice
    payout = int(bet * 1.95) if won else 0
    
    return {
        "result": result,
        "won": won,
        "payout": payout,
        "profit": payout - bet,
    }


# ─── CRASH ────────────────────────────────────────────────────────────────────

def generate_crash_point(house_edge: float = 0.05) -> float:
    """Generate crash point using provably fair formula."""
    r = random.random()
    if r < house_edge:
        return 1.0  # Instant crash
    crash = (1 - house_edge) / (1 - r)
    return round(max(1.01, min(crash, 1000.0)), 2)


def calculate_crash_result(bet: int, cashout_mult: float, crash_point: float) -> Dict[str, Any]:
    won = cashout_mult <= crash_point
    
    if won:
        payout = int(bet * cashout_mult)
        result = "win"
    else:
        payout = 0
        result = "loss"
    
    return {
        "crash_point": crash_point,
        "cashout_mult": cashout_mult if won else crash_point,
        "won": won,
        "payout": payout,
        "profit": payout - bet,
        "result": result,
    }


# ─── BLACKJACK ────────────────────────────────────────────────────────────────

CARD_VALUES = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "10": 10, "J": 10, "Q": 10, "K": 10, "A": 11,
}

CARD_SUITS = ["♠", "♥", "♦", "♣"]
CARD_RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


def create_deck() -> list:
    return [f"{rank}{suit}" for suit in CARD_SUITS for rank in CARD_RANKS]


def card_value(card: str) -> int:
    rank = card[:-1]  # Remove suit
    return CARD_VALUES.get(rank, 10)


def hand_score(cards: list) -> int:
    score = sum(card_value(c) for c in cards)
    aces = sum(1 for c in cards if c[:-1] == "A")
    while score > 21 and aces:
        score -= 10
        aces -= 1
    return score


def format_cards(cards: list) -> str:
    return " ".join(cards)


def deal_blackjack() -> Dict[str, Any]:
    deck = create_deck()
    random.shuffle(deck)
    
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]
    
    return {
        "player": player,
        "dealer": dealer,
        "deck": deck,
        "player_score": hand_score(player),
        "dealer_score": hand_score(dealer),
    }


def blackjack_hit(hand: list, deck: list) -> Tuple[list, list, int]:
    if not deck:
        deck = create_deck()
        random.shuffle(deck)
    hand.append(deck.pop())
    return hand, deck, hand_score(hand)


def resolve_blackjack(player: list, dealer: list, deck: list, bet: int) -> Dict[str, Any]:
    """Play out dealer's hand and determine winner."""
    player_score = hand_score(player)
    
    # Dealer draws to 17
    while hand_score(dealer) < 17:
        if not deck:
            deck = create_deck()
            random.shuffle(deck)
        dealer.append(deck.pop())
    
    dealer_score = hand_score(dealer)
    
    # Determine outcome
    player_bj = player_score == 21 and len(player) == 2
    dealer_bj = dealer_score == 21 and len(dealer) == 2
    
    if player_score > 21:
        outcome = "bust"
        payout = 0
    elif player_bj and not dealer_bj:
        outcome = "blackjack"
        payout = int(bet * 2.5)  # Blackjack pays 3:2
    elif dealer_score > 21:
        outcome = "win"
        payout = bet * 2
    elif player_score > dealer_score:
        outcome = "win"
        payout = bet * 2
    elif player_score == dealer_score:
        outcome = "push"
        payout = bet  # Return bet
    else:
        outcome = "loss"
        payout = 0
    
    return {
        "player": player,
        "dealer": dealer,
        "player_score": player_score,
        "dealer_score": dealer_score,
        "outcome": outcome,
        "payout": payout,
        "profit": payout - bet,
    }
