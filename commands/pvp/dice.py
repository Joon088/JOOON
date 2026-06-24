import discord
import random
from discord.ui import View, Button

from db import (
    get_user,
    add_money,
    remove_money,
    add_jackpot
)

from utils.checks import check_jail


class DiceView(View):
    def __init__(self, challenger, target, amount, guild_id):
        super().__init__(timeout=30)

        self.challenger = challenger
        self.target = target
        self.amount = amount
        self.guild_id = guild_id
        self.finished = False

    @discord.ui.button(label="수락", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: Button):

        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                "이 주사위 승부는 도전받은 사람만 수락할 수 있습니다.",
                ephemeral=True
            )
            return

        if self.finished:
            await interaction.response.send_message(
                "이미 종료된 승부입니다.",
                ephemeral=True
            )
            return

        if await check_jail(interaction):
            return

        challenger_user = get_user(self.challenger.id)
        target_user = get_user(self.target.id)

        if challenger_user["money"] < self.amount or target_user["money"] < self.amount:
            await interaction.response.send_message(
                "참가자 중 보유 칩이 부족한 사람이 있습니다.",
                ephemeral=True
            )
            return

        self.finished = True

        remove_money(self.challenger.id, self.amount)
        remove_money(self.target.id, self.amount)

        c_roll = random.randint(1, 6)
        t_roll = random.randint(1, 6)

        while c_roll == t_roll:
            c_roll = random.randint(1, 6)
            t_roll = random.randint(1, 6)

        total_pot = self.amount * 2
        fee = int(total_pot * 0.03)
        jackpot_add = int(total_pot * 0.01)
        winner_reward = total_pot - fee

        if c_roll > t_roll:
            winner = self.challenger
            loser = self.target
        else:
            winner = self.target
            loser = self.challenger

        add_money(winner.id, winner_reward)
        add_jackpot(self.guild_id, jackpot_add)

        winner_balance = get_user(winner.id)["money"]

        embed = discord.Embed(
            title="🎲 주사위 승부 결과",
            description="두 사람이 주사위를 굴렸습니다.",
            color=0xF1C40F
        )

        embed.add_field(
            name=f"{self.challenger.display_name}",
            value=f"🎲 **{c_roll}**",
            inline=True
        )

        embed.add_field(
            name=f"{self.target.display_name}",
            value=f"🎲 **{t_roll}**",
            inline=True
        )

        embed.add_field(
            name="🏆 승자",
            value=winner.mention,
            inline=False
        )

        embed.add_field(
            name="💀 패자",
            value=loser.mention,
            inline=True
        )

        embed.add_field(
            name="💰 승자 획득",
            value=f"**+{winner_reward:,}칩**",
            inline=True
        )

        embed.add_field(
            name="🎰 잭팟 적립",
            value=f"**+{jackpot_add:,}칩**",
            inline=True
        )

        embed.add_field(
            name="🏦 승자 잔액",
            value=f"**{winner_balance:,}칩**",
            inline=False
        )

        embed.set_footer(text="Casino Life • PvP 주사위")

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )

    @discord.ui.button(label="거절", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: Button):

        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                "이 주사위 승부는 도전받은 사람만 거절할 수 있습니다.",
                ephemeral=True
            )
            return

        self.finished = True

        embed = discord.Embed(
            title="❌ 주사위 승부 거절",
            description=f"{self.target.mention}님이 주사위 승부를 거절했습니다.",
            color=0xE74C3C
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )


def setup(bot):

    @bot.tree.command(name="주사위", description="유저와 주사위 PvP 도박을 합니다.")
    async def dice(
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

        challenger = interaction.user
        target = 상대

        if target.bot:
            await interaction.response.send_message("봇과는 승부할 수 없습니다.", ephemeral=True)
            return

        if target.id == challenger.id:
            await interaction.response.send_message("자기 자신과는 승부할 수 없습니다.", ephemeral=True)
            return

        challenger_user = get_user(challenger.id)
        target_user = get_user(target.id)

        if not challenger_user:
            await interaction.response.send_message("먼저 `/등록` 해주세요.", ephemeral=True)
            return

        if not target_user:
            await interaction.response.send_message("상대방이 아직 `/등록` 하지 않았습니다.", ephemeral=True)
            return

        if await check_jail(interaction):
            return

        if 금액 <= 0:
            await interaction.response.send_message("금액은 1 이상이어야 합니다.", ephemeral=True)
            return

        if challenger_user["money"] < 금액:
            await interaction.response.send_message("보유 칩이 부족합니다.", ephemeral=True)
            return

        if target_user["money"] < 금액:
            await interaction.response.send_message("상대방의 보유 칩이 부족합니다.", ephemeral=True)
            return

        total_pot = 금액 * 2
        fee = int(total_pot * 0.03)
        jackpot_add = int(total_pot * 0.01)
        winner_reward = total_pot - fee

        embed = discord.Embed(
            title="🎲 주사위 승부 신청",
            description=f"{challenger.mention}님이 {target.mention}님에게 주사위 승부를 신청했습니다.",
            color=0x3498DB
        )

        embed.add_field(name="참가 금액", value=f"각자 **{금액:,}칩**", inline=False)
        embed.add_field(name="승자 예상 수령", value=f"**{winner_reward:,}칩**", inline=True)
        embed.add_field(name="수수료", value=f"**{fee:,}칩**", inline=True)
        embed.add_field(name="잭팟 적립 예정", value=f"**{jackpot_add:,}칩**", inline=True)

        embed.set_footer(text="30초 안에 수락하지 않으면 자동 취소됩니다.")

        view = DiceView(
            challenger=challenger,
            target=target,
            amount=금액,
            guild_id=interaction.guild.id
        )

        await interaction.response.send_message(embed=embed, view=view)