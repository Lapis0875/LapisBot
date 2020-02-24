import asyncio
import sys

import discord
from discord.ext import commands
from discord.utils import get, find # 역할 지급시 해당하는 역할을 찾기 위해 사용

# 봇 설정 변수들
token: str = ''
desc = '서버 관리 기능을 제공하는 디스코드 봇입니다.'
bot = commands.Bot(command_prefix='!', description=desc)

# 역할 설정 관련 변수들
server_config_dict: dict = {}
emojis: dict = {}
# server_config_dict 은 "bot_notice_channel": (id), "roles_dict"을 포함합니다.


def init():
    global token, server_config_dict
    """
    봇의 기본 설정파일인 config.txt를 불러옵니다.
    """
    bot_config_file = None

    try:
        print('[init] > config.txt를 불러옵니다.')
        bot_config_file = open(mode='rt', file='config.txt', encoding='UTF8')
    except FileNotFoundError:
        print('[init] > config.txt 가 존재하지 않습니다! 설정이 필요합니다.')
        bot_config_file.close()
        token = input('[init] > discord application의 bot token을 입력해 주세요! : ')
        # mode = x(create a new file as writing mode)t(text mode)
        bot_config_file = open(mode='xt', file='config.txt', encoding='UTF8')
        bot_config_file.write(f'token={token}')
        bot_config_file.close()
    else:
        # config.txt 파일 불러오기
        print('[init] > config.txt 를 성공적으로 불러왔습니다.')
        token = bot_config_file.read().replace('token=', '')
        print(f'[init] > token = {str(token)}')
        bot_config_file.close()

    """
    서버별 설정파일을 불러옵니다.
    서버별 설정파일은 ./server_setting에 저장되어 있으며, 해당 경로에 존재하는 모든 파일들은 (서버명)덕들의방_config.json 의 이름을 가집니다.
    """
    import os # 폴더 내 파일 불러오기 위해 os 모듈 임포트

    print('[init] > 서버별 설정파일을 불러옵니다.')
    path = "./server_setting"     # 현재 디렉토리
    config_file_list = [file for file in os.listdir(path) if file.endswith(".json")]
    print(f'[init] > server_config_list: {config_file_list}')
    for file in config_file_list:
        server_config_file = None
        try:
            import json
            server_config_file = open(file=f'./server_setting/{file}', mode='rt', encoding='UTF8')
            config = json.loads(server_config_file.read())
            server_config_dict[config['guild_name']] = config
            server_config_file.close()
        except FileNotFoundError as e:
            print('[init] > 파일을 열지 못했습니다!')
            print(f'[init] > {e.with_traceback()}')
            server_config_file.close()
        except Exception as e:
            print('[init] > 오류가 발생했습니다!')
            print(f'[init] > {e.with_traceback()}')
            server_config_file.close()
            
        print(f'server_config_dict = {server_config_dict}')


def save_datas():
    global token, server_config_dict

    bot_config_file = None
    # 봇 설정파일 저장
    try:
        bot_config_file = open(mode='wt', file='config.txt', encoding='UTF8')
        bot_config_file.write(f'token={token}')
        bot_config_file.close()
    except Exception as e:
        print('[save_datas] > 오류가 발생했습니다!')
        print(f'[save_datas] > {e.with_traceback()}')
        bot_config_file.close()
        
    # 서버별 설정파일 저장
    import json
    server_config_file = None
    for server_config_dict in server_config_dict.items:
        try:
            server_config_file = open(file=f'./server_setting/{server_config_dict["guild_name"]}_config.json', mode='wt', encoding='UTF8')
            server_config_file.write(json.dumps(server_config_dict))
            server_config_file.close()
        except Exception as e:
            print('[save_datas] > 오류가 발생했습니다!')
            print(f'[save_datas] > {e.with_traceback()}')
            server_config_file.close()



