import discord
from db import get_user

def setup(bot):

    @bot.tree.command(name="잔액", description="보유 칩을 확인합니다.")
    async def balance(interaction: discord.Interaction):

        user = get_user(interaction.user.id)

        if not user:
            embed = discord.Embed(
                title="⚠️ 등록 필요",
                description="먼저 `/등록` 을 해주세요.",
                color=0xE74C3C
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="💰 자산 현황",
            color=0x2ECC71
        )

        embed.add_field(
            name="💵 보유 칩",
            value=f"**{user['money']:,}칩**",
            inline=False
        )

        embed.add_field(
            name="🏦 은행",
            value=f"{user['bank']:,}칩",
            inline=True
        )

        embed.add_field(
            name="💳 빚",
            value=f"{user['debt']:,}칩",
            inline=True
        )

        total_asset = user["money"] + user["bank"] - user["debt"]

        embed.add_field(
            name="📊 총 자산",
            value=f"**{total_asset:,}칩**",
            inline=False
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        embed.set_footer(
            text=f"{interaction.user.name}님의 자산 정보"
        )

        await interaction.response.send_message(
            embed=embed
        )