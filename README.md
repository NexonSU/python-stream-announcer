# python-stream-announcer
Simple Stream Telegram Announcer from Youtube and Twitch

## Instalation
```bash
cd <your script path>
pip install requests
wget https://github.com/NexonSU/python-stream-announcer/archive/master.zip
unzip master.zip
rm master.zip
mv ./python-stream-announcer-master/* ./
rmdir python-stream-announcer-master
```
## Additional installation for Youtube
```bash
pip install beautifulsoup4
pip install youtube-dl
pip install ffmpeg-python
```
Also, ffmpeg-python requires ffmpeg binary on your system: https://www.ffmpeg.org/

# TODO
- [ ] Upload files directly to telegram without web-server in youtube.py
- [ ] English translate