@bot.event
async def on_ready():
    global emojis
    print('봇이 다음 옵션으로 실행되었습니다. : ')
    print(f'command_prefix : {bot.command_prefix}')

    print('현재 봇이 소속된 서버 목록입니다 : ')
    print(f'guilds: {bot.guilds}')

    # 역할 설정시 사용할 이모지 명단 받아오기
    # 디코봇이 소속된 모든 서버에서 이모지를 받아온다.
    emojis = {x.name: x for x in bot.emojis}
    print(f'emojis = {emojis}')

    # 봇이 플레이중인 게임을 설정할 수 있습니다.
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(name="라피스봇이에요~", type=1))

    for guild in bot.guilds:
        await bot.get_channel(server_config_dict[guild.name]['bot_notice_ch_id']).send("서버관리 봇이 실행되었습니다! :sunny:")

    '''
    on_raw_reaction_add(payload):
        ...

    봇에 캐싱되지 않은 메세지에 반응이 추가되었을 때 실행되는 이벤트입니다.
    paylod는 discord.RawReactionActionEvent class로, 자세한 설명은

    on_raw_reaction_add() 이벤트 설명 : https://discordpy.readthedocs.io/en/latest/api.html#event-reference
    payload 설명 : https://discordpy.readthedocs.io/en/latest/api.html#discord.RawReactionActionEvent

    에서 확인하실 수 있습니다.
    '''

    @bot.event
    async def on_guild_join(guild: discord.Guild):
        with open(f'./server_setting/{guild.name}_config.json', 'xt') as config_file:
            global server_config_dict
            config_dict = {'guild_id': guild.id, 'guild_name': guild.name, 'bot_notice_ch_id': 0, 'role_setting_msg_id': 0, 'roles_dict': {}}
            server_config_dict[guild.name] = config_dict

    @bot.event
    async def on_guild_remove(guild: discord.Guild):
        with open(f'./server_setting/{guild.name}_config.json', 'xt') as config_file:
            global server_config_dict
            server_config_dict.pop(guild.name)



    @bot.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
        # payload에서 필요한 정보를 저장한다.
        msg_id: int = payload.message_id    # 반응 추가 이벤트가 발생한 메세지 id
        guild_id: int = payload.guild_id    # 반응 추가 이벤트가 발생한 길드 id
        user_id: int = payload.user_id    # 반응 추가 이벤트를 발생시킨 유저 id

        guild = find(lambda g: g.id == guild_id, bot.guilds)        # 반응 추가 이벤트가 발생한 길드
        role_setting_msg_id = server_config_dict[guild.name]['role_setting_msg_id'] # 이벤트가 발생한 길드의 역할설정 이벤트 메세지 id

        # 서버별로 roles_dict 내부 카테고리가 다를것을 상정하고, 루프를 돌며 이모지 명칭을 찾는다.
        emoji_name: str = payload.emoji.name
        selected_emoji_category: str = ''   # roles_dict의 카테고리 분류 저장

        # 자동 역할설정 기능 관련 변수들
        role_setting_msg_id: int = 0  # 이 이벤트가 발생한 길드의 역할 설정 메세지 id를 저장한다.

        print(f'[bot_event] (on_raw_reaction_remove) > {user_id} 님이 {guild_id} 서버의 {msg_id} 메세지에서 {emoji_name} 반응을 제거했습니다.')


        if msg_id == role_setting_msg_id:
            print(f'[bot_event] (on_raw_reaction_add) > {user_id} 님이 역할을 신청했습니다.')

            roles_dict = server_config_dict[guild.name]['roles_dict']
            for category in roles_dict.keys():
                for role_emoji_name in roles_dict[category].keys():
                    if role_emoji_name == emoji_name:
                        selected_emoji_category = category
                        break

            role = get(guild.roles, name=server_config_dict[guild.name]['roles_dict'][selected_emoji_category][emoji_name])
            if role is not None:
                member: discord.Member = find(lambda m: m.id == user_id, guild.members)
                if member is not None:
                    await member.add_roles(role, reason='Auto role assignment using bot.', atomic=True)
                else:
                    print('[bot_event] (on_raw_reaction_add) > member not found')
            else:
                print('[bot_event] (on_raw_reaction_add) > role not found')
        else:
            print(f'[bot_event] (on_raw_reaction_add) > {emoji_name} is used at {msg_id}')

    '''
    on_raw_reaction_remove(payload):
        ...

    봇에 캐싱되지 않은 메세지에 반응이 제거되었을 때 실행되는 이벤트입니다.
    paylod는 discord.RawReactionActionEvent class로, 자세한 설명은

    on_raw_reaction_add() 이벤트 설명 : https://discordpy.readthedocs.io/en/latest/api.html#event-reference
    payload 설명 : https://discordpy.readthedocs.io/en/latest/api.html#discord.RawReactionActionEvent

    에서 확인하실 수 있습니다.
    '''

    @bot.event
    async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
        # payload에서 필요한 정보를 저장한다.
        msg_id: int = payload.message_id  # 반응 추가 이벤트가 발생한 메세지 id
        guild_id: int = payload.guild_id  # 반응 추가 이벤트가 발생한 길드 id
        user_id: int = payload.user_id    # 반응 추가 이벤트를 발생시킨 유저 id

        guild = find(lambda g: g.id == guild_id, bot.guilds)        # 반응 추가 이벤트가 발생한 길드
        role_setting_msg_id = server_config_dict[guild.name]['role_setting_msg_id'] # 이벤트가 발생한 길드의 역할설정 이벤트 메세지 id

        # 서버별로 roles_dict 내부 카테고리가 다를것을 상정하고, 루프를 돌며 이모지 명칭을 찾는다.
        emoji_name: str = payload.emoji.name
        selected_emoji_category: str = ''  # roles_dict의 카테고리 분류 저장

        # 자동 역할설정 기능 관련 변수들
        role_setting_msg_id: int = 0  # 이 이벤트가 발생한 길드의 역할 설정 메세지 id를 저장한다.

        print(f'[bot_event] (on_raw_reaction_remove) > {user_id} 님이 {guild_id} 서버의 {msg_id} 메세지에서 {emoji_name} 반응을 제거했습니다.')

        # 역할설정 메세지에서 일어난 이벤트인지 확인하기 위해 이벤트가 발생한 길드의 역할설정 이벤트 메세지 id를 확인한다.
        # server_config_dict 에 저장된 각 서버별 dictionary를 server_config에 순차적으로 저장
        for server_config in server_config_dict.items():
            # server_config의 guild_id 키에 대한 값이 payload.guild_id와 같다면, 해당 길드에서 일어난 이벤트임을 확인하고 해당 길드의 역할설정 메세지 id를 가져온다.
            if server_config['guild_id'] == guild_id:
                role_setting_msg_id = server_config['role_setting_msg_id']
                break

        # 역할설정 메세지에서 일어난 이벤트라면
        if msg_id == role_setting_msg_id:
            print(f'[bot_event] (on_raw_reaction_remove) > {user_id} 님이 역할을 제거했습니다.')

            roles_dict = server_config_dict[guild.name]['roles_dict']
            for category in roles_dict.keys():
                for role_emoji_name in roles_dict[category].keys():
                    if role_emoji_name == emoji_name:
                        selected_emoji_category = category
                        break

            role = get(guild.roles, name=server_config_dict[guild.name]['roles_dict'][selected_emoji_category][payload.emoji.name])

            if role is not None:
                member: discord.Member = find(lambda m: m.id == user_id, guild.members)
                if member is not None:
                    await member.remove_roles(role, reason='Auto role assignment using bot.', atomic=True)
                else:
                    print('[bot_event] (on_raw_reaction_add) > member not found')
            else:
                print('[bot_event] (on_raw_reaction_add) > role not found')
        else:
            print(f'[bot_event] (on_raw_reaction_add) > {emoji_name} is used at {msg_id}')

    '''
    on_message(message):
        ...

    디스코드 채널에 메세지가 올라왔을 때 실행되는 이벤트입니다.
    bot.process_commands(message)
    위 구문 없이 on_message를 사용할 경우, 메세지가 이 이벤트에서만 처리되고 명령어가 실행되지 않습니다.
    이 구문은 전달받은 메세지를 명령어들에게 전달해 명령어도 실행되도록 합니다.
    '''

    @bot.event
    async def on_message(message: discord.Message):
        print(f'print() : {message.author} used {message.content} in {message.channel}')
        print(f'{message.author} used {message.content} in {message.channel}')
        await bot.process_commands(message)

    @bot.event
    async def on_command_error(ctx: discord.ext.commands.Context, e: discord.ext.commands.CommandError):
        print(f'[bot-event] (on_command_error) > {e.with_traceback()}')
        if isinstance(e, commands.errors.CheckFailure):
            return

    @commands.is_owner()
    @bot.group(name="설정", invoke_without_command=True)
    async def setting(ctx):
        await ctx.send('!설정 역할지급 혹은 !설정 역할지급_테스트를 사용해 주세요.')


    @commands.is_owner()
    @setting.command(name="역할지급 설정")
    async def autorole(ctx: discord.ext.commands.Context):
        global server_config_dict
        guild: discord.Guild = ctx.guild
        print(f'[역할설정 기능] {ctx.author} 님이 {guild} 서버의 {ctx.message.channel} 채널에서 {ctx.prefix}{ctx.command} 을(를) 사용했습니다.')

        content: str = '역할 자동부여 메세지 : '
        msg = await ctx.send(content=content)

        for category in server_config_dict[guild.name]['roles_dict'].items:
            content += f'**{category}**\n'
            await msg.edit(content=content)
            for emoji in category.keys():
                content += f'<:{emojis[emoji].name}:{emojis[emoji].id}> : {category[emoji]}\n'
                await msg.edit(content=content, supress=False)
                await msg.add_reaction(emojis[emoji])

        print('채널 설정 완료. 생성된 메세지의 id를 저장합니다.')
        server_config_dict[guild.name]['role_setting_msg_id'] = msg.id

init()
print(f'token = {token}')
bot.run(token)
save_datas()