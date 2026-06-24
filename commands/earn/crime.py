import discord
import random
from datetime import datetime, timedelta

from db import get_user, add_money, remove_money, set_jail
from utils.checks import check_jail

crime_cooldowns = {}

def setup(bot):

    @bot.tree.command(name="범죄", description="위험한 범죄로 큰돈을 노립니다.")
    async def crime(interaction: discord.Interaction):
        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 을 해주세요.", ephemeral=True)
            return

        if await check_jail(interaction):
            return

        now = datetime.now()
        last_time = crime_cooldowns.get(user_id)

        if last_time and now < last_time + timedelta(hours=2):
            remaining = (last_time + timedelta(hours=2)) - now
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60

            embed = discord.Embed(
                title="⏰ 범죄 대기 중",
                description=f"남은 시간: **{hours}시간 {minutes}분**",
                color=0xE67E22
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        crime_cooldowns[user_id] = now

        roll = random.random()

        # 성공 40%
        if roll < 0.40:
            reward = random.randint(100000, 500000)
            new_money = add_money(user_id, reward)

            embed = discord.Embed(
                title="🕶️ 범죄 성공!",
                description="위험한 작전에 성공했습니다.",
                color=0x2ECC71
            )
            embed.add_field(name="획득 금액", value=f"**+{reward:,}칩**", inline=True)
            embed.add_field(name="현재 잔액", value=f"**{new_money:,}칩**", inline=True)
            embed.set_footer(text="2시간 후 다시 시도할 수 있습니다.")

            await interaction.response.send_message(embed=embed)
            return

        # 실패 51% - 벌금만
        if roll < 0.91:
            percent = random.randint(10, 30)
            fine = int(user["money"] * percent / 100)
            new_money = remove_money(user_id, fine)

            embed = discord.Embed(
                title="💸 범죄 실패!",
                description="경찰의 눈을 피해 도망쳤지만 일부 칩을 잃었습니다.",
                color=0xE67E22
            )
            embed.add_field(name="압수 비율", value=f"**{percent}%**", inline=True)
            embed.add_field(name="압수 금액", value=f"**-{fine:,}칩**", inline=True)
            embed.add_field(name="현재 잔액", value=f"**{new_money:,}칩**", inline=False)
            embed.set_footer(text="2시간 후 다시 시도할 수 있습니다.")

            await interaction.response.send_message(embed=embed)
            return

        # 실패 9% - 10분 구금
        if roll < 0.99:
            percent = random.randint(20, 50)
            fine = int(user["money"] * percent / 100)
            new_money = remove_money(user_id, fine)

            jail_minutes = 10
            set_jail(user_id, datetime.now() + timedelta(minutes=jail_minutes))

            embed = discord.Embed(
                title="🚔 경범죄 적발!",
                description="경찰에게 붙잡혀 벌금과 구금을 받았습니다.",
                color=0xE74C3C
            )
            embed.add_field(name="압수 비율", value=f"**{percent}%**", inline=True)
            embed.add_field(name="압수 금액", value=f"**-{fine:,}칩**", inline=True)
            embed.add_field(name="🚔 구금", value=f"**{jail_minutes}분**", inline=True)
            embed.add_field(name="현재 잔액", value=f"**{new_money:,}칩**", inline=False)

            await interaction.response.send_message(embed=embed)
            return

        # 대실패 1% - 30분 구금
        percent = random.randint(50, 80)
        fine = int(user["money"] * percent / 100)
        new_money = remove_money(user_id, fine)

        jail_minutes = 30
        set_jail(user_id, datetime.now() + timedelta(minutes=jail_minutes))

        embed = discord.Embed(
            title="🚨 중범죄 적발!",
            description="대규모 범죄가 적발되었습니다.",
            color=0x8E44AD
        )
        embed.add_field(name="압수 비율", value=f"**{percent}%**", inline=True)
        embed.add_field(name="압수 금액", value=f"**-{fine:,}칩**", inline=True)
        embed.add_field(name="🚔 구금", value=f"**{jail_minutes}분**", inline=True)
        embed.add_field(name="현재 잔액", value=f"**{new_money:,}칩**", inline=False)

        await interaction.response.send_message(embed=embed)