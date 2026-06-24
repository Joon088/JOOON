import discord
from db import get_user, create_user


def setup(bot):

    @bot.tree.command(name="등록", description="카지노 라이프에 등록합니다.")
    async def register(interaction: discord.Interaction):
        user_id = interaction.user.id
        username = interaction.user.display_name

        existing_user = get_user(user_id)

        if existing_user:
            embed = discord.Embed(
                title="⚠️ 이미 등록되어 있습니다",
                description=(
                    "이미 카지노 라이프 계정이 존재합니다.\n"
                    "`/프로필` 또는 `/잔액`으로 내 정보를 확인해보세요."
                ),
                color=0xE74C3C
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return

        create_user(user_id, username)

        embed = discord.Embed(
            title="🎰 카지노 라이프 등록 완료!",
            description=(
                f"{interaction.user.mention}님, 카지노 라이프에 오신 것을 환영합니다.\n"
                "이제 당신의 칩 인생이 시작됩니다."
            ),
            color=0xF1C40F
        )

        embed.add_field(
            name="💰 가입 보상",
            value="**50,000칩**",
            inline=True
        )

        embed.add_field(
            name="⭐ 시작 등급",
            value="🥉 **Bronze**",
            inline=True
        )

        embed.add_field(
            name="📌 다음 단계",
            value=(
                "`/잔액` - 보유 칩 확인\n"
                "`/출석` - 첫 보상 받기\n"
                "`/가이드` - 성장 루트 확인"
            ),
            inline=False
        )

        embed.add_field(
            name="🎯 목표",
            value=(
                "돈을 벌고, 도박하고, 투자해서\n"
                "**나만의 카지노**를 운영해보세요."
            ),
            inline=False
        )

        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="🎰 Casino Life • 한 번의 선택으로 인생이 바뀐다")

        await interaction.response.send_message(embed=embed)

        try:
            dm_embed = discord.Embed(
                title="🎰 카지노 라이프에 오신 것을 환영합니다!",
                description=(
                    "가입이 완료되었습니다.\n\n"
                    "💰 시작 자금: **50,000칩**\n"
                    "🥉 시작 등급: **Bronze**"
                ),
                color=0x3498DB
            )

            dm_embed.add_field(
                name="📖 처음이라면",
                value=(
                    "`/가이드` - 추천 성장 루트\n"
                    "`/도움말` - 전체 명령어 목록\n"
                    "`/프로필` - 내 정보 확인"
                ),
                inline=False
            )

            dm_embed.add_field(
                name="🚀 추천 시작",
                value=(
                    "`/출석` → `/알바` → `/배달`\n"
                    "순서로 첫 자금을 모아보세요."
                ),
                inline=False
            )

            dm_embed.add_field(
                name="🎯 최종 목표",
                value=(
                    "칩을 벌고, 투자하고, 승부해서\n"
                    "**카지노 오너**가 되어보세요."
                ),
                inline=False
            )

            dm_embed.set_footer(text="🎰 Casino Life • 자세한 설명은 /가이드 에서 확인하세요.")

            await interaction.user.send(embed=dm_embed)

        except discord.Forbidden:
            pass