import discord
import random
from datetime import datetime, timedelta
from db import get_user, add_money

from utils.checks import check_jail

mining_cooldowns = {}

def setup(bot):

    @bot.tree.command(name="광산", description="광산에서 광물을 캐서 칩을 법니다.")
    async def mining(interaction: discord.Interaction):
        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 을 해주세요.", ephemeral=True)
            return
        
        if await check_jail(interaction):
            return

        now = datetime.now()
        last_time = mining_cooldowns.get(user_id)

        if last_time and now < last_time + timedelta(hours=1):
            remaining = (last_time + timedelta(hours=1)) - now
            minutes = remaining.seconds // 60
            seconds = remaining.seconds % 60

            embed = discord.Embed(
                title="⏰ 광산 대기 중",
                description=f"남은 시간: **{minutes}분 {seconds}초**",
                color=0xE67E22
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        ores = [
            ("🪨 돌", 20000, 50000),
            ("⛓️ 철", 50000, 100000),
            ("🥇 금", 100000, 180000),
            ("💎 다이아", 180000, 250000)
        ]

        ore = random.choices(
            ores,
            weights=[55, 30, 12, 3],
            k=1
        )[0]

        ore_name, min_reward, max_reward = ore
        reward = random.randint(min_reward, max_reward)
        new_money = add_money(user_id, reward)
        mining_cooldowns[user_id] = now

        embed = discord.Embed(
            title="⛏️ 채굴 완료!",
            description="광산에서 광물을 발견했습니다.",
            color=0x95A5A6
        )
        embed.add_field(name="획득 광물", value=ore_name, inline=False)
        embed.add_field(name="판매 금액", value=f"**+{reward:,}칩**", inline=True)
        embed.add_field(name="현재 잔액", value=f"**{new_money:,}칩**", inline=True)
        embed.set_footer(text="1시간 후 다시 채굴할 수 있습니다.")

        await interaction.response.send_message(embed=embed)