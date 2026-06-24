import discord
import random


from db import (
    get_user,
    add_money,
    remove_money,
    add_jackpot,
    claim_jackpot,
    get_jackpot,
    add_casino_vault,
    casino_owner_bonus
)

from utils.checks import check_jail

def setup(bot):

    @bot.tree.command(name="슬롯", description="슬롯머신")
    async def slot(
        interaction: discord.Interaction,
        금액: int
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

        jackpot_data = get_jackpot(guild_id)

        if jackpot_data["amount"] >= 100000 and random.random() < 0.0005:
            jackpot_amount = claim_jackpot(guild_id, user_id)

            if jackpot_amount > 0:
                new_balance = get_user(user_id)["money"]

                embed = discord.Embed(
                    title="🎰🎰🎰 JACKPOT 🎰🎰🎰",
                    description=(
                        f"🚨 **서버 잭팟 당첨!** 🚨\n\n"
                        f"{interaction.user.mention}님이 서버 잭팟을 터뜨렸습니다!"
                    ),
                    color=0xF1C40F
                )

                embed.add_field(
                    name="🏆 당첨자",
                    value=f"**{interaction.user.display_name}**",
                    inline=False
                )

                embed.add_field(
                    name="💰 잭팟 당첨금",
                    value=f"**+{jackpot_amount:,}칩**",
                    inline=False
                )

                embed.add_field(
                    name="🏦 현재 잔액",
                    value=f"**{new_balance:,}칩**",
                    inline=False
                )

                embed.add_field(
                    name="🎉 결과",
                    value="서버 잭팟을 독식했습니다!",
                    inline=False
                )

                embed.set_footer(
                    text="Casino Life • 서버 잭팟이 초기화되었습니다."
                )

                await interaction.response.send_message(
                    content="🚨 **서버 잭팟 발생!** 🚨",
                    embed=embed
                )
                return

        symbols = ["🍒", "🍋", "🍉", "💎", "7️⃣"]

        s1 = random.choice(symbols)
        s2 = random.choice(symbols)
        s3 = random.choice(symbols)

        display = f"{s1}  |  {s2}  |  {s3}"

        if s1 == s2 == s3:
            if s1 == "7️⃣":
                multiplier = 10
                title = "🎰 대박 당첨!"
                color = 0xF1C40F
            elif s1 == "💎":
                multiplier = 5
                title = "💎 다이아 당첨!"
                color = 0x9B59B6
            else:
                multiplier = 3
                title = "🎉 슬롯 당첨!"
                color = 0x2ECC71

            reward = 금액 * multiplier
            add_money(user_id, reward)
            new_balance = get_user(user_id)["money"]

            embed = discord.Embed(
                title=title,
                description=f"```{display}```",
                color=color
            )

            embed.add_field(name="🎲 배당", value=f"x{multiplier}", inline=True)
            embed.add_field(name="💰 획득", value=f"+{reward:,}칩", inline=True)
            embed.add_field(name="🏦 현재 잔액", value=f"{new_balance:,}칩", inline=False)

            embed.set_footer(text="Casino Life • 행운의 슬롯머신")

            await interaction.response.send_message(embed=embed)

        else:

            if casino_owner_bonus(guild_id, user_id):
                new_balance = get_user(user_id)["money"]

                embed = discord.Embed(
                    title="🏨 카지노 오너 보너스!",
                    description=f"```{display}```",
                    color=0xF1C40F
                )

                embed.add_field(
                    name="🛡 카지노 오너 특권 발동!",
                    value="이번 패배는 무효 처리되었습니다.",
                    inline=False
                )

                embed.add_field(
                    name="🎰 원래 결과",
                    value="꽝",
                    inline=True
                )

                embed.add_field(
                    name="💸 손실",
                    value="0칩",
                    inline=True
                )

                embed.add_field(
                    name="🏦 현재 잔액",
                    value=f"{new_balance:,}칩",
                    inline=False
                )

                embed.set_footer(
                    text="Casino Life • 카지노 오너 특권 발동"
                )

                await interaction.response.send_message(embed=embed)
                return

            remove_money(user_id, 금액)

            jackpot_add = int(금액 * 0.10)
            add_jackpot(guild_id, jackpot_add)

            casino_add = int(금액 * 0.02)
            add_casino_vault(guild_id, casino_add)

            new_balance = get_user(user_id)["money"]

            embed = discord.Embed(
                title="🎰 슬롯 결과",
                description=f"```{display}```",
                color=0xE74C3C
            )

            embed.add_field(name="💀 결과", value="꽝", inline=True)
            embed.add_field(name="💸 손실", value=f"-{금액:,}칩", inline=True)
            embed.add_field(name="🎰 잭팟 적립", value=f"+{jackpot_add:,}칩", inline=True)
            embed.add_field(name="🏨 카지노 금고", value=f"+{casino_add:,}칩", inline=True)
            embed.add_field(name="🏦 현재 잔액", value=f"{new_balance:,}칩", inline=False)

            embed.set_footer(text="Casino Life • 다음엔 대박일지도?")

            await interaction.response.send_message(embed=embed)