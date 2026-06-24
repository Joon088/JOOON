from datetime import datetime, date, timedelta
import json
import random
import psycopg2
import psycopg2.extras

from config import DATABASE_URL

START_MONEY = 50000

# ⚠️ 실제 운영 가격으로 돌릴 때는 500_000_000 추천
CASINO_PRICE = 500_000_000


# =========================
# PostgreSQL 기본 함수
# =========================

def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL 환경변수가 설정되어 있지 않습니다.")

    return psycopg2.connect(DATABASE_URL)


def _json_default(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


def _to_jsonb(data):
    return json.dumps(data, default=_json_default, ensure_ascii=False)


def _parse_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _parse_date(value):
    if not value:
        return None

    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    try:
        return date.fromisoformat(value)
    except Exception:
        return None


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS bot_users (
                    user_id BIGINT PRIMARY KEY,
                    data JSONB NOT NULL
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS guild_data (
                    guild_id BIGINT PRIMARY KEY,
                    data JSONB NOT NULL
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS bot_global (
                    key TEXT PRIMARY KEY,
                    data JSONB NOT NULL
                );
            """)

    init_stocks()


# =========================
# 기본 데이터
# =========================

def default_user(user_id: int, username: str):
    return {
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
        "property_last_claim": None,
        "stocks": {},
    }


def normalize_user(user):
    if not user:
        return None

    user.setdefault("bank", 0)
    user.setdefault("debt", 0)
    user.setdefault("vip", "Bronze")
    user.setdefault("credit", "B")
    user.setdefault("total_bet", 0)
    user.setdefault("total_win", 0)
    user.setdefault("total_lose", 0)
    user.setdefault("last_interest_date", None)
    user.setdefault("properties", [])
    user.setdefault("property_last_claim", None)
    user.setdefault("stocks", {})

    user["last_interest_date"] = _parse_date(user.get("last_interest_date"))
    user["property_last_claim"] = _parse_datetime(user.get("property_last_claim"))

    return user


def default_guild_data():
    return {
        "jackpot": {
            "amount": 0,
            "last_winner": None,
            "last_amount": 0
        },
        "settings": {
            "notice_channel": None,
            "lotto_channel": None,
            "jackpot_channel": None,
            "stock_channel": None
        },
        "lotto_tickets": [],
        "lotto_last_draw_date": None,
        "casino": {
            "owner_id": None,
            "value": CASINO_PRICE,
            "vault": 0,
            "total_profit": 0,
            "protected_until": None
        }
    }


def normalize_guild_data(data):
    if not data:
        data = default_guild_data()

    default = default_guild_data()

    for key, value in default.items():
        data.setdefault(key, value)

    for key, value in default["settings"].items():
        data["settings"].setdefault(key, value)

    for key, value in default["jackpot"].items():
        data["jackpot"].setdefault(key, value)

    for key, value in default["casino"].items():
        data["casino"].setdefault(key, value)

    data["casino"]["protected_until"] = _parse_datetime(
        data["casino"].get("protected_until")
    )

    return data


def save_user(user_id: int, user: dict):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO bot_users (user_id, data)
                VALUES (%s, %s::jsonb)
                ON CONFLICT (user_id)
                DO UPDATE SET data = EXCLUDED.data
                """,
                (user_id, _to_jsonb(user))
            )


def get_user(user_id: int):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT data FROM bot_users WHERE user_id = %s",
                (user_id,)
            )
            row = cur.fetchone()

    if not row:
        return None

    return normalize_user(dict(row["data"]))


def create_user(user_id: int, username: str):
    if get_user(user_id):
        return None

    user = default_user(user_id, username)
    save_user(user_id, user)

    return user


def is_registered(user_id: int):
    return get_user(user_id) is not None


def get_money(user_id: int):
    user = get_user(user_id)
    if not user:
        return None
    return user["money"]


def get_guild_data(guild_id: int):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT data FROM guild_data WHERE guild_id = %s",
                (guild_id,)
            )
            row = cur.fetchone()

    if not row:
        data = default_guild_data()
        save_guild_data(guild_id, data)
        return normalize_guild_data(data)

    return normalize_guild_data(dict(row["data"]))


def save_guild_data(guild_id: int, data: dict):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO guild_data (guild_id, data)
                VALUES (%s, %s::jsonb)
                ON CONFLICT (guild_id)
                DO UPDATE SET data = EXCLUDED.data
                """,
                (guild_id, _to_jsonb(data))
            )


def get_global_data(key: str, default):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT data FROM bot_global WHERE key = %s",
                (key,)
            )
            row = cur.fetchone()

    if not row:
        save_global_data(key, default)
        return default

    return row["data"]


def save_global_data(key: str, data):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO bot_global (key, data)
                VALUES (%s, %s::jsonb)
                ON CONFLICT (key)
                DO UPDATE SET data = EXCLUDED.data
                """,
                (key, _to_jsonb(data))
            )


