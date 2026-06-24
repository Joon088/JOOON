import discord

from db import (
    get_user,
    get_casino,
    buy_casino,
    claim_casino_vault,
    rob_casino,
    acquire_casino,
    get_guild_channel,
    CASINO_PRICE
)

from utils.checks import check_jail


def format_remaining(td):
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60

    if days > 0:
        return f"{days}일 {hours}시간 {minutes}분"

    if hours > 0:
        return f"{hours}시간 {minutes}분"

    return f"{minutes}분"


async def send_casino_notice(bot, guild, embed):
    channel_id = get_guild_channel(guild.id, "공지")

    if not channel_id:
        return

    channel = guild.get_channel(channel_id)

    if not channel:
        return

    await channel.send(embed=embed)


def setup(bot):

    @bot.tree.command(name="카지노정보", description="현재 서버 카지노 정보를 확인합니다.")
    async def casino_info(interaction: discord.Interaction):

        if not interaction.guild:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        casino = get_casino(interaction.guild.id)
        owner_id = casino["owner_id"]

        if owner_id:
            owner = interaction.guild.get_member(owner_id)
            owner_name = owner.mention if owner else f"<@{owner_id}>"
        else:
            owner_name = "없음"

        protected_text = "없음"

        if casino["protected_until"]:
            from datetime import datetime

            if datetime.now() < casino["protected_until"]:
                protected_text = format_remaining(casino["protected_until"] - datetime.now())
            else:
                protected_text = "종료됨"

        embed = discord.Embed(
            title="🏨 서버 카지노 정보",
            description="서버당 단 하나만 존재하는 최종 사업체입니다.",
            color=0xF1C40F
        )

        embed.add_field(name="👑 소유자", value=owner_name, inline=False)
        embed.add_field(name="💰 현재 가치", value=f"**{casino['value']:,}칩**", inline=True)
        embed.add_field(name="🏦 카지노 금고", value=f"**{casino['vault']:,}칩**", inline=True)
        embed.add_field(name="📈 누적 수익", value=f"**{casino['total_profit']:,}칩**", inline=False)
        embed.add_field(name="🛡 인수 보호기간", value=f"**{protected_text}**", inline=False)

        if not owner_id:
            embed.add_field(
                name="구매 안내",
                value=f"`/카지노구매` 로 **{CASINO_PRICE:,}칩**에 구매할 수 있습니다.",
                inline=False
            )
        else:
            min_price = int(casino["value"] * 1.2)
            embed.add_field(
                name="인수 안내",
                value=f"최소 인수가: **{min_price:,}칩**\n`/카지노인수 금액`",
                inline=False
            )

        embed.set_footer(text="Casino Life • 카지노 구매/인수 후 3일간 보호됩니다.")

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="카지노구매", description="서버 카지노를 구매합니다.")
    async def casino_buy(interaction: discord.Interaction):

        if not interaction.guild:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 해주세요.", ephemeral=True)
            return

        if user["money"] < CASINO_PRICE:
            await interaction.response.send_message(
                f"보유 칩이 부족합니다.\n필요 금액: **{CASINO_PRICE:,}칩**",
                ephemeral=True
            )
            return

        casino = buy_casino(interaction.guild.id, user_id)

        if not casino:
            await interaction.response.send_message(
                "이미 이 서버의 카지노는 다른 사람이 소유하고 있습니다.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🏨 카지노 구매 완료",
            description=f"{interaction.user.mention}님이 이 서버의 카지노 오너가 되었습니다!",
            color=0xF1C40F
        )

        embed.add_field(name="구매가", value=f"**{CASINO_PRICE:,}칩**", inline=True)
        embed.add_field(name="현재 금고", value="**0칩**", inline=True)
        embed.add_field(name="🛡 보호기간", value="**3일**", inline=False)
        embed.add_field(
            name="오너 혜택",
            value=(
                "카지노 금고 수익 수령\n"
                "추후 오너 전용 도박장 이용\n"
                "추후 카지노 게임 확률 보너스 적용"
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed)

        notice = discord.Embed(
            title="🏨 서버 카지노 탄생",
            description=f"{interaction.user.mention}님이 서버 카지노를 구매했습니다!",
            color=0xF1C40F
        )

        notice.add_field(name="구매가", value=f"**{CASINO_PRICE:,}칩**", inline=True)
        notice.add_field(name="보호기간", value="**3일**", inline=True)

        await send_casino_notice(bot, interaction.guild, notice)

    @bot.tree.command(name="카지노수익", description="카지노 금고 수익을 수령합니다.")
    async def casino_profit(interaction: discord.Interaction):

        if not interaction.guild:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 해주세요.", ephemeral=True)
            return

        amount = claim_casino_vault(interaction.guild.id, user_id)

        if amount is None:
            await interaction.response.send_message(
                "카지노 소유자만 수익을 수령할 수 있습니다.",
                ephemeral=True
            )
            return

        if amount <= 0:
            await interaction.response.send_message(
                "수령할 카지노 수익이 없습니다.",
                ephemeral=True
            )
            return

        user = get_user(user_id)

        embed = discord.Embed(
            title="💰 카지노 수익 수령",
            description="카지노 금고의 수익을 수령했습니다.",
            color=0x2ECC71
        )

        embed.add_field(name="수령 금액", value=f"**+{amount:,}칩**", inline=True)
        embed.add_field(name="현재 잔액", value=f"**{user['money']:,}칩**", inline=True)

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="카지노털기", description="카지노 금고를 털어봅니다.")
    async def casino_rob(interaction: discord.Interaction):

        if not interaction.guild:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 해주세요.", ephemeral=True)
            return

        if await check_jail(interaction):
            return

        result = rob_casino(interaction.guild.id, user_id)

        if result["reason"] == "NO_OWNER":
            await interaction.response.send_message("아직 이 서버에는 카지노 소유자가 없습니다.", ephemeral=True)
            return

        if result["reason"] == "OWNER":
            await interaction.response.send_message("자신의 카지노는 털 수 없습니다.", ephemeral=True)
            return

        if result["reason"] == "EMPTY":
            await interaction.response.send_message("카지노 금고가 비어 있습니다.", ephemeral=True)
            return

        if result["success"]:
            embed = discord.Embed(
                title="💰 카지노 털기 성공!",
                description=f"{interaction.user.mention}님이 카지노 금고를 털었습니다!",
                color=0x2ECC71
            )

            embed.add_field(name="강탈 비율", value=f"**{result['percent']}%**", inline=True)
            embed.add_field(name="획득 금액", value=f"**+{result['stolen']:,}칩**", inline=True)
            embed.add_field(name="남은 금고", value=f"**{result['vault']:,}칩**", inline=False)

            await interaction.response.send_message(embed=embed)
            return

        embed = discord.Embed(
            title="🚔 카지노 털기 실패!",
            description="경비에게 붙잡혀 30분 동안 구금됩니다.",
            color=0xE74C3C
        )

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="카지노인수", description="현재 카지노를 인수합니다.")
    async def casino_acquire(
        interaction: discord.Interaction,
        금액: int
    ):

        if not interaction.guild:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return

        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 해주세요.", ephemeral=True)
            return

        if 금액 <= 0:
            await interaction.response.send_message("금액은 1 이상이어야 합니다.", ephemeral=True)
            return

        result = acquire_casino(interaction.guild.id, user_id, 금액)

        if result["reason"] == "NO_OWNER":
            await interaction.response.send_message("아직 인수할 카지노가 없습니다. `/카지노구매` 를 사용하세요.", ephemeral=True)
            return

        if result["reason"] == "OWNER":
            await interaction.response.send_message("이미 카지노 소유자입니다.", ephemeral=True)
            return

        if result["reason"] == "PROTECTED":
            await interaction.response.send_message(
                f"현재 카지노는 보호 기간입니다.\n남은 시간: **{format_remaining(result['remaining'])}**",
                ephemeral=True
            )
            return

        if result["reason"] == "LOW_PRICE":
            await interaction.response.send_message(
                f"인수 금액이 부족합니다.\n최소 인수가: **{result['min_price']:,}칩**",
                ephemeral=True
            )
            return

        if result["reason"] == "NO_MONEY":
            await interaction.response.send_message("보유 칩이 부족합니다.", ephemeral=True)
            return

        old_owner = interaction.guild.get_member(result["old_owner_id"])
        old_owner_text = old_owner.mention if old_owner else f"<@{result['old_owner_id']}>"

        embed = discord.Embed(
            title="🏨 카지노 인수 완료",
            description=f"{interaction.user.mention}님이 카지노를 인수했습니다!",
            color=0xF1C40F
        )

        embed.add_field(name="이전 소유자", value=old_owner_text, inline=True)
        embed.add_field(name="새 소유자", value=interaction.user.mention, inline=True)
        embed.add_field(name="인수 금액", value=f"**{result['amount']:,}칩**", inline=False)
        embed.add_field(name="기존 금고 정산", value=f"**{result['old_vault']:,}칩**", inline=False)
        embed.add_field(name="새 보호기간", value="**3일**", inline=False)

        embed.set_footer(text="기존 금고는 이전 소유자에게 정산되고 새 금고는 0부터 시작합니다.")

        await interaction.response.send_message(embed=embed)

        notice = discord.Embed(
            title="🏨 카지노 인수전 종료",
            description=f"{interaction.user.mention}님이 서버 카지노를 인수했습니다!",
            color=0xF1C40F
        )

        notice.add_field(name="이전 소유자", value=old_owner_text, inline=True)
        notice.add_field(name="새 소유자", value=interaction.user.mention, inline=True)
        notice.add_field(name="인수 금액", value=f"**{result['amount']:,}칩**", inline=False)
        notice.add_field(name="기존 금고 정산", value=f"**{result['old_vault']:,}칩**", inline=False)
        notice.add_field(name="보호기간", value="**3일**", inline=False)

        await send_casino_notice(bot, interaction.guild, notice)