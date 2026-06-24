import discord
import random
from discord import app_commands

from db import (
    get_user,
    get_stocks,
    get_stock,
    buy_stock,
    sell_stock,
    get_user_stocks,
    get_guild_channel
)

STOCK_NAMES = ["K전자", "노브코인", "카지노홀딩스", "럭키게임즈", "블랙그룹"]

def setup(bot):

    @bot.tree.command(name="주식목록", description="현재 주식 시세를 확인합니다.")
    async def stock_list(interaction: discord.Interaction):

        stocks = get_stocks()

        embed = discord.Embed(
            title="📈 주식 시장",
            description="현재 거래 가능한 주식 목록입니다.",
            color=0x2ECC71
        )

        for name, data in stocks.items():
            change = data["last_change"]

            if change > 0:
                change_text = f"▲ +{change}%"
            elif change < 0:
                change_text = f"▼ {change}%"
            else:
                change_text = "변동 없음"

            embed.add_field(
                name=name,
                value=f"현재가: **{data['price']:,}칩**\n변동: {change_text}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="주식매수", description="주식을 매수합니다.")
    @app_commands.describe(
        회사="매수할 회사",
        수량="매수할 수량"
    )
    @app_commands.choices(
        회사=[
            app_commands.Choice(name="K전자", value="K전자"),
            app_commands.Choice(name="노브코인", value="노브코인"),
            app_commands.Choice(name="카지노홀딩스", value="카지노홀딩스"),
            app_commands.Choice(name="럭키게임즈", value="럭키게임즈"),
            app_commands.Choice(name="블랙그룹", value="블랙그룹"),
        ]
    )
    async def stock_buy(
        interaction: discord.Interaction,
        회사: app_commands.Choice[str],
        수량: int
    ):

        user = get_user(interaction.user.id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 해주세요.", ephemeral=True)
            return

        if 수량 <= 0:
            await interaction.response.send_message("수량은 1 이상이어야 합니다.", ephemeral=True)
            return

        stock_name = 회사.value
        stock = get_stock(stock_name)
        total_price = stock["price"] * 수량

        if user["money"] < total_price:
            await interaction.response.send_message("보유 칩이 부족합니다.", ephemeral=True)
            return

        updated_user = buy_stock(interaction.user.id, stock_name, 수량)

        embed = discord.Embed(
            title="📈 주식 매수 완료",
            color=0x2ECC71
        )

        embed.add_field(name="회사", value=stock_name, inline=True)
        embed.add_field(name="수량", value=f"{수량}주", inline=True)
        embed.add_field(name="매수 금액", value=f"{total_price:,}칩", inline=False)
        embed.add_field(name="보유 칩", value=f"{updated_user['money']:,}칩", inline=False)

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="주식매도", description="주식을 매도합니다.")
    @app_commands.describe(
        회사="매도할 회사",
        수량="매도할 수량"
    )
    @app_commands.choices(
        회사=[
            app_commands.Choice(name="K전자", value="K전자"),
            app_commands.Choice(name="노브코인", value="노브코인"),
            app_commands.Choice(name="카지노홀딩스", value="카지노홀딩스"),
            app_commands.Choice(name="럭키게임즈", value="럭키게임즈"),
            app_commands.Choice(name="블랙그룹", value="블랙그룹"),
        ]
    )
    async def stock_sell(
        interaction: discord.Interaction,
        회사: app_commands.Choice[str],
        수량: int
    ):

        user = get_user(interaction.user.id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 해주세요.", ephemeral=True)
            return

        if 수량 <= 0:
            await interaction.response.send_message("수량은 1 이상이어야 합니다.", ephemeral=True)
            return

        stock_name = 회사.value
        portfolio = get_user_stocks(interaction.user.id)

        if stock_name not in portfolio or portfolio[stock_name]["quantity"] < 수량:
            await interaction.response.send_message("보유 주식 수량이 부족합니다.", ephemeral=True)
            return

        stock = get_stock(stock_name)
        total_price = stock["price"] * 수량

        updated_user = sell_stock(interaction.user.id, stock_name, 수량)

        embed = discord.Embed(
            title="📉 주식 매도 완료",
            color=0xE67E22
        )

        embed.add_field(name="회사", value=stock_name, inline=True)
        embed.add_field(name="수량", value=f"{수량}주", inline=True)
        embed.add_field(name="매도 금액", value=f"{total_price:,}칩", inline=False)
        embed.add_field(name="보유 칩", value=f"{updated_user['money']:,}칩", inline=False)

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="내주식", description="내 보유 주식을 확인합니다.")
    async def my_stocks(interaction: discord.Interaction):

        user = get_user(interaction.user.id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 해주세요.", ephemeral=True)
            return

        portfolio = get_user_stocks(interaction.user.id)

        if not portfolio:
            await interaction.response.send_message("보유 중인 주식이 없습니다.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📊 내 주식",
            color=0x3498DB
        )

        total_value = 0
        total_profit = 0

        for name, data in portfolio.items():
            stock = get_stock(name)
            current_value = stock["price"] * data["quantity"]
            buy_value = data["avg_price"] * data["quantity"]
            profit = current_value - buy_value

            total_value += current_value
            total_profit += profit

            sign = "+" if profit >= 0 else ""

            embed.add_field(
                name=name,
                value=(
                    f"보유: **{data['quantity']}주**\n"
                    f"평균단가: **{data['avg_price']:,}칩**\n"
                    f"현재가: **{stock['price']:,}칩**\n"
                    f"평가손익: **{sign}{profit:,}칩**"
                ),
                inline=False
            )

        sign = "+" if total_profit >= 0 else ""

        embed.add_field(
            name="📌 총 평가",
            value=(
                f"평가금액: **{total_value:,}칩**\n"
                f"총 손익: **{sign}{total_profit:,}칩**"
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed)


async def update_stock_prices(bot):
    stocks = get_stocks()
    notices = []

    for name, data in stocks.items():
        roll = random.random()

        if roll < 0.02:
            change = random.randint(-30, -15)
            event = "💥 악재"
        elif roll < 0.10:
            change = random.randint(15, 30)
            event = "🚀 호재"
        else:
            change = random.randint(-5, 5)
            event = "일반 변동"

        old_price = data["price"]
        new_price = int(old_price * (100 + change) / 100)

        if new_price < 100:
            new_price = 100

        data["price"] = new_price
        data["last_change"] = change

        if event != "일반 변동":
            notices.append((name, old_price, new_price, change, event))

    for guild in bot.guilds:
        channel_id = get_guild_channel(guild.id, "주식")

        if not channel_id:
            continue

        channel = guild.get_channel(channel_id)

        if not channel:
            continue

        if not notices:
            continue

        embed = discord.Embed(
            title="📈 주식 속보",
            description="시장에 큰 변동이 발생했습니다.",
            color=0xF1C40F
        )

        for name, old_price, new_price, change, event in notices:
            sign = "+" if change > 0 else ""

            embed.add_field(
                name=f"{event} {name}",
                value=(
                    f"{old_price:,}칩 → **{new_price:,}칩**\n"
                    f"변동률: **{sign}{change}%**"
                ),
                inline=False
            )

        await channel.send(embed=embed)