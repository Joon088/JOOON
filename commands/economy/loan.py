import discord
from discord.ui import View, Button

from db import (
    get_user,
    add_debt,
    get_loan_limit,
    get_interest_rate,
    apply_daily_interest,
    update_vip
)

class LoanConfirmView(View):
    def __init__(self, user_id: int, amount: int):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.amount = amount

    @discord.ui.button(label="확인", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "이 대출 신청은 본인만 선택할 수 있습니다.",
                ephemeral=True
            )
            return

        user = get_user(self.user_id)

        if not user:
            await interaction.response.send_message("등록 정보가 없습니다.", ephemeral=True)
            return

        limit = get_loan_limit(self.user_id)

        if user["debt"] + self.amount > limit:
            await interaction.response.send_message(
                "대출 한도를 초과했습니다.",
                ephemeral=True
            )
            return

        add_debt(self.user_id, self.amount)
        user = get_user(self.user_id)

        embed = discord.Embed(
            title="🏦 대출 완료",
            description="대출금이 지급되었습니다.",
            color=0x2ECC71
        )

        embed.add_field(name="대출 금액", value=f"**{self.amount:,}칩**", inline=True)
        embed.add_field(name="현재 빚", value=f"**{user['debt']:,}칩**", inline=True)
        embed.add_field(name="보유 칩", value=f"**{user['money']:,}칩**", inline=False)

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="취소", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "이 대출 신청은 본인만 선택할 수 있습니다.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="❌ 대출 취소",
            description="대출 신청이 취소되었습니다.",
            color=0xE74C3C
        )

        await interaction.response.edit_message(embed=embed, view=None)


def setup(bot):

    @bot.tree.command(name="대출", description="은행에서 칩을 대출받습니다.")
    async def loan(interaction: discord.Interaction, 금액: int):
        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 을 해주세요.", ephemeral=True)
            return

        if 금액 <= 0:
            await interaction.response.send_message("대출 금액은 1칩 이상이어야 합니다.", ephemeral=True)
            return

        interest_added = apply_daily_interest(user_id)
        update_vip(user_id)

        user = get_user(user_id)
        limit = get_loan_limit(user_id)
        rate = get_interest_rate(user_id)

        if user["debt"] + 금액 > limit:
            await interaction.response.send_message(
                f"대출 한도를 초과했습니다.\n현재 한도: **{limit:,}칩**",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🏦 대출 신청서",
            description="정말 대출을 진행하시겠습니까?",
            color=0xF1C40F
        )

        embed.add_field(name="신청 금액", value=f"**{금액:,}칩**", inline=True)
        embed.add_field(name="현재 빚", value=f"**{user['debt']:,}칩**", inline=True)
        embed.add_field(name="대출 한도", value=f"**{limit:,}칩**", inline=False)
        embed.add_field(name="VIP 등급", value=f"**{user['vip']}**", inline=True)
        embed.add_field(name="일일 이자", value=f"**{rate}%**", inline=True)

        if interest_added:
            embed.add_field(
                name="오늘 적용된 이자",
                value=f"**+{interest_added:,}칩**",
                inline=False
            )

        embed.add_field(
            name="⚠️ 주의사항",
            value="대출금은 매일 이자가 붙습니다.\n상환하지 않으면 빚이 계속 증가합니다.",
            inline=False
        )

        view = LoanConfirmView(user_id, 금액)

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )