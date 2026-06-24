import discord
from discord import app_commands

from db import (
    set_guild_channel,
    get_guild_settings
)

CHANNEL_TYPES = ["공지", "로또", "잭팟", "주식"]

def setup(bot):

    @bot.tree.command(name="채널설정", description="공지용 채널을 설정합니다.")
    @app_commands.describe(
        종류="설정할 채널 종류",
        채널="설정할 디스코드 채널"
    )
    @app_commands.choices(
        종류=[
            app_commands.Choice(name="공지", value="공지"),
            app_commands.Choice(name="로또", value="로또"),
            app_commands.Choice(name="잭팟", value="잭팟"),
            app_commands.Choice(name="주식", value="주식"),
        ]
    )
    async def channel_setting(
        interaction: discord.Interaction,
        종류: app_commands.Choice[str],
        채널: discord.TextChannel
    ):

        if not interaction.guild:
            await interaction.response.send_message(
                "서버에서만 사용할 수 있는 명령어입니다.",
                ephemeral=True
            )
            return

        종류값 = 종류.value

        if 종류값 not in CHANNEL_TYPES:
            await interaction.response.send_message(
                "종류는 `공지`, `로또`, `잭팟`, `주식` 중 하나만 가능합니다.",
                ephemeral=True
            )
            return

        set_guild_channel(
            interaction.guild.id,
            종류값,
            채널.id
        )

        embed = discord.Embed(
            title="✅ 채널 설정 완료",
            description=f"**{종류값}** 채널이 설정되었습니다.",
            color=0x2ECC71
        )

        embed.add_field(
            name="설정 채널",
            value=채널.mention,
            inline=False
        )

        embed.set_footer(
            text="Casino Life • 서버 채널 설정"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    @bot.tree.command(name="채널확인", description="현재 서버 채널 설정을 확인합니다.")
    async def channel_check(interaction: discord.Interaction):

        if not interaction.guild:
            await interaction.response.send_message(
                "서버에서만 사용할 수 있는 명령어입니다.",
                ephemeral=True
            )
            return

        settings = get_guild_settings(interaction.guild.id)

        channel_map = {
            "📢 공지": settings["notice_channel"],
            "🎟 로또": settings["lotto_channel"],
            "🎰 잭팟": settings["jackpot_channel"],
            "📈 주식": settings["stock_channel"]
        }

        embed = discord.Embed(
            title="📋 서버 채널 설정",
            description="현재 설정된 공지 채널 목록입니다.",
            color=0x3498DB
        )

        for name, channel_id in channel_map.items():
            if channel_id:
                channel = interaction.guild.get_channel(channel_id)
                value = channel.mention if channel else "채널을 찾을 수 없음"
            else:
                if name != "📢 공지" and settings["notice_channel"]:
                    notice = interaction.guild.get_channel(settings["notice_channel"])
                    value = f"설정 안됨\n공지 채널 사용: {notice.mention if notice else '채널 없음'}"
                else:
                    value = "설정 안됨"

            embed.add_field(
                name=name,
                value=value,
                inline=False
            )

        embed.set_footer(
            text="로또/잭팟/주식 채널이 없으면 공지 채널을 사용합니다."
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )