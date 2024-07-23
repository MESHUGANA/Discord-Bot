import discord
# from discord import app_commands
# from discord.ext import commands

from datetime import datetime, timedelta

import os
from dotenv import load_dotenv

import asyncio
from lib import *

# 퀴즈 데이터 가져오기
PATH_RES = './res/'
txt_file_list = get_txt_file_list(PATH_RES)

# # 퀴즈 데이터 가공하여 초성 데이터 생성
quiz_data = make_quiz_data(txt_file_list)
active_quiz_data = {
    'subject': '모두',
    'data': sum([quiz['data'] for quiz in quiz_data], [])
}
# active_subject = [1] * len(txt_file_list)
active_quiz = None

last_message_id = None


######## 디스코드 #########

load_dotenv()
TOKEN = str(os.getenv('TOKEN'))
SERVER_ID = int(os.getenv('SERVER_ID'))
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

bot = discord.Bot()


@bot.event
async def on_ready():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f'{bot.user.name} is now online!')
    print(f'{bot.user.display_name} 온라인')

@bot.slash_command(name='도움말', description='각종 도움말을 보여줍니다.')
async def embed(ctx):
    # 임베드를 생성합니다
    user = ctx.user
    embed = discord.Embed(
        title='도움말',
        description='사용 방법 등',
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )
    embed.add_field(name='기본', value='사용방법', inline=False)
    embed.add_field(name='명령어', value='명령어 설명입니당', inline=True)
    embed.add_field(name='명령어2', value='명령어 설명입니당', inline=True)

    embed.set_footer(text=f'{user.name}', icon_url=user.avatar.url)
    embed.set_thumbnail(url=user.avatar.url)

    # 임베드 메시지를 보냅니다
    await ctx.respond(embed=embed, ephemeral=True)

class SelectView(discord.ui.View):
    @discord.ui.select(
        placeholder = '초성 퀴즈 주제 선택',
        min_values = 1,
        # max_values = 3,
        options = [
            discord.SelectOption(
                label=txt_file['name'],
                value=str(i)
                # description=''
            ) for i, txt_file in enumerate(txt_file_list)
        ]
    )
    async def select_callback(self, select, interaction):
        global last_message_id
        
        if last_message_id is not None:
            # 저장된 메시지 ID로 메시지를 가져오기
            channel = interaction.channel
            message = await channel.fetch_message(last_message_id)
            embed = message.embeds[0]

            embed.color = discord.Color.red()
            last_message_id = None
            
            # 임베드 및 버튼 상태 수정
            await message.edit(embed=embed, view=None)

        selected_value = int(select.values[0])
        selected_subject = txt_file_list[selected_value]['name']
        await interaction.response.send_message(f'초성 퀴즈 주제를 **{selected_subject}**{'' if end_with_vowel(selected_subject) else '으'}로 변경합니다!')

        active_quiz_data['subject'] = selected_subject
        active_quiz_data['data'] = quiz_data[selected_value]['data']


@bot.slash_command(name='주제', description='초성 퀴즈 주제를 변경합니다.')
async def quiz(ctx):
    await ctx.respond(f'현재 초성 퀴즈 주제는 **{active_quiz_data['subject']}**입니다.\n변경하려면 아래 목록에서 선택하세요.', view=SelectView())
    
@bot.slash_command(name='핑', description='봇의 핑을 ms 단위로 출력합니다.')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.respond(f'🏓 퐁! {latency}ms')

@bot.slash_command(name='답', description='답을 입력합니다.')
async def submit_answer(ctx, ans: discord.Option(str, name_localizations={'ko': '정답'})):
    global last_message_id

    if last_message_id is None:
        await ctx.respond('먼저 문제를 출제하세요.')
        return
    
    elif ans == active_quiz['ans']:
        # 저장된 메시지 ID로 메시지를 가져오기
        channel = ctx.channel
        message = await channel.fetch_message(last_message_id)
        embed = message.embeds[0]

        embed = discord.Embed(
            title=active_quiz['ans'],
            description=f'{active_quiz['subject']}',
            color=discord.Color.green()
        )

        last_message_id = None

        # 버튼 비활성화
        # view = MyView0()
        # view.disable_all_items()

        # 임베드 및 버튼 상태 수정
        await message.edit(embed=embed, view=None)

        await ctx.respond(f'{ctx.user.display_name}님 정답입니다!')
        
    else:
        await ctx.respond(f'**{ans}**: {ctx.user.display_name}님 틀렸습니다!')

