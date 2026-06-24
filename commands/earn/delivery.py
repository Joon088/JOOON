import discord
import random
from datetime import datetime, timedelta
from db import get_user, add_money

from utils.checks import check_jail

delivery_cooldowns = {}

def setup(bot):

    @bot.tree.command(name="배달", description="배달을 해서 칩을 법니다.")
    async def delivery(interaction: discord.Interaction):
        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 을 해주세요.", ephemeral=True)
            return
        
        if await check_jail(interaction):
            return

        now = datetime.now()
        last_time = delivery_cooldowns.get(user_id)

        if last_time and now < last_time + timedelta(minutes=30):
            remaining = (last_time + timedelta(minutes=30)) - now
            minutes = remaining.seconds // 60
            seconds = remaining.seconds % 60

            embed = discord.Embed(
                title="⏰ 배달 대기 중",
                description=f"남은 시간: **{minutes}분 {seconds}초**",
                color=0xE67E22
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        reward = random.randint(30000, 80000)
        new_money = add_money(user_id, reward)
        delivery_cooldowns[user_id] = now

        embed = discord.Embed(
            title="🛵 배달 완료!",
            description="무사히 배달을 끝냈습니다.",
            color=0x3498DB
        )
        embed.add_field(name="획득 보상", value=f"**+{reward:,}칩**", inline=True)
        embed.add_field(name="현재 잔액", value=f"**{new_money:,}칩**", inline=True)
        embed.set_footer(text="30분 후 다시 배달할 수 있습니다.")

        await interaction.response.send_message(embed=embed)