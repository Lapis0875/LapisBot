import logging
import sys

import discord
from discord.ext import commands
from discord.utils import get, find

# 로거 설정
logging.getLogger("discord.gateway").setLevel(logging.WARNING)
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'))
logger.addHandler(handler)

# 봇 설정
token: str = ''
desc = '서버 관리 기능을 제공하는 디스코드 봇입니다.'
bot = commands.Bot(command_prefix='!', description=desc)

# 역할 설정 관련 변수들
roles_dict: dict = {}
emojis: dict

global token, roles_dict, server_config_dict


@bot.event
async def on_ready():
    print('봇이 다음 옵션으로 실행되었습니다. : ')
    print(f'command_prefix : {bot.command_prefix}')
    global emojis
    emojis = {x.name: x for x in bot.emojis}
    print(f'emojis = {emojis}')

    # 봇이 플레이중인 게임을 설정할 수 있습니다.
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(name="Coders' Community Management", type=1))

    # await bot.get_channel(655675096903712778).send("서버관리 봇이 실행되었습니다! :sunny:")


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
async def on_raw_reaction_add(payload):
    msg_id = payload.message_id
    print(f'{payload.user_id} 님이 {msg_id}에 {payload.emoji.name} 반응을 남겼습니다.')
    print(f'role_setting_msg_id = {role_setting_msg_id}')

    # 역할설정 메세지에서 일어난 이벤트라면
    if msg_id == role_setting_msg_id:
        print(f'{payload.user_id} 님이 역할을 신청했습니다.')
        guild_id = payload.guild_id
        guild = find(lambda g: g.id == guild_id, bot.guilds)
        role = get(guild.roles, name=roles_dict['lang'][payload.emoji.name])
        if role is not None:
            member = find(lambda m: m.id == payload.user_id, guild.members)
            if member is not None:
                await member.add_roles(role, reason='Auto role assignment using bot.', atomic=True)
            else:
                logger.error('member not found')
        else:
            logger.error('role not found')
    else:
        logger.debug(f'{payload.emoji.name} is used at {msg_id}')


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
async def on_raw_reaction_remove(payload):
    msg_id = payload.message_id
    print(f'{payload.user_id} 님이 {msg_id}에 {payload.emoji.name} 반응을 남겼습니다.')
    print(f'role_setting_msg_id = {role_setting_msg_id}')

    # 역할설정 메세지에서 일어난 이벤트라면
    if msg_id == role_setting_msg_id:
        print(f'{payload.user_id} 님이 역할을 제거했습니다.')
        guild_id = payload.guild_id
        guild = find(lambda g: g.id == guild_id, bot.guilds)
        role = get(guild.roles, name=roles_dict['lang'][payload.emoji.name])
        if role is not None:
            member = find(lambda m: m.id == payload.user_id, guild.members)
            if member is not None:
                await member.remove_roles(role, reason='Auto role assignment using bot.', atomic=True)
            else:
                logger.error('member not found')
        else:
            logger.error('role not found')
    else:
        logger.debug(f'{payload.emoji.name} is used at {msg_id}')


'''
on_message(message):
    ...

디스코드 채널에 메세지가 올라왔을 때 실행되는 이벤트입니다.
bot.process_commands(message)
위 구문 없이 on_message를 사용할 경우, 메세지가 이 이벤트에서만 처리되고 명령어가 실행되지 않습니다.
이 구문은 전달받은 메세지를 명령어들에게 전달해 명령어도 실행되도록 합니다.
'''


@bot.event
async def on_message(message):
    print(f'print() : {message.author} used {message.content} in {message.channel}')
    print(f'{message.author} used {message.content} in {message.channel}')
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, e):
    if isinstance(e, commands.errors.CheckFailure):
        return


'''
[ 모듈 - 서버 설정 ] (모듈화 필요)
설정 커맨드와 여러 서브커맨드들이 모여있는 모듈입니다.
서버 관리 기능을 제공합니다.

@commands.is_owner() : 관리자 이상만 쓸 수 있는 명령어 (서버 소유자인가요? 봇 소유자?)

setting() : 설정
ㄴ set_role() : 역할 지급 채널 설정 커맨드.

사용법 : !설정 (커맨드 이름)

명령어 제작법 :
@setting.command(name='명령어 이름')
async def (함수명)(ctx, 필요한 추가 인자):
    ...

'''


@commands.is_owner()
@bot.group(name="설정", invoke_without_command=True)
async def setting(ctx):
    await ctx.send('!설정 역할지급 혹은 !설정 역할지급_테스트를 사용해 주세요.')

