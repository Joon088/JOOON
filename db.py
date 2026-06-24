from datetime import datetime, date, timedelta

START_MONEY = 50000

users = {}
jails = {}


def get_user(user_id: int):
    return users.get(user_id)


def create_user(user_id: int, username: str):
    if user_id in users:
        return None

    users[user_id] = {
        "user_id": user_id,
        "username": username,
        "money": START_MONEY,
        "bank": 0,
        "debt": 0,
        "vip": "Bronze",
        "credit": "B",
        "total_bet": 0,
        "total_win": 0,
        "total_lose": 0,
        "last_interest_date": None,
        "properties": [],
        "last_property_income": None,
    }

    return users[user_id]


def is_registered(user_id: int):
    return user_id in users


def get_money(user_id: int):
    user = get_user(user_id)
    if not user:
        return None
    return user["money"]


def add_money(user_id: int, amount: int):
    user = get_user(user_id)
    if not user:
        return None

    user["money"] += amount
    update_vip(user_id)
    return user["money"]


def remove_money(user_id: int, amount: int):
    user = get_user(user_id)
    if not user:
        return None

    user["money"] -= amount
    update_vip(user_id)
    return user["money"]


def deposit_money(user_id: int, amount: int):
    user = get_user(user_id)
    if not user or amount <= 0:
        return None

    if user["money"] < amount:
        return None

    user["money"] -= amount
    user["bank"] += amount
    update_vip(user_id)

    return user


def withdraw_money(user_id: int, amount: int):
    user = get_user(user_id)
    if not user or amount <= 0:
        return None

    if user["bank"] < amount:
        return None

    user["bank"] -= amount
    user["money"] += amount
    update_vip(user_id)

    return user


def get_total_asset(user_id: int):
    user = get_user(user_id)
    if not user:
        return None

    return user["money"] + user["bank"] - user["debt"]


def get_vip_data(user_id: int):
    asset = get_total_asset(user_id)

    if asset >= 1_000_000_000:
        return "Black", 50_000_000, 1

    if asset >= 100_000_000:
        return "Diamond", 20_000_000, 2

    if asset >= 10_000_000:
        return "Gold", 5_000_000, 3

    if asset >= 1_000_000:
        return "Silver", 1_000_000, 4

    return "Bronze", 500_000, 5


def update_vip(user_id: int):
    user = get_user(user_id)
    if not user:
        return None

    vip, limit, interest = get_vip_data(user_id)
    user["vip"] = vip

    return vip


def get_loan_limit(user_id: int):
    vip, limit, interest = get_vip_data(user_id)
    return limit


def get_interest_rate(user_id: int):
    vip, limit, interest = get_vip_data(user_id)
    return interest


def add_debt(user_id: int, amount: int):
    user = get_user(user_id)
    if not user:
        return None

    user["debt"] += amount
    user["money"] += amount
    update_vip(user_id)

    return user


def repay_debt(user_id: int, amount: int):
    user = get_user(user_id)
    if not user:
        return None

    if amount > user["debt"]:
        amount = user["debt"]

    if amount > user["money"]:
        return None

    user["money"] -= amount
    user["debt"] -= amount
    update_vip(user_id)

    return user


def apply_daily_interest(user_id: int):
    user = get_user(user_id)
    if not user:
        return None

    today = date.today()

    if user["debt"] <= 0:
        user["last_interest_date"] = today
        return 0

    if user["last_interest_date"] == today:
        return 0

    rate = get_interest_rate(user_id)
    interest = int(user["debt"] * rate / 100)

    user["debt"] += interest
    user["last_interest_date"] = today
    update_vip(user_id)

    return interest


def set_jail(user_id: int, until_time):
    jails[user_id] = until_time


def get_jail(user_id: int):
    return jails.get(user_id)


def is_jailed(user_id: int):
    until_time = jails.get(user_id)

    if not until_time:
        return False

    if datetime.now() >= until_time:
        del jails[user_id]
        return False

    return True


def get_jail_remaining(user_id: int):
    until_time = jails.get(user_id)

    if not until_time:
        return None

    remaining = until_time - datetime.now()

    if remaining.total_seconds() <= 0:
        del jails[user_id]
        return None

    return remaining


def clear_jail(user_id: int):
    if user_id in jails:
        del jails[user_id]


