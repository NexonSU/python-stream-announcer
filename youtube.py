#!/usr/bin/env python
import config
import sys
import requests
from bs4 import BeautifulSoup
import youtube_dl
import ffmpeg

#checking for videoid on stream page
try:
	stream = requests.get('https://www.youtube.com/embed/live_stream', params={'channel': config.youtube_channelid}).content
	soup = BeautifulSoup(stream, features="html.parser")
	videoid = soup.head.find_all('link', rel="canonical")[0]['href'].split('watch?v=')[1]
	title = soup.head.find_all('title')[0].text.split(' - YouTube')[0]
except:
	sys.exit(0)

lastvideoid = open('youtube.txt', 'r+')
if videoid != lastvideoid.read():
	#announcing stream in telegram
	message = f'Стрим "{title}" начался.\nhttps://www.youtube.com/watch?v={videoid}'
	playlist = youtube_dl.YoutubeDL({'skip_download': True, 'quiet': True}).extract_info(f'https://www.youtube.com/watch?v={videoid}')['url']
	thumbnail, _ = (ffmpeg.input(playlist).output('pipe:', vframes=1, format='image2', vcodec='mjpeg', **{'vf': 'scale=-1:720'}).run(capture_stdout=True, quiet=True))
	requests.post(f'https://api.telegram.org/bot{config.telegram_token}/sendPhoto', data={'chat_id': config.telegram_chat, 'caption': message}, files={'photo': thumbnail})
	lastvideoid.seek(0).truncate().write(videoid)
lastvideoid.close()
