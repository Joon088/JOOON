import discord
import random
from datetime import date

from db import (
    get_user,
    remove_money,
    add_money,
    add_jackpot,
    get_jackpot,
    claim_jackpot,
    buy_lotto_ticket,
    get_lotto_tickets,
    clear_lotto_tickets,
    get_lotto_last_draw_date,
    set_lotto_last_draw_date,
    get_guild_channel
)

from utils.checks import check_jail

LOTTO_PRICE = 10000

def setup(bot):

    @bot.tree.command(name="로또구매", description="로또를 구매합니다.")
    async def lotto_buy(interaction: discord.Interaction):

        if not interaction.guild:
            await interaction.response.send_message(
                "서버에서만 사용할 수 있습니다.",
                ephemeral=True
            )
            return

        user_id = interaction.user.id
        guild_id = interaction.guild.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message(
                "먼저 `/등록` 해주세요.",
                ephemeral=True
            )
            return

        if await check_jail(interaction):
            return

        if user["money"] < LOTTO_PRICE:
            await interaction.response.send_message(
                "로또 구매 비용이 부족합니다.",
                ephemeral=True
            )
            return

        numbers = sorted(random.sample(range(1, 46), 6))

        remove_money(user_id, LOTTO_PRICE)

        jackpot_add = int(LOTTO_PRICE * 0.5)
        add_jackpot(guild_id, jackpot_add)

        buy_lotto_ticket(guild_id, user_id, numbers)

        embed = discord.Embed(
            title="🎟 로또 구매 완료",
            description="행운의 번호가 발급되었습니다.",
            color=0xF1C40F
        )

        embed.add_field(
            name="구매 금액",
            value=f"**{LOTTO_PRICE:,}칩**",
            inline=True
        )

        embed.add_field(
            name="잭팟 적립",
            value=f"**+{jackpot_add:,}칩**",
            inline=True
        )

        embed.add_field(
            name="내 번호",
            value=" ".join([f"`{n}`" for n in numbers]),
            inline=False
        )

        embed.set_footer(text="매일 00:05 자동 추첨됩니다.")

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="로또확인", description="내가 구매한 로또를 확인합니다.")
    async def lotto_check(interaction: discord.Interaction):

        if not interaction.guild:
            await interaction.response.send_message(
                "서버에서만 사용할 수 있습니다.",
                ephemeral=True
            )
            return

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        tickets = [
            ticket for ticket in get_lotto_tickets(guild_id)
            if ticket["user_id"] == user_id
        ]

        if not tickets:
            await interaction.response.send_message(
                "구매한 로또가 없습니다.",
                ephemeral=True
            )
            return

        text = ""

        for index, ticket in enumerate(tickets, start=1):
            numbers = " ".join([f"`{n}`" for n in ticket["numbers"]])
            text += f"{index}. {numbers}\n"

        embed = discord.Embed(
            title="🎟 내 로또 목록",
            description=text,
            color=0x3498DB
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


async def draw_lotto_for_guild(bot, guild):
    guild_id = guild.id
    today = date.today()

    if get_lotto_last_draw_date(guild_id) == today:
        return

    tickets = get_lotto_tickets(guild_id)

    if not tickets:
        set_lotto_last_draw_date(guild_id, today)
        return

    winning_numbers = sorted(random.sample(range(1, 46), 6))

    result_text = ""
    jackpot_data = get_jackpot(guild_id)
    jackpot_amount = jackpot_data["amount"]

    for ticket in tickets:
        user_id = ticket["user_id"]
        match_count = len(set(ticket["numbers"]) & set(winning_numbers))

        reward = 0
        jackpot_reward = 0

        if match_count == 6:
            reward = 5000000

            if jackpot_amount > 0:
                jackpot_reward = int(jackpot_amount * 0.5)
                claim_jackpot(guild_id, user_id)

        elif match_count == 5:
            reward = 1000000

        elif match_count == 4:
            reward = 300000

        elif match_count == 3:
            reward = 50000

        total_reward = reward + jackpot_reward

        if total_reward > 0:
            add_money(user_id, total_reward)

        member = guild.get_member(user_id)
        name = member.display_name if member else "알 수 없음"

        result_text += f"**{name}** - {match_count}개 일치"

        if total_reward > 0:
            result_text += f" / +{total_reward:,}칩"

        result_text += "\n"

    clear_lotto_tickets(guild_id)
    set_lotto_last_draw_date(guild_id, today)

    channel_id = get_guild_channel(guild_id, "로또")

    if not channel_id:
        return

    channel = guild.get_channel(channel_id)

    if not channel:
        return

    embed = discord.Embed(
        title="🎟 로또 자동 추첨 결과",
        description="오늘의 로또 추첨이 완료되었습니다.",
        color=0xF1C40F
    )

    embed.add_field(
        name="당첨 번호",
        value=" ".join([f"`{n}`" for n in winning_numbers]),
        inline=False
    )

    embed.add_field(
        name="결과",
        value=result_text[:1000],
        inline=False
    )

    embed.set_footer(
        text="로또 티켓은 추첨 후 초기화됩니다."
    )

    await channel.send(embed=embed)


async def draw_all_lotto(bot):
    for guild in bot.guilds:
        await draw_lotto_for_guild(bot, guild)