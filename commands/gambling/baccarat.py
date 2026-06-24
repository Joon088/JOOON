import discord
import random
from discord import app_commands

from db import get_user, add_money, remove_money, add_jackpot, add_casino_vault, casino_owner_bonus
from utils.checks import check_jail


def draw_card():
    return random.randint(1, 13)


def card_value(card):
    if card >= 10:
        return 0
    return card


def baccarat_score(cards):
    return sum(card_value(card) for card in cards) % 10


def card_text(cards):
    return " ".join([f"`{card}`" for card in cards])


def setup(bot):

    @bot.tree.command(name="바카라", description="바카라 게임을 합니다.")
    @app_commands.describe(
        금액="베팅 금액",
        선택="플레이어 / 뱅커 / 타이 중 선택"
    )
    @app_commands.choices(
        선택=[
            app_commands.Choice(name="플레이어", value="플레이어"),
            app_commands.Choice(name="뱅커", value="뱅커"),
            app_commands.Choice(name="타이", value="타이"),
        ]
    )
    async def baccarat(
        interaction: discord.Interaction,
        금액: int,
        선택: app_commands.Choice[str]
    ):

        if not interaction.guild:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        user_id = interaction.user.id
        guild_id = interaction.guild.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 해주세요.", ephemeral=True)
            return

        if await check_jail(interaction):
            return

        if 금액 <= 0:
            await interaction.response.send_message("금액은 1 이상이어야 합니다.", ephemeral=True)
            return

        if user["money"] < 금액:
            await interaction.response.send_message("보유 칩이 부족합니다.", ephemeral=True)
            return

        choice = 선택.value

        player_cards = [draw_card(), draw_card()]
        banker_cards = [draw_card(), draw_card()]

        player_score = baccarat_score(player_cards)
        banker_score = baccarat_score(banker_cards)

        if player_score <= 5:
            player_cards.append(draw_card())

        if banker_score <= 5:
            banker_cards.append(draw_card())

        player_score = baccarat_score(player_cards)
        banker_score = baccarat_score(banker_cards)

        if player_score > banker_score:
            result = "플레이어"
        elif banker_score > player_score:
            result = "뱅커"
        else:
            result = "타이"

        reward = 0
        jackpot_add = 0
        casino_add = 0
        owner_bonus = False

        if choice == result:
            if result == "타이":
                reward = 금액 * 8
            else:
                reward = 금액

            add_money(user_id, reward)
            title = "🎉 바카라 승리"
            color = 0x2ECC71
            desc = "예측에 성공했습니다."

        else:
            if casino_owner_bonus(guild_id, user_id):
                title = "🏨 카지노 오너 보너스!"
                color = 0xF1C40F
                desc = "패배할 뻔했지만 카지노 오너 특권으로 손실이 무효 처리되었습니다."
                owner_bonus = True
            else:
                remove_money(user_id, 금액)

                jackpot_add = int(금액 * 0.05)
                add_jackpot(guild_id, jackpot_add)

                casino_add = int(금액 * 0.02)
                add_casino_vault(guild_id, casino_add)

                title = "💀 바카라 패배"
                color = 0xE74C3C
                desc = "예측에 실패했습니다."

        new_balance = get_user(user_id)["money"]

        embed = discord.Embed(
            title=title,
            description=desc,
            color=color
        )

        embed.add_field(
            name="🎯 선택",
            value=f"**{choice}**",
            inline=True
        )

        embed.add_field(
            name="📌 결과",
            value=f"**{result}**",
            inline=True
        )

        embed.add_field(
            name="🧑 플레이어",
            value=f"{card_text(player_cards)}\n점수: **{player_score}**",
            inline=True
        )

        embed.add_field(
            name="🏦 뱅커",
            value=f"{card_text(banker_cards)}\n점수: **{banker_score}**",
            inline=True
        )

        if reward > 0:
            embed.add_field(
                name="💰 획득",
                value=f"**+{reward:,}칩**",
                inline=False
            )

        if owner_bonus:
            embed.add_field(
                name="🏨 카지노 오너 보너스",
                value="이번 패배는 무효 처리되었습니다!",
                inline=False
            )    

        if jackpot_add > 0:
            embed.add_field(
                name="🎰 잭팟 적립",
                value=f"**+{jackpot_add:,}칩**",
                inline=False
            )

        if casino_add > 0:
            embed.add_field(
                name="🏨 카지노 금고",
                value=f"**+{casino_add:,}칩**",
                inline=False
        )    

        embed.add_field(
            name="🏦 현재 잔액",
            value=f"**{new_balance:,}칩**",
            inline=False
        )

        embed.set_footer(text="Casino Life • 바카라")

        await interaction.response.send_message(embed=embed)