#!/usr/bin/env python
import config
import json
import os
import sys
import time
import datetime
import requests
import logging
import pickle

script_name = __file__.rsplit('.', 1)[0]

#log init
logging.basicConfig(filename=f"{script_name}.log", level=config.loglevel, format=config.logformat, datefmt=config.logdatefmt)

#checking pickle file
if not os.path.exists(f'{script_name}.pkl'):
	storage = {'game': 'None', 'msg': '0', 'status': 'None', 'stream': 'offline', 'viewers': '0'} 
	pickle.dump(storage, open(f'{script_name}.pkl', 'wb'))

#loading variables from pickle file
storage = pickle.load(open(f'{script_name}.pkl', 'rb'))

#checking status and game changes
channel = requests.get(f'https://api.twitch.tv/kraken/channels/{config.twitch_channelid}', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)', 'Client-ID': config.twitch_client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}).json()
status = channel['status']
game = channel['game']

if storage['status'] != status:
	storage['status'] = status
	message = f'Статус изменен на "{status}".'
	logging.info(message)
	requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendMessage', data={'chat_id': config.telegram_chat, 'text': message, 'disable_notification': True})

if storage['game'] != game:
	storage['game'] = game
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
	if storage['stream'] != 'online':
		#posting stream announce in telegram
		storage['stream'] = 'online'
		storage['viewers'] = 0
		message = f'Стрим "{status}" начался.\nКатегория: {game}.\nhttps://twitch.tv/{config.twitch_channelname}'
		logging.info(message)
		msg = requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendPhoto', data={'chat_id': config.telegram_chat, 'photo': thumbnail, 'caption': message}).json()
		storage['msg'] = msg['result']['message_id']
	else:
		#updating stream information in telegram
		msg = storage['msg']
		caption = f'Стрим: {status}.\nКатегория: {game}.\nОнлайн: {viewers}.\nhttps://twitch.tv/{config.twitch_channelname}'
		requests.post(f'https://api.telegram.org/bot{config.telegram_token}/editMessageMedia', data={'chat_id': config.telegram_chat, 'message_id': msg, 'media': json.dumps({'type': 'photo', 'media': thumbnail, 'caption': caption})})
	if int(storage['viewers']) < int(viewers):
		#updating viewers count
		storage['viewers'] = viewers
else:
	logging.info('Stream offline')
	if storage['stream'] != 'offline':
		#posting end of stream in telegram
		storage['stream'] = 'offline'
		viewers = storage['viewers']
		status = storage['status']
		msg = storage['msg']
		message = f'Стрим "{status}" закончился.\nМаксимум зрителей за стрим: {viewers}'
		logging.info(message)
		requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendMessage', data={'chat_id': config.telegram_chat, 'text': message, 'reply_to_message_id': msg, 'disable_notification': True})

logging.info(f'Status: {status}')
logging.info(f'Category: {game}')

#store variables to pickle file
pickle.dump(storage, open(f'{script_name}.pkl', 'wb'))