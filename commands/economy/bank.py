import discord
from db import get_user

def setup(bot):

    @bot.tree.command(name="은행", description="은행 계좌를 확인합니다.")
    async def bank(interaction: discord.Interaction):
        user = get_user(interaction.user.id)

        if not user:
            embed = discord.Embed(
                title="⚠️ 등록 필요",
                description="먼저 `/등록` 을 해주세요.",
                color=0xE74C3C
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        total_asset = user["money"] + user["bank"] - user["debt"]

        embed = discord.Embed(
            title="🏦 은행 계좌",
            description="현재 은행 정보를 확인합니다.",
            color=0x3498DB
        )

        embed.add_field(
            name="💵 보유 칩",
            value=f"**{user['money']:,}칩**",
            inline=True
        )

        embed.add_field(
            name="🏦 은행 예금",
            value=f"**{user['bank']:,}칩**",
            inline=True
        )

        embed.add_field(
            name="📊 총 자산",
            value=f"**{total_asset:,}칩**",
            inline=False
        )

        embed.set_footer(text="Casino Life • 안전한 자산 관리")

        await interaction.response.send_message(embed=embed)