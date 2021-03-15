#!/usr/bin/env python
import config
import os
import pickle
import requests
import random
from bs4 import BeautifulSoup

#checking pickle file
if not os.path.exists('youtube.pkl'):
	storage = {'lastvideoid': ''} 
	pickle.dump(storage, open('youtube.pkl', 'wb'))

#checking for videoid on stream page
stream = requests.get(f'https://youtube.com/{config.youtube_channelname}/live?{random.random()}').content
soup = BeautifulSoup(stream, features="html.parser")
title = soup.title.string.split(' - YouTube')[0]
videoid = soup.find('link', rel='canonical')['href'].split('watch?v=')[1]

#loading variables from pickle file
storage = pickle.load(open('youtube.pkl', 'rb'))

if videoid != storage['lastvideoid']:
	#announcing stream in telegram
	message = f'Стрим "{title}" начался.\nhttps://youtube.com/{config.youtube_channelname}/live'
	requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendMessage', data={'chat_id': config.telegram_chat, 'text': message})
	storage['lastvideoid'] = videoid

	#store variables to pickle file
	pickle.dump(storage, open('youtube.pkl', 'wb'))
