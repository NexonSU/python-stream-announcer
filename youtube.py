#!/usr/bin/env python
import config
import os
import pickle
import requests
import random
from bs4 import BeautifulSoup
import youtube_dl
import ffmpeg

#checking pickle file
if not os.path.exists('youtube.pkl'):
	storage = {'lastvideoid': ''} 
	pickle.dump(storage, open('youtube.pkl', 'wb'))

#checking for videoid on stream page
stream = requests.get(f'https://www.youtube.com/{config.youtube_channelname}/live?{random.random()}').content
soup = BeautifulSoup(stream, features="html.parser")
title = soup.title.string.split(' - YouTube')[0]
videoid = soup.find('link', rel='canonical')['href'].split('watch?v=')[1]

#loading variables from pickle file
storage = pickle.load(open('youtube.pkl', 'rb'))

if videoid != storage['lastvideoid']:
	#announcing stream in telegram
	message = f'Стрим "{title}" начался.\nhttps://www.youtube.com/watch?v={videoid}'
	playlist = youtube_dl.YoutubeDL({'skip_download': True, 'quiet': True}).extract_info(f'https://www.youtube.com/watch?v={videoid}')['url']
	thumbnail, _ = (ffmpeg.input(playlist).output('pipe:', vframes=1, format='image2', vcodec='mjpeg', **{'vf': 'scale=-1:720'}).run(capture_stdout=True, quiet=True))
	requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendPhoto', data={'chat_id': config.telegram_chat, 'caption': message}, files={'photo': thumbnail})
	storage['lastvideoid'] = videoid

	#store variables to pickle file
	pickle.dump(storage, open('youtube.pkl', 'wb'))
