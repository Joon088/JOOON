import discord
from db import is_jailed, get_jail_remaining

async def check_jail(interaction: discord.Interaction):
    user_id = interaction.user.id

    if not is_jailed(user_id):
        return False

    remaining = get_jail_remaining(user_id)

    if not remaining:
        return False

    minutes = int(remaining.total_seconds() // 60)
    seconds = int(remaining.total_seconds() % 60)

    embed = discord.Embed(
        title="🚔 구금 상태",
        description="현재 구금 중이라 이 명령어를 사용할 수 없습니다.",
        color=0xE74C3C
    )

    embed.add_field(
        name="남은 시간",
        value=f"**{minutes}분 {seconds}초**",
        inline=False
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )

    return True