import discord
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# ── 설정 ──────────────────────────────────────────────────────
BOT_TOKEN    = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN')
GUILD_ID     = int(os.environ.get('GUILD_ID', '1272943446998388887'))
FIREBASE_CRED = os.environ.get('FIREBASE_CRED', '{}')

# 블루팀 채널 키워드
BLUE_KW = ['블루팀', 'BLUE', 'blue', '1팀', '내전 1팀', '내전1팀']
# 레드팀 채널 키워드
RED_KW  = ['레드팀', 'RED', 'red', '2팀', '내전 2팀', '내전2팀']

# ── Firebase 초기화 ───────────────────────────────────────────
def init_firebase():
    try:
        cred_dict = json.loads(FIREBASE_CRED)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f'Firebase 초기화 실패: {e}')
        return None

db = init_firebase()

# ── 채널 팀 판별 ──────────────────────────────────────────────
def get_team(channel_name):
    for kw in BLUE_KW:
        if kw in channel_name:
            return 'blue'
    for kw in RED_KW:
        if kw in channel_name:
            return 'red'
    return None

# ── Firebase에 음성 상태 저장 ─────────────────────────────────
def save_voice_status(guild_id, blue_members, red_members):
    if not db:
        print('Firebase 없음 - 저장 스킵')
        return
    try:
        db.collection('voiceStatus').document(str(guild_id)).set({
            'blue': blue_members,
            'red':  red_members,
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        print(f'저장완료 | 블루: {blue_members} | 레드: {red_members}')
    except Exception as e:
        print(f'Firebase 저장 실패: {e}')

# ── 서버 음성채널 전체 스캔 ───────────────────────────────────
def scan_voice(guild):
    blue, red = [], []
    for ch in guild.voice_channels:
        team = get_team(ch.name)
        if not team:
            continue
        for m in ch.members:
            nick = m.nick or m.display_name or m.name
            if team == 'blue':
                blue.append(nick)
            else:
                red.append(nick)
    return blue, red

# ── Discord Bot ───────────────────────────────────────────────
intents = discord.Intents.default()
intents.voice_states = True
intents.members      = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'봇 로그인 완료: {client.user}')
    guild = client.get_guild(GUILD_ID)
    if guild:
        blue, red = scan_voice(guild)
        save_voice_status(GUILD_ID, blue, red)
    else:
        print(f'서버를 찾을 수 없음: {GUILD_ID}')

@client.event
async def on_voice_state_update(member, before, after):
    if member.guild.id != GUILD_ID:
        return
    blue, red = scan_voice(member.guild)
    save_voice_status(GUILD_ID, blue, red)

client.run(BOT_TOKEN)
