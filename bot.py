# -*- coding:utf-8 -*-

import logging
import os
import sys
import traceback

import discord
from discord.ext import commands
from discord.utils import get, find  # 역할 지급시 해당하는 역할을 찾기 위해 사용

# 로깅 설정
logging.getLogger("discord.gateway").setLevel(logging.WARNING)
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'))
logger.addHandler(handler)

# 봇 설정 변수들
token: str = ''
desc = '서버 관리 기능을 제공하는 디스코드 봇입니다.'
bot = commands.Bot(command_prefix='라피스봇 ', description=desc)

do_reboot: bool = False  # 봇 재시작 명령어 체크용 flag

# 알람 종료용 변수
do_waitforsec: bool = False  # 봇 알람 명령어 알람 실행 및 종료용 flag

# 라피스 개발서버 관련 변수들
official_management_servername: str = '라피스 작업실'
developer_ids = [280855156608860160]

# 역할 설정 관련 변수들
server_config_dict: dict = {}
emojis: dict = {}


# server_config_dict 은 "bot_notice_channel": (id), "roles_dict"을 포함합니다.


def init():
    global token, server_config_dict
    """
    봇의 기본 설정파일인 config.txt를 불러옵니다.
    config.txt는 ./ (프로젝트 경로)에 저장되어 있으며, token=(토큰) 의 형식으로 토큰을 저장합니다.
    """

    try:
        print('[init] > config.txt를 불러옵니다.')
        bot_config_file = open(mode='rt', file='config.txt', encoding='utf-8')
    except FileNotFoundError as e:
        print('[init] > config.txt 가 존재하지 않습니다! 설정이 필요합니다.')
        print(f'[init] > Exception Type : {type(e)}')
        print(f'[init] > Exception Value : {e}')
        token = input('[init] > discord application의 bot token을 입력해 주세요! : ')
        # mode = x(create a new file as writing mode)t(text mode)
        bot_config_file = open(mode='xt', file='config.txt', encoding='utf-8')
        bot_config_file.write(f'token={token}')
        bot_config_file.close()
    else:
        # config.txt 파일 불러오기
        print('[init] > config.txt 를 성공적으로 불러왔습니다.')
        token = bot_config_file.read().replace('token=', '')
        if token == '':
            print('[init] > config.txt를 불러왔으나, token이 비어있네요 :(')
            token = input('[init] > discord application의 bot token을 입력해 주세요! : ')
        print(f'token = {token}')
        bot_config_file.close()

    """
    서버별 설정파일을 불러옵니다.
    서버별 설정파일은 ./server_setting/ 에 저장되어 있으며, 해당 경로에 존재하는 모든 파일들은 (서버명)_config.json 의 이름을 가집니다.
    """

    print('[init] > 서버별 설정파일을 불러옵니다.')
    path = "./server_setting"  # 현재 디렉토리
    config_file_list = [file for file in os.listdir(path) if file.endswith(".json")]
    print(f'[init] > server_config_list: {config_file_list}')

    for file in config_file_list:
        if file == 'sample_config.json':  # 설정파일 작성법을 안내하기 위해 만들어진 초기 설정파일은 불러오지 않습니다.
            continue
        print(f'[init] > [{file.replace("_config.json", "")}] 서버의 설정파일을 불러옵니다.')
        try:
            import json
            server_config_file = open(file=f'./server_setting/{file}', mode='rt', encoding='utf-8')
            config = json.loads(server_config_file.read())
            server_config_dict[config['guild_name']] = config
            server_config_file.close()
        except FileNotFoundError as e:
            print(f'[init] > Exception Type : {type(e)}')
            print(f'[init] > Exception Value : {e}')
            print('[init] > 파일을 열지 못했습니다! 파일을 새로 생성합니다.')
            server_config_file = open(file=f'server_setting/{file}', mode='wt', encoding='utf-8')
            server_config_file.write('{}')
            server_config_dict[file.replace('_config.json', '')] = {}
        except Exception as e:
            print('[init] > 오류가 발생했습니다!')
            print(f'[init] > Exception Type : {type(e)}')
            print(f'[init] > Exception Value : {e}')

    print(f'server_config_dict = {server_config_dict}')


