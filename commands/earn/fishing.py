import discord
import random
from datetime import datetime, timedelta
from db import get_user, add_money

from utils.checks import check_jail

fishing_cooldowns = {}

def setup(bot):

    @bot.tree.command(name="낚시", description="낚시로 물고기를 잡아 칩을 법니다.")
    async def fishing(interaction: discord.Interaction):
        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 을 해주세요.", ephemeral=True)
            return
        
        if await check_jail(interaction):
            return

        now = datetime.now()
        last_time = fishing_cooldowns.get(user_id)

        if last_time and now < last_time + timedelta(minutes=20):
            remaining = (last_time + timedelta(minutes=20)) - now
            minutes = remaining.seconds // 60
            seconds = remaining.seconds % 60

            embed = discord.Embed(
                title="⏰ 낚시 대기 중",
                description=f"남은 시간: **{minutes}분 {seconds}초**",
                color=0xE67E22
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        fish_list = [
            ("🐟 잡어", 5000, 20000),
            ("🐠 고등어", 20000, 50000),
            ("🐡 참치", 50000, 100000),
            ("🐬 황금 물고기", 100000, 150000)
        ]

        fish = random.choices(
            fish_list,
            weights=[50, 30, 15, 5],
            k=1
        )[0]

        fish_name, min_reward, max_reward = fish
        reward = random.randint(min_reward, max_reward)
        new_money = add_money(user_id, reward)
        fishing_cooldowns[user_id] = now

        embed = discord.Embed(
            title="🎣 낚시 성공!",
            description="물고기를 잡아서 판매했습니다.",
            color=0x1ABC9C
        )
        embed.add_field(name="잡은 물고기", value=fish_name, inline=False)
        embed.add_field(name="판매 금액", value=f"**+{reward:,}칩**", inline=True)
        embed.add_field(name="현재 잔액", value=f"**{new_money:,}칩**", inline=True)
        embed.set_footer(text="20분 후 다시 낚시할 수 있습니다.")

        await interaction.response.send_message(embed=embed)