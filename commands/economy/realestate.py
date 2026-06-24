import discord
from discord import app_commands

from db import (
    get_user,
    get_real_estates,
    get_user_properties,
    buy_property,
    sell_property,
    claim_property_income
)

PROPERTY_CHOICES = [
    app_commands.Choice(name="원룸", value="원룸"),
    app_commands.Choice(name="아파트", value="아파트"),
    app_commands.Choice(name="상가", value="상가"),
    app_commands.Choice(name="호텔", value="호텔"),
]


def setup(bot):

    @bot.tree.command(name="부동산목록", description="구매 가능한 부동산 목록을 확인합니다.")
    async def property_list(interaction: discord.Interaction):

        estates = get_real_estates()

        embed = discord.Embed(
            title="🏠 부동산 시장",
            description="종류별로 1개씩만 보유할 수 있습니다.",
            color=0x3498DB
        )

        icons = {
            "원룸": "🏠",
            "아파트": "🏢",
            "상가": "🏬",
            "호텔": "🏨"
        }

        for name, data in estates.items():
            embed.add_field(
                name=f"{icons.get(name, '🏘')} {name}",
                value=(
                    f"💰 구매 **{data['price']:,}칩**\n"
                    f"💸 매매 **{data['sell_price']:,}칩**\n"
                    f"📈 수익 **{data['income_min']:,}~{data['income_max']:,}칩**\n"
                    f"⏰ 12시간"
                ),
                inline=True
            )

        embed.set_footer(text="매매 시 구매가의 80%만 돌려받습니다.")

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="부동산구매", description="부동산을 구매합니다.")
    @app_commands.describe(종류="구매할 부동산")
    @app_commands.choices(종류=PROPERTY_CHOICES)
    async def property_buy(
        interaction: discord.Interaction,
        종류: app_commands.Choice[str]
    ):

        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 해주세요.", ephemeral=True)
            return

        property_name = 종류.value
        estates = get_real_estates()
        data = estates[property_name]

        if property_name in get_user_properties(user_id):
            await interaction.response.send_message(
                "이미 해당 부동산을 보유하고 있습니다.",
                ephemeral=True
            )
            return

        if user["money"] < data["price"]:
            await interaction.response.send_message(
                "보유 칩이 부족합니다.",
                ephemeral=True
            )
            return

        updated_user = buy_property(user_id, property_name)

        embed = discord.Embed(
            title="🏠 부동산 구매 완료",
            description=f"**{property_name}** 을(를) 구매했습니다.",
            color=0x2ECC71
        )

        embed.add_field(name="구매가", value=f"**{data['price']:,}칩**", inline=True)
        embed.add_field(name="매매가", value=f"**{data['sell_price']:,}칩**", inline=True)
        embed.add_field(name="현재 잔액", value=f"**{updated_user['money']:,}칩**", inline=False)

        embed.set_footer(text="부동산 수익은 /부동산수익 으로 12시간마다 받을 수 있습니다.")

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="내부동산", description="내가 보유한 부동산을 확인합니다.")
    async def my_properties(interaction: discord.Interaction):

        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 해주세요.", ephemeral=True)
            return

        properties = get_user_properties(user_id)

        if not properties:
            await interaction.response.send_message(
                "보유 중인 부동산이 없습니다.",
                ephemeral=True
            )
            return

        estates = get_real_estates()

        embed = discord.Embed(
            title="🏘 내 부동산",
            description="현재 보유 중인 부동산입니다.",
            color=0xF1C40F
        )

        icons = {
            "원룸": "🏠",
            "아파트": "🏢",
            "상가": "🏬",
            "호텔": "🏨"
        }

        total_buy = 0
        total_sell = 0

        for property_name in properties:
            data = estates[property_name]
            total_buy += data["price"]
            total_sell += data["sell_price"]

            embed.add_field(
                name=f"{icons.get(property_name, '🏘')} {property_name}",
                value=(
                    f"구매가: **{data['price']:,}칩**\n"
                    f"매매가: **{data['sell_price']:,}칩**\n"
                    f"수익: **{data['income_min']:,}~{data['income_max']:,}칩**"
                ),
                inline=True
            )

        embed.add_field(
            name="📊 총 부동산 가치",
            value=(
                f"구매 기준: **{total_buy:,}칩**\n"
                f"매매 기준: **{total_sell:,}칩**"
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="부동산매매", description="보유한 부동산을 매매합니다.")
    @app_commands.describe(종류="매매할 부동산")
    @app_commands.choices(종류=PROPERTY_CHOICES)
    async def property_sell(
        interaction: discord.Interaction,
        종류: app_commands.Choice[str]
    ):

        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 해주세요.", ephemeral=True)
            return

        property_name = 종류.value
        properties = get_user_properties(user_id)

        if property_name not in properties:
            await interaction.response.send_message(
                "해당 부동산을 보유하고 있지 않습니다.",
                ephemeral=True
            )
            return

        estates = get_real_estates()
        data = estates[property_name]

        sell_price = sell_property(user_id, property_name)
        updated_user = get_user(user_id)

        embed = discord.Embed(
            title="🏚 부동산 매매 완료",
            description=f"**{property_name}** 을(를) 매매했습니다.",
            color=0xE67E22
        )

        embed.add_field(name="기존 구매가", value=f"**{data['price']:,}칩**", inline=True)
        embed.add_field(name="매매 금액", value=f"**+{sell_price:,}칩**", inline=True)
        embed.add_field(name="현재 잔액", value=f"**{updated_user['money']:,}칩**", inline=False)

        embed.set_footer(text="부동산 매매가는 구매가의 80%입니다.")

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="부동산수익", description="보유한 부동산의 수익을 수령합니다.")
    async def property_income(interaction: discord.Interaction):

        user_id = interaction.user.id
        user = get_user(user_id)

        if not user:
            await interaction.response.send_message("먼저 `/등록` 해주세요.", ephemeral=True)
            return

        result = claim_property_income(user_id)

        if result is None:
            await interaction.response.send_message(
                "수익을 받을 부동산이 없습니다.",
                ephemeral=True
            )
            return

        if not result["success"]:
            remaining = result["remaining"]
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60

            await interaction.response.send_message(
                f"아직 부동산 수익을 받을 수 없습니다.\n남은 시간: **{hours}시간 {minutes}분**",
                ephemeral=True
            )
            return

        detail_text = ""

        for property_name, income in result["details"]:
            detail_text += f"{property_name}: **+{income:,}칩**\n"

        embed = discord.Embed(
            title="💰 부동산 수익 수령",
            description="보유 부동산에서 수익이 발생했습니다.",
            color=0x2ECC71
        )

        embed.add_field(name="수익 상세", value=detail_text, inline=False)
        embed.add_field(name="총 수익", value=f"**+{result['income']:,}칩**", inline=True)
        embed.add_field(name="현재 잔액", value=f"**{result['money']:,}칩**", inline=True)

        embed.set_footer(text="부동산 수익은 12시간마다 1회 받을 수 있습니다.")

        await interaction.response.send_message(embed=embed)