"""
@commands.is_owner()
@setting.command(name="역할지급")
async def set_role(ctx):
    global roles_dict, role_setting_msg_id
    # logger.debug('set_role 진입')
    print(f'{ctx.author} 님이 {ctx.message.channel}에서 {ctx.prefix}{ctx.command} 을(를) 사용했습니다.')
    msg = await ctx.send('현재 사용 가능한 역할들입니다!')
    print(f'msg.id = {msg.id}')
    role_setting_msg_id = msg.id
    for emoji in roles_dict['lang'].keys():
        await msg.add_reaction(emojis[emoji])
    print('채널 설정 완료. 생성된 메세지의 id를 저장합니다.')

    config = open(mode='wt', file='config.txt')
    config.write(f'role_setting_msg_id={str(msg.id)}')
    config.close()
"""

@commands.is_owner()
@setting.command(name="역할지급_테스트")
async def set_role_test(ctx):
    global roles_dict, role_setting_msg_id
    
    print(f'[ 테스트 커맨드 ] {ctx.author} 님이 {ctx.message.channel}에서 {ctx.prefix}{ctx.command} 을(를) 사용했습니다.')
    await ctx.send('현재 사용 가능한 역할들입니다!')
    # role_setting_msg_id = msg.id
    content = '**게임 역할**\n'
    msg = await ctx.send(content)
    for emoji in roles_dict['game'].keys():
        content += f'<:{emojis[emoji].name}:{emojis[emoji].id}> : {roles_dict[emoji]}\n'
        print(f'content = {content}')
        await msg.edit(content=content, supress=False)
        await msg.add_reaction(emojis[emoji])
    msg.edit('**기능**')
    for emoji in roles_dict['features'].keys():
        await msg.add_reaction(emojis[emoji])
    print('채널 설정 완료. 생성된 메세지의 id를 저장합니다.')


'''
[ 봇 전후처리 로직 ]

< init() >
봇 실행 전 config.txt, 덕들의방_config.json 파일에서 필요한 데이터를 읽어와 저장합니다.
또, 모듈의 초기화도 담당합니다. (config.py 존재할 경우에만)
token 값은 config.py 존재시 해당 파일에서 가져오며, 그렇지 않을 경우 콘솔에서 직접 입력받습니다.

< save_datas() >
봇 종료 후 가지고 있던 role_setting_msg_id 변수의 값을 config.txt에 저장합니다.
'''


def init():
    global token, role_setting_msg_id, roles_dict
    try:
        print('config.txt를 불러옵니다.')
        config = open(mode='rt', file='config.txt', encoding='UTF8')
    except FileNotFoundError as error:
        print(f'config.txt 가 존재하지 않습니다! 설정이 필요합니다.')
        token = input('discord application의 bot token을 입력해 주세요! : ')
        # mode = x(create a new file as writing mode)t(text mode)
        config = open(mode='xt', file='config.txt', encoding='UTF8')
        config.write(f'token={token}\nrole_setting_msg_id=')
    else:
        # config.txt 파일 불러오기
        print('config.txt 를 성공적으로 불러왔습니다.')
        print(f'token = {str(token)}')
        config.close()

    # 서버별 설정파일 불러오기
    import os # 폴더 내 파일 불러오기 위해 os 모듈 임포트
    try:
        path = "./server_setting"     # 현재 디렉토리
        server_config_list = [file for file in os.listdir(path) if file.endswith(".py")]
        print(f'server_config_list: {server_config_list}')

    except FileNotFoundError as e:
        print(e)
    else:
        import json
        global server_config_dict
        for file in server_config_list:
            config = json.loads(open(file=file, mode='rt').read())
        # 덕들의방_config.json 불러오기
        rl = open(mode='rt', file='server_setting/덕들의방_config.json', encoding='UTF8')
        import json
        roles_dict = json.loads(rl.read())['roles_dict']
        rl.close()
        print(f'roles_dict = {roles_dict}')
        print(f'roles_dict["lang"] = {roles_dict["lang"]}')
        print(f'list(roles_dict["lang"].keys()) = {list(roles_dict["lang"].keys())}')


def save_datas():
    global token, role_setting_msg_id
    config = open(mode='wt', file='config.txt')
    config.write(f'token={token}, \nrole_setting_msg_id={str(role_setting_msg_id)}')
    config.close()


'''
[ 프로그램 로직 ]

봇 실행 전 초기화 작업
< init() >
-> 봇 실행
< bot.run(token) >
-> 봇 종료 후 데이터 저장 작업
< save_datas() >
'''

print('init 실행')
init()
# logger.debug(f'token = {token}')
print(f'token = {token}')
bot.run(token)
save_datas()
