import discord
import random
from discord.ui import View, Button

from db import get_user, add_money, remove_money, add_jackpot, add_casino_vault, casino_owner_bonus
from utils.checks import check_jail


def draw_card():
    cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
    return random.choice(cards)


def hand_value(hand):
    total = sum(hand)
    aces = hand.count(11)

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total


def hand_text(hand):
    return " ".join([f"`{card}`" for card in hand])


class BlackjackView(View):
    def __init__(self, user_id, amount, guild_id):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.amount = amount
        self.guild_id = guild_id
        self.player_hand = [draw_card(), draw_card()]
        self.dealer_hand = [draw_card(), draw_card()]
        self.finished = False

    async def finish_game(self, interaction: discord.Interaction):
        self.finished = True

        player_score = hand_value(self.player_hand)
        dealer_score = hand_value(self.dealer_hand)

        while dealer_score < 17:
            self.dealer_hand.append(draw_card())
            dealer_score = hand_value(self.dealer_hand)

        title = ""
        color = 0x3498DB
        result_text = ""
        reward = 0
        jackpot_add = 0
        casino_add = 0
        owner_bonus = False

        if player_score > 21:

            if casino_owner_bonus(self.guild_id, self.user_id):
                title = "🏨 카지노 오너 보너스!"
                result_text = "버스트였지만 카지노 오너 특권으로 손실이 무효 처리되었습니다."
                owner_bonus = True
                color = 0xF1C40F

            else:
                title = "💀 블랙잭 패배"
                result_text = "버스트로 패배했습니다."
                remove_money(self.user_id, self.amount)

                jackpot_add = int(self.amount * 0.05)
                add_jackpot(self.guild_id, jackpot_add)

                casino_add = int(self.amount * 0.02)
                add_casino_vault(self.guild_id, casino_add)

                color = 0xE74C3C

            remove_money(self.user_id, self.amount)
            jackpot_add = int(self.amount * 0.05)
            add_jackpot(self.guild_id, jackpot_add)
            casino_add = int(self.amount * 0.02)
            add_casino_vault(self.guild_id, casino_add)
            color = 0xE74C3C

        elif dealer_score > 21 or player_score > dealer_score:
            title = "🎉 블랙잭 승리"
            result_text = "딜러를 이겼습니다."
            reward = self.amount
            add_money(self.user_id, reward)
            color = 0x2ECC71

        elif player_score == dealer_score:
            title = "🤝 블랙잭 무승부"
            result_text = "승부가 비겼습니다."
            color = 0x95A5A6

        else:

            if casino_owner_bonus(self.guild_id, self.user_id):
                title = "🏨 카지노 오너 보너스!"
                result_text = "딜러에게 질 뻔했지만 카지노 오너 특권으로 손실이 무효 처리되었습니다."
                owner_bonus = True
                color = 0xF1C40F

            else:
                title = "💀 블랙잭 패배"
                result_text = "딜러에게 패배했습니다."
                remove_money(self.user_id, self.amount)

                jackpot_add = int(self.amount * 0.05)
                add_jackpot(self.guild_id, jackpot_add)

                casino_add = int(self.amount * 0.02)
                add_casino_vault(self.guild_id, casino_add)

                color = 0xE74C3C

            jackpot_add = int(self.amount * 0.05)
            add_jackpot(self.guild_id, jackpot_add)
            casino_add = int(self.amount * 0.02)
            add_casino_vault(self.guild_id, casino_add)
            color = 0xE74C3C

        user = get_user(self.user_id)

        embed = discord.Embed(
            title=title,
            description=result_text,
            color=color
        )

        embed.add_field(
            name="🧑 내 카드",
            value=f"{hand_text(self.player_hand)}\n합계: **{player_score}**",
            inline=True
        )

        embed.add_field(
            name="🎩 딜러 카드",
            value=f"{hand_text(self.dealer_hand)}\n합계: **{dealer_score}**",
            inline=True
        )

        if reward > 0:
            embed.add_field(
                name="💰 획득",
                value=f"**+{reward:,}칩**",
                inline=False
            )

        if jackpot_add > 0:
            embed.add_field(
                name="🎰 잭팟 적립",
                value=f"**+{jackpot_add:,}칩**",
                inline=False
            )

        if casino_add > 0:
            embed.add_field(
                name="🏨 카지노 금고",
                value=f"**+{casino_add:,}칩**",
                inline=False
            )    

        if owner_bonus:
            embed.add_field(
            name="🏨 카지노 오너 보너스",
            value="이번 패배는 무효 처리되었습니다!",
            inline=False
            )

        embed.add_field(
            name="🏦 현재 잔액",
            value=f"**{user['money']:,}칩**",
            inline=False
        )

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="히트", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: Button):

        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "이 블랙잭은 신청자만 조작할 수 있습니다.",
                ephemeral=True
            )
            return

        if self.finished:
            await interaction.response.send_message(
                "이미 종료된 게임입니다.",
                ephemeral=True
            )
            return

        self.player_hand.append(draw_card())

        if hand_value(self.player_hand) >= 21:
            await self.finish_game(interaction)
            return

        embed = self.make_playing_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="스탠드", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: Button):

        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "이 블랙잭은 신청자만 조작할 수 있습니다.",
                ephemeral=True
            )
            return

        if self.finished:
            await interaction.response.send_message(
                "이미 종료된 게임입니다.",
                ephemeral=True
            )
            return

        await self.finish_game(interaction)

    def make_playing_embed(self):
        player_score = hand_value(self.player_hand)

        embed = discord.Embed(
            title="🃏 블랙잭",
            description="히트 또는 스탠드를 선택하세요.",
            color=0x3498DB
        )

        embed.add_field(
            name="🧑 내 카드",
            value=f"{hand_text(self.player_hand)}\n합계: **{player_score}**",
            inline=True
        )

        embed.add_field(
            name="🎩 딜러 카드",
            value=f"`{self.dealer_hand[0]}` `?`\n합계: **?**",
            inline=True
        )

        embed.add_field(
            name="베팅 금액",
            value=f"**{self.amount:,}칩**",
            inline=False
        )

        return embed


def setup(bot):

    @bot.tree.command(name="블랙잭", description="딜러와 블랙잭을 합니다.")
    async def blackjack(interaction: discord.Interaction, 금액: int):

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

        if 금액 <= 0:
            await interaction.response.send_message("금액은 1 이상이어야 합니다.", ephemeral=True)
            return

        if user["money"] < 금액:
            await interaction.response.send_message("보유 칩이 부족합니다.", ephemeral=True)
            return

        view = BlackjackView(user_id, 금액, interaction.guild.id)
        embed = view.make_playing_embed()

        await interaction.response.send_message(embed=embed, view=view)