def add_jail_time(user_id: int, minutes: int):
    until_time = jails.get(user_id)

    if not until_time or datetime.now() >= until_time:
        jails[user_id] = datetime.now() + timedelta(minutes=minutes)
    else:
        jails[user_id] = until_time + timedelta(minutes=minutes)

    return jails[user_id]

def get_vip_display(user_id: int):
    user = get_user(user_id)
    if not user:
        return "🥉 Bronze"

    update_vip(user_id)
    vip = user["vip"]

    vip_icons = {
        "Bronze": "🥉 Bronze",
        "Silver": "🥈 Silver",
        "Gold": "🥇 Gold",
        "Diamond": "💎 Diamond",
        "Black": "🖤 Black"
    }

    return vip_icons.get(vip, "🥉 Bronze")

def get_ranking():
    ranking = []

    for user_id, user in users.items():
        total_asset = user["money"] + user["bank"] - user["debt"]

        ranking.append({
            "user_id": user_id,
            "username": user["username"],
            "money": user["money"],
            "bank": user["bank"],
            "debt": user["debt"],
            "total_asset": total_asset,
            "vip": user["vip"]
        })

    ranking.sort(
        key=lambda x: x["total_asset"],
        reverse=True
    )

    return ranking

def get_vip_color(user_id: int):
    user = get_user(user_id)

    if not user:
        return 0xCD7F32

    update_vip(user_id)

    colors = {
        "Bronze": 0xCD7F32,   # 갈색
        "Silver": 0xC0C0C0,   # 은색
        "Gold": 0xFFD700,     # 금색
        "Diamond": 0x00FFFF,  # 하늘색
        "Black": 0x2C2F33     # 검정
    }

    return colors.get(user["vip"], 0xCD7F32)

jackpots = {}

def get_jackpot(guild_id: int):
    if guild_id not in jackpots:
        jackpots[guild_id] = {
            "amount": 0,
            "last_winner": None,
            "last_amount": 0
        }

    return jackpots[guild_id]


def add_jackpot(guild_id: int, amount: int):
    jackpot = get_jackpot(guild_id)
    jackpot["amount"] += amount
    return jackpot["amount"]

def claim_jackpot(guild_id: int, user_id: int):
    jackpot = get_jackpot(guild_id)

    amount = jackpot["amount"]

    if amount <= 0:
        return 0

    jackpot["amount"] = 0
    jackpot["last_winner"] = user_id
    jackpot["last_amount"] = amount

    add_money(user_id, amount)

    return amount

guild_settings = {}

def get_guild_settings(guild_id: int):
    if guild_id not in guild_settings:
        guild_settings[guild_id] = {
            "notice_channel": None,
            "lotto_channel": None,
            "jackpot_channel": None,
            "stock_channel": None
        }

    return guild_settings[guild_id]


def set_guild_channel(guild_id: int, channel_type: str, channel_id: int):
    settings = get_guild_settings(guild_id)

    channel_keys = {
        "공지": "notice_channel",
        "로또": "lotto_channel",
        "잭팟": "jackpot_channel",
        "주식": "stock_channel"
    }

    if channel_type not in channel_keys:
        return None

    key = channel_keys[channel_type]
    settings[key] = channel_id

    return settings


def get_guild_channel(guild_id: int, channel_type: str):
    settings = get_guild_settings(guild_id)

    channel_keys = {
        "공지": "notice_channel",
        "로또": "lotto_channel",
        "잭팟": "jackpot_channel",
        "주식": "stock_channel"
    }

    key = channel_keys.get(channel_type)

    if not key:
        return None

    channel_id = settings.get(key)

    if channel_id:
        return channel_id

    return settings.get("notice_channel")

lotto_tickets = {}
lotto_last_draw_date = {}

def buy_lotto_ticket(guild_id: int, user_id: int, numbers: list):
    if guild_id not in lotto_tickets:
        lotto_tickets[guild_id] = []

    lotto_tickets[guild_id].append({
        "user_id": user_id,
        "numbers": numbers
    })

def get_lotto_tickets(guild_id: int):
    return lotto_tickets.get(guild_id, [])

def clear_lotto_tickets(guild_id: int):
    lotto_tickets[guild_id] = []

def get_lotto_last_draw_date(guild_id: int):
    return lotto_last_draw_date.get(guild_id)

def set_lotto_last_draw_date(guild_id: int, draw_date):
    lotto_last_draw_date[guild_id] = draw_date

