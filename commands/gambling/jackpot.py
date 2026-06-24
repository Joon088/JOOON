import discord
from db import get_jackpot

def setup(bot):

    @bot.tree.command(name="잭팟", description="현재 서버 잭팟을 확인합니다.")
    async def jackpot(interaction: discord.Interaction):

        if not interaction.guild:
            await interaction.response.send_message(
                "서버에서만 사용할 수 있는 명령어입니다.",
                ephemeral=True
            )
            return

        jackpot_data = get_jackpot(interaction.guild.id)

        last_winner = jackpot_data["last_winner"]
        last_amount = jackpot_data["last_amount"]

        if last_winner:
            member = interaction.guild.get_member(last_winner)
            last_winner_name = member.display_name if member else "알 수 없음"
        else:
            last_winner_name = "없음"

        embed = discord.Embed(
            title="🎰 서버 잭팟",
            description="이 서버에서 누적된 공용 잭팟입니다.",
            color=0xF1C40F
        )

        embed.add_field(
            name="💰 현재 누적금",
            value=f"**{jackpot_data['amount']:,}칩**",
            inline=False
        )

        embed.add_field(
            name="🏆 최근 당첨자",
            value=last_winner_name,
            inline=True
        )

        embed.add_field(
            name="💸 최근 당첨 금액",
            value=f"{last_amount:,}칩",
            inline=True
        )

        embed.set_footer(
            text="슬롯에서 극악 확률로 잭팟이 터집니다."
        )

        await interaction.response.send_message(embed=embed)