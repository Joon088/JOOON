import discord
from datetime import datetime, timedelta
from db import get_user, add_money

daily_cooldowns = {}

def setup(bot):

    @bot.tree.command(name="출석", description="일일 출석 보상을 받습니다.")
    async def daily(interaction: discord.Interaction):
        user_id = interaction.user.id
        user = get_user(user_id)

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

        now = datetime.now()
        last_time = daily_cooldowns.get(user_id)

        if last_time and now < last_time + timedelta(hours=24):
            remaining = (last_time + timedelta(hours=24)) - now

            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60

            embed = discord.Embed(
                title="⏰ 출석 대기 중",
                description="아직 출석 보상을 받을 수 없습니다.",
                color=0xE67E22
            )

            embed.add_field(
                name="남은 시간",
                value=f"{hours}시간 {minutes}분",
                inline=False
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return

        reward = 50000
        new_money = add_money(user_id, reward)

        daily_cooldowns[user_id] = now

        embed = discord.Embed(
            title="🎁 출석 완료!",
            description="오늘의 출석 보상을 획득했습니다.",
            color=0x2ECC71
        )

        embed.add_field(
            name="획득 보상",
            value=f"**+{reward:,}칩**",
            inline=True
        )

        embed.add_field(
            name="현재 잔액",
            value=f"**{new_money:,}칩**",
            inline=True
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        embed.set_footer(
            text="내일 다시 출석 보상을 받을 수 있습니다."
        )

        await interaction.response.send_message(
            embed=embed
        )