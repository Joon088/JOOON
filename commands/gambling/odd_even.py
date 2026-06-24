import discord
import random

from db import get_user, add_money, remove_money, add_jackpot, add_casino_vault, casino_owner_bonus
from utils.checks import check_jail

def setup(bot):

    @bot.tree.command(name="홀짝", description="홀짝 게임")
    async def odd_even(
        interaction: discord.Interaction,
        금액: int,
        선택: str
    ):

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
            embed = discord.Embed(
                title="⚠️ 등록 필요",
                description="먼저 `/등록` 해주세요.",
                color=0xE74C3C
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if await check_jail(interaction):
            return

        if 금액 <= 0:
            embed = discord.Embed(
                title="⚠️ 잘못된 금액",
                description="금액은 1 이상이어야 합니다.",
                color=0xE74C3C
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user["money"] < 금액:
            embed = discord.Embed(
                title="💸 칩 부족",
                description="보유 칩이 부족합니다.",
                color=0xE74C3C
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if 선택 not in ["홀", "짝"]:
            embed = discord.Embed(
                title="⚠️ 입력 오류",
                description="`홀` 또는 `짝`만 입력 가능합니다.",
                color=0xE74C3C
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        result_number = random.randint(1, 10)
        result = "홀" if result_number % 2 else "짝"

        if result == 선택:
            add_money(user_id, 금액)
            new_balance = get_user(user_id)["money"]

            embed = discord.Embed(
                title="🎉 승리!",
                description="예측에 성공했습니다!",
                color=0x2ECC71
            )

            embed.add_field(name="🎯 선택", value=선택, inline=True)
            embed.add_field(name="🎲 주사위", value=str(result_number), inline=True)
            embed.add_field(name="📌 결과", value=result, inline=True)
            embed.add_field(name="💰 획득", value=f"+{금액:,}칩", inline=True)
            embed.add_field(name="🏦 현재 잔액", value=f"{new_balance:,}칩", inline=True)

            await interaction.response.send_message(embed=embed)

        else:

            if casino_owner_bonus(guild_id, user_id):
                new_balance = get_user(user_id)["money"]

                embed = discord.Embed(
                    title="🏨 카지노 오너 보너스!",
                    description="패배할 뻔했지만 카지노 오너 특권으로 손실이 무효 처리되었습니다.",
                    color=0xF1C40F
                )

                embed.add_field(name="🎯 선택", value=선택, inline=True)
                embed.add_field(name="🎲 주사위", value=str(result_number), inline=True)
                embed.add_field(name="📌 결과", value=result, inline=True)
                embed.add_field(name="🛡 보너스", value="손실 무효", inline=True)
                embed.add_field(name="🏦 현재 잔액", value=f"{new_balance:,}칩", inline=True)

                await interaction.response.send_message(embed=embed)
                return

            remove_money(user_id, 금액)

            jackpot_add = int(금액 * 0.05)
            add_jackpot(guild_id, jackpot_add)

            casino_add = int(금액 * 0.02)
            add_casino_vault(guild_id, casino_add)

            new_balance = get_user(user_id)["money"]

            embed = discord.Embed(
                title="💀 패배!",
                description="예측에 실패했습니다.",
                color=0xE74C3C
            )

            embed.add_field(name="🎯 선택", value=선택, inline=True)
            embed.add_field(name="🎲 주사위", value=str(result_number), inline=True)
            embed.add_field(name="📌 결과", value=result, inline=True)
            embed.add_field(name="💸 손실", value=f"-{금액:,}칩", inline=True)
            embed.add_field(name="🎰 잭팟 적립", value=f"+{jackpot_add:,}칩", inline=True)
            embed.add_field(name="🏨 카지노 금고", value=f"+{casino_add:,}칩", inline=True)
            embed.add_field(name="🏦 현재 잔액", value=f"{new_balance:,}칩", inline=False)

            await interaction.response.send_message(embed=embed)