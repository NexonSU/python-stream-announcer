import json
import os
import sys
import time
import datetime
import requests


temp_folder_name = __file__.rsplit('.', 1)[0]
twitch_client_id = 'example' #to get Client ID, visit https://dev.twitch.tv/docs/authentication#registration
telegram_token = 'example:example' #to get token, create bot via @botfather at telegram https://t.me/BotFather
telegram_chat = '@example' #your telegram channel
twitch_channelid = 'example' #to get your channel ID, you need to make API call, but you can just open your Twitch page and lookup for some API requests from DevTools > Network, for example https://api.twitch.tv/helix/streams?user_id=<your ID>
twitch_channelname = 'example' #for link in messages

#checking temp files
if not os.path.exists(temp_folder_name): os.makedirs(temp_folder_name)
tempfiles = ['game', 'msg', 'status', 'stream', 'viewers']
for file in tempfiles: 
	if not os.path.exists(f'{temp_folder_name}/{file}'): 
		os.mknod(f'{temp_folder_name}/{file}')

#checking status and game changes
channel = requests.get(f'https://api.twitch.tv/kraken/channels/{twitch_channelid}', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)', 'Client-ID': twitch_client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}).json()
status = channel['status']
game = channel['game']

if open(f'{temp_folder_name}/status', 'r').read() != status:
	open(f'{temp_folder_name}/status', 'wt', encoding='utf-8').write(status)
	message = f'Статус изменен на "{status}".'
	requests.post(f'https://api.telegram.org/bot{telegram_token}/sendMessage', data={'chat_id': telegram_chat, 'text': message, 'disable_notification': True})

if open(f'{temp_folder_name}/game', 'r').read() != game:
	open(f'{temp_folder_name}/game', 'wt', encoding='utf-8').write(game)
	message = f'Категория изменена на "{game}".'
	requests.post(f'https://api.telegram.org/bot{telegram_token}/sendMessage', data={'chat_id': telegram_chat, 'text': message, 'disable_notification': True})

#getting stream information
stream = requests.get(f'https://api.twitch.tv/kraken/streams/{twitch_channelid}', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)', 'Client-ID': twitch_client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}).json()

#checking stream online status
if stream.get("stream") != None:
	stream = stream["stream"]
	viewers = str(stream['viewers'])
	thumbnail = stream['preview']['large']+'?'+str(time.time())
	if open(f'{temp_folder_name}/stream', 'r').read() != 'online':
		#posting stream announce in telegram
		open(f'{temp_folder_name}/stream', 'wt', encoding='utf-8').write('online')
		open(f'{temp_folder_name}/viewers', 'wt', encoding='utf-8').write('0')
		message = f'Стрим "{status}" начался.\nКатегория: {game}.\nhttps://twitch.tv/{twitch_channelname}'
		msg = requests.post(f'https://api.telegram.org/bot{telegram_token}/sendPhoto', data={'chat_id': telegram_chat, 'photo': thumbnail, 'caption': message}).json()
		open(f'{temp_folder_name}/msg', 'wt', encoding='utf-8').write(str(msg['result']['message_id']))
	else:
		#updating stream information in telegram
		msg = open(f'{temp_folder_name}/msg', 'r').read();
		caption = f'Стрим: "{status}".\nКатегория: {game}.\nОнлайн: {viewers}.\nhttps://twitch.tv/{twitch_channelname}'
		requests.post(f'https://api.telegram.org/bot{telegram_token}/editMessageMedia', data={'chat_id': telegram_chat, 'message_id': msg, 'media': json.dumps({'type': 'photo', 'media': thumbnail, 'caption': caption})})
	if int(open(f'{temp_folder_name}/viewers', 'r').read()) < int(viewers):
		#updating viewers count
		open(f'{temp_folder_name}/viewers', 'wt', encoding='utf-8').write(viewers)
else:
	if open(f'{temp_folder_name}/stream', 'r').read() != 'offline':
		#posting end of stream in telegram
		open(f'{temp_folder_name}/stream', 'wt', encoding='utf-8').write('offline')
		viewers = open(f'{temp_folder_name}/viewers', 'r').read();
		status = open(f'{temp_folder_name}/status', 'r').read();
		msg = open(f'{temp_folder_name}/msg', 'r').read();
		message = f'Стрим "{status}" закончился.\nМаксимум зрителей за стрим: {viewers}'
		requests.post(f'https://api.telegram.org/bot{telegram_token}/sendMessage', data={'chat_id': telegram_chat, 'text': message, 'reply_to_message_id': msg, 'disable_notification': True})