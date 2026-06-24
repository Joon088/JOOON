import discord
from db import get_user, deposit_money

def setup(bot):

    @bot.tree.command(name="입금", description="보유 칩을 은행에 입금합니다.")
    async def deposit(
        interaction: discord.Interaction,
        금액: int
    ):
        user = get_user(interaction.user.id)

        if not user:
            embed = discord.Embed(
                title="⚠️ 등록 필요",
                description="먼저 `/등록` 을 해주세요.",
                color=0xE74C3C
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if 금액 <= 0:
            embed = discord.Embed(
                title="⚠️ 잘못된 금액",
                description="입금 금액은 1칩 이상이어야 합니다.",
                color=0xE74C3C
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user["money"] < 금액:
            embed = discord.Embed(
                title="💸 보유 칩 부족",
                description="입금할 칩이 부족합니다.",
                color=0xE74C3C
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        updated_user = deposit_money(interaction.user.id, 금액)

        embed = discord.Embed(
            title="🏦 입금 완료",
            description="보유 칩을 은행에 안전하게 보관했습니다.",
            color=0x2ECC71
        )

        embed.add_field(
            name="입금 금액",
            value=f"**{금액:,}칩**",
            inline=True
        )

        embed.add_field(
            name="보유 칩",
            value=f"**{updated_user['money']:,}칩**",
            inline=True
        )

        embed.add_field(
            name="은행 예금",
            value=f"**{updated_user['bank']:,}칩**",
            inline=False
        )

        embed.set_footer(text="Casino Life • 은행에 있는 칩은 도박에 바로 사용되지 않습니다.")

        await interaction.response.send_message(embed=embed)