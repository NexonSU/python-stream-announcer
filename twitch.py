#!/usr/bin/env python
import config
import json
import os
import sys
import time
import datetime
import requests
import logging

temp_folder_name = __file__.rsplit('.', 1)[0]

logging.basicConfig(filename=f"{temp_folder_name}.log", level=config.loglevel, format=config.logformat, datefmt=config.logdatefmt)

#checking temp files
if not os.path.exists(temp_folder_name): os.makedirs(temp_folder_name)
tempfiles = ['game', 'msg', 'status', 'stream', 'viewers']
for file in tempfiles: 
	if not os.path.exists(f'{temp_folder_name}/{file}'): 
		os.mknod(f'{temp_folder_name}/{file}')

#checking status and game changes
channel = requests.get(f'https://api.twitch.tv/kraken/channels/{config.twitch_channelid}', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)', 'Client-ID': config.twitch_client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}).json()
status = channel['status']
game = channel['game']

if open(f'{temp_folder_name}/status', 'r').read() != status:
	open(f'{temp_folder_name}/status', 'wt', encoding='utf-8').write(status)
	message = f'Статус изменен на "{status}".'
	logging.info(message)
	requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendMessage', data={'chat_id': config.telegram_chat, 'text': message, 'disable_notification': True})

if open(f'{temp_folder_name}/game', 'r').read() != game:
	open(f'{temp_folder_name}/game', 'wt', encoding='utf-8').write(game)
	message = f'Категория изменена на "{game}".'
	logging.info(message)
	requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendMessage', data={'chat_id': config.telegram_chat, 'text': message, 'disable_notification': True})

#getting stream information
stream = requests.get(f'https://api.twitch.tv/kraken/streams/{config.twitch_channelid}', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)', 'Client-ID': config.twitch_client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}).json()

#checking stream online status
if stream.get("stream") != None:
	stream = stream["stream"]
	viewers = str(stream['viewers'])
	thumbnail = stream['preview']['large']+'?'+str(time.time())
	logging.info('Stream online')
	logging.info(f'Viewers: {viewers}')
	if open(f'{temp_folder_name}/stream', 'r').read() != 'online':
		#posting stream announce in telegram
		open(f'{temp_folder_name}/stream', 'wt', encoding='utf-8').write('online')
		open(f'{temp_folder_name}/viewers', 'wt', encoding='utf-8').write('0')
		message = f'Стрим "{status}" начался.\nКатегория: {game}.\nhttps://twitch.tv/{config.twitch_channelname}'
		logging.info(message)
		msg = requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendPhoto', data={'chat_id': config.telegram_chat, 'photo': thumbnail, 'caption': message}).json()
		open(f'{temp_folder_name}/msg', 'wt', encoding='utf-8').write(str(msg['result']['message_id']))
	else:
		#updating stream information in telegram
		msg = open(f'{temp_folder_name}/msg', 'r').read();
		caption = f'Стрим: {status}.\nКатегория: {game}.\nОнлайн: {viewers}.\nhttps://twitch.tv/{config.twitch_channelname}'
		requests.post(f'https://api.telegram.org/bot{config.telegram_token}/editMessageMedia', data={'chat_id': config.telegram_chat, 'message_id': msg, 'media': json.dumps({'type': 'photo', 'media': thumbnail, 'caption': caption})})
	if int(open(f'{temp_folder_name}/viewers', 'r').read()) < int(viewers):
		#updating viewers count
		open(f'{temp_folder_name}/viewers', 'wt', encoding='utf-8').write(viewers)
else:
	logging.info('Stream offline')
	if open(f'{temp_folder_name}/stream', 'r').read() != 'offline':
		#posting end of stream in telegram
		open(f'{temp_folder_name}/stream', 'wt', encoding='utf-8').write('offline')
		viewers = open(f'{temp_folder_name}/viewers', 'r').read();
		status = open(f'{temp_folder_name}/status', 'r').read();
		msg = open(f'{temp_folder_name}/msg', 'r').read();
		message = f'Стрим "{status}" закончился.\nМаксимум зрителей за стрим: {viewers}'
		logging.info(message)
		requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendMessage', data={'chat_id': config.telegram_chat, 'text': message, 'reply_to_message_id': msg, 'disable_notification': True})

logging.info(f'Status: {status}')
logging.info(f'Category: {game}')