def save_datas():
    global token, server_config_dict

    # 봇 설정파일 저장
    print('[save_datas] > config.txt를 저장합니다...')
    try:
        with open(mode='wt', file='config.txt', encoding='utf-8') as bot_config_file:
            print(f'token={token}')
            print(f'bot_config_file = {bot_config_file}')
            bot_config_file.write(f'token={token}')
    except Exception as e:
        print('[save_datas] > 오류가 발생했습니다!')
        traceback.print_exception(etype=type(e), value=e, tb=e.__traceback__)
        return '**config.txt** 파일을 저장하는데 실패했습니다!', e
    else:
        print('[save_datas] > config.txt를 저장했습니다!')

    # 서버별 설정파일 저장
    print('[save_datas] > 서버별 설정파일을 저장합니다...')
    import json
    for server_config in server_config_dict.values():
        print(f'[save_datas] > server_config = {server_config}')
        try:
            with open(file=f'server_setting/{server_config["guild_name"]}_config.json',
                      mode='wt',
                      encoding='utf-8') as server_config_file:
                print(f'server_config_file = {server_config_file}')
                json.dump(obj=server_config, fp=server_config_file, indent=4, ensure_ascii=False)
        except Exception as e:
            print('[save_datas] > 오류가 발생했습니다 :(')
            traceback.print_exception(etype=type(e), value=e, tb=e.__traceback__)
            return f'**{server_config["guild_name"]}** 서버의 설정파일을 저장하는데 실패했습니다!', e
        else:
            print(f'[save_datas] > {server_config["guild_name"]} 서버의 설정파일을 저장하는데 성공했습니다!')

    return '설정 저장에 성공했습니다!', None


