import discord
from db import get_user, withdraw_money

def setup(bot):

    @bot.tree.command(name="출금", description="은행에 있는 칩을 출금합니다.")
    async def withdraw(
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
                description="출금 금액은 1칩 이상이어야 합니다.",
                color=0xE74C3C
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if user["bank"] < 금액:
            embed = discord.Embed(
                title="🏦 은행 잔액 부족",
                description="은행에 있는 칩이 부족합니다.",
                color=0xE74C3C
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        updated_user = withdraw_money(interaction.user.id, 금액)

        embed = discord.Embed(
            title="💵 출금 완료",
            description="은행에서 칩을 출금했습니다.",
            color=0x2ECC71
        )

        embed.add_field(
            name="출금 금액",
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

        embed.set_footer(text="Casino Life • 출금한 칩은 바로 사용할 수 있습니다.")

        await interaction.response.send_message(embed=embed)