# =========================
# 돈 / 은행 / 대출 / VIP
# =========================

def add_money(user_id: int, amount: int):
    user = get_user(user_id)
    if not user:
        return None

    user["money"] += amount
    update_vip_data(user)

    save_user(user_id, user)
    return user["money"]


def remove_money(user_id: int, amount: int):
    user = get_user(user_id)
    if not user:
        return None

    user["money"] -= amount
    update_vip_data(user)

    save_user(user_id, user)
    return user["money"]


def deposit_money(user_id: int, amount: int):
    user = get_user(user_id)
    if not user or amount <= 0:
        return None

    if user["money"] < amount:
        return None

    user["money"] -= amount
    user["bank"] += amount
    update_vip_data(user)

    save_user(user_id, user)
    return user


def withdraw_money(user_id: int, amount: int):
    user = get_user(user_id)
    if not user or amount <= 0:
        return None

    if user["bank"] < amount:
        return None

    user["bank"] -= amount
    user["money"] += amount
    update_vip_data(user)

    save_user(user_id, user)
    return user


def get_total_asset(user_id: int):
    user = get_user(user_id)
    if not user:
        return None

    return user["money"] + user["bank"] - user["debt"]


def get_vip_data(user_id: int):
    asset = get_total_asset(user_id)

    if asset is None:
        return "Bronze", 500_000, 5

    if asset >= 1_000_000_000:
        return "Black", 50_000_000, 1

    if asset >= 100_000_000:
        return "Diamond", 20_000_000, 2

    if asset >= 10_000_000:
        return "Gold", 5_000_000, 3

    if asset >= 1_000_000:
        return "Silver", 1_000_000, 4

    return "Bronze", 500_000, 5


def update_vip_data(user: dict):
    asset = user["money"] + user["bank"] - user["debt"]

    if asset >= 1_000_000_000:
        user["vip"] = "Black"
    elif asset >= 100_000_000:
        user["vip"] = "Diamond"
    elif asset >= 10_000_000:
        user["vip"] = "Gold"
    elif asset >= 1_000_000:
        user["vip"] = "Silver"
    else:
        user["vip"] = "Bronze"


def update_vip(user_id: int):
    user = get_user(user_id)
    if not user:
        return None

    update_vip_data(user)
    save_user(user_id, user)

    return user["vip"]


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
    update_vip_data(user)

    save_user(user_id, user)
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
    update_vip_data(user)

    save_user(user_id, user)
    return user


def apply_daily_interest(user_id: int):
    user = get_user(user_id)
    if not user:
        return None

    today = date.today()

    if user["debt"] <= 0:
        user["last_interest_date"] = today
        save_user(user_id, user)
        return 0

    if user["last_interest_date"] == today:
        return 0

    rate = get_interest_rate(user_id)
    interest = int(user["debt"] * rate / 100)

    user["debt"] += interest
    user["last_interest_date"] = today
    update_vip_data(user)

    save_user(user_id, user)
    return interest


def get_vip_display(user_id: int):
    user = get_user(user_id)
    if not user:
        return "🥉 Bronze"

    update_vip(user_id)
    user = get_user(user_id)
    vip = user["vip"]

    vip_icons = {
        "Bronze": "🥉 Bronze",
        "Silver": "🥈 Silver",
        "Gold": "🥇 Gold",
        "Diamond": "💎 Diamond",
        "Black": "🖤 Black"
    }

    return vip_icons.get(vip, "🥉 Bronze")


def get_vip_color(user_id: int):
    user = get_user(user_id)

    if not user:
        return 0xCD7F32

    update_vip(user_id)
    user = get_user(user_id)

    colors = {
        "Bronze": 0xCD7F32,
        "Silver": 0xC0C0C0,
        "Gold": 0xFFD700,
        "Diamond": 0x00FFFF,
        "Black": 0x2C2F33
    }

    return colors.get(user["vip"], 0xCD7F32)


def get_ranking():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT user_id, data FROM bot_users")
            rows = cur.fetchall()

    ranking = []

    for row in rows:
        user_id = int(row["user_id"])
        user = normalize_user(dict(row["data"]))
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

    ranking.sort(key=lambda x: x["total_asset"], reverse=True)
    return ranking


# =========================
# 구금
# =========================

def get_jails():
    jails = get_global_data("jails", {})

    for user_id, until_time in list(jails.items()):
        jails[user_id] = _parse_datetime(until_time)

    return jails


