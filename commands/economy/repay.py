import discord

from db import get_user, repay_debt, apply_daily_interest, update_vip

def setup(bot):

    @bot.tree.command(name="상환", description="대출금을 상환합니다.")
    async def repay(interaction: discord.Interaction, 금액: int):
        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 을 해주세요.", ephemeral=True)
            return

        if 금액 <= 0:
            await interaction.response.send_message("상환 금액은 1칩 이상이어야 합니다.", ephemeral=True)
            return

        interest_added = apply_daily_interest(user_id)
        user = get_user(user_id)

        if user["debt"] <= 0:
            await interaction.response.send_message("상환할 대출금이 없습니다.", ephemeral=True)
            return

        if 금액 > user["money"]:
            await interaction.response.send_message("보유 칩이 부족합니다.", ephemeral=True)
            return

        updated_user = repay_debt(user_id, 금액)
        update_vip(user_id)

        embed = discord.Embed(
            title="💳 상환 완료",
            description="대출금을 상환했습니다.",
            color=0x2ECC71
        )

        embed.add_field(name="상환 금액", value=f"**{금액:,}칩**", inline=True)
        embed.add_field(name="남은 빚", value=f"**{updated_user['debt']:,}칩**", inline=True)
        embed.add_field(name="보유 칩", value=f"**{updated_user['money']:,}칩**", inline=False)

        if interest_added:
            embed.add_field(
                name="오늘 적용된 이자",
                value=f"**+{interest_added:,}칩**",
                inline=False
            )

        await interaction.response.send_message(embed=embed)