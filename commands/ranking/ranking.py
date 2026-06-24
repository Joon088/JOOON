import discord
from db import get_ranking, get_vip_display

def setup(bot):

    @bot.tree.command(name="랭킹", description="현재 서버 재산 랭킹을 확인합니다.")
    async def ranking(interaction: discord.Interaction):

        ranking_data = get_ranking()

        if not interaction.guild:
            await interaction.response.send_message(
                "서버에서만 사용할 수 있는 명령어입니다.",
                ephemeral=True
            )
            return

        server_member_ids = [member.id for member in interaction.guild.members]

        server_ranking = [
            data for data in ranking_data
            if data["user_id"] in server_member_ids
        ]

        if not server_ranking:
            embed = discord.Embed(
                title="🏆 서버 재산 랭킹",
                description="아직 이 서버에 등록된 유저가 없습니다.",
                color=0xE74C3C
            )
            await interaction.response.send_message(embed=embed)
            return

        description = ""
        medals = ["🥇", "🥈", "🥉"]

        for index, data in enumerate(server_ranking[:10], start=1):
            medal = medals[index - 1] if index <= 3 else f"{index}위"

            member = interaction.guild.get_member(data["user_id"])
            name = member.display_name if member else data["username"]

            vip = get_vip_display(data["user_id"])

            description += (
                f"{medal} **{name}**\n"
                f"⭐ {vip}\n"
                f"💰 총자산: **{data['total_asset']:,}칩**\n\n"
            )

        first_user = server_ranking[0]["user_id"]

        embed = discord.Embed(
            title="🏆 카지노 라이프 재산 랭킹",
            description=description,
            color=get_vip_color(first_user)
        )

        embed.set_footer(
            text="현재 서버에 있는 등록 유저만 표시됩니다."
        )

        await interaction.response.send_message(embed=embed)