def save_jails(jails: dict):
    serializable = {
        str(user_id): until_time
        for user_id, until_time in jails.items()
    }
    save_global_data("jails", serializable)


def set_jail(user_id: int, until_time):
    jails = get_jails()
    jails[str(user_id)] = until_time
    save_jails(jails)


def get_jail(user_id: int):
    jails = get_jails()
    return jails.get(str(user_id))


def is_jailed(user_id: int):
    jails = get_jails()
    until_time = jails.get(str(user_id))

    if not until_time:
        return False

    if datetime.now() >= until_time:
        del jails[str(user_id)]
        save_jails(jails)
        return False

    return True


def get_jail_remaining(user_id: int):
    jails = get_jails()
    until_time = jails.get(str(user_id))

    if not until_time:
        return None

    remaining = until_time - datetime.now()

    if remaining.total_seconds() <= 0:
        del jails[str(user_id)]
        save_jails(jails)
        return None

    return remaining


def clear_jail(user_id: int):
    jails = get_jails()

    if str(user_id) in jails:
        del jails[str(user_id)]
        save_jails(jails)


def add_jail_time(user_id: int, minutes: int):
    jails = get_jails()
    until_time = jails.get(str(user_id))

    if not until_time or datetime.now() >= until_time:
        jails[str(user_id)] = datetime.now() + timedelta(minutes=minutes)
    else:
        jails[str(user_id)] = until_time + timedelta(minutes=minutes)

    save_jails(jails)
    return jails[str(user_id)]


# =========================
# 잭팟
# =========================

def get_jackpot(guild_id: int):
    data = get_guild_data(guild_id)
    return data["jackpot"]


def add_jackpot(guild_id: int, amount: int):
    data = get_guild_data(guild_id)
    data["jackpot"]["amount"] += amount

    save_guild_data(guild_id, data)
    return data["jackpot"]["amount"]


def claim_jackpot(guild_id: int, user_id: int):
    data = get_guild_data(guild_id)
    jackpot = data["jackpot"]

    amount = jackpot["amount"]

    if amount <= 0:
        return 0

    jackpot["amount"] = 0
    jackpot["last_winner"] = user_id
    jackpot["last_amount"] = amount

    save_guild_data(guild_id, data)
    add_money(user_id, amount)

    return amount


# =========================
# 서버 설정
# =========================

def get_guild_settings(guild_id: int):
    data = get_guild_data(guild_id)
    return data["settings"]


def set_guild_channel(guild_id: int, channel_type: str, channel_id: int):
    data = get_guild_data(guild_id)
    settings = data["settings"]

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

    save_guild_data(guild_id, data)
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


# =========================
# 로또
# =========================

def buy_lotto_ticket(guild_id: int, user_id: int, numbers: list):
    data = get_guild_data(guild_id)

    data["lotto_tickets"].append({
        "user_id": user_id,
        "numbers": numbers
    })

    save_guild_data(guild_id, data)


def get_lotto_tickets(guild_id: int):
    data = get_guild_data(guild_id)
    return data["lotto_tickets"]


def clear_lotto_tickets(guild_id: int):
    data = get_guild_data(guild_id)
    data["lotto_tickets"] = []
    save_guild_data(guild_id, data)


def get_lotto_last_draw_date(guild_id: int):
    data = get_guild_data(guild_id)

    last_date = data.get("lotto_last_draw_date")
    return _parse_date(last_date)


def set_lotto_last_draw_date(guild_id: int, draw_date):
    data = get_guild_data(guild_id)
    data["lotto_last_draw_date"] = draw_date
    save_guild_data(guild_id, data)


# =========================
# 주식
# =========================

DEFAULT_STOCKS = {
    "K전자": {"price": 10000, "last_change": 0},
    "노브코인": {"price": 5000, "last_change": 0},
    "카지노홀딩스": {"price": 50000, "last_change": 0},
    "럭키게임즈": {"price": 100000, "last_change": 0},
    "블랙그룹": {"price": 500000, "last_change": 0},
}

stocks = {}


def init_stocks():
    global stocks
    stocks = get_global_data("stocks", DEFAULT_STOCKS.copy())


def save_stocks():
    save_global_data("stocks", stocks)


def get_stocks():
    return stocks


def get_stock(name: str):
    return stocks.get(name)


def get_user_stocks(user_id: int):
    user = get_user(user_id)

    if not user:
        return {}

    user.setdefault("stocks", {})
    return user["stocks"]


def buy_stock(user_id: int, stock_name: str, quantity: int):
    user = get_user(user_id)
    stock = get_stock(stock_name)

    if not user or not stock or quantity <= 0:
        return None

    total_price = stock["price"] * quantity

    if user["money"] < total_price:
        return None

    user["money"] -= total_price

    portfolio = user.setdefault("stocks", {})

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

    update_vip_data(user)
    save_user(user_id, user)

    return user