stocks = {
    "K전자": {"price": 10000, "last_change": 0},
    "노브코인": {"price": 5000, "last_change": 0},
    "카지노홀딩스": {"price": 50000, "last_change": 0},
    "럭키게임즈": {"price": 100000, "last_change": 0},
    "블랙그룹": {"price": 500000, "last_change": 0},
}

user_stocks = {}


def get_stocks():
    return stocks


def get_stock(name: str):
    return stocks.get(name)


def get_user_stocks(user_id: int):
    if user_id not in user_stocks:
        user_stocks[user_id] = {}

    return user_stocks[user_id]


def buy_stock(user_id: int, stock_name: str, quantity: int):
    user = get_user(user_id)
    stock = get_stock(stock_name)

    if not user or not stock or quantity <= 0:
        return None

    total_price = stock["price"] * quantity

    if user["money"] < total_price:
        return None

    user["money"] -= total_price

    portfolio = get_user_stocks(user_id)

    if stock_name not in portfolio:
        portfolio[stock_name] = {
            "quantity": 0,
            "avg_price": 0
        }

    current_qty = portfolio[stock_name]["quantity"]
    current_avg = portfolio[stock_name]["avg_price"]

    new_qty = current_qty + quantity
    new_avg = int(((current_qty * current_avg) + total_price) / new_qty)

    portfolio[stock_name]["quantity"] = new_qty
    portfolio[stock_name]["avg_price"] = new_avg

    update_vip(user_id)
    return user


def sell_stock(user_id: int, stock_name: str, quantity: int):
    user = get_user(user_id)
    stock = get_stock(stock_name)
    portfolio = get_user_stocks(user_id)

    if not user or not stock or quantity <= 0:
        return None

    if stock_name not in portfolio:
        return None

    if portfolio[stock_name]["quantity"] < quantity:
        return None

    total_price = stock["price"] * quantity

    portfolio[stock_name]["quantity"] -= quantity

    if portfolio[stock_name]["quantity"] <= 0:
        del portfolio[stock_name]

    user["money"] += total_price

    update_vip(user_id)
    return user

import random

real_estates = {
    "원룸": {
        "price": 10_000_000,
        "sell_price": 8_000_000,
        "income_min": 50_000,
        "income_max": 100_000
    },
    "아파트": {
        "price": 50_000_000,
        "sell_price": 40_000_000,
        "income_min": 300_000,
        "income_max": 500_000
    },
    "상가": {
        "price": 100_000_000,
        "sell_price": 80_000_000,
        "income_min": 700_000,
        "income_max": 1_200_000
    },
    "호텔": {
        "price": 500_000_000,
        "sell_price": 400_000_000,
        "income_min": 3_000_000,
        "income_max": 5_000_000
    }
}


def get_real_estates():
    return real_estates


def get_user_properties(user_id: int):
    user = get_user(user_id)

    if not user:
        return []

    if "properties" not in user:
        user["properties"] = []

    return user["properties"]


def buy_property(user_id: int, property_name: str):
    user = get_user(user_id)

    if not user:
        return None

    if "properties" not in user:
        user["properties"] = []

    if property_name not in real_estates:
        return None

    if property_name in user["properties"]:
        return None

    price = real_estates[property_name]["price"]

    if user["money"] < price:
        return None

    user["money"] -= price
    user["properties"].append(property_name)

    update_vip(user_id)
    return user


def sell_property(user_id: int, property_name: str):
    user = get_user(user_id)

    if not user:
        return None

    if "properties" not in user:
        user["properties"] = []

    if property_name not in user["properties"]:
        return None

    sell_price = real_estates[property_name]["sell_price"]

    user["properties"].remove(property_name)
    user["money"] += sell_price

    update_vip(user_id)
    return sell_price


def claim_property_income(user_id: int):
    user = get_user(user_id)

    if not user:
        return None

    if "properties" not in user:
        user["properties"] = []

    if "property_last_claim" not in user:
        user["property_last_claim"] = None

    if not user["properties"]:
        return None

    now = datetime.now()
    last_claim = user["property_last_claim"]

    if last_claim and now < last_claim + timedelta(hours=12):
        remaining = (last_claim + timedelta(hours=12)) - now
        return {
            "success": False,
            "remaining": remaining
        }

    total_income = 0
    details = []

    for property_name in user["properties"]:
        data = real_estates[property_name]
        income = random.randint(data["income_min"], data["income_max"])
        total_income += income
        details.append((property_name, income))

    user["money"] += total_income
    user["property_last_claim"] = now

    update_vip(user_id)

    return {
        "success": True,
        "income": total_income,
        "details": details,
        "money": user["money"]
    }

