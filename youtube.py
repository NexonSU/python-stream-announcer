#!/usr/bin/env python
import config
import json
import os
import sys
import time
import requests
import logging
from bs4 import BeautifulSoup
 
temp_folder_name = __file__.rsplit('.', 1)[0]

logging.basicConfig(filename=f"{temp_folder_name}.log", level=config.loglevel, format=config.logformat, datefmt=config.logdatefmt)

#checking temp files
if not os.path.exists(temp_folder_name): os.makedirs(temp_folder_name)
tempfiles = ['game', 'msg', 'status', 'stream', 'viewers']
for file in tempfiles: 
	if not os.path.exists(f'{temp_folder_name}/{file}'): 
		os.mknod(f'{temp_folder_name}/{file}')
if not os.path.exists(f'{temp_folder_name}/categorylist'):
	categorylist = requests.get('https://www.googleapis.com/youtube/v3/videoCategories', params={'part': 'snippet', 'regionCode': 'ru', 'hl': 'ru_RU', 'key': config.youtube_api_key}).text
	open(f'{temp_folder_name}/categorylist', 'wt', encoding='utf-8').write(categorylist)

#checking for videoid on stream page 
stream = requests.get('https://www.youtube.com/embed/live_stream', params={'channel': config.youtube_channelid}).content
soup = BeautifulSoup(stream, features="html.parser")
videoid = soup.head.find_all('link', rel="canonical")[0]['href'].split('watch?v=')[1]

#getting stream information
stream = requests.get('https://www.googleapis.com/youtube/v3/videos', params={'part': 'snippet,liveStreamingDetails', 'id': videoid, 'key': config.youtube_api_key}).json().get("items")[0]

#checking status and game changes
categorylist = json.loads(open(f'{temp_folder_name}/categorylist', 'r').read());
category = [subd['snippet']['title'] for subd in categorylist['items'] if subd['id'] == stream['snippet']['categoryId']][0]
status = stream['snippet']['title']
thumbnail = 'https://zavtrastream.nexon.su/thumbnail.jpg?'+str(time.time())

if open(f'{temp_folder_name}/status', 'r').read() != status:
	open(f'{temp_folder_name}/status', 'wt', encoding='utf-8').write(status)
	message = f'Статус изменен на "{status}".'
	logging.info(message)
	requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendMessage', data={'chat_id': config.telegram_chat, 'text': message, 'disable_notification': True})

if open(f'{temp_folder_name}/game', 'r').read() != category:
	open(f'{temp_folder_name}/game', 'wt', encoding='utf-8').write(category)
	message = f'Категория изменена на "{category}".'
	logging.info(message)
	requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendMessage', data={'chat_id': config.telegram_chat, 'text': message, 'disable_notification': True})

#checking stream online status
if 'concurrentViewers' in stream['liveStreamingDetails']:
	logging.info('Stream online')
	viewers = str(stream['liveStreamingDetails']['concurrentViewers'])
	logging.info(f'Viewers: {viewers}')
	if open(f'{temp_folder_name}/stream', 'r').read() != 'online':
		#announcing stream in telegram
		open(f'{temp_folder_name}/stream', 'wt', encoding='utf-8').write('online')
		open(f'{temp_folder_name}/viewers', 'wt', encoding='utf-8').write('0')
		message = f'Стрим "{status}" начался.\nКатегория: {category}.\nhttps://www.youtube.com/watch?v={videoid}'
		logging.info(message)
		os.system(f'youtube-dl --get-url "https://www.youtube.com/watch?v={videoid}" > {temp_folder_name}/stream-url')
		time.sleep(1)
		os.system(f'ffmpeg -i $(cat {temp_folder_name}/stream-url) -f image2 -frames:v 1 -y -v 0 {temp_folder_name}/thumbnail.jpg')
		time.sleep(3)
		msg = requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendPhoto', data={'chat_id': config.telegram_chat, 'photo': thumbnail, 'caption': message}).json()
		open(f'{temp_folder_name}/msg', 'wt', encoding='utf-8').write(str(msg['result']['message_id']))
	else:
		#updating stream information in telegram
		msg = open(f'{temp_folder_name}/msg', 'r').read();
		caption = f'Стрим: {status}.\nКатегория: {category}.\nОнлайн: {viewers}.\nhttps://www.youtube.com/watch?v={videoid}'
		os.system(f'youtube-dl --get-url "https://www.youtube.com/watch?v={videoid}" > {temp_folder_name}/stream-url')
		time.sleep(1)
		os.system(f'ffmpeg -i $(cat {temp_folder_name}/stream-url) -f image2 -frames:v 1 -y -v 0 {temp_folder_name}/thumbnail.jpg')
		time.sleep(3)
		requests.post(f'https://api.telegram.org/bot{config.telegram_token}/editMessageMedia', data={'chat_id': config.telegram_chat, 'message_id': msg, 'media': json.dumps({'type': 'photo', 'media': thumbnail, 'caption': caption})})
	if int(open(f'{temp_folder_name}/viewers', 'r').read()) < int(viewers):
		#updating viewers count
		open(f'{temp_folder_name}/viewers', 'wt', encoding='utf-8').write(str(viewers))
else:
	logging.info('Stream offline')
	if open(f'{temp_folder_name}/stream', 'r').read() != 'offline':
		#posting end of stream in telegram
		open(f'{temp_folder_name}/stream', 'wt', encoding='utf-8').write('offline')
		viewers = open(f'{temp_folder_name}/viewers', 'r').read();
		status = open(f'{temp_folder_name}/status', 'r').read();
		msg = open(f'{temp_folder_name}/msg', 'r').read();
		message = f'Стрим "{status}" закончился.\nМаксимум зрителей за стрим: {viewers}.'
		logging.info(message)
		requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendMessage', data={'chat_id': config.telegram_chat, 'text': message, 'reply_to_message_id': msg, 'disable_notification': True})

logging.info(f'Status: {status}')
logging.info(f'Category: {category}')