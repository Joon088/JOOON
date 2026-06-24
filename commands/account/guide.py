import discord


def setup(bot):

    @bot.tree.command(name="가이드", description="카지노 라이프 초보자 가이드를 확인합니다.")
    async def guide(interaction: discord.Interaction):

        embed = discord.Embed(
            title="📖 카지노 라이프 가이드",
            description=(
                "처음 시작하는 유저를 위한 성장 루트입니다.\n"
                "칩을 벌고, 도박하고, 투자하고, 최종적으로 카지노를 운영해보세요."
            ),
            color=0x3498DB
        )

        embed.add_field(
            name="1️⃣ 계정 만들기",
            value=(
                "`/등록`\n"
                "카지노 라이프 계정을 생성합니다.\n"
                "가입 시 **50,000칩**을 받을 수 있습니다."
            ),
            inline=False
        )

        embed.add_field(
            name="2️⃣ 기본 자금 모으기",
            value=(
                "`/출석` - 매일 보상 받기\n"
                "`/알바` - 안정적인 기본 수입\n"
                "`/배달` - 추가 수입 획득\n"
                "`/낚시` - 물고기로 돈 벌기\n"
                "`/광산` - 광물 채굴\n"
                "`/범죄` - 높은 보상, 높은 위험"
            ),
            inline=False
        )

        embed.add_field(
            name="3️⃣ 돈 안전하게 보관하기",
            value=(
                "`/은행` - 은행 정보 확인\n"
                "`/입금` - 현금을 은행에 보관\n"
                "`/출금` - 은행 돈을 현금으로 출금\n\n"
                "큰돈을 들고 다니기보다 은행에 보관하는 것이 안전합니다."
            ),
            inline=False
        )

        embed.add_field(
            name="4️⃣ 카지노 게임 즐기기",
            value=(
                "`/홀짝` - 가장 간단한 도박\n"
                "`/슬롯` - 슬롯머신 도전\n"
                "`/블랙잭` - 전략형 카드 게임\n"
                "`/바카라` - 승부 예측 게임\n"
                "`/잭팟` - 누적 잭팟 확인"
            ),
            inline=False
        )

        embed.add_field(
            name="5️⃣ 로또와 PvP 도전",
            value=(
                "`/로또구매` - 로또 구매\n"
                "`/로또확인` - 로또 결과 확인\n\n"
                "`/코인플립` - 유저와 1대1 승부\n"
                "`/주사위` - 주사위 PvP 대결"
            ),
            inline=False
        )

        embed.add_field(
            name="6️⃣ 투자로 자산 늘리기",
            value=(
                "`/주식목록` - 주식 목록 확인\n"
                "`/주식매수` - 주식 구매\n"
                "`/주식매도` - 주식 판매\n"
                "`/내주식` - 보유 주식 확인\n\n"
                "도박만 하지 말고 투자로 자산을 키워보세요."
            ),
            inline=False
        )

        embed.add_field(
            name="7️⃣ 대출과 VIP 활용",
            value=(
                "`/대출` - 부족한 자금 대출\n"
                "`/상환` - 대출금 상환\n"
                "`/vip` - VIP 등급과 혜택 확인\n\n"
                "VIP 등급이 높을수록 더 좋은 혜택을 받을 수 있습니다."
            ),
            inline=False
        )

        embed.add_field(
            name="8️⃣ 나만의 카지노 운영하기",
            value=(
                "`/카지노구매` - 서버 카지노 구매\n"
                "`/카지노정보` - 카지노 상태 확인\n"
                "`/카지노수익` - 카지노 금고 수익 출금\n\n"
                "카지노를 소유하면 카지노 게임에서 특별한 혜택을 받을 수 있습니다."
            ),
            inline=False
        )

        embed.add_field(
            name="9️⃣ 카지노 털기",
            value=(
                "`/카지노털기`\n"
                "다른 카지노의 금고를 털어 큰돈을 노릴 수 있습니다.\n\n"
                "성공하면 금고 일부를 훔치지만,\n"
                "실패하면 감옥에 갈 수 있습니다."
            ),
            inline=False
        )

        embed.add_field(
            name="🚔 감옥 시스템",
            value=(
                "`/탈옥`\n"
                "범죄나 카지노 털기에 실패하면 구금될 수 있습니다.\n"
                "구금 중에는 대부분의 활동이 제한됩니다."
            ),
            inline=False
        )

        embed.add_field(
            name="🚀 추천 성장 루트",
            value=(
                "등록 → 출석 / 알바 / 배달\n"
                "⬇️\n"
                "은행에 돈 보관\n"
                "⬇️\n"
                "홀짝 / 슬롯으로 소액 도전\n"
                "⬇️\n"
                "주식 투자와 로또 참여\n"
                "⬇️\n"
                "VIP 등급 올리기\n"
                "⬇️\n"
                "카지노 구매 후 수익 운영"
            ),
            inline=False
        )

        embed.add_field(
            name="⚠️ 주의사항",
            value=(
                "도박은 큰돈을 벌 수도 있지만 잃을 수도 있습니다.\n"
                "범죄와 카지노 털기는 실패 시 감옥에 갈 수 있습니다.\n"
                "대출은 반드시 상환 계획을 세우고 이용하세요."
            ),
            inline=False
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        embed.set_footer(
            text="🎰 Casino Life • 부자가 되는 길은 하나가 아닙니다."
        )

        await interaction.response.send_message(embed=embed)