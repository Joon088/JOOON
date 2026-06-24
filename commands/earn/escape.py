import discord
import random

from db import get_user, is_jailed, clear_jail, add_jail_time, remove_money, get_jail_remaining

def setup(bot):

    @bot.tree.command(name="탈옥", description="구금 상태에서 탈옥을 시도합니다.")
    async def escape(interaction: discord.Interaction):
        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 을 해주세요.", ephemeral=True)
            return

        if not is_jailed(user_id):
            embed = discord.Embed(
                title="🚔 구금 상태 아님",
                description="현재 구금 중이 아닙니다.",
                color=0x3498DB
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        roll = random.random()

        # 성공 20%
        if roll < 0.20:
            clear_jail(user_id)

            embed = discord.Embed(
                title="🏃 탈옥 성공!",
                description="감시가 허술한 틈을 타 교도소를 탈출했습니다.",
                color=0x2ECC71
            )
            embed.add_field(name="결과", value="구금 즉시 해제", inline=False)

            await interaction.response.send_message(embed=embed)
            return

        # 대실패 5%
        if roll < 0.25:
            add_jail_time(user_id, 30)

            fine = int(user["money"] * 0.20)
            new_money = remove_money(user_id, fine)

            remaining = get_jail_remaining(user_id)
            minutes = int(remaining.total_seconds() // 60)

            embed = discord.Embed(
                title="🚨 탈옥 대실패!",
                description="교도관에게 완전히 들켰습니다.",
                color=0x8E44AD
            )
            embed.add_field(name="추가 구금", value="**+30분**", inline=True)
            embed.add_field(name="추가 벌금", value=f"**-{fine:,}칩**", inline=True)
            embed.add_field(name="현재 잔액", value=f"**{new_money:,}칩**", inline=False)
            embed.add_field(name="남은 구금", value=f"약 **{minutes}분**", inline=False)

            await interaction.response.send_message(embed=embed)
            return

        # 실패 75%
        add_jail_time(user_id, 10)

        remaining = get_jail_remaining(user_id)
        minutes = int(remaining.total_seconds() // 60)

        embed = discord.Embed(
            title="🚔 탈옥 실패!",
            description="교도관에게 붙잡혔습니다.",
            color=0xE74C3C
        )
        embed.add_field(name="추가 구금", value="**+10분**", inline=True)
        embed.add_field(name="남은 구금", value=f"약 **{minutes}분**", inline=True)

        await interaction.response.send_message(embed=embed)