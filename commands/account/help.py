import discord


def setup(bot):

    @bot.tree.command(name="도움말", description="카지노 라이프 명령어 목록을 확인합니다.")
    async def help_command(interaction: discord.Interaction):

        embed = discord.Embed(
            title="🎰 카지노 라이프 도움말",
            description=(
                "돈을 벌고, 도박하고, 투자하고,\n"
                "나만의 카지노까지 운영하는 디스코드 경제 게임입니다."
            ),
            color=0xF1C40F
        )

        embed.add_field(
            name="👤 기본",
            value=(
                "`/등록` - 계정 생성\n"
                "`/프로필` - 내 정보 확인\n"
                "`/잔액` - 보유 현금 확인\n"
                "`/가이드` - 초보자 진행 순서\n"
                "`/도움말` - 명령어 목록\n"
                "`/핑` - 봇 상태 확인"
            ),
            inline=False
        )

        embed.add_field(
            name="💵 돈벌기",
            value=(
                "`/출석` - 출석 보상 받기\n"
                "`/알바` - 기본 돈벌기\n"
                "`/배달` - 배달 보상 획득\n"
                "`/낚시` - 물고기 낚기\n"
                "`/광산` - 광물 채굴\n"
                "`/범죄` - 위험한 한탕"
            ),
            inline=False
        )

        embed.add_field(
            name="🎰 카지노 게임",
            value=(
                "`/슬롯` - 슬롯머신\n"
                "`/홀짝` - 홀짝 도박\n"
                "`/블랙잭` - 카드 게임\n"
                "`/바카라` - 바카라 게임\n"
                "`/잭팟` - 현재 잭팟 확인"
            ),
            inline=False
        )

        embed.add_field(
            name="🏛 카지노 소유",
            value=(
                "`/카지노구매` - 서버 카지노 구매\n"
                "`/카지노정보` - 카지노 정보 확인\n"
                "`/카지노수익` - 카지노 금고 수익 출금\n"
                "`/카지노털기` - 다른 카지노 금고 털기"
            ),
            inline=False
        )

        embed.add_field(
            name="🏦 은행 / VIP",
            value=(
                "`/은행` - 은행 정보 확인\n"
                "`/입금` - 현금 입금\n"
                "`/출금` - 은행 돈 출금\n"
                "`/대출` - 대출 받기\n"
                "`/상환` - 대출 상환\n"
                "`/vip` - VIP 혜택 확인"
            ),
            inline=False
        )

        embed.add_field(
            name="📈 투자 / 복권",
            value=(
                "`/주식목록` - 주식 목록 확인\n"
                "`/주식매수` - 주식 구매\n"
                "`/주식매도` - 주식 판매\n"
                "`/내주식` - 내 주식 확인\n"
                "`/로또구매` - 로또 구매\n"
                "`/로또확인` - 로또 결과 확인"
            ),
            inline=False
        )

        embed.add_field(
            name="⚔ PvP / 거래",
            value=(
                "`/코인플립` - 유저끼리 코인플립\n"
                "`/주사위` - 유저끼리 주사위 대결\n"
                "`/송금` - 다른 유저에게 송금"
            ),
            inline=False
        )

        embed.add_field(
            name="🚔 감옥 / 랭킹",
            value=(
                "`/탈옥` - 감옥에서 탈출 시도\n"
                "`/랭킹` - 서버 랭킹 확인"
            ),
            inline=False
        )

        embed.add_field(
            name="⚙ 서버 설정",
            value=(
                "`/채널설정` - 봇 사용 채널 설정\n"
                "`/채널확인` - 현재 설정 채널 확인"
            ),
            inline=False
        )

        embed.set_thumbnail(
            url=interaction.guild.icon.url
            if interaction.guild and interaction.guild.icon
            else None
        )

        embed.set_footer(
            text="🎰 처음이라면 /가이드 를 먼저 확인하세요."
        )

        await interaction.response.send_message(embed=embed)