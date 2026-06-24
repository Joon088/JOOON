import discord
from discord.ext import commands, tasks
from datetime import datetime

from commands.account import register
from commands.account import balance
from commands.account import profile
from commands.account import help
from commands.account import guide

from commands.earn import daily
from commands.earn import work
from commands.earn import delivery
from commands.earn import fishing
from commands.earn import mining
from commands.earn import crime
from commands.earn import escape

from commands.gambling import odd_even
from commands.gambling import slot
from commands.gambling import jackpot
from commands.gambling import lotto
from commands.gambling import blackjack
from commands.gambling import baccarat

from commands.economy import bank
from commands.economy import deposit
from commands.economy import withdraw
from commands.economy import loan
from commands.economy import repay
from commands.economy import vip
from commands.economy import transfer
from commands.economy import stocks
from commands.economy import realestate

from commands.ranking import ranking

from commands.settings import channel_settings

from commands.pvp import coinflip
from commands.pvp import dice

from commands.business import casino

from config import DISCORD_TOKEN


intents = discord.Intents.default()
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


register.setup(bot)
balance.setup(bot)
profile.setup(bot)
help.setup(bot)
guide.setup(bot)

daily.setup(bot)
work.setup(bot)
delivery.setup(bot)
fishing.setup(bot)
mining.setup(bot)
crime.setup(bot)
escape.setup(bot)

odd_even.setup(bot)
slot.setup(bot)
jackpot.setup(bot)
lotto.setup(bot)
blackjack.setup(bot)
baccarat.setup(bot)

bank.setup(bot)
deposit.setup(bot)
withdraw.setup(bot)
loan.setup(bot)
repay.setup(bot)
vip.setup(bot)
transfer.setup(bot)
stocks.setup(bot)
realestate.setup(bot)

ranking.setup(bot)

channel_settings.setup(bot)

coinflip.setup(bot)
dice.setup(bot)

casino.setup(bot)


from db import init_db

@bot.event
async def on_ready():

    init_db()

    synced = await bot.tree.sync()

    print(f"✅ 로그인 완료: {bot.user}")
    print(f"✅ 동기화된 명령어 수: {len(synced)}")
    print([cmd.name for cmd in synced])

    if not lotto_auto_draw.is_running():
        lotto_auto_draw.start()

    if not stock_price_loop.is_running():
        stock_price_loop.start()


@tasks.loop(minutes=1)
async def lotto_auto_draw():

    now = datetime.now()

    if now.hour == 0 and now.minute == 5:
        await lotto.draw_all_lotto(bot)


@tasks.loop(hours=1)
async def stock_price_loop():

    await stocks.update_stock_prices(bot)


@bot.tree.command(
    name="핑",
    description="봇 상태를 확인합니다."
)
async def ping(interaction: discord.Interaction):

    await interaction.response.send_message(
        "🏓 퐁! 봇이 정상 작동 중입니다."
    )


bot.run(DISCORD_TOKEN)