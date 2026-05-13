import discord
import requests
import os
import json
from datetime import datetime, timezone

# ── 설정 ──────────────────────────────────────────────────────
BOT_TOKEN     = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN')
GUILD_ID      = int(os.environ.get('GUILD_ID', '1272943446998388887'))
FIREBASE_URL  = os.environ.get('FIREBASE_URL', '')  # Firestore REST API URL

# 블루팀 채널 키워드
BLUE_KW = ['블루팀', 'BLUE', 'blue', '1팀', '내전 1팀', '내전1팀']
# 레드팀 채널 키워드
RED_KW  = ['레드팀', 'RED', 'red', '2팀', '내전 2팀', '내전2팀']

# ── 채널 팀 판별 ──────────────────────────────────────────────
def get_team(channel_name):
    for kw in BLUE_KW:
        if kw in channel_name:
            return 'blue'
    for kw in RED_KW:
        if kw in channel_name:
            return 'red'
    return None

# ── Firestore REST API로 저장 ─────────────────────────────────
def save_voice_status(guild_id, blue_members, red_members):
    if not FIREBASE_URL:
        print('FIREBASE_URL 없음 - 저장 스킵')
        return
    try:
        url = f'{FIREBASE_URL}/voiceStatus/{guild_id}'
        payload = {
            'fields': {
                'blue': {'arrayValue': {'values': [{'stringValue': m} for m in blue_members]}},
                'red':  {'arrayValue': {'values': [{'stringValue': m} for m in red_members]}},
                'updatedAt': {'stringValue': datetime.now(timezone.utc).isoformat()}
            }
        }
        resp = requests.patch(url, json=payload, timeout=10)
        if resp.status_code in (200, 201):
            print(f'저장완료 | 블루: {blue_members} | 레드: {red_members}')
        else:
            print(f'저장 실패: {resp.status_code} {resp.text[:200]}')
    except Exception as e:
        print(f'저장 오류: {e}')

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
        print(f'초기 스캔 완료')
    else:
        print(f'서버를 찾을 수 없음: {GUILD_ID}')

@client.event
async def on_voice_state_update(member, before, after):
    if member.guild.id != GUILD_ID:
        return
    blue, red = scan_voice(member.guild)
    save_voice_status(GUILD_ID, blue, red)

client.run(BOT_TOKEN)