casinos = {}

CASINO_PRICE = 50_000


def get_casino(guild_id: int):
    if guild_id not in casinos:
        casinos[guild_id] = {
            "owner_id": None,
            "value": CASINO_PRICE,
            "vault": 0,
            "total_profit": 0,
            "protected_until": None
        }

    return casinos[guild_id]


def buy_casino(guild_id: int, user_id: int):
    user = get_user(user_id)

    if not user:
        return None

    casino = get_casino(guild_id)

    if casino["owner_id"] is not None:
        return None

    if user["money"] < casino["value"]:
        return None

    user["money"] -= casino["value"]

    casino["owner_id"] = user_id
    casino["vault"] = 0
    casino["total_profit"] = 0
    casino["protected_until"] = datetime.now() + timedelta(days=3)

    update_vip(user_id)

    return casino


def is_casino_owner(guild_id: int, user_id: int):
    casino = get_casino(guild_id)
    return casino["owner_id"] == user_id


def add_casino_vault(guild_id: int, amount: int):
    casino = get_casino(guild_id)

    if casino["owner_id"] is None:
        return 0

    casino["vault"] += amount
    casino["total_profit"] += amount

    return casino["vault"]


def claim_casino_vault(guild_id: int, user_id: int):
    casino = get_casino(guild_id)

    if casino["owner_id"] != user_id:
        return None

    amount = casino["vault"]

    if amount <= 0:
        return 0

    casino["vault"] = 0
    add_money(user_id, amount)

    return amount


def rob_casino(guild_id: int, user_id: int):
    import random

    user = get_user(user_id)
    casino = get_casino(guild_id)

    if not user:
        return None

    if casino["owner_id"] is None:
        return {"success": False, "reason": "NO_OWNER"}

    if casino["owner_id"] == user_id:
        return {"success": False, "reason": "OWNER"}

    if casino["vault"] <= 0:
        return {"success": False, "reason": "EMPTY"}

    success = random.random() < 0.20

    if success:
        percent = random.randint(20, 40)
        stolen = int(casino["vault"] * percent / 100)

        casino["vault"] -= stolen
        add_money(user_id, stolen)

        return {
            "success": True,
            "stolen": stolen,
            "percent": percent,
            "vault": casino["vault"]
        }

    set_jail(user_id, datetime.now() + timedelta(minutes=30))

    return {"success": False, "reason": "FAILED"}


def acquire_casino(guild_id: int, buyer_id: int, amount: int):
    buyer = get_user(buyer_id)
    casino = get_casino(guild_id)

    if not buyer:
        return None

    if casino["owner_id"] is None:
        return {"success": False, "reason": "NO_OWNER"}

    if casino["owner_id"] == buyer_id:
        return {"success": False, "reason": "OWNER"}

    if casino["protected_until"] and datetime.now() < casino["protected_until"]:
        remaining = casino["protected_until"] - datetime.now()
        return {
            "success": False,
            "reason": "PROTECTED",
            "remaining": remaining
        }

    min_price = int(casino["value"] * 1.2)

    if amount < min_price:
        return {
            "success": False,
            "reason": "LOW_PRICE",
            "min_price": min_price
        }

    if buyer["money"] < amount:
        return {"success": False, "reason": "NO_MONEY"}

    old_owner_id = casino["owner_id"]
    old_owner = get_user(old_owner_id)
    old_vault = casino["vault"]

    buyer["money"] -= amount

    if old_owner:
        old_owner["money"] += amount
        old_owner["money"] += old_vault
        update_vip(old_owner_id)

    casino["owner_id"] = buyer_id
    casino["value"] = amount
    casino["vault"] = 0
    casino["total_profit"] = 0
    casino["protected_until"] = datetime.now() + timedelta(days=3)

    update_vip(buyer_id)

    return {
        "success": True,
        "old_owner_id": old_owner_id,
        "new_owner_id": buyer_id,
        "amount": amount,
        "old_vault": old_vault,
        "protected_until": casino["protected_until"]
    }

def casino_owner_bonus(guild_id: int, user_id: int):
    import random

    casino = get_casino(guild_id)

    if casino["owner_id"] != user_id:
        return False

    return random.random() < 0.05