class MyView0(discord.ui.View):
    @discord.ui.button(label='힌트', style=discord.ButtonStyle.secondary, emoji='🪄', custom_id='hint_btn')
    async def button3_callback(self, button, interaction):
        global active_quiz
        if len(active_quiz['hint']):
            active_quiz = get_hint(active_quiz)

            embed = discord.Embed(
                title=active_quiz['chs'],
                description=f'{active_quiz['subject']}',
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=self)
            # await interaction.followup.send('버튼을 눌러 힌트를 사용했습니다.', ephemeral=True)
        else:
            await interaction.response.send_message('더 이상 힌트를 사용할 수 없습니다. `/답공개`를 사용해 주세요!', ephemeral=True)

    @discord.ui.button(label='답공개', style=discord.ButtonStyle.red, emoji='🔎', custom_id='ans_btn')
    async def button2_callback(self, button, interaction):
        global last_message_id

        embed = discord.Embed(
            title=active_quiz['ans'],
            description=f'{active_quiz['subject']}',
            color=discord.Color.red()
        )

        last_message_id = None

        # 버튼을 비활성화하고 메시지 수정
        # self.disable_all_items()

        await interaction.response.edit_message(embed=embed, view=None)
        await interaction.followup.send('빛나라 지식의 별! ⭐٩(`･ω･´)و💫')
        # await interaction.followup.send('버튼을 눌러 답공개를 사용했습니다.', ephemeral=True)

@bot.slash_command(name='문제', description='봇이 문제를 냅니다.')
async def send_problem(ctx):
    global last_message_id
    global active_quiz

    if last_message_id is None:
        # 문제 뽑기
        active_quiz = get_quiz(active_quiz_data)
        # 문제 임베드 생성
        embed = discord.Embed(
            title=f'{active_quiz['chs']}',
            description=f'[{active_quiz['subject']}]',
            color=discord.Color.blue()
            # timestamp=datetime.now()
        )
        # embed.set_footer(text=f'{user.name}', icon_url=user.avatar.url)
        await ctx.respond(embed=embed, view=MyView0())
        
        # 메시지 객체를 가져와 ID 저장
        response = await ctx.interaction.original_response()
        last_message_id = response.id
        
    else:
        await ctx.respond(f'{ctx.user.display_name}님 이 문제부터 맞혀주세요', ephemeral=True)

@bot.slash_command(name='힌트', description='힌트를 제공합니다.')
async def send_hint(ctx):
    global last_message_id
    global active_quiz

    if last_message_id is None:
        await ctx.respond('먼저 문제를 출제하세요.')
        return

    # 저장된 메시지 ID로 메시지를 가져오기
    channel = ctx.channel
    message = await channel.fetch_message(last_message_id)
    embed = message.embeds[0]
    
    if len(active_quiz['hint']):
        active_quiz = get_hint(active_quiz)
        
        # 수정
        embed.title = active_quiz['chs']
        embed.color = discord.Color.green()
        await message.edit(embed=embed)

        await ctx.respond('힌트 처리중...', ephemeral=True, delete_after=0)
        
    else:
        await ctx.respond('더 이상 힌트를 사용할 수 없습니다. `/답공개`를 사용해 주세요!', ephemeral=True)

@bot.slash_command(name='답공개', description='답을 공개합니다.')
async def open_quiz(ctx):
    global last_message_id

    if last_message_id is None:
        await ctx.respond('먼저 문제를 출제하세요.')
        return

    # 저장된 메시지 ID로 메시지를 가져오기
    channel = ctx.channel
    message = await channel.fetch_message(last_message_id)
    embed = message.embeds[0]

    embed.title = active_quiz['ans']
    embed.color = discord.Color.red()

    last_message_id = None

    # 버튼 비활성화
    # view = MyView0()
    # view.disable_all_items()
    
    # 임베드 및 버튼 상태 수정
    await message.edit(embed=embed, view=None)
    await ctx.respond('빛나라 지식의 별! ⭐٩(`･ω･´)و💫')
    # await ctx.respond('답공개 처리중...', ephemeral=True, delete_after=0)

###### 앱 명령 #######

@bot.user_command(name='계정 생성일')
async def account_creation_date(ctx, member: discord.Member):
    await ctx.respond(f"{member.display_name}님의 계정 생성일은 {member.created_at}입니다!")

@bot.user_command(name='합류일')
async def account_creation_date(ctx, member: discord.Member):
    await ctx.respond(f"{member.display_name}님의 합류일은 {member.joined_at}입니다!")

# 봇 실행
bot.run(TOKEN)