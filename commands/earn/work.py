import discord
import random
from datetime import datetime, timedelta
from db import get_user, add_money

from utils.checks import check_jail

work_cooldowns = {}

def setup(bot):

    @bot.tree.command(name="알바", description="알바를 해서 칩을 법니다.")
    async def work(interaction: discord.Interaction):
        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            embed = discord.Embed(
                title="⚠️ 등록 필요",
                description="먼저 `/등록` 을 해주세요.",
                color=0xE74C3C
            )
        if await check_jail(interaction):
            return
            
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return

        now = datetime.now()
        last_time = work_cooldowns.get(user_id)

        if last_time and now < last_time + timedelta(minutes=10):
            remaining = (last_time + timedelta(minutes=10)) - now

            minutes = remaining.seconds // 60
            seconds = remaining.seconds % 60

            embed = discord.Embed(
                title="⏰ 알바 대기 중",
                description="아직 알바를 할 수 없습니다.",
                color=0xE67E22
            )

            embed.add_field(
                name="남은 시간",
                value=f"{minutes}분 {seconds}초",
                inline=False
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return

        reward = random.randint(10000, 30000)
        new_money = add_money(user_id, reward)

        work_cooldowns[user_id] = now

        jobs = [
            ("🏪", "편의점 알바"),
            ("☕", "카페 알바"),
            ("🖥️", "PC방 알바"),
            ("🍜", "식당 서빙"),
            ("📄", "전단지 배포")
        ]

        emoji, job = random.choice(jobs)

        embed = discord.Embed(
            title="💼 알바 완료!",
            description="오늘도 열심히 일했습니다.",
            color=0x3498DB
        )

        embed.add_field(
            name="직업",
            value=f"{emoji} {job}",
            inline=False
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
            text="10분 후 다시 알바할 수 있습니다."
        )

        await interaction.response.send_message(
            embed=embed
        )