@bot.event
async def on_ready():
    global emojis

    logger.info(f'discord.py version : {discord.__version__} ({discord.version_info})')
    logger.info(f'봇이 다음 옵션으로 실행되었습니다. :\ncommand_prefix : {bot.command_prefix}')
    logger.info(f'현재 봇이 소속된 서버 목록입니다 :\nguilds: {bot.guilds}')

    # 역할 설정시 사용할 이모지 명단 받아오기
    # 디코봇이 소속된 모든 서버에서 이모지를 받아온다.
    emojis = {x.name: x for x in bot.emojis}
    logger.debug(f'emojis = {emojis}')

    logger.debug(f'서버 설정파일을 불러온 서버 목록 : {server_config_dict.keys()}')

    # 봇이 플레이중인 게임을 설정할 수 있습니다.
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(name="아직 개발중!", type=1))

    logger.info('소속된 서버들에 봇 온라인 메세지를 전송합니다!')
    for guild in bot.guilds:
        logger.debug(f'{guild.name} 서버의 컨피그 존재여부를 확인합니다...')
        if guild.name in server_config_dict.keys():
            userlog_ch_id = server_config_dict[guild.name]['bot_ch_ids']['onofflog_ch_id']
            if userlog_ch_id != 0:
                logger.debug(f'{guild.name} 서버는 config가 존재합니다! 봇 온라인 메세지를 전송합니다.')
                await bot.get_channel(userlog_ch_id).send("라피스봇 온라인! :sunny:")
    logger.info('소속된 서버들에 봇 온라인 메세지를 전송했습니다!')

    @bot.event
    async def on_guild_join(guild: discord.Guild):
        logger.info(f'봇이 {guild.name} 서버에 참여했습니다! 서버 설정 파일을 생성합니다...')
        with open(f'./server_setting/{guild.name}_config.json', 'xt', encoding='utf-8') as config_file:
            global server_config_dict
            import json
            config_dict = {'guild_name': guild.name,
                           'bot_ch_ids': {
                               'notice_ch_id': 0,
                               'userlog_ch_id': 0,
                               'onofflog_ch_id': 0
                           },
                           'role_setting_msg_ids': [0],
                           'roles_dict': {}}
            server_config_dict[guild.name] = config_dict
            json.dump(obj=config_dict, fp=config_file, indent=4, ensure_ascii=False)

    @bot.event
    async def on_guild_remove(guild: discord.Guild):
        logger.info(f'봇이 {guild.name} 서버에서 나갔습니다! 서버 설정 리스트에서 이 서버의 불러와져있던 설정을 제거합니다....')
        server_config_dict.pop(guild.name)
        logger.info(f'{guild.name} 서버의 불러와져있던 설정을 제거했습니다! 서버 설정 파일을 제거합니다...')

        file = f'./server_setting/{guild.name}_config.json'
        if os.path.isfile(file):
            logger.info(f'{guild.name} 서버의 설정 파일을 발견했습니다!')
            os.remove(file)
            logger.info(f'{guild.name} 서버의 설정 파일을 제거했습니다!')
        else:
            logger.error(f'{guild.name} 서버의 설정 파일을 발견하지 못했습니다 :( 설정 파일 제거에 실패했습니다.')

    @bot.event
    async def on_member_join(member: discord.Member):
        logger.info(f'{member} has joined to the server {member.guild.name}')
        guild: discord.Guild = member.guild

        role = get(guild.roles, name=server_config_dict[guild.name]['auth']['noauth_role_name'])
        if role is not None:
            await member.add_roles(role)

        userlog_ch_id = server_config_dict[guild.name]['bot_ch_ids']['userlog_ch_id']
        if userlog_ch_id != 0:
            await bot.get_channel(userlog_ch_id).send(f'{member} 님 안녕하세요!')

    @bot.event
    async def on_member_remove(member: discord.Member):

        logger.info(f'{member} has left the server {member.guild.name}')
        guild: discord.Guild = member.guild
        userlog_ch_id = server_config_dict[guild.name]['bot_ch_ids']['userlog_ch_id']
        if userlog_ch_id != 0:
            await bot.get_channel(userlog_ch_id).send(f'{member} 님 안녕하세요!')

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
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
        # payload에서 필요한 정보를 저장한다.
        msg_id: int = payload.message_id  # 반응 추가 이벤트가 발생한 메세지 id
        guild_id: int = payload.guild_id  # 반응 추가 이벤트가 발생한 길드 id
        user_id: int = payload.user_id  # 반응 추가 이벤트를 발생시킨 유저 id

        member = payload.member  # 반응 추가 이벤트를 발생시킨 사용자. REACTION_ADD 유형의 이벤트에서만 사용 가능하다.

        guild: discord.Guild = find(lambda g: g.id == guild_id, bot.guilds)  # 반응 추가 이벤트가 발생한 길드
        logger.debug(f'[bot_event] (on_raw_reaction_add) > guild.name = {guild.name}')
        role_setting_msg_ids: list = server_config_dict[guild.name][
            'role_setting_msg_ids']  # 이벤트가 발생한 길드의 역할설정 이벤트 메세지 id

        auth_msg_id: int = server_config_dict[guild.name]['auth']['auth_msg_id']  # 이벤트가 발생한 길드의 역할설정 이벤트 메세지 id
        noauth_role_name: str = server_config_dict[guild.name]['auth']['noauth_role_name']
        auth_role_name: str = server_config_dict[guild.name]['auth']['auth_role_name']

        # 서버별로 roles_dict 내부 카테고리가 다를것을 상정하고, 루프를 돌며 이모지 명칭을 찾는다.
        emoji: discord.PartialEmoji = payload.emoji
        selected_emoji_category: str = ''  # roles_dict의 카테고리 분류 저장

        logger.info(
            f'[bot_event] (on_raw_reaction_add) > {user_id} 님이 {guild_id} 서버의 {msg_id} 메세지에서 {emoji} 반응을 추가했습니다.')

        """
        자동역할 기능 부분
        """
        if msg_id in role_setting_msg_ids:
            logger.info(f'[bot_event] (on_raw_reaction_add) > {user_id} 님이 역할을 신청했습니다.')

            roles_dict = server_config_dict[guild.name]['roles_dict']
            for category in roles_dict.keys():
                for role_emoji_name in roles_dict[category].keys():
                    if role_emoji_name == emoji.name:
                        selected_emoji_category = category
                        break
            logger.debug(f'[bot_event] (on_raw_reaction_add) > selected_emoji_category = {selected_emoji_category}')

            role_name = server_config_dict[guild.name]['roles_dict'][selected_emoji_category][emoji.name]
            logger.debug(f'[bot_event] (on_raw_reaction_add) > {user_id} 님이 신청한 역할 : {role_name}')
            role = get(guild.roles, name=role_name)

            if role is not None:
                member: discord.Member = find(lambda m: m.id == user_id, guild.members)
                if member is not None:
                    await member.add_roles(role, reason='Auto role assignment using bot.', atomic=True)
                else:
                    logger.error('[bot_event] (on_raw_reaction_add) > member not found')
            else:
                logger.error('[bot_event] (on_raw_reaction_add) > role not found')
        else:
            logger.info(f'[bot_event] (on_raw_reaction_add) > {emoji.name} is used at {msg_id}')

        """
        사용자 인증 부분
        """
        if msg_id == auth_msg_id:
            logger.info(f'[bot_event] (on_raw_reaction_add) > {user_id} 님이 인증 절차를 거쳤습니다.')
            logger.debug(f'[bot_event] (on_raw_reaction_remove) > 사용된 이모지 : {emoji}, emoji.name = {emoji.name}')
            if emoji.name == '✅':
                logger.info(f'[bot_event] (on_raw_reaction_add) > {member.display_name}님이 ✅ 반응을 제거해 인증을 취소했습니다.')

                noauth_role = get(guild.roles, name=noauth_role_name)
                logger.debug(f'[bot_event] (on_raw_reaction_add) > noauth_role = {noauth_role}')
                await member.remove_roles(noauth_role)
                auth_role = get(guild.roles, name=auth_role_name)
                logger.debug(f'[bot_event] (on_raw_reaction_add) > auth_role = {auth_role}')
                await member.add_roles(auth_role)
            else:
                pass

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
        user_id: int = payload.user_id  # 반응 추가 이벤트를 발생시킨 유저 id

        # member = payload.member  # 반응 추가 이벤트를 발생시킨 사용자. REACTION_ADD 유형의 이벤트에서만 사용 가능하다. --> REACTION_REMOVE 유형의 이벤트이므로 사용 불가.

        guild: discord.Guild = find(lambda g: g.id == guild_id, bot.guilds)  # 반응 추가 이벤트가 발생한 길드
        role_setting_msg_ids: list = server_config_dict[guild.name][
            'role_setting_msg_ids']  # 이벤트가 발생한 길드의 역할설정 이벤트 메세지 id

        auth_msg_id: int = server_config_dict[guild.name]['auth']['auth_msg_id']  # 이벤트가 발생한 길드의 역할설정 이벤트 메세지 id
        noauth_role_name: str = server_config_dict[guild.name]['auth']['noauth_role_name']
        auth_role_name: str = server_config_dict[guild.name]['auth']['auth_role_name']

        # 서버별로 roles_dict 내부 카테고리가 다를것을 상정하고, 루프를 돌며 이모지 명칭을 찾는다.
        emoji: discord.PartialEmoji = payload.emoji
        selected_emoji_category: str = ''  # roles_dict의 카테고리 분류 저장

        logger.info(
            f'[bot_event] (on_raw_reaction_remove) > {user_id} 님이 {guild_id} 서버의 {msg_id} 메세지에서 {emoji.name} 반응을 제거했습니다.')

        # 역할설정 메세지에서 일어난 이벤트라면
        if msg_id in role_setting_msg_ids:
            logger.info(f'[bot_event] (on_raw_reaction_remove) > {user_id} 님이 역할을 제거했습니다.')

            roles_dict = server_config_dict[guild.name]['roles_dict']
            for category in roles_dict.keys():
                for role_emoji_name in roles_dict[category].keys():
                    if role_emoji_name == emoji.name:
                        selected_emoji_category = category
                        break
            logger.debug(f'[bot_event] (on_raw_reaction_remove) > selected_emoji_category = {selected_emoji_category}')

            role_name = server_config_dict[guild.name]['roles_dict'][selected_emoji_category][emoji.name]
            logger.debug(f'[bot_event] (on_raw_reaction_remove) > {user_id} 님이 신청한 역할 : {role_name}')
            role = get(guild.roles, name=role_name)

            if role is not None:
                member: discord.Member = find(lambda m: m.id == user_id, guild.members)
                if member is not None:
                    await member.remove_roles(role, reason='Auto role assignment using bot.', atomic=True)
                else:
                    logger.error('[bot_event] (on_raw_reaction_remove) > member not found')
            else:
                logger.error('[bot_event] (on_raw_reaction_remove) > role not found')
        else:
            logger.info(f'[bot_event] (on_raw_reaction_remove) > {emoji.name} is used at {msg_id}')

        """
        사용자 인증 부분
        """
        if msg_id == auth_msg_id:
            logger.info(f'[bot_event] (on_raw_reaction_remove) > {user_id} 님이 인증 절차를 거쳤습니다.')
            logger.debug(f'[bot_event] (on_raw_reaction_remove) > 사용된 이모지 : {emoji}, emoji.name = {emoji.name}')
            if emoji.name == '✅':
                member: discord.Member = guild.get_member(user_id=user_id)
                logger.info(f'[bot_event] (on_raw_reaction_remove) > {member.display_name}님이 ✅ 반응을 제거해 인증을 취소했습니다.')

                noauth_role = get(guild.roles, name=noauth_role_name)
                logger.debug(f'[bot_event] (on_raw_reaction_remove) > noauth_role = {noauth_role}')
                await member.add_roles(noauth_role)
                auth_role = get(guild.roles, name=auth_role_name)
                logger.debug(f'[bot_event] (on_raw_reaction_remove) > auth_role = {auth_role}')
                await member.remove_roles(auth_role)
            else:
                pass

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
        await bot.process_commands(message)

    @bot.event
    async def on_command_error(ctx: discord.ext.commands.Context, e: discord.ext.commands.CommandError):
        logger.error(f'[bot-event] (on_command_error) > message : {ctx.message}')
        logger.error(f'[bot-event] (on_command_error) > error : {e}')
        if isinstance(e, commands.errors.CheckFailure):
            return

        if 'cooldown' in str(e):
            time_left: str = str(e).split("Try again in ")[1]
            cooltime: float = float(time_left)
            await ctx.send(f'명령어 재사용 대기시간이 {cooltime / 60}분 남았습니다.')
        if 'permission(s)' in str(e):
            missing_perm: str = str(e).replace('You are missing ', '').replace(' permission(s) to run this command.',
                                                                               '')
            await ctx.send(f'당신은 다음 권한을 가지고 있지 않습니다! : {missing_perm}')

    @bot.command(name='알람')
    async def setalarm(ctx: discord.ext.commands.Context, h: str = '0', m: str = '0', s: str = '0'):
        global do_waitforsec
        author: discord.Member = ctx.author
        hour = int(h)
        min = int(m)
        sec = int(s)
        logger.debug(f'time = {hour} {min} {sec}')
        await ctx.send(f'{hour}시간 {min}분 {sec}초 주기로 알람을 설정했습니다.')
        do_waitforsec = True
        import asyncio
        totalsec = hour * 3600 + min * 60 + sec
        while do_waitforsec:
            logger.debug(f'[알람] wating sec : {totalsec}')
            for currentmin in range(0, hour * 60 + min):
                logger.info(f'[알람] {currentmin}분 지났습니다.')
                lefttime = (hour * 60 + min) - currentmin
                logger.debug(f'lefttime = {lefttime}')
                await bot.change_presence(status=discord.Status.online,
                                          activity=discord.Game(name=f'알람까지 {lefttime}분 남았습니다', type=1))
                await asyncio.sleep(60)

            await asyncio.sleep(sec)
            logger.info(f'[알람] 시간이 다 되었습니다!')
            await ctx.send(f'{author.mention} 시간이 다 되었습니다!')
        await bot.change_presence(status=discord.Status.online,
                                  activity=discord.Game(name='아직 작업중!', type=1))

    @bot.command(name='알람끄기')
    async def stopalarm(ctx: discord.ext.commands.Context):
        global do_waitforsec
        do_waitforsec = False
        await ctx.send('알람을 종료했습니다!')

    @commands.is_owner()
    @bot.group(name="개발자")
    async def dev(ctx: discord.ext.commands.Context):
        if ctx.author.id in developer_ids:
            logger.info(f'[dev] > {ctx.author} 유저가 명령어를 사용했습니다 :\n> {ctx.message.content}')
            if ctx.message.content.replace(f'{bot.command_prefix}개발자', '') == '':
                await ctx.send('현재 다음과 같은 명령어들이 있어요!\n\n' +
                               '> **종료** : 개발자 전용 명령어로, 봇을 종료시킵니다.\n' +
                               '> **재시작** : 개발자 전용 명령어로, 봇을 재시작시킵니다. (WIP)\n' +
                               '> **공지하기** : 개발자 전용 명령어로, 봇이 접속해있는 서버의 봇 공지사항 채널에 공지사항을 전송합니다.\n' +
                               '> **설정저장** : 개발자 전용 명령어로, 현재 봇이 불러온 설정을 각 서버의 설정 파일로 저장합니다.\n')
            else:
                pass
        else:
            logger.info(f'{ctx.author}가 관리 명령어를 사용하려 했으나, 개발자가 아니므로 거부당했습니다..')
            await ctx.send('개발자만 사용할 수 있는 기능입니다!')

    @commands.cooldown(rate=1, per=60)
    @commands.is_owner()
    @dev.command(name="종료")
    async def stop(ctx: discord.ext.commands.Context):
        global do_reboot
        if ctx.author.id in developer_ids:
            logger.info(f'{ctx.author} 님이 봇을 종료시켰습니다.')
            await ctx.send('봇을 종료합니다...')
            do_reboot = False
            for guild in bot.guilds:
                if guild.name in server_config_dict.keys():
                    bot_onofflog_ch_id = server_config_dict[guild.name]['bot_ch_ids']['onofflog_ch_id']
                    if bot_onofflog_ch_id != 0:
                        await bot.get_channel(bot_onofflog_ch_id).send("라피스봇 오프라인...  :full_moon:")
            await bot.close()
        else:
            logger.info(f'{ctx.author}가 종료 명령어를 사용하려 했으나, 개발자가 아니므로 거부당했습니다..')
            await ctx.send('개발자만 사용할 수 있는 기능입니다!')

    @commands.cooldown(rate=1, per=60)
    @commands.is_owner()
    @dev.command(name="재시작")
    async def restart(ctx: discord.ext.commands.Context):
        global do_reboot
        if ctx.author.id in developer_ids:
            logger.info(f'{ctx.author} 님이 봇을 재시작시켰습니다.')
            await ctx.send('봇을 재시작합니다...')
            do_reboot = True
            for guild in bot.guilds:
                if guild.name in server_config_dict.keys():
                    bot_onofflog_ch_id = server_config_dict[guild.name]['bot_ch_ids']['onofflog_ch_id']
                    if bot_onofflog_ch_id != 0:
                        await bot.get_channel(bot_onofflog_ch_id).send("라피스봇 오프라인...  :full_moon:")
            await bot.close()
        else:
            logger.info(f'{ctx.author}가 재시작 명령어를 사용하려 했으나, 개발자가 아니므로 거부당했습니다..')
            await ctx.send('개발자만 사용할 수 있는 기능입니다!')

    @commands.cooldown(rate=1, per=60)
    @commands.is_owner()
    @dev.command(name="공지하기")
    async def sendnotice(ctx: discord.ext.commands.Context):
        logger.info(f'{ctx.author}가 공지하기 명령어를 사용했습니다.')
        if ctx.guild.name == official_management_servername and ctx.author.id in developer_ids:
            await ctx.send('소속된 서버에 해당 공지사항을 전송합니다!')
            for guild in bot.guilds:
                if guild.name in server_config_dict.keys():
                    notice_ch_id = server_config_dict[guild.name]['bot_ch_ids']['notice_ch_id']
                    if notice_ch_id != 0:
                        await bot.get_channel(notice_ch_id).send(f'봇 공지사항이 전달되었습니다! by {ctx.message.author}\n ' +
                                                                 f'{ctx.message.content.replace(f"{bot.command_prefix}개발자 공지하기 ", "")}')
        else:
            await ctx.send(f'라피스봇 공식 서버인 {official_management_servername} 서버에서만 사용 가능한 명령어입니다!')

    @commands.cooldown(rate=1, per=60)
    @commands.is_owner()
    @dev.command(name="설정저장")
    async def savedata(ctx: discord.ext.commands.Context):
        if ctx.author.id in developer_ids:
            logger.info(f'{ctx.author}가 설정 저장 명령어를 사용했습니다.')
            await ctx.send('설정 파일들을 저장합니다...')
            result, error = save_datas()
            await ctx.send(f'설정파일 저장 시도후 다음 결과를 얻었습니다 : {result}')
            if error is not None:
                await ctx.send(f'다음과 같은 오류가 발생했습니다! :\n```css\n{error.with_traceback(error.__traceback__)}\n```')
        else:
            logger.info(f'{ctx.author}가 설정저장 명령어를 사용하려 했으나, 개발자가 아니므로 거부당했습니다..')
            await ctx.send('개발자만 사용할 수 있는 기능입니다!')

    @commands.has_guild_permissions(administrator=True)
    @bot.group(name="관리")
    async def manage(ctx: discord.ext.commands.Context):
        if ctx.author.id in developer_ids:
            logger.info(f'{ctx.author} 유저가 명령어를 사용했습니다 :\n> {ctx.message.content}')
            if ctx.message.content.replace(f'{bot.command_prefix}관리', '') == '':
                await ctx.send('현재 다음과 같은 명령어들이 있어요!\n\n' +
                               '**자동역할** : 관리자 전용 명령어로, 명령어를 사용한 채널에 자동역할 메세지를 생성하고 해당 메세지에 반응을 추가하고 제거하는 방식으로 역할 부여를 자동화합니다.\n' +
                               '**설정보기** : 관리자 전용 명령어로, 명령어를 사용한 서버의 불러와진 설정(json)을 코드 하이라이팅을 입혀 채팅으로 보여줍니다.')
            else:
                pass
        else:
            logger.info(f'{ctx.author}가 관리 명령어를 사용하려 했으나, 서버 관리자가 아니므로 거부당했습니다..')
            await ctx.send('서버 관리자만 사용할 수 있는 기능입니다!')

    @commands.cooldown(rate=1, per=60 * 60)
    @commands.has_guild_permissions(administrator=True)
    @manage.command(name="자동역할")
    async def autorole(ctx: discord.ext.commands.Context):
        logger.info(f'{ctx.author}가 자동역할 명령어를 사용했습니다.')
        global server_config_dict
        guild: discord.Guild = ctx.guild
        logger.info(
            f'[역할설정 기능] {ctx.author} 님이 {guild} 서버의 {ctx.message.channel} 채널에서 {ctx.prefix}{ctx.command} 을(를) 사용했습니다.')

        await ctx.send(content='역할 자동부여 메세지 :')
        role_setting_msg_ids: list = []
        try:
            logger.debug(
                f'server_config_dict[guild.name]["roles_dict"].keys() = {server_config_dict[guild.name]["roles_dict"].keys()}')
            for category in server_config_dict[guild.name]['roles_dict'].keys():
                content = f'**{category}**\n'
                msg = await ctx.send(content=content)
                logger.debug(
                    f"server_config_dict[guild.name]['roles_dict'][{category}].keys() = {server_config_dict[guild.name]['roles_dict'][category].keys()}")
                for emoji in server_config_dict[guild.name]['roles_dict'][category].keys():
                    content.join(
                        f"<:{emoji}:{emojis[emoji].id}> : {server_config_dict[guild.name]['roles_dict'][category][emoji]}\n")
                    await msg.edit(content=content, supress=False)
                    await msg.add_reaction(emojis[emoji])
                role_setting_msg_ids.append(msg.id)
        except Exception as e:
            import traceback
            logger.error('[bot_command] autorole > Exception caught! :')
            traceback.print_exception(type(e), e, e.__traceback__)

        logger.info('채널 설정 완료. 생성된 메세지의 id를 저장합니다.')
        logger.debug(f'[bot_command] autorole > role_setting_msg_ids = {role_setting_msg_ids}')
        server_config_dict[guild.name]['role_setting_msg_ids'] = role_setting_msg_ids

    @commands.has_guild_permissions(administrator=True)
    @manage.command(name="설정보기")
    async def showconfig(ctx: discord.ext.commands.Context):
        logger.info(f'{ctx.author}가 설정보기 명령어를 사용했습니다.')
        import json
        await ctx.send('이 서버의 설정 파일을 보여드릴게요!')
        config_str = json.dumps(obj=server_config_dict[ctx.guild.name], indent=4, ensure_ascii=False)
        await ctx.send(f'```json\n{config_str}\n```')

    @commands.has_guild_permissions(administrator=True)
    @manage.command(name="유저인증")
    async def auth(ctx: discord.ext.commands.Context, msg: str = '✅ 이모지를 눌러 인증하세요!'):
        global server_config_dict
        logger.info(f'{ctx.author}가 유저인증 명령어를 사용했습니다.')
        guild_name = ctx.guild.name
        auth_msg = await ctx.send(f'당신이 정상적인 유저인지 확인합니다!\n> {msg}')
        server_config_dict[guild_name]['auth']['auth_msg_id'] = auth_msg.id
        await auth_msg.add_reaction('✅')


# print ASCII ART
with open(file='lapisbot_ascii.txt', mode='rt', encoding='utf-8') as f:
    print(f.read())

# init bot settings : loads config, server settings
init()

# set token
print(f'token = {token}')

# run bot
bot.run(token)

# save datas before program stops
result, error = save_datas()
print(f'save_datas() 실행결과 : {result}')
if error is not None:
    print(f'save_datas() 실행결과 발생한 오류 : {error.with_traceback(error.__traceback__)}')

# if reboot mode on, run reboot code
if bot.is_closed() and do_reboot:
    print('[bot.py] > 봇 재시작 명령이 들어와 봇을 재시작합니다 :')
    excutable = sys.executable
    args = sys.argv[:]
    args.insert(0, excutable)
    os.execv(sys.executable, args)