def sell_stock(user_id: int, stock_name: str, quantity: int):
    user = get_user(user_id)
    stock = get_stock(stock_name)

    if not user or not stock or quantity <= 0:
        return None

    portfolio = user.setdefault("stocks", {})

    if stock_name not in portfolio:
        return None

    if portfolio[stock_name]["quantity"] < quantity:
        return None

    total_price = stock["price"] * quantity

    portfolio[stock_name]["quantity"] -= quantity

    if portfolio[stock_name]["quantity"] <= 0:
        del portfolio[stock_name]

    user["money"] += total_price

    update_vip_data(user)
    save_user(user_id, user)

    return user


# =========================
# 부동산
# =========================

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

    user.setdefault("properties", [])
    return user["properties"]


def buy_property(user_id: int, property_name: str):
    user = get_user(user_id)

    if not user:
        return None

    user.setdefault("properties", [])

    if property_name not in real_estates:
        return None

    if property_name in user["properties"]:
        return None

    price = real_estates[property_name]["price"]

    if user["money"] < price:
        return None

    user["money"] -= price
    user["properties"].append(property_name)

    update_vip_data(user)
    save_user(user_id, user)

    return user


def sell_property(user_id: int, property_name: str):
    user = get_user(user_id)

    if not user:
        return None

    user.setdefault("properties", [])

    if property_name not in user["properties"]:
        return None

    sell_price = real_estates[property_name]["sell_price"]

    user["properties"].remove(property_name)
    user["money"] += sell_price

    update_vip_data(user)
    save_user(user_id, user)

    return sell_price


def claim_property_income(user_id: int):
    user = get_user(user_id)

    if not user:
        return None

    user.setdefault("properties", [])
    user.setdefault("property_last_claim", None)

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

    update_vip_data(user)
    save_user(user_id, user)

    return {
        "success": True,
        "income": total_income,
        "details": details,
        "money": user["money"]
    }


# =========================
# 카지노
# =========================

def get_casino(guild_id: int):
    data = get_guild_data(guild_id)
    return data["casino"]


def buy_casino(guild_id: int, user_id: int):
    user = get_user(user_id)

    if not user:
        return None

    data = get_guild_data(guild_id)
    casino = data["casino"]

    if casino["owner_id"] is not None:
        return None

    if user["money"] < casino["value"]:
        return None

    user["money"] -= casino["value"]

    casino["owner_id"] = user_id
    casino["vault"] = 0
    casino["total_profit"] = 0
    casino["protected_until"] = datetime.now() + timedelta(days=3)

    update_vip_data(user)

    save_user(user_id, user)
    save_guild_data(guild_id, data)

    return casino


def is_casino_owner(guild_id: int, user_id: int):
    casino = get_casino(guild_id)
    return casino["owner_id"] == user_id


def add_casino_vault(guild_id: int, amount: int):
    data = get_guild_data(guild_id)
    casino = data["casino"]

    if casino["owner_id"] is None:
        return 0

    casino["vault"] += amount
    casino["total_profit"] += amount

    save_guild_data(guild_id, data)
    return casino["vault"]


def claim_casino_vault(guild_id: int, user_id: int):
    data = get_guild_data(guild_id)
    casino = data["casino"]

    if casino["owner_id"] != user_id:
        return None

    amount = casino["vault"]

    if amount <= 0:
        return 0

    casino["vault"] = 0

    save_guild_data(guild_id, data)
    add_money(user_id, amount)

    return amount


def rob_casino(guild_id: int, user_id: int):
    user = get_user(user_id)
    data = get_guild_data(guild_id)
    casino = data["casino"]

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

        save_guild_data(guild_id, data)
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
    data = get_guild_data(guild_id)
    casino = data["casino"]

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
        update_vip_data(old_owner)
        save_user(old_owner_id, old_owner)

    casino["owner_id"] = buyer_id
    casino["value"] = amount
    casino["vault"] = 0
    casino["total_profit"] = 0
    casino["protected_until"] = datetime.now() + timedelta(days=3)

    update_vip_data(buyer)

    save_user(buyer_id, buyer)
    save_guild_data(guild_id, data)

    return {
        "success": True,
        "old_owner_id": old_owner_id,
        "new_owner_id": buyer_id,
        "amount": amount,
        "old_vault": old_vault,
        "protected_until": casino["protected_until"]
    }


def casino_owner_bonus(guild_id: int, user_id: int):
    casino = get_casino(guild_id)

    if casino["owner_id"] != user_id:
        return False

    return random.random() < 0.05
