import discord
from db import get_user, get_vip_display, get_vip_color

def setup(bot):

    @bot.tree.command(name="프로필", description="내 프로필을 확인합니다.")
    async def profile(interaction: discord.Interaction):

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

        total_asset = (
            user["money"]
            + user["bank"]
            - user["debt"]
        )

        embed = discord.Embed(
            title="👤 플레이어 프로필",
            color=get_vip_color(interaction.user.id)
        )

        embed.add_field(
            name="🎮 닉네임",
            value=interaction.user.display_name,
            inline=True
        )

        embed.add_field(
            name="⭐ VIP",
            value=get_vip_display(interaction.user.id),
            inline=True
        )

        embed.add_field(
            name="📈 신용등급",
            value=user["credit"],
            inline=True
        )

        embed.add_field(
            name="💰 보유 칩",
            value=f"{user['money']:,}칩",
            inline=True
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

        embed.add_field(
            name="📊 총 자산",
            value=f"**{total_asset:,}칩**",
            inline=False
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        embed.set_footer(
            text="Casino Life • 플레이어 정보"
        )

        await interaction.response.send_message(
            embed=embed
        )