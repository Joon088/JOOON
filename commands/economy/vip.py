import discord

from db import (
    get_user,
    update_vip,
    get_total_asset,
    get_loan_limit,
    get_interest_rate,
    get_vip_display,
    get_vip_color
)

def setup(bot):

    @bot.tree.command(name="vip", description="내 VIP 등급을 확인합니다.")
    async def vip(interaction: discord.Interaction):
        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 을 해주세요.", ephemeral=True)
            return

        update_vip(user_id)
        user = get_user(user_id)

        total_asset = get_total_asset(user_id)
        loan_limit = get_loan_limit(user_id)
        interest = get_interest_rate(user_id)

        embed = discord.Embed(
            title="⭐ VIP 등급 정보",
            description="VIP 등급은 총자산 기준으로 결정됩니다.",
            color=get_vip_color(user_id)
        )

        embed.add_field(name="현재 등급", value=f"**{get_vip_display(user_id)}**", inline=True)
        embed.add_field(name="총자산", value=f"**{total_asset:,}칩**", inline=True)
        embed.add_field(name="대출 한도", value=f"**{loan_limit:,}칩**", inline=False)
        embed.add_field(name="일일 이자", value=f"**{interest}%**", inline=True)

        embed.add_field(
            name="등급 기준",
            value=(
                "Bronze: 0칩 이상\n"
                "Silver: 1,000,000칩 이상\n"
                "Gold: 10,000,000칩 이상\n"
                "Diamond: 100,000,000칩 이상\n"
                "Black: 1,000,000,000칩 이상"
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed)