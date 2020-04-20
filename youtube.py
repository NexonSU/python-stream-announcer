#!/usr/bin/env python
import config
import json
import os
import sys
import time
import requests
from bs4 import BeautifulSoup
import logging
import pickle
import youtube_dl
import ffmpeg
import base64

script_name = __file__.rsplit('.', 1)[0]

#log init
logging.basicConfig(filename=f"{script_name}.log", level=config.loglevel, format=config.logformat, datefmt=config.logdatefmt)

#checking pickle file
if not os.path.exists(f'{script_name}.pkl'):
	storage = {'category': 'None', 'msg': '0', 'status': 'None', 'stream': 'offline', 'viewers': '0', 'categorylist_update_date': 0, 'categorylist': '', 'stream-url': '', 'thumbnail': ''} 
	pickle.dump(storage, open(f'{script_name}.pkl', 'wb'))

#loading variables from pickle file
storage = pickle.load(open(f'{script_name}.pkl', 'rb'))

#update categorylist
if int(time.time())-int(storage['categorylist_update_date']) > 2630000:
	storage['categorylist'] = requests.get('https://www.googleapis.com/youtube/v3/videoCategories', params={'part': 'snippet', 'regionCode': 'ru', 'hl': 'ru_RU', 'key': config.youtube_api_key}).json()
	storage['categorylist_update_date'] = int(time.time())

#checking for videoid on stream page 
stream = requests.get('https://www.youtube.com/embed/live_stream', params={'channel': config.youtube_channelid}).content
soup = BeautifulSoup(stream, features="html.parser")
videoid = soup.head.find_all('link', rel="canonical")[0]['href'].split('watch?v=')[1]

#getting stream information
stream = requests.get('https://www.googleapis.com/youtube/v3/videos', params={'part': 'snippet,liveStreamingDetails', 'id': videoid, 'key': config.youtube_api_key}).json().get("items")[0]

#checking status and category changes
categorylist = storage['categorylist']
category = [subd['snippet']['title'] for subd in categorylist['items'] if subd['id'] == stream['snippet']['categoryId']][0]
status = stream['snippet']['title']

if storage['status'] != status:
	storage['status'] = status
	message = f'Статус изменен на "{status}".'
	logging.info(message)
	requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendMessage', data={'chat_id': config.telegram_chat, 'text': message, 'disable_notification': True})

if storage['category'] != category:
	storage['category'] = category
	message = f'Категория изменена на "{category}".'
	logging.info(message)
	requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendMessage', data={'chat_id': config.telegram_chat, 'text': message, 'disable_notification': True})

#checking stream online status
if 'concurrentViewers' in stream['liveStreamingDetails']:
	logging.info('Stream online')
	viewers = str(stream['liveStreamingDetails']['concurrentViewers'])
	logging.info(f'Viewers: {viewers}')
	if storage['stream'] != 'online':
		#announcing stream in telegram
		storage['stream'] = 'online'
		storage['viewers'] = 0
		message = f'Стрим "{status}" начался.\nКатегория: {category}.\nhttps://www.youtube.com/watch?v={videoid}'
		logging.info(message)
		playlist = youtube_dl.YoutubeDL({'skip_download': True, 'quiet': True}).extract_info(f'https://www.youtube.com/watch?v={videoid}')['url']
		thumbnail, _ = (ffmpeg.input(playlist).output('pipe:', vframes=1, format='image2', vcodec='mjpeg', **{'vf': 'scale=-1:720'}).run(capture_stdout=True, quiet=True))
		msg = requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendPhoto', data={'chat_id': config.telegram_chat, 'caption': message}, files={'photo': thumbnail}).json()
		storage['msg'] = msg['result']['message_id']
	else:
		#updating stream information in telegram
		msg = str(storage['msg'])
		caption = f'Стрим: {status}.\nКатегория: {category}.\nОнлайн: {viewers}.\nhttps://www.youtube.com/watch?v={videoid}'
		playlist = youtube_dl.YoutubeDL({'skip_download': True, 'quiet': True}).extract_info(f'https://www.youtube.com/watch?v={videoid}')['url']
		thumbnail, _ = (ffmpeg.input(playlist).output('pipe:', vframes=1, format='image2', vcodec='mjpeg', **{'vf': 'scale=-1:720'}).run(capture_stdout=True, quiet=True))
		#temporary solution with web-server
		open('thumbnail.jpg', 'wb').write(thumbnail)
		thumbnail = 'https://<yourdomain>/<path to thumbnail.jpg>?'+str(time.time())
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
		message = f'Стрим "{status}" закончился.\nМаксимум зрителей за стрим: {viewers}.'
		logging.info(message)
		requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendMessage', data={'chat_id': config.telegram_chat, 'text': message, 'reply_to_message_id': msg, 'disable_notification': True})

logging.info(f'Status: {status}')
logging.info(f'Category: {category}')

#store variables to pickle file
pickle.dump(storage, open(f'{script_name}.pkl', 'wb'))