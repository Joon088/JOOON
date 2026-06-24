import discord

from db import get_user, remove_money, add_money, add_jackpot
from utils.checks import check_jail

def setup(bot):

    @bot.tree.command(name="송금", description="다른 유저에게 칩을 송금합니다.")
    async def transfer(
        interaction: discord.Interaction,
        상대: discord.Member,
        금액: int
    ):

        if not interaction.guild:
            await interaction.response.send_message(
                "서버에서만 사용할 수 있습니다.",
                ephemeral=True
            )
            return

        sender_id = interaction.user.id
        receiver_id = 상대.id
        guild_id = interaction.guild.id

        sender = get_user(sender_id)
        receiver = get_user(receiver_id)

        if not sender:
            await interaction.response.send_message(
                "먼저 `/등록` 해주세요.",
                ephemeral=True
            )
            return

        if await check_jail(interaction):
            return

        if 상대.bot:
            await interaction.response.send_message(
                "봇에게는 송금할 수 없습니다.",
                ephemeral=True
            )
            return

        if receiver_id == sender_id:
            await interaction.response.send_message(
                "자기 자신에게는 송금할 수 없습니다.",
                ephemeral=True
            )
            return

        if not receiver:
            await interaction.response.send_message(
                "상대방이 아직 `/등록` 하지 않았습니다.",
                ephemeral=True
            )
            return

        if 금액 <= 0:
            await interaction.response.send_message(
                "송금 금액은 1칩 이상이어야 합니다.",
                ephemeral=True
            )
            return

        if sender["money"] < 금액:
            await interaction.response.send_message(
                "보유 칩이 부족합니다.",
                ephemeral=True
            )
            return

        fee = int(금액 * 0.02)
        jackpot_add = int(금액 * 0.01)
        receive_amount = 금액 - fee

        remove_money(sender_id, 금액)
        add_money(receiver_id, receive_amount)
        add_jackpot(guild_id, jackpot_add)

        sender_balance = get_user(sender_id)["money"]
        receiver_balance = get_user(receiver_id)["money"]

        embed = discord.Embed(
            title="💸 송금 완료",
            description=f"{interaction.user.mention}님이 {상대.mention}님에게 칩을 송금했습니다.",
            color=0x2ECC71
        )

        embed.add_field(
            name="보낸 금액",
            value=f"**{금액:,}칩**",
            inline=True
        )

        embed.add_field(
            name="상대 수령",
            value=f"**{receive_amount:,}칩**",
            inline=True
        )

        embed.add_field(
            name="수수료",
            value=f"**{fee:,}칩**",
            inline=True
        )

        embed.add_field(
            name="🎰 잭팟 적립",
            value=f"**+{jackpot_add:,}칩**",
            inline=True
        )

        embed.add_field(
            name="내 잔액",
            value=f"**{sender_balance:,}칩**",
            inline=True
        )

        embed.add_field(
            name="상대 잔액",
            value=f"**{receiver_balance:,}칩**",
            inline=True
        )

        embed.set_footer(
            text="Casino Life • 유저 거래"
        )

        await interaction.response.send_message(embed=embed)